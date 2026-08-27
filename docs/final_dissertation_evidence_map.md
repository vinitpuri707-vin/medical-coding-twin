# Final Dissertation Evidence Map

**Document version:** 1.0.0  
**Purpose:** Map frozen research evidence and operational implementation evidence into the final dissertation.  
**Status:** FINAL WRITING TRACEABILITY

---

# 1. Frozen Aim

> To design, implement and critically evaluate a reproducible AI-powered operational digital-twin research prototype for 50-category ICD-10 recommendation from NHS-aligned synthetic clinical text, incorporating comparative modelling, calibration, explainability, shortcut analysis and auditable human review.

---

# 2. Chapter Contract

| Chapter | Title | Evidence function |
|---|---|---|
| 1 | Introduction | Define the research problem, aim, objectives, research questions, contribution and dissertation scope. |
| 2 | Critical Literature Review | Critically position automated ICD coding, transformers, calibration, explainability, synthetic data and operational digital twins. |
| 3 | Methodology | Describe the frozen benchmark, leakage controls, comparative modelling, calibration, XAI, confirmatory evaluation and reproducibility protocol. |
| 4 | System Design and Implementation | Describe implementation of frozen inference, calibration, XAI, state transitions, human review, persistence and tamper-evident auditability. |
| 5 | Evaluation and Results | Report predictive, calibration, XAI, error-analysis and engineering-verification evidence. |
| 6 | Discussion | Answer RQ1-RQ5 critically and interpret negative, positive and bounded findings. |
| 7 | Conclusion and Future Work | Summarise what was established, what was not established and what future NHS validation requires. |

---

# 3. RQ → Experiment → Evidence → Claim Map

| RQ | Methodology | Results | Discussion | Primary conclusion |
|---|---|---|---|---|
| RQ1 | Ch. 3: Benchmark construction, provenance, family-controlled splitting and leakage/shortcut controls | Ch. 5: Benchmark validity, shortcut audit and failure analysis | Ch. 6: Synthetic benchmark validity and external-validity limits | BNS-CCB provides a reproducible controlled synthetic benchmark, but substantial lexical/template shortcut risk limits external validity. |
| RQ2 | Ch. 3: TF-IDF logistic-regression baseline and frozen BioClinicalBERT comparative protocol | Ch. 5: Predictive comparison and three-seed transformer robustness | Ch. 6: Interpretation of the unsupported transformer-superiority hypothesis | BioClinicalBERT did not outperform the controlled TF-IDF/logistic-regression baseline on the locked test partition. |
| RQ3 | Ch. 3: Validation-only scalar temperature calibration | Ch. 5: Raw versus calibrated NLL, Brier score and ECE | Ch. 6: Probability reliability and limits of confidence | Validation-fitted scalar temperature scaling substantially improved probability reliability. |
| RQ4 | Ch. 3: Predicted-class Layer Integrated Gradients and quantitative faithfulness evaluation | Ch. 5: Token-attribution and targeted-versus-random masking evidence | Ch. 6: Explanation usefulness, faithfulness and interpretability limits | The prototype provides pre-specified token-level model-relevance evidence with quantitative faithfulness evaluation. |
| RQ5 | Ch. 3: Operational digital-twin state, human-review and auditability design | Ch. 5: Engineering verification and deterministic end-to-end workflow demonstration | Ch. 6: Operational feasibility, governance and deployment limitations | Ranked predictions, calibrated confidence, XAI, mandatory human decisions, persistent state and tamper-evident audit history can be integrated in an event-driven operational research prototype. |

---

# RQ1 — Benchmark validity and shortcut risk

## Frozen question

To what extent does BNS-CCB-2.0.0 provide a reproducible and leakage-controlled synthetic benchmark for 50-category ICD-10 recommendation, and what synthetic shortcut risks remain after patient-family separation and text-only feature enforcement?

## Scientific evidence

- BNS-CCB-2.0.0 release/audit evidence
- Phase 5 shortcut/leakage analysis
- Phase 10 post-test error/claims freeze

## Implementation / repository evidence

- `evidence/01_verification/frozen_scientific_contract.txt`
- `artifacts/provenance/source_artifact_hashes.json`
- `docs/final_implementation_record.md`

## Dissertation placement

- Chapter 3: Benchmark construction, provenance, family-controlled splitting and leakage/shortcut controls
- Chapter 5: Benchmark validity, shortcut audit and failure analysis
- Chapter 6: Synthetic benchmark validity and external-validity limits

## Final bounded claim

BNS-CCB provides a reproducible controlled synthetic benchmark, but substantial lexical/template shortcut risk limits external validity.

## Boundary

Do not claim real NHS generalisation from BNS-CCB.

---

# RQ2 — Predictive comparison

## Frozen question

How does BioClinicalBERT compare with the TF-IDF multinomial logistic-regression baseline for single-label 50-category ICD-10 recommendation under the same frozen BNS-CCB partitions?

## Scientific evidence

- Phase 6 lexical baseline
- Phase 7 canonical BioClinicalBERT
- Phase 7B seeds 42/43/44
- Phase 9 one-shot test
- Phase 10 error analysis

## Implementation / repository evidence

- `artifacts/model/model.safetensors`
- `evidence/03_fresh_inference/E07_fresh_prediction.png`

## Dissertation placement

- Chapter 3: TF-IDF logistic-regression baseline and frozen BioClinicalBERT comparative protocol
- Chapter 5: Predictive comparison and three-seed transformer robustness
- Chapter 6: Interpretation of the unsupported transformer-superiority hypothesis

## Final bounded claim

BioClinicalBERT did not outperform the controlled TF-IDF/logistic-regression baseline on the locked test partition.

## Boundary

The operational prototype must not be used to imply transformer superiority.

---

# RQ3 — Calibration and reliability

## Frozen question

How well calibrated are the frozen transformer's predicted probabilities, and can a validation-fitted post-hoc calibration method improve probability reliability without using test data for fitting or selection?

## Scientific evidence

- Phase 8B validation-fitted temperature scaling
- Phase 9 locked-test calibration evaluation

## Implementation / repository evidence

- `artifacts/calibration/temperature_scaling.json`
- `evidence/02_replay/E03_replay_prediction.png`
- `evidence/03_fresh_inference/E07_fresh_prediction.png`

## Dissertation placement

- Chapter 3: Validation-only scalar temperature calibration
- Chapter 5: Raw versus calibrated NLL, Brier score and ECE
- Chapter 6: Probability reliability and limits of confidence

## Final bounded claim

Validation-fitted scalar temperature scaling substantially improved probability reliability.

## Boundary

Calibrated confidence is not a probability of clinical safety, coding correctness or billing correctness.

---

# RQ4 — Explainability

## Frozen question

To what extent do token-level attribution methods identify model-relevant evidence for ICD-10 recommendations, and how faithful or stable are those explanations under a pre-specified perturbation/stability evaluation?

## Scientific evidence

- Phase 8A XAI protocol freeze
- Phase 8B deterministic validation XAI
- Phase 8B quantitative faithfulness evaluation

## Implementation / repository evidence

- `artifacts/replay/layer_integrated_gradients_cases.csv`
- `evidence/02_replay/E04_replay_xai.png`
- `evidence/03_fresh_inference/E08_fresh_lig.png`

## Dissertation placement

- Chapter 3: Predicted-class Layer Integrated Gradients and quantitative faithfulness evaluation
- Chapter 5: Token-attribution and targeted-versus-random masking evidence
- Chapter 6: Explanation usefulness, faithfulness and interpretability limits

## Final bounded claim

The prototype provides pre-specified token-level model-relevance evidence with quantitative faithfulness evaluation.

## Boundary

Token attribution is model-behaviour evidence, not causal clinical evidence.

---

# RQ5 — Operational digital twin

## Frozen question

Can ranked predictions, calibrated confidence, explanations and human accept/reject/amend decisions be represented in an event-driven operational digital twin with reproducible state transitions and an auditable case history?

## Scientific evidence

- Phase 11B operational digital-twin implementation
- Final automated software verification
- Final deterministic demonstration

## Implementation / repository evidence

- `evidence/04_human_review/E05_awaiting_human_review.png`
- `evidence/04_human_review/E06_accepted_completed.png`
- `evidence/04_human_review/E09_amended_completed.png`
- `evidence/05_audit/E10_audit_history.png`
- `evidence/05_audit/E11_audit_integrity_pass.png`
- `evidence/01_verification/pytest_full_results.txt`

## Dissertation placement

- Chapter 3: Operational digital-twin state, human-review and auditability design
- Chapter 5: Engineering verification and deterministic end-to-end workflow demonstration
- Chapter 6: Operational feasibility, governance and deployment limitations

## Final bounded claim

Ranked predictions, calibrated confidence, XAI, mandatory human decisions, persistent state and tamper-evident audit history can be integrated in an event-driven operational research prototype.

## Boundary

This establishes engineering feasibility, not NHS deployment readiness or clinical safety.

---

# Visual Evidence Placement

| ID | Repository file | Dissertation use | Role | Recommended caption | Status |
|---|---|---|---|---|---|
| E01 | `evidence/02_replay/E01_application_scope.png` | Chapter 4 | Main figure | Research-scope and governance boundary of the operational coding-twin prototype. | VERIFIED |
| E02 | `evidence/02_replay/E02_replay_case_selected.png` | Appendix | Supporting figure | Selection of a deterministic frozen Phase 8B validation replay case. | VERIFIED |
| E03 | `evidence/02_replay/E03_replay_prediction.png` | Chapter 4 | Main figure | Frozen validation replay showing Top-1/Top-3 recommendations and calibrated descriptive confidence. | VERIFIED |
| E04 | `evidence/02_replay/E04_replay_xai.png` | Chapter 4 | Main figure | Frozen Layer Integrated Gradients evidence integrated into the operational workflow. | VERIFIED |
| E05 | `evidence/04_human_review/E05_awaiting_human_review.png` | Chapter 4 | Main figure | Mandatory Awaiting Human Review state separating AI recommendation from final coding disposition. | VERIFIED |
| E06 | `evidence/04_human_review/E06_accepted_completed.png` | Appendix | Supporting figure | Human acceptance followed by explicit case completion. | VERIFIED |
| E07 | `evidence/03_fresh_inference/E07_fresh_prediction.png` | Chapter 4 | Main figure | Fresh synthetic-note inference using the frozen canonical BioClinicalBERT model. | VERIFIED |
| E08 | `evidence/03_fresh_inference/E08_fresh_lig.png` | Chapter 4 | Main figure | Fresh 50-step predicted-class Layer Integrated Gradients explanation. | VERIFIED |
| E09 | `evidence/04_human_review/E09_amended_completed.png` | Chapter 4 | Main figure | Human amendment demonstrating reviewer authority over the AI-generated coding recommendation. | VERIFIED |
| E10 | `evidence/05_audit/E10_audit_history.png` | Chapter 4 | Main figure | Ordered operational audit history for a coding case. | VERIFIED |
| E11 | `evidence/05_audit/E11_audit_integrity_pass.png` | Appendix | Supporting verification | Successful verification of the SHA-256 chained tamper-evident audit history. | VERIFIED |
| E12 | `evidence/06_provenance/E12_manifest_sha256_verified.png` | Appendix | Reproducibility evidence | Successful SHA-256 verification of the frozen evidence-package manifest. | VERIFIED |

---

# Recommended Results Tables

| ID | Location | Proposed title | Scientific evidence | Required content |
|---|---|---|---|---|
| T5-1 | Chapter 5 | Final predictive comparison on the locked test partition | Phase 9 one-shot confirmatory results | Baseline and BioClinicalBERT accuracy, macro-F1, difference and confidence interval |
| T5-2 | Chapter 5 | BioClinicalBERT three-seed validation robustness | Phase 7B seeds 42/43/44 | Mean ± sample SD for frozen validation metrics |
| T5-3 | Chapter 5 | Raw versus calibrated probability-reliability metrics | Phase 8B and Phase 9 | NLL, multiclass Brier score and ECE before/after temperature scaling |
| T5-4 | Chapter 5 | Transformer error analysis and common confusion patterns | Phase 10 | Error count, confusion pairs, support and lowest-performing categories |
| T5-5 | Chapter 5 | Explainability faithfulness evaluation | Phase 8B | Targeted attribution masking versus deterministic random masking |
| T5-6 | Chapter 5 | Operational implementation verification | Final pytest and project-verifier evidence | Verified inference, XAI, state, review, persistence, audit and governance requirements |

---

# Main-text versus Appendix Rule

Main-text figures should be retained only when they directly support the research argument.

Recommended main-text operational figures:

- E01 — system/research boundary;
- E03 — ranked calibrated prediction;
- E04 — frozen XAI integration;
- E05 — mandatory human-review gate;
- E07 — fresh frozen-model inference;
- E08 — fresh LIG;
- E09 — human amendment;
- E10 — audit history.

Recommended appendix figures:

- E02 — replay-case selection;
- E06 — accepted-case completion;
- E11 — audit-integrity verification;
- E12 — evidence-manifest verification.

---

# Evidence Interpretation Rules

1. Predictive accuracy/F1 claims must come from frozen experimental metrics, not screenshots.

2. Workflow-functionality claims should be supported by source code, automated tests and operational evidence.

3. Calibration should be described as probability-reliability improvement, not clinical correctness.

4. XAI should be described as model-behaviour evidence, not causal clinical evidence.

5. The unsupported transformer-superiority result must be reported explicitly.

6. Synthetic benchmark limitations must remain visible in Results, Discussion and Conclusion.

7. Human review remains mandatory throughout the operational interpretation.

---

# Final Dissertation Claim Chain

```text
Frozen Aim
   ↓
O1–O5
   ↓
RQ1–RQ5
   ↓
Method / Experiment
   ↓
Scientific Result
   ↓
Operational Evidence where applicable
   ↓
Bounded Discussion Claim
   ↓
Conclusion
```

---

**Dissertation evidence-map status: COMPLETE**
