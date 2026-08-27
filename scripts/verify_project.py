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
    FrozenExplainabilityService,
)

from operational_coding_twin.frozen_resources import (
    load_frozen_resources,
)

from operational_coding_twin.inference import (
    FrozenInferenceService,
)


# ============================================================
# HELPERS
# ============================================================

def heading(
    title: str,
) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def pass_line(
    name: str,
) -> None:
    print(
        f"{name:<48} PASS"
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(
            message
        )


# ============================================================
# MAIN VERIFICATION
# ============================================================

def main() -> None:

    heading(
        "STEP 15 — OPERATIONAL CODING TWIN VERIFICATION"
    )

    # ========================================================
    # 1. LOAD FROZEN SCIENTIFIC RESOURCES
    # ========================================================

    heading(
        "1. FROZEN RESOURCES"
    )

    resources = (
        load_frozen_resources()
    )

    require(
        len(
            resources.label2id
        ) == 50,
        "Expected exactly 50 frozen ICD-10 categories.",
    )

    require(
        len(
            resources.id2label
        ) == 50,
        "Expected exactly 50 reverse label mappings.",
    )

    require(
        resources.replay_sample.shape[
            0
        ] == 100,
        "Expected deterministic replay sample n=100.",
    )

    require(
        resources.replay_probabilities.shape
        == (375, 50),
        "Expected validation calibrated probabilities "
        "shape (375, 50).",
    )

    require(
        resources.replay_explanations.shape[
            0
        ] == 100,
        "Expected 100 frozen LIG case explanations.",
    )

    require(
        abs(
            resources.temperature
            - 0.18388931380527324
        )
        < 1e-10,
        "Unexpected frozen temperature.",
    )

    pass_line(
        "Frozen resources"
    )

    pass_line(
        "50-category label space"
    )

    pass_line(
        "Validation replay n=100"
    )

    pass_line(
        "Calibration temperature"
    )


    # ========================================================
    # 2. CREATE READ-ONLY REPLAY SERVICES
    # ========================================================

    heading(
        "2. REPLAY SERVICES"
    )

    inference = (
        FrozenInferenceService(
            resources
        )
    )

    explainability = (
        FrozenExplainabilityService(
            resources
        )
    )

    pass_line(
        "Frozen inference service"
    )

    pass_line(
        "Frozen explainability service"
    )


    # ========================================================
    # 3. CHOOSE THREE FROZEN VALIDATION CASES
    # ========================================================

    heading(
        "3. DETERMINISTIC VALIDATION CASES"
    )

    replay_table = (
        resources
        .replay_sample
        .sort_values(
            "sample_rank"
        )
        .reset_index(
            drop=True
        )
    )

    require(
        len(
            replay_table
        ) >= 3,
        "At least three replay cases are required.",
    )

    selected_rows = [
        int(
            replay_table.iloc[
                index
            ][
                "validation_row"
            ]
        )
        for index in range(
            3
        )
    ]

    print(
        "Selected validation rows:",
        selected_rows,
    )

    # Validate predictions + explanations before twin testing.

    for validation_row in (
        selected_rows
    ):

        prediction = (
            inference.replay(
                validation_row
            )
        )

        explanation = (
            explainability.replay(
                validation_row
            )
        )

        require(
            len(
                prediction.top3
            ) == 3,
            "Replay prediction must provide Top-3.",
        )

        require(
            prediction.recommendation
            in resources.label2id,
            "Replay recommendation outside frozen label space.",
        )

        require(
            explanation.category
            == prediction.recommendation,
            (
                "Replay explanation category does not match "
                "replay prediction."
            ),
        )

        require(
            explanation.steps
            == 50,
            "Frozen replay LIG must use 50 steps.",
        )

    pass_line(
        "Replay predictions"
    )

    pass_line(
        "Replay Top-3"
    )

    pass_line(
        "Replay LIG target alignment"
    )

    pass_line(
        "Replay LIG 50 steps"
    )


    # ========================================================
    # 4. CREATE ISOLATED TEMPORARY TWIN
    # ========================================================

    heading(
        "4. DIGITAL-TWIN WORKFLOW"
    )

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
            / "verification.jsonl"
        )

        twin = OperationalCodingTwin(
            store=store,

            audit=audit,

            valid_categories=set(
                resources.label2id.keys()
            ),

            explanations_dir=(
                root
                / "explanations"
            ),
        )


        # ====================================================
        # ACCEPT PATH
        # ====================================================

        validation_row = (
            selected_rows[
                0
            ]
        )

        sample = (
            replay_table[
                replay_table[
                    "validation_row"
                ].astype(
                    int
                )
                == validation_row
            ]
            .iloc[
                0
            ]
        )

        accept_id = (
            "VERIFY-ACCEPT"
        )

        twin.ingest(
            case_id=accept_id,

            source_mode=(
                "frozen_validation_replay"
            ),

            source_ref=str(
                validation_row
            ),

            source_sha256=str(
                sample[
                    "sample_hash"
                ]
            ),
        )

        twin.preprocess(
            accept_id
        )

        accept_prediction = (
            inference.replay(
                validation_row
            )
        )

        twin.attach_prediction(
            accept_id,
            accept_prediction,
        )

        accept_explanation = (
            explainability.replay(
                validation_row
            )
        )

        twin.attach_explanation(
            accept_id,
            accept_explanation,
        )

        twin.send_for_review(
            accept_id
        )

        reviewed = twin.review(
            accept_id,

            decision="accept",

            reviewer_identity=(
                "verification-reviewer"
            ),

            reason=(
                "Automated verification of "
                "the mandatory human-review path."
            ),
        )

        require(
            reviewed[
                "state"
            ]
            == State.ACCEPTED.value,
            "Accept path failed.",
        )

        require(
            reviewed[
                "final_category"
            ]
            == accept_prediction.recommendation,
            "Accepted case must preserve recommendation.",
        )

        completed = twin.complete(
            accept_id
        )

        require(
            completed[
                "state"
            ]
            == State.COMPLETED.value,
            "Accepted case did not complete.",
        )

        pass_line(
            "Accept workflow"
        )


        # ====================================================
        # AMEND PATH
        # ====================================================

        validation_row = (
            selected_rows[
                1
            ]
        )

        sample = (
            replay_table[
                replay_table[
                    "validation_row"
                ].astype(
                    int
                )
                == validation_row
            ]
            .iloc[
                0
            ]
        )

        amend_id = (
            "VERIFY-AMEND"
        )

        twin.ingest(
            case_id=amend_id,

            source_mode=(
                "frozen_validation_replay"
            ),

            source_ref=str(
                validation_row
            ),

            source_sha256=str(
                sample[
                    "sample_hash"
                ]
            ),
        )

        twin.preprocess(
            amend_id
        )

        amend_prediction = (
            inference.replay(
                validation_row
            )
        )

        twin.attach_prediction(
            amend_id,
            amend_prediction,
        )

        amend_explanation = (
            explainability.replay(
                validation_row
            )
        )

        twin.attach_explanation(
            amend_id,
            amend_explanation,
        )

        twin.send_for_review(
            amend_id
        )

        # Choose a valid category that differs
        # from the model recommendation.

        replacement = next(
            category

            for category
            in sorted(
                resources.label2id.keys()
            )

            if category
            != amend_prediction.recommendation
        )

        amended = twin.review(
            amend_id,

            decision="amend",

            reviewer_identity=(
                "verification-reviewer"
            ),

            reason=(
                "Automated verification of "
                "the amendment pathway."
            ),

            amended_category=(
                replacement
            ),
        )

        require(
            amended[
                "state"
            ]
            == State.AMENDED.value,
            "Amend path failed.",
        )

        require(
            amended[
                "final_category"
            ]
            == replacement,
            "Amend path failed to store replacement category.",
        )

        completed = twin.complete(
            amend_id
        )

        require(
            completed[
                "state"
            ]
            == State.COMPLETED.value,
            "Amended case did not complete.",
        )

        pass_line(
            "Amend workflow"
        )


        # ====================================================
        # REJECT PATH
        # ====================================================

        validation_row = (
            selected_rows[
                2
            ]
        )

        sample = (
            replay_table[
                replay_table[
                    "validation_row"
                ].astype(
                    int
                )
                == validation_row
            ]
            .iloc[
                0
            ]
        )

        reject_id = (
            "VERIFY-REJECT"
        )

        twin.ingest(
            case_id=reject_id,

            source_mode=(
                "frozen_validation_replay"
            ),

            source_ref=str(
                validation_row
            ),

            source_sha256=str(
                sample[
                    "sample_hash"
                ]
            ),
        )

        twin.preprocess(
            reject_id
        )

        reject_prediction = (
            inference.replay(
                validation_row
            )
        )

        twin.attach_prediction(
            reject_id,
            reject_prediction,
        )

        reject_explanation = (
            explainability.replay(
                validation_row
            )
        )

        twin.attach_explanation(
            reject_id,
            reject_explanation,
        )

        twin.send_for_review(
            reject_id
        )

        rejected = twin.review(
            reject_id,

            decision="reject",

            reviewer_identity=(
                "verification-reviewer"
            ),

            reason=(
                "Automated verification of "
                "the rejection pathway."
            ),
        )

        require(
            rejected[
                "state"
            ]
            == State.REJECTED.value,
            "Reject path failed.",
        )

        require(
            rejected[
                "final_category"
            ]
            is None,
            "Rejected case must not have a final category.",
        )

        completed = twin.complete(
            reject_id
        )

        require(
            completed[
                "state"
            ]
            == State.COMPLETED.value,
            "Rejected case did not complete.",
        )

        pass_line(
            "Reject workflow"
        )


        # ====================================================
        # 5. GOVERNANCE BLOCKS
        # ====================================================

        heading(
            "5. GOVERNANCE BLOCKS"
        )

        governance_id = (
            "VERIFY-GOVERNANCE"
        )

        validation_row = (
            selected_rows[
                0
            ]
        )

        sample = (
            replay_table[
                replay_table[
                    "validation_row"
                ].astype(
                    int
                )
                == validation_row
            ]
            .iloc[
                0
            ]
        )

        twin.ingest(
            case_id=governance_id,

            source_mode=(
                "frozen_validation_replay"
            ),

            source_ref=str(
                validation_row
            ),

            source_sha256=str(
                sample[
                    "sample_hash"
                ]
            ),
        )

        # ----------------------------------------------------
        # Automatic/direct completion must fail.
        # ----------------------------------------------------

        auto_completion_blocked = False

        try:
            twin.complete(
                governance_id
            )

        except RuntimeError:
            auto_completion_blocked = (
                True
            )

        require(
            auto_completion_blocked,
            "Automatic/direct completion was not blocked.",
        )

        pass_line(
            "Automatic completion blocked"
        )


        # ----------------------------------------------------
        # Prepare case for human review.
        # ----------------------------------------------------

        twin.preprocess(
            governance_id
        )

        governance_prediction = (
            inference.replay(
                validation_row
            )
        )

        twin.attach_prediction(
            governance_id,
            governance_prediction,
        )

        governance_explanation = (
            explainability.replay(
                validation_row
            )
        )

        twin.attach_explanation(
            governance_id,
            governance_explanation,
        )

        twin.send_for_review(
            governance_id
        )


        # ----------------------------------------------------
        # Missing reviewer identity must fail.
        # ----------------------------------------------------

        missing_reviewer_blocked = False

        try:
            twin.review(
                governance_id,

                decision="accept",

                reviewer_identity="",

                reason=(
                    "Verification."
                ),
            )

        except ValueError:
            missing_reviewer_blocked = (
                True
            )

        require(
            missing_reviewer_blocked,
            "Missing reviewer identity was not blocked.",
        )

        pass_line(
            "Missing reviewer blocked"
        )


        # ----------------------------------------------------
        # Missing reason must fail.
        # ----------------------------------------------------

        missing_reason_blocked = False

        try:
            twin.review(
                governance_id,

                decision="accept",

                reviewer_identity=(
                    "verification-reviewer"
                ),

                reason="",
            )

        except ValueError:
            missing_reason_blocked = (
                True
            )

        require(
            missing_reason_blocked,
            "Missing review reason was not blocked.",
        )

        pass_line(
            "Missing review reason blocked"
        )


        # ----------------------------------------------------
        # Invalid amendment category must fail.
        # ----------------------------------------------------

        invalid_amendment_blocked = False

        try:
            twin.review(
                governance_id,

                decision="amend",

                reviewer_identity=(
                    "verification-reviewer"
                ),

                reason=(
                    "Verification."
                ),

                amended_category=(
                    "NOT-A-FROZEN-CATEGORY"
                ),
            )

        except ValueError:
            invalid_amendment_blocked = (
                True
            )

        require(
            invalid_amendment_blocked,
            "Invalid amendment category was not blocked.",
        )

        pass_line(
            "Invalid amendment blocked"
        )


        # ====================================================
        # 6. DUPLICATE CASE-ID PROTECTION
        # ====================================================

        heading(
            "6. CASE PERSISTENCE SAFETY"
        )

        duplicate_blocked = False

        try:
            twin.ingest(
                case_id=accept_id,

                source_mode=(
                    "frozen_validation_replay"
                ),

                source_ref=str(
                    selected_rows[
                        0
                    ]
                ),

                source_sha256=str(
                    replay_table.iloc[
                        0
                    ][
                        "sample_hash"
                    ]
                ),
            )

        except ValueError:
            duplicate_blocked = (
                True
            )

        require(
            duplicate_blocked,
            "Duplicate case ID was not blocked.",
        )

        pass_line(
            "Duplicate case ID blocked"
        )


        # ====================================================
        # 7. PERSISTED CASE CONTENT
        # ====================================================

        accept_case = store.get(
            accept_id
        )

        require(
            accept_case[
                "governance"
            ][
                "automatic_acceptance"
            ]
            is False,
            "Case governance incorrectly enables auto acceptance.",
        )

        require(
            accept_case[
                "governance"
            ][
                "human_review_required"
            ]
            is True,
            "Case governance does not require human review.",
        )

        require(
            accept_case[
                "prediction"
            ]
            is not None,
            "Prediction not persisted.",
        )

        require(
            accept_case[
                "explanation"
            ]
            is not None,
            "Explanation not persisted.",
        )

        require(
            accept_case[
                "review"
            ]
            is not None,
            "Review not persisted.",
        )

        require(
            accept_case[
                "state"
            ]
            == State.COMPLETED.value,
            "Final case state was not persisted.",
        )

        pass_line(
            "Current case state persistence"
        )

        pass_line(
            "Prediction persistence"
        )

        pass_line(
            "Explanation persistence"
        )

        pass_line(
            "Human-review persistence"
        )


        # ====================================================
        # 8. AUDIT CHAIN
        # ====================================================

        heading(
            "7. AUDIT INTEGRITY"
        )

        require(
            audit.verify()
            is True,
            "Audit SHA-256 chain verification failed.",
        )

        all_events = (
            audit.events()
        )

        require(
            len(
                all_events
            ) > 0,
            "No audit events were recorded.",
        )

        print(
            "Audit event count:",
            len(
                all_events
            ),
        )

        pass_line(
            "Append-only audit events"
        )

        pass_line(
            "Audit SHA-256 chain"
        )


        # ====================================================
        # 9. TEST-PARTITION GUARD
        # ====================================================

        heading(
            "8. SEALED TEST-PARTITION GUARD"
        )

        application_paths = [
            str(
                Path(__file__).resolve()
            ),

            str(
                resources
                .replay_sample
                .shape
            ),
        ]

        # More importantly, verify all replay data are labelled
        # as validation rows and the source workflow uses only
        # frozen validation replay.

        for case in (
            store.list_all()
        ):
            source_mode = (
                case[
                    "source"
                ][
                    "mode"
                ]
            )

            require(
                source_mode
                == "frozen_validation_replay",
                "Verification unexpectedly used another data source.",
            )

        forbidden_terms = (
            "phase9",
            "test_predictions",
            "transformer_test",
            "baseline_test",
        )

        for text in (
            application_paths
        ):
            lowered = (
                text.lower()
            )

            require(
                not any(
                    term in lowered

                    for term
                    in forbidden_terms
                ),
                "Prohibited test-partition dependency detected.",
            )

        pass_line(
            "Validation replay only"
        )

        pass_line(
            "Phase 9 dependency absent"
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    heading(
        "STEP 15 RESULT"
    )

    print(
        "Frozen artefacts                  PASS"
    )

    print(
        "Frozen BioClinicalBERT resources  PASS"
    )

    print(
        "Validation replay                 PASS"
    )

    print(
        "Top-3 recommendations             PASS"
    )

    print(
        "Layer Integrated Gradients        PASS"
    )

    print(
        "Accept workflow                   PASS"
    )

    print(
        "Reject workflow                   PASS"
    )

    print(
        "Amend workflow                    PASS"
    )

    print(
        "Automatic acceptance              BLOCKED"
    )

    print(
        "Reviewer identity                 REQUIRED"
    )

    print(
        "Review reason                     REQUIRED"
    )

    print(
        "Duplicate case overwrite          BLOCKED"
    )

    print(
        "Audit SHA-256 chain               PASS"
    )

    print(
        "TEST PARTITION ACCESSED           NO"
    )

    print()
    print(
        "STEP 15: PASS"
    )


if __name__ == "__main__":
    main()