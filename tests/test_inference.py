from __future__ import annotations

import math

import numpy as np
import pytest

from operational_coding_twin.frozen_resources import (
    load_frozen_resources,
)

from operational_coding_twin.inference import (
    FrozenInferenceService,
    PredictionResult,
    RankedPrediction,
)


# ============================================================
# TEST SYNTHETIC NOTE
# ============================================================

SYNTHETIC_NOTE = (
    "Synthetic patient presented with worsening breathlessness, "
    "bilateral ankle oedema and reduced exercise tolerance. "
    "Echocardiography demonstrated impaired left ventricular "
    "systolic function. The patient received medical treatment "
    "and was discharged for outpatient follow-up."
)


# ============================================================
# MODULE-SCOPED FIXTURES
#
# The 413 MB model is loaded once for this test module.
# Fresh BioClinicalBERT inference is also run only once.
# ============================================================

@pytest.fixture(
    scope="module"
)
def resources():
    return load_frozen_resources()


@pytest.fixture(
    scope="module"
)
def service(
    resources,
):
    return FrozenInferenceService(
        resources
    )


@pytest.fixture(
    scope="module"
)
def fresh_prediction(
    service,
):
    return service.predict(
        SYNTHETIC_NOTE
    )


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

def test_inference_service_uses_frozen_max_length(
    service,
):
    assert (
        service.max_length
        == 320
    )


def test_inference_service_uses_50_labels(
    service,
):
    assert len(
        service.label2id
    ) == 50

    assert len(
        service.id2label
    ) == 50


def test_inference_service_uses_frozen_temperature(
    service,
):
    assert (
        service.temperature
        == pytest.approx(
            0.18388931380527324,
            abs=1e-10,
        )
    )


def test_model_is_in_eval_mode(
    service,
):
    assert (
        service.model.training
        is False
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

def test_none_text_is_rejected(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.predict(
            None
        )


def test_empty_text_is_rejected(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.predict(
            ""
        )


def test_whitespace_only_text_is_rejected(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.predict(
            "     "
        )


def test_too_short_text_is_rejected(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.predict(
            "Short synthetic note."
        )


def test_excessively_long_text_is_rejected(
    service,
):
    excessive = (
        "synthetic "
        * 6000
    )

    assert len(
        excessive
    ) > 50_000

    with pytest.raises(
        ValueError
    ):
        service.predict(
            excessive
        )


# ============================================================
# FRESH FROZEN INFERENCE
# ============================================================

def test_fresh_prediction_returns_expected_type(
    fresh_prediction,
):
    assert isinstance(
        fresh_prediction,
        PredictionResult,
    )


def test_fresh_prediction_mode(
    fresh_prediction,
):
    assert (
        fresh_prediction.source_mode
        == "fresh_frozen_inference"
    )


def test_fresh_prediction_is_in_frozen_label_space(
    fresh_prediction,
    resources,
):
    assert (
        fresh_prediction.recommendation
        in resources.label2id
    )


def test_fresh_prediction_class_id_is_valid(
    fresh_prediction,
):
    assert (
        0
        <= fresh_prediction.predicted_class_id
        < 50
    )


def test_fresh_prediction_label_matches_class_id(
    fresh_prediction,
    resources,
):
    expected = resources.id2label[
        fresh_prediction.predicted_class_id
    ]

    assert (
        fresh_prediction.recommendation
        == expected
    )


def test_fresh_prediction_has_exactly_top3(
    fresh_prediction,
):
    assert len(
        fresh_prediction.top3
    ) == 3


def test_top3_items_are_ranked_prediction_objects(
    fresh_prediction,
):
    assert all(
        isinstance(
            item,
            RankedPrediction,
        )
        for item in fresh_prediction.top3
    )


def test_top3_ranks_are_one_two_three(
    fresh_prediction,
):
    assert [
        item.rank
        for item in fresh_prediction.top3
    ] == [
        1,
        2,
        3,
    ]


def test_top3_categories_are_unique(
    fresh_prediction,
):
    categories = [
        item.category
        for item in fresh_prediction.top3
    ]

    assert len(
        categories
    ) == len(
        set(
            categories
        )
    )


def test_top3_categories_are_in_frozen_space(
    fresh_prediction,
    resources,
):
    assert all(
        item.category
        in resources.label2id
        for item
        in fresh_prediction.top3
    )


def test_top3_probabilities_are_descending(
    fresh_prediction,
):
    probabilities = [
        item.probability
        for item in fresh_prediction.top3
    ]

    assert (
        probabilities
        == sorted(
            probabilities,
            reverse=True,
        )
    )


def test_top3_probabilities_are_valid(
    fresh_prediction,
):
    for item in (
        fresh_prediction.top3
    ):
        assert math.isfinite(
            item.probability
        )

        assert (
            0.0
            <= item.probability
            <= 1.0
        )


def test_top1_matches_recommendation(
    fresh_prediction,
):
    assert (
        fresh_prediction.top3[
            0
        ].category
        == fresh_prediction.recommendation
    )


def test_calibrated_confidence_matches_top1(
    fresh_prediction,
):
    assert (
        fresh_prediction.calibrated_confidence
        == pytest.approx(
            fresh_prediction.top3[
                0
            ].probability,
            abs=1e-12,
        )
    )


def test_fresh_calibrated_confidence_is_valid(
    fresh_prediction,
):
    assert math.isfinite(
        fresh_prediction.calibrated_confidence
    )

    assert (
        0.0
        <= fresh_prediction.calibrated_confidence
        <= 1.0
    )


def test_fresh_raw_confidence_is_valid(
    fresh_prediction,
):
    assert math.isfinite(
        fresh_prediction.raw_confidence
    )

    assert (
        0.0
        <= fresh_prediction.raw_confidence
        <= 1.0
    )


def test_fresh_prediction_records_temperature(
    fresh_prediction,
):
    assert (
        fresh_prediction.temperature
        == pytest.approx(
            0.18388931380527324,
            abs=1e-10,
        )
    )


def test_fresh_prediction_records_token_count(
    fresh_prediction,
):
    assert (
        fresh_prediction.input_tokens
        > 0
    )


def test_short_synthetic_note_not_truncated(
    fresh_prediction,
):
    assert (
        fresh_prediction.truncated
        is False
    )


def test_model_remains_eval_after_prediction(
    service,
    fresh_prediction,
):
    assert fresh_prediction is not None

    assert (
        service.model.training
        is False
    )


# ============================================================
# CALIBRATION BEHAVIOUR
# ============================================================

def test_calibrated_and_raw_confidence_are_not_assumed_equal(
    fresh_prediction,
):
    """
    Temperature scaling should normally alter confidence.

    We do not require a specific direction because that depends
    on the model logits.
    """

    assert math.isfinite(
        fresh_prediction.raw_confidence
    )

    assert math.isfinite(
        fresh_prediction.calibrated_confidence
    )

    assert (
        fresh_prediction.raw_confidence
        != pytest.approx(
            fresh_prediction.calibrated_confidence,
            abs=1e-12,
        )
    )


# ============================================================
# FROZEN VALIDATION REPLAY
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
    service,
    replay_row,
):
    return service.replay(
        replay_row
    )


def test_replay_returns_prediction_result(
    replay_prediction,
):
    assert isinstance(
        replay_prediction,
        PredictionResult,
    )


def test_replay_mode_is_correct(
    replay_prediction,
):
    assert (
        replay_prediction.source_mode
        == "frozen_validation_replay"
    )


def test_replay_has_exactly_top3(
    replay_prediction,
):
    assert len(
        replay_prediction.top3
    ) == 3


def test_replay_top3_is_descending(
    replay_prediction,
):
    values = [
        item.probability
        for item
        in replay_prediction.top3
    ]

    assert (
        values
        == sorted(
            values,
            reverse=True,
        )
    )


def test_replay_recommendation_is_top1(
    replay_prediction,
):
    assert (
        replay_prediction.recommendation
        == replay_prediction.top3[
            0
        ].category
    )


def test_replay_confidence_matches_top1(
    replay_prediction,
):
    assert (
        replay_prediction.calibrated_confidence
        == pytest.approx(
            replay_prediction.top3[
                0
            ].probability,
            abs=1e-12,
        )
    )


def test_replay_prediction_is_in_label_space(
    replay_prediction,
    resources,
):
    assert (
        replay_prediction.recommendation
        in resources.label2id
    )


def test_replay_class_id_matches_label(
    replay_prediction,
    resources,
):
    assert (
        resources.id2label[
            replay_prediction.predicted_class_id
        ]
        == replay_prediction.recommendation
    )


def test_replay_uses_frozen_temperature(
    replay_prediction,
):
    assert (
        replay_prediction.temperature
        == pytest.approx(
            0.18388931380527324,
            abs=1e-10,
        )
    )


def test_replay_raw_confidence_is_unavailable(
    replay_prediction,
):
    assert math.isnan(
        replay_prediction.raw_confidence
    )


def test_replay_does_not_claim_input_token_count(
    replay_prediction,
):
    assert (
        replay_prediction.input_tokens
        == 0
    )


# ============================================================
# REPLAY MUST MATCH STORED PROBABILITY MATRIX
# ============================================================

def test_replay_top1_matches_saved_probability_matrix(
    resources,
    replay_row,
    replay_prediction,
):
    probabilities = (
        resources
        .replay_probabilities[
            replay_row
        ]
    )

    expected_class_id = int(
        np.argmax(
            probabilities
        )
    )

    expected_category = (
        resources.id2label[
            expected_class_id
        ]
    )

    assert (
        replay_prediction.predicted_class_id
        == expected_class_id
    )

    assert (
        replay_prediction.recommendation
        == expected_category
    )


def test_replay_confidence_matches_saved_matrix(
    resources,
    replay_row,
    replay_prediction,
):
    expected = float(
        resources
        .replay_probabilities[
            replay_row,
            replay_prediction.predicted_class_id,
        ]
    )

    assert (
        replay_prediction.calibrated_confidence
        == pytest.approx(
            expected,
            abs=1e-12,
        )
    )


# ============================================================
# REPLAY ACCESS CONTROL
# ============================================================

def test_replay_rejects_negative_row(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.replay(
            -1
        )


def test_replay_rejects_row_375(
    service,
):
    with pytest.raises(
        ValueError
    ):
        service.replay(
            375
        )


def test_replay_rejects_validation_row_not_in_frozen_sample(
    service,
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

    non_sample_rows = [
        row
        for row in range(
            375
        )
        if row not in permitted
    ]

    assert non_sample_rows, (
        "Expected at least one validation row outside "
        "the deterministic n=100 replay sample."
    )

    with pytest.raises(
        ValueError
    ):
        service.replay(
            non_sample_rows[
                0
            ]
        )


def test_every_frozen_sample_row_is_permitted(
    service,
    resources,
):
    """
    We do not invoke all 100 predictions through the model.
    Replay is only array lookup, so checking every frozen row
    is inexpensive.
    """

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

    for row in rows:
        result = service.replay(
            row
        )

        assert (
            result.source_mode
            == "frozen_validation_replay"
        )


# ============================================================
# CRITICAL REPLAY GOVERNANCE TEST
# ============================================================

def test_replay_does_not_call_bioclinicalbert_forward(
    service,
    replay_row,
    monkeypatch,
):
    """
    Replay mode must use the already-frozen Phase 8B
    probability matrix rather than rerunning inference.

    If model.forward is invoked, this test deliberately fails.
    """

    def prohibited_forward(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "BioClinicalBERT forward pass was called "
            "during frozen validation replay."
        )

    monkeypatch.setattr(
        service.model,
        "forward",
        prohibited_forward,
    )

    result = service.replay(
        replay_row
    )

    assert (
        result.source_mode
        == "frozen_validation_replay"
    )


# ============================================================
# NO AUTOMATIC DECISION SEMANTICS IN INFERENCE LAYER
# ============================================================

def test_prediction_result_contains_no_accept_field(
    fresh_prediction,
):
    assert not hasattr(
        fresh_prediction,
        "accepted"
    )

    assert not hasattr(
        fresh_prediction,
        "auto_accept"
    )

    assert not hasattr(
        fresh_prediction,
        "threshold"
    )