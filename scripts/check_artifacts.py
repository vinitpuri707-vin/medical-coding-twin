from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from operational_coding_twin.config import get_settings


# ============================================================
# HELPERS
# ============================================================

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def print_header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def load_json(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    settings = get_settings()

    print_header(
        "STEP 9 — FROZEN ARTEFACT INVENTORY"
    )

    print(
        f"Project root : {settings.project_root}"
    )

    print(
        f"Artefact root: {settings.artifacts_dir}"
    )

    # --------------------------------------------------------
    # REQUIRED FILES
    # --------------------------------------------------------

    required_files = {
        "model.safetensors":
            settings.model_file,

        "config.json":
            settings.config_file,

        "tokenizer.json":
            settings.tokenizer_file,

        "tokenizer_config.json":
            settings.tokenizer_config_file,

        "label_mapping.json":
            settings.label_mapping_file,

        "temperature_scaling.json":
            settings.temperature_file,

        "deterministic_validation_sample_100.csv":
            settings.replay_sample_file,

        "validation_calibrated_probabilities.npy":
            settings.replay_probabilities_file,

        "layer_integrated_gradients_cases.csv":
            settings.replay_explanations_file,

        "final_claims_freeze.json":
            settings.claims_file,

        "source_artifact_hashes.json":
            settings.hash_manifest_file,
    }

    missing = []

    print_header(
        "1. FILE PRESENCE"
    )

    for name, path in required_files.items():
        if path.is_file():
            print(
                f"PASS  {name:<48} "
                f"{size_mb(path):>9.2f} MB"
            )
        else:
            print(
                f"MISS  {name:<48} "
                f"{path}"
            )

            missing.append(
                path
            )

    if missing:
        print()
        print(
            "STEP 9 STATUS: FAIL"
        )

        print(
            "Copy the missing frozen artefacts "
            "before continuing."
        )

        return 1

    # --------------------------------------------------------
    # SHA-256
    # --------------------------------------------------------

    print_header(
        "2. SHA-256 INVENTORY"
    )

    for name, path in required_files.items():
        digest = sha256_file(
            path
        )

        print(
            f"{name:<48} {digest}"
        )

    # --------------------------------------------------------
    # LABEL MAPPING
    # --------------------------------------------------------

    print_header(
        "3. LABEL MAPPING"
    )

    mapping = load_json(
        settings.label_mapping_file
    )

    print(
        "Top-level keys:",
        list(
            mapping.keys()
        ),
    )

    if (
        "label2id" not in mapping
        or "id2label" not in mapping
    ):
        print(
            "FAIL: label_mapping.json must "
            "contain label2id and id2label."
        )

        return 1

    label2id = mapping[
        "label2id"
    ]

    id2label = mapping[
        "id2label"
    ]

    print(
        "label2id count:",
        len(
            label2id
        ),
    )

    print(
        "id2label count:",
        len(
            id2label
        ),
    )

    if (
        len(label2id) != 50
        or len(id2label) != 50
    ):
        print(
            "FAIL: expected exactly "
            "50 frozen categories."
        )

        return 1

    print(
        "First 5 mappings:"
    )

    for label, class_id in list(
        label2id.items()
    )[:5]:
        print(
            f"  {label} -> {class_id}"
        )

    print(
        "LABEL MAPPING: PASS"
    )

    # --------------------------------------------------------
    # MODEL CONFIG
    # --------------------------------------------------------

    print_header(
        "4. MODEL CONFIG"
    )

    model_config = load_json(
        settings.config_file
    )

    print(
        "architectures:",
        model_config.get(
            "architectures"
        ),
    )

    print(
        "num_labels:",
        model_config.get(
            "num_labels"
        ),
    )

    print(
        "model_type:",
        model_config.get(
            "model_type"
        ),
    )

    num_labels = model_config.get(
        "num_labels"
    )

    # Some Hugging Face configs may infer this from id2label.
    if (
        num_labels is not None
        and int(num_labels) != 50
    ):
        print(
            "FAIL: model configuration does "
            "not describe 50 labels."
        )

        return 1

    print(
        "MODEL CONFIG: PASS"
    )

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    print_header(
        "5. CALIBRATION FILE"
    )

    temperature_json = load_json(
        settings.temperature_file
    )

    print(
        json.dumps(
            temperature_json,
            indent=2,
        )[:3000]
    )

    print()
    print(
        "Expected frozen temperature:",
        0.1838893138,
    )

    # We deliberately inspect the actual JSON now rather
    # than assuming its exact nesting structure.
    print(
        "CALIBRATION FILE: READABLE"
    )

    # --------------------------------------------------------
    # REPLAY SAMPLE
    # --------------------------------------------------------

    print_header(
        "6. FROZEN VALIDATION REPLAY SAMPLE"
    )

    replay_sample = pd.read_csv(
        settings.replay_sample_file
    )

    print(
        "Shape:",
        replay_sample.shape,
    )

    print(
        "Columns:",
        list(
            replay_sample.columns
        ),
    )

    print(
        replay_sample.head(
            3
        ).to_string(
            index=False
        )
    )

    if len(
        replay_sample
    ) != 100:
        print(
            "FAIL: deterministic validation "
            "sample should contain 100 rows."
        )

        return 1

    if (
        "validation_row"
        not in replay_sample.columns
    ):
        print(
            "FAIL: validation_row column missing."
        )

        return 1

    print(
        "REPLAY SAMPLE: PASS"
    )

    # --------------------------------------------------------
    # CALIBRATED VALIDATION PROBABILITIES
    # --------------------------------------------------------

    print_header(
        "7. CALIBRATED VALIDATION PROBABILITIES"
    )

    probabilities = np.load(
        settings.replay_probabilities_file,
        allow_pickle=False,
    )

    print(
        "Shape:",
        probabilities.shape,
    )

    print(
        "dtype:",
        probabilities.dtype,
    )

    print(
        "Finite:",
        bool(
            np.isfinite(
                probabilities
            ).all()
        ),
    )

    row_sums = probabilities.sum(
        axis=1
    )

    print(
        "Row-sum min:",
        float(
            row_sums.min()
        ),
    )

    print(
        "Row-sum max:",
        float(
            row_sums.max()
        ),
    )

    if (
        probabilities.shape
        != (375, 50)
    ):
        print(
            "FAIL: expected probability "
            "matrix shape (375, 50)."
        )

        return 1

    if not np.isfinite(
        probabilities
    ).all():
        print(
            "FAIL: probability matrix "
            "contains non-finite values."
        )

        return 1

    if not np.allclose(
        row_sums,
        1.0,
        atol=1e-8,
    ):
        print(
            "FAIL: calibrated probability "
            "rows do not sum to 1."
        )

        return 1

    print(
        "CALIBRATED PROBABILITIES: PASS"
    )

    # --------------------------------------------------------
    # SAVED LIG EXPLANATIONS
    # --------------------------------------------------------

    print_header(
        "8. SAVED LIG EXPLANATIONS"
    )

    lig_cases = pd.read_csv(
        settings.replay_explanations_file
    )

    print(
        "Shape:",
        lig_cases.shape,
    )

    print(
        "Columns:",
        list(
            lig_cases.columns
        ),
    )

    if len(
        lig_cases
    ) != 100:
        print(
            "FAIL: expected 100 saved "
            "LIG cases."
        )

        return 1

    if (
        "validation_row"
        not in lig_cases.columns
    ):
        print(
            "FAIL: validation_row missing "
            "from LIG cases."
        )

        return 1

    if (
        "lig_steps"
        in lig_cases.columns
    ):
        unique_steps = sorted(
            lig_cases[
                "lig_steps"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        print(
            "LIG steps:",
            unique_steps,
        )

        if unique_steps != [50]:
            print(
                "FAIL: frozen LIG should "
                "use 50 steps."
            )

            return 1

    if (
        "top_support_tokens"
        not in lig_cases.columns
    ):
        print(
            "FAIL: top_support_tokens "
            "column missing."
        )

        return 1

    print(
        "LIG REPLAY DATA: PASS"
    )

    # --------------------------------------------------------
    # FINAL CLAIMS
    # --------------------------------------------------------

    print_header(
        "9. FINAL CLAIMS FREEZE"
    )

    claims = load_json(
        settings.claims_file
    )

    print(
        "Top-level keys:",
        list(
            claims.keys()
        ),
    )

    operational = claims.get(
        "operational_interpretation"
    )

    if operational is not None:
        print(
            "operational_interpretation:"
        )

        print(
            json.dumps(
                operational,
                indent=2,
            )
        )
    else:
        print(
            "NOTE: operational_interpretation "
            "is not a top-level object."
        )

        print(
            "We will inspect the actual "
            "structure before writing "
            "the resource loader."
        )

    # --------------------------------------------------------
    # PHASE 8 PROVENANCE
    # --------------------------------------------------------

    print_header(
        "10. SOURCE ARTEFACT HASH RECORD"
    )

    provenance = load_json(
        settings.hash_manifest_file
    )

    print(
        "Top-level keys:",
        list(
            provenance.keys()
        ),
    )

    print(
        json.dumps(
            provenance,
            indent=2,
        )[:4000]
    )

    print()
    print(
        "NOTE: This script does NOT rewrite "
        "the original provenance file."
    )

    print(
        "It is being inspected read-only."
    )

    # --------------------------------------------------------
    # TEST PARTITION GUARD
    # --------------------------------------------------------

    print_header(
        "11. TEST-PARTITION DEPENDENCY CHECK"
    )

    forbidden_terms = (
        "phase9",
        "test_predictions",
        "transformer_test",
        "baseline_test",
    )

    bad_paths = []

    for path in required_files.values():
        lowered = str(
            path
        ).lower()

        if any(
            term in lowered
            for term in forbidden_terms
        ):
            bad_paths.append(
                path
            )

    if bad_paths:
        print(
            "FAIL: application artefact set "
            "contains test-partition dependency:"
        )

        for path in bad_paths:
            print(
                path
            )

        return 1

    print(
        "SEALED TEST PARTITION DEPENDENCY: NONE"
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print_header(
        "STEP 9 RESULT"
    )

    print(
        "FILE PRESENCE                 PASS"
    )

    print(
        "LABEL SPACE                   PASS"
    )

    print(
        "MODEL CONFIG                  PASS"
    )

    print(
        "CALIBRATION FILE              READABLE"
    )

    print(
        "VALIDATION REPLAY SAMPLE      PASS"
    )

    print(
        "CALIBRATED PROBABILITIES      PASS"
    )

    print(
        "SAVED LIG EXPLANATIONS        PASS"
    )

    print(
        "FINAL CLAIMS                  READABLE"
    )

    print(
        "PROVENANCE RECORD             READABLE"
    )

    print(
        "TEST PARTITION DEPENDENCY     NONE"
    )

    print()
    print(
        "STEP 9: PASS"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )