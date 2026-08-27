from __future__ import annotations

import json
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from operational_coding_twin.audit_log import (
    AppendOnlyAuditLog,
)

from operational_coding_twin.case_store import (
    CaseStore,
)

from operational_coding_twin.config import (
    CONFIDENCE_WARNING,
    EXPLANATION_WARNING,
    get_settings,
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
    PredictionResult,
    RankedPrediction,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Operational Coding Twin",
    page_icon="🩺",
    layout="wide",
)


# ============================================================
# LOAD FROZEN SERVICES
# ============================================================

@st.cache_resource(
    show_spinner="Loading frozen BioClinicalBERT resources..."
)
def load_services():
    """
    Load the frozen scientific resources exactly once per
    Streamlit process.
    """

    settings = get_settings()

    resources = load_frozen_resources()

    inference = FrozenInferenceService(
        resources
    )

    explainability = FrozenExplainabilityService(
        resources
    )

    store = CaseStore(
        settings.cases_dir
    )

    audit = AppendOnlyAuditLog(
        settings.audit_dir
        / "operational_twin_audit.jsonl"
    )

    twin = OperationalCodingTwin(
        store=store,
        audit=audit,
        valid_categories=set(
            resources.label2id.keys()
        ),
        explanations_dir=(
            settings.explanations_dir
        ),
    )

    return {
        "settings": settings,
        "resources": resources,
        "inference": inference,
        "explainability": explainability,
        "store": store,
        "audit": audit,
        "twin": twin,
    }


try:
    SERVICES = load_services()

except Exception as exc:
    st.error(
        "The operational twin could not load "
        "its frozen scientific resources."
    )

    st.exception(
        exc
    )

    st.stop()


settings = SERVICES["settings"]
resources = SERVICES["resources"]
inference = SERVICES["inference"]
explainability = SERVICES["explainability"]
store = SERVICES["store"]
audit = SERVICES["audit"]
twin = SERVICES["twin"]


# ============================================================
# SESSION STATE
# ============================================================

if "active_case_id" not in st.session_state:
    st.session_state[
        "active_case_id"
    ] = None


# ============================================================
# HELPERS
# ============================================================

def rerun() -> None:
    st.rerun()


def get_active_case():
    """
    Return the currently selected operational-twin case.
    """

    case_id = st.session_state.get(
        "active_case_id"
    )

    if not case_id:
        return None

    try:
        return twin.get_case(
            case_id
        )

    except KeyError:
        st.session_state[
            "active_case_id"
        ] = None

        return None


def prediction_from_case(
    case: dict,
) -> PredictionResult:
    """
    Reconstruct a typed PredictionResult from a persisted
    digital-twin case.
    """

    stored = case.get(
        "prediction"
    )

    if not stored:
        raise RuntimeError(
            "Case does not contain a prediction."
        )

    top3 = [
        RankedPrediction(
            rank=int(
                item["rank"]
            ),
            category=str(
                item["category"]
            ),
            probability=float(
                item["probability"]
            ),
        )
        for item in stored["top3"]
    ]

    raw = stored.get(
        "raw_confidence"
    )

    raw_confidence = (
        float(raw)
        if raw is not None
        else float("nan")
    )

    return PredictionResult(
        recommendation=str(
            stored["recommendation"]
        ),

        predicted_class_id=int(
            stored["predicted_class_id"]
        ),

        calibrated_confidence=float(
            stored["calibrated_confidence"]
        ),

        raw_confidence=raw_confidence,

        top3=top3,

        temperature=float(
            stored["temperature"]
        ),

        input_tokens=int(
            stored.get(
                "input_tokens",
                0,
            )
        ),

        truncated=bool(
            stored.get(
                "truncated",
                False,
            )
        ),

        source_mode=str(
            stored["source_mode"]
        ),
    )


def render_prediction(
    case: dict,
) -> None:
    """
    Display model recommendation and Top-3 shortlist.
    """

    prediction = case.get(
        "prediction"
    )

    if not prediction:
        return

    st.subheader(
        "Model recommendation"
    )

    c1, c2, c3 = st.columns(
        3
    )

    c1.metric(
        "Top-1 ICD-10 category",
        prediction[
            "recommendation"
        ],
    )

    c2.metric(
        "Calibrated confidence",
        f"{prediction['calibrated_confidence']:.3f}",
    )

    c3.metric(
        "Temperature",
        f"{prediction['temperature']:.10f}",
    )

    st.warning(
        CONFIDENCE_WARNING
    )

    top3 = pd.DataFrame(
        prediction["top3"]
    )

    top3 = top3[
        [
            "rank",
            "category",
            "probability",
        ]
    ]

    top3.columns = [
        "Rank",
        "ICD-10 category",
        "Calibrated probability",
    ]

    st.markdown(
        "**Reviewer Top-3 shortlist**"
    )

    st.dataframe(
        top3,
        hide_index=True,
        use_container_width=True,
    )

    if prediction.get(
        "truncated"
    ):
        st.warning(
            "The note exceeded the frozen 320-token "
            "model input limit and was truncated."
        )


def render_explanation(
    case: dict,
) -> None:
    """
    Display saved explainability evidence.
    """

    explanation = case.get(
        "explanation"
    )

    if not explanation:
        return

    st.subheader(
        "Explainability evidence"
    )

    st.write(
        f"**Method:** "
        f"{explanation['method']}"
    )

    st.write(
        f"**Target category:** "
        f"{explanation['category']}"
    )

    st.write(
        f"**Integration steps:** "
        f"{explanation['steps']}"
    )

    st.write(
        f"**Baseline:** "
        f"{explanation['baseline']}"
    )

    st.warning(
        EXPLANATION_WARNING
    )

    explanation_ref = (
        explanation.get(
            "explanation_ref"
        )
    )

    if not explanation_ref:
        st.info(
            "No detailed explanation reference "
            "is available for this case."
        )
        return

    try:
        path = Path(
            explanation_ref
        )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        evidence = data.get(
            "evidence",
            [],
        )

        if evidence:
            frame = pd.DataFrame(
                evidence
            )

            wanted = [
                column
                for column in (
                    "position",
                    "token",
                    "raw_score",
                    "normalized_score",
                )
                if column in frame.columns
            ]

            st.dataframe(
                frame[wanted],
                hide_index=True,
                use_container_width=True,
            )

        else:
            st.info(
                "No positive supporting tokens "
                "were retained for this case."
            )

    except Exception as exc:
        st.warning(
            "Explanation summary exists, but "
            "the detailed explanation file "
            "could not be displayed."
        )

        st.caption(
            str(exc)
        )


def render_review(
    case: dict,
) -> None:
    """
    Display completed human-review information.
    """

    review = case.get(
        "review"
    )

    if not review:
        return

    st.subheader(
        "Human review decision"
    )

    c1, c2 = st.columns(
        2
    )

    c1.write(
        f"**Reviewer:** "
        f"{review['reviewer_identity']}"
    )

    c1.write(
        f"**Decision:** "
        f"{review['decision'].upper()}"
    )

    c2.write(
        f"**Model recommendation:** "
        f"{review['model_recommendation']}"
    )

    c2.write(
        f"**Final category:** "
        f"{case.get('final_category') or 'None'}"
    )

    st.write(
        f"**Review reason:** "
        f"{review['reason']}"
    )


def render_audit(
    case_id: str,
) -> None:
    """
    Display the append-only audit trail.
    """

    st.subheader(
        "Operational audit trail"
    )

    events = audit.events(
        case_id
    )

    if not events:
        st.info(
            "No audit events recorded."
        )
        return

    frame = pd.DataFrame(
        events
    )

    columns = [
        column
        for column in (
            "timestamp_utc",
            "actor",
            "action",
            "from_state",
            "to_state",
            "reason",
            "event_hash",
        )
        if column in frame.columns
    ]

    st.dataframe(
        frame[columns],
        hide_index=True,
        use_container_width=True,
    )

    try:
        valid = audit.verify()

        if valid:
            st.success(
                "Audit SHA-256 chain: PASS"
            )

    except Exception as exc:
        st.error(
            "Audit SHA-256 chain: FAIL"
        )

        st.exception(
            exc
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Operational Twin"
)

st.sidebar.caption(
    "Research prototype — synthetic/demo data only."
)

if st.sidebar.button(
    "＋ New case",
    use_container_width=True,
):
    st.session_state[
        "active_case_id"
    ] = None

    rerun()


existing_cases = (
    store.list_all()
)

if existing_cases:
    case_ids = [
        case["case_id"]
        for case in existing_cases
    ]

    active = (
        st.session_state.get(
            "active_case_id"
        )
    )

    selected = st.sidebar.selectbox(
        "Open existing case",
        options=[""] + case_ids,
        index=(
            case_ids.index(active) + 1
            if active in case_ids
            else 0
        ),
    )

    if (
        selected
        and selected != active
    ):
        st.session_state[
            "active_case_id"
        ] = selected

        rerun()


st.sidebar.divider()

st.sidebar.write(
    "**Frozen model**"
)

st.sidebar.caption(
    "BioClinicalBERT seed 42"
)

st.sidebar.write(
    "**Label space**"
)

st.sidebar.caption(
    "50 ICD-10 categories"
)

st.sidebar.write(
    "**Calibration**"
)

st.sidebar.caption(
    f"T = {resources.temperature:.10f}"
)

st.sidebar.write(
    "**Automatic acceptance**"
)

st.sidebar.caption(
    "Disabled"
)

st.sidebar.write(
    "**Human review**"
)

st.sidebar.caption(
    "Mandatory"
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "AI-Powered Operational Digital Twin for Medical Coding"
)

st.caption(
    "Synthetic/demo research prototype using frozen "
    "BioClinicalBERT inference, calibrated confidence, "
    "Layer Integrated Gradients and mandatory human review."
)

st.info(
    "This prototype is for synthetic/demo research use only. "
    "It does not establish clinical or NHS deployment validity."
)


# ============================================================
# ACTIVE CASE
# ============================================================

case = get_active_case()


# ============================================================
# CREATE NEW CASE
# ============================================================

if case is None:
    st.header(
        "Create a coding case"
    )

    mode = st.radio(
        "Input mode",
        options=[
            "New synthetic clinical note",
            "Synthetic CSV upload",
            "Frozen validation replay",
        ],
        horizontal=True,
    )

    # ========================================================
    # MODE 1 — SYNTHETIC NOTE
    # ========================================================

    if mode == "New synthetic clinical note":
        st.info(
            "Use synthetic or demonstration text only. "
            "Do not enter real identifiable patient data."
        )

        clinical_text = st.text_area(
            "Synthetic clinical note",
            height=260,
            placeholder=(
                "Enter a synthetic discharge-summary-style "
                "clinical narrative..."
            ),
        )

        synthetic_confirmed = (
            st.checkbox(
                "I confirm this is synthetic/demo text "
                "and contains no real identifiable "
                "patient information."
            )
        )

        if st.button(
            "Create twin case",
            type="primary",
            disabled=(
                not synthetic_confirmed
            ),
        ):
            try:
                clean_text = (
                    clinical_text
                    or ""
                ).strip()

                if len(clean_text) < 30:
                    st.error(
                        "Enter at least 30 characters of "
                        "synthetic clinical text."
                    )

                else:
                    case_id = (
                        f"SYN-"
                        f"{uuid.uuid4().hex[:12].upper()}"
                    )

                    twin.ingest(
                        case_id=case_id,
                        source_mode=(
                            "synthetic_note"
                        ),
                        clinical_text=(
                            clean_text
                        ),
                    )

                    st.session_state[
                        "active_case_id"
                    ] = case_id

                    rerun()

            except ValueError as exc:
                st.error(
                    str(exc)
                )

            except RuntimeError as exc:
                st.error(
                    str(exc)
                )

            except Exception as exc:
                st.error(
                    "Case could not be created."
                )

                st.exception(
                    exc
                )

    # ========================================================
    # MODE 2 — SYNTHETIC CSV
    # ========================================================

    elif mode == "Synthetic CSV upload":
        st.info(
            "Upload synthetic/demo data only. "
            "The CSV must contain a `clinical_text` column."
        )

        uploaded = st.file_uploader(
            "Synthetic CSV",
            type=[
                "csv"
            ],
        )

        synthetic_confirmed = (
            st.checkbox(
                "I confirm the uploaded CSV contains "
                "synthetic/demo data only and no real "
                "identifiable patient information."
            )
        )

        if uploaded is not None:
            try:
                csv_data = pd.read_csv(
                    uploaded
                )

            except Exception as exc:
                st.error(
                    "Unable to read CSV."
                )

                st.exception(
                    exc
                )

                csv_data = None

            if csv_data is not None:
                if (
                    "clinical_text"
                    not in csv_data.columns
                ):
                    st.error(
                        "CSV must contain a "
                        "`clinical_text` column."
                    )

                elif len(csv_data) == 0:
                    st.error(
                        "CSV contains no rows."
                    )

                else:
                    st.write(
                        f"Rows detected: "
                        f"{len(csv_data)}"
                    )

                    row_index = st.selectbox(
                        "Choose a row",
                        options=list(
                            csv_data.index
                        ),
                    )

                    selected_row = (
                        csv_data.loc[
                            row_index
                        ]
                    )

                    selected_text = str(
                        selected_row[
                            "clinical_text"
                        ]
                    )

                    st.text_area(
                        "Selected clinical text",
                        value=selected_text,
                        height=220,
                        disabled=True,
                    )

                    if st.button(
                        "Create twin case from selected row",
                        type="primary",
                        disabled=(
                            not synthetic_confirmed
                        ),
                    ):
                        try:
                            clean_text = (
                                selected_text
                                or ""
                            ).strip()

                            if len(clean_text) < 30:
                                st.error(
                                    "Selected clinical_text "
                                    "is too short."
                                )

                            else:
                                case_id = (
                                    f"CSV-"
                                    f"{uuid.uuid4().hex[:12].upper()}"
                                )

                                twin.ingest(
                                    case_id=case_id,

                                    source_mode=(
                                        "synthetic_csv"
                                    ),

                                    clinical_text=(
                                        clean_text
                                    ),

                                    source_ref=(
                                        f"uploaded_csv_row:"
                                        f"{row_index}"
                                    ),
                                )

                                st.session_state[
                                    "active_case_id"
                                ] = case_id

                                rerun()

                        except ValueError as exc:
                            st.error(
                                str(exc)
                            )

                        except RuntimeError as exc:
                            st.error(
                                str(exc)
                            )

                        except Exception as exc:
                            st.error(
                                "CSV case could not "
                                "be created."
                            )

                            st.exception(
                                exc
                            )

    # ========================================================
    # MODE 3 — FROZEN VALIDATION REPLAY
    # ========================================================

    else:
        st.info(
            "Reproducibility mode. This uses only the "
            "deterministic Phase 8B validation sample "
            "and does not access the sealed test partition."
        )

        replay = (
            resources
            .replay_sample
            .sort_values(
                "sample_rank"
            )
            .reset_index(
                drop=True
            )
        )

        options = (
            replay[
                "validation_row"
            ]
            .astype(
                int
            )
            .tolist()
        )

        validation_row = (
            st.selectbox(
                "Frozen validation row",
                options=options,
                format_func=lambda row: (
                    f"Validation row {row}"
                ),
            )
        )

        selected = replay[
            replay[
                "validation_row"
            ].astype(
                int
            )
            == int(
                validation_row
            )
        ].iloc[0]

        st.write(
            f"**Encounter:** "
            f"{selected['encounter_id']}"
        )

        st.write(
            f"**Deterministic sample rank:** "
            f"{selected['sample_rank']}"
        )

        st.caption(
            "The reference category remains hidden "
            "during the review workflow."
        )

        if st.button(
            "Create replay twin case",
            type="primary",
        ):
            try:
                case_id = (
                    f"REPLAY-{validation_row}-"
                    f"{uuid.uuid4().hex[:8].upper()}"
                )

                twin.ingest(
                    case_id=case_id,

                    source_mode=(
                        "frozen_validation_replay"
                    ),

                    source_ref=str(
                        validation_row
                    ),

                    source_sha256=str(
                        selected[
                            "sample_hash"
                        ]
                    ),
                )

                st.session_state[
                    "active_case_id"
                ] = case_id

                rerun()

            except ValueError as exc:
                st.error(
                    str(exc)
                )

            except RuntimeError as exc:
                st.error(
                    str(exc)
                )

            except Exception as exc:
                st.error(
                    "Replay case could not "
                    "be created."
                )

                st.exception(
                    exc
                )

    st.stop()


# ============================================================
# DISPLAY ACTIVE CASE
# ============================================================

state = State(
    case["state"]
)

st.header(
    f"Case: {case['case_id']}"
)

c1, c2, c3 = st.columns(
    3
)

c1.metric(
    "Current twin state",
    state.value,
)

c2.metric(
    "Source",
    case[
        "source"
    ][
        "mode"
    ],
)

c3.metric(
    "Human review",
    "Required",
)


# ============================================================
# SOURCE INFORMATION
# ============================================================

with st.expander(
    "Case source",
    expanded=False,
):
    st.json(
        case["source"]
    )

    if case.get(
        "clinical_text"
    ):
        st.text_area(
            "Synthetic clinical text",
            value=case[
                "clinical_text"
            ],
            height=220,
            disabled=True,
        )


# ============================================================
# INGESTED → PREPROCESSED
# ============================================================

if state == State.INGESTED:
    st.subheader(
        "1. Preprocessing"
    )

    st.write(
        "Validate the case against the frozen "
        "`clinical_text` input contract."
    )

    if st.button(
        "Preprocess case",
        type="primary",
    ):
        try:
            twin.preprocess(
                case["case_id"]
            )

            rerun()

        except ValueError as exc:
            st.error(
                str(exc)
            )

        except RuntimeError as exc:
            st.error(
                str(exc)
            )

        except Exception as exc:
            st.error(
                "Preprocessing failed."
            )

            st.exception(
                exc
            )


# ============================================================
# PREPROCESSED → PREDICTED
# ============================================================

elif state == State.PREPROCESSED:
    st.success(
        "Input preprocessing completed."
    )

    st.subheader(
        "2. Generate coding recommendation"
    )

    source_mode = (
        case[
            "source"
        ][
            "mode"
        ]
    )

    if (
        source_mode
        == "frozen_validation_replay"
    ):
        st.write(
            "Load the frozen Phase 8B calibrated "
            "prediction for this validation case."
        )

    else:
        st.write(
            "Run the frozen seed-42 BioClinicalBERT "
            "classifier. No model training occurs."
        )

    if st.button(
        "Generate recommendation",
        type="primary",
    ):
        try:
            if (
                source_mode
                == "frozen_validation_replay"
            ):
                validation_row = int(
                    case[
                        "source"
                    ][
                        "reference"
                    ]
                )

                prediction = (
                    inference.replay(
                        validation_row
                    )
                )

            else:
                prediction = (
                    inference.predict(
                        case[
                            "clinical_text"
                        ]
                    )
                )

            twin.attach_prediction(
                case["case_id"],
                prediction,
            )

            rerun()

        except ValueError as exc:
            st.error(
                str(exc)
            )

        except RuntimeError as exc:
            st.error(
                str(exc)
            )

        except Exception as exc:
            st.error(
                "Prediction failed."
            )

            st.exception(
                exc
            )


# ============================================================
# PREDICTED → EXPLAINED
# ============================================================

elif state == State.PREDICTED:
    render_prediction(
        case
    )

    st.subheader(
        "3. Generate explanation"
    )

    source_mode = (
        case[
            "source"
        ][
            "mode"
        ]
    )

    if (
        source_mode
        == "frozen_validation_replay"
    ):
        st.write(
            "Load the saved Phase 8B "
            "Layer Integrated Gradients evidence."
        )

    else:
        st.write(
            "Calculate a fresh 50-step "
            "Layer Integrated Gradients explanation "
            "for the model's predicted category."
        )

        st.info(
            "Fresh LIG calculation may take some time "
            "on a CPU."
        )

    if st.button(
        "Generate explanation",
        type="primary",
    ):
        try:
            if (
                source_mode
                == "frozen_validation_replay"
            ):
                validation_row = int(
                    case[
                        "source"
                    ][
                        "reference"
                    ]
                )

                explanation = (
                    explainability.replay(
                        validation_row
                    )
                )

            else:
                prediction = (
                    prediction_from_case(
                        case
                    )
                )

                explanation = (
                    explainability.explain(
                        case[
                            "clinical_text"
                        ],
                        prediction,
                    )
                )

            twin.attach_explanation(
                case["case_id"],
                explanation,
            )

            rerun()

        except ValueError as exc:
            st.error(
                str(exc)
            )

        except RuntimeError as exc:
            st.error(
                str(exc)
            )

        except Exception as exc:
            st.error(
                "Explainability processing failed."
            )

            st.exception(
                exc
            )


# ============================================================
# EXPLAINED → AWAITING HUMAN REVIEW
# ============================================================

elif state == State.EXPLAINED:
    render_prediction(
        case
    )

    render_explanation(
        case
    )

    st.subheader(
        "4. Human review queue"
    )

    st.warning(
        "The recommendation cannot be automatically "
        "accepted. Human review is mandatory."
    )

    if st.button(
        "Send for human review",
        type="primary",
    ):
        try:
            twin.send_for_review(
                case["case_id"]
            )

            rerun()

        except ValueError as exc:
            st.error(
                str(exc)
            )

        except RuntimeError as exc:
            st.error(
                str(exc)
            )

        except Exception as exc:
            st.error(
                "Unable to send case for review."
            )

            st.exception(
                exc
            )


# ============================================================
# AWAITING HUMAN REVIEW
# ============================================================

elif (
    state
    == State.AWAITING_HUMAN_REVIEW
):
    render_prediction(
        case
    )

    render_explanation(
        case
    )

    st.header(
        "Mandatory human review"
    )

    st.warning(
        "Model confidence is descriptive uncertainty only. "
        "It must not trigger automatic acceptance."
    )

    with st.form(
        "human_review_form"
    ):
        reviewer_identity = (
            st.text_input(
                "Reviewer identity",
                placeholder=(
                    "e.g. demo-reviewer"
                ),
            )
        )

        decision = st.radio(
            "Decision",
            options=[
                "Accept",
                "Reject",
                "Amend",
            ],
            horizontal=True,
        )

        reason = st.text_area(
            "Reason for decision",
            height=120,
            placeholder=(
                "Record the reason for accepting, "
                "rejecting or amending the recommendation."
            ),
        )

        amended_category = None

        if decision == "Amend":
            recommendation = (
                case[
                    "prediction"
                ][
                    "recommendation"
                ]
            )

            categories = sorted(
                category
                for category
                in resources.label2id.keys()
                if (
                    category
                    != recommendation
                )
            )

            amended_category = (
                st.selectbox(
                    "Replacement ICD-10 category",
                    options=categories,
                )
            )

        submitted = (
            st.form_submit_button(
                "Record human decision",
                type="primary",
            )
        )

        # ====================================================
        # FIXED FORM VALIDATION
        # ====================================================

        if submitted:
            reviewer_identity_clean = (
                reviewer_identity
                or ""
            ).strip()

            reason_clean = (
                reason
                or ""
            ).strip()

            # ------------------------------------------------
            # Validate required fields in the UI FIRST.
            #
            # digital_twin.py retains the same checks as the
            # authoritative backend safeguard.
            # ------------------------------------------------

            if not reviewer_identity_clean:
                st.error(
                    "Reviewer identity is required "
                    "before a decision can be recorded."
                )

            elif not reason_clean:
                st.error(
                    "A reason for the review decision "
                    "is required."
                )

            elif (
                decision == "Amend"
                and not amended_category
            ):
                st.error(
                    "Select a replacement ICD-10 category "
                    "for an amendment."
                )

            else:
                try:
                    twin.review(
                        case["case_id"],

                        decision=(
                            decision.lower()
                        ),

                        reviewer_identity=(
                            reviewer_identity_clean
                        ),

                        reason=(
                            reason_clean
                        ),

                        amended_category=(
                            amended_category
                            if decision == "Amend"
                            else None
                        ),
                    )

                    rerun()

                # --------------------------------------------
                # Expected application validation failures
                # should appear as clean messages rather than
                # full Streamlit tracebacks.
                # --------------------------------------------

                except ValueError as exc:
                    st.error(
                        str(exc)
                    )

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )

                except Exception as exc:
                    st.error(
                        "Unexpected error while recording "
                        "the human-review decision."
                    )

                    st.exception(
                        exc
                    )


# ============================================================
# ACCEPTED / REJECTED / AMENDED
# ============================================================

elif state in {
    State.ACCEPTED,
    State.REJECTED,
    State.AMENDED,
}:
    render_prediction(
        case
    )

    render_explanation(
        case
    )

    render_review(
        case
    )

    st.success(
        f"Human review state: "
        f"{state.value}"
    )

    if st.button(
        "Complete case",
        type="primary",
    ):
        try:
            twin.complete(
                case["case_id"]
            )

            rerun()

        except ValueError as exc:
            st.error(
                str(exc)
            )

        except RuntimeError as exc:
            st.error(
                str(exc)
            )

        except Exception as exc:
            st.error(
                "Case completion failed."
            )

            st.exception(
                exc
            )


# ============================================================
# COMPLETED
# ============================================================

elif state == State.COMPLETED:
    st.success(
        "Operational coding workflow completed."
    )

    render_prediction(
        case
    )

    render_explanation(
        case
    )

    render_review(
        case
    )

    st.subheader(
        "Final disposition"
    )

    decision = (
        case[
            "review"
        ][
            "decision"
        ]
    )

    if decision == "reject":
        st.write(
            "**Final category:** "
            "No model recommendation accepted."
        )

    else:
        st.write(
            f"**Final category:** "
            f"{case['final_category']}"
        )

    st.write(
        "**Automatic acceptance:** Disabled"
    )

    st.write(
        "**Human review completed:** Yes"
    )

    # --------------------------------------------------------
    # Reveal replay reference only AFTER completion.
    # --------------------------------------------------------

    if (
        case[
            "source"
        ][
            "mode"
        ]
        == "frozen_validation_replay"
    ):
        validation_row = int(
            case[
                "source"
            ][
                "reference"
            ]
        )

        reference_row = (
            resources
            .replay_sample[
                resources
                .replay_sample[
                    "validation_row"
                ]
                .astype(
                    int
                )
                == validation_row
            ]
        )

        if len(
            reference_row
        ) == 1:
            reference_category = str(
                reference_row.iloc[
                    0
                ][
                    "true_category"
                ]
            )

            st.info(
                "Frozen replay reference category "
                "(revealed after workflow completion): "
                f"**{reference_category}**"
            )


# ============================================================
# ERROR
# ============================================================

elif state == State.ERROR:
    st.error(
        "This case entered the terminal Error state."
    )

    if case.get(
        "error"
    ):
        st.json(
            case["error"]
        )


# ============================================================
# AUDIT
# ============================================================

st.divider()

render_audit(
    case["case_id"]
)