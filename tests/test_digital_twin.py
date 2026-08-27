from __future__ import annotations

from pathlib import Path

import pytest

from operational_coding_twin.audit_log import (
    AppendOnlyAuditLog,
)

from operational_coding_twin.case_store import (
    CaseStore,
)

from operational_coding_twin.digital_twin import (
    OperationalCodingTwin,
    State,
    VALID_TRANSITIONS,
)

from operational_coding_twin.explainability import (
    ExplanationResult,
    TokenAttribution,
)

from operational_coding_twin.inference import (
    PredictionResult,
    RankedPrediction,
)


# ============================================================
# FROZEN-LABEL TEST SPACE
#
# These are synthetic test labels. We deliberately avoid
# loading the 413 MB model because this module tests workflow
# behaviour rather than scientific inference.
# ============================================================

VALID_CATEGORIES = {
    f"C{i:02d}"
    for i in range(50)
}


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def store(
    tmp_path: Path,
):
    return CaseStore(
        tmp_path
        / "cases"
    )


@pytest.fixture
def audit(
    tmp_path: Path,
):
    return AppendOnlyAuditLog(
        tmp_path
        / "audit"
        / "audit.jsonl"
    )


@pytest.fixture
def twin(
    tmp_path: Path,
    store,
    audit,
):
    return OperationalCodingTwin(
        store=store,

        audit=audit,

        valid_categories=(
            VALID_CATEGORIES
        ),

        explanations_dir=(
            tmp_path
            / "explanations"
        ),
    )


@pytest.fixture
def prediction():
    return PredictionResult(
        recommendation="C01",

        predicted_class_id=1,

        calibrated_confidence=0.70,

        raw_confidence=0.40,

        top3=[
            RankedPrediction(
                rank=1,
                category="C01",
                probability=0.70,
            ),

            RankedPrediction(
                rank=2,
                category="C02",
                probability=0.20,
            ),

            RankedPrediction(
                rank=3,
                category="C03",
                probability=0.05,
            ),
        ],

        temperature=0.18388931380527324,

        input_tokens=100,

        truncated=False,

        source_mode=(
            "fresh_frozen_inference"
        ),
    )


@pytest.fixture
def explanation():
    support = TokenAttribution(
        position=4,
        token="synthetic",
        raw_score=0.5,
        normalized_score=0.25,
    )

    return ExplanationResult(
        category="C01",

        method=(
            "Layer Integrated Gradients"
        ),

        steps=50,

        baseline=(
            "PAD-content baseline; "
            "special tokens preserved"
        ),

        evidence=[
            support
        ],

        all_token_attributions=[
            support
        ],

        convergence_delta=0.001,

        source_mode="fresh_lig",

        warning=(
            "Model-behaviour evidence only."
        ),
    )


@pytest.fixture
def synthetic_text():
    return (
        "Synthetic demonstration patient presented with "
        "sufficient clinical narrative for testing the "
        "operational digital-twin workflow."
    )


# ============================================================
# HELPER
# ============================================================

def create_case_at_review(
    twin,
    prediction,
    explanation,
    synthetic_text,
    *,
    case_id="CASE-REVIEW",
):
    """
    Create a valid case and move it to Awaiting Human Review.
    """

    twin.ingest(
        case_id=case_id,

        source_mode=(
            "synthetic_note"
        ),

        clinical_text=(
            synthetic_text
        ),
    )

    twin.preprocess(
        case_id
    )

    twin.attach_prediction(
        case_id,
        prediction,
    )

    twin.attach_explanation(
        case_id,
        explanation,
    )

    twin.send_for_review(
        case_id
    )

    return twin.get_case(
        case_id
    )


# ============================================================
# STATE-MACHINE CONTRACT
# ============================================================

def test_initial_state_transition_contract():
    assert (
        State.PREPROCESSED
        in VALID_TRANSITIONS[
            State.INGESTED
        ]
    )

    assert (
        State.ERROR
        in VALID_TRANSITIONS[
            State.INGESTED
        ]
    )


def test_preprocessed_can_only_progress_to_prediction_or_error():
    assert (
        VALID_TRANSITIONS[
            State.PREPROCESSED
        ]
        == {
            State.PREDICTED,
            State.ERROR,
        }
    )


def test_predicted_can_progress_to_explanation():
    assert (
        State.EXPLAINED
        in VALID_TRANSITIONS[
            State.PREDICTED
        ]
    )


def test_explained_can_progress_to_human_review():
    assert (
        State.AWAITING_HUMAN_REVIEW
        in VALID_TRANSITIONS[
            State.EXPLAINED
        ]
    )


def test_review_state_allows_three_decisions():
    transitions = (
        VALID_TRANSITIONS[
            State.AWAITING_HUMAN_REVIEW
        ]
    )

    assert State.ACCEPTED in transitions
    assert State.REJECTED in transitions
    assert State.AMENDED in transitions


def test_review_outcomes_can_complete():
    assert (
        State.COMPLETED
        in VALID_TRANSITIONS[
            State.ACCEPTED
        ]
    )

    assert (
        State.COMPLETED
        in VALID_TRANSITIONS[
            State.REJECTED
        ]
    )

    assert (
        State.COMPLETED
        in VALID_TRANSITIONS[
            State.AMENDED
        ]
    )


def test_completed_is_terminal():
    assert (
        VALID_TRANSITIONS[
            State.COMPLETED
        ]
        == set()
    )


def test_error_is_terminal():
    assert (
        VALID_TRANSITIONS[
            State.ERROR
        ]
        == set()
    )


# ============================================================
# INGESTION
# ============================================================

def test_ingest_creates_case(
    twin,
    synthetic_text,
):
    case = twin.ingest(
        case_id="INGEST-001",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    assert (
        case[
            "case_id"
        ]
        == "INGEST-001"
    )

    assert (
        case[
            "state"
        ]
        == State.INGESTED.value
    )


def test_ingest_persists_case(
    twin,
    store,
    synthetic_text,
):
    twin.ingest(
        case_id="INGEST-002",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    assert (
        store.exists(
            "INGEST-002"
        )
        is True
    )


def test_duplicate_case_id_is_blocked(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="DUPLICATE",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    with pytest.raises(
        ValueError
    ):
        twin.ingest(
            case_id="DUPLICATE",

            source_mode="synthetic_note",

            clinical_text=synthetic_text,
        )


def test_invalid_source_mode_is_blocked(
    twin,
    synthetic_text,
):
    with pytest.raises(
        ValueError
    ):
        twin.ingest(
            case_id="BAD-SOURCE",

            source_mode="real_patient_data",

            clinical_text=synthetic_text,
        )


def test_short_synthetic_text_is_blocked(
    twin,
):
    with pytest.raises(
        ValueError
    ):
        twin.ingest(
            case_id="SHORT",

            source_mode="synthetic_note",

            clinical_text="Too short.",
        )


# ============================================================
# GOVERNANCE STORED AT INGESTION
# ============================================================

def test_case_governance_disables_automatic_acceptance(
    twin,
    synthetic_text,
):
    case = twin.ingest(
        case_id="GOV-001",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    assert (
        case[
            "governance"
        ][
            "automatic_acceptance"
        ]
        is False
    )


def test_case_governance_requires_human_review(
    twin,
    synthetic_text,
):
    case = twin.ingest(
        case_id="GOV-002",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    assert (
        case[
            "governance"
        ][
            "human_review_required"
        ]
        is True
    )


# ============================================================
# NORMAL PIPELINE
# ============================================================

def test_valid_workflow_reaches_review(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    case = create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
    )

    assert (
        case[
            "state"
        ]
        == (
            State
            .AWAITING_HUMAN_REVIEW
            .value
        )
    )


def test_prediction_is_persisted(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    case = create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
    )

    stored = case[
        "prediction"
    ]

    assert (
        stored[
            "recommendation"
        ]
        == "C01"
    )

    assert (
        stored[
            "calibrated_confidence"
        ]
        == pytest.approx(
            0.70
        )
    )

    assert len(
        stored[
            "top3"
        ]
    ) == 3


def test_explanation_is_persisted(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    case = create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
    )

    stored = case[
        "explanation"
    ]

    assert (
        stored[
            "category"
        ]
        == "C01"
    )

    assert (
        stored[
            "steps"
        ]
        == 50
    )

    assert (
        "Layer Integrated Gradients"
        in stored[
            "method"
        ]
    )


# ============================================================
# ILLEGAL TRANSITIONS
# ============================================================

def test_prediction_cannot_be_attached_before_preprocessing(
    twin,
    prediction,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-TRANSITION-1",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_prediction(
            "BAD-TRANSITION-1",
            prediction,
        )


def test_explanation_cannot_be_attached_before_prediction(
    twin,
    explanation,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-TRANSITION-2",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-TRANSITION-2"
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_explanation(
            "BAD-TRANSITION-2",
            explanation,
        )


def test_case_cannot_be_sent_to_review_before_explanation(
    twin,
    prediction,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-TRANSITION-3",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-TRANSITION-3"
    )

    twin.attach_prediction(
        "BAD-TRANSITION-3",
        prediction,
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.send_for_review(
            "BAD-TRANSITION-3"
        )


# ============================================================
# AUTOMATIC COMPLETION MUST BE BLOCKED
# ============================================================

def test_ingested_case_cannot_complete(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="NO-AUTO-1",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.complete(
            "NO-AUTO-1"
        )


def test_review_pending_case_cannot_complete(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="NO-AUTO-2",
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.complete(
            "NO-AUTO-2"
        )


# ============================================================
# HUMAN REVIEW — ACCEPT
# ============================================================

def test_accept_path(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="ACCEPT-001",
    )

    case = twin.review(
        "ACCEPT-001",

        decision="accept",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason=(
            "Recommendation reviewed "
            "and accepted."
        ),
    )

    assert (
        case[
            "state"
        ]
        == State.ACCEPTED.value
    )

    assert (
        case[
            "final_category"
        ]
        == "C01"
    )

    assert (
        case[
            "review"
        ][
            "reviewer_identity"
        ]
        == "test-reviewer"
    )


def test_accepted_case_can_complete(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="ACCEPT-002",
    )

    twin.review(
        "ACCEPT-002",

        decision="accept",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason=(
            "Reviewed."
        ),
    )

    case = twin.complete(
        "ACCEPT-002"
    )

    assert (
        case[
            "state"
        ]
        == State.COMPLETED.value
    )

    assert (
        case[
            "final_category"
        ]
        == "C01"
    )


# ============================================================
# HUMAN REVIEW — REJECT
# ============================================================

def test_reject_path(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REJECT-001",
    )

    case = twin.review(
        "REJECT-001",

        decision="reject",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason=(
            "Recommendation rejected "
            "after review."
        ),
    )

    assert (
        case[
            "state"
        ]
        == State.REJECTED.value
    )

    assert (
        case[
            "final_category"
        ]
        is None
    )


def test_rejected_case_can_complete(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REJECT-002",
    )

    twin.review(
        "REJECT-002",

        decision="reject",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason="Reviewed.",
    )

    case = twin.complete(
        "REJECT-002"
    )

    assert (
        case[
            "state"
        ]
        == State.COMPLETED.value
    )

    assert (
        case[
            "final_category"
        ]
        is None
    )


# ============================================================
# HUMAN REVIEW — AMEND
# ============================================================

def test_amend_path(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AMEND-001",
    )

    case = twin.review(
        "AMEND-001",

        decision="amend",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason=(
            "Reviewer selected another "
            "valid category."
        ),

        amended_category="C02",
    )

    assert (
        case[
            "state"
        ]
        == State.AMENDED.value
    )

    assert (
        case[
            "final_category"
        ]
        == "C02"
    )

    assert (
        case[
            "review"
        ][
            "amended_category"
        ]
        == "C02"
    )


def test_amended_case_can_complete(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AMEND-002",
    )

    twin.review(
        "AMEND-002",

        decision="amend",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason="Reviewed.",

        amended_category="C02",
    )

    case = twin.complete(
        "AMEND-002"
    )

    assert (
        case[
            "state"
        ]
        == State.COMPLETED.value
    )

    assert (
        case[
            "final_category"
        ]
        == "C02"
    )


# ============================================================
# HUMAN-REVIEW FIELD REQUIREMENTS
# ============================================================

def test_missing_reviewer_identity_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REVIEWER-MISSING",
    )

    with pytest.raises(
        ValueError,
        match="Reviewer identity",
    ):
        twin.review(
            "REVIEWER-MISSING",

            decision="accept",

            reviewer_identity="",

            reason="Reviewed.",
        )


def test_whitespace_reviewer_identity_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REVIEWER-WHITESPACE",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "REVIEWER-WHITESPACE",

            decision="accept",

            reviewer_identity="   ",

            reason="Reviewed.",
        )


def test_missing_review_reason_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REASON-MISSING",
    )

    with pytest.raises(
        ValueError,
        match="reason",
    ):
        twin.review(
            "REASON-MISSING",

            decision="accept",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="",
        )


def test_invalid_review_decision_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="BAD-DECISION",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "BAD-DECISION",

            decision="auto_accept",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Invalid test.",
        )


# ============================================================
# AMENDMENT GOVERNANCE
# ============================================================

def test_amend_requires_category(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AMEND-MISSING",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "AMEND-MISSING",

            decision="amend",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Amend test.",

            amended_category=None,
        )


def test_invalid_amended_category_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AMEND-INVALID",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "AMEND-INVALID",

            decision="amend",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Amend test.",

            amended_category=(
                "NOT-A-FROZEN-CATEGORY"
            ),
        )


def test_amend_to_same_model_category_is_blocked(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AMEND-SAME",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "AMEND-SAME",

            decision="amend",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Amend test.",

            amended_category="C01",
        )


def test_accept_cannot_include_amended_category(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="ACCEPT-WITH-AMEND",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "ACCEPT-WITH-AMEND",

            decision="accept",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Review.",

            amended_category="C02",
        )


def test_reject_cannot_include_amended_category(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="REJECT-WITH-AMEND",
    )

    with pytest.raises(
        ValueError
    ):
        twin.review(
            "REJECT-WITH-AMEND",

            decision="reject",

            reviewer_identity=(
                "test-reviewer"
            ),

            reason="Review.",

            amended_category="C02",
        )


# ============================================================
# PREDICTION VALIDATION
# ============================================================

def test_prediction_outside_label_space_is_blocked(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-PREDICTION",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-PREDICTION"
    )

    invalid = PredictionResult(
        recommendation="INVALID",

        predicted_class_id=1,

        calibrated_confidence=0.7,

        raw_confidence=0.4,

        top3=[
            RankedPrediction(
                rank=1,
                category="INVALID",
                probability=0.7,
            ),

            RankedPrediction(
                rank=2,
                category="C02",
                probability=0.2,
            ),

            RankedPrediction(
                rank=3,
                category="C03",
                probability=0.05,
            ),
        ],

        temperature=(
            0.18388931380527324
        ),

        input_tokens=100,

        truncated=False,

        source_mode=(
            "fresh_frozen_inference"
        ),
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_prediction(
            "BAD-PREDICTION",
            invalid,
        )


def test_prediction_requires_exactly_three_ranked_categories(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-TOP3",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-TOP3"
    )

    invalid = PredictionResult(
        recommendation="C01",

        predicted_class_id=1,

        calibrated_confidence=0.7,

        raw_confidence=0.4,

        top3=[
            RankedPrediction(
                rank=1,
                category="C01",
                probability=0.7,
            ),
        ],

        temperature=(
            0.18388931380527324
        ),

        input_tokens=100,

        truncated=False,

        source_mode=(
            "fresh_frozen_inference"
        ),
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_prediction(
            "BAD-TOP3",
            invalid,
        )


# ============================================================
# EXPLANATION GOVERNANCE
# ============================================================

def test_explanation_must_match_prediction(
    twin,
    prediction,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-XAI-TARGET",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-XAI-TARGET"
    )

    twin.attach_prediction(
        "BAD-XAI-TARGET",
        prediction,
    )

    invalid_explanation = (
        ExplanationResult(
            category="C02",

            method=(
                "Layer Integrated Gradients"
            ),

            steps=50,

            baseline=(
                "PAD-content baseline"
            ),

            evidence=[],

            all_token_attributions=[],

            convergence_delta=0.0,

            source_mode="fresh_lig",

            warning=(
                "Model behaviour only."
            ),
        )
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_explanation(
            "BAD-XAI-TARGET",
            invalid_explanation,
        )


def test_explanation_requires_50_steps(
    twin,
    prediction,
    synthetic_text,
):
    twin.ingest(
        case_id="BAD-XAI-STEPS",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "BAD-XAI-STEPS"
    )

    twin.attach_prediction(
        "BAD-XAI-STEPS",
        prediction,
    )

    invalid_explanation = (
        ExplanationResult(
            category="C01",

            method=(
                "Layer Integrated Gradients"
            ),

            steps=25,

            baseline=(
                "PAD-content baseline"
            ),

            evidence=[],

            all_token_attributions=[],

            convergence_delta=0.0,

            source_mode="fresh_lig",

            warning=(
                "Model behaviour only."
            ),
        )
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_explanation(
            "BAD-XAI-STEPS",
            invalid_explanation,
        )


# ============================================================
# ERROR STATE
# ============================================================

def test_case_can_enter_error_state(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="ERROR-001",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    case = twin.fail(
        "ERROR-001",

        error=(
            "Synthetic verification failure."
        ),
    )

    assert (
        case[
            "state"
        ]
        == State.ERROR.value
    )

    assert (
        case[
            "error"
        ][
            "message"
        ]
        == (
            "Synthetic verification failure."
        )
    )


def test_error_description_is_required(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="ERROR-002",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    with pytest.raises(
        ValueError
    ):
        twin.fail(
            "ERROR-002",
            error="",
        )


def test_error_state_is_terminal(
    twin,
    synthetic_text,
):
    twin.ingest(
        case_id="ERROR-003",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.fail(
        "ERROR-003",

        error="Test error.",
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.preprocess(
            "ERROR-003"
        )


# ============================================================
# COMPLETED STATE IS TERMINAL
# ============================================================

def test_completed_case_cannot_fail(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="TERMINAL-001",
    )

    twin.review(
        "TERMINAL-001",

        decision="accept",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason="Reviewed.",
    )

    twin.complete(
        "TERMINAL-001"
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.fail(
            "TERMINAL-001",

            error=(
                "Should not be possible."
            ),
        )


def test_completed_case_cannot_complete_twice(
    twin,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="TERMINAL-002",
    )

    twin.review(
        "TERMINAL-002",

        decision="accept",

        reviewer_identity=(
            "test-reviewer"
        ),

        reason="Reviewed.",
    )

    twin.complete(
        "TERMINAL-002"
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.complete(
            "TERMINAL-002"
        )


# ============================================================
# PERSISTENCE
# ============================================================

def test_completed_human_review_is_persisted(
    twin,
    store,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="PERSIST-001",
    )

    twin.review(
        "PERSIST-001",

        decision="amend",

        reviewer_identity=(
            "persist-reviewer"
        ),

        reason=(
            "Persistence verification."
        ),

        amended_category="C02",
    )

    twin.complete(
        "PERSIST-001"
    )

    case = store.get(
        "PERSIST-001"
    )

    assert (
        case[
            "state"
        ]
        == State.COMPLETED.value
    )

    assert (
        case[
            "review"
        ][
            "reviewer_identity"
        ]
        == "persist-reviewer"
    )

    assert (
        case[
            "review"
        ][
            "decision"
        ]
        == "amend"
    )

    assert (
        case[
            "final_category"
        ]
        == "C02"
    )


# ============================================================
# AUDIT EVENTS
# ============================================================

def test_full_workflow_audit_chain_passes(
    twin,
    audit,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AUDIT-WORKFLOW",
    )

    twin.review(
        "AUDIT-WORKFLOW",

        decision="accept",

        reviewer_identity=(
            "audit-reviewer"
        ),

        reason=(
            "Audit verification."
        ),
    )

    twin.complete(
        "AUDIT-WORKFLOW"
    )

    assert (
        audit.verify()
        is True
    )


def test_completed_case_has_expected_audit_actions(
    twin,
    audit,
    prediction,
    explanation,
    synthetic_text,
):
    create_case_at_review(
        twin,
        prediction,
        explanation,
        synthetic_text,
        case_id="AUDIT-ACTIONS",
    )

    twin.review(
        "AUDIT-ACTIONS",

        decision="accept",

        reviewer_identity=(
            "audit-reviewer"
        ),

        reason="Reviewed.",
    )

    twin.complete(
        "AUDIT-ACTIONS"
    )

    events = audit.events(
        "AUDIT-ACTIONS"
    )

    actions = [
        event[
            "action"
        ]
        for event
        in events
    ]

    assert (
        "CASE_INGESTED"
        in actions
    )

    assert (
        "CASE_PREPROCESSED"
        in actions
    )

    assert (
        "MODEL_PREDICTION_RECORDED"
        in actions
    )

    assert (
        "EXPLANATION_RECORDED"
        in actions
    )

    assert (
        "HUMAN_REVIEW_REQUIRED"
        in actions
    )

    assert (
        "HUMAN_REVIEW_ACCEPT"
        in actions
    )

    assert (
        "CASE_COMPLETED"
        in actions
    )


def test_invalid_transition_is_audited(
    twin,
    audit,
    prediction,
    synthetic_text,
):
    twin.ingest(
        case_id="AUDIT-INVALID",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    with pytest.raises(
        RuntimeError
    ):
        twin.attach_prediction(
            "AUDIT-INVALID",
            prediction,
        )

    events = audit.events(
        "AUDIT-INVALID"
    )

    actions = [
        event[
            "action"
        ]
        for event
        in events
    ]

    assert (
        "INVALID_TRANSITION_ATTEMPT"
        in actions
    )

    assert (
        audit.verify()
        is True
    )


# ============================================================
# NO AUTO-ACCEPTANCE SEMANTICS
# ============================================================

def test_twin_exposes_no_auto_accept_method(
    twin,
):
    assert not hasattr(
        twin,
        "auto_accept"
    )

    assert not hasattr(
        twin,
        "automatic_accept"
    )


def test_high_confidence_does_not_bypass_review(
    twin,
    explanation,
    synthetic_text,
):
    """
    Even an artificially near-certain prediction must still
    enter mandatory human review.
    """

    high_confidence = (
        PredictionResult(
            recommendation="C01",

            predicted_class_id=1,

            calibrated_confidence=(
                0.999999
            ),

            raw_confidence=(
                0.999999
            ),

            top3=[
                RankedPrediction(
                    rank=1,
                    category="C01",
                    probability=(
                        0.999999
                    ),
                ),

                RankedPrediction(
                    rank=2,
                    category="C02",
                    probability=(
                        0.0000006
                    ),
                ),

                RankedPrediction(
                    rank=3,
                    category="C03",
                    probability=(
                        0.0000004
                    ),
                ),
            ],

            temperature=(
                0.18388931380527324
            ),

            input_tokens=100,

            truncated=False,

            source_mode=(
                "fresh_frozen_inference"
            ),
        )
    )

    twin.ingest(
        case_id="HIGH-CONFIDENCE",

        source_mode="synthetic_note",

        clinical_text=synthetic_text,
    )

    twin.preprocess(
        "HIGH-CONFIDENCE"
    )

    twin.attach_prediction(
        "HIGH-CONFIDENCE",
        high_confidence,
    )

    twin.attach_explanation(
        "HIGH-CONFIDENCE",
        explanation,
    )

    case = twin.send_for_review(
        "HIGH-CONFIDENCE"
    )

    assert (
        case[
            "state"
        ]
        == (
            State
            .AWAITING_HUMAN_REVIEW
            .value
        )
    )

    assert (
        case[
            "governance"
        ][
            "automatic_acceptance"
        ]
        is False
    )

    assert (
        case[
            "governance"
        ][
            "human_review_required"
        ]
        is True
    )