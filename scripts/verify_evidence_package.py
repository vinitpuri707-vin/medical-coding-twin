from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_DOCUMENTS = [
    "docs/final_implementation_record.md",
    "docs/final_requirements_traceability_matrix.md",
    "docs/final_demonstration_protocol.md",
    "docs/final_evidence_index.md",
    "EVIDENCE.md",
]


REQUIRED_GENERATED_INDEXES = [
    "evidence/evidence_index.csv",
    "evidence/visual_evidence_register.csv",
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
]


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


def exists(
    relative_path: str,
) -> bool:
    return (
        ROOT
        / relative_path
    ).is_file()


def sha256(
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


def verify_rtm() -> tuple[
    bool,
    str,
]:
    path = (
        ROOT
        / "docs"
        / "final_requirements_traceability_matrix.md"
    )

    if not path.is_file():
        return (
            False,
            "RTM file is missing.",
        )

    text = path.read_text(
        encoding="utf-8",
    )

    requirements = re.findall(
        r"^\|\s*OT-R\d{2}\s*\|",
        text,
        flags=re.MULTILINE,
    )

    if len(
        requirements
    ) != 50:
        return (
            False,
            (
                "Expected 50 OT-R requirements, "
                f"found {len(requirements)}."
            ),
        )

    return (
        True,
        "50 OT-R requirements found.",
    )


def verify_visual_csv() -> tuple[
    bool,
    str,
]:
    path = (
        ROOT
        / "evidence"
        / "visual_evidence_register.csv"
    )

    if not path.is_file():
        return (
            False,
            "Visual evidence register missing.",
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    ids = {
        row[
            "evidence_id"
        ]
        for row in rows
    }

    expected = {
        f"E{i:02d}"
        for i in range(
            1,
            13,
        )
    }

    if ids != expected:
        return (
            False,
            (
                "Visual register IDs do not equal "
                "E01–E12."
            ),
        )

    return (
        True,
        "Visual register contains E01–E12.",
    )


def verify_working_manifest_checksum() -> tuple[
    bool,
    str,
]:
    manifest = (
        ROOT
        / "artifacts"
        / "provenance"
        / "working_artifact_manifest.json"
    )

    sidecar = (
        ROOT
        / "artifacts"
        / "provenance"
        / "working_artifact_manifest.sha256"
    )

    if not manifest.is_file():
        return (
            False,
            "Working manifest is missing.",
        )

    if not sidecar.is_file():
        return (
            False,
            "Working manifest SHA-256 sidecar is missing.",
        )

    expected = (
        sidecar
        .read_text(
            encoding="utf-8",
        )
        .strip()
        .split()[0]
        .lower()
    )

    actual = sha256(
        manifest
    )

    if actual != expected:
        return (
            False,
            (
                "Working manifest SHA-256 mismatch."
            ),
        )

    return (
        True,
        "Working manifest SHA-256 verified.",
    )


def verify_pytest_summary() -> tuple[
    bool,
    str,
]:
    path = (
        ROOT
        / "evidence"
        / "01_verification"
        / "pytest_final_summary.txt"
    )

    if not path.is_file():
        return (
            False,
            "Final pytest summary missing.",
        )

    text = (
        path.read_text(
            encoding="utf-8",
            errors="replace",
        )
        .lower()
    )

    if "passed" not in text:
        return (
            False,
            "Pytest summary does not contain a passed result.",
        )

    failure_patterns = [
        r"\b[1-9]\d*\s+failed\b",
        r"\b[1-9]\d*\s+error(?:s)?\b",
    ]

    if any(
        re.search(
            pattern,
            text,
        )
        for pattern in failure_patterns
    ):
        return (
            False,
            "Pytest summary contains failures/errors.",
        )

    return (
        True,
        "Pytest summary contains no reported failures.",
    )


def check_files(
    paths: list[str],
) -> list[str]:
    return [
        path
        for path in paths
        if not exists(
            path
        )
    ]


def main() -> None:
    # print("entering main function")
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Require all visual and non-visual "
            "evidence to exist."
        ),
    )

    args = parser.parse_args()

    failures: list[str] = []

    print()
    print(
        "=" * 72
    )
    print(
        "FINAL EVIDENCE PACKAGE VERIFICATION"
    )
    print(
        "=" * 72
    )

    missing_docs = check_files(
        REQUIRED_DOCUMENTS
    )

    missing_indexes = check_files(
        REQUIRED_GENERATED_INDEXES
    )

    missing_non_visual = check_files(
        REQUIRED_NON_VISUAL
    )

    missing_visuals = check_files(
        REQUIRED_VISUALS
    )

    for path in REQUIRED_DOCUMENTS:
        print(
            (
                "PASS"
                if exists(path)
                else "FAIL"
            ),
            path,
        )

    for path in REQUIRED_GENERATED_INDEXES:
        print(
            (
                "PASS"
                if exists(path)
                else "FAIL"
            ),
            path,
        )

    rtm_ok, rtm_message = (
        verify_rtm()
    )

    print(
        (
            "PASS"
            if rtm_ok
            else "FAIL"
        ),
        "RTM:",
        rtm_message,
    )

    visual_csv_ok, visual_csv_message = (
        verify_visual_csv()
    )

    print(
        (
            "PASS"
            if visual_csv_ok
            else "FAIL"
        ),
        "Visual register:",
        visual_csv_message,
    )

    manifest_ok, manifest_message = (
        verify_working_manifest_checksum()
    )

    print(
        (
            "PASS"
            if manifest_ok
            else "FAIL"
        ),
        "Manifest:",
        manifest_message,
    )

    pytest_ok, pytest_message = (
        verify_pytest_summary()
    )

    print(
        (
            "PASS"
            if pytest_ok
            else "FAIL"
        ),
        "Pytest:",
        pytest_message,
    )

    print()
    print(
        "Visual evidence:"
    )

    for path in REQUIRED_VISUALS:
        print(
            (
                "PASS"
                if exists(path)
                else "MISSING"
            ),
            path,
        )

    print()
    print(
        "Non-visual evidence:"
    )

    for path in REQUIRED_NON_VISUAL:
        print(
            (
                "PASS"
                if exists(path)
                else "MISSING"
            ),
            path,
        )

    if missing_docs:
        failures.append(
            "Required documentation missing."
        )

    if missing_indexes:
        failures.append(
            "Generated index files missing."
        )

    if not rtm_ok:
        failures.append(
            rtm_message
        )

    if not visual_csv_ok:
        failures.append(
            visual_csv_message
        )

    if not manifest_ok:
        failures.append(
            manifest_message
        )

    if args.strict:
        if missing_non_visual:
            failures.append(
                (
                    "Strict mode: "
                    "non-visual evidence missing."
                )
            )

        if missing_visuals:
            failures.append(
                (
                    "Strict mode: "
                    "visual evidence missing."
                )
            )

        if not pytest_ok:
            failures.append(
                pytest_message
            )

    print()
    print(
        "=" * 72
    )

    if failures:
        print(
            "EVIDENCE PACKAGE: INCOMPLETE"
        )

        for failure in failures:
            print(
                f"- {failure}"
            )

        if args.strict:
            raise SystemExit(
                1
            )

    else:
        print(
            "EVIDENCE PACKAGE: PASS"
        )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()