from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from operational_coding_twin.config import (
    FROZEN_TEMPERATURE,
    get_settings,
)

from operational_coding_twin.frozen_resources import (
    load_frozen_resources,
)


# ============================================================
# BASIC FILE PRESENCE
# ============================================================

def test_all_required_frozen_files_exist():
    settings = get_settings()

    required = [
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
    ]

    missing = [
        path
        for path in required
        if not path.is_file()
    ]

    assert not missing, (
        "Missing frozen artefacts:\n"
        + "\n".join(
            str(path)
            for path in missing
        )
    )


def test_model_weights_are_not_empty():
    settings = get_settings()

    assert (
        settings.model_file.stat().st_size
        > 100_000_000
    )


def test_probability_file_is_not_empty():
    settings = get_settings()

    assert (
        settings
        .replay_probabilities_file
        .stat()
        .st_size
        > 0
    )


# ============================================================
# LABEL MAPPING
# ============================================================

def test_label_mapping_contains_50_categories():
    settings = get_settings()

    mapping = json.loads(
        settings
        .label_mapping_file
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        "label2id"
        in mapping
    )

    assert (
        "id2label"
        in mapping
    )

    assert len(
        mapping["label2id"]
    ) == 50

    assert len(
        mapping["id2label"]
    ) == 50


def test_label_mapping_class_ids_are_zero_to_49():
    settings = get_settings()

    mapping = json.loads(
        settings
        .label_mapping_file
        .read_text(
            encoding="utf-8"
        )
    )

    ids = {
        int(value)
        for value
        in mapping[
            "label2id"
        ].values()
    }

    assert ids == set(
        range(50)
    )


def test_label_mapping_is_bidirectionally_consistent():
    settings = get_settings()

    mapping = json.loads(
        settings
        .label_mapping_file
        .read_text(
            encoding="utf-8"
        )
    )

    label2id = {
        str(label): int(index)
        for label, index
        in mapping[
            "label2id"
        ].items()
    }

    id2label = {
        int(index): str(label)
        for index, label
        in mapping[
            "id2label"
        ].items()
    }

    for label, index in (
        label2id.items()
    ):
        assert (
            id2label[index]
            == label
        )


# ============================================================
# MODEL CONFIG
# ============================================================

def test_model_config_is_bert_sequence_classifier():
    settings = get_settings()

    config = json.loads(
        settings
        .config_file
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        config.get(
            "model_type"
        )
        == "bert"
    )

    architectures = (
        config.get(
            "architectures"
        )
        or []
    )

    assert (
        "BertForSequenceClassification"
        in architectures
    )


# ============================================================
# CALIBRATION
# ============================================================

def test_temperature_matches_frozen_phase8b_value():
    settings = get_settings()

    calibration = json.loads(
        settings
        .temperature_file
        .read_text(
            encoding="utf-8"
        )
    )

    observed = float(
        calibration[
            "temperature"
        ]
    )

    assert math.isclose(
        observed,
        FROZEN_TEMPERATURE,
        rel_tol=0.0,
        abs_tol=1e-10,
    )


def test_calibration_was_validation_only():
    settings = get_settings()

    calibration = json.loads(
        settings
        .temperature_file
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        calibration[
            "fit_partition"
        ]
        == "validation"
    )

    assert (
        calibration[
            "fit_examples"
        ]
        == 375
    )

    assert (
        calibration[
            "test_partition_evaluated"
        ]
        is False
    )


def test_temperature_scaling_did_not_change_classes():
    settings = get_settings()

    calibration = json.loads(
        settings
        .temperature_file
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        calibration[
            "prediction_classes_changed"
        ]
        == 0
    )


# ============================================================
# DETERMINISTIC VALIDATION SAMPLE
# ============================================================

def test_replay_sample_contains_exactly_100_rows():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    assert sample.shape[
        0
    ] == 100


def test_replay_sample_required_columns_exist():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    required = {
        "validation_row",
        "encounter_id",
        "true_class_id",
        "sample_hash",
        "sample_rank",
        "true_category",
    }

    assert required.issubset(
        sample.columns
    )


def test_replay_sample_has_unique_validation_rows():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    assert not (
        sample[
            "validation_row"
        ]
        .duplicated()
        .any()
    )


def test_replay_sample_has_unique_sample_ranks():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    assert not (
        sample[
            "sample_rank"
        ]
        .duplicated()
        .any()
    )


def test_replay_rows_are_inside_validation_range():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    rows = (
        sample[
            "validation_row"
        ]
        .astype(
            int
        )
    )

    assert (
        rows.min()
        >= 0
    )

    assert (
        rows.max()
        < 375
    )


def test_replay_true_class_ids_are_inside_label_space():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    ids = (
        sample[
            "true_class_id"
        ]
        .astype(
            int
        )
    )

    assert (
        ids.min()
        >= 0
    )

    assert (
        ids.max()
        < 50
    )


# ============================================================
# CALIBRATED VALIDATION PROBABILITIES
# ============================================================

def test_calibrated_probability_shape():
    settings = get_settings()

    probabilities = np.load(
        settings.replay_probabilities_file,
        allow_pickle=False,
    )

    assert (
        probabilities.shape
        == (375, 50)
    )


def test_calibrated_probabilities_are_finite():
    settings = get_settings()

    probabilities = np.load(
        settings.replay_probabilities_file,
        allow_pickle=False,
    )

    assert (
        np.isfinite(
            probabilities
        )
        .all()
    )


def test_calibrated_probabilities_are_valid_range():
    settings = get_settings()

    probabilities = np.load(
        settings.replay_probabilities_file,
        allow_pickle=False,
    )

    assert (
        probabilities.min()
        >= -1e-12
    )

    assert (
        probabilities.max()
        <= 1.0 + 1e-12
    )


def test_calibrated_probability_rows_sum_to_one():
    settings = get_settings()

    probabilities = np.load(
        settings.replay_probabilities_file,
        allow_pickle=False,
    )

    row_sums = (
        probabilities.sum(
            axis=1
        )
    )

    assert np.allclose(
        row_sums,
        1.0,
        atol=1e-8,
    )


# ============================================================
# LIG REPLAY ARTEFACT
# ============================================================

def test_lig_cases_contains_exactly_100_rows():
    settings = get_settings()

    lig = pd.read_csv(
        settings.replay_explanations_file
    )

    assert lig.shape[
        0
    ] == 100


def test_lig_required_columns_exist():
    settings = get_settings()

    lig = pd.read_csv(
        settings.replay_explanations_file
    )

    required = {
        "validation_row",
        "predicted_category",
        "top_support_tokens",
        "lig_steps",
    }

    assert required.issubset(
        lig.columns
    )


def test_lig_uses_exactly_50_steps():
    settings = get_settings()

    lig = pd.read_csv(
        settings.replay_explanations_file
    )

    unique_steps = set(
        lig[
            "lig_steps"
        ]
        .astype(
            int
        )
    )

    assert unique_steps == {
        50
    }


def test_lig_and_replay_sample_cover_same_validation_rows():
    settings = get_settings()

    sample = pd.read_csv(
        settings.replay_sample_file
    )

    lig = pd.read_csv(
        settings.replay_explanations_file
    )

    sample_rows = set(
        sample[
            "validation_row"
        ]
        .astype(
            int
        )
    )

    lig_rows = set(
        lig[
            "validation_row"
        ]
        .astype(
            int
        )
    )

    assert (
        sample_rows
        == lig_rows
    )


def test_lig_top_support_tokens_are_valid_json_lists():
    settings = get_settings()

    lig = pd.read_csv(
        settings.replay_explanations_file
    )

    for value in (
        lig[
            "top_support_tokens"
        ]
    ):
        parsed = json.loads(
            value
        )

        assert isinstance(
            parsed,
            list,
        )


# ============================================================
# GOVERNANCE CLAIMS
# ============================================================

def _find_key_recursive(
    data,
    key,
):
    if isinstance(
        data,
        dict,
    ):
        if key in data:
            return data[
                key
            ]

        for value in (
            data.values()
        ):
            found = (
                _find_key_recursive(
                    value,
                    key,
                )
            )

            if found is not None:
                return found

    elif isinstance(
        data,
        list,
    ):
        for value in data:
            found = (
                _find_key_recursive(
                    value,
                    key,
                )
            )

            if found is not None:
                return found

    return None


def test_claims_prohibit_automatic_acceptance():
    settings = get_settings()

    claims = json.loads(
        settings
        .claims_file
        .read_text(
            encoding="utf-8"
        )
    )

    value = (
        _find_key_recursive(
            claims,
            "automatic_acceptance",
        )
    )

    assert value is False


def test_claims_require_human_review():
    settings = get_settings()

    claims = json.loads(
        settings
        .claims_file
        .read_text(
            encoding="utf-8"
        )
    )

    value = (
        _find_key_recursive(
            claims,
            "human_review_required",
        )
    )

    assert value is True


# ============================================================
# PROVENANCE
# ============================================================

def test_provenance_file_is_readable_json():
    settings = get_settings()

    provenance = json.loads(
        settings
        .hash_manifest_file
        .read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        provenance,
        dict,
    )

    assert len(
        provenance
    ) > 0


# ============================================================
# SEALED TEST-PARTITION GUARD
# ============================================================

def test_application_paths_do_not_reference_phase9():
    settings = get_settings()

    paths = [
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
    ]

    forbidden = (
        "phase9",
        "test_predictions",
        "transformer_test",
        "baseline_test",
        "test_logits",
        "test_probabilities",
    )

    for path in paths:
        text = str(
            path
        ).lower()

        assert not any(
            term in text
            for term in forbidden
        ), (
            "Prohibited test dependency: "
            f"{path}"
        )


# ============================================================
# FULL FROZEN RESOURCE LOADER
# ============================================================

@pytest.fixture(
    scope="module"
)
def resources():
    """
    Load the 413 MB frozen model once for this module.
    """

    return load_frozen_resources()


def test_frozen_resource_loader_returns_50_labels(
    resources,
):
    assert len(
        resources.label2id
    ) == 50

    assert len(
        resources.id2label
    ) == 50


def test_frozen_resource_loader_temperature(
    resources,
):
    assert (
        resources.temperature
        == pytest.approx(
            0.18388931380527324,
            abs=1e-10,
        )
    )


def test_frozen_resource_loader_replay_shapes(
    resources,
):
    assert (
        resources.replay_sample.shape[
            0
        ]
        == 100
    )

    assert (
        resources
        .replay_probabilities
        .shape
        == (375, 50)
    )

    assert (
        resources
        .replay_explanations
        .shape[
            0
        ]
        == 100
    )


def test_frozen_model_is_eval_mode(
    resources,
):
    assert (
        resources.model.training
        is False
    )


def test_frozen_model_has_50_output_labels(
    resources,
):
    assert (
        int(
            resources
            .model
            .config
            .num_labels
        )
        == 50
    )