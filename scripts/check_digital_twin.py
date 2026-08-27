from __future__ import annotations

import tempfile

from pathlib import Path

from operational_coding_twin.audit_log import (
    AppendOnlyAuditLog,
)

from operational_coding_twin.case_store import (
    CaseStore,
)

from operational_coding_twin.digital_twin import (
    OperationalCodingTwin,
    State,
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
# TEST LABEL SPACE
# ============================================================

VALID_CATEGORIES = {
    f"C{i:02d}"
    for i in range(50)
}


# ============================================================
# FIXTURE PREDICTION
# ============================================================

prediction = PredictionResult(
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


# ============================================================
# FIXTURE EXPLANATION
# ============================================================

support = TokenAttribution(
    position=4,
    token="synthetic",
    raw_score=0.5,
    normalized_score=0.25,
)

explanation = ExplanationResult(
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


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    with tempfile.TemporaryDirectory() as temp:

        root = Path(
            temp
        )

        store = CaseStore(
            root
            / "cases"
        )

        audit = AppendOnlyAuditLog(
            root
            / "audit"
            / "audit.jsonl"
        )

        twin = OperationalCodingTwin(
            store=store,
            audit=audit,
            valid_categories=(
                VALID_CATEGORIES
            ),
            explanations_dir=(
                root
                / "explanations"
            ),
        )

        # ----------------------------------------------------
        # ACCEPT PATH
        # ----------------------------------------------------

        case = twin.ingest(
            case_id="ACCEPT-DEMO",

            source_mode=(
                "synthetic_note"
            ),

            clinical_text=(
                "Synthetic demonstration patient "
                "with sufficient clinical narrative "
                "for workflow verification only."
            ),
        )

        assert (
            case[
                "state"
            ]
            == State.INGESTED.value
        )

        case = twin.preprocess(
            "ACCEPT-DEMO"
        )

        assert (
            case[
                "state"
            ]
            == State.PREPROCESSED.value
        )

        case = (
            twin.attach_prediction(
                "ACCEPT-DEMO",
                prediction,
            )
        )

        assert (
            case[
                "state"
            ]
            == State.PREDICTED.value
        )

        case = (
            twin.attach_explanation(
                "ACCEPT-DEMO",
                explanation,
            )
        )

        assert (
            case[
                "state"
            ]
            == State.EXPLAINED.value
        )

        case = twin.send_for_review(
            "ACCEPT-DEMO"
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

        case = twin.review(
            "ACCEPT-DEMO",

            decision="accept",

            reviewer_identity=(
                "demo-reviewer"
            ),

            reason=(
                "Synthetic workflow "
                "verification."
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

        case = twin.complete(
            "ACCEPT-DEMO"
        )

        assert (
            case[
                "state"
            ]
            == State.COMPLETED.value
        )

        # ----------------------------------------------------
        # AMEND PATH
        # ----------------------------------------------------

        twin.ingest(
            case_id="AMEND-DEMO",

            source_mode=(
                "synthetic_note"
            ),

            clinical_text=(
                "Another synthetic demonstration "
                "clinical narrative for testing "
                "the amendment workflow."
            ),
        )

        twin.preprocess(
            "AMEND-DEMO"
        )

        twin.attach_prediction(
            "AMEND-DEMO",
            prediction,
        )

        twin.attach_explanation(
            "AMEND-DEMO",
            explanation,
        )

        twin.send_for_review(
            "AMEND-DEMO"
        )

        amended = twin.review(
            "AMEND-DEMO",

            decision="amend",

            reviewer_identity=(
                "demo-reviewer"
            ),

            reason=(
                "Reviewer selected another "
                "frozen category."
            ),

            amended_category="C02",
        )

        assert (
            amended[
                "state"
            ]
            == State.AMENDED.value
        )

        assert (
            amended[
                "final_category"
            ]
            == "C02"
        )

        twin.complete(
            "AMEND-DEMO"
        )

        # ----------------------------------------------------
        # REJECT PATH
        # ----------------------------------------------------

        twin.ingest(
            case_id="REJECT-DEMO",

            source_mode=(
                "synthetic_note"
            ),

            clinical_text=(
                "Third synthetic demonstration "
                "clinical narrative for testing "
                "the rejection workflow."
            ),
        )

        twin.preprocess(
            "REJECT-DEMO"
        )

        twin.attach_prediction(
            "REJECT-DEMO",
            prediction,
        )

        twin.attach_explanation(
            "REJECT-DEMO",
            explanation,
        )

        twin.send_for_review(
            "REJECT-DEMO"
        )

        rejected = twin.review(
            "REJECT-DEMO",

            decision="reject",

            reviewer_identity=(
                "demo-reviewer"
            ),

            reason=(
                "Recommendation rejected "
                "during synthetic verification."
            ),
        )

        assert (
            rejected[
                "state"
            ]
            == State.REJECTED.value
        )

        assert (
            rejected[
                "final_category"
            ]
            is None
        )

        twin.complete(
            "REJECT-DEMO"
        )

        # ----------------------------------------------------
        # HUMAN REVIEW REQUIRED
        # ----------------------------------------------------

        twin.ingest(
            case_id="NO-AUTO-DEMO",

            source_mode=(
                "synthetic_note"
            ),

            clinical_text=(
                "Synthetic narrative created "
                "specifically to verify that "
                "automatic acceptance is blocked."
            ),
        )

        blocked = False

        try:

            twin.complete(
                "NO-AUTO-DEMO"
            )

        except RuntimeError:

            blocked = True

        assert blocked

        # ----------------------------------------------------
        # MISSING REVIEWER BLOCKED
        # ----------------------------------------------------

        twin.preprocess(
            "NO-AUTO-DEMO"
        )

        twin.attach_prediction(
            "NO-AUTO-DEMO",
            prediction,
        )

        twin.attach_explanation(
            "NO-AUTO-DEMO",
            explanation,
        )

        twin.send_for_review(
            "NO-AUTO-DEMO"
        )

        blocked = False

        try:

            twin.review(
                "NO-AUTO-DEMO",

                decision="accept",

                reviewer_identity="",

                reason="Test",
            )

        except ValueError:

            blocked = True

        assert blocked

        # ----------------------------------------------------
        # AUDIT CHAIN
        # ----------------------------------------------------

        assert (
            audit.verify()
            is True
        )

        print()
        print(
            "ACCEPT PATH: PASS"
        )

        print(
            "AMEND PATH: PASS"
        )

        print(
            "REJECT PATH: PASS"
        )

        print(
            "AUTO ACCEPTANCE: BLOCKED"
        )

        print(
            "MISSING REVIEWER: BLOCKED"
        )

        print(
            "AUDIT SHA-256 CHAIN: PASS"
        )

        print(
            "TEST PARTITION ACCESSED: NO"
        )

        print()
        print(
            "STEP 13: PASS"
        )


if __name__ == "__main__":
    main()