from __future__ import annotations

import json
from pathlib import Path

import pytest

from operational_coding_twin.audit_log import (
    AppendOnlyAuditLog,
    AuditIntegrityError,
)

from operational_coding_twin.case_store import (
    CaseStore,
)

from operational_coding_twin.config import (
    CALIBRATOR_REFERENCE,
    CLAIMS_REFERENCE,
    CONFIDENCE_WARNING,
    EXPLANATION_WARNING,
    FROZEN_TEMPERATURE,
    MODEL_REFERENCE,
    get_settings,
)


# ============================================================
# CONFIGURATION
# ============================================================

def test_project_root_exists():
    settings = get_settings()

    assert settings.project_root.exists()
    assert settings.project_root.is_dir()


def test_project_root_is_expected_repository():
    settings = get_settings()

    assert (
        settings.project_root.name
        == "operational_coding_twin"
    )


def test_artifact_directories_are_under_project_root():
    settings = get_settings()

    expected_artifacts = (
        settings.project_root
        / "artifacts"
    )

    assert (
        settings.artifacts_dir
        == expected_artifacts
    )

    assert (
        settings.model_dir
        == expected_artifacts
        / "model"
    )

    assert (
        settings.calibration_dir
        == expected_artifacts
        / "calibration"
    )

    assert (
        settings.replay_dir
        == expected_artifacts
        / "replay"
    )

    assert (
        settings.governance_dir
        == expected_artifacts
        / "governance"
    )

    assert (
        settings.provenance_dir
        == expected_artifacts
        / "provenance"
    )


def test_runtime_directories_exist():
    settings = get_settings()

    assert settings.runtime_dir.exists()
    assert settings.cases_dir.exists()
    assert settings.explanations_dir.exists()
    assert settings.audit_dir.exists()
    assert settings.errors_dir.exists()


# ============================================================
# FROZEN GOVERNANCE CONSTANTS
# ============================================================

def test_frozen_temperature_constant():
    assert (
        FROZEN_TEMPERATURE
        == pytest.approx(
            0.1838893138,
            abs=1e-12,
        )
    )


def test_model_reference_is_frozen_seed42():
    assert (
        "SEED42"
        in MODEL_REFERENCE.upper()
    )


def test_calibrator_reference_is_phase8():
    assert (
        "P8"
        in CALIBRATOR_REFERENCE.upper()
    )

    assert (
        "0.1838893138"
        in CALIBRATOR_REFERENCE
    )


def test_claims_reference_is_phase10():
    assert (
        "P10"
        in CLAIMS_REFERENCE.upper()
    )


def test_confidence_warning_is_not_clinical_probability():
    text = CONFIDENCE_WARNING.lower()

    assert (
        "descriptive"
        in text
    )

    assert (
        "not"
        in text
    )

    assert (
        "correctness"
        in text
        or
        "clinical"
        in text
    )


def test_explanation_warning_is_non_causal():
    text = EXPLANATION_WARNING.lower()

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


# ============================================================
# CASE STORE
# ============================================================

def test_case_store_save_and_load(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    payload = {
        "case_id": "CASE-001",
        "state": "Ingested",
        "prediction": None,
    }

    saved_path = store.save(
        "CASE-001",
        payload,
    )

    assert saved_path.exists()

    loaded = store.get(
        "CASE-001"
    )

    assert loaded == payload


def test_case_store_exists(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    payload = {
        "case_id": "CASE-002",
        "state": "Ingested",
    }

    assert (
        store.exists(
            "CASE-002"
        )
        is False
    )

    store.save(
        "CASE-002",
        payload,
    )

    assert (
        store.exists(
            "CASE-002"
        )
        is True
    )


def test_case_store_unknown_case_raises(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    with pytest.raises(
        KeyError
    ):
        store.get(
            "UNKNOWN"
        )


def test_case_store_payload_id_must_match(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    payload = {
        "case_id": "CASE-A",
        "state": "Ingested",
    }

    with pytest.raises(
        ValueError
    ):
        store.save(
            "CASE-B",
            payload,
        )


def test_case_store_list_all(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    for index in range(
        3
    ):
        case_id = (
            f"CASE-{index}"
        )

        store.save(
            case_id,
            {
                "case_id": case_id,
                "state": "Ingested",
            },
        )

    cases = store.list_all()

    assert len(
        cases
    ) == 3

    assert {
        case[
            "case_id"
        ]
        for case
        in cases
    } == {
        "CASE-0",
        "CASE-1",
        "CASE-2",
    }


def test_case_store_count(
    tmp_path: Path,
):
    store = CaseStore(
        tmp_path
        / "cases"
    )

    assert store.count() == 0

    store.save(
        "ONE",
        {
            "case_id": "ONE",
            "state": "Ingested",
        },
    )

    assert store.count() == 1


# ============================================================
# AUDIT LOG
# ============================================================

def test_audit_append_and_verify(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    event = audit.append(
        case_id="AUDIT-001",
        actor="system",
        action="CASE_INGESTED",
        reason="Foundation test.",
        from_state=None,
        to_state="Ingested",
        payload={
            "test": True
        },
    )

    assert (
        event[
            "case_id"
        ]
        == "AUDIT-001"
    )

    assert (
        "event_hash"
        in event
    )

    assert (
        audit.verify()
        is True
    )


def test_audit_chain_links_events(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    first = audit.append(
        case_id="AUDIT-002",
        actor="system",
        action="INGEST",
        reason="Test ingest.",
        from_state=None,
        to_state="Ingested",
    )

    second = audit.append(
        case_id="AUDIT-002",
        actor="system",
        action="PREPROCESS",
        reason="Test preprocessing.",
        from_state="Ingested",
        to_state="Preprocessed",
    )

    assert (
        second[
            "previous_event_hash"
        ]
        == first[
            "event_hash"
        ]
    )

    assert (
        audit.verify()
        is True
    )


def test_audit_filter_by_case(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    audit.append(
        case_id="CASE-A",
        actor="system",
        action="TEST",
        reason="Case A.",
        from_state=None,
        to_state="Ingested",
    )

    audit.append(
        case_id="CASE-B",
        actor="system",
        action="TEST",
        reason="Case B.",
        from_state=None,
        to_state="Ingested",
    )

    case_a_events = audit.events(
        "CASE-A"
    )

    assert len(
        case_a_events
    ) == 1

    assert (
        case_a_events[
            0
        ][
            "case_id"
        ]
        == "CASE-A"
    )


def test_audit_requires_case_id(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    with pytest.raises(
        ValueError
    ):
        audit.append(
            case_id="",
            actor="system",
            action="TEST",
            reason="Test.",
            from_state=None,
            to_state="Ingested",
        )


def test_audit_requires_actor(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    with pytest.raises(
        ValueError
    ):
        audit.append(
            case_id="CASE",
            actor="",
            action="TEST",
            reason="Test.",
            from_state=None,
            to_state="Ingested",
        )


def test_audit_requires_reason(
    tmp_path: Path,
):
    audit = AppendOnlyAuditLog(
        tmp_path
        / "audit.jsonl"
    )

    with pytest.raises(
        ValueError
    ):
        audit.append(
            case_id="CASE",
            actor="system",
            action="TEST",
            reason="",
            from_state=None,
            to_state="Ingested",
        )


# ============================================================
# TAMPER DETECTION
# ============================================================

def test_audit_detects_tampering(
    tmp_path: Path,
):
    path = (
        tmp_path
        / "audit.jsonl"
    )

    audit = AppendOnlyAuditLog(
        path
    )

    audit.append(
        case_id="TAMPER-001",
        actor="system",
        action="ORIGINAL_ACTION",
        reason="Original event.",
        from_state=None,
        to_state="Ingested",
    )

    assert (
        audit.verify()
        is True
    )

    # --------------------------------------------------------
    # Simulate modification of an existing audit event.
    # --------------------------------------------------------

    lines = (
        path.read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    event = json.loads(
        lines[
            0
        ]
    )

    event[
        "reason"
    ] = (
        "This event has been altered."
    )

    path.write_text(
        json.dumps(
            event
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        AuditIntegrityError
    ):
        audit.verify()