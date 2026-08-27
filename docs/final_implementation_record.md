# Final Operational Coding Twin — Implementation Record

**Document version:** 1.0.0  
**Project:** AI-Powered Operational Digital Twin for Automated Medical Coding  
**Implementation status:** Frozen working prototype  
**Runtime scope:** Synthetic/demo data and frozen validation replay only  

---

## 1. Purpose

This document records the final implemented architecture of the operational
digital-twin prototype.

The prototype integrates a frozen medical-coding classifier, calibrated
confidence, explainability evidence, an explicit operational state machine,
mandatory human review, persistent case state, and a tamper-evident audit
trail.

The implementation is a research prototype.

It is not presented as:

- a clinically validated coding system;
- an autonomous coding system;
- a replacement for professional coding review;
- a billing-authorisation system;
- evidence of real NHS deployment performance.

---

## 2. Final System Boundary

The operational prototype supports three input modes:

1. New synthetic clinical note.
2. Synthetic CSV record containing `clinical_text`.
3. Frozen Phase 8B deterministic validation replay.

The application does not intentionally accept identifiable real-patient
information.

The Phase 9 test partition is not part of the operational runtime.

No model training, model selection, threshold optimisation or calibration
fitting occurs inside the application.

---

## 3. Frozen Scientific Contract

### 3.1 Model

Canonical runtime model:

`P7-BIOCLINICALBERT-SEED42-CANONICAL`

Architecture:

`BertForSequenceClassification`

Base model:

`emilyalsentzer/Bio_ClinicalBERT`

Prediction setting:

`single-label multiclass`

Number of output categories:

`50`

Maximum token length:

`320`

The application loads the frozen model in evaluation mode.

No model parameters are updated during runtime.

---

## 3.2 Label Space

The operational application uses the frozen 50-category ICD-10 label mapping.

Runtime mapping files:

- `artifacts/model/label_mapping.json`
- model configuration associated with the canonical seed-42 checkpoint.

The classifier must return exactly one predicted class from the frozen
50-category space.

The user interface additionally displays the highest-ranked three categories
as a reviewer shortlist.

---

## 3.3 Calibration

Calibration method:

`single scalar temperature scaling`

Frozen temperature:

`0.18388931380527324`

Operational transformation:

`softmax(logits / T)`

Calibration fitting partition:

`validation`

Calibration fitting examples:

`375`

Test partition used during calibration fitting:

`No`

Prediction classes changed by calibration:

`0`

Runtime artefact:

`artifacts/calibration/temperature_scaling.json`

The calibrated Top-1 probability is displayed as descriptive model
uncertainty.

It must not be interpreted as a probability of:

- clinical safety;
- coding correctness;
- billing correctness.

Calibration does not create an automatic acceptance threshold.

---

## 3.4 Explainability

Fresh synthetic-case explainability method:

`Layer Integrated Gradients`

Integration steps:

`50`

Target:

`Predicted model class`

Baseline:

`PAD-content baseline with special tokens preserved`

Fresh explainability is calculated against the frozen BioClinicalBERT model.

Frozen validation replay does not recalculate attribution.

Replay mode instead uses the saved Phase 8B explanation artefact:

`artifacts/replay/layer_integrated_gradients_cases.csv`

Explainability output is interpreted as model-behaviour evidence.

It is not presented as causal clinical evidence.

---

# 4. Operational Architecture

The final system architecture is:

```text
                    INPUT / SIMULATION LAYER
                ┌────────────┬───────────────┐
                │            │               │
          Synthetic note   Synthetic CSV   Frozen replay
                │            │               │
                └────────────┴───────────────┘
                             │
                             ▼
                       CASE INGESTION
                             │
                             ▼
                    OPERATIONAL TWIN STATE
                             │
                             ▼
                       PREPROCESSING
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        Fresh synthetic case        Validation replay
                │                         │
                ▼                         ▼
        Frozen BioClinicalBERT      Frozen probability
             inference                   matrix
                │                         │
                ▼                         │
        Temperature scaling               │
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                    TOP-1 / TOP-3 OUTPUT
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
          Fresh 50-step LIG       Frozen Phase 8B LIG
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                    HUMAN REVIEW GATE
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
             Accept        Reject       Amend
                │            │            │
                └────────────┼────────────┘
                             │
                             ▼
                         COMPLETED
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
            CASE PERSISTENCE      AUDIT HASH CHAIN