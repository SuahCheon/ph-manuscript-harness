---
name: reporting-guidelines
description: >-
  Audit a public-health or medical manuscript for reporting-guideline
  completeness by routing the study to the right EQUATOR checklist (STROBE for
  observational studies, CONSORT for randomised trials, PRISMA for systematic
  reviews, TRIPOD+AI for prediction / AI models), checking each required item,
  and stamping every item PRESENT / PARTIAL / MISSING so nothing is silently
  skipped. Use this skill whenever the user is drafting, revising, or finalising
  a research manuscript, a methods section, or a results section — even if they
  do not say "check reporting" — and whenever a study design is named (cohort,
  case-control, cross-sectional, RCT, trial, systematic review, meta-analysis,
  prediction or risk model, machine-learning / AI model). A reference manager or
  a generic writing assistant does not know which checklist applies or which
  items are missing, so this skill must be consulted instead of assuming the
  manuscript is complete. Trigger on phrases like "is my methods section
  complete," "which reporting guideline applies," "did I miss anything for
  STROBE/CONSORT/PRISMA/TRIPOD," or any reporting-checklist review.
---

# Reporting Guidelines (Codex port)

Audit a public-health / medical manuscript against the *right* EQUATOR reporting
checklist, stamp every required item with its status, and surface what is still
missing.

> **Enforcement on this runtime.** This is the Codex port of the Claude Code
> skill; the *discipline* (route → run checklist → stamp) is identical. Only the
> enforcement point differs. On Claude Code a PostToolUse hook reports gaps on
> every save; Codex's hooks cannot intercept Write, so the audit is surfaced at
> the **git pre-commit boundary** by `codex/hooks/manuscript_precommit_check.py`
> (see `codex/INSTALL.md`). Crucially, the asymmetry with citation-verifier is
> preserved: **reporting NEVER blocks the commit.** A missing reporting item is
> fixable and progressive, so the gate prints the gaps (MISSING / unstamped /
> PARTIAL) and lets the commit through. Full rationale:
> `.claude/skills/reporting-guidelines/SKILL.md`.

## Core principle — check, don't block

A fabricated citation is *not fixable* (blocked at commit). A missing reporting
item is *fixable and progressive*: a methods section is incomplete for most of
its life. So reporting enforces **one notch softer** — the audit cannot be
skipped (it runs at every commit), but it annotates rather than blocks. Surface
the gap, leave the fix to the human. Same designed-deference shape, moved one
step down the enforcement spectrum.

## The checkpoint model

The *audit* is upstream work, done by the agent: (1) decide which guideline
applies, (2) run that checklist against the manuscript, (3) write the result in
as markers. The *gate* (`manuscript_precommit_check.py`) does not judge whether a
section is adequate — it reads the markers and reports the gaps. Keeping the gate
a pure marker-reader is what keeps it dependency-free and portable.

## Step 1 — Route the study to one guideline

Pick the single guideline that matches the design; do not audit against more than
one.

| Study design | Guideline | Declaration name |
|--------------|-----------|------------------|
| Observational (cohort, case-control, cross-sectional, surveillance) | **STROBE** (22 items) | `STROBE` |
| Randomised controlled trial | **CONSORT** 2010 (25 items) | `CONSORT` |
| Systematic review / meta-analysis | **PRISMA** 2020 (27 items) | `PRISMA` |
| Diagnostic / prognostic **prediction model**, including ML / AI | **TRIPOD+AI** 2024 (27 items) | `TRIPOD+AI` |

Routing hints: *cohort, case-control, cross-sectional, surveillance, registry* →
STROBE. *Randomised, allocation, trial arms* → CONSORT. *Systematic review,
meta-analysis, search strategy, screening* → PRISMA. *Prediction model, risk
score, discrimination/calibration, AUROC, machine learning, classifier* →
TRIPOD+AI.

> **Growth, not a main guideline.** STARD, RECORD, SPIRIT are added to *this same
> frame* (a new name + a new item roster), never as new skills — the same
> add-only structure borrowed from medsci's 32-guideline `check-reporting`.

## Step 2 — Run the selected checklist (condensed rosters)

Compare the manuscript against every required item; the item **IDs are the
contract** — the gate expects a stamp for every ID in the active roster.

**STROBE (22) — observational**
1 Title and abstract · 2 Background/rationale · 3 Objectives · 4 Study design ·
5 Setting · 6 Participants · 7 Variables · 8 Data sources/measurement · 9 Bias ·
10 Study size · 11 Quantitative variables · 12 Statistical methods ·
13 Participants (numbers/flow) · 14 Descriptive data · 15 Outcome data ·
16 Main results · 17 Other analyses · 18 Key results · 19 Limitations ·
20 Interpretation · 21 Generalisability · 22 Funding

**CONSORT (25) — randomised trial**
1 Title and abstract · 2 Background and objectives · 3 Trial design ·
4 Participants · 5 Interventions · 6 Outcomes · 7 Sample size ·
8 Randomisation: sequence generation · 9 Allocation concealment ·
10 Randomisation: implementation · 11 Blinding · 12 Statistical methods ·
13 Participant flow · 14 Recruitment · 15 Baseline data · 16 Numbers analysed ·
17 Outcomes and estimation · 18 Ancillary analyses · 19 Harms · 20 Limitations ·
21 Generalisability · 22 Interpretation · 23 Registration · 24 Protocol ·
25 Funding

**PRISMA (27) — systematic review / meta-analysis**
1 Title · 2 Abstract · 3 Rationale · 4 Objectives · 5 Eligibility criteria ·
6 Information sources · 7 Search strategy · 8 Selection process ·
9 Data collection process · 10 Data items · 11 Risk-of-bias assessment ·
12 Effect measures · 13 Synthesis methods · 14 Reporting-bias assessment ·
15 Certainty assessment · 16 Study selection (flow) · 17 Study characteristics ·
18 Risk of bias in studies · 19 Results of individual studies ·
20 Results of syntheses · 21 Reporting biases · 22 Certainty of evidence ·
23 Discussion · 24 Registration and protocol · 25 Support/funding ·
26 Competing interests · 27 Availability of data/code/materials

**TRIPOD+AI (27) — prediction / AI model**
1 Title · 2 Abstract · 3 Background · 4 Objectives · 5 Data sources ·
6 Participants · 7 Data preparation · 8 Outcome · 9 Predictors · 10 Sample size ·
11 Missing data · 12 Analytical methods · 13 Class imbalance · 14 Fairness ·
15 Model output · 16 Training vs evaluation · 17 Ethical approval ·
18 Open science (funding/COI/protocol/registration/data/code) ·
19 Patient & public involvement · 20 Participants (results) ·
21 Model development · 22 Model specification · 23 Model performance ·
24 Model updating · 25 Interpretation · 26 Limitations ·
27 Usability in current care

## Step 3 — Declare and stamp

Markers are HTML comments (invisible in rendered prose, found by the gate and a
human reading the source).

**One declaration**, naming the active guideline:

```
<!-- [REPORTING-GUIDELINE: TRIPOD+AI] -->
```

**One stamp per required item**, exactly one status each:

```
<!-- [TRIPOD+AI-8: PRESENT] -->
<!-- [TRIPOD+AI-13: PARTIAL] class imbalance named, not quantified -->
<!-- [TRIPOD+AI-17: MISSING] -->
```

| Status | Meaning |
|--------|---------|
| `PRESENT` | Reported adequately. |
| `PARTIAL` | Addressed but incomplete (named but not specified / not quantified). |
| `MISSING` | Required for this design and not addressed. |

Rules:

- Stamp **every** item ID in the active roster. An unstamped required item is
  read as a silently skipped check and reported as a gap, exactly like a
  `MISSING`. Completeness of the *audit* is enforced, not just of the manuscript.
- Exactly one status per ID. Token grammar is `[NAME-ID: STATUS]` — keep it
  exact. Free text after the closing bracket (a short reason) is encouraged for
  `PARTIAL` / `MISSING`.
- Do not invent content to make an item PRESENT, and do not downgrade a real gap
  to PARTIAL to quiet the audit. The honest status is the point.

## What the gate reports (and does not do)

For a manuscript carrying a declaration, the commit gate reads the declared
guideline's roster and lists every `MISSING`, every unstamped required item, and
every `PARTIAL` item — then **lets the commit through** (reporting never blocks).
A file with no `[REPORTING-GUIDELINE: …]` declaration is treated as
not-under-audit and passes silently. A declared guideline not yet in the roster
(STARD, RECORD, SPIRIT) also passes silently — do not invent an audit for it.

## Output format

Report: the routed guideline and why; a one-line tally
(`PRESENT n / PARTIAL n / MISSING n / unstamped n`); then `MISSING` and unstamped
items first (the gaps to close), then `PARTIAL`, then confirm the `PRESENT`
count.

## Scope (v1)

- **In scope:** four guidelines (STROBE, CONSORT, PRISMA, TRIPOD+AI), routing by
  design, per-item PRESENT/PARTIAL/MISSING stamping, and a commit-time report of
  MISSING / unstamped / PARTIAL items that never blocks the commit.
- **Out of scope (v2+):** STARD, RECORD, SPIRIT and other guidelines (added to
  the same frame); risk-of-bias tool integration; claim-level adequacy judgement
  of each section (the gate reads stamps, it does not grade prose).
