from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


REQUIRED = [
    "xai/deterministic_validation_sample_100.csv",
    "xai/layer_integrated_gradients_cases.csv",
    "xai/layer_integrated_gradients_tokens.csv",
    "faithfulness/faithfulness_case_summary.csv",
    "faithfulness/faithfulness_summary.json",
    "faithfulness/faithfulness_summary_table.csv",
    "faithfulness/random_mask_results_20_per_case.csv",
    "provenance/phase8b_configuration.json",
    "SHA256SUMS.txt",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_sha_manifest(path: Path) -> dict[str, str]:
    values = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line:
            continue

        digest, relative = line.split(None, 1)
        values[relative.strip()] = digest.strip()

    return values


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--phase8b-dir",
        required=True,
        help="Path to frozen P8B-CORRECTIVE-V201-SEED42 directory.",
    )

    parser.add_argument(
        "--output",
        default="rq4_existing_evidence_closure.json",
    )

    args = parser.parse_args()

    root = Path(args.phase8b_dir).resolve()

    # --------------------------------------------------------
    # Hard safety boundary
    # --------------------------------------------------------

    if "P8B-CORRECTIVE-V201-SEED42" not in str(root):
        raise RuntimeError(
            "Refusing to run outside the frozen Phase 8B directory."
        )

    for relative in REQUIRED:
        path = root / relative

        if not path.is_file():
            raise FileNotFoundError(path)

    # --------------------------------------------------------
    # Verify frozen SHA-256 provenance
    # --------------------------------------------------------

    manifest = read_sha_manifest(root / "SHA256SUMS.txt")

    verified = {}

    for relative in REQUIRED:
        if relative == "SHA256SUMS.txt":
            continue

        expected = manifest.get(relative)

        if expected is None:
            raise RuntimeError(
                f"{relative} missing from SHA256SUMS.txt"
            )

        actual = sha256(root / relative)

        if actual != expected:
            raise RuntimeError(
                f"SHA-256 mismatch: {relative}"
            )

        verified[relative] = actual

    # --------------------------------------------------------
    # Read SAVED outputs only.
    #
    # No torch.
    # No transformers.
    # No Captum.
    # No model checkpoint.
    # No test data.
    # --------------------------------------------------------

    cases = pd.read_csv(
        root / "xai/layer_integrated_gradients_cases.csv"
    )

    tokens = pd.read_csv(
        root / "xai/layer_integrated_gradients_tokens.csv"
    )

    faith_cases = pd.read_csv(
        root / "faithfulness/faithfulness_case_summary.csv"
    )

    faith_summary = json.loads(
        (
            root
            / "faithfulness/faithfulness_summary.json"
        ).read_text(encoding="utf-8")
    )

    config = json.loads(
        (
            root
            / "provenance/phase8b_configuration.json"
        ).read_text(encoding="utf-8")
    )

    # --------------------------------------------------------
    # Determine whether any separate stability artefact exists.
    # This is discovery only; nothing is generated.
    # --------------------------------------------------------

    stability_files = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and "stability" in p.name.lower()
    ]

    result = {
        "closure_id": "G06-RQ4-EXISTING-EVIDENCE-ONLY",

        "source_run": "P8B-CORRECTIVE-V201-SEED42",

        "new_model_inference": False,
        "new_attribution_generation": False,
        "test_partition_accessed": False,

        "attribution": {
            "method": config["xai"]["method"],
            "target": config["xai"]["target"],
            "integration_steps": config["xai"]["integration_steps"],
            "partition": config["xai"]["sample_partition"],
            "sample_n": config["xai"]["sample_n"],
            "sample_seed": config["xai"]["sample_seed"],
            "saved_case_rows": int(len(cases)),
            "saved_token_rows": int(len(tokens)),
            "relevance_status": (
                "SAVED QUALITATIVE/MODEL-RELEVANCE EVIDENCE"
            ),
            "relevance_sources": [
                "layer_integrated_gradients_cases.csv::top_support_tokens",
                "layer_integrated_gradients_tokens.csv::"
                "attribution_signed_normalized",
            ],
        },

        "faithfulness": {
            "status": "QUANTITATIVELY VERIFIED",
            "intervention": faith_summary["intervention"],
            "random_comparator": faith_summary["random_comparator"],

            "probability_drop": (
                faith_summary["probability_drop"]
            ),

            "logit_drop": (
                faith_summary["logit_drop"]
            ),

            "saved_case_rows": int(len(faith_cases)),
        },

        "stability": {
            "status": (
                "NOT SEPARATELY EXECUTED OR SAVED"
                if not stability_files
                else "SAVED ARTEFACT FOUND"
            ),
            "files": stability_files,
            "claim_allowed": bool(stability_files),
        },

        "rq4_ruling": (
            "COMPLETE WITH BOUNDED CONCLUSION: "
            "saved relevance evidence and quantitative "
            "faithfulness are available; no separate "
            "stability result is claimed."
        ),

        "sha256_verified_files": verified,
    }

    output = Path(args.output)

    output.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print("RQ4 EXISTING-EVIDENCE CLOSURE")
    print("=" * 60)

    print(
        f"Saved LIG cases: {len(cases)}"
    )

    print(
        f"Saved LIG token rows: {len(tokens)}"
    )

    print(
        "Probability paired difference:",
        faith_summary[
            "probability_drop"
        ][
            "paired_difference"
        ][
            "observed_mean"
        ],
    )

    print(
        "Probability 95% CI:",
        (
            faith_summary[
                "probability_drop"
            ][
                "paired_difference"
            ][
                "lower_95"
            ],
            faith_summary[
                "probability_drop"
            ][
                "paired_difference"
            ][
                "upper_95"
            ],
        ),
    )

    print(
        "Stability artefacts:",
        stability_files or "NONE",
    )

    print(
        "Test partition accessed: FALSE"
    )

    print()
    print(
        "G06 / RQ4: CLOSED WITH EXPLICIT STABILITY LIMITATION"
    )


if __name__ == "__main__":
    main()
