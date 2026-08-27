from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

RESEARCH_JSON = (
    EVIDENCE
    / "research_traceability.json"
)

VISUAL_REGISTER = (
    EVIDENCE
    / "visual_evidence_register.csv"
)

OUTPUT_MD = (
    DOCS
    / "final_dissertation_evidence_map.md"
)

OUTPUT_CSV = (
    EVIDENCE
    / "dissertation_evidence_map.csv"
)

EVIDENCE_POINTER = ROOT / "EVIDENCE.md"


BEGIN_MARKER = (
    "<!-- BEGIN: DISSERTATION_EVIDENCE_MAP -->"
)

END_MARKER = (
    "<!-- END: DISSERTATION_EVIDENCE_MAP -->"
)


# ============================================================
# CHAPTER CONTRACT
# ============================================================

CHAPTERS = {
    "1": {
        "title": "Introduction",
        "purpose": (
            "Define the research problem, aim, objectives, "
            "research questions, contribution and dissertation scope."
        ),
    },

    "2": {
        "title": "Critical Literature Review",
        "purpose": (
            "Critically position automated ICD coding, transformers, "
            "calibration, explainability, synthetic data and "
            "operational digital twins."
        ),
    },

    "3": {
        "title": "Methodology",
        "purpose": (
            "Describe the frozen benchmark, leakage controls, "
            "comparative modelling, calibration, XAI, confirmatory "
            "evaluation and reproducibility protocol."
        ),
    },

    "4": {
        "title": "System Design and Implementation",
        "purpose": (
            "Describe implementation of frozen inference, "
            "calibration, XAI, state transitions, human review, "
            "persistence and tamper-evident auditability."
        ),
    },

    "5": {
        "title": "Evaluation and Results",
        "purpose": (
            "Report predictive, calibration, XAI, error-analysis "
            "and engineering-verification evidence."
        ),
    },

    "6": {
        "title": "Discussion",
        "purpose": (
            "Answer RQ1-RQ5 critically and interpret negative, "
            "positive and bounded findings."
        ),
    },

    "7": {
        "title": "Conclusion and Future Work",
        "purpose": (
            "Summarise what was established, what was not "
            "established and what future NHS validation requires."
        ),
    },
}


# ============================================================
# FINAL RQ → DISSERTATION MAP
# ============================================================

RQ_MAP = {
    "RQ1": {
        "chapter_methods": "3",
        "chapter_results": "5",
        "chapter_discussion": "6",

        "method_section": (
            "Benchmark construction, provenance, family-controlled "
            "splitting and leakage/shortcut controls"
        ),

        "results_section": (
            "Benchmark validity, shortcut audit and failure analysis"
        ),

        "discussion_section": (
            "Synthetic benchmark validity and external-validity limits"
        ),

        "scientific_evidence": [
            "BNS-CCB-2.0.0 release/audit evidence",
            "Phase 5 shortcut/leakage analysis",
            "Phase 10 post-test error/claims freeze",
        ],

        "implementation_evidence": [
            "evidence/01_verification/frozen_scientific_contract.txt",
            "artifacts/provenance/source_artifact_hashes.json",
            "docs/final_implementation_record.md",
        ],

        "main_claim": (
            "BNS-CCB provides a reproducible controlled synthetic "
            "benchmark, but substantial lexical/template shortcut "
            "risk limits external validity."
        ),

        "boundary": (
            "Do not claim real NHS generalisation from BNS-CCB."
        ),
    },

    "RQ2": {
        "chapter_methods": "3",
        "chapter_results": "5",
        "chapter_discussion": "6",

        "method_section": (
            "TF-IDF logistic-regression baseline and frozen "
            "BioClinicalBERT comparative protocol"
        ),

        "results_section": (
            "Predictive comparison and three-seed transformer robustness"
        ),

        "discussion_section": (
            "Interpretation of the unsupported transformer-superiority "
            "hypothesis"
        ),

        "scientific_evidence": [
            "Phase 6 lexical baseline",
            "Phase 7 canonical BioClinicalBERT",
            "Phase 7B seeds 42/43/44",
            "Phase 9 one-shot test",
            "Phase 10 error analysis",
        ],

        "implementation_evidence": [
            "artifacts/model/model.safetensors",
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],

        "main_claim": (
            "BioClinicalBERT did not outperform the controlled "
            "TF-IDF/logistic-regression baseline on the locked "
            "test partition."
        ),

        "boundary": (
            "The operational prototype must not be used to imply "
            "transformer superiority."
        ),
    },

    "RQ3": {
        "chapter_methods": "3",
        "chapter_results": "5",
        "chapter_discussion": "6",

        "method_section": (
            "Validation-only scalar temperature calibration"
        ),

        "results_section": (
            "Raw versus calibrated NLL, Brier score and ECE"
        ),

        "discussion_section": (
            "Probability reliability and limits of confidence"
        ),

        "scientific_evidence": [
            "Phase 8B validation-fitted temperature scaling",
            "Phase 9 locked-test calibration evaluation",
        ],

        "implementation_evidence": [
            "artifacts/calibration/temperature_scaling.json",
            "evidence/02_replay/E03_replay_prediction.png",
            "evidence/03_fresh_inference/E07_fresh_prediction.png",
        ],

        "main_claim": (
            "Validation-fitted scalar temperature scaling "
            "substantially improved probability reliability."
        ),

        "boundary": (
            "Calibrated confidence is not a probability of clinical "
            "safety, coding correctness or billing correctness."
        ),
    },

    "RQ4": {
        "chapter_methods": "3",
        "chapter_results": "5",
        "chapter_discussion": "6",

        "method_section": (
            "Predicted-class Layer Integrated Gradients and "
            "quantitative faithfulness evaluation"
        ),

        "results_section": (
            "Token-attribution and targeted-versus-random masking evidence"
        ),

        "discussion_section": (
            "Explanation usefulness, faithfulness and interpretability limits"
        ),

        "scientific_evidence": [
            "Phase 8A XAI protocol freeze",
            "Phase 8B deterministic validation XAI",
            "Phase 8B quantitative faithfulness evaluation",
        ],

        "implementation_evidence": [
            "artifacts/replay/layer_integrated_gradients_cases.csv",
            "evidence/02_replay/E04_replay_xai.png",
            "evidence/03_fresh_inference/E08_fresh_lig.png",
        ],

        "main_claim": (
            "The prototype provides pre-specified token-level "
            "model-relevance evidence with quantitative "
            "faithfulness evaluation."
        ),

        "boundary": (
            "Token attribution is model-behaviour evidence, "
            "not causal clinical evidence."
        ),
    },

    "RQ5": {
        "chapter_methods": "3",
        "chapter_results": "5",
        "chapter_discussion": "6",

        "method_section": (
            "Operational digital-twin state, human-review and "
            "auditability design"
        ),

        "results_section": (
            "Engineering verification and deterministic end-to-end "
            "workflow demonstration"
        ),

        "discussion_section": (
            "Operational feasibility, governance and deployment limitations"
        ),

        "scientific_evidence": [
            "Phase 11B operational digital-twin implementation",
            "Final automated software verification",
            "Final deterministic demonstration",
        ],

        "implementation_evidence": [
            "evidence/04_human_review/E05_awaiting_human_review.png",
            "evidence/04_human_review/E06_accepted_completed.png",
            "evidence/04_human_review/E09_amended_completed.png",
            "evidence/05_audit/E10_audit_history.png",
            "evidence/05_audit/E11_audit_integrity_pass.png",
            "evidence/01_verification/pytest_full_results.txt",
        ],

        "main_claim": (
            "Ranked predictions, calibrated confidence, XAI, "
            "mandatory human decisions, persistent state and "
            "tamper-evident audit history can be integrated in an "
            "event-driven operational research prototype."
        ),

        "boundary": (
            "This establishes engineering feasibility, not NHS "
            "deployment readiness or clinical safety."
        ),
    },
}


# ============================================================
# VISUAL-EVIDENCE DISSERTATION USE
# ============================================================

VISUAL_USE = {
    "E01": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Research-scope and governance boundary of the "
            "operational coding-twin prototype."
        ),
    },

    "E02": {
        "location": "Appendix",
        "role": "Supporting figure",
        "caption": (
            "Selection of a deterministic frozen Phase 8B "
            "validation replay case."
        ),
    },

    "E03": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Frozen validation replay showing Top-1/Top-3 "
            "recommendations and calibrated descriptive confidence."
        ),
    },

    "E04": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Frozen Layer Integrated Gradients evidence integrated "
            "into the operational workflow."
        ),
    },

    "E05": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Mandatory Awaiting Human Review state separating "
            "AI recommendation from final coding disposition."
        ),
    },

    "E06": {
        "location": "Appendix",
        "role": "Supporting figure",
        "caption": (
            "Human acceptance followed by explicit case completion."
        ),
    },

    "E07": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Fresh synthetic-note inference using the frozen "
            "canonical BioClinicalBERT model."
        ),
    },

    "E08": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Fresh 50-step predicted-class Layer Integrated "
            "Gradients explanation."
        ),
    },

    "E09": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Human amendment demonstrating reviewer authority "
            "over the AI-generated coding recommendation."
        ),
    },

    "E10": {
        "location": "Chapter 4",
        "role": "Main figure",
        "caption": (
            "Ordered operational audit history for a coding case."
        ),
    },

    "E11": {
        "location": "Appendix",
        "role": "Supporting verification",
        "caption": (
            "Successful verification of the SHA-256 chained "
            "tamper-evident audit history."
        ),
    },

    "E12": {
        "location": "Appendix",
        "role": "Reproducibility evidence",
        "caption": (
            "Successful SHA-256 verification of the frozen "
            "evidence-package manifest."
        ),
    },
}


# ============================================================
# RECOMMENDED RESULT TABLES
# ============================================================

RESULT_TABLES = [
    {
        "id": "T5-1",
        "chapter": "Chapter 5",
        "title": (
            "Final predictive comparison on the locked test partition"
        ),
        "evidence": (
            "Phase 9 one-shot confirmatory results"
        ),
        "content": (
            "Baseline and BioClinicalBERT accuracy, macro-F1, "
            "difference and confidence interval"
        ),
    },

    {
        "id": "T5-2",
        "chapter": "Chapter 5",
        "title": (
            "BioClinicalBERT three-seed validation robustness"
        ),
        "evidence": (
            "Phase 7B seeds 42/43/44"
        ),
        "content": (
            "Mean ± sample SD for frozen validation metrics"
        ),
    },

    {
        "id": "T5-3",
        "chapter": "Chapter 5",
        "title": (
            "Raw versus calibrated probability-reliability metrics"
        ),
        "evidence": (
            "Phase 8B and Phase 9"
        ),
        "content": (
            "NLL, multiclass Brier score and ECE before/after "
            "temperature scaling"
        ),
    },

    {
        "id": "T5-4",
        "chapter": "Chapter 5",
        "title": (
            "Transformer error analysis and common confusion patterns"
        ),
        "evidence": (
            "Phase 10"
        ),
        "content": (
            "Error count, confusion pairs, support and lowest-performing "
            "categories"
        ),
    },

    {
        "id": "T5-5",
        "chapter": "Chapter 5",
        "title": (
            "Explainability faithfulness evaluation"
        ),
        "evidence": (
            "Phase 8B"
        ),
        "content": (
            "Targeted attribution masking versus deterministic "
            "random masking"
        ),
    },

    {
        "id": "T5-6",
        "chapter": "Chapter 5",
        "title": (
            "Operational implementation verification"
        ),
        "evidence": (
            "Final pytest and project-verifier evidence"
        ),
        "content": (
            "Verified inference, XAI, state, review, persistence, "
            "audit and governance requirements"
        ),
    },
]


# ============================================================
# HELPERS
# ============================================================

def write_lf(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        (
            text.replace("\r\n", "\n")
            .replace("\r", "\n")
        ).encode("utf-8")
    )


def load_research() -> dict:
    if not RESEARCH_JSON.is_file():
        raise RuntimeError(
            "Missing evidence/research_traceability.json. "
            "Complete Step 19 first."
        )

    return json.loads(
        RESEARCH_JSON.read_text(
            encoding="utf-8"
        )
    )


def load_visual_register() -> list[dict]:
    if not VISUAL_REGISTER.is_file():
        raise RuntimeError(
            "Missing evidence/visual_evidence_register.csv."
        )

    with VISUAL_REGISTER.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


# ============================================================
# MARKDOWN
# ============================================================

def build_markdown(
    research: dict,
    visual_rows: list[dict],
) -> str:
    aim = research["aim"]

    lines = [
        "# Final Dissertation Evidence Map",
        "",
        "**Document version:** 1.0.0  ",
        "**Purpose:** Map frozen research evidence and operational "
        "implementation evidence into the final dissertation.  ",
        "**Status:** FINAL WRITING TRACEABILITY",
        "",
        "---",
        "",
        "# 1. Frozen Aim",
        "",
        f"> {aim}",
        "",
        "---",
        "",
        "# 2. Chapter Contract",
        "",
        "| Chapter | Title | Evidence function |",
        "|---|---|---|",
    ]

    for chapter_id, chapter in CHAPTERS.items():
        lines.append(
            f"| {chapter_id} "
            f"| {chapter['title']} "
            f"| {chapter['purpose']} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# 3. RQ → Experiment → Evidence → Claim Map",
            "",
            "| RQ | Methodology | Results | Discussion | "
            "Primary conclusion |",
            "|---|---|---|---|---|",
        ]
    )

    for rq_id, item in RQ_MAP.items():
        lines.append(
            f"| {rq_id} "
            f"| Ch. {item['chapter_methods']}: "
            f"{item['method_section']} "
            f"| Ch. {item['chapter_results']}: "
            f"{item['results_section']} "
            f"| Ch. {item['chapter_discussion']}: "
            f"{item['discussion_section']} "
            f"| {item['main_claim']} |"
        )

    for rq_id, item in RQ_MAP.items():
        rq = research[
            "research_questions"
        ][rq_id]

        lines.extend(
            [
                "",
                "---",
                "",
                f"# {rq_id} — {rq['title']}",
                "",
                "## Frozen question",
                "",
                rq["question"],
                "",
                "## Scientific evidence",
                "",
            ]
        )

        for value in item["scientific_evidence"]:
            lines.append(f"- {value}")

        lines.extend(
            [
                "",
                "## Implementation / repository evidence",
                "",
            ]
        )

        for value in item["implementation_evidence"]:
            lines.append(f"- `{value}`")

        lines.extend(
            [
                "",
                "## Dissertation placement",
                "",
                (
                    f"- Chapter {item['chapter_methods']}: "
                    f"{item['method_section']}"
                ),
                (
                    f"- Chapter {item['chapter_results']}: "
                    f"{item['results_section']}"
                ),
                (
                    f"- Chapter {item['chapter_discussion']}: "
                    f"{item['discussion_section']}"
                ),
                "",
                "## Final bounded claim",
                "",
                item["main_claim"],
                "",
                "## Boundary",
                "",
                item["boundary"],
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Visual Evidence Placement",
            "",
            "| ID | Repository file | Dissertation use | Role | "
            "Recommended caption | Status |",
            "|---|---|---|---|---|---|",
        ]
    )

    visual_by_id = {
        row["evidence_id"]: row
        for row in visual_rows
    }

    for evidence_id in sorted(VISUAL_USE):
        use = VISUAL_USE[evidence_id]
        row = visual_by_id[evidence_id]

        lines.append(
            f"| {evidence_id} "
            f"| `{row['file']}` "
            f"| {use['location']} "
            f"| {use['role']} "
            f"| {use['caption']} "
            f"| {row['status']} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Recommended Results Tables",
            "",
            "| ID | Location | Proposed title | Scientific evidence | "
            "Required content |",
            "|---|---|---|---|---|",
        ]
    )

    for table in RESULT_TABLES:
        lines.append(
            f"| {table['id']} "
            f"| {table['chapter']} "
            f"| {table['title']} "
            f"| {table['evidence']} "
            f"| {table['content']} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "# Main-text versus Appendix Rule",
            "",
            "Main-text figures should be retained only when they directly "
            "support the research argument.",
            "",
            "Recommended main-text operational figures:",
            "",
            "- E01 — system/research boundary;",
            "- E03 — ranked calibrated prediction;",
            "- E04 — frozen XAI integration;",
            "- E05 — mandatory human-review gate;",
            "- E07 — fresh frozen-model inference;",
            "- E08 — fresh LIG;",
            "- E09 — human amendment;",
            "- E10 — audit history.",
            "",
            "Recommended appendix figures:",
            "",
            "- E02 — replay-case selection;",
            "- E06 — accepted-case completion;",
            "- E11 — audit-integrity verification;",
            "- E12 — evidence-manifest verification.",
            "",
            "---",
            "",
            "# Evidence Interpretation Rules",
            "",
            "1. Predictive accuracy/F1 claims must come from frozen "
            "experimental metrics, not screenshots.",
            "",
            "2. Workflow-functionality claims should be supported by "
            "source code, automated tests and operational evidence.",
            "",
            "3. Calibration should be described as probability-reliability "
            "improvement, not clinical correctness.",
            "",
            "4. XAI should be described as model-behaviour evidence, "
            "not causal clinical evidence.",
            "",
            "5. The unsupported transformer-superiority result must be "
            "reported explicitly.",
            "",
            "6. Synthetic benchmark limitations must remain visible in "
            "Results, Discussion and Conclusion.",
            "",
            "7. Human review remains mandatory throughout the operational "
            "interpretation.",
            "",
            "---",
            "",
            "# Final Dissertation Claim Chain",
            "",
            "```text",
            "Frozen Aim",
            "   ↓",
            "O1–O5",
            "   ↓",
            "RQ1–RQ5",
            "   ↓",
            "Method / Experiment",
            "   ↓",
            "Scientific Result",
            "   ↓",
            "Operational Evidence where applicable",
            "   ↓",
            "Bounded Discussion Claim",
            "   ↓",
            "Conclusion",
            "```",
            "",
            "---",
            "",
            "**Dissertation evidence-map status: COMPLETE**",
            "",
        ]
    )

    return "\n".join(lines)


# ============================================================
# CSV
# ============================================================

def write_csv(
    research: dict,
) -> None:
    fields = [
        "rq_id",
        "rq_title",
        "research_question",
        "methodology_chapter",
        "methodology_section",
        "results_chapter",
        "results_section",
        "discussion_chapter",
        "discussion_section",
        "scientific_evidence",
        "implementation_evidence",
        "main_claim",
        "claim_boundary",
    ]

    with OUTPUT_CSV.open(
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

        for rq_id, item in RQ_MAP.items():
            rq = research[
                "research_questions"
            ][rq_id]

            writer.writerow(
                {
                    "rq_id": rq_id,
                    "rq_title": rq["title"],
                    "research_question": rq["question"],

                    "methodology_chapter":
                        item["chapter_methods"],

                    "methodology_section":
                        item["method_section"],

                    "results_chapter":
                        item["chapter_results"],

                    "results_section":
                        item["results_section"],

                    "discussion_chapter":
                        item["chapter_discussion"],

                    "discussion_section":
                        item["discussion_section"],

                    "scientific_evidence":
                        "; ".join(
                            item["scientific_evidence"]
                        ),

                    "implementation_evidence":
                        "; ".join(
                            item[
                                "implementation_evidence"
                            ]
                        ),

                    "main_claim":
                        item["main_claim"],

                    "claim_boundary":
                        item["boundary"],
                }
            )


# ============================================================
# EVIDENCE POINTER
# ============================================================

def update_pointer() -> None:
    if not EVIDENCE_POINTER.is_file():
        return

    section = "\n".join(
        [
            BEGIN_MARKER,
            "",
            "## Dissertation Evidence Map",
            "",
            "Final research-question-to-dissertation mapping:",
            "",
            "- [`docs/final_dissertation_evidence_map.md`]"
            "(docs/final_dissertation_evidence_map.md)",
            "- [`evidence/dissertation_evidence_map.csv`]"
            "(evidence/dissertation_evidence_map.csv)",
            "",
            END_MARKER,
        ]
    )

    text = EVIDENCE_POINTER.read_text(
        encoding="utf-8"
    )

    if (
        BEGIN_MARKER in text
        and END_MARKER in text
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
            + "\n\n"
            + section
            + "\n"
        )

    write_lf(
        EVIDENCE_POINTER,
        text,
    )


# ============================================================
# VERIFICATION
# ============================================================

def verify(
    research: dict,
    visual_rows: list[dict],
) -> bool:
    failures = []

    print()
    print("=" * 72)
    print(
        "STEP 20 — DISSERTATION EVIDENCE MAP VERIFICATION"
    )
    print("=" * 72)

    for path in (
        OUTPUT_MD,
        OUTPUT_CSV,
    ):
        if path.is_file():
            print(
                f"PASS: {path.relative_to(ROOT)}"
            )
        else:
            failures.append(
                f"Missing {path.relative_to(ROOT)}"
            )

    text = (
        OUTPUT_MD.read_text(
            encoding="utf-8"
        )
        if OUTPUT_MD.is_file()
        else ""
    )

    for rq_id in (
        "RQ1",
        "RQ2",
        "RQ3",
        "RQ4",
        "RQ5",
    ):
        if rq_id in text:
            print(
                f"PASS: {rq_id} mapped"
            )
        else:
            failures.append(
                f"{rq_id} not mapped"
            )

    visual_ids = {
        row["evidence_id"]
        for row in visual_rows
    }

    expected_visual_ids = {
        f"E{i:02d}"
        for i in range(1, 13)
    }

    if visual_ids == expected_visual_ids:
        print(
            "PASS: E01–E12 visual register complete"
        )
    else:
        failures.append(
            "Visual evidence register does not contain exactly E01–E12"
        )

    for evidence_id in expected_visual_ids:
        if evidence_id not in VISUAL_USE:
            failures.append(
                f"{evidence_id} has no dissertation placement"
            )

    for table in RESULT_TABLES:
        if table["id"] in text:
            print(
                f"PASS: {table['id']} results table mapped"
            )
        else:
            failures.append(
                f"{table['id']} missing"
            )

    prohibited = [
        "SYNC_FROM_FROZEN_RESEARCH_SPEC",
        "INSERT_RQ",
        "TODO_RQ",
    ]

    for token in prohibited:
        if token in text:
            failures.append(
                f"Unresolved placeholder: {token}"
            )

    # Preserve key final scientific conclusions.
    required_claim_fragments = [
        "did not outperform",
        "improved probability reliability",
        "not causal clinical evidence",
        "engineering feasibility",
    ]

    lowered = text.lower()

    for fragment in required_claim_fragments:
        if fragment.lower() not in lowered:
            failures.append(
                f"Missing bounded claim fragment: {fragment}"
            )

    print()
    print("=" * 72)

    if failures:
        print("STEP 20: FAIL")

        for failure in failures:
            print(f"- {failure}")

        print("=" * 72)

        return False

    print("STEP 20: PASS")
    print("RQ1–RQ5 dissertation mapping: COMPLETE")
    print("E01–E12 placement: COMPLETE")
    print("Results-table register: COMPLETE")
    print("Claim boundaries: COMPLETE")
    print("=" * 72)

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    research = load_research()
    visual_rows = load_visual_register()

    write_lf(
        OUTPUT_MD,
        build_markdown(
            research,
            visual_rows,
        ),
    )

    write_csv(
        research
    )

    update_pointer()

    ok = verify(
        research,
        visual_rows,
    )

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()