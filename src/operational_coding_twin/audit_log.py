from __future__ import annotations

import hashlib
import json
import threading
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def canonical_json(
    payload: dict[str, Any],
) -> str:
    """
    Produce deterministic JSON for SHA-256 hashing.

    Sorting keys and using fixed separators ensures the same
    event content always produces the same hash.
    """

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


# ============================================================
# EXCEPTION
# ============================================================

class AuditIntegrityError(
    RuntimeError
):
    """
    Raised when the audit hash chain fails verification.
    """


# ============================================================
# APPEND-ONLY AUDIT LOG
# ============================================================

class AppendOnlyAuditLog:
    """
    Append-only JSONL audit history with SHA-256 hash chaining.

    Each event records:
        - timestamp
        - case ID
        - actor
        - action
        - state transition
        - reason
        - payload
        - previous event hash
        - current event hash

    The mechanism is tamper-evident for this research prototype.

    It should NOT be described as cryptographically immutable
    storage.
    """

    def __init__(
        self,
        path: Path,
    ) -> None:

        self.path = Path(
            path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.touch(
            exist_ok=True
        )

        # Prevent two threads from writing at exactly
        # the same time inside one running process.
        self._lock = threading.Lock()


    # ========================================================
    # INTERNAL
    # ========================================================

    def _last_event_hash(
        self,
    ) -> str | None:
        """
        Return the hash of the most recent audit event.
        """

        last_hash = None

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:

                if not line.strip():
                    continue

                event = json.loads(
                    line
                )

                last_hash = event[
                    "event_hash"
                ]

        return last_hash


    # ========================================================
    # WRITE EVENT
    # ========================================================

    def append(
        self,
        *,
        case_id: str,
        actor: str,
        action: str,
        reason: str,
        from_state: str | None,
        to_state: str | None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Append a single audit event.

        Existing events are never rewritten.
        """

        case_id = (
            case_id
            or ""
        ).strip()

        actor = (
            actor
            or ""
        ).strip()

        action = (
            action
            or ""
        ).strip()

        reason = (
            reason
            or ""
        ).strip()

        if not case_id:
            raise ValueError(
                "Audit case_id is required."
            )

        if not actor:
            raise ValueError(
                "Audit actor is required."
            )

        if not action:
            raise ValueError(
                "Audit action is required."
            )

        if not reason:
            raise ValueError(
                "Audit reason is required."
            )

        with self._lock:

            event = {

                "event_id":
                    str(
                        uuid.uuid4()
                    ),

                "timestamp_utc":
                    utc_now(),

                "case_id":
                    case_id,

                "actor":
                    actor,

                "action":
                    action,

                "from_state":
                    from_state,

                "to_state":
                    to_state,

                "reason":
                    reason,

                "payload":
                    payload or {},

                "previous_event_hash":
                    self._last_event_hash(),
            }

            event_hash = hashlib.sha256(
                canonical_json(
                    event
                ).encode(
                    "utf-8"
                )
            ).hexdigest()

            event[
                "event_hash"
            ] = event_hash

            # IMPORTANT:
            # File is opened in append mode.
            #
            # Existing audit events are not rewritten.

            with self.path.open(
                "a",
                encoding="utf-8",
            ) as handle:

                handle.write(
                    json.dumps(
                        event,
                        sort_keys=True,
                        ensure_ascii=False,
                        allow_nan=False,
                    )
                    + "\n"
                )

        return event


    # ========================================================
    # READ EVENTS
    # ========================================================

    def events(
        self,
        case_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return all audit events, or only events for one case.
        """

        output: list[
            dict[str, Any]
        ] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:

                if not line.strip():
                    continue

                event = json.loads(
                    line
                )

                if (
                    case_id is None
                    or event[
                        "case_id"
                    ]
                    == case_id
                ):
                    output.append(
                        event
                    )

        return output


    # ========================================================
    # VERIFY HASH CHAIN
    # ========================================================

    def verify(
        self,
    ) -> bool:
        """
        Verify the complete SHA-256 audit chain.

        Raises AuditIntegrityError if any event has been altered
        or if the previous-event links are broken.
        """

        previous_hash = None

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for (
                line_number,
                line
            ) in enumerate(
                handle,
                start=1,
            ):

                if not line.strip():
                    continue

                stored_event = json.loads(
                    line
                )

                stored_hash = (
                    stored_event.pop(
                        "event_hash"
                    )
                )

                # ------------------------------------------------
                # Verify link to previous event
                # ------------------------------------------------

                if (
                    stored_event[
                        "previous_event_hash"
                    ]
                    != previous_hash
                ):

                    raise AuditIntegrityError(
                        "Broken audit-chain link "
                        f"at line {line_number}."
                    )

                # ------------------------------------------------
                # Recalculate this event's SHA-256
                # ------------------------------------------------

                calculated_hash = hashlib.sha256(
                    canonical_json(
                        stored_event
                    ).encode(
                        "utf-8"
                    )
                ).hexdigest()

                if (
                    calculated_hash
                    != stored_hash
                ):

                    raise AuditIntegrityError(
                        "Audit event hash mismatch "
                        f"at line {line_number}."
                    )

                previous_hash = (
                    stored_hash
                )

        return True