from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    ROOT
    / "docs"
    / "final_requirements_traceability_matrix.md"
)


REQUIREMENTS = [
    (
        "OT-R01",
        "The prototype shall operate on the frozen single-label 50-category ICD-10 task.",
        "`frozen_resources.py`, `inference.py`",
        "`test_frozen_resources.py`, `test_inference.py`",
        "`artifacts/model/label_mapping.json`",
    ),
    (
        "OT-R02",
        "Runtime model inference shall use the frozen canonical seed-42 BioClinicalBERT checkpoint.",
        "`frozen_resources.py`, `inference.py`",
        "`test_frozen_resources.py`, `test_inference.py`",
        "`artifacts/model/model.safetensors`",
    ),
    (
        "OT-R03",
        "Runtime inference shall not retrain or update model parameters.",
        "`frozen_resources.py`, `inference.py`, `streamlit_app.py`",
        "`test_governance.py`, `test_inference.py`",
        "Source code and pytest evidence",
    ),
    (
        "OT-R04",
        "Fresh clinical-text input shall use the frozen maximum sequence length of 320 tokens.",
        "`inference.py`",
        "`test_inference.py`",
        "Inference implementation",
    ),
    (
        "OT-R05",
        "Prediction shall return one Top-1 recommendation from the frozen category space.",
        "`inference.py`",
        "`test_inference.py`",
        "Runtime prediction records",
    ),
    (
        "OT-R06",
        "Prediction shall provide a Top-3 shortlist for reviewer support.",
        "`inference.py`, `streamlit_app.py`",
        "`test_inference.py`, `test_digital_twin.py`",
        "Persisted case prediction",
    ),
    (
        "OT-R07",
        "Confidence shall use the frozen Phase 8B scalar temperature calibration.",
        "`config.py`, `frozen_resources.py`, `inference.py`",
        "`test_frozen_resources.py`, `test_inference.py`",
        "`artifacts/calibration/temperature_scaling.json`",
    ),
    (
        "OT-R08",
        "Temperature scaling shall use the validation-fitted frozen temperature and shall not be refitted at runtime.",
        "`frozen_resources.py`, `inference.py`",
        "`test_frozen_resources.py`, `test_governance.py`",
        "`artifacts/calibration/temperature_scaling.json`",
    ),
    (
        "OT-R09",
        "Calibrated confidence shall be treated as descriptive model uncertainty rather than clinical or coding correctness.",
        "`config.py`, `streamlit_app.py`",
        "`test_foundation.py`, `test_governance.py`",
        "UI confidence warning",
    ),
    (
        "OT-R10",
        "Fresh explainability shall use Layer Integrated Gradients.",
        "`explainability.py`",
        "`test_explainability.py`",
        "Runtime explanation record",
    ),
    (
        "OT-R11",
        "Fresh Layer Integrated Gradients shall use exactly 50 integration steps.",
        "`explainability.py`",
        "`test_explainability.py`, `test_digital_twin.py`",
        "XAI implementation and tests",
    ),
    (
        "OT-R12",
        "Fresh Layer Integrated Gradients shall target the predicted class rather than a reference label.",
        "`explainability.py`",
        "`test_explainability.py`",
        "Predicted-class targeting test",
    ),
    (
        "OT-R13",
        "Layer Integrated Gradients shall use the PAD-content baseline with special tokens preserved.",
        "`explainability.py`",
        "`test_explainability.py`",
        "Baseline verification",
    ),
    (
        "OT-R14",
        "Explainability shall be represented as model-behaviour evidence rather than causal clinical evidence.",
        "`config.py`, `streamlit_app.py`",
        "`test_foundation.py`, `test_governance.py`",
        "XAI warning contract",
    ),
    (
        "OT-R15",
        "Frozen replay shall use only deterministic Phase 8B validation cases.",
        "`frozen_resources.py`, `inference.py`, `streamlit_app.py`",
        "`test_frozen_resources.py`, `test_inference.py`",
        "`artifacts/replay/deterministic_validation_sample_100.csv`",
    ),
    (
        "OT-R16",
        "Frozen validation replay shall use saved calibrated probabilities rather than a new model forward pass.",
        "`inference.py`",
        "`test_inference.py`",
        "`artifacts/replay/validation_calibrated_probabilities.npy`",
    ),
    (
        "OT-R17",
        "Frozen validation replay shall use saved Phase 8B LIG evidence rather than rerunning Captum.",
        "`explainability.py`",
        "`test_explainability.py`",
        "`artifacts/replay/layer_integrated_gradients_cases.csv`",
    ),
    (
        "OT-R18",
        "The operational application shall not depend on Phase 9 test predictions or test probabilities.",
        "`frozen_resources.py`, runtime artefact layout",
        "`test_frozen_resources.py`, `test_governance.py`, `verify_project.py`",
        "`artifacts/provenance/working_artifact_manifest.json`",
    ),
    (
        "OT-R19",
        "A coding case shall be represented by an explicit operational state.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "Persisted case JSON",
    ),
    (
        "OT-R20",
        "Legal workflow progression shall follow Ingested → Preprocessed → Predicted → Explained → Awaiting Human Review.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "State-transition and audit evidence",
    ),
    (
        "OT-R21",
        "Human review shall be mandatory before a coding disposition can complete.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`, `test_governance.py`",
        "`evidence/04_human_review/E05_awaiting_human_review.png`",
    ),
    (
        "OT-R22",
        "The system shall support explicit Accept decisions.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`",
        "`evidence/04_human_review/E06_accepted_completed.png`",
    ),
    (
        "OT-R23",
        "The system shall support explicit Reject decisions.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`",
        "Audit event and persisted case record",
    ),
    (
        "OT-R24",
        "The system shall support explicit Amend decisions.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`",
        "`evidence/04_human_review/E09_amended_completed.png`",
    ),
    (
        "OT-R25",
        "Reviewer identity shall be mandatory.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`",
        "Persisted human-review record",
    ),
    (
        "OT-R26",
        "A review reason shall be mandatory.",
        "`digital_twin.py`, `streamlit_app.py`",
        "`test_digital_twin.py`",
        "Persisted human-review record",
    ),
    (
        "OT-R27",
        "Amended categories shall remain within the frozen 50-category label space.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "Amendment validation evidence",
    ),
    (
        "OT-R28",
        "An amended category shall differ from the model recommendation.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "Amendment validation evidence",
    ),
    (
        "OT-R29",
        "Model confidence shall never automatically accept a recommendation.",
        "`digital_twin.py`",
        "`test_digital_twin.py`, `test_governance.py`",
        "Human-review governance tests",
    ),
    (
        "OT-R30",
        "Even a very high confidence prediction shall enter mandatory human review.",
        "`digital_twin.py`",
        "`test_high_confidence_does_not_bypass_review`",
        "High-confidence governance test",
    ),
    (
        "OT-R31",
        "Accepted, Rejected and Amended states shall require an explicit completion transition.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "State-machine tests",
    ),
    (
        "OT-R32",
        "Completed cases shall be terminal.",
        "`digital_twin.py`",
        "`test_digital_twin.py`, `test_governance.py`",
        "Terminal-state verification",
    ),
    (
        "OT-R33",
        "Error shall be represented as an explicit terminal operational state.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "Error-state verification",
    ),
    (
        "OT-R34",
        "Invalid state transitions shall be rejected.",
        "`digital_twin.py`",
        "`test_digital_twin.py`",
        "Invalid-transition tests",
    ),
    (
        "OT-R35",
        "Invalid state-transition attempts shall be recorded in the audit trail where the transition layer handles them.",
        "`digital_twin.py`, `audit_log.py`",
        "`test_digital_twin.py`",
        "Audit JSONL evidence",
    ),
    (
        "OT-R36",
        "Current digital-twin case state shall persist between application interactions.",
        "`case_store.py`, `digital_twin.py`",
        "`test_foundation.py`, `test_digital_twin.py`",
        "`runtime/cases/`",
    ),
    (
        "OT-R37",
        "Case persistence shall use deterministic safe filenames and atomic replacement.",
        "`case_store.py`",
        "`test_foundation.py`",
        "Case-store implementation",
    ),
    (
        "OT-R38",
        "Duplicate operational case identifiers shall not overwrite existing cases.",
        "`digital_twin.py`, `case_store.py`",
        "`test_digital_twin.py`",
        "Duplicate-case tests",
    ),
    (
        "OT-R39",
        "Operational events shall be appended to the audit log rather than editing earlier events.",
        "`audit_log.py`",
        "`test_foundation.py`, `test_digital_twin.py`",
        "`runtime/audit/`",
    ),
    (
        "OT-R40",
        "Audit events shall be linked using SHA-256 hashes.",
        "`audit_log.py`",
        "`test_foundation.py`",
        "Audit hash-chain evidence",
    ),
    (
        "OT-R41",
        "Modification of a previously recorded audit event shall be detectable.",
        "`audit_log.py`",
        "`test_foundation.py`",
        "Audit tamper-detection test",
    ),
    (
        "OT-R42",
        "The audit mechanism shall be described as tamper-evident rather than immutable.",
        "Documentation and UI terminology",
        "`test_governance.py`, documentation review",
        "`docs/final_implementation_record.md`",
    ),
    (
        "OT-R43",
        "The prototype shall support direct synthetic-note input.",
        "`streamlit_app.py`",
        "Manual UI verification",
        "`evidence/03_fresh_inference/E07_fresh_prediction.png`",
    ),
    (
        "OT-R44",
        "The prototype shall support synthetic CSV input containing clinical_text.",
        "`streamlit_app.py`",
        "Manual UI verification",
        "Streamlit prototype",
    ),
    (
        "OT-R45",
        "The prototype shall support frozen validation replay.",
        "`streamlit_app.py`",
        "`test_inference.py`, `test_explainability.py`, manual UI verification",
        "`evidence/02_replay/`",
    ),
    (
        "OT-R46",
        "The UI shall state that synthetic/demo input should contain no real identifiable patient information.",
        "`streamlit_app.py`",
        "`test_governance.py`",
        "`evidence/02_replay/E01_application_scope.png`",
    ),
    (
        "OT-R47",
        "Replay ground truth shall not be exposed during the human-review decision.",
        "`streamlit_app.py`",
        "Manual workflow inspection",
        "Frozen replay workflow",
    ),
    (
        "OT-R48",
        "Replay reference category may be revealed only after workflow completion.",
        "`streamlit_app.py`",
        "Manual workflow inspection",
        "Completed replay case",
    ),
    (
        "OT-R49",
        "Frozen research artefacts shall remain separate from runtime-created cases, explanations and audit files.",
        "Repository structure and `config.py`",
        "`test_governance.py`",
        "Frozen/runtime directory separation",
    ),
    (
        "OT-R50",
        "The completed working build shall be reproducibly fingerprinted using SHA-256.",
        "`scripts/freeze_working_build.py`",
        "Manifest SHA-256 verification",
        "`artifacts/provenance/working_artifact_manifest.json`",
    ),
]


def validate_requirements() -> None:
    if len(REQUIREMENTS) != 50:
        raise RuntimeError(
            f"Expected exactly 50 requirements, found {len(REQUIREMENTS)}."
        )

    actual_ids = [
        row[0]
        for row in REQUIREMENTS
    ]

    expected_ids = [
        f"OT-R{i:02d}"
        for i in range(1, 51)
    ]

    if actual_ids != expected_ids:
        raise RuntimeError(
            "Requirement IDs are not exactly OT-R01 through OT-R50."
        )


def build_markdown() -> str:
    lines = [
        "# Final Requirements Traceability Matrix",
        "",
        "**Document version:** 1.0.0  ",
        "**Project:** AI-Powered Operational Digital Twin for Automated Medical Coding  ",
        "**Scope:** Frozen operational research prototype  ",
        "**Runtime boundary:** Synthetic/demo data and frozen Phase 8B validation replay only  ",
        "",
        "---",
        "",
        "# 1. Purpose",
        "",
        "This matrix maps each final operational requirement to its implementation, verification mechanism and evidence artefact.",
        "",
        "The traceability chain is:",
        "",
        "```text",
        "Requirement",
        "    ↓",
        "Implementation",
        "    ↓",
        "Verification",
        "    ↓",
        "Evidence",
        "    ↓",
        "Bounded dissertation claim",
        "```",
        "",
        "---",
        "",
        "# 2. Final Requirements",
        "",
        "| ID | Requirement | Implementation | Verification | Evidence | Status |",
        "|---|---|---|---|---|---|",
    ]

    for (
        requirement_id,
        requirement,
        implementation,
        verification,
        evidence,
    ) in REQUIREMENTS:
        lines.append(
            f"| {requirement_id} "
            f"| {requirement} "
            f"| {implementation} "
            f"| {verification} "
            f"| {evidence} "
            f"| COMPLETE |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# 3. Governance Summary",
            "",
            "| Constraint | Final status |",
            "|---|---|",
            "| Single-label 50-category task | FROZEN |",
            "| Canonical model | Seed-42 BioClinicalBERT |",
            "| Runtime retraining | DISABLED |",
            "| Runtime recalibration | DISABLED |",
            "| Calibration | Frozen validation-fitted scalar temperature |",
            "| Fresh XAI | 50-step predicted-class Layer Integrated Gradients |",
            "| Replay | Phase 8B deterministic validation sample |",
            "| Phase 9 runtime dependency | NONE |",
            "| Automatic acceptance | DISABLED |",
            "| Human review | REQUIRED |",
            "| Reviewer identity | REQUIRED |",
            "| Review reason | REQUIRED |",
            "| Audit terminology | TAMPER-EVIDENT |",
            "",
            "---",
            "",
            "# 4. Evidence Interpretation Boundary",
            "",
            "The implementation evidence supports the claim that a frozen medical-coding model can be integrated into a state-driven, explainable, human-reviewed and auditable operational prototype.",
            "",
            "It does **not** establish:",
            "",
            "- real NHS predictive performance;",
            "- clinical effectiveness;",
            "- coding reimbursement correctness;",
            "- prospective patient-safety performance;",
            "- external NHS generalisation;",
            "- production deployment readiness;",
            "- autonomous coding safety.",
            "",
            "---",
            "",
            "# 5. Research-Level Traceability",
            "",
            "This implementation RTM uses OT-R01 through OT-R50.",
            "",
            "It must not silently replace the frozen research-level objectives, research questions or research-governance traceability matrix.",
            "",
            "Exact Research Question and Objective identifiers should be cross-referenced from the authoritative frozen research specification.",
            "",
            "---",
            "",
            "# 6. Final Status",
            "",
            f"Total implementation requirements: **{len(REQUIREMENTS)}**",
            "",
            "Completed implementation requirements: **50**",
            "",
            "**Traceability status: COMPLETE**",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    validate_requirements()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        build_markdown(),
        encoding="utf-8",
    )

    print(
        f"Generated: {OUTPUT}"
    )

    print(
        f"Requirements: {len(REQUIREMENTS)}"
    )

    print()
    print(
        "STEP 17C RTM REPAIR: PASS"
    )


if __name__ == "__main__":
    main()