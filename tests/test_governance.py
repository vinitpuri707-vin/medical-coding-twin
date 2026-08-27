from __future__ import annotations

import json
from pathlib import Path

from operational_coding_twin.config import (
    CALIBRATOR_REFERENCE,
    CLAIMS_REFERENCE,
    CONFIDENCE_WARNING,
    EXPLANATION_WARNING,
    MODEL_REFERENCE,
    get_settings,
)

from operational_coding_twin.digital_twin import (
    State,
    VALID_TRANSITIONS,
)


# ============================================================
# HELPERS
# ============================================================

def _find_key_recursive(
    data,
    key: str,
):
    if isinstance(data, dict):

        if key in data:
            return data[key]

        for value in data.values():
            result = _find_key_recursive(
                value,
                key,
            )

            if result is not None:
                return result

    elif isinstance(data, list):

        for value in data:
            result = _find_key_recursive(
                value,
                key,
            )

            if result is not None:
                return result

    return None


# ============================================================
# SCIENTIFIC ARTEFACT SEPARATION
# ============================================================

def test_runtime_artifacts_are_separate_from_runtime_cases():
    settings = get_settings()

    assert (
        settings.artifacts_dir
        != settings.runtime_dir
    )

    assert (
        settings.model_dir
        != settings.cases_dir
    )


def test_runtime_directories_are_not_inside_model_directory():
    settings = get_settings()

    model_root = (
        settings.model_dir.resolve()
    )

    runtime_paths = [
        settings.runtime_dir,
        settings.cases_dir,
        settings.explanations_dir,
        settings.audit_dir,
        settings.errors_dir,
    ]

    for path in runtime_paths:

        resolved = (
            path.resolve()
        )

        assert not (
            resolved == model_root
            or model_root in resolved.parents
        )


# ============================================================
# FROZEN GOVERNANCE REFERENCES
# ============================================================

def test_model_reference_points_to_canonical_seed42():
    text = MODEL_REFERENCE.upper()

    assert "SEED42" in text
    assert "CANONICAL" in text


def test_calibrator_reference_points_to_phase8b():
    text = CALIBRATOR_REFERENCE.upper()

    assert "P8B" in text

    assert (
        "0.1838893138"
        in CALIBRATOR_REFERENCE
    )


def test_claims_reference_points_to_phase10():
    assert (
        "P10"
        in CLAIMS_REFERENCE.upper()
    )


# ============================================================
# CLAIMS FREEZE
# ============================================================

def test_final_claims_freeze_exists():
    settings = get_settings()

    assert (
        settings.claims_file.is_file()
    )


def test_final_claims_freeze_requires_human_review():
    settings = get_settings()

    claims = json.loads(
        settings
        .claims_file
        .read_text(
            encoding="utf-8"
        )
    )

    value = _find_key_recursive(
        claims,
        "human_review_required",
    )

    assert value is True


def test_final_claims_freeze_disables_automatic_acceptance():
    settings = get_settings()

    claims = json.loads(
        settings
        .claims_file
        .read_text(
            encoding="utf-8"
        )
    )

    value = _find_key_recursive(
        claims,
        "automatic_acceptance",
    )

    assert value is False


# ============================================================
# WARNING CONTRACT
# ============================================================

def test_confidence_warning_does_not_claim_coding_correctness():
    warning = (
        CONFIDENCE_WARNING.lower()
    )

    assert "descriptive" in warning
    assert "not" in warning

    assert (
        "coding correctness"
        in warning
        or
        "correctness"
        in warning
    )


def test_confidence_warning_does_not_claim_clinical_safety():
    warning = (
        CONFIDENCE_WARNING.lower()
    )

    assert (
        "clinical"
        in warning
    )

    assert (
        "not"
        in warning
    )


def test_explanation_warning_rejects_causal_interpretation():
    warning = (
        EXPLANATION_WARNING.lower()
    )

    assert "not" in warning

    assert (
        "causal"
        in warning
    )


# ============================================================
# HUMAN-REVIEW STATE CONTRACT
# ============================================================

def test_model_cannot_transition_directly_to_acceptance():
    assert (
        State.ACCEPTED
        not in VALID_TRANSITIONS[
            State.PREDICTED
        ]
    )


def test_explanation_cannot_transition_directly_to_acceptance():
    assert (
        State.ACCEPTED
        not in VALID_TRANSITIONS[
            State.EXPLAINED
        ]
    )


def test_only_human_review_state_reaches_review_decisions():
    review_states = {
        State.ACCEPTED,
        State.REJECTED,
        State.AMENDED,
    }

    assert (
        review_states
        .issubset(
            VALID_TRANSITIONS[
                State.AWAITING_HUMAN_REVIEW
            ]
        )
    )

    for state in (
        State.INGESTED,
        State.PREPROCESSED,
        State.PREDICTED,
        State.EXPLAINED,
    ):

        assert not (
            review_states
            & VALID_TRANSITIONS[state]
        )


def test_review_outcomes_require_explicit_completion():
    for state in (
        State.ACCEPTED,
        State.REJECTED,
        State.AMENDED,
    ):

        assert (
            State.COMPLETED
            in VALID_TRANSITIONS[
                state
            ]
        )


def test_completed_state_is_terminal():
    assert (
        VALID_TRANSITIONS[
            State.COMPLETED
        ]
        == set()
    )


def test_error_state_is_terminal():
    assert (
        VALID_TRANSITIONS[
            State.ERROR
        ]
        == set()
    )


# ============================================================
# APPLICATION SOURCE GOVERNANCE
# ============================================================

def test_application_source_exists():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    assert app_file.is_file()


def test_application_identifies_synthetic_demo_scope():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    source = (
        app_file
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert "synthetic" in source

    assert (
        "identifiable"
        in source
    )


def test_application_exposes_human_review():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    source = (
        app_file
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert (
        "mandatory human review"
        in source
    )

    assert (
        "reviewer identity"
        in source
    )


def test_application_exposes_accept_reject_amend():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    source = (
        app_file
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert '"accept"' in source
    assert '"reject"' in source
    assert '"amend"' in source


# ============================================================
# TEST-PARTITION SEPARATION
# ============================================================

def test_runtime_artifact_paths_do_not_point_to_phase9():
    settings = get_settings()

    runtime_dependencies = [
        settings.model_file,
        settings.config_file,
        settings.tokenizer_file,
        settings.tokenizer_config_file,
        settings.label_mapping_file,
        settings.temperature_file,
        settings.replay_sample_file,
        settings.replay_probabilities_file,
        settings.replay_explanations_file,
        settings.claims_file,
        settings.hash_manifest_file,
    ]

    forbidden = (
        "phase9",
        "test_predictions",
        "transformer_test",
        "baseline_test",
        "test_logits",
        "test_probabilities",
    )

    for path in runtime_dependencies:

        text = str(
            path
        ).lower()

        assert not any(
            term in text
            for term in forbidden
        ), (
            "Prohibited test artefact dependency: "
            f"{path}"
        )


def test_replay_filename_is_validation_scoped():
    settings = get_settings()

    filename = (
        settings
        .replay_probabilities_file
        .name
        .lower()
    )

    assert (
        "validation"
        in filename
    )

    assert (
        "test"
        not in filename
    )


# ============================================================
# RESEARCH / OPERATIONAL BOUNDARY
# ============================================================

def test_app_does_not_contain_training_call():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    source = (
        app_file
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    # The UI should never initiate a Hugging Face
    # training workflow.

    assert ".train(" not in source

    assert "trainer(" not in source


def test_app_does_not_expose_threshold_based_acceptance():
    settings = get_settings()

    app_file = (
        settings.project_root
        / "app"
        / "streamlit_app.py"
    )

    source = (
        app_file
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert (
        "auto_accept("
        not in source
    )

    assert (
        "automatic_accept("
        not in source
    )


# ============================================================
# REQUIRED WORKING DIRECTORIES
# ============================================================

def test_required_runtime_directories_exist():
    settings = get_settings()

    required = [
        settings.runtime_dir,
        settings.cases_dir,
        settings.explanations_dir,
        settings.audit_dir,
        settings.errors_dir,
    ]

    for directory in required:

        assert directory.exists()

        assert directory.is_dir()