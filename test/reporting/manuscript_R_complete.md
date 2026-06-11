# A Neuro-Symbolic Model for AEFI Causality Triage (example manuscript)

## Abstract
We develop and internally validate a neuro-symbolic prediction model
that triages adverse events following immunisation (AEFI) by likelihood of a
causal association, combining a neural encoder over case narratives with a
symbolic layer encoding the WHO AEFI causality algorithm.

## Introduction
Passive AEFI surveillance generates more reports than expert panels can review.
We frame causal triage as a multivariable prediction task. Existing rule-only
systems [PMID-VERIFIED] miss narrative signal; pure neural models lack the
auditability that pharmacovigilance requires. The WHO AEFI causality
classification [GREY-LIT-WHO] and the Brighton Collaboration case definitions
[GREY-LIT-WHO] supply the symbolic backbone; KDCA pharmacovigilance guidance
[GREY-LIT-KDCA] frames the Korean reporting context.

## Methods
Development used national passive-surveillance reports; evaluation used a
held-out temporal split. Predictors were narrative-derived features plus
structured fields. The outcome was the expert-panel causality category. Model
performance was assessed by discrimination and calibration.

## Results
The model was developed and temporally evaluated; performance is reported with
confidence intervals.

## Discussion
The model surfaces likely-causal AEFI for expert review without replacing the
panel. We discuss limitations and the path to prospective use.

<!-- ==== Reporting compliance (TRIPOD+AI) ==== -->
<!-- [REPORTING-GUIDELINE: TRIPOD+AI] -->

<!-- [TRIPOD+AI-1: PRESENT] Title -->
<!-- [TRIPOD+AI-2: PRESENT] Abstract -->
<!-- [TRIPOD+AI-3: PRESENT] Background -->
<!-- [TRIPOD+AI-4: PRESENT] Objectives -->
<!-- [TRIPOD+AI-5: PRESENT] Data sources -->
<!-- [TRIPOD+AI-6: PRESENT] Participants -->
<!-- [TRIPOD+AI-7: PRESENT] Data preparation -->
<!-- [TRIPOD+AI-8: PRESENT] Outcome -->
<!-- [TRIPOD+AI-9: PRESENT] Predictors -->
<!-- [TRIPOD+AI-10: PRESENT] Sample size -->
<!-- [TRIPOD+AI-11: PRESENT] Missing data -->
<!-- [TRIPOD+AI-12: PRESENT] Analytical methods -->
<!-- [TRIPOD+AI-13: PRESENT] Class imbalance -->
<!-- [TRIPOD+AI-14: PRESENT] Fairness -->
<!-- [TRIPOD+AI-15: PRESENT] Model output -->
<!-- [TRIPOD+AI-16: PRESENT] Training vs evaluation -->
<!-- [TRIPOD+AI-17: PRESENT] Ethical approval -->
<!-- [TRIPOD+AI-18: PRESENT] Open science -->
<!-- [TRIPOD+AI-19: PRESENT] Patient & public involvement -->
<!-- [TRIPOD+AI-20: PRESENT] Participants (results) -->
<!-- [TRIPOD+AI-21: PRESENT] Model development -->
<!-- [TRIPOD+AI-22: PRESENT] Model specification -->
<!-- [TRIPOD+AI-23: PRESENT] Model performance -->
<!-- [TRIPOD+AI-24: PRESENT] Model updating -->
<!-- [TRIPOD+AI-25: PRESENT] Interpretation -->
<!-- [TRIPOD+AI-26: PRESENT] Limitations -->
<!-- [TRIPOD+AI-27: PRESENT] Usability in current care -->
