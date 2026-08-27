from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DOCS_DIR = ROOT / "docs"
EVIDENCE_DIR = ROOT / "evidence"

TRACEABILITY_MD = (
    DOCS_DIR
    / "final_research_traceability.md"
)

TRACEABILITY_CSV = (
    EVIDENCE_DIR
    / "research_traceability.csv"
)

OBJECTIVES_CSV = (
    EVIDENCE_DIR
    / "research_objectives.csv"
)

TRACEABILITY_JSON = (
    EVIDENCE_DIR
    / "research_traceability.json"
)

EVIDENCE_INDEX = (
    DOCS_DIR
    / "final_evidence_index.md"
)

ROOT_EVIDENCE_POINTER = (
    ROOT
    / "EVIDENCE.md"
)


# ============================================================
# GOVERNANCE VERSIONS
# ============================================================

RESEARCH_SPEC_VERSION = "2.0.0"
RESEARCH_SPEC_EFFECTIVE_DATE = "2026-08-17"

PROTOCOL_VERSION = "2.0.1"

POST_TEST_GOVERNANCE_VERSION = "2.1.0"
POST_TEST_GOVERNANCE_DATE = "2026-08-22"

DATASET_VERSION = "BNS-CCB-2.0.0"


# ============================================================
# EXACT FROZEN AIM
#
# Source:
# Frozen Research Specification v2.0.0
# ============================================================

AIM = (
    "To design, implement and critically evaluate a reproducible "
    "AI-powered operational digital-twin research prototype for "
    "50-category ICD-10 recommendation from NHS-aligned synthetic "
    "clinical text, incorporating comparative modelling, calibration, "
    "explainability, shortcut analysis and auditable human review."
)


# ============================================================
# EXACT FROZEN SMART OBJECTIVES
# ============================================================

OBJECTIVES = {
    "O1": {
        "title": (
            "Freeze and validate the BNS-CCB v2 benchmark"
        ),
        "text": (
            "Use the released BNS-CCB-2.0.0 modelling contract "
            "without altering its label space or supplied "
            "patient-family split. Verify dataset provenance, "
            "checksums, the 2,500-record/1,281-patient/50-category "
            "structure, the 1,750/375/375 train/validation/test "
            "allocation, and the rule that clinical_text is the only "
            "predictive feature. Preserve the test partition until "
            "the Phase 8 protocol is frozen."
        ),
    },

    "O2": {
        "title": (
            "Establish controlled predictive comparators"
        ),
        "text": (
            "Evaluate the implemented TF-IDF (word 1–2 grams) + "
            "balanced multinomial logistic regression baseline and "
            "the primary BioClinicalBERT 50-way sequence classifier "
            "using the same frozen BNS-CCB train/validation "
            "partitions. Preserve the seed-42 canonical "
            "BioClinicalBERT run and quantify transformer variability "
            "using the pre-declared seeds 42, 43 and 44 without using "
            "the test partition."
        ),
    },

    "O3": {
        "title": (
            "Quantify predictive performance, robustness and "
            "failure modes"
        ),
        "text": (
            "Report accuracy, balanced accuracy, micro-F1, macro "
            "precision/recall/F1, weighted-F1, top-3/top-5 accuracy, "
            "log loss and per-class error analysis. Report the "
            "lexical baseline even when it outperforms the "
            "transformer. Evaluate shortcut sensitivity and report "
            "mean ± sample standard deviation across the three "
            "deterministic transformer seeds once Phase 7B is "
            "executed."
        ),
    },

    "O4": {
        "title": (
            "Evaluate probability reliability and explanation quality"
        ),
        "text": (
            "Using the frozen seed-42 validation logits/probabilities, "
            "report uncalibrated negative log-likelihood, multiclass "
            "Brier score and Expected Calibration Error (ECE). Fit "
            "any selected post-hoc calibration method on validation "
            "data only. Generate token-level explanations for the "
            "frozen transformer and perform at least one quantitative "
            "faithfulness or stability evaluation. Calibration and "
            "XAI methods must be fixed before test access."
        ),
    },

    "O5": {
        "title": (
            "Implement and verify the operational digital twin"
        ),
        "text": (
            "Implement an event-driven prototype that carries a coding "
            "case through ingestion, preprocessing, prediction, "
            "ranked alternatives, calibrated confidence, explanation, "
            "human review and completion/error states. The reviewer "
            "must be able to accept, reject or amend a recommendation, "
            "and material state transitions must be recorded in an "
            "append-only audit history. Automated tests and at least "
            "one reproducible end-to-end demonstration are required."
        ),
    },
}


# ============================================================
# EXACT FROZEN RESEARCH QUESTIONS
# ============================================================

RESEARCH_QUESTIONS = {
    "RQ1": {
        "title": (
            "Benchmark validity and shortcut risk"
        ),
        "question": (
            "To what extent does BNS-CCB-2.0.0 provide a "
            "reproducible and leakage-controlled synthetic benchmark "
            "for 50-category ICD-10 recommendation, and what "
            "synthetic shortcut risks remain after patient-family "
            "separation and text-only feature enforcement?"
        ),
    },

    "RQ2": {
        "title": (
            "Predictive comparison"
        ),
        "question": (
            "How does BioClinicalBERT compare with the TF-IDF "
            "multinomial logistic-regression baseline for single-label "
            "50-category ICD-10 recommendation under the same frozen "
            "BNS-CCB partitions?"
        ),
    },

    "RQ3": {
        "title": (
            "Calibration and reliability"
        ),
        "question": (
            "How well calibrated are the frozen transformer's "
            "predicted probabilities, and can a validation-fitted "
            "post-hoc calibration method improve probability "
            "reliability without using test data for fitting or "
            "selection?"
        ),
    },

    "RQ4": {
        "title": (
            "Explainability"
        ),
        "question": (
            "To what extent do token-level attribution methods "
            "identify model-relevant evidence for ICD-10 "
            "recommendations, and how faithful or stable are those "
            "explanations under a pre-specified perturbation/stability "
            "evaluation?"
        ),
    },

    "RQ5": {
        "title": (
            "Operational digital twin"
        ),
        "question": (
            "Can ranked predictions, calibrated confidence, "
            "explanations and human accept/reject/amend decisions be "
            "represented in an event-driven operational digital twin "
            "with reproducible state transitions and an auditable "
            "case history?"
        ),
    },
}


# ============================================================
# FROZEN CONFIRMATORY HYPOTHESES
# ============================================================

HYPOTHESES = {
    "H1": {
        "title": "Predictive comparison",
        "null": (
            "On the locked BNS-CCB test partition, BioClinicalBERT "
            "does not improve the pre-declared primary predictive "
            "measure (macro-F1) over the TF-IDF logistic-regression "
            "baseline."
        ),
        "alternative": (
            "On the locked BNS-CCB test partition, BioClinicalBERT "
            "improves macro-F1 over the TF-IDF logistic-regression "
            "baseline."
        ),
        "result": (
            "NOT SUPPORTED"
        ),
    },

    "H2": {
        "title": "Calibration",
        "null": (
            "Validation-fitted post-hoc calibration does not improve "
            "probability calibration on the locked test partition."
        ),
        "alternative": (
            "Validation-fitted post-hoc calibration improves "
            "probability calibration on the locked test partition, "
            "evidenced by lower ECE and/or multiclass Brier score "
            "and/or NLL, while discrimination is reported separately."
        ),
        "result": (
            "SUPPORTED"
        ),
    },
}


# ============================================================
# FROZEN PHASE 9 / 10 RESULTS
# ============================================================

FINAL_RESULTS = {
    "baseline_accuracy": 1.0000,
    "baseline_macro_f1": 1.000000,

    "transformer_accuracy": 0.9120,
    "transformer_macro_f1": 0.878264,

    "transformer_minus_baseline_macro_f1": -0.121736,
    "h1_ci_lower": -0.129076,
    "h1_ci_upper": -0.112000,

    "raw_nll": 1.421040,
    "calibrated_nll": 0.235008,

    "nll_difference": -1.186032,
    "nll_ci_lower": -1.257841,
    "nll_ci_upper": -1.114956,

    "raw_brier": 0.5160255455212994,
    "calibrated_brier": 0.12275846411598085,

    "raw_ece_15": 0.5825058279792223,
    "calibrated_ece_15": 0.053714356051539874,

    "transformer_test_errors": 33,
    "top3_test_accuracy": 1.0000,
}


# ============================================================
# FROZEN PHASE 10 CLAIMS
# ============================================================

FROZEN_CLAIMS = {
    "C1": (
        "The transformer-superiority hypothesis was not supported."
    ),
    "C2": (
        "The calibration hypothesis was supported."
    ),
    "C3": (
        "BNS-CCB is a synthetic benchmark and is susceptible to "
        "lexical/template shortcuts."
    ),
    "C4": (
        "The results do not establish generalisation to real NHS "
        "clinical data."
    ),
    "C5": (
        "Model predictions require human review."
    ),
}


# ============================================================
# FINAL RQ TRACEABILITY
#
# NOTE:
# research_archive_reference values are references to the
# separate research archive. They are deliberately not runtime
# application dependencies.
# ============================================================

RQ_TRACEABILITY = [
    {
        "rq_id": "RQ1",

        "objective_ids": [
            "O1",
            "O3",
        ],

        "research_phases": [
            "Phase 3 — benchmark construction/provenance",
            "Phase 5 — leakage and shortcut analysis",
            "Phase 10 — post-test failure analysis and claims freeze",
            "Phase 11A — post-test governance synchronisation",
        ],

        "research_archive_reference": [
            "BNS-CCB-2.0.0 release/audit package",
            "Phase 5 shortcut/leakage artefacts",
            "P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201",
            "POST_TEST_GOVERNANCE_UPDATE_v2.1.0",
        ],

        "implementation": [
            "artifacts/model/label_mapping.json",
            "artifacts/governance/final_claims_freeze.json",
            "src/operational_coding_twin/frozen_resources.py",
        ],

        "local_evidence": [
            "evidence/01_verification/frozen_scientific_contract.txt",
            "artifacts/provenance/source_artifact_hashes.json",
            "docs/final_implementation_record.md",
        ],

        "implementation_requirements": [
            "OT-R01",
            "OT-R02",
            "OT-R18",
            "OT-R46",
            "OT-R49",
        ],

        "final_answer": (
            "BNS-CCB-2.0.0 provides a reproducible frozen synthetic "
            "benchmark under the supplied patient-family split and "
            "clinical_text-only modelling contract, but the evidence "
            "also demonstrates substantial lexical/template shortcut "
            "risk. The perfect lexical-baseline test result is "
            "consistent with extreme synthetic separability. The "
            "benchmark therefore supports controlled methodological "
            "evaluation but does not establish real NHS "
            "generalisation."
        ),

        "claim_boundary": (
            "Do not interpret benchmark reproducibility as external "
            "clinical validity. BNS-CCB remains wholly synthetic."
        ),

        "dissertation_sections": [
            "Chapter 3 — Dataset, benchmark construction and validity controls",
            "Chapter 5 — Shortcut/failure analysis",
            "Chapter 6 — Validity limitations and NHS generalisation",
        ],

        "status": (
            "ANSWERED_WITH_MAJOR_VALIDITY_LIMITATION"
        ),
    },

    {
        "rq_id": "RQ2",

        "objective_ids": [
            "O2",
            "O3",
        ],

        "research_phases": [
            "Phase 6 — TF-IDF/logistic-regression baseline",
            "Phase 7 — canonical BioClinicalBERT",
            "Phase 7B — three-seed robustness",
            "Phase 9 — one-shot confirmatory test",
            "Phase 10 — post-test error analysis",
        ],

        "research_archive_reference": [
            "Phase 6 frozen lexical baseline",
            "P7-BIOCLINICALBERT-SEED42-CANONICAL",
            "P7-BIOCLINICALBERT-3SEED-ROBUSTNESS-v1",
            "P9-ONESHOT-CONFIRMATORY-v201-SEED42",
            "P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201",
        ],

        "implementation": [
            "artifacts/model/model.safetensors",
            "artifacts/model/config.json",
            "src/operational_coding_twin/inference.py",
        ],

        "local_evidence": [
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
            "evidence/01_verification/frozen_scientific_contract.txt",
        ],

        "implementation_requirements": [
            "OT-R01",
            "OT-R02",
            "OT-R03",
            "OT-R04",
            "OT-R05",
            "OT-R06",
        ],

        "final_answer": (
            "BioClinicalBERT did not outperform the frozen lexical "
            "baseline. On the locked one-shot test partition, the "
            "TF-IDF/logistic-regression baseline achieved macro-F1 "
            "1.000000, whereas BioClinicalBERT achieved macro-F1 "
            "0.878264. The transformer-minus-baseline difference was "
            "-0.121736 with 95% CI [-0.129076, -0.112000]. "
            "Accordingly, the transformer-superiority hypothesis was "
            "not supported."
        ),

        "claim_boundary": (
            "The negative result must be retained. The operational "
            "prototype must not be used to imply transformer "
            "superiority."
        ),

        "dissertation_sections": [
            "Chapter 3 — Comparative modelling methodology",
            "Chapter 5 — Predictive comparison",
            "Chapter 6 — Interpretation of the negative result",
        ],

        "status": (
            "ANSWERED_NEGATIVE_RESULT"
        ),
    },

    {
        "rq_id": "RQ3",

        "objective_ids": [
            "O4",
        ],

        "research_phases": [
            "Phase 8B-Corrective — validation-only temperature calibration",
            "Phase 9 — one-shot confirmatory calibration evaluation",
            "Phase 10 — final claims freeze",
        ],

        "research_archive_reference": [
            "P8B-CORRECTIVE-V201-SEED42",
            "P9-ONESHOT-CONFIRMATORY-v201-SEED42",
            "P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201",
        ],

        "implementation": [
            "artifacts/calibration/temperature_scaling.json",
            "src/operational_coding_twin/config.py",
            "src/operational_coding_twin/inference.py",
        ],

        "local_evidence": [
            "evidence/02_replay/E03_replay_prediction.png",
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],

        "implementation_requirements": [
            "OT-R07",
            "OT-R08",
            "OT-R09",
            "OT-R29",
            "OT-R30",
        ],

        "final_answer": (
            "Validation-fitted scalar temperature calibration "
            "substantially improved probability reliability on the "
            "locked test partition. NLL decreased from 1.421040 to "
            "0.235008; multiclass Brier score decreased from "
            "0.516026 to 0.122758; and 15-bin ECE decreased from "
            "0.582506 to 0.053714. The primary calibrated-minus-raw "
            "NLL difference was -1.186032 with 95% CI "
            "[-1.257841, -1.114956]. The calibration hypothesis was "
            "therefore supported."
        ),

        "claim_boundary": (
            "Calibration improves probability reliability but does "
            "not convert confidence into a probability of clinical "
            "safety, coding correctness or billing correctness. "
            "No automatic acceptance threshold is authorised."
        ),

        "dissertation_sections": [
            "Chapter 3 — Calibration methodology",
            "Chapter 5 — Calibration results",
            "Chapter 6 — Confidence interpretation",
        ],

        "status": (
            "ANSWERED_H2_SUPPORTED"
        ),
    },

    {
        "rq_id": "RQ4",

        "objective_ids": [
            "O4",
        ],

        "research_phases": [
            "Phase 8A — XAI protocol freeze",
            "Phase 8B-Corrective — LIG and quantitative faithfulness evaluation",
            "Phase 11B — operational XAI integration",
        ],

        "research_archive_reference": [
            "P8B-CORRECTIVE-V201-SEED42",
            (
                "Deterministic validation n=100 Layer Integrated "
                "Gradients package"
            ),
            (
                "Top-10% positive-attribution masking versus "
                "20 deterministic random-mask comparisons"
            ),
        ],

        "implementation": [
            "src/operational_coding_twin/explainability.py",
            "artifacts/replay/layer_integrated_gradients_cases.csv",
        ],

        "local_evidence": [
            "evidence/02_replay/E04_replay_xai.png",
            "evidence/03_fresh_inference/E08_fresh_lig.png",
        ],

        "implementation_requirements": [
            "OT-R10",
            "OT-R11",
            "OT-R12",
            "OT-R13",
            "OT-R14",
            "OT-R17",
        ],

        "final_answer": (
            "The project implemented a pre-specified token-level "
            "explanation protocol using predicted-class Layer "
            "Integrated Gradients with 50 integration steps and a "
            "PAD-content baseline, and completed a quantitative "
            "faithfulness evaluation using targeted-token masking "
            "against deterministic random masking. This provides "
            "model-relevance and faithfulness evidence beyond visual "
            "inspection alone."
        ),

        "claim_boundary": (
            "Attribution is evidence about model behaviour. It is not "
            "causal clinical evidence and does not prove that a "
            "prediction is clinically correct."
        ),

        "dissertation_sections": [
            "Chapter 3 — Explainability methodology",
            "Chapter 4 — XAI integration",
            "Chapter 5 — Explanation evaluation",
            "Chapter 6 — Explainability limitations",
        ],

        "status": (
            "ANSWERED_WITH_BOUNDED_XAI_EVIDENCE"
        ),
    },

    {
        "rq_id": "RQ5",

        "objective_ids": [
            "O5",
        ],

        "research_phases": [
            "Phase 8B — frozen confidence/XAI inputs",
            "Phase 10 — human-review claims freeze",
            "Phase 11B — operational digital-twin implementation",
            "Steps 15–18 — final implementation/evidence verification",
        ],

        "research_archive_reference": [
            "P8B-CORRECTIVE-V201-SEED42",
            "P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201",
            "Phase 11B operational workflow evidence",
        ],

        "implementation": [
            "src/operational_coding_twin/digital_twin.py",
            "src/operational_coding_twin/case_store.py",
            "src/operational_coding_twin/audit_log.py",
            "src/operational_coding_twin/inference.py",
            "src/operational_coding_twin/explainability.py",
            "app/streamlit_app.py",
        ],

        "local_evidence": [
            "evidence/04_human_review/E05_awaiting_human_review.png",
            "evidence/04_human_review/E06_accepted_completed.png",
            "evidence/04_human_review/E09_amended_completed.png",
            "evidence/05_audit/E10_audit_history.png",
            "evidence/05_audit/E11_audit_integrity_pass.png",
            "evidence/01_verification/pytest_full_results.txt",
            "evidence/01_verification/project_verification.txt",
        ],

        "implementation_requirements": [
            "OT-R19–OT-R42",
            "OT-R43–OT-R49",
        ],

        "final_answer": (
            "Yes, the required information can be represented in an "
            "event-driven operational research prototype. The final "
            "implementation maintains explicit coding-case state, "
            "ranked model recommendations, calibrated descriptive "
            "confidence, explanations, mandatory human review, "
            "Accept/Reject/Amend decisions, persistent case "
            "disposition and a SHA-256 chained tamper-evident audit "
            "history."
        ),

        "claim_boundary": (
            "This answers the engineering feasibility question only. "
            "It does not demonstrate real NHS deployment readiness, "
            "clinical safety, coder productivity improvement or "
            "autonomous coding suitability."
        ),

        "dissertation_sections": [
            "Chapter 4 — Operational digital-twin architecture",
            "Chapter 4 — Human-review workflow",
            "Chapter 5 — Engineering verification",
            "Chapter 6 — Operational and clinical limitations",
        ],

        "status": (
            "ANSWERED_ENGINEERING_PROTOTYPE"
        ),
    },
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

BEGIN_MARKER = (
    "<!-- BEGIN: FROZEN_RESEARCH_TRACEABILITY -->"
)

END_MARKER = (
    "<!-- END: FROZEN_RESEARCH_TRACEABILITY -->"
)


def write_lf_text(
    path: Path,
    text: str,
) -> None:
    """
    Write UTF-8 using explicit LF bytes.

    This avoids Windows CRLF ambiguity when the repository
    is inspected from Git Bash.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        text.replace(
            "\r\n",
            "\n",
        )
        .replace(
            "\r",
            "\n",
        )
        .encode(
            "utf-8"
        )
    )


def bullet_list(
    values: list[str],
) -> list[str]:
    return [
        f"- {value}"
        for value in values
    ]


def code_bullet_list(
    values: list[str],
) -> list[str]:
    return [
        f"- `{value}`"
        for value in values
    ]


def semicolon(
    values: list[str],
) -> str:
    return "; ".join(
        values
    )


def find_rq_record(
    rq_id: str,
) -> dict:
    for record in RQ_TRACEABILITY:
        if record["rq_id"] == rq_id:
            return record

    raise KeyError(
        rq_id
    )


# ============================================================
# MARKDOWN GENERATION
# ============================================================

def build_traceability_markdown() -> str:
    lines: list[str] = []

    lines.extend(
        [
            "# Final Research Question and Evidence Traceability",
            "",
            "**Document version:** 1.0.0  ",
            f"**Frozen research specification:** v{RESEARCH_SPEC_VERSION}  ",
            f"**Frozen calibration/XAI/test protocol:** v{PROTOCOL_VERSION}  ",
            f"**Post-test governance status:** v{POST_TEST_GOVERNANCE_VERSION}  ",
            f"**Dataset:** {DATASET_VERSION}  ",
            "**Status:** FINAL RESEARCH TRACEABILITY",
            "",
            "---",
            "",
            "# 1. Governance hierarchy",
            "",
            "The final traceability hierarchy is:",
            "",
            "```text",
            "Frozen Research Specification v2.0.0",
            "        ↓",
            "Aim + O1–O5 + RQ1–RQ5",
            "        ↓",
            "Frozen Protocol v2.0.1",
            "        ↓",
            "Phase 7B / 8B / 9 / 10 scientific evidence",
            "        ↓",
            "Post-Test Governance v2.1.0",
            "        ↓",
            "Operational implementation",
            "        ↓",
            "Automated verification + evidence package",
            "        ↓",
            "Bounded dissertation conclusions",
            "```",
            "",
            "Research Specification v2.0.0 remains the frozen technical "
            "research specification. Protocol v2.0.1 freezes calibration, "
            "XAI and confirmatory-test procedure without replacing the "
            "research Aim, Objectives or Research Questions.",
            "",
            "---",
            "",
            "# 2. Frozen Aim",
            "",
            f"> {AIM}",
            "",
            "---",
            "",
            "# 3. Frozen SMART Objectives",
            "",
        ]
    )

    for objective_id, objective in OBJECTIVES.items():
        lines.extend(
            [
                f"## {objective_id} — {objective['title']}",
                "",
                objective["text"],
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "# 4. Frozen Research Questions",
            "",
        ]
    )

    for rq_id, rq in RESEARCH_QUESTIONS.items():
        lines.extend(
            [
                f"## {rq_id} — {rq['title']}",
                "",
                rq["question"],
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "# 5. Frozen Confirmatory Hypotheses",
            "",
        ]
    )

    for hypothesis_id, hypothesis in HYPOTHESES.items():
        lines.extend(
            [
                f"## {hypothesis_id} — {hypothesis['title']}",
                "",
                "**Null hypothesis**",
                "",
                hypothesis["null"],
                "",
                "**Alternative hypothesis**",
                "",
                hypothesis["alternative"],
                "",
                f"**Final outcome:** {hypothesis['result']}",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "# 6. Final Research-Question Traceability Matrix",
            "",
            "| RQ | Objective(s) | Experiment / evaluation | "
            "Implementation evidence | Final conclusion | Status |",
            "|---|---|---|---|---|---|",
        ]
    )

    for record in RQ_TRACEABILITY:
        rq_id = record["rq_id"]

        lines.append(
            "| "
            + rq_id
            + " | "
            + "<br>".join(
                record[
                    "objective_ids"
                ]
            )
            + " | "
            + "<br>".join(
                record[
                    "research_phases"
                ]
            )
            + " | "
            + "<br>".join(
                f"`{item}`"
                for item in record[
                    "local_evidence"
                ]
            )
            + " | "
            + record[
                "final_answer"
            ]
            + " | "
            + record[
                "status"
            ]
            + " |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# 7. Detailed RQ Evidence Chains",
            "",
        ]
    )

    for record in RQ_TRACEABILITY:
        rq_id = record["rq_id"]

        rq = RESEARCH_QUESTIONS[
            rq_id
        ]

        lines.extend(
            [
                f"## {rq_id} — {rq['title']}",
                "",
                "### Frozen question",
                "",
                rq["question"],
                "",
                "### Objective mapping",
                "",
            ]
        )

        lines.extend(
            bullet_list(
                record[
                    "objective_ids"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Experiment / evaluation programme",
                "",
            ]
        )

        lines.extend(
            bullet_list(
                record[
                    "research_phases"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Research-archive references",
                "",
            ]
        )

        lines.extend(
            bullet_list(
                record[
                    "research_archive_reference"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Operational implementation",
                "",
            ]
        )

        lines.extend(
            code_bullet_list(
                record[
                    "implementation"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Local evidence",
                "",
            ]
        )

        lines.extend(
            code_bullet_list(
                record[
                    "local_evidence"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Implementation requirements",
                "",
            ]
        )

        lines.extend(
            code_bullet_list(
                record[
                    "implementation_requirements"
                ]
            )
        )

        lines.extend(
            [
                "",
                "### Final answer",
                "",
                record[
                    "final_answer"
                ],
                "",
                "### Claim boundary",
                "",
                record[
                    "claim_boundary"
                ],
                "",
                "### Dissertation mapping",
                "",
            ]
        )

        lines.extend(
            bullet_list(
                record[
                    "dissertation_sections"
                ]
            )
        )

        lines.extend(
            [
                "",
                f"**RQ status:** `{record['status']}`",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "# 8. Frozen Final Test Results",
            "",
            "| Measure | Frozen result |",
            "|---|---:|",
            (
                "| TF-IDF baseline accuracy | "
                f"{FINAL_RESULTS['baseline_accuracy']:.4f} |"
            ),
            (
                "| TF-IDF baseline macro-F1 | "
                f"{FINAL_RESULTS['baseline_macro_f1']:.6f} |"
            ),
            (
                "| BioClinicalBERT accuracy | "
                f"{FINAL_RESULTS['transformer_accuracy']:.4f} |"
            ),
            (
                "| BioClinicalBERT macro-F1 | "
                f"{FINAL_RESULTS['transformer_macro_f1']:.6f} |"
            ),
            (
                "| Transformer − baseline macro-F1 | "
                f"{FINAL_RESULTS['transformer_minus_baseline_macro_f1']:.6f} |"
            ),
            (
                "| H1 95% CI | "
                f"[{FINAL_RESULTS['h1_ci_lower']:.6f}, "
                f"{FINAL_RESULTS['h1_ci_upper']:.6f}] |"
            ),
            (
                "| Raw NLL | "
                f"{FINAL_RESULTS['raw_nll']:.6f} |"
            ),
            (
                "| Calibrated NLL | "
                f"{FINAL_RESULTS['calibrated_nll']:.6f} |"
            ),
            (
                "| Calibrated − raw NLL | "
                f"{FINAL_RESULTS['nll_difference']:.6f} |"
            ),
            (
                "| H2 NLL 95% CI | "
                f"[{FINAL_RESULTS['nll_ci_lower']:.6f}, "
                f"{FINAL_RESULTS['nll_ci_upper']:.6f}] |"
            ),
            (
                "| Raw multiclass Brier | "
                f"{FINAL_RESULTS['raw_brier']:.6f} |"
            ),
            (
                "| Calibrated multiclass Brier | "
                f"{FINAL_RESULTS['calibrated_brier']:.6f} |"
            ),
            (
                "| Raw ECE (15 bins) | "
                f"{FINAL_RESULTS['raw_ece_15']:.6f} |"
            ),
            (
                "| Calibrated ECE (15 bins) | "
                f"{FINAL_RESULTS['calibrated_ece_15']:.6f} |"
            ),
            (
                "| Transformer test errors | "
                f"{FINAL_RESULTS['transformer_test_errors']} |"
            ),
            (
                "| Top-3 test accuracy | "
                f"{FINAL_RESULTS['top3_test_accuracy']:.4f} |"
            ),
            "",
            "---",
            "",
            "# 9. Frozen Final Claims",
            "",
        ]
    )

    for claim_id, claim in FROZEN_CLAIMS.items():
        lines.append(
            f"- **{claim_id}:** {claim}"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# 10. Final Aim Assessment",
            "",
            "**Aim status: ACHIEVED WITH EXPLICIT SCOPE LIMITATIONS**",
            "",
            "The assessed work has implemented the frozen comparative "
            "modelling, calibration, explainability, shortcut-analysis "
            "and auditable human-review components required by the "
            "v2.0.0 Aim.",
            "",
            "The Aim is satisfied as a research-prototype objective. "
            "It must not be interpreted as evidence of production NHS "
            "deployment readiness or real-world clinical generalisation.",
            "",
            "---",
            "",
            "# 11. Dissertation Claim Rule",
            "",
            "Every final dissertation conclusion should be traceable as:",
            "",
            "```text",
            "Aim",
            "  ↓",
            "Objective",
            "  ↓",
            "Research Question",
            "  ↓",
            "Method / Experiment",
            "  ↓",
            "Observed Evidence",
            "  ↓",
            "Implementation Evidence where applicable",
            "  ↓",
            "Bounded Conclusion",
            "```",
            "",
            "No UI screenshot should be used as evidence of predictive "
            "accuracy, and no predictive metric should be used as "
            "evidence that the operational state machine functions "
            "correctly.",
            "",
            "---",
            "",
            "**Final research traceability status: COMPLETE**",
            "",
        ]
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


# ============================================================
# CSV GENERATION
# ============================================================

def write_traceability_csv() -> None:
    fields = [
        "rq_id",
        "rq_title",
        "research_question",
        "objective_ids",
        "research_phases",
        "research_archive_reference",
        "implementation",
        "local_evidence",
        "implementation_requirements",
        "final_answer",
        "claim_boundary",
        "dissertation_sections",
        "status",
    ]

    TRACEABILITY_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TRACEABILITY_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            lineterminator="\n",
        )

        writer.writeheader()

        for record in RQ_TRACEABILITY:
            rq = RESEARCH_QUESTIONS[
                record["rq_id"]
            ]

            writer.writerow(
                {
                    "rq_id":
                        record["rq_id"],

                    "rq_title":
                        rq["title"],

                    "research_question":
                        rq["question"],

                    "objective_ids":
                        semicolon(
                            record[
                                "objective_ids"
                            ]
                        ),

                    "research_phases":
                        semicolon(
                            record[
                                "research_phases"
                            ]
                        ),

                    "research_archive_reference":
                        semicolon(
                            record[
                                "research_archive_reference"
                            ]
                        ),

                    "implementation":
                        semicolon(
                            record[
                                "implementation"
                            ]
                        ),

                    "local_evidence":
                        semicolon(
                            record[
                                "local_evidence"
                            ]
                        ),

                    "implementation_requirements":
                        semicolon(
                            record[
                                "implementation_requirements"
                            ]
                        ),

                    "final_answer":
                        record[
                            "final_answer"
                        ],

                    "claim_boundary":
                        record[
                            "claim_boundary"
                        ],

                    "dissertation_sections":
                        semicolon(
                            record[
                                "dissertation_sections"
                            ]
                        ),

                    "status":
                        record[
                            "status"
                        ],
                }
            )


def write_objectives_csv() -> None:
    fields = [
        "objective_id",
        "title",
        "objective",
        "research_questions",
        "status",
    ]

    objective_to_rqs: dict[
        str,
        list[str],
    ] = {
        objective_id: []
        for objective_id in OBJECTIVES
    }

    for record in RQ_TRACEABILITY:
        for objective_id in record[
            "objective_ids"
        ]:
            objective_to_rqs[
                objective_id
            ].append(
                record[
                    "rq_id"
                ]
            )

    with OBJECTIVES_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            lineterminator="\n",
        )

        writer.writeheader()

        for objective_id, objective in OBJECTIVES.items():
            writer.writerow(
                {
                    "objective_id":
                        objective_id,

                    "title":
                        objective["title"],

                    "objective":
                        objective["text"],

                    "research_questions":
                        semicolon(
                            objective_to_rqs[
                                objective_id
                            ]
                        ),

                    "status":
                        "COMPLETE",
                }
            )


# ============================================================
# JSON GENERATION
# ============================================================

def write_traceability_json() -> None:
    payload = {
        "schema_version":
            "1.0.0",

        "research_specification": {
            "version":
                RESEARCH_SPEC_VERSION,

            "effective_date":
                RESEARCH_SPEC_EFFECTIVE_DATE,

            "status":
                "FROZEN",
        },

        "protocol": {
            "version":
                PROTOCOL_VERSION,

            "status":
                "FROZEN",
        },

        "post_test_governance": {
            "version":
                POST_TEST_GOVERNANCE_VERSION,

            "record_date":
                POST_TEST_GOVERNANCE_DATE,

            "status":
                "FROZEN CLAIMS / STATUS LAYER",
        },

        "dataset":
            DATASET_VERSION,

        "aim":
            AIM,

        "objectives":
            OBJECTIVES,

        "research_questions":
            RESEARCH_QUESTIONS,

        "hypotheses":
            HYPOTHESES,

        "final_results":
            FINAL_RESULTS,

        "frozen_claims":
            FROZEN_CLAIMS,

        "research_traceability":
            RQ_TRACEABILITY,

        "boundaries": {
            "real_nhs_generalisation_claimed":
                False,

            "clinical_deployment_readiness_claimed":
                False,

            "automatic_acceptance":
                False,

            "human_review_required":
                True,

            "phase9_runtime_dependency":
                False,

            "xai_is_causal_clinical_evidence":
                False,
        },
    }

    write_lf_text(
        TRACEABILITY_JSON,
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )


# ============================================================
# EVIDENCE INDEX SYNCHRONISATION
# ============================================================

def build_index_section() -> str:
    lines = [
        BEGIN_MARKER,
        "",
        "# Frozen Research Governance and RQ Traceability",
        "",
        f"**Frozen research specification:** v{RESEARCH_SPEC_VERSION}  ",
        f"**Frozen protocol:** v{PROTOCOL_VERSION}  ",
        f"**Post-test governance:** v{POST_TEST_GOVERNANCE_VERSION}",
        "",
        "## Frozen Aim",
        "",
        f"> {AIM}",
        "",
        "## Objective → Research Question Lookup",
        "",
        "| Objective | Research question(s) | Primary purpose |",
        "|---|---|---|",
        (
            "| O1 | RQ1 | Benchmark validity, provenance, "
            "leakage/shortcut control |"
        ),
        (
            "| O2 | RQ2 | Controlled predictive comparators |"
        ),
        (
            "| O3 | RQ1; RQ2 | Robustness, predictive evaluation "
            "and failure analysis |"
        ),
        (
            "| O4 | RQ3; RQ4 | Calibration and explainability |"
        ),
        (
            "| O5 | RQ5 | Operational digital twin and "
            "human-review workflow |"
        ),
        "",
        "## Research Question → Evidence Lookup",
        "",
        "| RQ | Topic | Scientific evidence | "
        "Implementation/evidence | Final status |",
        "|---|---|---|---|---|",
    ]

    for record in RQ_TRACEABILITY:
        rq = RESEARCH_QUESTIONS[
            record["rq_id"]
        ]

        scientific = "<br>".join(
            record[
                "research_archive_reference"
            ]
        )

        local = "<br>".join(
            f"`{item}`"
            for item in record[
                "local_evidence"
            ]
        )

        lines.append(
            f"| {record['rq_id']} "
            f"| {rq['title']} "
            f"| {scientific} "
            f"| {local} "
            f"| {record['status']} |"
        )

    lines.extend(
        [
            "",
            "Full research traceability:",
            "",
            "- `docs/final_research_traceability.md`",
            "- `evidence/research_traceability.csv`",
            "- `evidence/research_objectives.csv`",
            "- `evidence/research_traceability.json`",
            "",
            END_MARKER,
        ]
    )

    return (
        "\n".join(
            lines
        )
    )


def replace_or_append_section(
    path: Path,
    section: str,
) -> None:
    if not path.is_file():
        raise RuntimeError(
            f"Required file is missing: {path}"
        )

    text = path.read_text(
        encoding="utf-8",
    )

    if (
        BEGIN_MARKER in text
        and
        END_MARKER in text
    ):
        before = text.split(
            BEGIN_MARKER,
            1,
        )[0]

        after = text.split(
            END_MARKER,
            1,
        )[1]

        text = (
            before.rstrip()
            + "\n\n"
            + section
            + "\n\n"
            + after.lstrip()
        )

    else:
        text = (
            text.rstrip()
            + "\n\n---\n\n"
            + section
            + "\n"
        )

    # Remove the old placeholder anywhere it survived.
    text = text.replace(
        "SYNC_FROM_FROZEN_RESEARCH_SPEC",
        "SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0",
    )

    write_lf_text(
        path,
        text,
    )


def update_evidence_pointer() -> None:
    if not ROOT_EVIDENCE_POINTER.is_file():
        return

    marker_begin = (
        "<!-- BEGIN: RESEARCH_TRACEABILITY_POINTER -->"
    )

    marker_end = (
        "<!-- END: RESEARCH_TRACEABILITY_POINTER -->"
    )

    section = "\n".join(
        [
            marker_begin,
            "",
            "## Research Traceability",
            "",
            "Frozen Aim, Objectives, Research Questions, experiment "
            "mapping and bounded final conclusions:",
            "",
            "- [`docs/final_research_traceability.md`]"
            "(docs/final_research_traceability.md)",
            "- [`evidence/research_traceability.csv`]"
            "(evidence/research_traceability.csv)",
            "- [`evidence/research_objectives.csv`]"
            "(evidence/research_objectives.csv)",
            "- [`evidence/research_traceability.json`]"
            "(evidence/research_traceability.json)",
            "",
            marker_end,
        ]
    )

    text = ROOT_EVIDENCE_POINTER.read_text(
        encoding="utf-8",
    )

    if (
        marker_begin in text
        and marker_end in text
    ):
        before = text.split(
            marker_begin,
            1,
        )[0]

        after = text.split(
            marker_end,
            1,
        )[1]

        text = (
            before.rstrip()
            + "\n\n"
            + section
            + "\n\n"
            + after.lstrip()
        )

    else:
        text = (
            text.rstrip()
            + "\n\n"
            + section
            + "\n"
        )

    write_lf_text(
        ROOT_EVIDENCE_POINTER,
        text,
    )


# ============================================================
# VERIFICATION
# ============================================================

def fail(
    message: str,
    failures: list[str],
) -> None:
    failures.append(
        message
    )

    print(
        f"FAIL: {message}"
    )


def verify() -> bool:
    failures: list[str] = []

    print()
    print(
        "=" * 76
    )
    print(
        "STEP 19 — RESEARCH TRACEABILITY VERIFICATION"
    )
    print(
        "=" * 76
    )

    required_files = [
        TRACEABILITY_MD,
        TRACEABILITY_CSV,
        OBJECTIVES_CSV,
        TRACEABILITY_JSON,
        EVIDENCE_INDEX,
    ]

    for path in required_files:
        if path.is_file():
            print(
                f"PASS: {path.relative_to(ROOT)}"
            )
        else:
            fail(
                (
                    "Missing file: "
                    f"{path.relative_to(ROOT)}"
                ),
                failures,
            )

    if failures:
        return False

    md_text = TRACEABILITY_MD.read_text(
        encoding="utf-8",
    )

    index_text = EVIDENCE_INDEX.read_text(
        encoding="utf-8",
    )

    # Exact frozen aim.
    for text, label in (
        (
            AIM,
            "Frozen Aim",
        ),
    ):
        if text in md_text:
            print(
                f"PASS: {label} in final research traceability"
            )
        else:
            fail(
                f"{label} missing from research traceability",
                failures,
            )

        if text in index_text:
            print(
                f"PASS: {label} synchronised into evidence index"
            )
        else:
            fail(
                f"{label} missing from evidence index",
                failures,
            )

    # O1-O5 exact text.
    for objective_id, objective in OBJECTIVES.items():
        if objective["text"] in md_text:
            print(
                f"PASS: {objective_id} exact objective text"
            )
        else:
            fail(
                (
                    f"{objective_id} exact objective "
                    "text missing"
                ),
                failures,
            )

    # RQ1-RQ5 exact text.
    for rq_id, rq in RESEARCH_QUESTIONS.items():
        if rq["question"] in md_text:
            print(
                f"PASS: {rq_id} exact frozen question"
            )
        else:
            fail(
                f"{rq_id} exact text missing from research traceability",
                failures,
            )

        if rq_id in index_text:
            print(
                f"PASS: {rq_id} represented in evidence index"
            )
        else:
            fail(
                f"{rq_id} missing from evidence index",
                failures,
            )

    # Ensure superseded placeholder is gone.
    targets = [
        TRACEABILITY_MD,
        EVIDENCE_INDEX,
        TRACEABILITY_CSV,
    ]

    for path in targets:
        text = path.read_text(
            encoding="utf-8",
        )

        if "SYNC_FROM_FROZEN_RESEARCH_SPEC" in text:
            fail(
                (
                    "Old research-spec placeholder remains in "
                    f"{path.relative_to(ROOT)}"
                ),
                failures,
            )

    # CSV count.
    with TRACEABILITY_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rq_rows = list(
            csv.DictReader(
                handle
            )
        )

    if len(rq_rows) == 5:
        print(
            "PASS: research_traceability.csv contains 5 RQ rows"
        )
    else:
        fail(
            (
                "research_traceability.csv expected "
                f"5 rows, found {len(rq_rows)}"
            ),
            failures,
        )

    with OBJECTIVES_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        objective_rows = list(
            csv.DictReader(
                handle
            )
        )

    if len(objective_rows) == 5:
        print(
            "PASS: research_objectives.csv contains 5 objective rows"
        )
    else:
        fail(
            (
                "research_objectives.csv expected "
                f"5 rows, found {len(objective_rows)}"
            ),
            failures,
        )

    # JSON semantic checks.
    payload = json.loads(
        TRACEABILITY_JSON.read_text(
            encoding="utf-8",
        )
    )

    if payload[
        "research_specification"
    ][
        "version"
    ] == RESEARCH_SPEC_VERSION:
        print(
            "PASS: frozen research specification version = 2.0.0"
        )
    else:
        fail(
            "Incorrect research specification version",
            failures,
        )

    if payload[
        "protocol"
    ][
        "version"
    ] == PROTOCOL_VERSION:
        print(
            "PASS: frozen protocol version = 2.0.1"
        )
    else:
        fail(
            "Incorrect protocol version",
            failures,
        )

    if payload[
        "post_test_governance"
    ][
        "version"
    ] == POST_TEST_GOVERNANCE_VERSION:
        print(
            "PASS: post-test governance version = 2.1.0"
        )
    else:
        fail(
            "Incorrect post-test governance version",
            failures,
        )

    if payload[
        "boundaries"
    ][
        "automatic_acceptance"
    ] is False:
        print(
            "PASS: automatic acceptance = false"
        )
    else:
        fail(
            "Automatic acceptance boundary violated",
            failures,
        )

    if payload[
        "boundaries"
    ][
        "human_review_required"
    ] is True:
        print(
            "PASS: human review required = true"
        )
    else:
        fail(
            "Human review boundary violated",
            failures,
        )

    # H1/H2 conclusions.
    if (
        HYPOTHESES[
            "H1"
        ][
            "result"
        ]
        == "NOT SUPPORTED"
    ):
        print(
            "PASS: H1 final outcome preserved"
        )

    if (
        HYPOTHESES[
            "H2"
        ][
            "result"
        ]
        == "SUPPORTED"
    ):
        print(
            "PASS: H2 final outcome preserved"
        )

    print()
    print(
        "=" * 76
    )

    if failures:
        print(
            "STEP 19: FAIL"
        )

        for failure in failures:
            print(
                f"- {failure}"
            )

        print(
            "=" * 76
        )

        return False

    print(
        "STEP 19: PASS"
    )

    print(
        "Frozen Aim: SYNCHRONISED"
    )

    print(
        "Objectives O1–O5: SYNCHRONISED"
    )

    print(
        "Research Questions RQ1–RQ5: SYNCHRONISED"
    )

    print(
        "Research → experiment → implementation → evidence → claim: COMPLETE"
    )

    print(
        "=" * 76
    )

    return True


# ============================================================
# GENERATION
# ============================================================

def generate() -> None:
    DOCS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not EVIDENCE_INDEX.is_file():
        raise RuntimeError(
            (
                "docs/final_evidence_index.md is missing. "
                "Run scripts/generate_evidence_index.py first."
            )
        )

    write_lf_text(
        TRACEABILITY_MD,
        build_traceability_markdown(),
    )

    write_traceability_csv()
    write_objectives_csv()
    write_traceability_json()

    replace_or_append_section(
        EVIDENCE_INDEX,
        build_index_section(),
    )

    update_evidence_pointer()

    print()
    print(
        "Generated Step 19 research traceability:"
    )

    print(
        "  docs/final_research_traceability.md"
    )

    print(
        "  evidence/research_traceability.csv"
    )

    print(
        "  evidence/research_objectives.csv"
    )

    print(
        "  evidence/research_traceability.json"
    )

    print(
        "  docs/final_evidence_index.md [SYNCHRONISED]"
    )

    print(
        "  EVIDENCE.md [UPDATED]"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help=(
            "Verify Step 19 outputs without regenerating them."
        ),
    )

    args = parser.parse_args()

    if not args.verify_only:
        generate()

    ok = verify()

    if not ok:
        raise SystemExit(
            1
        )


if __name__ == "__main__":
    main()