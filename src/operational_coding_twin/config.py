from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# LOAD OPTIONAL .env FILE
# ============================================================

load_dotenv()


# ============================================================
# FROZEN SCIENTIFIC CONFIGURATION
# ============================================================

FROZEN_TEMPERATURE = 0.1838893138

MODEL_REFERENCE = "P7-BIOCLINICALBERT-SEED42-CANONICAL"

CALIBRATOR_REFERENCE = (
    "P8B-CORRECTIVE-V201-SEED42::"
    "temperature=0.1838893138"
)

CLAIMS_REFERENCE = (
    "P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201"
)


# ============================================================
# DISPLAY / GOVERNANCE WARNINGS
# ============================================================

CONFIDENCE_WARNING = (
    "Descriptive model uncertainty only. "
    "This value is not a probability of clinical safety, "
    "coding correctness, or billing correctness."
)

EXPLANATION_WARNING = (
    "Token attribution describes model behaviour only. "
    "It is not causal clinical evidence."
)


# ============================================================
# SETTINGS OBJECT
# ============================================================

@dataclass(frozen=True)
class Settings:

    # Project
    project_root: Path

    # Frozen artefacts
    artifacts_dir: Path
    model_dir: Path
    calibration_dir: Path
    replay_dir: Path
    governance_dir: Path
    provenance_dir: Path

    # Runtime
    runtime_dir: Path
    cases_dir: Path
    explanations_dir: Path
    audit_dir: Path
    errors_dir: Path

    # Frozen model files
    model_file: Path
    config_file: Path
    tokenizer_file: Path
    tokenizer_config_file: Path
    label_mapping_file: Path

    # Calibration
    temperature_file: Path

    # Replay
    replay_sample_file: Path
    replay_probabilities_file: Path
    replay_explanations_file: Path

    # Governance
    claims_file: Path

    # Provenance
    hash_manifest_file: Path


# ============================================================
# PATH HELPERS
# ============================================================

def _default_project_root() -> Path:
    """
    Resolve the repository root from this file.

    config.py is expected at:

        PROJECT_ROOT/
            src/
                operational_coding_twin/
                    config.py

    Therefore parents[2] is PROJECT_ROOT.
    """

    return Path(__file__).resolve().parents[2]


def _resolve_environment_path(
    variable_name: str,
    default: Path,
    project_root: Path,
) -> Path:
    """
    Resolve an optional environment-variable path.

    Relative paths are interpreted relative to the project root.
    """

    value = os.getenv(variable_name)

    if not value:
        return default.resolve()

    path = Path(value)

    if not path.is_absolute():
        path = project_root / path

    return path.resolve()


# ============================================================
# PUBLIC SETTINGS FUNCTION
# ============================================================

def get_settings() -> Settings:
    """
    Return all filesystem paths required by the working project.

    This function does not load the ML model and does not access
    any test-set artefacts.
    """

    default_root = _default_project_root()

    project_root = _resolve_environment_path(
        variable_name="BNS_PROJECT_ROOT",
        default=default_root,
        project_root=default_root,
    )

    artifacts_dir = (
        project_root
        / "artifacts"
    )

    model_dir = (
        artifacts_dir
        / "model"
    )

    calibration_dir = (
        artifacts_dir
        / "calibration"
    )

    replay_dir = (
        artifacts_dir
        / "replay"
    )

    governance_dir = (
        artifacts_dir
        / "governance"
    )

    provenance_dir = (
        artifacts_dir
        / "provenance"
    )

    runtime_dir = _resolve_environment_path(
        variable_name="BNS_RUNTIME_DIR",
        default=project_root / "runtime",
        project_root=project_root,
    )

    cases_dir = (
        runtime_dir
        / "cases"
    )

    explanations_dir = (
        runtime_dir
        / "explanations"
    )

    audit_dir = (
        runtime_dir
        / "audit"
    )

    errors_dir = (
        runtime_dir
        / "errors"
    )

    # --------------------------------------------------------
    # Create runtime folders automatically.
    # Frozen artefact folders are NOT created here because
    # missing frozen artefacts should later fail explicitly.
    # --------------------------------------------------------

    for directory in (
        runtime_dir,
        cases_dir,
        explanations_dir,
        audit_dir,
        errors_dir,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    return Settings(

        # Project
        project_root=project_root,

        # Artefact directories
        artifacts_dir=artifacts_dir,
        model_dir=model_dir,
        calibration_dir=calibration_dir,
        replay_dir=replay_dir,
        governance_dir=governance_dir,
        provenance_dir=provenance_dir,

        # Runtime directories
        runtime_dir=runtime_dir,
        cases_dir=cases_dir,
        explanations_dir=explanations_dir,
        audit_dir=audit_dir,
        errors_dir=errors_dir,

        # Model
        model_file=(
            model_dir
            / "model.safetensors"
        ),

        config_file=(
            model_dir
            / "config.json"
        ),

        tokenizer_file=(
            model_dir
            / "tokenizer.json"
        ),

        tokenizer_config_file=(
            model_dir
            / "tokenizer_config.json"
        ),

        label_mapping_file=(
            model_dir
            / "label_mapping.json"
        ),

        # Calibration
        temperature_file=(
            calibration_dir
            / "temperature_scaling.json"
        ),

        # Replay
        replay_sample_file=(
            replay_dir
            / "deterministic_validation_sample_100.csv"
        ),

        replay_probabilities_file=(
            replay_dir
            / "validation_calibrated_probabilities.npy"
        ),

        replay_explanations_file=(
            replay_dir
            / "layer_integrated_gradients_cases.csv"
        ),

        # Governance
        claims_file=(
            governance_dir
            / "final_claims_freeze.json"
        ),

        # Provenance
        hash_manifest_file=(
            provenance_dir
            / "source_artifact_hashes.json"
        ),
    )