# Final Research Question and Evidence Traceability

**Document version:** 1.0.0  
**Frozen research specification:** v2.0.0  
**Frozen calibration/XAI/test protocol:** v2.0.1  
**Post-test governance status:** v2.1.0  
**Dataset:** BNS-CCB-2.0.0  
**Status:** FINAL RESEARCH TRACEABILITY

---

# 1. Governance hierarchy

The final traceability hierarchy is:

```text
Frozen Research Specification v2.0.0
        ↓
Aim + O1–O5 + RQ1–RQ5
        ↓
Frozen Protocol v2.0.1
        ↓
Phase 7B / 8B / 9 / 10 scientific evidence
        ↓
Post-Test Governance v2.1.0
        ↓
Operational implementation
        ↓
Automated verification + evidence package
        ↓
Bounded dissertation conclusions
```

Research Specification v2.0.0 remains the frozen technical research specification. Protocol v2.0.1 freezes calibration, XAI and confirmatory-test procedure without replacing the research Aim, Objectives or Research Questions.

---

# 2. Frozen Aim

> To design, implement and critically evaluate a reproducible AI-powered operational digital-twin research prototype for 50-category ICD-10 recommendation from NHS-aligned synthetic clinical text, incorporating comparative modelling, calibration, explainability, shortcut analysis and auditable human review.

---

# 3. Frozen SMART Objectives

## O1 — Freeze and validate the BNS-CCB v2 benchmark

Use the released BNS-CCB-2.0.0 modelling contract without altering its label space or supplied patient-family split. Verify dataset provenance, checksums, the 2,500-record/1,281-patient/50-category structure, the 1,750/375/375 train/validation/test allocation, and the rule that clinical_text is the only predictive feature. Preserve the test partition until the Phase 8 protocol is frozen.

## O2 — Establish controlled predictive comparators

Evaluate the implemented TF-IDF (word 1–2 grams) + balanced multinomial logistic regression baseline and the primary BioClinicalBERT 50-way sequence classifier using the same frozen BNS-CCB train/validation partitions. Preserve the seed-42 canonical BioClinicalBERT run and quantify transformer variability using the pre-declared seeds 42, 43 and 44 without using the test partition.

## O3 — Quantify predictive performance, robustness and failure modes

Report accuracy, balanced accuracy, micro-F1, macro precision/recall/F1, weighted-F1, top-3/top-5 accuracy, log loss and per-class error analysis. Report the lexical baseline even when it outperforms the transformer. Evaluate shortcut sensitivity and report mean ± sample standard deviation across the three deterministic transformer seeds once Phase 7B is executed.

## O4 — Evaluate probability reliability and explanation quality

Using the frozen seed-42 validation logits/probabilities, report uncalibrated negative log-likelihood, multiclass Brier score and Expected Calibration Error (ECE). Fit any selected post-hoc calibration method on validation data only. Generate token-level explanations for the frozen transformer and perform at least one quantitative faithfulness or stability evaluation. Calibration and XAI methods must be fixed before test access.

## O5 — Implement and verify the operational digital twin

Implement an event-driven prototype that carries a coding case through ingestion, preprocessing, prediction, ranked alternatives, calibrated confidence, explanation, human review and completion/error states. The reviewer must be able to accept, reject or amend a recommendation, and material state transitions must be recorded in an append-only audit history. Automated tests and at least one reproducible end-to-end demonstration are required.

---

# 4. Frozen Research Questions

## RQ1 — Benchmark validity and shortcut risk

To what extent does BNS-CCB-2.0.0 provide a reproducible and leakage-controlled synthetic benchmark for 50-category ICD-10 recommendation, and what synthetic shortcut risks remain after patient-family separation and text-only feature enforcement?

## RQ2 — Predictive comparison

How does BioClinicalBERT compare with the TF-IDF multinomial logistic-regression baseline for single-label 50-category ICD-10 recommendation under the same frozen BNS-CCB partitions?

## RQ3 — Calibration and reliability

How well calibrated are the frozen transformer's predicted probabilities, and can a validation-fitted post-hoc calibration method improve probability reliability without using test data for fitting or selection?

## RQ4 — Explainability

To what extent do token-level attribution methods identify model-relevant evidence for ICD-10 recommendations, and how faithful or stable are those explanations under a pre-specified perturbation/stability evaluation?

## RQ5 — Operational digital twin

Can ranked predictions, calibrated confidence, explanations and human accept/reject/amend decisions be represented in an event-driven operational digital twin with reproducible state transitions and an auditable case history?

---

# 5. Frozen Confirmatory Hypotheses

## H1 — Predictive comparison

**Null hypothesis**

On the locked BNS-CCB test partition, BioClinicalBERT does not improve the pre-declared primary predictive measure (macro-F1) over the TF-IDF logistic-regression baseline.

**Alternative hypothesis**

On the locked BNS-CCB test partition, BioClinicalBERT improves macro-F1 over the TF-IDF logistic-regression baseline.

**Final outcome:** NOT SUPPORTED

## H2 — Calibration

**Null hypothesis**

Validation-fitted post-hoc calibration does not improve probability calibration on the locked test partition.

**Alternative hypothesis**

Validation-fitted post-hoc calibration improves probability calibration on the locked test partition, evidenced by lower ECE and/or multiclass Brier score and/or NLL, while discrimination is reported separately.

**Final outcome:** SUPPORTED

---

# 6. Final Research-Question Traceability Matrix

| RQ | Objective(s) | Experiment / evaluation | Implementation evidence | Final conclusion | Status |
|---|---|---|---|---|---|
| RQ1 | O1<br>O3 | Phase 3 — benchmark construction/provenance<br>Phase 5 — leakage and shortcut analysis<br>Phase 10 — post-test failure analysis and claims freeze<br>Phase 11A — post-test governance synchronisation | `evidence/01_verification/frozen_scientific_contract.txt`<br>`artifacts/provenance/source_artifact_hashes.json`<br>`docs/final_implementation_record.md` | BNS-CCB-2.0.0 provides a reproducible frozen synthetic benchmark under the supplied patient-family split and clinical_text-only modelling contract, but the evidence also demonstrates substantial lexical/template shortcut risk. The perfect lexical-baseline test result is consistent with extreme synthetic separability. The benchmark therefore supports controlled methodological evaluation but does not establish real NHS generalisation. | ANSWERED_WITH_MAJOR_VALIDITY_LIMITATION |
| RQ2 | O2<br>O3 | Phase 6 — TF-IDF/logistic-regression baseline<br>Phase 7 — canonical BioClinicalBERT<br>Phase 7B — three-seed robustness<br>Phase 9 — one-shot confirmatory test<br>Phase 10 — post-test error analysis | `evidence/03_fresh_inference/E07_fresh_prediction.png`<br>`evidence/01_verification/frozen_scientific_contract.txt` | BioClinicalBERT did not outperform the frozen lexical baseline. On the locked one-shot test partition, the TF-IDF/logistic-regression baseline achieved macro-F1 1.000000, whereas BioClinicalBERT achieved macro-F1 0.878264. The transformer-minus-baseline difference was -0.121736 with 95% CI [-0.129076, -0.112000]. Accordingly, the transformer-superiority hypothesis was not supported. | ANSWERED_NEGATIVE_RESULT |
| RQ3 | O4 | Phase 8B-Corrective — validation-only temperature calibration<br>Phase 9 — one-shot confirmatory calibration evaluation<br>Phase 10 — final claims freeze | `evidence/02_replay/E03_replay_prediction.png`<br>`evidence/03_fresh_inference/E07_fresh_prediction.png` | Validation-fitted scalar temperature calibration substantially improved probability reliability on the locked test partition. NLL decreased from 1.421040 to 0.235008; multiclass Brier score decreased from 0.516026 to 0.122758; and 15-bin ECE decreased from 0.582506 to 0.053714. The primary calibrated-minus-raw NLL difference was -1.186032 with 95% CI [-1.257841, -1.114956]. The calibration hypothesis was therefore supported. | ANSWERED_H2_SUPPORTED |
| RQ4 | O4 | Phase 8A — XAI protocol freeze<br>Phase 8B-Corrective — LIG and quantitative faithfulness evaluation<br>Phase 11B — operational XAI integration | `evidence/02_replay/E04_replay_xai.png`<br>`evidence/03_fresh_inference/E08_fresh_lig.png` | The project implemented a pre-specified token-level explanation protocol using predicted-class Layer Integrated Gradients with 50 integration steps and a PAD-content baseline, and completed a quantitative faithfulness evaluation using targeted-token masking against deterministic random masking. This provides model-relevance and faithfulness evidence beyond visual inspection alone. | ANSWERED_WITH_BOUNDED_XAI_EVIDENCE |
| RQ5 | O5 | Phase 8B — frozen confidence/XAI inputs<br>Phase 10 — human-review claims freeze<br>Phase 11B — operational digital-twin implementation<br>Steps 15–18 — final implementation/evidence verification | `evidence/04_human_review/E05_awaiting_human_review.png`<br>`evidence/04_human_review/E06_accepted_completed.png`<br>`evidence/04_human_review/E09_amended_completed.png`<br>`evidence/05_audit/E10_audit_history.png`<br>`evidence/05_audit/E11_audit_integrity_pass.png`<br>`evidence/01_verification/pytest_full_results.txt`<br>`evidence/01_verification/project_verification.txt` | Yes, the required information can be represented in an event-driven operational research prototype. The final implementation maintains explicit coding-case state, ranked model recommendations, calibrated descriptive confidence, explanations, mandatory human review, Accept/Reject/Amend decisions, persistent case disposition and a SHA-256 chained tamper-evident audit history. | ANSWERED_ENGINEERING_PROTOTYPE |

---

# 7. Detailed RQ Evidence Chains

## RQ1 — Benchmark validity and shortcut risk

### Frozen question

To what extent does BNS-CCB-2.0.0 provide a reproducible and leakage-controlled synthetic benchmark for 50-category ICD-10 recommendation, and what synthetic shortcut risks remain after patient-family separation and text-only feature enforcement?

### Objective mapping

- O1
- O3

### Experiment / evaluation programme

- Phase 3 — benchmark construction/provenance
- Phase 5 — leakage and shortcut analysis
- Phase 10 — post-test failure analysis and claims freeze
- Phase 11A — post-test governance synchronisation

### Research-archive references

- BNS-CCB-2.0.0 release/audit package
- Phase 5 shortcut/leakage artefacts
- P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201
- POST_TEST_GOVERNANCE_UPDATE_v2.1.0

### Operational implementation

- `artifacts/model/label_mapping.json`
- `artifacts/governance/final_claims_freeze.json`
- `src/operational_coding_twin/frozen_resources.py`

### Local evidence

- `evidence/01_verification/frozen_scientific_contract.txt`
- `artifacts/provenance/source_artifact_hashes.json`
- `docs/final_implementation_record.md`

### Implementation requirements

- `OT-R01`
- `OT-R02`
- `OT-R18`
- `OT-R46`
- `OT-R49`

### Final answer

BNS-CCB-2.0.0 provides a reproducible frozen synthetic benchmark under the supplied patient-family split and clinical_text-only modelling contract, but the evidence also demonstrates substantial lexical/template shortcut risk. The perfect lexical-baseline test result is consistent with extreme synthetic separability. The benchmark therefore supports controlled methodological evaluation but does not establish real NHS generalisation.

### Claim boundary

Do not interpret benchmark reproducibility as external clinical validity. BNS-CCB remains wholly synthetic.

### Dissertation mapping

- Chapter 3 — Dataset, benchmark construction and validity controls
- Chapter 5 — Shortcut/failure analysis
- Chapter 6 — Validity limitations and NHS generalisation

**RQ status:** `ANSWERED_WITH_MAJOR_VALIDITY_LIMITATION`

---

## RQ2 — Predictive comparison

### Frozen question

How does BioClinicalBERT compare with the TF-IDF multinomial logistic-regression baseline for single-label 50-category ICD-10 recommendation under the same frozen BNS-CCB partitions?

### Objective mapping

- O2
- O3

### Experiment / evaluation programme

- Phase 6 — TF-IDF/logistic-regression baseline
- Phase 7 — canonical BioClinicalBERT
- Phase 7B — three-seed robustness
- Phase 9 — one-shot confirmatory test
- Phase 10 — post-test error analysis

### Research-archive references

- Phase 6 frozen lexical baseline
- P7-BIOCLINICALBERT-SEED42-CANONICAL
- P7-BIOCLINICALBERT-3SEED-ROBUSTNESS-v1
- P9-ONESHOT-CONFIRMATORY-v201-SEED42
- P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201

### Operational implementation

- `artifacts/model/model.safetensors`
- `artifacts/model/config.json`
- `src/operational_coding_twin/inference.py`

### Local evidence

- `evidence/03_fresh_inference/E07_fresh_prediction.png`
- `evidence/01_verification/frozen_scientific_contract.txt`

### Implementation requirements

- `OT-R01`
- `OT-R02`
- `OT-R03`
- `OT-R04`
- `OT-R05`
- `OT-R06`

### Final answer

BioClinicalBERT did not outperform the frozen lexical baseline. On the locked one-shot test partition, the TF-IDF/logistic-regression baseline achieved macro-F1 1.000000, whereas BioClinicalBERT achieved macro-F1 0.878264. The transformer-minus-baseline difference was -0.121736 with 95% CI [-0.129076, -0.112000]. Accordingly, the transformer-superiority hypothesis was not supported.

### Claim boundary

The negative result must be retained. The operational prototype must not be used to imply transformer superiority.

### Dissertation mapping

- Chapter 3 — Comparative modelling methodology
- Chapter 5 — Predictive comparison
- Chapter 6 — Interpretation of the negative result

**RQ status:** `ANSWERED_NEGATIVE_RESULT`

---

## RQ3 — Calibration and reliability

### Frozen question

How well calibrated are the frozen transformer's predicted probabilities, and can a validation-fitted post-hoc calibration method improve probability reliability without using test data for fitting or selection?

### Objective mapping

- O4

### Experiment / evaluation programme

- Phase 8B-Corrective — validation-only temperature calibration
- Phase 9 — one-shot confirmatory calibration evaluation
- Phase 10 — final claims freeze

### Research-archive references

- P8B-CORRECTIVE-V201-SEED42
- P9-ONESHOT-CONFIRMATORY-v201-SEED42
- P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201

### Operational implementation

- `artifacts/calibration/temperature_scaling.json`
- `src/operational_coding_twin/config.py`
- `src/operational_coding_twin/inference.py`

### Local evidence

- `evidence/02_replay/E03_replay_prediction.png`
- `evidence/03_fresh_inference/E07_fresh_prediction.png`

### Implementation requirements

- `OT-R07`
- `OT-R08`
- `OT-R09`
- `OT-R29`
- `OT-R30`

### Final answer

Validation-fitted scalar temperature calibration substantially improved probability reliability on the locked test partition. NLL decreased from 1.421040 to 0.235008; multiclass Brier score decreased from 0.516026 to 0.122758; and 15-bin ECE decreased from 0.582506 to 0.053714. The primary calibrated-minus-raw NLL difference was -1.186032 with 95% CI [-1.257841, -1.114956]. The calibration hypothesis was therefore supported.

### Claim boundary

Calibration improves probability reliability but does not convert confidence into a probability of clinical safety, coding correctness or billing correctness. No automatic acceptance threshold is authorised.

### Dissertation mapping

- Chapter 3 — Calibration methodology
- Chapter 5 — Calibration results
- Chapter 6 — Confidence interpretation

**RQ status:** `ANSWERED_H2_SUPPORTED`

---

## RQ4 — Explainability

### Frozen question

To what extent do token-level attribution methods identify model-relevant evidence for ICD-10 recommendations, and how faithful or stable are those explanations under a pre-specified perturbation/stability evaluation?

### Objective mapping

- O4

### Experiment / evaluation programme

- Phase 8A — XAI protocol freeze
- Phase 8B-Corrective — LIG and quantitative faithfulness evaluation
- Phase 11B — operational XAI integration

### Research-archive references

- P8B-CORRECTIVE-V201-SEED42
- Deterministic validation n=100 Layer Integrated Gradients package
- Top-10% positive-attribution masking versus 20 deterministic random-mask comparisons

### Operational implementation

- `src/operational_coding_twin/explainability.py`
- `artifacts/replay/layer_integrated_gradients_cases.csv`

### Local evidence

- `evidence/02_replay/E04_replay_xai.png`
- `evidence/03_fresh_inference/E08_fresh_lig.png`

### Implementation requirements

- `OT-R10`
- `OT-R11`
- `OT-R12`
- `OT-R13`
- `OT-R14`
- `OT-R17`

### Final answer

The project implemented a pre-specified token-level explanation protocol using predicted-class Layer Integrated Gradients with 50 integration steps and a PAD-content baseline, and completed a quantitative faithfulness evaluation using targeted-token masking against deterministic random masking. This provides model-relevance and faithfulness evidence beyond visual inspection alone.

### Claim boundary

Attribution is evidence about model behaviour. It is not causal clinical evidence and does not prove that a prediction is clinically correct.

### Dissertation mapping

- Chapter 3 — Explainability methodology
- Chapter 4 — XAI integration
- Chapter 5 — Explanation evaluation
- Chapter 6 — Explainability limitations

**RQ status:** `ANSWERED_WITH_BOUNDED_XAI_EVIDENCE`

---

## RQ5 — Operational digital twin

### Frozen question

Can ranked predictions, calibrated confidence, explanations and human accept/reject/amend decisions be represented in an event-driven operational digital twin with reproducible state transitions and an auditable case history?

### Objective mapping

- O5

### Experiment / evaluation programme

- Phase 8B — frozen confidence/XAI inputs
- Phase 10 — human-review claims freeze
- Phase 11B — operational digital-twin implementation
- Steps 15–18 — final implementation/evidence verification

### Research-archive references

- P8B-CORRECTIVE-V201-SEED42
- P10-POSTTEST-ERROR-CLAIMS-FREEZE-v201
- Phase 11B operational workflow evidence

### Operational implementation

- `src/operational_coding_twin/digital_twin.py`
- `src/operational_coding_twin/case_store.py`
- `src/operational_coding_twin/audit_log.py`
- `src/operational_coding_twin/inference.py`
- `src/operational_coding_twin/explainability.py`
- `app/streamlit_app.py`

### Local evidence

- `evidence/04_human_review/E05_awaiting_human_review.png`
- `evidence/04_human_review/E06_accepted_completed.png`
- `evidence/04_human_review/E09_amended_completed.png`
- `evidence/05_audit/E10_audit_history.png`
- `evidence/05_audit/E11_audit_integrity_pass.png`
- `evidence/01_verification/pytest_full_results.txt`
- `evidence/01_verification/project_verification.txt`

### Implementation requirements

- `OT-R19–OT-R42`
- `OT-R43–OT-R49`

### Final answer

Yes, the required information can be represented in an event-driven operational research prototype. The final implementation maintains explicit coding-case state, ranked model recommendations, calibrated descriptive confidence, explanations, mandatory human review, Accept/Reject/Amend decisions, persistent case disposition and a SHA-256 chained tamper-evident audit history.

### Claim boundary

This answers the engineering feasibility question only. It does not demonstrate real NHS deployment readiness, clinical safety, coder productivity improvement or autonomous coding suitability.

### Dissertation mapping

- Chapter 4 — Operational digital-twin architecture
- Chapter 4 — Human-review workflow
- Chapter 5 — Engineering verification
- Chapter 6 — Operational and clinical limitations

**RQ status:** `ANSWERED_ENGINEERING_PROTOTYPE`

---

# 8. Frozen Final Test Results

| Measure | Frozen result |
|---|---:|
| TF-IDF baseline accuracy | 1.0000 |
| TF-IDF baseline macro-F1 | 1.000000 |
| BioClinicalBERT accuracy | 0.9120 |
| BioClinicalBERT macro-F1 | 0.878264 |
| Transformer − baseline macro-F1 | -0.121736 |
| H1 95% CI | [-0.129076, -0.112000] |
| Raw NLL | 1.421040 |
| Calibrated NLL | 0.235008 |
| Calibrated − raw NLL | -1.186032 |
| H2 NLL 95% CI | [-1.257841, -1.114956] |
| Raw multiclass Brier | 0.516026 |
| Calibrated multiclass Brier | 0.122758 |
| Raw ECE (15 bins) | 0.582506 |
| Calibrated ECE (15 bins) | 0.053714 |
| Transformer test errors | 33 |
| Top-3 test accuracy | 1.0000 |

---

# 9. Frozen Final Claims

- **C1:** The transformer-superiority hypothesis was not supported.
- **C2:** The calibration hypothesis was supported.
- **C3:** BNS-CCB is a synthetic benchmark and is susceptible to lexical/template shortcuts.
- **C4:** The results do not establish generalisation to real NHS clinical data.
- **C5:** Model predictions require human review.

---

# 10. Final Aim Assessment

**Aim status: ACHIEVED WITH EXPLICIT SCOPE LIMITATIONS**

The assessed work has implemented the frozen comparative modelling, calibration, explainability, shortcut-analysis and auditable human-review components required by the v2.0.0 Aim.

The Aim is satisfied as a research-prototype objective. It must not be interpreted as evidence of production NHS deployment readiness or real-world clinical generalisation.

---

# 11. Dissertation Claim Rule

Every final dissertation conclusion should be traceable as:

```text
Aim
  ↓
Objective
  ↓
Research Question
  ↓
Method / Experiment
  ↓
Observed Evidence
  ↓
Implementation Evidence where applicable
  ↓
Bounded Conclusion
```

No UI screenshot should be used as evidence of predictive accuracy, and no predictive metric should be used as evidence that the operational state machine functions correctly.

---

**Final research traceability status: COMPLETE**

