from __future__ import annotations

import json
import math

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import torch

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from operational_coding_twin.config import (
    FROZEN_TEMPERATURE,
    get_settings,
)


# ============================================================
# FROZEN RESOURCE CONTAINER
# ============================================================

@dataclass
class FrozenResources:
    """
    Read-only scientific resources required by the
    operational coding twin.
    """

    tokenizer: Any
    model: Any

    label2id: dict[str, int]
    id2label: dict[int, str]

    temperature: float

    replay_sample: pd.DataFrame
    replay_probabilities: np.ndarray
    replay_explanations: pd.DataFrame

    claims: dict[str, Any]
    provenance: dict[str, Any]

    device: torch.device


# ============================================================
# JSON HELPERS
# ============================================================

def _load_json(
    path,
) -> dict[str, Any]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        return json.load(
            handle
        )


def _find_key_recursive(
    data: Any,
    target_key: str,
) -> Any:
    """
    Search a nested JSON-compatible object for a key.

    This lets us validate frozen governance fields without
    assuming that every historical JSON file uses exactly
    the same nesting layout.
    """

    if isinstance(
        data,
        dict,
    ):

        if target_key in data:
            return data[
                target_key
            ]

        for value in data.values():

            result = _find_key_recursive(
                value,
                target_key,
            )

            if result is not None:
                return result

    elif isinstance(
        data,
        list,
    ):

        for value in data:

            result = _find_key_recursive(
                value,
                target_key,
            )

            if result is not None:
                return result

    return None


# ============================================================
# TEST-PARTITION GUARD
# ============================================================

def _assert_no_test_dependencies(
    paths,
) -> None:
    """
    Fail closed if any application resource points at
    Phase 9/test-prediction artefacts.
    """

    forbidden_terms = (
        "phase9",
        "test_predictions",
        "transformer_test",
        "baseline_test",
        "test_logits",
        "test_probabilities",
    )

    for path in paths:

        lowered = str(
            path
        ).lower()

        for term in forbidden_terms:

            if term in lowered:

                raise RuntimeError(
                    "Prohibited sealed-test dependency "
                    f"detected:\n{path}"
                )


# ============================================================
# LABEL MAPPING
# ============================================================

def _load_label_mapping(
    path,
) -> tuple[
    dict[str, int],
    dict[int, str],
]:

    mapping = _load_json(
        path
    )

    if (
        "label2id"
        not in mapping
        or
        "id2label"
        not in mapping
    ):
        raise RuntimeError(
            "label_mapping.json must contain "
            "'label2id' and 'id2label'."
        )

    label2id = {
        str(label):
            int(class_id)

        for label, class_id
        in mapping[
            "label2id"
        ].items()
    }

    id2label = {
        int(class_id):
            str(label)

        for class_id, label
        in mapping[
            "id2label"
        ].items()
    }

    if len(
        label2id
    ) != 50:

        raise RuntimeError(
            "Frozen label space must contain "
            "exactly 50 ICD-10 categories."
        )

    if len(
        id2label
    ) != 50:

        raise RuntimeError(
            "Frozen reverse label mapping must "
            "contain exactly 50 categories."
        )

    # --------------------------------------------------------
    # Verify bidirectional consistency
    # --------------------------------------------------------

    for label, class_id in (
        label2id.items()
    ):

        if (
            id2label.get(
                class_id
            )
            != label
        ):
            raise RuntimeError(
                "label2id and id2label are "
                f"inconsistent for {label}."
            )

    expected_ids = set(
        range(
            50
        )
    )

    if (
        set(
            id2label.keys()
        )
        != expected_ids
    ):
        raise RuntimeError(
            "Frozen class IDs must be exactly 0–49."
        )

    return (
        label2id,
        id2label,
    )


# ============================================================
# CALIBRATION
# ============================================================

def _load_temperature(
    path,
) -> float:

    calibration = _load_json(
        path
    )

    if (
        "temperature"
        not in calibration
    ):
        raise RuntimeError(
            "temperature_scaling.json does not "
            "contain 'temperature'."
        )

    temperature = float(
        calibration[
            "temperature"
        ]
    )

    # Actual frozen Phase 8B value:
    #
    # 0.18388931380527324
    #
    # config.py contains the concise frozen value:
    #
    # 0.1838893138

    if not math.isclose(
        temperature,
        FROZEN_TEMPERATURE,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise RuntimeError(
            "Frozen calibration temperature mismatch.\n"
            f"Expected approximately: "
            f"{FROZEN_TEMPERATURE}\n"
            f"Observed: {temperature}"
        )

    # --------------------------------------------------------
    # Governance validation
    # --------------------------------------------------------

    if (
        calibration.get(
            "fit_partition"
        )
        != "validation"
    ):
        raise RuntimeError(
            "Calibration must have been fitted "
            "on the validation partition."
        )

    if (
        calibration.get(
            "test_partition_evaluated"
        )
        is not False
    ):
        raise RuntimeError(
            "Phase 8B calibration artefact must "
            "record test_partition_evaluated=false."
        )

    if (
        calibration.get(
            "prediction_classes_changed"
        )
        != 0
    ):
        raise RuntimeError(
            "Unexpected change in predicted classes "
            "during temperature scaling."
        )

    return temperature


# ============================================================
# REPLAY EVIDENCE
# ============================================================

def _load_replay_sample(
    path,
) -> pd.DataFrame:

    sample = pd.read_csv(
        path
    )

    if len(
        sample
    ) != 100:

        raise RuntimeError(
            "Frozen deterministic replay sample "
            "must contain exactly 100 cases."
        )

    required_columns = {
        "validation_row",
        "encounter_id",
        "true_class_id",
        "sample_hash",
        "sample_rank",
        "true_category",
    }

    missing = (
        required_columns
        -
        set(
            sample.columns
        )
    )

    if missing:

        raise RuntimeError(
            "Replay sample is missing columns: "
            f"{sorted(missing)}"
        )

    if (
        sample[
            "validation_row"
        ]
        .duplicated()
        .any()
    ):

        raise RuntimeError(
            "Replay sample contains duplicate "
            "validation rows."
        )

    if (
        sample[
            "sample_rank"
        ]
        .duplicated()
        .any()
    ):

        raise RuntimeError(
            "Replay sample contains duplicate "
            "sample ranks."
        )

    return sample


def _load_replay_probabilities(
    path,
) -> np.ndarray:

    probabilities = np.load(
        path,
        allow_pickle=False,
    )

    if (
        probabilities.shape
        != (375, 50)
    ):

        raise RuntimeError(
            "Frozen validation probability matrix "
            "must have shape (375, 50). "
            f"Observed: {probabilities.shape}"
        )

    if not np.isfinite(
        probabilities
    ).all():

        raise RuntimeError(
            "Frozen validation probabilities "
            "contain non-finite values."
        )

    if (
        probabilities.min()
        < -1e-12
    ):

        raise RuntimeError(
            "Frozen probability matrix contains "
            "negative values."
        )

    if (
        probabilities.max()
        > 1.0 + 1e-12
    ):

        raise RuntimeError(
            "Frozen probability matrix contains "
            "values greater than 1."
        )

    row_sums = (
        probabilities.sum(
            axis=1
        )
    )

    if not np.allclose(
        row_sums,
        1.0,
        atol=1e-8,
    ):

        raise RuntimeError(
            "Frozen validation probability rows "
            "do not sum to one."
        )

    return probabilities


def _load_replay_explanations(
    path,
    replay_sample: pd.DataFrame,
) -> pd.DataFrame:

    explanations = pd.read_csv(
        path
    )

    if len(
        explanations
    ) != 100:

        raise RuntimeError(
            "Frozen LIG case table must contain "
            "exactly 100 cases."
        )

    required_columns = {
        "validation_row",
        "predicted_category",
        "top_support_tokens",
        "lig_steps",
    }

    missing = (
        required_columns
        -
        set(
            explanations.columns
        )
    )

    if missing:

        raise RuntimeError(
            "LIG replay table is missing columns: "
            f"{sorted(missing)}"
        )

    if not (
        explanations[
            "lig_steps"
        ]
        .eq(
            50
        )
        .all()
    ):

        raise RuntimeError(
            "Frozen LIG explanations must use "
            "exactly 50 integration steps."
        )

    # --------------------------------------------------------
    # Verify same validation population
    # --------------------------------------------------------

    sample_rows = set(
        replay_sample[
            "validation_row"
        ].astype(
            int
        )
    )

    explanation_rows = set(
        explanations[
            "validation_row"
        ].astype(
            int
        )
    )

    if (
        sample_rows
        != explanation_rows
    ):

        raise RuntimeError(
            "Replay sample and LIG explanation "
            "validation rows do not match."
        )

    # --------------------------------------------------------
    # Confirm support-token JSON is readable
    # --------------------------------------------------------

    for row_number, value in enumerate(
        explanations[
            "top_support_tokens"
        ],
        start=1,
    ):

        try:

            parsed = json.loads(
                value
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ) as exc:

            raise RuntimeError(
                "Invalid top_support_tokens JSON "
                f"at LIG row {row_number}."
            ) from exc

        if not isinstance(
            parsed,
            list,
        ):

            raise RuntimeError(
                "top_support_tokens must contain "
                "a JSON list."
            )

    return explanations


# ============================================================
# GOVERNANCE CLAIMS
# ============================================================

def _load_claims(
    path,
) -> dict[str, Any]:

    claims = _load_json(
        path
    )

    automatic_acceptance = (
        _find_key_recursive(
            claims,
            "automatic_acceptance",
        )
    )

    human_review_required = (
        _find_key_recursive(
            claims,
            "human_review_required",
        )
    )

    if (
        automatic_acceptance
        is not False
    ):

        raise RuntimeError(
            "Frozen Phase 10 claims must prohibit "
            "automatic acceptance."
        )

    if (
        human_review_required
        is not True
    ):

        raise RuntimeError(
            "Frozen Phase 10 claims must require "
            "human review."
        )

    return claims


# ============================================================
# LOAD MODEL + TOKENIZER
# ============================================================

def _load_model_and_tokenizer(
    model_dir,
    id2label: dict[int, str],
    label2id: dict[str, int],
):
    """
    Load the exact locally persisted Phase 7 seed-42 model.

    No internet model download is permitted here.
    """

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            str(
                model_dir
            ),
            local_files_only=True,
            use_fast=True,
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            str(
                model_dir
            ),
            local_files_only=True,
        )
    )

    # --------------------------------------------------------
    # Verify architecture
    # --------------------------------------------------------

    if (
        model.__class__.__name__
        != "BertForSequenceClassification"
    ):

        raise RuntimeError(
            "Unexpected model architecture: "
            f"{model.__class__.__name__}"
        )

    if (
        int(
            model.config.num_labels
        )
        != 50
    ):

        raise RuntimeError(
            "Loaded BioClinicalBERT model must "
            "have exactly 50 outputs."
        )

    # Ensure runtime interpretation uses our frozen mapping.

    model.config.id2label = (
        id2label.copy()
    )

    model.config.label2id = (
        label2id.copy()
    )

    model.eval()

    # --------------------------------------------------------
    # No optimisation/training is performed here.
    # --------------------------------------------------------

    return (
        tokenizer,
        model,
    )


# ============================================================
# PUBLIC LOADER
# ============================================================

def load_frozen_resources() -> FrozenResources:
    """
    Load and validate all read-only frozen artefacts required
    by the operational coding twin.

    This function:
        - does NOT train
        - does NOT recalibrate
        - does NOT choose thresholds
        - does NOT perform model selection
        - does NOT access Phase 9 test artefacts
    """

    settings = get_settings()

    required_paths = (
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
    )

    # --------------------------------------------------------
    # Confirm everything exists
    # --------------------------------------------------------

    for path in required_paths:

        if not path.is_file():

            raise FileNotFoundError(
                "Required frozen artefact missing:\n"
                f"{path}"
            )

    # --------------------------------------------------------
    # Explicit sealed-test guard
    # --------------------------------------------------------

    _assert_no_test_dependencies(
        required_paths
    )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    (
        label2id,
        id2label,
    ) = _load_label_mapping(
        settings.label_mapping_file
    )

    # --------------------------------------------------------
    # Calibration
    # --------------------------------------------------------

    temperature = (
        _load_temperature(
            settings.temperature_file
        )
    )

    # --------------------------------------------------------
    # Replay evidence
    # --------------------------------------------------------

    replay_sample = (
        _load_replay_sample(
            settings.replay_sample_file
        )
    )

    replay_probabilities = (
        _load_replay_probabilities(
            settings.replay_probabilities_file
        )
    )

    replay_explanations = (
        _load_replay_explanations(
            settings.replay_explanations_file,
            replay_sample,
        )
    )

    # --------------------------------------------------------
    # Frozen claims
    # --------------------------------------------------------

    claims = (
        _load_claims(
            settings.claims_file
        )
    )

    # --------------------------------------------------------
    # Provenance
    # --------------------------------------------------------

    provenance = (
        _load_json(
            settings.hash_manifest_file
        )
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    # --------------------------------------------------------
    # Frozen Phase 7 model
    # --------------------------------------------------------

    tokenizer, model = (
        _load_model_and_tokenizer(
            settings.model_dir,
            id2label,
            label2id,
        )
    )

    model.to(
        device
    )

    model.eval()

    # --------------------------------------------------------
    # Return read-only resource collection
    # --------------------------------------------------------

    return FrozenResources(
        tokenizer=tokenizer,
        model=model,

        label2id=label2id,
        id2label=id2label,

        temperature=temperature,

        replay_sample=replay_sample,
        replay_probabilities=replay_probabilities,
        replay_explanations=replay_explanations,

        claims=claims,
        provenance=provenance,

        device=device,
    )