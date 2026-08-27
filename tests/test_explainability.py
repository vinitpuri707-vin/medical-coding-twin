from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from operational_coding_twin.config import (
    EXPLANATION_WARNING,
)

from operational_coding_twin.explainability import (
    ExplanationResult,
    FrozenExplainabilityService,
    TokenAttribution,
)

from operational_coding_twin.frozen_resources import (
    load_frozen_resources,
)

from operational_coding_twin.inference import (
    FrozenInferenceService,
    PredictionResult,
    RankedPrediction,
)


# ============================================================
# SYNTHETIC NOTE
# ============================================================

SYNTHETIC_NOTE = (
    "Synthetic patient presented with worsening breathlessness, "
    "bilateral ankle oedema and reduced exercise tolerance. "
    "Echocardiography demonstrated impaired left ventricular "
    "systolic function. The patient received medical treatment "
    "and was discharged for outpatient follow-up."
)


# ============================================================
# MODULE FIXTURES
#
# Frozen model is loaded once.
# Fresh BioClinicalBERT inference is run once.
# Full 50-step LIG is also run once only.
# ============================================================

@pytest.fixture(
    scope="module"
)
def resources():
    return load_frozen_resources()


@pytest.fixture(
    scope="module"
)
def inference_service(
    resources,
):
    return FrozenInferenceService(
        resources
    )


@pytest.fixture(
    scope="module"
)
def xai_service(
    resources,
):
    return FrozenExplainabilityService(
        resources
    )


@pytest.fixture(
    scope="module"
)
def fresh_prediction(
    inference_service,
):
    return inference_service.predict(
        SYNTHETIC_NOTE
    )


@pytest.fixture(
    scope="module"
)
def fresh_explanation(
    xai_service,
    fresh_prediction,
):
    """
    This is the only full 50-step fresh LIG calculation
    performed in this module.
    """

    return xai_service.explain(
        SYNTHETIC_NOTE,
        fresh_prediction,
    )


# ============================================================
# XAI CONFIGURATION
# ============================================================

def test_xai_uses_frozen_max_length(
    xai_service,
):
    assert (
        xai_service.max_length
        == 320
    )


def test_xai_uses_exactly_50_steps(
    xai_service,
):
    assert (
        xai_service.n_steps
        == 50
    )


def test_xai_rejects_non_frozen_step_count(
    resources,
):
    with pytest.raises(
        RuntimeError
    ):
        FrozenExplainabilityService(
            resources,
            n_steps=49,
        )


def test_xai_requires_positive_top_k(
    resources,
):
    with pytest.raises(
        ValueError
    ):
        FrozenExplainabilityService(
            resources,
            top_k=0,
        )


def test_xai_model_is_eval_mode(
    xai_service,
):
    assert (
        xai_service.model.training
        is False
    )


def test_xai_uses_bert_embedding_layer(
    xai_service,
):
    assert hasattr(
        xai_service.model,
        "bert",
    )

    assert hasattr(
        xai_service.model.bert,
        "embeddings",
    )


# ============================================================
# PAD-CONTENT BASELINE
# ============================================================

def test_pad_content_baseline_preserves_special_tokens(
    xai_service,
):
    encoded = (
        xai_service.tokenizer(
            SYNTHETIC_NOTE,
            truncation=True,
            max_length=320,
            padding=False,
            return_tensors="pt",
        )
    )

    input_ids = encoded[
        "input_ids"
    ].to(
        xai_service.device
    )

    attention_mask = encoded[
        "attention_mask"
    ].to(
        xai_service.device
    )

    baseline_ids, content_mask = (
        xai_service._build_baseline(
            input_ids,
            attention_mask,
        )
    )

    original = (
        input_ids[
            0
        ]
        .detach()
        .cpu()
        .numpy()
    )

    baseline = (
        baseline_ids[
            0
        ]
        .detach()
        .cpu()
        .numpy()
    )

    # --------------------------------------------------------
    # Content positions must be replaced by PAD.
    # --------------------------------------------------------

    assert (
        baseline[
            content_mask
        ]
        == xai_service
        .tokenizer
        .pad_token_id
    ).all()

    # --------------------------------------------------------
    # Non-content positions, including [CLS] and [SEP],
    # must remain unchanged.
    # --------------------------------------------------------

    assert np.array_equal(
        baseline[
            ~content_mask
        ],
        original[
            ~content_mask
        ],
    )


def test_pad_content_baseline_has_explainable_tokens(
    xai_service,
):
    encoded = (
        xai_service.tokenizer(
            SYNTHETIC_NOTE,
            truncation=True,
            max_length=320,
            padding=False,
            return_tensors="pt",
        )
    )

    baseline_ids, content_mask = (
        xai_service._build_baseline(
            encoded[
                "input_ids"
            ].to(
                xai_service.device
            ),
            encoded[
                "attention_mask"
            ].to(
                xai_service.device
            ),
        )
    )

    assert baseline_ids is not None

    assert (
        int(
            content_mask.sum()
        )
        > 0
    )


# ============================================================
# TARGET-CLASS CONTRACT
# ============================================================

def test_fresh_xai_targets_predicted_class(
    resources,
    fresh_prediction,
    monkeypatch,
):
    """
    Verify the class passed to Captum without performing
    another expensive 50-step LIG run.
    """

    service = FrozenExplainabilityService(
        resources
    )

    captured = {}

    def fake_attribute(
        *,
        inputs,
        baselines,
        additional_forward_args,
        target,
        n_steps,
        internal_batch_size,
        return_convergence_delta,
    ):
        captured[
            "target"
        ] = target

        captured[
            "n_steps"
        ] = n_steps

        captured[
            "internal_batch_size"
        ] = internal_batch_size

        captured[
            "return_convergence_delta"
        ] = (
            return_convergence_delta
        )

        sequence_length = int(
            inputs.shape[
                1
            ]
        )

        hidden_size = int(
            service
            .model
            .config
            .hidden_size
        )

        # Shape expected from embedding-layer attribution:
        # batch × sequence × hidden size
        attributions = torch.zeros(
            (
                1,
                sequence_length,
                hidden_size,
            ),
            dtype=torch.float32,
            device=service.device,
        )

        # Give one token a positive attribution so the
        # downstream support-token logic remains exercised.
        if sequence_length > 2:
            attributions[
                0,
                1,
                0,
            ] = 1.0

        delta = torch.tensor(
            [0.0],
            dtype=torch.float32,
            device=service.device,
        )

        return (
            attributions,
            delta,
        )

    monkeypatch.setattr(
        service.lig,
        "attribute",
        fake_attribute,
    )

    explanation = service.explain(
        SYNTHETIC_NOTE,
        fresh_prediction,
    )

    assert (
        captured[
            "target"
        ]
        == fresh_prediction
        .predicted_class_id
    )

    assert (
        captured[
            "n_steps"
        ]
        == 50
    )

    assert (
        captured[
            "internal_batch_size"
        ]
        == 5
    )

    assert (
        captured[
            "return_convergence_delta"
        ]
        is True
    )

    assert (
        explanation.category
        == fresh_prediction.recommendation
    )


# ============================================================
# PREDICTION / EXPLANATION CONSISTENCY
# ============================================================

def test_fresh_xai_rejects_replay_prediction(
    xai_service,
):
    replay_prediction = PredictionResult(
        recommendation="B96",

        predicted_class_id=0,

        calibrated_confidence=0.8,

        raw_confidence=float(
            "nan"
        ),

        top3=[
            RankedPrediction(
                rank=1,
                category="B96",
                probability=0.8,
            ),

            RankedPrediction(
                rank=2,
                category="C50",
                probability=0.1,
            ),

            RankedPrediction(
                rank=3,
                category="C77",
                probability=0.05,
            ),
        ],

        temperature=0.18388931380527324,

        input_tokens=0,

        truncated=False,

        source_mode=(
            "frozen_validation_replay"
        ),
    )

    with pytest.raises(
        ValueError
    ):
        xai_service.explain(
            SYNTHETIC_NOTE,
            replay_prediction,
        )


def test_fresh_xai_rejects_category_id_mismatch(
    xai_service,
    fresh_prediction,
):
    wrong_category = next(
        label
        for label
        in xai_service.resources.label2id
        if label
        != fresh_prediction.recommendation
    )

    invalid = PredictionResult(
        recommendation=wrong_category,

        predicted_class_id=(
            fresh_prediction
            .predicted_class_id
        ),

        calibrated_confidence=(
            fresh_prediction
            .calibrated_confidence
        ),

        raw_confidence=(
            fresh_prediction
            .raw_confidence
        ),

        top3=(
            fresh_prediction
            .top3
        ),

        temperature=(
            fresh_prediction
            .temperature
        ),

        input_tokens=(
            fresh_prediction
            .input_tokens
        ),

        truncated=(
            fresh_prediction
            .truncated
        ),

        source_mode=(
            "fresh_frozen_inference"
        ),
    )

    with pytest.raises(
        RuntimeError
    ):
        xai_service.explain(
            SYNTHETIC_NOTE,
            invalid,
        )


# ============================================================
# ACTUAL FRESH 50-STEP LIG
# ============================================================

def test_fresh_explanation_returns_expected_type(
    fresh_explanation,
):
    assert isinstance(
        fresh_explanation,
        ExplanationResult,
    )


def test_fresh_explanation_target_matches_prediction(
    fresh_explanation,
    fresh_prediction,
):
    assert (
        fresh_explanation.category
        == fresh_prediction.recommendation
    )


def test_fresh_explanation_method_is_lig(
    fresh_explanation,
):
    assert (
        fresh_explanation.method
        == "Layer Integrated Gradients"
    )


def test_fresh_explanation_uses_50_steps(
    fresh_explanation,
):
    assert (
        fresh_explanation.steps
        == 50
    )


def test_fresh_explanation_records_pad_baseline(
    fresh_explanation,
):
    text = (
        fresh_explanation
        .baseline
        .lower()
    )

    assert (
        "pad"
        in text
    )

    assert (
        "special"
        in text
    )


def test_fresh_explanation_mode(
    fresh_explanation,
):
    assert (
        fresh_explanation.source_mode
        == "fresh_lig"
    )


def test_fresh_explanation_contains_warning(
    fresh_explanation,
):
    assert (
        fresh_explanation.warning
        == EXPLANATION_WARNING
    )


def test_explanation_warning_is_non_causal(
    fresh_explanation,
):
    text = (
        fresh_explanation
        .warning
        .lower()
    )

    assert (
        "not"
        in text
    )

    assert (
        "causal"
        in text
        or
        "model behaviour"
        in text
    )


def test_fresh_explanation_contains_token_attributions(
    fresh_explanation,
):
    assert isinstance(
        fresh_explanation
        .all_token_attributions,
        list,
    )

    assert (
        len(
            fresh_explanation
            .all_token_attributions
        )
        > 0
    )


def test_fresh_attributions_have_valid_positions(
    fresh_explanation,
):
    positions = [
        item.position
        for item
        in fresh_explanation
        .all_token_attributions
    ]

    assert all(
        isinstance(
            position,
            int,
        )
        for position in positions
    )

    assert all(
        position >= 0
        for position in positions
    )


def test_fresh_attributions_are_finite(
    fresh_explanation,
):
    for item in (
        fresh_explanation
        .all_token_attributions
    ):
        assert math.isfinite(
            item.raw_score
        )

        assert math.isfinite(
            item.normalized_score
        )


def test_fresh_evidence_contains_only_positive_support(
    fresh_explanation,
):
    for item in (
        fresh_explanation.evidence
    ):
        assert (
            item.raw_score
            > 0
        )


def test_fresh_evidence_respects_top_k(
    fresh_explanation,
    xai_service,
):
    assert (
        len(
            fresh_explanation.evidence
        )
        <= xai_service.top_k
    )


def test_fresh_evidence_sorted_by_support(
    fresh_explanation,
):
    scores = [
        item.raw_score
        for item
        in fresh_explanation.evidence
    ]

    assert (
        scores
        == sorted(
            scores,
            reverse=True,
        )
    )


def test_token_attribution_objects_are_typed(
    fresh_explanation,
):
    assert all(
        isinstance(
            item,
            TokenAttribution,
        )
        for item
        in fresh_explanation
        .all_token_attributions
    )

    assert all(
        isinstance(
            item,
            TokenAttribution,
        )
        for item
        in fresh_explanation.evidence
    )


def test_convergence_delta_is_finite_when_available(
    fresh_explanation,
):
    if (
        fresh_explanation
        .convergence_delta
        is not None
    ):
        assert math.isfinite(
            fresh_explanation
            .convergence_delta
        )


def test_model_remains_eval_after_lig(
    xai_service,
    fresh_explanation,
):
    assert fresh_explanation is not None

    assert (
        xai_service.model.training
        is False
    )


# ============================================================
# FROZEN REPLAY FIXTURES
# ============================================================

@pytest.fixture(
    scope="module"
)
def replay_row(
    resources,
):
    return int(
        resources
        .replay_sample
        .sort_values(
            "sample_rank"
        )
        .iloc[
            0
        ][
            "validation_row"
        ]
    )


@pytest.fixture(
    scope="module"
)
def replay_prediction(
    inference_service,
    replay_row,
):
    return inference_service.replay(
        replay_row
    )


@pytest.fixture(
    scope="module"
)
def replay_explanation(
    xai_service,
    replay_row,
):
    return xai_service.replay(
        replay_row
    )


# ============================================================
# REPLAY EXPLAINABILITY
# ============================================================

def test_replay_explanation_type(
    replay_explanation,
):
    assert isinstance(
        replay_explanation,
        ExplanationResult,
    )


def test_replay_explanation_mode(
    replay_explanation,
):
    assert (
        replay_explanation.source_mode
        == "frozen_validation_replay"
    )


def test_replay_explanation_method(
    replay_explanation,
):
    assert (
        "Layer Integrated Gradients"
        in replay_explanation.method
    )


def test_replay_explanation_uses_50_steps(
    replay_explanation,
):
    assert (
        replay_explanation.steps
        == 50
    )


def test_replay_explanation_matches_prediction(
    replay_explanation,
    replay_prediction,
):
    assert (
        replay_explanation.category
        == replay_prediction.recommendation
    )


def test_replay_explanation_has_warning(
    replay_explanation,
):
    assert (
        replay_explanation.warning
        == EXPLANATION_WARNING
    )


def test_replay_evidence_is_list(
    replay_explanation,
):
    assert isinstance(
        replay_explanation.evidence,
        list,
    )


def test_replay_evidence_items_are_typed(
    replay_explanation,
):
    assert all(
        isinstance(
            item,
            TokenAttribution,
        )
        for item
        in replay_explanation.evidence
    )


def test_replay_does_not_claim_full_token_table(
    replay_explanation,
):
    """
    The working replay application uses the frozen
    Phase 8B case-level support-token summary.
    """

    assert (
        replay_explanation
        .all_token_attributions
        == []
    )


def test_replay_does_not_invent_convergence_delta(
    replay_explanation,
):
    assert (
        replay_explanation
        .convergence_delta
        is None
    )


# ============================================================
# REPLAY ACCESS CONTROL
# ============================================================

def test_replay_rejects_non_sample_validation_row(
    xai_service,
    resources,
):
    permitted = set(
        resources
        .replay_sample[
            "validation_row"
        ]
        .astype(
            int
        )
        .tolist()
    )

    outside_sample = next(
        row
        for row
        in range(
            375
        )
        if row not in permitted
    )

    with pytest.raises(
        ValueError
    ):
        xai_service.replay(
            outside_sample
        )


# ============================================================
# CRITICAL GOVERNANCE TEST
# ============================================================

def test_replay_xai_does_not_run_new_captum_attribution(
    resources,
    replay_row,
    monkeypatch,
):
    """
    Frozen validation replay must use the saved Phase 8B
    explanation and must NOT calculate another explanation.
    """

    service = (
        FrozenExplainabilityService(
            resources
        )
    )

    def prohibited_attribute(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "Captum LIG was unexpectedly executed "
            "during frozen validation replay."
        )

    monkeypatch.setattr(
        service.lig,
        "attribute",
        prohibited_attribute,
    )

    result = service.replay(
        replay_row
    )

    assert (
        result.source_mode
        == "frozen_validation_replay"
    )


# ============================================================
# ALL 100 REPLAY CASES
# ============================================================

def test_all_frozen_replay_explanations_are_accessible(
    xai_service,
    resources,
):
    rows = (
        resources
        .replay_sample[
            "validation_row"
        ]
        .astype(
            int
        )
        .tolist()
    )

    assert len(
        rows
    ) == 100

    for row in rows:
        result = xai_service.replay(
            row
        )

        assert (
            result.steps
            == 50
        )

        assert (
            result.category
            in resources.label2id
        )


# ============================================================
# EXPLANATION IS NOT AN ACCEPTANCE DECISION
# ============================================================

def test_explanation_result_contains_no_acceptance_field(
    fresh_explanation,
):
    assert not hasattr(
        fresh_explanation,
        "accepted",
    )

    assert not hasattr(
        fresh_explanation,
        "auto_accept",
    )

    assert not hasattr(
        fresh_explanation,
        "decision",
    )