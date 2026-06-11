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
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        # Checkpoint, not auditor. The audit (which guideline applies, whether
        # each item is addressed) happens upstream: Claude runs the checklist
        # against the manuscript and writes a [REPORTING-GUIDELINE: NAME]
        # declaration plus one [NAME-ID: STATUS] stamp per item into the text.
        # This hook fires AFTER the save, reads only those markers, and reports
        # any item that is MISSING, PARTIAL, or never stamped. It does not — and
        # at PostToolUse cannot — undo the write: the save stands and the audit
        # is surfaced as feedback. That is the point. citation-verifier blocks a
        # proven-wrong citation before it lands (PreToolUse, deny); a missing
        # reporting item is fixable and progressive, so its enforcement is one
        # notch softer: the check cannot be skipped, but it annotates instead of
        # blocking. Same discipline/enforcement split, bundled in one
        # git-deployable directory an MCP server cannot carry.
        - type: command
          # Exec form (args) avoids shell quoting. CLAUDE_PROJECT_DIR is the
          # documented, reliably-substituted placeholder; CLAUDE_SKILL_DIR is
          # avoided because its substitution is currently unreliable.
          # On Windows the interpreter is usually "python"; on macOS / Linux it
          # is "python3". Match the interpreter that exists on the target machine
          # (this repo's citation-verifier install uses "python").
          command: "python"
          args:
            - "${CLAUDE_PROJECT_DIR}/.claude/skills/reporting-guidelines/scripts/post_write_reporting_check.py"
          timeout: 10
          statusMessage: "Reporting audit: checking checklist completeness…"
---

# Reporting Guidelines

Audit a public-health / medical manuscript against the *right* EQUATOR reporting
checklist, stamp every required item with its status, and surface what is still
missing — automatically, on every save, without the writer having to ask.

## Core principle — check, don't block

This is the sibling of `citation-verifier`, and the difference between them is
deliberate. A fabricated citation is *not fixable*: it is wrong the moment it
lands, and trust is damaged immediately, so it is **blocked before writing**
(PreToolUse · deny). A missing reporting item is *fixable and progressive*: a
methods section is incomplete for most of its life and gets completed over many
edits. Blocking a save because STROBE item 12 is not yet written would stop the
author from writing at all. So reporting enforces **one notch softer**:

> The audit cannot be skipped, but it annotates rather than blocks.

The manuscript is always saved. After the save, the skill reports which items
are PRESENT, which are PARTIAL, and which are MISSING. The enforcement is that
this report is **not optional** — the user does not have to say "check
reporting"; it runs on every manuscript save and the missing items are named.
This is the same designed-deference shape as citation-verifier, moved one step
down the enforcement spectrum: surface the gap, leave the fix to the human.

## The checkpoint model (same division of labour as citation-verifier)

The *audit* is upstream work, done here by Claude:

1. decide which guideline applies (routing, Step 1),
2. run that guideline's checklist against the manuscript (Step 2),
3. write the result into the manuscript as markers (Step 3).

The *hook* (`scripts/post_write_reporting_check.py`) does **not** judge whether a
section is adequate. It fires after the save, reads the markers, and reports the
gaps. The judgement lives in the discipline below; the hook only enforces that
the judgement was recorded and surfaces what is incomplete. Keeping the hook a
pure marker-reader is what keeps it dependency-free and portable, exactly as in
citation-verifier.

## Step 1 — Route the study to one guideline

Identify the study design, then select the single guideline that matches. Do not
audit against more than one; pick the one that fits the design.

| Study design | Guideline | Declaration name |
|--------------|-----------|------------------|
| Observational (cohort, case-control, cross-sectional, surveillance) | **STROBE** (22 items) | `STROBE` |
| Randomised controlled trial | **CONSORT** 2010 (25 items) | `CONSORT` |
| Systematic review / meta-analysis | **PRISMA** 2020 (27 items) | `PRISMA` |
| Diagnostic / prognostic **prediction model**, including ML / AI | **TRIPOD+AI** 2024 (27 items) | `TRIPOD+AI` |

Routing hints: words like *cohort, case-control, cross-sectional, surveillance,
registry* → STROBE. *Randomised, randomly assigned, trial arms, allocation* →
CONSORT. *Systematic review, meta-analysis, search strategy, screening, PRISMA
flow* → PRISMA. *Prediction model, risk score, discrimination/calibration, AUROC,
machine learning, neural, classifier* → TRIPOD+AI.

> **Growth, not a main guideline.** v1 ships four guidelines. STARD (diagnostic
> accuracy), RECORD (routinely-collected data), and SPIRIT (trial protocols) are
> the next slots: they are added to *this same frame* — a new name, a new item
> roster — never a new skill. Routing plus add-only growth is the structure
> (borrowed from medsci's `check-reporting`, which holds 32 guidelines in one
> skill); never split one guideline into its own skill.

## Step 2 — Run the selected checklist

Compare the manuscript against every required item of the chosen guideline and
decide a status for each (Step 3 defines the statuses). Use the condensed rosters
below as the item set; consult the full EQUATOR checklist text when an item's
intent is unclear. The item **IDs are the contract** — the hook expects a stamp
for every ID in the active guideline's roster.

### STROBE (22) — observational

1 Title and abstract · 2 Background/rationale · 3 Objectives · 4 Study design ·
5 Setting · 6 Participants · 7 Variables · 8 Data sources/measurement · 9 Bias ·
10 Study size · 11 Quantitative variables · 12 Statistical methods ·
13 Participants (numbers/flow) · 14 Descriptive data · 15 Outcome data ·
16 Main results · 17 Other analyses · 18 Key results · 19 Limitations ·
20 Interpretation · 21 Generalisability · 22 Funding

### CONSORT (25) — randomised trial

1 Title and abstract · 2 Background and objectives · 3 Trial design ·
4 Participants · 5 Interventions · 6 Outcomes · 7 Sample size ·
8 Randomisation: sequence generation · 9 Allocation concealment ·
10 Randomisation: implementation · 11 Blinding · 12 Statistical methods ·
13 Participant flow · 14 Recruitment · 15 Baseline data · 16 Numbers analysed ·
17 Outcomes and estimation · 18 Ancillary analyses · 19 Harms · 20 Limitations ·
21 Generalisability · 22 Interpretation · 23 Registration · 24 Protocol ·
25 Funding

### PRISMA (27) — systematic review / meta-analysis

1 Title · 2 Abstract · 3 Rationale · 4 Objectives · 5 Eligibility criteria ·
6 Information sources · 7 Search strategy · 8 Selection process ·
9 Data collection process · 10 Data items · 11 Risk-of-bias assessment ·
12 Effect measures · 13 Synthesis methods · 14 Reporting-bias assessment ·
15 Certainty assessment · 16 Study selection (flow) · 17 Study characteristics ·
18 Risk of bias in studies · 19 Results of individual studies ·
20 Results of syntheses · 21 Reporting biases · 22 Certainty of evidence ·
23 Discussion · 24 Registration and protocol · 25 Support/funding ·
26 Competing interests · 27 Availability of data/code/materials

### TRIPOD+AI (27) — prediction / AI model

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

Write two kinds of marker into the manuscript. Markers are HTML comments so they
do not appear in rendered prose but are still found by the hook and by a human
reviewer reading the source.

**One declaration**, naming the active guideline:

```
<!-- [REPORTING-GUIDELINE: TRIPOD+AI] -->
```

**One stamp per required item**, with exactly one status:

```
<!-- [TRIPOD+AI-8: PRESENT] -->
<!-- [TRIPOD+AI-13: PARTIAL] outcome class imbalance only named, not quantified -->
<!-- [TRIPOD+AI-17: MISSING] -->
```

Status meanings:

| Status | Meaning |
|--------|---------|
| `PRESENT` | The item is reported adequately in the manuscript. |
| `PARTIAL` | The item is addressed but incompletely (named but not specified, mentioned but not quantified). |
| `MISSING` | The item is required for this design and is not addressed. |

Rules:

- Stamp **every** item ID in the active guideline's roster. An item that is left
  unstamped is read by the hook as a silently skipped check — it is reported as a
  gap exactly like a `MISSING`. Completeness of the *audit* is enforced, not just
  completeness of the manuscript.
- Use exactly one status per item ID. The token grammar is
  `[NAME-ID: STATUS]` — keep it exact so the hook can parse it. Free-text after
  the closing bracket (a short reason) is fine and encouraged for `PARTIAL` /
  `MISSING`.
- Do **not** invent content to make an item PRESENT, and do not downgrade a real
  gap to PARTIAL to quiet the audit. The honest status is the point; the human
  fixes the gap.

## What the hook reports (and what it does not do)

On every save of a manuscript carrying a declaration, the hook:

- reads the declared guideline and its required-ID roster,
- lists every `MISSING` item, every unstamped required item, and every `PARTIAL`
  item,
- exits non-zero so the audit is surfaced to Claude as feedback.

It does **not** block the save — at PostToolUse the write has already happened.
The save always stands; the audit is advisory-but-unskippable. If a manuscript
carries no `[REPORTING-GUIDELINE: …]` declaration, the hook stays silent: the
discipline above is what adds the declaration, and a file with no declaration is
treated as not-under-audit rather than guessed at.

## Output format

When auditing, report: the routed guideline and why; a one-line tally
(`PRESENT n / PARTIAL n / MISSING n / unstamped n`); then the `MISSING` and
unstamped items first (these are the gaps to close), followed by `PARTIAL` items
(incomplete), and finally confirm the `PRESENT` count. Group gaps at the top so
they are seen and resolved first — the same ordering principle as
citation-verifier's blocked-entries-first output.

## Scope (v1)

- **In scope:** four guidelines (STROBE, CONSORT, PRISMA, TRIPOD+AI), routing by
  study design, per-item PRESENT/PARTIAL/MISSING stamping, and a PostToolUse hook
  that reports MISSING / unstamped / PARTIAL items without blocking the save.
- **Out of scope (v2+):** STARD, RECORD, SPIRIT and other guidelines (added to
  the same frame, not new skills); risk-of-bias tool integration; claim-level
  adequacy judgement of each section (the hook reads stamps, it does not grade
  prose). Auto-generated flow diagrams are a format aid, not part of this audit.

## Why this is a skill and not a checklist PDF or an on-demand command

A checklist PDF waits to be opened and filled in by hand; a `/check-reporting`
command waits to be called. Both are skippable — the moment a deadline looms, the
checklist is the first thing dropped. This skill exists to (1) route the study to
the correct guideline so the author is not auditing against the wrong checklist,
(2) make the status of every item a marker that travels with the manuscript
rather than a form filled once and lost, and (3) run the completeness audit
automatically on every save so "I forgot to check reporting" stops being
possible — while still leaving every fix to the human.
