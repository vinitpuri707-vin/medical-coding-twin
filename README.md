# AI-Powered Operational Digital Twin for Automated Medical Coding

## Project Overview

This repository contains an MSc dissertation research prototype for an **AI-powered operational digital twin for automated medical coding**.

The project investigates how automated ICD-10 recommendation can be combined with:

- a frozen clinical transformer model;
- calibrated prediction confidence;
- explainable AI;
- explicit operational case states;
- mandatory human review;
- Accept, Reject and Amend decisions;
- persistent case storage;
- tamper-evident audit logging;
- and reproducible research governance.

The purpose of the system is not to replace professional medical coders or provide autonomous coding decisions.

Instead, it demonstrates how an AI recommendation model can operate as part of a controlled, human-in-the-loop medical-coding workflow.

---

## Research Aim

The frozen research aim is:

> To design, implement and critically evaluate a reproducible AI-powered operational digital-twin research prototype for 50-category ICD-10 recommendation from NHS-aligned synthetic clinical text, incorporating comparative modelling, calibration, explainability, shortcut analysis and auditable human review.

---

## Research Questions

The dissertation investigates five principal research questions.

### RQ1 — Benchmark Validity and Shortcut Risk

To what extent does BNS-CCB-2.0.0 provide a reproducible and leakage-controlled synthetic benchmark for 50-category ICD-10 recommendation, and what synthetic shortcut risks remain after patient-family separation and text-only feature enforcement?

### RQ2 — Predictive Comparison

How does BioClinicalBERT compare with the TF-IDF multinomial logistic-regression baseline for single-label 50-category ICD-10 recommendation under the same frozen BNS-CCB partitions?

### RQ3 — Calibration and Reliability

How well calibrated are the frozen transformer's predicted probabilities, and can a validation-fitted post-hoc calibration method improve probability reliability without using test data for fitting or selection?

### RQ4 — Explainability

To what extent do token-level attribution methods identify model-relevant evidence for ICD-10 recommendations, and how faithful or stable are those explanations under a pre-specified perturbation or stability evaluation?

### RQ5 — Operational Digital Twin

Can ranked predictions, calibrated confidence, explanations and human Accept/Reject/Amend decisions be represented in an event-driven operational digital twin with reproducible state transitions and an auditable case history?

---

# Dataset

## BNS-CCB v2.0.0

The primary assessed benchmark is **BNS-CCB v2.0.0**, an NHS-aligned synthetic clinical coding benchmark.

The frozen modelling contract contains:

- 2,500 synthetic encounters;
- 1,281 synthetic patients;
- 641 patient families;
- 50 three-character ICD-10 diagnosis categories;
- `clinical_text` as the only predictive text input;
- `target_category` as the single classification target.

The supplied family-controlled split is:

| Partition | Records |
|---|---:|
| Training | 1,750 |
| Validation | 375 |
| Test | 375 |
| **Total** | **2,500** |

The prediction problem is therefore:

```text
single-label
multiclass
50-category ICD-10 classification
```

The dataset is synthetic and may contain lexical or template-based shortcuts.

Results should therefore be interpreted as controlled benchmark evidence rather than evidence of real NHS clinical performance.

---

# Predictive Models

Two primary modelling approaches were evaluated.

## TF-IDF + Logistic Regression

The controlled lexical baseline uses:

- word unigram and bigram TF-IDF features;
- balanced multinomial logistic regression.

The baseline provides an important comparison against the higher-complexity transformer model.

## BioClinicalBERT

The primary transformer uses:

```text
emilyalsentzer/Bio_ClinicalBERT
```

The canonical frozen model is the:

```text
seed-42 BioClinicalBERT checkpoint
```

Fresh inference uses:

- maximum sequence length: 320;
- 50-way classification;
- softmax output;
- frozen model parameters;
- no runtime training;
- no runtime model selection.

---

# Final Predictive Results

The final one-shot evaluation was performed on the locked test partition.

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| TF-IDF + Logistic Regression | 1.0000 | 1.000000 |
| BioClinicalBERT | 0.9120 | 0.878264 |

The difference in macro-F1 was:

```text
BioClinicalBERT − baseline = -0.121736
```

with a 95% confidence interval of approximately:

```text
[-0.129076, -0.112000]
```

Therefore, the hypothesis that BioClinicalBERT would outperform the lexical baseline was **not supported**.

This negative result is intentionally retained.

It is not replaced by a more favourable run.

The perfect lexical-baseline result also reinforces an important limitation of the synthetic benchmark: the data may contain strong lexical or template-based shortcuts that make the classification task unusually separable.

---

# Probability Calibration

The frozen transformer uses validation-fitted scalar temperature scaling.

The frozen temperature is:

```text
T = 0.18388931380527324
```

Calibration is applied as:

```text
softmax(logits / T)
```

The calibration method was fitted on validation data only.

The locked test partition was not used to select or fit the temperature.

## Final Calibration Results

| Metric | Raw | Calibrated |
|---|---:|---:|
| Negative Log-Likelihood | 1.421040 | 0.235008 |
| Multiclass Brier Score | 0.516026 | 0.122758 |
| Expected Calibration Error | 0.582506 | 0.053714 |

The final calibration result therefore supports the conclusion that validation-fitted temperature scaling substantially improved probability reliability.

However, displayed confidence values must be interpreted as:

> Descriptive model uncertainty only.

They are **not** probabilities of:

- clinical safety;
- coding correctness;
- billing correctness;
- or appropriate autonomous coding.

No confidence threshold can bypass human review.

---

# Explainable AI

The project integrates **Layer Integrated Gradients** for token-level explanation of BioClinicalBERT predictions.

The frozen explainability protocol uses:

```text
Method:
Layer Integrated Gradients

Target:
Predicted class

Integration steps:
50

Baseline:
PAD-content baseline

Special tokens:
Preserved
```

The resulting token-level evidence is used to show which parts of the input text were most influential for a model recommendation.

For fresh synthetic cases, attribution is generated dynamically.

For deterministic validation replay, previously frozen Phase 8B attribution evidence is used.

The project also includes quantitative explanation evaluation rather than relying only on visual inspection.

## Explainability Boundary

Token attribution is interpreted as:

```text
model-behaviour evidence
```

It must not be interpreted as:

```text
causal clinical evidence
```

An explanation does not prove that the underlying recommendation is clinically correct.

---

# Operational Digital Twin

The operational component maintains an explicit digital representation of the coding-case lifecycle.

The main state model is:

```text
Ingested
    ↓
Preprocessed
    ↓
Predicted
    ↓
Explained
    ↓
Awaiting Human Review
    ↓
Accepted / Rejected / Amended
    ↓
Completed
```

An alternative terminal state is:

```text
Error
```

This means the prototype is not simply a stateless model API.

Each coding case maintains an operational state that changes as it moves through:

- data ingestion;
- preprocessing;
- AI prediction;
- confidence calibration;
- explanation generation;
- human review;
- final disposition;
- audit recording.

---

# Human-in-the-Loop Review

Human review is mandatory.

The application deliberately enforces:

```text
automatic_acceptance = false
human_review_required = true
```

Every recommendation must pass through the:

```text
Awaiting Human Review
```

state.

The reviewer can perform one of three actions.

## Accept

The reviewer accepts the model recommendation.

## Reject

The reviewer rejects the model recommendation.

## Amend

The reviewer replaces the model recommendation with another valid ICD-10 category from the frozen label space.

Human review also requires:

- reviewer identity;
- review reason.

A recommendation cannot complete directly from the prediction state.

Even an artificially high-confidence prediction must still enter human review.

---

# Auditability

Operational events are stored in an append-only audit history.

Each audit event records information such as:

- event identifier;
- UTC timestamp;
- case identifier;
- actor;
- action;
- previous state;
- new state;
- review reason;
- payload;
- previous event hash;
- current event SHA-256 hash.

Events are chained cryptographically using SHA-256.

This allows modification of historical events to be detected.

The audit mechanism is therefore described as:

```text
tamper-evident
```

It should not be described as:

```text
immutable
```

---

# Case Persistence

Operational case state is persisted locally rather than relying only on transient Streamlit session state.

Persistent runtime information includes:

- case identifiers;
- ingestion metadata;
- current workflow state;
- prediction results;
- explanations;
- reviewer decisions;
- final ICD-10 disposition;
- audit events.

The prototype uses deterministic safe filenames and atomic replacement for case persistence.

Duplicate case identifiers are prevented from silently overwriting existing cases.

---

# Application Modes

The Streamlit interface supports three primary demonstration modes.

## 1. Fresh Synthetic Clinical Note

The user can paste a new synthetic clinical note.

The workflow is:

```text
Synthetic clinical note
        ↓
Tokenisation
        ↓
Frozen BioClinicalBERT
        ↓
50 model logits
        ↓
Frozen temperature scaling
        ↓
Calibrated probabilities
        ↓
Top-1 recommendation
        ↓
Top-3 alternatives
        ↓
Layer Integrated Gradients
        ↓
Mandatory human review
        ↓
Accept / Reject / Amend
        ↓
Completed
```

---

## 2. Synthetic CSV Upload

The application can also process synthetic CSV input containing:

```text
clinical_text
```

This mode provides a convenient demonstration of the operational workflow for externally prepared synthetic cases.

No identifiable real-patient information should be uploaded.

---

## 3. Frozen Validation Replay

A deterministic subset of frozen Phase 8B validation cases can be replayed.

Replay uses stored:

- calibrated probabilities;
- model recommendations;
- validation metadata;
- Layer Integrated Gradients evidence.

Replay does **not**:

- perform a new scientific experiment;
- retrain the model;
- recalibrate the model;
- rerun model selection;
- access Phase 9 test prediction artefacts.

Replay exists to demonstrate the operational workflow reproducibly.

---

# Technology Stack

The project uses:

- Python
- PyTorch
- Hugging Face Transformers
- BioClinicalBERT
- scikit-learn
- Captum
- Streamlit
- pandas
- NumPy
- pytest
- uv
- Git
- Git LFS
- SHA-256 cryptographic manifests

---

# Repository Structure

```text
operational_coding_twin/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   └── operational_coding_twin/
│       ├── __init__.py
│       ├── config.py
│       ├── frozen_resources.py
│       ├── inference.py
│       ├── explainability.py
│       ├── digital_twin.py
│       ├── case_store.py
│       └── audit_log.py
│
├── artifacts/
│   ├── model/
│   │   ├── model.safetensors
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   ├── tokenizer_config.json
│   │   └── label_mapping.json
│   │
│   ├── calibration/
│   │   └── temperature_scaling.json
│   │
│   ├── replay/
│   │   ├── deterministic_validation_sample_100.csv
│   │   ├── validation_calibrated_probabilities.npy
│   │   └── layer_integrated_gradients_cases.csv
│   │
│   ├── governance/
│   │   └── final_claims_freeze.json
│   │
│   └── provenance/
│
├── runtime/
│   ├── cases/
│   ├── explanations/
│   ├── audit/
│   └── errors/
│
├── tests/
│   ├── test_foundation.py
│   ├── test_frozen_resources.py
│   ├── test_inference.py
│   ├── test_explainability.py
│   ├── test_digital_twin.py
│   └── test_governance.py
│
├── scripts/
│
├── docs/
│
├── evidence/
│
├── EVIDENCE.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

---

# Installation

## Requirements

The project requires:

- Python;
- Git;
- Git LFS;
- uv.

Clone the repository:

```bash
git clone https://github.com/vinitpuri707-vin/medical-coding-twin.git
```

Enter the repository:

```bash
cd medical-coding-twin
```

Install Git LFS:

```bash
git lfs install
```

Pull LFS-managed files:

```bash
git lfs pull
```

Install Python dependencies:

```bash
uv sync
```

---

# Running the Application Locally

Start the Streamlit application with:

```bash
uv run streamlit run app/streamlit_app.py
```

Streamlit should provide a local URL similar to:

```text
http://localhost:8501
```

---

# Running Automated Tests

Run the complete test suite:

```bash
uv run pytest tests -v
```

The test suite verifies areas including:

- configuration loading;
- frozen resource loading;
- 50-category label contract;
- fresh model inference;
- frozen replay;
- temperature calibration;
- Layer Integrated Gradients;
- 50-step attribution;
- state-machine transitions;
- mandatory human review;
- Accept workflow;
- Reject workflow;
- Amend workflow;
- duplicate protection;
- case persistence;
- audit chaining;
- tamper detection;
- governance boundaries;
- Phase 9 runtime isolation.

---

# Project Verification

Run the project-level verifier:

```bash
uv run python scripts/verify_project.py
```

This performs an end-to-end verification of the frozen operational implementation.

---

# Evidence and Traceability

The repository contains several complementary traceability systems.

## Requirements Traceability Matrix

```text
docs/final_requirements_traceability_matrix.md
```

This document provides requirement-first traceability across:

```text
OT-R01
...
OT-R50
```

Each requirement is mapped to:

- implementation;
- verification;
- evidence;
- completion status.

---

## Final Evidence Index

```text
docs/final_evidence_index.md
```

This is the primary topic-first evidence lookup.

It allows a reviewer to locate supporting material for topics such as:

- model inference;
- calibration;
- explainability;
- validation replay;
- mandatory human review;
- Accept/Reject/Amend;
- case persistence;
- auditability;
- provenance;
- reproducibility.

---

## Research Traceability

```text
docs/final_research_traceability.md
```

This connects:

```text
Research Aim
    ↓
Objectives
    ↓
Research Questions
    ↓
Experiments
    ↓
Scientific Results
    ↓
Implementation Evidence
    ↓
Bounded Dissertation Claims
```

---

## Dissertation Evidence Map

```text
docs/final_dissertation_evidence_map.md
```

This maps each research question and evidence item to its intended dissertation chapter.

---

# Evidence Package

The repository contains a structured evidence directory.

```text
evidence/
├── 01_verification/
├── 02_replay/
├── 03_fresh_inference/
├── 04_human_review/
├── 05_audit/
└── 06_provenance/
```

Visual evidence includes:

```text
E01 — application scope
E02 — replay case selected
E03 — replay prediction
E04 — replay XAI
E05 — awaiting human review
E06 — accepted and completed
E07 — fresh inference
E08 — fresh LIG
E09 — amended and completed
E10 — audit history
E11 — audit integrity
E12 — manifest SHA-256 verification
```

---

# Reproducibility

The final implementation and evidence package use cryptographic provenance.

## Working Build Manifest

```text
artifacts/provenance/working_artifact_manifest.json
```

This fingerprints the frozen working implementation.

## Evidence Manifest

```text
evidence/evidence_manifest.json
evidence/evidence_manifest.sha256
```

This separately fingerprints the final evidence package.

The separation preserves the distinction between:

```text
scientific / implementation freeze
```

and:

```text
final dissertation evidence package
```

---

# Git LFS

The frozen BioClinicalBERT model checkpoint is approximately several hundred megabytes and exceeds GitHub's normal 100 MB file limit.

The model is therefore managed using **Git Large File Storage**.

The tracked model path is:

```text
artifacts/model/model.safetensors
```

After cloning the repository, run:

```bash
git lfs install
git lfs pull
```

Verify that the model is available with:

```bash
git lfs ls-files
```

---

# Deployment

The application entry point is:

```text
app/streamlit_app.py
```

For Streamlit Community Cloud, configure:

```text
Repository:
vinitpuri707-vin/medical-coding-twin

Branch:
main

Main file:
app/streamlit_app.py
```

The deployed environment must have access to the frozen model artefacts and required Python dependencies.

---

# Research Governance

The prototype follows a frozen research protocol.

Key governance rules include:

```text
No runtime retraining
No runtime recalibration
No runtime model selection
No Phase 9 test prediction access
No confidence-based auto-acceptance
Mandatory human review
Synthetic/demo inputs only
```

The application therefore separates:

```text
scientific experimentation
```

from:

```text
operational demonstration
```

---

# Important Scientific Findings

The main findings of the project include:

1. The lexical TF-IDF/logistic-regression baseline achieved stronger predictive performance than BioClinicalBERT on the frozen synthetic benchmark.

2. The hypothesis that the transformer would outperform the lexical baseline was not supported.

3. Validation-fitted temperature scaling substantially improved probability reliability.

4. Layer Integrated Gradients provided token-level evidence about model behaviour.

5. The synthetic benchmark exhibited strong shortcut susceptibility.

6. Ranked predictions, calibrated confidence, XAI, persistent operational state, mandatory human review and tamper-evident auditability could be integrated into a reproducible prototype.

7. None of these findings establish generalisation to genuine NHS clinical data.

---

# Project Contribution

The principal contribution of the project is not simply another medical-text classifier.

The project integrates:

```text
predictive modelling
        +
probability calibration
        +
explainable AI
        +
explicit operational state
        +
mandatory human review
        +
case persistence
        +
tamper-evident auditability
        +
research provenance
```

within one controlled operational research prototype.

The digital-twin component represents the operational lifecycle of a coding case rather than merely exposing a model prediction endpoint.

---

# Limitations

The project has several important limitations.

## Synthetic Dataset

The primary benchmark is synthetic.

This limits the extent to which model behaviour can be generalised to genuine NHS clinical documentation.

## Shortcut Susceptibility

The strong lexical baseline indicates that the synthetic dataset may contain substantial lexical or template-based shortcuts.

## No Real NHS External Validation

The final predictive evaluation does not use genuine identifiable NHS clinical text.

Therefore, real NHS predictive performance is not claimed.

## Explainability Limitation

Token attribution indicates which model inputs influenced a prediction.

It does not demonstrate causal clinical reasoning.

## Human-Factors Evaluation

Although human review is implemented structurally, the project does not include a formal prospective study of professional medical coders.

Therefore, improvements in:

- coder efficiency;
- coder accuracy;
- workload;
- usability;
- clinical workflow performance

are not claimed.

## Deployment Limitation

The implementation is a research prototype rather than a production clinical system.

It has not undergone:

- NHS production security assessment;
- clinical safety certification;
- medical-device conformity assessment;
- large-scale performance testing;
- production EHR integration.

---

# Safety and Intended Use

This software is intended for:

```text
research
education
demonstration
controlled synthetic-data evaluation
```

It is not intended for:

```text
clinical diagnosis
treatment decisions
autonomous medical coding
billing decisions
real-patient decision support
production NHS deployment
```

Human review is required for every recommendation.

---

# Data Privacy

Only synthetic or appropriately approved demonstration data should be entered into the prototype.

Do not upload:

- patient names;
- NHS numbers;
- addresses;
- dates of birth;
- identifiable clinical records;
- or other real patient-identifiable information.

---

# Dissertation Context

This repository supports an MSc dissertation investigating the design and evaluation of an AI-powered operational digital twin for automated medical coding.

The dissertation evaluates:

- benchmark validity;
- lexical shortcut risk;
- classical machine learning;
- transformer-based coding;
- calibration;
- uncertainty;
- explainability;
- human review;
- operational-state modelling;
- auditability;
- reproducibility;
- and limitations of synthetic clinical data.

---

# Final Interpretation

The project demonstrates that an automated medical-coding model can be embedded within a structured operational workflow containing calibrated confidence, explainability, explicit state transitions, mandatory human decision-making and auditable case history.

However, the scientific evidence also shows that model complexity does not automatically imply better predictive performance.

The strong lexical baseline and synthetic-data shortcut risks require conservative interpretation.

Accordingly, the prototype should be viewed as:

> A reproducible engineering and research demonstration of human-supervised AI medical-coding workflow integration.

It should not be viewed as:

> A clinically validated autonomous NHS medical-coding system.

---

# Disclaimer

This repository contains an academic research prototype.

The software must not be used for real-world clinical diagnosis, treatment, autonomous medical coding, reimbursement decisions or production healthcare deployment.

All predictions, probabilities and explanations produced by the prototype require human interpretation and review.