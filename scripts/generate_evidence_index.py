from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOCS_DIR = ROOT / "docs"
EVIDENCE_DIR = ROOT / "evidence"

MARKDOWN_OUTPUT = (
    DOCS_DIR
    / "final_evidence_index.md"
)

TOPIC_CSV_OUTPUT = (
    EVIDENCE_DIR
    / "evidence_index.csv"
)

VISUAL_CSV_OUTPUT = (
    EVIDENCE_DIR
    / "visual_evidence_register.csv"
)

ROOT_POINTER = (
    ROOT
    / "EVIDENCE.md"
)


# ============================================================
# EXACT RESEARCH QUESTION MAPPING
#
# Do not invent RQ/objective numbers here.
#
# These placeholders should later be replaced using the final
# frozen research specification.
# ============================================================

RQ_PENDING = (
    "SYNC_FROM_FROZEN_RESEARCH_SPEC"
)


# ============================================================
# TOPIC-FIRST LOOKUP DATA
# ============================================================

TOPICS = [
    {
        "id": "T01",
        "topic": "Dataset and frozen scientific scope",
        "requirements": (
            "OT-R01; OT-R02; OT-R18; OT-R46; OT-R49"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "artifacts/model/label_mapping.json",
            "artifacts/governance/final_claims_freeze.json",
            "docs/final_implementation_record.md",
        ],
        "verification": [
            "tests/test_frozen_resources.py",
            "tests/test_governance.py",
        ],
        "evidence": [
            "evidence/01_verification/frozen_scientific_contract.txt",
            "docs/final_requirements_traceability_matrix.md",
        ],
        "dissertation": [
            "Chapter 3 — Methodology",
            "Chapter 4 — System Design and Implementation",
            "Chapter 6 — Discussion and Limitations",
        ],
        "claim": (
            "The working application implements the frozen "
            "single-label 50-category synthetic ICD-10 "
            "research setting."
        ),
        "boundary": (
            "Does not establish performance on genuine NHS "
            "free text or clinical deployment readiness."
        ),
    },

    {
        "id": "T02",
        "topic": "Frozen BioClinicalBERT model",
        "requirements": (
            "OT-R01–OT-R06"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/frozen_resources.py",
            "src/operational_coding_twin/inference.py",
        ],
        "verification": [
            "tests/test_frozen_resources.py",
            "tests/test_inference.py",
        ],
        "evidence": [
            "artifacts/model/model.safetensors",
            "artifacts/model/config.json",
            "artifacts/model/tokenizer.json",
            "artifacts/model/tokenizer_config.json",
            "artifacts/model/label_mapping.json",
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],
        "dissertation": [
            "Chapter 3 — Predictive methodology",
            "Chapter 4 — Model integration",
            "Chapter 5 — Experimental results",
        ],
        "claim": (
            "Fresh synthetic cases use the frozen canonical "
            "seed-42 BioClinicalBERT model."
        ),
        "boundary": (
            "Application screenshots do not establish "
            "predictive superiority or external validity."
        ),
    },

    {
        "id": "T03",
        "topic": "Calibration and model confidence",
        "requirements": (
            "OT-R07–OT-R09; OT-R29; OT-R30"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/config.py",
            "src/operational_coding_twin/frozen_resources.py",
            "src/operational_coding_twin/inference.py",
        ],
        "verification": [
            "tests/test_frozen_resources.py",
            "tests/test_inference.py",
            "tests/test_governance.py",
        ],
        "evidence": [
            "artifacts/calibration/temperature_scaling.json",
            "evidence/02_replay/E03_replay_prediction.png",
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],
        "dissertation": [
            "Chapter 3 — Calibration methodology",
            "Chapter 4 — Confidence integration",
            "Chapter 5 — Calibration evaluation",
            "Chapter 6 — Uncertainty limitations",
        ],
        "claim": (
            "Runtime logits are transformed using the frozen "
            "validation-fitted scalar temperature before "
            "probabilities are displayed."
        ),
        "boundary": (
            "Calibrated confidence is descriptive model "
            "uncertainty, not a probability of coding "
            "correctness, billing correctness or clinical "
            "safety."
        ),
    },

    {
        "id": "T04",
        "topic": "Fresh synthetic inference",
        "requirements": (
            "OT-R01–OT-R09; OT-R43; OT-R46"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/inference.py",
            "app/streamlit_app.py",
        ],
        "verification": [
            "tests/test_inference.py",
        ],
        "evidence": [
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],
        "dissertation": [
            "Chapter 4 — Fresh synthetic-case inference",
        ],
        "claim": (
            "A new synthetic clinical note can be processed "
            "through frozen BioClinicalBERT inference and "
            "temperature calibration."
        ),
        "boundary": (
            "This is operational implementation evidence, "
            "not evidence of performance on authentic NHS "
            "clinical notes."
        ),
    },

    {
        "id": "T05",
        "topic": "Frozen validation replay",
        "requirements": (
            "OT-R15–OT-R18; OT-R45; OT-R47; OT-R48"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/frozen_resources.py",
            "src/operational_coding_twin/inference.py",
            "src/operational_coding_twin/explainability.py",
            "app/streamlit_app.py",
        ],
        "verification": [
            "tests/test_frozen_resources.py",
            "tests/test_inference.py",
            "tests/test_explainability.py",
        ],
        "evidence": [
            "artifacts/replay/deterministic_validation_sample_100.csv",
            "artifacts/replay/validation_calibrated_probabilities.npy",
            "artifacts/replay/layer_integrated_gradients_cases.csv",
            "evidence/02_replay/E02_replay_case_selected.png",
            "evidence/02_replay/E03_replay_prediction.png",
            "evidence/02_replay/E04_replay_xai.png",
        ],
        "dissertation": [
            "Chapter 4 — Deterministic operational replay",
            "Appendix — Demonstration protocol",
        ],
        "claim": (
            "Replay reconstructs workflow behaviour using "
            "frozen Phase 8B validation artefacts."
        ),
        "boundary": (
            "Replay is not a second experiment and does not "
            "constitute Phase 9 test evaluation."
        ),
    },

    {
        "id": "T06",
        "topic": "Explainable AI",
        "requirements": (
            "OT-R10–OT-R14; OT-R17"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/explainability.py",
        ],
        "verification": [
            "tests/test_explainability.py",
        ],
        "evidence": [
            "artifacts/replay/layer_integrated_gradients_cases.csv",
            "evidence/02_replay/E04_replay_xai.png",
            "evidence/03_fresh_inference/E08_fresh_lig.png",
        ],
        "dissertation": [
            "Chapter 3 — Explainability methodology",
            "Chapter 4 — XAI implementation",
            "Chapter 5 — XAI evaluation",
            "Chapter 6 — Interpretability limitations",
        ],
        "claim": (
            "The prototype integrates predicted-class "
            "Layer Integrated Gradients using 50 steps and "
            "the frozen PAD-content baseline."
        ),
        "boundary": (
            "Token attribution describes model behaviour; "
            "it is not causal clinical evidence."
        ),
    },

    {
        "id": "T07",
        "topic": "Operational digital-twin state machine",
        "requirements": (
            "OT-R19–OT-R35"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/digital_twin.py",
        ],
        "verification": [
            "tests/test_digital_twin.py",
            "tests/test_governance.py",
        ],
        "evidence": [
            "docs/final_implementation_record.md",
            "evidence/04_human_review/E05_awaiting_human_review.png",
            "evidence/04_human_review/E06_accepted_completed.png",
            "evidence/04_human_review/E09_amended_completed.png",
        ],
        "dissertation": [
            "Chapter 4 — Operational digital-twin architecture",
        ],
        "claim": (
            "Each coding case has an explicit persistent "
            "operational state and controlled state "
            "transitions."
        ),
        "boundary": (
            "The prototype is an operational workflow twin, "
            "not a physiological patient digital twin."
        ),
    },

    {
        "id": "T08",
        "topic": "Mandatory human review",
        "requirements": (
            "OT-R21; OT-R25; OT-R26; "
            "OT-R29; OT-R30; OT-R31"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/digital_twin.py",
            "app/streamlit_app.py",
        ],
        "verification": [
            "tests/test_digital_twin.py",
            "tests/test_governance.py",
        ],
        "evidence": [
            "evidence/04_human_review/E05_awaiting_human_review.png",
            "evidence/04_human_review/E06_accepted_completed.png",
            "evidence/04_human_review/E09_amended_completed.png",
        ],
        "dissertation": [
            "Chapter 4 — Human-in-the-loop workflow",
            "Chapter 6 — Governance discussion",
        ],
        "claim": (
            "Every model recommendation requires an explicit "
            "human-review decision before completion."
        ),
        "boundary": (
            "The implementation does not establish that "
            "human review improves real coder productivity "
            "or accuracy."
        ),
    },

    {
        "id": "T09",
        "topic": "Accept, Reject and Amend",
        "requirements": (
            "OT-R22–OT-R28; OT-R31"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/digital_twin.py",
            "app/streamlit_app.py",
        ],
        "verification": [
            "tests/test_digital_twin.py",
        ],
        "evidence": [
            "evidence/04_human_review/E06_accepted_completed.png",
            "evidence/04_human_review/E09_amended_completed.png",
        ],
        "dissertation": [
            "Chapter 4 — Human disposition workflow",
        ],
        "claim": (
            "The reviewer retains authority to accept, "
            "reject or amend the model recommendation."
        ),
        "boundary": (
            "Human authority is implemented structurally; "
            "no claim of improved clinical outcome is made."
        ),
    },

    {
        "id": "T10",
        "topic": "Case persistence",
        "requirements": (
            "OT-R36–OT-R38"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/case_store.py",
            "src/operational_coding_twin/digital_twin.py",
        ],
        "verification": [
            "tests/test_foundation.py",
            "tests/test_digital_twin.py",
        ],
        "evidence": [
            "runtime/cases/",
        ],
        "dissertation": [
            "Chapter 4 — Persistent case state",
        ],
        "claim": (
            "Operational case state persists independently "
            "of transient Streamlit interactions."
        ),
        "boundary": (
            "Local JSON persistence is a research-prototype "
            "storage mechanism rather than production EHR "
            "persistence."
        ),
    },

    {
        "id": "T11",
        "topic": "Auditability",
        "requirements": (
            "OT-R35; OT-R39–OT-R42"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/audit_log.py",
            "src/operational_coding_twin/digital_twin.py",
        ],
        "verification": [
            "tests/test_foundation.py",
            "tests/test_digital_twin.py",
        ],
        "evidence": [
            "evidence/05_audit/E10_audit_history.png",
            "evidence/05_audit/E11_audit_integrity_pass.png",
            "runtime/audit/",
        ],
        "dissertation": [
            "Chapter 4 — Audit architecture",
            "Chapter 6 — Governance and limitations",
        ],
        "claim": (
            "Operational events are linked through a "
            "SHA-256 tamper-evident hash chain."
        ),
        "boundary": (
            "The mechanism is tamper-evident, not immutable."
        ),
    },

    {
        "id": "T12",
        "topic": "No automatic acceptance",
        "requirements": (
            "OT-R29; OT-R30"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/digital_twin.py",
        ],
        "verification": [
            "tests/test_digital_twin.py",
            "tests/test_governance.py",
        ],
        "evidence": [
            "evidence/04_human_review/E05_awaiting_human_review.png",
        ],
        "dissertation": [
            "Chapter 4 — Decision-support governance",
            "Chapter 6 — Safety and limitations",
        ],
        "claim": (
            "High confidence cannot bypass mandatory human "
            "review."
        ),
        "boundary": (
            "Calibration is not used as an autonomous "
            "coding-correctness threshold."
        ),
    },

    {
        "id": "T13",
        "topic": "Phase 9 / test-partition isolation",
        "requirements": (
            "OT-R18"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "src/operational_coding_twin/frozen_resources.py",
            "src/operational_coding_twin/inference.py",
        ],
        "verification": [
            "tests/test_frozen_resources.py",
            "tests/test_governance.py",
            "scripts/verify_project.py",
        ],
        "evidence": [
            "artifacts/provenance/working_artifact_manifest.json",
            "evidence/01_verification/project_verification.txt",
        ],
        "dissertation": [
            "Chapter 3 — Experimental protocol",
            "Chapter 5 — Final evaluation",
            "Appendix — Reproducibility",
        ],
        "claim": (
            "Phase 9 test prediction artefacts are not "
            "operational runtime dependencies."
        ),
        "boundary": (
            "Phase 9 remains legitimate final scientific "
            "evaluation evidence and is deliberately "
            "separate from runtime replay."
        ),
    },

    {
        "id": "T14",
        "topic": "Reproducibility and SHA-256 provenance",
        "requirements": (
            "OT-R50"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "scripts/freeze_working_build.py",
        ],
        "verification": [
            "artifacts/provenance/working_artifact_manifest.sha256",
        ],
        "evidence": [
            "artifacts/provenance/source_artifact_hashes.json",
            "artifacts/provenance/working_artifact_manifest.json",
            "artifacts/provenance/working_artifact_manifest.sha256",
            "evidence/06_provenance/E12_manifest_sha256_verified.png",
            "evidence/06_provenance/manifest_verification.txt",
        ],
        "dissertation": [
            "Chapter 3 — Reproducibility",
            "Appendix — Provenance",
        ],
        "claim": (
            "The frozen working-copy implementation is "
            "fingerprinted using SHA-256."
        ),
        "boundary": (
            "The working manifest does not independently "
            "prove source-archive identity unless compared "
            "against authoritative source hashes."
        ),
    },

    {
        "id": "T15",
        "topic": "Automated implementation verification",
        "requirements": (
            "Cross-cutting"
        ),
        "rq_objective": RQ_PENDING,
        "implementation": [
            "tests/test_foundation.py",
            "tests/test_frozen_resources.py",
            "tests/test_inference.py",
            "tests/test_explainability.py",
            "tests/test_digital_twin.py",
            "tests/test_governance.py",
        ],
        "verification": [
            "runtime/pytest_full_results.txt",
            "evidence/01_verification/pytest_final_summary.txt",
            "evidence/01_verification/project_verification.txt",
        ],
        "evidence": [
            "evidence/01_verification/pytest_full_results.txt",
            "evidence/01_verification/pytest_final_summary.txt",
            "evidence/01_verification/project_verification.txt",
        ],
        "dissertation": [
            "Chapter 5 — Engineering verification",
            "Appendix — Full automated test output",
        ],
        "claim": (
            "The final operational prototype is subject to "
            "automated verification across scientific "
            "resources, inference, XAI, workflow and "
            "governance."
        ),
        "boundary": (
            "Software tests are engineering evidence and "
            "must not be presented as predictive model "
            "performance."
        ),
    },
]


# ============================================================
# VISUAL EVIDENCE REGISTER
# ============================================================

VISUAL_EVIDENCE = [
    {
        "id": "E01",
        "path": (
            "evidence/02_replay/"
            "E01_application_scope.png"
        ),
        "topic": "Application scope",
        "demonstrates": (
            "Synthetic/demo boundary, mandatory human review "
            "and application governance."
        ),
    },
    {
        "id": "E02",
        "path": (
            "evidence/02_replay/"
            "E02_replay_case_selected.png"
        ),
        "topic": "Frozen validation replay",
        "demonstrates": (
            "Selection of a deterministic Phase 8B "
            "validation replay case."
        ),
    },
    {
        "id": "E03",
        "path": (
            "evidence/02_replay/"
            "E03_replay_prediction.png"
        ),
        "topic": "Replay prediction",
        "demonstrates": (
            "Top-1, Top-3 and calibrated probability display "
            "during frozen validation replay."
        ),
    },
    {
        "id": "E04",
        "path": (
            "evidence/02_replay/"
            "E04_replay_xai.png"
        ),
        "topic": "Replay explainability",
        "demonstrates": (
            "Frozen Phase 8B LIG evidence displayed within "
            "the operational workflow."
        ),
    },
    {
        "id": "E05",
        "path": (
            "evidence/04_human_review/"
            "E05_awaiting_human_review.png"
        ),
        "topic": "Mandatory human review",
        "demonstrates": (
            "AI recommendation reaching the explicit human "
            "review gate."
        ),
    },
    {
        "id": "E06",
        "path": (
            "evidence/04_human_review/"
            "E06_accepted_completed.png"
        ),
        "topic": "Acceptance workflow",
        "demonstrates": (
            "Human acceptance followed by explicit workflow "
            "completion."
        ),
    },
    {
        "id": "E07",
        "path": (
            "evidence/03_fresh_inference/"
            "E07_fresh_prediction.png"
        ),
        "topic": "Fresh frozen-model inference",
        "demonstrates": (
            "New synthetic-note inference using the frozen "
            "BioClinicalBERT model."
        ),
    },
    {
        "id": "E08",
        "path": (
            "evidence/03_fresh_inference/"
            "E08_fresh_lig.png"
        ),
        "topic": "Fresh Layer Integrated Gradients",
        "demonstrates": (
            "Runtime 50-step predicted-class LIG evidence."
        ),
    },
    {
        "id": "E09",
        "path": (
            "evidence/04_human_review/"
            "E09_amended_completed.png"
        ),
        "topic": "Human amendment",
        "demonstrates": (
            "Human reviewer replacing an AI recommendation "
            "with another valid frozen ICD-10 category."
        ),
    },
    {
        "id": "E10",
        "path": (
            "evidence/05_audit/"
            "E10_audit_history.png"
        ),
        "topic": "Operational audit history",
        "demonstrates": (
            "Ordered operational events for a coding case."
        ),
    },
    {
        "id": "E11",
        "path": (
            "evidence/05_audit/"
            "E11_audit_integrity_pass.png"
        ),
        "topic": "Audit integrity",
        "demonstrates": (
            "Successful verification of the tamper-evident "
            "audit hash chain."
        ),
    },
    {
        "id": "E12",
        "path": (
            "evidence/06_provenance/"
            "E12_manifest_sha256_verified.png"
        ),
        "topic": "Working-build provenance",
        "demonstrates": (
            "Successful SHA-256 verification of the frozen "
            "working-build manifest."
        ),
    },
]


# ============================================================
# NON-VISUAL EVIDENCE
# ============================================================

NON_VISUAL = [
    {
        "name": "Full pytest output",
        "path": (
            "evidence/01_verification/"
            "pytest_full_results.txt"
        ),
        "purpose": (
            "Detailed automated implementation verification."
        ),
    },
    {
        "name": "Final pytest summary",
        "path": (
            "evidence/01_verification/"
            "pytest_final_summary.txt"
        ),
        "purpose": (
            "Concise final automated verification result."
        ),
    },
    {
        "name": "Project verifier",
        "path": (
            "evidence/01_verification/"
            "project_verification.txt"
        ),
        "purpose": (
            "End-to-end project verification."
        ),
    },
    {
        "name": "Frozen scientific contract",
        "path": (
            "evidence/01_verification/"
            "frozen_scientific_contract.txt"
        ),
        "purpose": (
            "Human-readable frozen runtime configuration."
        ),
    },
    {
        "name": "Original source provenance",
        "path": (
            "evidence/06_provenance/"
            "source_artifact_hashes.json"
        ),
        "purpose": (
            "Source research artefact provenance."
        ),
    },
    {
        "name": "Working-build manifest",
        "path": (
            "evidence/06_provenance/"
            "working_artifact_manifest.json"
        ),
        "purpose": (
            "Frozen working implementation fingerprint."
        ),
    },
    {
        "name": "Working-build checksum",
        "path": (
            "evidence/06_provenance/"
            "working_artifact_manifest.sha256"
        ),
        "purpose": (
            "SHA-256 checksum for the working manifest."
        ),
    },
    {
        "name": "Manifest verification",
        "path": (
            "evidence/06_provenance/"
            "manifest_verification.txt"
        ),
        "purpose": (
            "Recorded successful SHA-256 verification."
        ),
    },
]


def exists(
    relative_path: str,
) -> bool:
    return (
        ROOT
        / relative_path
    ).exists()


def md_paths(
    values: list[str],
) -> str:
    return "<br>".join(
        f"`{value}`"
        for value in values
    )


def md_text_list(
    values: list[str],
) -> str:
    return "<br>".join(
        values
    )


def visual_status(
    item: dict,
) -> str:
    return (
        "VERIFIED"
        if exists(
            item["path"]
        )
        else "MISSING"
    )


def topic_primary_status(
    item: dict,
) -> str:
    paths = (
        item["implementation"]
        + item["verification"]
        + item["evidence"]
    )

    # Runtime directories and screenshots may legitimately
    # not exist before the final evidence capture.
    checkable = [
        path
        for path in paths
        if not path.endswith("/")
        and not path.endswith(".png")
    ]

    if all(
        exists(path)
        for path in checkable
    ):
        return "AVAILABLE"

    return "PARTIAL"


def write_topic_csv() -> None:
    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "topic_id",
        "topic",
        "requirements",
        "rq_objective",
        "implementation",
        "verification",
        "evidence",
        "dissertation_location",
        "supported_claim",
        "claim_boundary",
        "status",
    ]

    with TOPIC_CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in TOPICS:
            writer.writerow(
                {
                    "topic_id":
                        item["id"],

                    "topic":
                        item["topic"],

                    "requirements":
                        item["requirements"],

                    "rq_objective":
                        item["rq_objective"],

                    "implementation":
                        "; ".join(
                            item[
                                "implementation"
                            ]
                        ),

                    "verification":
                        "; ".join(
                            item[
                                "verification"
                            ]
                        ),

                    "evidence":
                        "; ".join(
                            item[
                                "evidence"
                            ]
                        ),

                    "dissertation_location":
                        "; ".join(
                            item[
                                "dissertation"
                            ]
                        ),

                    "supported_claim":
                        item["claim"],

                    "claim_boundary":
                        item["boundary"],

                    "status":
                        topic_primary_status(
                            item
                        ),
                }
            )


def write_visual_csv() -> None:
    fields = [
        "evidence_id",
        "topic",
        "file",
        "demonstrates",
        "status",
    ]

    with VISUAL_CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in VISUAL_EVIDENCE:
            writer.writerow(
                {
                    "evidence_id":
                        item["id"],

                    "topic":
                        item["topic"],

                    "file":
                        item["path"],

                    "demonstrates":
                        item[
                            "demonstrates"
                        ],

                    "status":
                        visual_status(
                            item
                        ),
                }
            )


def build_markdown() -> str:
    lines: list[str] = []

    lines.extend(
        [
            "# Final Evidence and Traceability Index",
            "",
            "**Document version:** 1.0.0  ",
            "**Purpose:** Repository evidence lookup and dissertation traceability  ",
            "**Runtime boundary:** Synthetic/demo data and frozen Phase 8B validation replay only  ",
            "",
            "---",
            "",
            "# 1. Purpose",
            "",
            "This document is the primary topic-first evidence lookup for the repository.",
            "",
            "It answers:",
            "",
            "> Where is the evidence supporting a particular implementation or research claim?",
            "",
            "The evidence chain is:",
            "",
            "```text",
            "Research / governance requirement",
            "        ↓",
            "Implementation",
            "        ↓",
            "Automated verification",
            "        ↓",
            "Evidence artefact",
            "        ↓",
            "Dissertation interpretation",
            "```",
            "",
            "Screenshots are implementation evidence and must not be treated as predictive-performance evidence.",
            "",
            "---",
            "",
            "# 2. Quick Evidence Lookup",
            "",
            "| ID | Topic | Requirement | Primary evidence | Status |",
            "|---|---|---|---|---|",
        ]
    )

    for item in TOPICS:
        evidence = (
            item["evidence"][0]
            if item["evidence"]
            else "-"
        )

        lines.append(
            f"| {item['id']} "
            f"| {item['topic']} "
            f"| {item['requirements']} "
            f"| `{evidence}` "
            f"| {topic_primary_status(item)} |"
        )

    for number, item in enumerate(
        TOPICS,
        start=3,
    ):
        lines.extend(
            [
                "",
                "---",
                "",
                f"# {number}. {item['topic']}",
                "",
                "## Requirements",
                "",
                f"`{item['requirements']}`",
                "",
                "## Frozen RQ / Objective",
                "",
                f"`{item['rq_objective']}`",
                "",
                "## Implementation",
                "",
            ]
        )

        for path in item[
            "implementation"
        ]:
            lines.append(
                f"- `{path}`"
            )

        lines.extend(
            [
                "",
                "## Verification",
                "",
            ]
        )

        for path in item[
            "verification"
        ]:
            lines.append(
                f"- `{path}`"
            )

        lines.extend(
            [
                "",
                "## Evidence",
                "",
            ]
        )

        for path in item[
            "evidence"
        ]:
            status = (
                "AVAILABLE"
                if exists(path)
                else "MISSING"
            )

            lines.append(
                f"- `{path}` — {status}"
            )

        lines.extend(
            [
                "",
                "## Dissertation location",
                "",
            ]
        )

        for location in item[
            "dissertation"
        ]:
            lines.append(
                f"- {location}"
            )

        lines.extend(
            [
                "",
                "## Supported claim",
                "",
                item["claim"],
                "",
                "## Claim boundary",
                "",
                item["boundary"],
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Visual Evidence Register",
            "",
            "| ID | Topic | File | Demonstrates | Status |",
            "|---|---|---|---|---|",
        ]
    )

    for item in VISUAL_EVIDENCE:
        lines.append(
            f"| {item['id']} "
            f"| {item['topic']} "
            f"| `{item['path']}` "
            f"| {item['demonstrates']} "
            f"| {visual_status(item)} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Non-Visual Evidence Register",
            "",
            "| Evidence | Location | Purpose | Status |",
            "|---|---|---|---|",
        ]
    )

    for item in NON_VISUAL:
        status = (
            "AVAILABLE"
            if exists(
                item["path"]
            )
            else "MISSING"
        )

        lines.append(
            f"| {item['name']} "
            f"| `{item['path']}` "
            f"| {item['purpose']} "
            f"| {status} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Dissertation Mapping",
            "",
            "| Evidence area | Recommended location |",
            "|---|---|",
            "| Scientific scope | Chapter 3 — Methodology |",
            "| Dataset/task contract | Chapter 3 — Methodology |",
            "| Frozen model | Chapters 3 and 4 |",
            "| Calibration methodology | Chapter 3 |",
            "| Calibration results | Chapter 5 |",
            "| Fresh inference | Chapter 4 |",
            "| Validation replay | Chapter 4 |",
            "| XAI methodology | Chapter 3 |",
            "| XAI implementation | Chapter 4 |",
            "| XAI interpretation | Chapters 5 and 6 |",
            "| Digital-twin state machine | Chapter 4 |",
            "| Human review | Chapter 4 |",
            "| Accept/Reject/Amend | Chapter 4 |",
            "| Auditability | Chapter 4 |",
            "| Automated software verification | Chapter 5 |",
            "| Predictive experimental results | Chapter 5 |",
            "| Limitations | Chapter 6 |",
            "| Provenance | Chapter 3 / Appendix |",
            "| Full test output | Appendix |",
            "| Requirements traceability | Appendix |",
            "",
            "---",
            "",
            "# Research Question Synchronisation",
            "",
            "The exact final Research Question and Objective identifiers must be copied from the frozen research specification.",
            "",
            "They are intentionally not guessed in this evidence index.",
            "",
            "Replace:",
            "",
            f"`{RQ_PENDING}`",
            "",
            "only after checking the authoritative frozen research specification.",
            "",
            "---",
            "",
            "# Claims That Must Not Be Made From Implementation Evidence",
            "",
            "The evidence package does not establish:",
            "",
            "- real NHS predictive performance;",
            "- clinical effectiveness;",
            "- prospective coding safety;",
            "- billing correctness;",
            "- coder productivity improvement;",
            "- production readiness;",
            "- external generalisation;",
            "- autonomous coding safety.",
            "",
            "---",
            "",
            "# Reviewer Navigation",
            "",
            "Recommended repository review order:",
            "",
            "```text",
            "README.md",
            "   ↓",
            "EVIDENCE.md",
            "   ↓",
            "docs/final_evidence_index.md",
            "   ↓",
            "docs/final_implementation_record.md",
            "   ↓",
            "docs/final_requirements_traceability_matrix.md",
            "   ↓",
            "evidence/",
            "   ↓",
            "tests/",
            "   ↓",
            "src/operational_coding_twin/",
            "   ↓",
            "artifacts/provenance/",
            "```",
            "",
            "---",
            "",
            "# Final Evidence Status",
            "",
        ]
    )

    visual_available = sum(
        1
        for item in VISUAL_EVIDENCE
        if exists(
            item["path"]
        )
    )

    non_visual_available = sum(
        1
        for item in NON_VISUAL
        if exists(
            item["path"]
        )
    )

    lines.extend(
        [
            f"Visual evidence available: **{visual_available}/{len(VISUAL_EVIDENCE)}**",
            "",
            f"Non-visual evidence available: **{non_visual_available}/{len(NON_VISUAL)}**",
            "",
            "Evidence index status:",
            "",
            (
                "**COMPLETE**"
                if (
                    visual_available
                    == len(
                        VISUAL_EVIDENCE
                    )
                    and
                    non_visual_available
                    == len(
                        NON_VISUAL
                    )
                )
                else "**IN PROGRESS**"
            ),
            "",
        ]
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


def write_root_pointer() -> None:
    content = """# Project Evidence

The primary evidence lookup for this repository is:

[`docs/final_evidence_index.md`](docs/final_evidence_index.md)

Machine-readable indexes:

- [`evidence/evidence_index.csv`](evidence/evidence_index.csv)
- [`evidence/visual_evidence_register.csv`](evidence/visual_evidence_register.csv)

The index maps research/governance topics to:

- implementation source;
- automated verification;
- frozen and runtime artefacts;
- screenshots;
- dissertation sections;
- bounded claims;
- implementation requirements.

The evidence package intentionally separates scientific evaluation evidence from operational implementation evidence.
"""

    ROOT_POINTER.write_text(
        content,
        encoding="utf-8",
    )


def main() -> None:
    DOCS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_topic_csv()
    write_visual_csv()

    MARKDOWN_OUTPUT.write_text(
        build_markdown(),
        encoding="utf-8",
    )

    write_root_pointer()

    print(
        "Evidence lookup generated:"
    )

    print(
        f"  {MARKDOWN_OUTPUT}"
    )

    print(
        f"  {TOPIC_CSV_OUTPUT}"
    )

    print(
        f"  {VISUAL_CSV_OUTPUT}"
    )

    print(
        f"  {ROOT_POINTER}"
    )

    print()
    print(
        "STEP 18B: PASS"
    )


if __name__ == "__main__":
    main()