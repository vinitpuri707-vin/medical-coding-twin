from __future__ import annotations

import hashlib
import json
import os

from pathlib import Path
from typing import Any


class CaseStore:
    """
    Persistent JSON-based storage for operational-twin cases.

    Each case is stored as an individual JSON file.

    This represents the current digital state of a coding case.

    Example:

        case_id = SYN-001

        state = Awaiting Human Review

        recommendation = I50

        reviewer_identity = None
    """

    def __init__(
        self,
        directory: Path,
    ) -> None:

        self.directory = Path(
            directory
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )


    # ========================================================
    # INTERNAL FILE PATH
    # ========================================================

    def _path(
        self,
        case_id: str,
    ) -> Path:
        """
        Convert a case ID into a safe deterministic filename.

        We do not use the raw case ID directly as a filename.
        """

        case_id = (
            case_id
            or ""
        ).strip()

        if not case_id:
            raise ValueError(
                "case_id is required."
            )

        safe_id = hashlib.sha256(
            case_id.encode(
                "utf-8"
            )
        ).hexdigest()[:24]

        return (
            self.directory
            / f"case_{safe_id}.json"
        )


    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        case_id: str,
        payload: dict[str, Any],
    ) -> Path:
        """
        Persist the latest state of a case.

        A temporary file is written first and then atomically
        replaced to reduce the chance of a partially written
        JSON case file.
        """

        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "Case payload must be a dictionary."
            )

        if (
            payload.get(
                "case_id"
            )
            != case_id
        ):
            raise ValueError(
                "payload['case_id'] must match case_id."
            )

        target = self._path(
            case_id
        )

        temporary = (
            target.with_suffix(
                ".tmp"
            )
        )

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
    # GET
    # ========================================================

    def get(
        self,
        case_id: str,
    ) -> dict[str, Any]:
        """
        Load one stored case.
        """

        target = self._path(
            case_id
        )

        if not target.exists():
            raise KeyError(
                f"Unknown case_id: {case_id}"
            )

        payload = json.loads(
            target.read_text(
                encoding="utf-8"
            )
        )

        if (
            payload.get(
                "case_id"
            )
            != case_id
        ):
            raise RuntimeError(
                "Stored case ID does not match "
                "requested case ID."
            )

        return payload


    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        case_id: str,
    ) -> bool:
        """
        Return True if the case already exists.
        """

        return self._path(
            case_id
        ).exists()


    # ========================================================
    # LIST CASES
    # ========================================================

    def list_all(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all stored cases.
        """

        cases: list[
            dict[str, Any]
        ] = []

        for path in sorted(
            self.directory.glob(
                "case_*.json"
            )
        ):

            try:

                payload = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

                cases.append(
                    payload
                )

            except (
                json.JSONDecodeError,
                OSError,
            ) as exc:

                raise RuntimeError(
                    "Unable to read case file: "
                    f"{path}"
                ) from exc

        return cases


    # ========================================================
    # COUNT
    # ========================================================

    def count(
        self,
    ) -> int:
        """
        Return number of currently stored cases.
        """

        return len(
            list(
                self.directory.glob(
                    "case_*.json"
                )
            )
        )