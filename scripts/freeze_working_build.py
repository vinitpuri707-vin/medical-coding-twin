from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from operational_coding_twin.config import (
    CALIBRATOR_REFERENCE,
    CLAIMS_REFERENCE,
    FROZEN_TEMPERATURE,
    MODEL_REFERENCE,
    get_settings,
)


MANIFEST_VERSION = "1.0.0"


def sha256_file(
    path: Path,
    *,
    chunk_size: int = 1024 * 1024,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(
                chunk_size
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def package_version(
    package: str,
) -> str | None:
    try:
        return version(
            package
        )

    except PackageNotFoundError:
        return None


def relative_to_root(
    path: Path,
    root: Path,
) -> str:
    return (
        path.resolve()
        .relative_to(
            root.resolve()
        )
        .as_posix()
    )


def main() -> None:
    settings = get_settings()

    root = (
        settings.project_root
        .resolve()
    )

    target = (
        settings.provenance_dir
        / "working_artifact_manifest.json"
    )

    # --------------------------------------------------------
    # Files that define the final working implementation.
    # --------------------------------------------------------

    required_files = [

        # Repository / dependency definition
        root / "pyproject.toml",
        root / "uv.lock",

        # Final freeze procedure
        root
        / "scripts"
        / "freeze_working_build.py",

        # Final implementation documentation
        root
        / "docs"
        / "final_implementation_record.md",

        root
        / "docs"
        / "final_requirements_traceability_matrix.md",

        root
        / "docs"
        / "final_demonstration_protocol.md",

        # Application
        root / "app" / "streamlit_app.py",

        # Runtime package
        root
        / "src"
        / "operational_coding_twin"
        / "__init__.py",

        root
        / "src"
        / "operational_coding_twin"
        / "config.py",

        root
        / "src"
        / "operational_coding_twin"
        / "frozen_resources.py",

        root
        / "src"
        / "operational_coding_twin"
        / "inference.py",

        root
        / "src"
        / "operational_coding_twin"
        / "explainability.py",

        root
        / "src"
        / "operational_coding_twin"
        / "digital_twin.py",

        root
        / "src"
        / "operational_coding_twin"
        / "case_store.py",

        root
        / "src"
        / "operational_coding_twin"
        / "audit_log.py",

        # Verification scripts
        root
        / "scripts"
        / "check_artifacts.py",

        root
        / "scripts"
        / "check_digital_twin.py",

        root
        / "scripts"
        / "verify_project.py",

        # Tests
        root
        / "tests"
        / "test_foundation.py",

        root
        / "tests"
        / "test_frozen_resources.py",

        root
        / "tests"
        / "test_inference.py",

        root
        / "tests"
        / "test_explainability.py",

        root
        / "tests"
        / "test_digital_twin.py",

        root
        / "tests"
        / "test_governance.py",

        # Frozen scientific runtime artefacts
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

        # Authoritative research provenance
        settings.hash_manifest_file,

        # Test evidence
        root
        / "runtime"
        / "pytest_full_results.txt",
    ]

    # --------------------------------------------------------
    # Validate required files before creating a manifest.
    # --------------------------------------------------------

    missing = [
        path
        for path in required_files
        if not path.is_file()
    ]

    if missing:
        print()
        print(
            "WORKING BUILD FREEZE: FAILED"
        )
        print()
        print(
            "Required files are missing:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

        raise SystemExit(
            1
        )

    # --------------------------------------------------------
    # Explicit guard against Phase 9 / test-partition artefacts.
    # --------------------------------------------------------

    forbidden_terms = (
        "phase9",
        "test_predictions",
        "transformer_test",
        "baseline_test",
        "test_logits",
        "test_probabilities",
    )

    for path in required_files:
        lowered = str(
            path
        ).lower()

        if any(
            term in lowered
            for term in forbidden_terms
        ):
            raise RuntimeError(
                "Prohibited test-partition dependency "
                f"detected: {path}"
            )

    # --------------------------------------------------------
    # Hash the complete frozen working build.
    # --------------------------------------------------------

    records = []

    print()
    print(
        "=" * 72
    )
    print(
        "FREEZING WORKING OPERATIONAL-TWIN BUILD"
    )
    print(
        "=" * 72
    )

    for index, path in enumerate(
        required_files,
        start=1,
    ):
        digest = sha256_file(
            path
        )

        record = {
            "path": relative_to_root(
                path,
                root,
            ),
            "size_bytes": (
                path.stat().st_size
            ),
            "sha256": digest,
        }

        records.append(
            record
        )

        print(
            f"[{index:02d}/{len(required_files):02d}] "
            f"{record['path']}"
        )

        print(
            f"       SHA-256: {digest}"
        )

    # --------------------------------------------------------
    # Environment snapshot
    # --------------------------------------------------------

    packages = {
        package: package_version(
            package
        )
        for package in (
            "torch",
            "transformers",
            "captum",
            "streamlit",
            "numpy",
            "pandas",
            "pytest",
        )
    }

    manifest = {
        "manifest_version":
            MANIFEST_VERSION,

        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "project":
            "operational_coding_twin",

        "purpose":
            (
                "SHA-256 freeze of the completed "
                "working operational digital-twin "
                "research prototype."
            ),

        "research_boundary": {
            "primary_runtime_scope":
                "synthetic/demo data only",

            "replay_partition":
                "validation",

            "phase9_test_runtime_access":
                False,

            "automatic_acceptance":
                False,

            "human_review_required":
                True,
        },

        "frozen_scientific_contract": {
            "model_reference":
                MODEL_REFERENCE,

            "calibrator_reference":
                CALIBRATOR_REFERENCE,

            "claims_reference":
                CLAIMS_REFERENCE,

            "temperature":
                FROZEN_TEMPERATURE,

            "max_length":
                320,

            "label_count":
                50,

            "prediction_setting":
                "single-label multiclass",

            "calibration":
                "single scalar temperature scaling",

            "explainability":
                "Layer Integrated Gradients",

            "lig_steps":
                50,

            "lig_target":
                "predicted class",

            "lig_baseline":
                "PAD-content baseline; special tokens preserved",
        },

        "environment": {
            "python":
                sys.version,

            "python_executable":
                sys.executable,

            "platform":
                platform.platform(),

            "packages":
                packages,
        },

        "files":
            records,
    }

    # --------------------------------------------------------
    # Manifest-level digest.
    #
    # Calculate against the deterministic manifest body before
    # adding the manifest's own hash.
    # --------------------------------------------------------

    canonical = json.dumps(
        manifest,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    manifest_hash = (
        hashlib.sha256(
            canonical
        )
        .hexdigest()
    )

    manifest[
        "manifest_sha256"
    ] = manifest_hash

    settings.provenance_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "=" * 72
    )
    print(
        "WORKING BUILD FREEZE RESULT"
    )
    print(
        "=" * 72
    )

    print(
        f"Files hashed: "
        f"{len(records)}"
    )

    print(
        f"Manifest: "
        f"{relative_to_root(target, root)}"
    )

    print(
        f"Manifest SHA-256: "
        f"{manifest_hash}"
    )

    print(
        "Automatic acceptance: DISABLED"
    )

    print(
        "Human review: REQUIRED"
    )

    print(
        "Replay partition: VALIDATION"
    )

    print(
        "Phase 9/test runtime access: NO"
    )

    print()
    print(
        "STEP 17A: PASS"
    )


if __name__ == "__main__":
    main()