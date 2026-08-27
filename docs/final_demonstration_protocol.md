# Final Operational Coding Twin — Demonstration Protocol

**Document version:** 1.0.0  
**Project:** AI-Powered Operational Digital Twin for Automated Medical Coding  
**Purpose:** Reproducible dissertation/viva demonstration  
**Scope:** Synthetic/demo inputs and frozen Phase 8B validation replay only

---

# 1. Demonstration Objective

The demonstration shall show that the completed prototype integrates:

1. clinical-case ingestion;
2. frozen medical-coding inference;
3. calibrated confidence;
4. explainability evidence;
5. explicit operational state transitions;
6. mandatory human review;
7. Accept / Reject / Amend decisions;
8. persistent case state;
9. tamper-evident audit history.

The demonstration is not intended to establish real NHS clinical performance.

---

# 2. Preconditions

Before starting the demonstration, verify that the project is located at:

`F:/operational_coding_twin`

and that the virtual environment is active.

The shell prompt should contain:

`(operational-coding-twin)`

Verify the automated test suite:

```bash
uv run pytest tests -q