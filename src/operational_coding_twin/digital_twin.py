from __future__ import annotations

import hashlib
import json
import math
import os
import uuid

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from operational_coding_twin.audit_log import (
    AppendOnlyAuditLog,
)

from operational_coding_twin.case_store import (
    CaseStore,
)

from operational_coding_twin.config import (
    CALIBRATOR_REFERENCE,
    CLAIMS_REFERENCE,
    MODEL_REFERENCE,
)

from operational_coding_twin.explainability import (
    ExplanationResult,
)

from operational_coding_twin.inference import (
    PredictionResult,
)


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# STATES
# ============================================================

class State(str, Enum):
    INGESTED = "Ingested"
    PREPROCESSED = "Preprocessed"
    PREDICTED = "Predicted"
    EXPLAINED = "Explained"

    AWAITING_HUMAN_REVIEW = (
        "Awaiting Human Review"
    )

    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    AMENDED = "Amended"

    COMPLETED = "Completed"
    ERROR = "Error"


# ============================================================
# VALID TRANSITIONS
# ============================================================

VALID_TRANSITIONS: dict[
    State,
    set[State],
] = {

    State.INGESTED: {
        State.PREPROCESSED,
        State.ERROR,
    },

    State.PREPROCESSED: {
        State.PREDICTED,
        State.ERROR,
    },

    State.PREDICTED: {
        State.EXPLAINED,
        State.ERROR,
    },

    State.EXPLAINED: {
        State.AWAITING_HUMAN_REVIEW,
        State.ERROR,
    },

    State.AWAITING_HUMAN_REVIEW: {
        State.ACCEPTED,
        State.REJECTED,
        State.AMENDED,
        State.ERROR,
    },

    State.ACCEPTED: {
        State.COMPLETED,
        State.ERROR,
    },

    State.REJECTED: {
        State.COMPLETED,
        State.ERROR,
    },

    State.AMENDED: {
        State.COMPLETED,
        State.ERROR,
    },

    State.COMPLETED: set(),

    State.ERROR: set(),
}


# ============================================================
# DIGITAL TWIN
# ============================================================

class OperationalCodingTwin:
    """
    Operational digital twin for a synthetic/demo
    clinical-coding case.

    The twin maintains:

        - current case state
        - frozen model recommendation
        - calibrated confidence
        - Top-3 shortlist
        - XAI evidence
        - mandatory human-review decision
        - final coding disposition
        - append-only audit history

    Automatic acceptance is deliberately unsupported.
    """

    def __init__(
        self,
        *,
        store: CaseStore,
        audit: AppendOnlyAuditLog,
        valid_categories: set[str],
        explanations_dir: Path,
    ) -> None:

        self.store = store
        self.audit = audit

        self.valid_categories = set(
            valid_categories
        )

        self.explanations_dir = Path(
            explanations_dir
        )

        self.explanations_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        if len(
            self.valid_categories
        ) != 50:

            raise RuntimeError(
                "Operational twin requires exactly "
                "50 frozen ICD-10 categories."
            )


    # ========================================================
    # INTERNAL
    # ========================================================

    def _load(
        self,
        case_id: str,
    ) -> dict[str, Any]:

        return self.store.get(
            case_id
        )


    def _current_state(
        self,
        case: dict[str, Any],
    ) -> State:

        try:

            return State(
                case[
                    "state"
                ]
            )

        except (
            KeyError,
            ValueError,
        ) as exc:

            raise RuntimeError(
                "Case contains an invalid state."
            ) from exc


    def _transition(
        self,
        *,
        case: dict[str, Any],
        target: State,
        actor: str,
        action: str,
        reason: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        current = self._current_state(
            case
        )

        if (
            target
            not in VALID_TRANSITIONS[
                current
            ]
        ):

            # Record prohibited transition attempt.
            self.audit.append(
                case_id=case[
                    "case_id"
                ],

                actor=actor,

                action=(
                    "INVALID_TRANSITION_ATTEMPT"
                ),

                reason=(
                    f"{current.value} -> "
                    f"{target.value} prohibited. "
                    f"{reason}"
                ),

                from_state=(
                    current.value
                ),

                to_state=(
                    target.value
                ),

                payload={
                    "requested_action":
                        action,
                },
            )

            raise RuntimeError(
                "Invalid digital-twin transition: "
                f"{current.value} -> "
                f"{target.value}"
            )

        previous_state = (
            current.value
        )

        case[
            "state"
        ] = target.value

        case[
            "updated_at_utc"
        ] = utc_now()

        self.store.save(
            case[
                "case_id"
            ],
            case,
        )

        self.audit.append(
            case_id=case[
                "case_id"
            ],

            actor=actor,

            action=action,

            reason=reason,

            from_state=previous_state,

            to_state=target.value,

            payload=(
                payload
                or {}
            ),
        )

        return case


    # ========================================================
    # INGEST
    # ========================================================

    def ingest(
        self,
        *,
        source_mode: str,
        clinical_text: str | None = None,
        source_ref: str | None = None,
        source_sha256: str | None = None,
        case_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new operational-twin case.

        Supported application modes will later include:

            synthetic_note
            synthetic_csv
            frozen_validation_replay
        """

        source_mode = (
            source_mode
            or ""
        ).strip()

        allowed_modes = {
            "synthetic_note",
            "synthetic_csv",
            "frozen_validation_replay",
        }

        if (
            source_mode
            not in allowed_modes
        ):

            raise ValueError(
                "Unsupported source_mode."
            )

        if case_id is None:

            case_id = (
                f"TWIN-{uuid.uuid4()}"
            )

        case_id = (
            case_id
            .strip()
        )

        if not case_id:

            raise ValueError(
                "case_id cannot be empty."
            )

        # ----------------------------------------------------
        # Prevent accidental overwriting of an existing twin.
        # ----------------------------------------------------

        if self.store.exists(
            case_id
        ):

            raise ValueError(
                "Case already exists: "
                f"{case_id}"
            )

        # ----------------------------------------------------
        # Fresh synthetic modes require text.
        # ----------------------------------------------------

        if source_mode in {
            "synthetic_note",
            "synthetic_csv",
        }:

            if clinical_text is None:

                raise ValueError(
                    "Synthetic inference mode "
                    "requires clinical_text."
                )

            clinical_text = (
                str(
                    clinical_text
                )
                .strip()
            )

            if len(
                clinical_text
            ) < 30:

                raise ValueError(
                    "Clinical text is too short."
                )

            calculated_source_hash = (
                hashlib.sha256(
                    clinical_text.encode(
                        "utf-8"
                    )
                )
                .hexdigest()
            )

        else:

            # Validation replay should not require copying
            # validation clinical text into the runtime case.
            calculated_source_hash = (
                source_sha256
            )

        if (
            source_sha256 is not None
            and
            calculated_source_hash is not None
            and
            source_sha256
            != calculated_source_hash
            and
            source_mode
            != "frozen_validation_replay"
        ):

            raise ValueError(
                "Provided source SHA-256 does not "
                "match the supplied clinical text."
            )

        now = utc_now()

        case: dict[str, Any] = {

            "case_id":
                case_id,

            "state":
                State.INGESTED.value,

            "created_at_utc":
                now,

            "updated_at_utc":
                now,

            "source": {
                "mode":
                    source_mode,

                "reference":
                    source_ref,

                "sha256":
                    (
                        source_sha256
                        or calculated_source_hash
                    ),
            },

            # Store text only for explicitly synthetic/demo
            # inference modes.
            "clinical_text": (
                clinical_text
                if source_mode
                in {
                    "synthetic_note",
                    "synthetic_csv",
                }
                else None
            ),

            "preprocessing": None,

            "prediction": None,

            "explanation": None,

            "review": None,

            "final_category": None,

            "governance": {
                "model_reference":
                    MODEL_REFERENCE,

                "calibrator_reference":
                    CALIBRATOR_REFERENCE,

                "claims_reference":
                    CLAIMS_REFERENCE,

                "automatic_acceptance":
                    False,

                "human_review_required":
                    True,
            },
        }

        self.store.save(
            case_id,
            case,
        )

        self.audit.append(
            case_id=case_id,

            actor="system",

            action="CASE_INGESTED",

            reason=(
                "New coding case created in "
                "operational twin."
            ),

            from_state=None,

            to_state=(
                State.INGESTED.value
            ),

            payload={
                "source_mode":
                    source_mode,

                "source_sha256":
                    case[
                        "source"
                    ][
                        "sha256"
                    ],

                "automatic_acceptance":
                    False,

                "human_review_required":
                    True,
            },
        )

        return case


    # ========================================================
    # PREPROCESS
    # ========================================================

    def preprocess(
        self,
        case_id: str,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        state = self._current_state(
            case
        )

        if (
            state
            != State.INGESTED
        ):

            return self._transition(
                case=case,

                target=State.PREPROCESSED,

                actor="system",

                action="PREPROCESS",

                reason=(
                    "Attempted preprocessing "
                    "from invalid state."
                ),
            )

        source_mode = (
            case[
                "source"
            ][
                "mode"
            ]
        )

        if source_mode in {
            "synthetic_note",
            "synthetic_csv",
        }:

            clinical_text = (
                case.get(
                    "clinical_text"
                )
                or ""
            ).strip()

            if len(
                clinical_text
            ) < 30:

                raise ValueError(
                    "Clinical text failed "
                    "preprocessing validation."
                )

            preprocessing = {
                "input_policy":
                    "clinical_text_only",

                "characters":
                    len(
                        clinical_text
                    ),

                "status":
                    "validated",
            }

        else:

            preprocessing = {
                "input_policy":
                    "frozen_validation_replay",

                "status":
                    "validated",
            }

        case[
            "preprocessing"
        ] = preprocessing

        return self._transition(
            case=case,

            target=(
                State.PREPROCESSED
            ),

            actor="system",

            action=(
                "CASE_PREPROCESSED"
            ),

            reason=(
                "Input satisfied frozen "
                "operational preprocessing contract."
            ),

            payload=preprocessing,
        )


    # ========================================================
    # ATTACH PREDICTION
    # ========================================================

    def attach_prediction(
        self,
        case_id: str,
        prediction: PredictionResult,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        if (
            self._current_state(
                case
            )
            != State.PREPROCESSED
        ):

            return self._transition(
                case=case,

                target=State.PREDICTED,

                actor="system",

                action="PREDICT",

                reason=(
                    "Attempted prediction attachment "
                    "from invalid state."
                ),
            )

        recommendation = (
            prediction.recommendation
        )

        if (
            recommendation
            not in self.valid_categories
        ):

            raise RuntimeError(
                "Prediction is outside frozen "
                "ICD-10 category space."
            )

        if len(
            prediction.top3
        ) != 3:

            raise RuntimeError(
                "Prediction must contain "
                "exactly three ranked categories."
            )

        # ----------------------------------------------------
        # Validate Top-3
        # ----------------------------------------------------

        categories = []

        expected_ranks = [
            1,
            2,
            3,
        ]

        for (
            expected_rank,
            item,
        ) in zip(
            expected_ranks,
            prediction.top3,
        ):

            if (
                item.rank
                != expected_rank
            ):

                raise RuntimeError(
                    "Top-3 ranks must be 1, 2, 3."
                )

            if (
                item.category
                not in self.valid_categories
            ):

                raise RuntimeError(
                    "Top-3 contains unknown "
                    "ICD-10 category."
                )

            if (
                not math.isfinite(
                    item.probability
                )
                or
                item.probability < 0
                or
                item.probability > 1
            ):

                raise RuntimeError(
                    "Invalid Top-3 probability."
                )

            categories.append(
                item.category
            )

        if len(
            set(
                categories
            )
        ) != 3:

            raise RuntimeError(
                "Top-3 categories must be unique."
            )

        if (
            categories[
                0
            ]
            != recommendation
        ):

            raise RuntimeError(
                "Top-1 category must match "
                "the recommendation."
            )

        if not math.isclose(
            prediction.calibrated_confidence,
            prediction.top3[
                0
            ].probability,
            rel_tol=0.0,
            abs_tol=1e-8,
        ):

            raise RuntimeError(
                "Calibrated confidence must match "
                "the Top-1 probability."
            )

        case[
            "prediction"
        ] = {

            "recommendation":
                recommendation,

            "predicted_class_id":
                int(
                    prediction.predicted_class_id
                ),

            "calibrated_confidence":
                float(
                    prediction.calibrated_confidence
                ),

            "raw_confidence":
                (
                    float(
                        prediction.raw_confidence
                    )
                    if math.isfinite(
                        prediction.raw_confidence
                    )
                    else None
                ),

            "temperature":
                float(
                    prediction.temperature
                ),

            "input_tokens":
                int(
                    prediction.input_tokens
                ),

            "truncated":
                bool(
                    prediction.truncated
                ),

            "source_mode":
                prediction.source_mode,

            "top3": [
                {
                    "rank":
                        item.rank,

                    "category":
                        item.category,

                    "probability":
                        float(
                            item.probability
                        ),
                }

                for item in (
                    prediction.top3
                )
            ],
        }

        return self._transition(
            case=case,

            target=(
                State.PREDICTED
            ),

            actor="system",

            action=(
                "MODEL_PREDICTION_RECORDED"
            ),

            reason=(
                "Frozen BioClinicalBERT "
                "recommendation recorded."
            ),

            payload={
                "recommendation":
                    recommendation,

                "calibrated_confidence":
                    float(
                        prediction
                        .calibrated_confidence
                    ),

                "automatic_acceptance":
                    False,
            },
        )


    # ========================================================
    # SAVE EXPLANATION FILE
    # ========================================================

    def _save_explanation(
        self,
        *,
        case_id: str,
        explanation: ExplanationResult,
    ) -> Path:

        safe_case_id = (
            hashlib.sha256(
                case_id.encode(
                    "utf-8"
                )
            )
            .hexdigest()[
                :24
            ]
        )

        target = (
            self.explanations_dir
            / (
                f"explanation_"
                f"{safe_case_id}.json"
            )
        )

        temporary = (
            target.with_suffix(
                ".tmp"
            )
        )

        payload = {

            "case_id":
                case_id,

            "category":
                explanation.category,

            "method":
                explanation.method,

            "steps":
                explanation.steps,

            "baseline":
                explanation.baseline,

            "source_mode":
                explanation.source_mode,

            "warning":
                explanation.warning,

            "convergence_delta":
                explanation.convergence_delta,

            "evidence": [
                {
                    "position":
                        item.position,

                    "token":
                        item.token,

                    "raw_score":
                        item.raw_score,

                    "normalized_score":
                        item.normalized_score,
                }

                for item in (
                    explanation.evidence
                )
            ],

            "all_token_attributions": [
                {
                    "position":
                        item.position,

                    "token":
                        item.token,

                    "raw_score":
                        item.raw_score,

                    "normalized_score":
                        item.normalized_score,
                }

                for item in (
                    explanation
                    .all_token_attributions
                )
            ],
        }

        temporary.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )

        os.replace(
            temporary,
            target,
        )

        return target


    # ========================================================
    # ATTACH EXPLANATION
    # ========================================================

    def attach_explanation(
        self,
        case_id: str,
        explanation: ExplanationResult,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        if (
            self._current_state(
                case
            )
            != State.PREDICTED
        ):

            return self._transition(
                case=case,

                target=State.EXPLAINED,

                actor="system",

                action="EXPLAIN",

                reason=(
                    "Attempted explanation attachment "
                    "from invalid state."
                ),
            )

        prediction = case.get(
            "prediction"
        )

        if not prediction:

            raise RuntimeError(
                "Case has no recorded prediction."
            )

        if (
            explanation.category
            != prediction[
                "recommendation"
            ]
        ):

            raise RuntimeError(
                "Explanation target does not match "
                "the predicted category."
            )

        if (
            int(
                explanation.steps
            )
            != 50
        ):

            raise RuntimeError(
                "Operational XAI contract requires "
                "50 LIG steps."
            )

        if (
            "Layer Integrated Gradients"
            not in explanation.method
        ):

            raise RuntimeError(
                "Unexpected explainability method."
            )

        explanation_path = (
            self._save_explanation(
                case_id=case_id,
                explanation=explanation,
            )
        )

        case[
            "explanation"
        ] = {

            "category":
                explanation.category,

            "method":
                explanation.method,

            "steps":
                explanation.steps,

            "baseline":
                explanation.baseline,

            "source_mode":
                explanation.source_mode,

            "warning":
                explanation.warning,

            "convergence_delta":
                explanation.convergence_delta,

            "evidence_count":
                len(
                    explanation.evidence
                ),

            "explanation_ref":
                str(
                    explanation_path
                ),
        }

        return self._transition(
            case=case,

            target=(
                State.EXPLAINED
            ),

            actor="system",

            action=(
                "EXPLANATION_RECORDED"
            ),

            reason=(
                "Layer Integrated Gradients "
                "evidence recorded."
            ),

            payload={
                "method":
                    explanation.method,

                "steps":
                    explanation.steps,

                "category":
                    explanation.category,

                "explanation_ref":
                    str(
                        explanation_path
                    ),
            },
        )


    # ========================================================
    # SEND TO HUMAN REVIEW
    # ========================================================

    def send_for_review(
        self,
        case_id: str,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        if (
            self._current_state(
                case
            )
            != State.EXPLAINED
        ):

            return self._transition(
                case=case,

                target=(
                    State.AWAITING_HUMAN_REVIEW
                ),

                actor="system",

                action="SEND_FOR_REVIEW",

                reason=(
                    "Attempted review queueing "
                    "from invalid state."
                ),
            )

        if not case.get(
            "prediction"
        ):

            raise RuntimeError(
                "Prediction is required before review."
            )

        if not case.get(
            "explanation"
        ):

            raise RuntimeError(
                "Explanation is required before review."
            )

        return self._transition(
            case=case,

            target=(
                State.AWAITING_HUMAN_REVIEW
            ),

            actor="system",

            action=(
                "HUMAN_REVIEW_REQUIRED"
            ),

            reason=(
                "Prediction and explanation ready "
                "for mandatory human review."
            ),

            payload={
                "automatic_acceptance":
                    False,

                "human_review_required":
                    True,
            },
        )


    # ========================================================
    # HUMAN REVIEW
    # ========================================================

    def review(
        self,
        case_id: str,
        *,
        decision: str,
        reviewer_identity: str,
        reason: str,
        amended_category: str | None = None,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        if (
            self._current_state(
                case
            )
            != State.AWAITING_HUMAN_REVIEW
        ):

            raise RuntimeError(
                "Human review is permitted only "
                "from Awaiting Human Review."
            )

        reviewer_identity = (
            reviewer_identity
            or ""
        ).strip()

        reason = (
            reason
            or ""
        ).strip()

        decision = (
            decision
            or ""
        ).strip().lower()

        if not reviewer_identity:

            raise ValueError(
                "Reviewer identity is mandatory."
            )

        if not reason:

            raise ValueError(
                "Reviewer reason is mandatory."
            )

        allowed_decisions = {
            "accept",
            "reject",
            "amend",
        }

        if (
            decision
            not in allowed_decisions
        ):

            raise ValueError(
                "decision must be "
                "accept, reject, or amend."
            )

        recommendation = (
            case[
                "prediction"
            ][
                "recommendation"
            ]
        )

        # ----------------------------------------------------
        # ACCEPT
        # ----------------------------------------------------

        if decision == "accept":

            if amended_category is not None:

                raise ValueError(
                    "amended_category must not be "
                    "provided for an accept decision."
                )

            target = (
                State.ACCEPTED
            )

            final_category = (
                recommendation
            )

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        elif decision == "reject":

            if amended_category is not None:

                raise ValueError(
                    "amended_category must not be "
                    "provided for a reject decision."
                )

            target = (
                State.REJECTED
            )

            final_category = None

        # ----------------------------------------------------
        # AMEND
        # ----------------------------------------------------

        else:

            amended_category = (
                amended_category
                or ""
            ).strip()

            if not amended_category:

                raise ValueError(
                    "An amended category is required "
                    "for an amend decision."
                )

            if (
                amended_category
                not in self.valid_categories
            ):

                raise ValueError(
                    "Amended category is outside "
                    "the frozen ICD-10 label space."
                )

            if (
                amended_category
                == recommendation
            ):

                raise ValueError(
                    "Amended category must differ "
                    "from the model recommendation. "
                    "Use accept otherwise."
                )

            target = (
                State.AMENDED
            )

            final_category = (
                amended_category
            )

        review_time = utc_now()

        case[
            "review"
        ] = {

            "reviewer_identity":
                reviewer_identity,

            "decision":
                decision,

            "reason":
                reason,

            "reviewed_at_utc":
                review_time,

            "model_recommendation":
                recommendation,

            "amended_category":
                (
                    amended_category
                    if decision == "amend"
                    else None
                ),
        }

        case[
            "final_category"
        ] = final_category

        return self._transition(
            case=case,

            target=target,

            actor=(
                reviewer_identity
            ),

            action=(
                f"HUMAN_REVIEW_"
                f"{decision.upper()}"
            ),

            reason=reason,

            payload={
                "model_recommendation":
                    recommendation,

                "final_category":
                    final_category,

                "decision":
                    decision,

                "human_review":
                    True,
            },
        )


    # ========================================================
    # COMPLETE
    # ========================================================

    def complete(
        self,
        case_id: str,
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        state = self._current_state(
            case
        )

        allowed = {
            State.ACCEPTED,
            State.REJECTED,
            State.AMENDED,
        }

        if state not in allowed:

            raise RuntimeError(
                "Case can be completed only after "
                "Accepted, Rejected, or Amended."
            )

        review = case.get(
            "review"
        )

        if not review:

            raise RuntimeError(
                "Human review record is required "
                "before completion."
            )

        if not review.get(
            "reviewer_identity"
        ):

            raise RuntimeError(
                "Reviewer identity is missing."
            )

        if not review.get(
            "reason"
        ):

            raise RuntimeError(
                "Reviewer reason is missing."
            )

        return self._transition(
            case=case,

            target=(
                State.COMPLETED
            ),

            actor=(
                review[
                    "reviewer_identity"
                ]
            ),

            action=(
                "CASE_COMPLETED"
            ),

            reason=(
                "Mandatory human-review workflow "
                "completed."
            ),

            payload={
                "review_decision":
                    review[
                        "decision"
                    ],

                "final_category":
                    case.get(
                        "final_category"
                    ),

                "automatic_acceptance":
                    False,
            },
        )


    # ========================================================
    # ERROR
    # ========================================================

    def fail(
        self,
        case_id: str,
        *,
        error: str,
        actor: str = "system",
    ) -> dict[str, Any]:

        case = self._load(
            case_id
        )

        state = self._current_state(
            case
        )

        if state in {
            State.COMPLETED,
            State.ERROR,
        }:

            raise RuntimeError(
                "Terminal case cannot transition "
                "to Error."
            )

        error = (
            error
            or ""
        ).strip()

        if not error:

            raise ValueError(
                "Error description is required."
            )

        case[
            "error"
        ] = {

            "message":
                error,

            "recorded_at_utc":
                utc_now(),
        }

        return self._transition(
            case=case,

            target=(
                State.ERROR
            ),

            actor=actor,

            action=(
                "CASE_ERROR"
            ),

            reason=error,

            payload={
                "error":
                    error,
            },
        )


    # ========================================================
    # GET CASE
    # ========================================================

    def get_case(
        self,
        case_id: str,
    ) -> dict[str, Any]:

        return self._load(
            case_id
        )