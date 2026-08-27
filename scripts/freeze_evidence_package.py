from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_DIR = (
    ROOT
    / "evidence"
)

MANIFEST = (
    EVIDENCE_DIR
    / "evidence_manifest.json"
)

SIDECAR = (
    EVIDENCE_DIR
    / "evidence_manifest.sha256"
)


EXCLUDED = {
    MANIFEST.resolve(),
    SIDECAR.resolve(),
}


REQUIRED_VISUALS = [
    "evidence/02_replay/E01_application_scope.png",
    "evidence/02_replay/E02_replay_case_selected.png",
    "evidence/02_replay/E03_replay_prediction.png",
    "evidence/02_replay/E04_replay_xai.png",

    "evidence/04_human_review/E05_awaiting_human_review.png",
    "evidence/04_human_review/E06_accepted_completed.png",

    "evidence/03_fresh_inference/E07_fresh_prediction.png",
    "evidence/03_fresh_inference/E08_fresh_lig.png",

    "evidence/04_human_review/E09_amended_completed.png",

    "evidence/05_audit/E10_audit_history.png",
    "evidence/05_audit/E11_audit_integrity_pass.png",

    "evidence/06_provenance/E12_manifest_sha256_verified.png",
]


REQUIRED_NON_VISUAL = [
    "evidence/01_verification/pytest_full_results.txt",
    "evidence/01_verification/pytest_final_summary.txt",
    "evidence/01_verification/project_verification.txt",
    "evidence/01_verification/frozen_scientific_contract.txt",

    "evidence/06_provenance/source_artifact_hashes.json",
    "evidence/06_provenance/working_artifact_manifest.json",
    "evidence/06_provenance/working_artifact_manifest.sha256",
    "evidence/06_provenance/manifest_verification.txt",

    "evidence/evidence_index.csv",
    "evidence/visual_evidence_register.csv",

    "docs/final_evidence_index.md",
    "docs/final_implementation_record.md",
    "docs/final_requirements_traceability_matrix.md",
    "docs/final_demonstration_protocol.md",

    "EVIDENCE.md",
]


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        while True:
            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def relative(
    path: Path,
) -> str:
    return (
        path.resolve()
        .relative_to(
            ROOT.resolve()
        )
        .as_posix()
    )


def verify_required_files() -> None:
    required = (
        REQUIRED_VISUALS
        + REQUIRED_NON_VISUAL
    )

    missing = [
        path
        for path in required
        if not (
            ROOT
            / path
        ).is_file()
    ]

    if missing:
        print()
        print(
            "EVIDENCE FREEZE: FAILED"
        )

        print(
            "Required evidence is missing:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

        raise SystemExit(
            1
        )


def run_strict_verification() -> None:
    # --------------------------------------------------------
    # Verify the complete evidence package.
    # --------------------------------------------------------

    evidence_command = [
        sys.executable,
        str(
            ROOT
            / "scripts"
            / "verify_evidence_package.py"
        ),
        "--strict",
    ]

    evidence_result = subprocess.run(
        evidence_command,
        cwd=ROOT,
        check=False,
    )

    if evidence_result.returncode != 0:
        raise RuntimeError(
            "Strict evidence verification failed."
        )

    # --------------------------------------------------------
    # Verify frozen research traceability separately.
    #
    # This ensures that the exact v2.0.0 Aim, O1-O5 and
    # RQ1-RQ5 remain synchronised with the evidence index
    # before the evidence package can be frozen.
    # --------------------------------------------------------

    research_command = [
        sys.executable,
        str(
            ROOT
            / "scripts"
            / "step19_research_traceability.py"
        ),
        "--verify-only",
    ]

    research_result = subprocess.run(
        research_command,
        cwd=ROOT,
        check=False,
    )

    if research_result.returncode != 0:
        raise RuntimeError(
            "Frozen research traceability verification failed."
        )


def collect_files() -> list[Path]:
    files: set[Path] = set()

    # All evidence files.
    for path in EVIDENCE_DIR.rglob(
        "*"
    ):
        if (
            path.is_file()
            and
            path.resolve()
            not in EXCLUDED
        ):
            files.add(
                path.resolve()
            )

    # Final documentation.
    for name in (
    "generate_evidence_index.py",
    "verify_evidence_package.py",
    "freeze_evidence_package.py",
    "step19_research_traceability.py",
    "step20_dissertation_evidence_map.py",
):
        path = (
            ROOT
            / "docs"
            / name
        )

        if path.is_file():
            files.add(
                path.resolve()
            )
            # Final documentation.
#
# Include every final_*.md document automatically so later
# traceability/evidence documents cannot accidentally be omitted.
    docs_dir = ROOT / "docs"

    for path in sorted(
        docs_dir.glob("final_*.md")):

        if path.is_file():
            files.add(
            path.resolve()
        )

    # Repository evidence pointer.
    pointer = (
        ROOT
        / "EVIDENCE.md"
    )

    if pointer.is_file():
        files.add(
            pointer.resolve()
        )

    # Evidence tooling itself.
    for name in (
        "generate_evidence_index.py",
        "verify_evidence_package.py",
        "freeze_evidence_package.py",
    ):
        path = (
            ROOT
            / "scripts"
            / name
        )

        if path.is_file():
            files.add(
                path.resolve()
            )

    return sorted(
        files,
        key=lambda item: relative(
            item
        ),
    )


def main() -> None:
    verify_required_files()

    run_strict_verification()

    files = collect_files()

    records = []

    print()
    print(
        "=" * 72
    )
    print(
        "FREEZING FINAL EVIDENCE PACKAGE"
    )
    print(
        "=" * 72
    )

    for index, path in enumerate(
        files,
        start=1,
    ):
        digest = sha256_file(
            path
        )

        record = {
            "path":
                relative(
                    path
                ),

            "size_bytes":
                path.stat().st_size,

            "sha256":
                digest,
        }

        records.append(
            record
        )

        print(
            f"[{index:02d}/{len(files):02d}] "
            f"{record['path']}"
        )

    body = {
        "manifest_version":
            "1.0.0",

        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "purpose":
            (
                "SHA-256 evidence-package freeze for "
                "the completed MSc operational coding "
                "twin dissertation implementation."
            ),

        "boundary": {
            "implementation_evidence":
                True,

            "scientific_results_reproduced_here":
                False,

            "real_nhs_validation_claimed":
                False,

            "phase9_runtime_dependency":
                False,

            "human_review_required":
                True,

            "automatic_acceptance":
                False,
        },

        "file_count":
            len(
                records
            ),

        "files":
            records,
    }

    canonical = json.dumps(
        body,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    body[
        "manifest_content_sha256"
    ] = hashlib.sha256(
        canonical
    ).hexdigest()

    MANIFEST.write_text(
        json.dumps(
            body,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    physical_hash = sha256_file(
        MANIFEST
    )

    SIDECAR.write_bytes(
    (
        f"{physical_hash}  "
        f"{relative(MANIFEST)}\n"
    ).encode("utf-8")
    )

    print()
    print(
        "=" * 72
    )
    print(
        "FINAL EVIDENCE FREEZE"
    )
    print(
        "=" * 72
    )

    print(
        f"Files hashed: {len(records)}"
    )

    print(
        f"Manifest: {relative(MANIFEST)}"
    )

    print(
        f"Physical SHA-256: {physical_hash}"
    )

    print()
    print(
        "STEP 18D: PASS"
    )


if __name__ == "__main__":
    main()