# Final Evidence and Traceability Index

**Document version:** 1.0.0  
**Purpose:** Repository evidence lookup and dissertation traceability  
**Runtime boundary:** Synthetic/demo data and frozen Phase 8B validation replay only  

---

# 1. Purpose

This document is the primary topic-first evidence lookup for the repository.

It answers:

> Where is the evidence supporting a particular implementation or research claim?

The evidence chain is:

```text
Research / governance requirement
        ↓
Implementation
        ↓
Automated verification
        ↓
Evidence artefact
        ↓
Dissertation interpretation
```

Screenshots are implementation evidence and must not be treated as predictive-performance evidence.

---

# 2. Quick Evidence Lookup

| ID | Topic | Requirement | Primary evidence | Status |
|---|---|---|---|---|
| T01 | Dataset and frozen scientific scope | OT-R01; OT-R02; OT-R18; OT-R46; OT-R49 | `evidence/01_verification/frozen_scientific_contract.txt` | AVAILABLE |
| T02 | Frozen BioClinicalBERT model | OT-R01–OT-R06 | `artifacts/model/model.safetensors` | AVAILABLE |
| T03 | Calibration and model confidence | OT-R07–OT-R09; OT-R29; OT-R30 | `artifacts/calibration/temperature_scaling.json` | AVAILABLE |
| T04 | Fresh synthetic inference | OT-R01–OT-R09; OT-R43; OT-R46 | `evidence/03_fresh_inference/E07_fresh_prediction.png` | AVAILABLE |
| T05 | Frozen validation replay | OT-R15–OT-R18; OT-R45; OT-R47; OT-R48 | `artifacts/replay/deterministic_validation_sample_100.csv` | AVAILABLE |
| T06 | Explainable AI | OT-R10–OT-R14; OT-R17 | `artifacts/replay/layer_integrated_gradients_cases.csv` | AVAILABLE |
| T07 | Operational digital-twin state machine | OT-R19–OT-R35 | `docs/final_implementation_record.md` | AVAILABLE |
| T08 | Mandatory human review | OT-R21; OT-R25; OT-R26; OT-R29; OT-R30; OT-R31 | `evidence/04_human_review/E05_awaiting_human_review.png` | AVAILABLE |
| T09 | Accept, Reject and Amend | OT-R22–OT-R28; OT-R31 | `evidence/04_human_review/E06_accepted_completed.png` | AVAILABLE |
| T10 | Case persistence | OT-R36–OT-R38 | `runtime/cases/` | AVAILABLE |
| T11 | Auditability | OT-R35; OT-R39–OT-R42 | `evidence/05_audit/E10_audit_history.png` | AVAILABLE |
| T12 | No automatic acceptance | OT-R29; OT-R30 | `evidence/04_human_review/E05_awaiting_human_review.png` | AVAILABLE |
| T13 | Phase 9 / test-partition isolation | OT-R18 | `artifacts/provenance/working_artifact_manifest.json` | AVAILABLE |
| T14 | Reproducibility and SHA-256 provenance | OT-R50 | `artifacts/provenance/source_artifact_hashes.json` | AVAILABLE |
| T15 | Automated implementation verification | Cross-cutting | `evidence/01_verification/pytest_full_results.txt` | AVAILABLE |

---

# 3. Dataset and frozen scientific scope

## Requirements

`OT-R01; OT-R02; OT-R18; OT-R46; OT-R49`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `artifacts/model/label_mapping.json`
- `artifacts/governance/final_claims_freeze.json`
- `docs/final_implementation_record.md`

## Verification

- `tests/test_frozen_resources.py`
- `tests/test_governance.py`

## Evidence

- `evidence/01_verification/frozen_scientific_contract.txt` — AVAILABLE
- `docs/final_requirements_traceability_matrix.md` — AVAILABLE

## Dissertation location

- Chapter 3 — Methodology
- Chapter 4 — System Design and Implementation
- Chapter 6 — Discussion and Limitations

## Supported claim

The working application implements the frozen single-label 50-category synthetic ICD-10 research setting.

## Claim boundary

Does not establish performance on genuine NHS free text or clinical deployment readiness.

---

# 4. Frozen BioClinicalBERT model

## Requirements

`OT-R01–OT-R06`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/frozen_resources.py`
- `src/operational_coding_twin/inference.py`

## Verification

- `tests/test_frozen_resources.py`
- `tests/test_inference.py`

## Evidence

- `artifacts/model/model.safetensors` — AVAILABLE
- `artifacts/model/config.json` — AVAILABLE
- `artifacts/model/tokenizer.json` — AVAILABLE
- `artifacts/model/tokenizer_config.json` — AVAILABLE
- `artifacts/model/label_mapping.json` — AVAILABLE
- `evidence/03_fresh_inference/E07_fresh_prediction.png` — AVAILABLE

## Dissertation location

- Chapter 3 — Predictive methodology
- Chapter 4 — Model integration
- Chapter 5 — Experimental results

## Supported claim

Fresh synthetic cases use the frozen canonical seed-42 BioClinicalBERT model.

## Claim boundary

Application screenshots do not establish predictive superiority or external validity.

---

# 5. Calibration and model confidence

## Requirements

`OT-R07–OT-R09; OT-R29; OT-R30`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/config.py`
- `src/operational_coding_twin/frozen_resources.py`
- `src/operational_coding_twin/inference.py`

## Verification

- `tests/test_frozen_resources.py`
- `tests/test_inference.py`
- `tests/test_governance.py`

## Evidence

- `artifacts/calibration/temperature_scaling.json` — AVAILABLE
- `evidence/02_replay/E03_replay_prediction.png` — AVAILABLE
- `evidence/03_fresh_inference/E07_fresh_prediction.png` — AVAILABLE

## Dissertation location

- Chapter 3 — Calibration methodology
- Chapter 4 — Confidence integration
- Chapter 5 — Calibration evaluation
- Chapter 6 — Uncertainty limitations

## Supported claim

Runtime logits are transformed using the frozen validation-fitted scalar temperature before probabilities are displayed.

## Claim boundary

Calibrated confidence is descriptive model uncertainty, not a probability of coding correctness, billing correctness or clinical safety.

---

# 6. Fresh synthetic inference

## Requirements

`OT-R01–OT-R09; OT-R43; OT-R46`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/inference.py`
- `app/streamlit_app.py`

## Verification

- `tests/test_inference.py`

## Evidence

- `evidence/03_fresh_inference/E07_fresh_prediction.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Fresh synthetic-case inference

## Supported claim

A new synthetic clinical note can be processed through frozen BioClinicalBERT inference and temperature calibration.

## Claim boundary

This is operational implementation evidence, not evidence of performance on authentic NHS clinical notes.

---

# 7. Frozen validation replay

## Requirements

`OT-R15–OT-R18; OT-R45; OT-R47; OT-R48`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/frozen_resources.py`
- `src/operational_coding_twin/inference.py`
- `src/operational_coding_twin/explainability.py`
- `app/streamlit_app.py`

## Verification

- `tests/test_frozen_resources.py`
- `tests/test_inference.py`
- `tests/test_explainability.py`

## Evidence

- `artifacts/replay/deterministic_validation_sample_100.csv` — AVAILABLE
- `artifacts/replay/validation_calibrated_probabilities.npy` — AVAILABLE
- `artifacts/replay/layer_integrated_gradients_cases.csv` — AVAILABLE
- `evidence/02_replay/E02_replay_case_selected.png` — AVAILABLE
- `evidence/02_replay/E03_replay_prediction.png` — AVAILABLE
- `evidence/02_replay/E04_replay_xai.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Deterministic operational replay
- Appendix — Demonstration protocol

## Supported claim

Replay reconstructs workflow behaviour using frozen Phase 8B validation artefacts.

## Claim boundary

Replay is not a second experiment and does not constitute Phase 9 test evaluation.

---

# 8. Explainable AI

## Requirements

`OT-R10–OT-R14; OT-R17`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/explainability.py`

## Verification

- `tests/test_explainability.py`

## Evidence

- `artifacts/replay/layer_integrated_gradients_cases.csv` — AVAILABLE
- `evidence/02_replay/E04_replay_xai.png` — AVAILABLE
- `evidence/03_fresh_inference/E08_fresh_lig.png` — AVAILABLE

## Dissertation location

- Chapter 3 — Explainability methodology
- Chapter 4 — XAI implementation
- Chapter 5 — XAI evaluation
- Chapter 6 — Interpretability limitations

## Supported claim

The prototype integrates predicted-class Layer Integrated Gradients using 50 steps and the frozen PAD-content baseline.

## Claim boundary

Token attribution describes model behaviour; it is not causal clinical evidence.

---

# 9. Operational digital-twin state machine

## Requirements

`OT-R19–OT-R35`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/digital_twin.py`

## Verification

- `tests/test_digital_twin.py`
- `tests/test_governance.py`

## Evidence

- `docs/final_implementation_record.md` — AVAILABLE
- `evidence/04_human_review/E05_awaiting_human_review.png` — AVAILABLE
- `evidence/04_human_review/E06_accepted_completed.png` — AVAILABLE
- `evidence/04_human_review/E09_amended_completed.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Operational digital-twin architecture

## Supported claim

Each coding case has an explicit persistent operational state and controlled state transitions.

## Claim boundary

The prototype is an operational workflow twin, not a physiological patient digital twin.

---

# 10. Mandatory human review

## Requirements

`OT-R21; OT-R25; OT-R26; OT-R29; OT-R30; OT-R31`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/digital_twin.py`
- `app/streamlit_app.py`

## Verification

- `tests/test_digital_twin.py`
- `tests/test_governance.py`

## Evidence

- `evidence/04_human_review/E05_awaiting_human_review.png` — AVAILABLE
- `evidence/04_human_review/E06_accepted_completed.png` — AVAILABLE
- `evidence/04_human_review/E09_amended_completed.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Human-in-the-loop workflow
- Chapter 6 — Governance discussion

## Supported claim

Every model recommendation requires an explicit human-review decision before completion.

## Claim boundary

The implementation does not establish that human review improves real coder productivity or accuracy.

---

# 11. Accept, Reject and Amend

## Requirements

`OT-R22–OT-R28; OT-R31`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/digital_twin.py`
- `app/streamlit_app.py`

## Verification

- `tests/test_digital_twin.py`

## Evidence

- `evidence/04_human_review/E06_accepted_completed.png` — AVAILABLE
- `evidence/04_human_review/E09_amended_completed.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Human disposition workflow

## Supported claim

The reviewer retains authority to accept, reject or amend the model recommendation.

## Claim boundary

Human authority is implemented structurally; no claim of improved clinical outcome is made.

---

# 12. Case persistence

## Requirements

`OT-R36–OT-R38`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/case_store.py`
- `src/operational_coding_twin/digital_twin.py`

## Verification

- `tests/test_foundation.py`
- `tests/test_digital_twin.py`

## Evidence

- `runtime/cases/` — AVAILABLE

## Dissertation location

- Chapter 4 — Persistent case state

## Supported claim

Operational case state persists independently of transient Streamlit interactions.

## Claim boundary

Local JSON persistence is a research-prototype storage mechanism rather than production EHR persistence.

---

# 13. Auditability

## Requirements

`OT-R35; OT-R39–OT-R42`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/audit_log.py`
- `src/operational_coding_twin/digital_twin.py`

## Verification

- `tests/test_foundation.py`
- `tests/test_digital_twin.py`

## Evidence

- `evidence/05_audit/E10_audit_history.png` — AVAILABLE
- `evidence/05_audit/E11_audit_integrity_pass.png` — AVAILABLE
- `runtime/audit/` — AVAILABLE

## Dissertation location

- Chapter 4 — Audit architecture
- Chapter 6 — Governance and limitations

## Supported claim

Operational events are linked through a SHA-256 tamper-evident hash chain.

## Claim boundary

The mechanism is tamper-evident, not immutable.

---

# 14. No automatic acceptance

## Requirements

`OT-R29; OT-R30`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/digital_twin.py`

## Verification

- `tests/test_digital_twin.py`
- `tests/test_governance.py`

## Evidence

- `evidence/04_human_review/E05_awaiting_human_review.png` — AVAILABLE

## Dissertation location

- Chapter 4 — Decision-support governance
- Chapter 6 — Safety and limitations

## Supported claim

High confidence cannot bypass mandatory human review.

## Claim boundary

Calibration is not used as an autonomous coding-correctness threshold.

---

# 15. Phase 9 / test-partition isolation

## Requirements

`OT-R18`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `src/operational_coding_twin/frozen_resources.py`
- `src/operational_coding_twin/inference.py`

## Verification

- `tests/test_frozen_resources.py`
- `tests/test_governance.py`
- `scripts/verify_project.py`

## Evidence

- `artifacts/provenance/working_artifact_manifest.json` — AVAILABLE
- `evidence/01_verification/project_verification.txt` — AVAILABLE

## Dissertation location

- Chapter 3 — Experimental protocol
- Chapter 5 — Final evaluation
- Appendix — Reproducibility

## Supported claim

Phase 9 test prediction artefacts are not operational runtime dependencies.

## Claim boundary

Phase 9 remains legitimate final scientific evaluation evidence and is deliberately separate from runtime replay.

---

# 16. Reproducibility and SHA-256 provenance

## Requirements

`OT-R50`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `scripts/freeze_working_build.py`

## Verification

- `artifacts/provenance/working_artifact_manifest.sha256`

## Evidence

- `artifacts/provenance/source_artifact_hashes.json` — AVAILABLE
- `artifacts/provenance/working_artifact_manifest.json` — AVAILABLE
- `artifacts/provenance/working_artifact_manifest.sha256` — AVAILABLE
- `evidence/06_provenance/E12_manifest_sha256_verified.png` — AVAILABLE
- `evidence/06_provenance/manifest_verification.txt` — AVAILABLE

## Dissertation location

- Chapter 3 — Reproducibility
- Appendix — Provenance

## Supported claim

The frozen working-copy implementation is fingerprinted using SHA-256.

## Claim boundary

The working manifest does not independently prove source-archive identity unless compared against authoritative source hashes.

---

# 17. Automated implementation verification

## Requirements

`Cross-cutting`

## Frozen RQ / Objective

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

## Implementation

- `tests/test_foundation.py`
- `tests/test_frozen_resources.py`
- `tests/test_inference.py`
- `tests/test_explainability.py`
- `tests/test_digital_twin.py`
- `tests/test_governance.py`

## Verification

- `runtime/pytest_full_results.txt`
- `evidence/01_verification/pytest_final_summary.txt`
- `evidence/01_verification/project_verification.txt`

## Evidence

- `evidence/01_verification/pytest_full_results.txt` — AVAILABLE
- `evidence/01_verification/pytest_final_summary.txt` — AVAILABLE
- `evidence/01_verification/project_verification.txt` — AVAILABLE

## Dissertation location

- Chapter 5 — Engineering verification
- Appendix — Full automated test output

## Supported claim

The final operational prototype is subject to automated verification across scientific resources, inference, XAI, workflow and governance.

## Claim boundary

Software tests are engineering evidence and must not be presented as predictive model performance.

---

# Visual Evidence Register

| ID | Topic | File | Demonstrates | Status |
|---|---|---|---|---|
| E01 | Application scope | `evidence/02_replay/E01_application_scope.png` | Synthetic/demo boundary, mandatory human review and application governance. | VERIFIED |
| E02 | Frozen validation replay | `evidence/02_replay/E02_replay_case_selected.png` | Selection of a deterministic Phase 8B validation replay case. | VERIFIED |
| E03 | Replay prediction | `evidence/02_replay/E03_replay_prediction.png` | Top-1, Top-3 and calibrated probability display during frozen validation replay. | VERIFIED |
| E04 | Replay explainability | `evidence/02_replay/E04_replay_xai.png` | Frozen Phase 8B LIG evidence displayed within the operational workflow. | VERIFIED |
| E05 | Mandatory human review | `evidence/04_human_review/E05_awaiting_human_review.png` | AI recommendation reaching the explicit human review gate. | VERIFIED |
| E06 | Acceptance workflow | `evidence/04_human_review/E06_accepted_completed.png` | Human acceptance followed by explicit workflow completion. | VERIFIED |
| E07 | Fresh frozen-model inference | `evidence/03_fresh_inference/E07_fresh_prediction.png` | New synthetic-note inference using the frozen BioClinicalBERT model. | VERIFIED |
| E08 | Fresh Layer Integrated Gradients | `evidence/03_fresh_inference/E08_fresh_lig.png` | Runtime 50-step predicted-class LIG evidence. | VERIFIED |
| E09 | Human amendment | `evidence/04_human_review/E09_amended_completed.png` | Human reviewer replacing an AI recommendation with another valid frozen ICD-10 category. | VERIFIED |
| E10 | Operational audit history | `evidence/05_audit/E10_audit_history.png` | Ordered operational events for a coding case. | VERIFIED |
| E11 | Audit integrity | `evidence/05_audit/E11_audit_integrity_pass.png` | Successful verification of the tamper-evident audit hash chain. | VERIFIED |
| E12 | Working-build provenance | `evidence/06_provenance/E12_manifest_sha256_verified.png` | Successful SHA-256 verification of the frozen working-build manifest. | VERIFIED |

---

# Non-Visual Evidence Register

| Evidence | Location | Purpose | Status |
|---|---|---|---|
| Full pytest output | `evidence/01_verification/pytest_full_results.txt` | Detailed automated implementation verification. | AVAILABLE |
| Final pytest summary | `evidence/01_verification/pytest_final_summary.txt` | Concise final automated verification result. | AVAILABLE |
| Project verifier | `evidence/01_verification/project_verification.txt` | End-to-end project verification. | AVAILABLE |
| Frozen scientific contract | `evidence/01_verification/frozen_scientific_contract.txt` | Human-readable frozen runtime configuration. | AVAILABLE |
| Original source provenance | `evidence/06_provenance/source_artifact_hashes.json` | Source research artefact provenance. | AVAILABLE |
| Working-build manifest | `evidence/06_provenance/working_artifact_manifest.json` | Frozen working implementation fingerprint. | AVAILABLE |
| Working-build checksum | `evidence/06_provenance/working_artifact_manifest.sha256` | SHA-256 checksum for the working manifest. | AVAILABLE |
| Manifest verification | `evidence/06_provenance/manifest_verification.txt` | Recorded successful SHA-256 verification. | AVAILABLE |

---

# Dissertation Mapping

| Evidence area | Recommended location |
|---|---|
| Scientific scope | Chapter 3 — Methodology |
| Dataset/task contract | Chapter 3 — Methodology |
| Frozen model | Chapters 3 and 4 |
| Calibration methodology | Chapter 3 |
| Calibration results | Chapter 5 |
| Fresh inference | Chapter 4 |
| Validation replay | Chapter 4 |
| XAI methodology | Chapter 3 |
| XAI implementation | Chapter 4 |
| XAI interpretation | Chapters 5 and 6 |
| Digital-twin state machine | Chapter 4 |
| Human review | Chapter 4 |
| Accept/Reject/Amend | Chapter 4 |
| Auditability | Chapter 4 |
| Automated software verification | Chapter 5 |
| Predictive experimental results | Chapter 5 |
| Limitations | Chapter 6 |
| Provenance | Chapter 3 / Appendix |
| Full test output | Appendix |
| Requirements traceability | Appendix |

---

# Research Question Synchronisation

The exact final Research Question and Objective identifiers must be copied from the frozen research specification.

They are intentionally not guessed in this evidence index.

Replace:

`SYNCHRONISED_FROM_RESEARCH_SPEC_V2.0.0`

only after checking the authoritative frozen research specification.

---

# Claims That Must Not Be Made From Implementation Evidence

The evidence package does not establish:

- real NHS predictive performance;
- clinical effectiveness;
- prospective coding safety;
- billing correctness;
- coder productivity improvement;
- production readiness;
- external generalisation;
- autonomous coding safety.

---

# Reviewer Navigation

Recommended repository review order:

```text
README.md
   ↓
EVIDENCE.md
   ↓
docs/final_evidence_index.md
   ↓
docs/final_implementation_record.md
   ↓
docs/final_requirements_traceability_matrix.md
   ↓
evidence/
   ↓
tests/
   ↓
src/operational_coding_twin/
   ↓
artifacts/provenance/
```

---

# Final Evidence Status

Visual evidence available: **12/12**

Non-visual evidence available: **8/8**

Evidence index status:

**COMPLETE**

---

<!-- BEGIN: FROZEN_RESEARCH_TRACEABILITY -->

# Frozen Research Governance and RQ Traceability

**Frozen research specification:** v2.0.0  
**Frozen protocol:** v2.0.1  
**Post-test governance:** v2.1.0

## Frozen Aim

> To design, implement and critically evaluate a reproducible AI-powered operational digital-twin research prototype for 50-category ICD-10 recommendation from NHS-aligned synthetic clinical text, incorporating comparative modelling, calibration, explainability, shortcut analysis and auditable human review.

## Objective → Research Question Lookup

| Objective | Research question(s) | Primary purpose |
|---|---|---|
| O1 | RQ1 | Benchmark validity, provenance, leakage/shortcut control |
| O2 | RQ2 | Controlled predictive comparators |
| O3 | RQ1; RQ2 | Robustness, predictive evaluation and failure analysis |
| O4 | RQ3; RQ4 | Calibration and explainability |
| O5 | RQ5 | Operational digital twin and human-review workflow |

## Research Question → Evidence Lookup

| RQ | Topic | Scientific evidence | Implementation/evidence | Final status |
|---|---|---|---|---|
| RQ1 | Benchmark validity and shortcut risk | BNS-CCB-2.0.0 release/audit package<br>Phase 5 shortcut/leakage artefacts<br>P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201<br>POST_TEST_GOVERNANCE_UPDATE_v2.1.0 | `evidence/01_verification/frozen_scientific_contract.txt`<br>`artifacts/provenance/source_artifact_hashes.json`<br>`docs/final_implementation_record.md` | ANSWERED_WITH_MAJOR_VALIDITY_LIMITATION |
| RQ2 | Predictive comparison | Phase 6 frozen lexical baseline<br>P7-BIOCLINICALBERT-SEED42-CANONICAL<br>P7-BIOCLINICALBERT-3SEED-ROBUSTNESS-v1<br>P9-ONESHOT-CONFIRMATORY-v201-SEED42<br>P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201 | `evidence/03_fresh_inference/E07_fresh_prediction.png`<br>`evidence/01_verification/frozen_scientific_contract.txt` | ANSWERED_NEGATIVE_RESULT |
| RQ3 | Calibration and reliability | P8B-CORRECTIVE-V201-SEED42<br>P9-ONESHOT-CONFIRMATORY-v201-SEED42<br>P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201 | `evidence/02_replay/E03_replay_prediction.png`<br>`evidence/03_fresh_inference/E07_fresh_prediction.png` | ANSWERED_H2_SUPPORTED |
| RQ4 | Explainability | P8B-CORRECTIVE-V201-SEED42<br>Deterministic validation n=100 Layer Integrated Gradients package<br>Top-10% positive-attribution masking versus 20 deterministic random-mask comparisons | `evidence/02_replay/E04_replay_xai.png`<br>`evidence/03_fresh_inference/E08_fresh_lig.png` | ANSWERED_WITH_BOUNDED_XAI_EVIDENCE |
| RQ5 | Operational digital twin | P8B-CORRECTIVE-V201-SEED42<br>P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201<br>Phase 11B operational workflow evidence | `evidence/04_human_review/E05_awaiting_human_review.png`<br>`evidence/04_human_review/E06_accepted_completed.png`<br>`evidence/04_human_review/E09_amended_completed.png`<br>`evidence/05_audit/E10_audit_history.png`<br>`evidence/05_audit/E11_audit_integrity_pass.png`<br>`evidence/01_verification/pytest_full_results.txt`<br>`evidence/01_verification/project_verification.txt` | ANSWERED_ENGINEERING_PROTOTYPE |

Full research traceability:

- `docs/final_research_traceability.md`
- `evidence/research_traceability.csv`
- `evidence/research_objectives.csv`
- `evidence/research_traceability.json`

<!-- END: FROZEN_RESEARCH_TRACEABILITY -->
