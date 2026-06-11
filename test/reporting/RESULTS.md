# Test record — reporting-guidelines audit vs. the checkpoint

Two layers, mirroring citation-verifier's record:

- **Layer 1 — decision logic** (container + local Git Bash): feed manuscripts to
  the hook as Write/Edit tool-call JSON and check the exit code / report.
- **Layer 2 — live firing** (local Claude Code session): confirm Claude Code
  actually fires the frontmatter PostToolUse hook on a real save and surfaces the
  report. **Both layers now pass.**

Domain: an example neuro-symbolic AEFI prediction model. By the
concept note's own routing table this is a **TRIPOD+AI** study (diagnostic /
prognostic prediction model, AI included), so the test manuscripts declare
`[REPORTING-GUIDELINE: TRIPOD+AI]` and the audit runs the 27-item TRIPOD+AI
roster.

## Test manuscripts

| File | Contents | Purpose |
|------|----------|---------|
| `manuscript_R_complete.md` | TRIPOD+AI declared; all 27 items stamped PRESENT | A fully-audited manuscript should pass |
| `manuscript_R_incomplete.md` | same study; 2 MISSING (14 Fairness, 17 Ethical approval), 2 PARTIAL (13 Class imbalance, 23 Model performance), 2 UNSTAMPED (19 PPI, 24 Model updating) | Gaps of all three kinds should be surfaced — without blocking the save |

## Layer 1 — decision logic

| Manuscript | Audit state | Expected | Hook exit | Verdict |
|------------|-------------|:--------:|:--------:|:------:|
| R — complete | 27/27 PRESENT | pass (0) | 0 | ✅ |
| R — incomplete | PRESENT 21 / PARTIAL 2 / MISSING 2 / unstamped 2 | report (2) | 2 | ✅ |

Edge cases (all pass-through, exit 0): no `[REPORTING-GUIDELINE]` declaration
(not under audit); an unrostered guideline (STARD, out of v1 scope); the skill's
own `SKILL.md` / any `/.claude/` file (self-guard); malformed JSON (fail open).
Edit-tool input (`new_string`) is audited the same as Write `content` (verified
with a STROBE example).

On the incomplete manuscript, stderr named the exact gaps, grouped gaps-first:

```
PRESENT 21 / PARTIAL 2 / MISSING 2 / unstamped 2  (required: 27)
MISSING (required, not addressed):
  - TRIPOD+AI-14  (Fairness)
  - TRIPOD+AI-17  (Ethical approval)
UNSTAMPED (required item never assessed):
  - TRIPOD+AI-19
  - TRIPOD+AI-24
PARTIAL (addressed but incomplete):
  - TRIPOD+AI-13  (Class imbalance - imbalance named but resampling not quantified)
  - TRIPOD+AI-23  (Model performance - AUROC given, calibration not reported)
```

Note (Windows): the Layer-1 manual harness must avoid a PowerShell 5.1
`python | python` native pipe, which injects a UTF-8 BOM and cp949-mangles the
JSON, making `json.loads` fail (the hook then fail-opens, exit 0, no report).
Use Git Bash or a single-process invocation; the hook itself reads stdin via
`utf-8-sig` so it is immune to the BOM once the pipe corruption is avoided. See
`LOCAL-TEST.md` §3.

## Layer 2 — live firing (Claude Code session) ★ beat 4, reporting half

Same two manuscripts, saved through Claude Code with the skill active:

| Request | File created? | PostToolUse hook | Verdict |
|---------|:---:|------|:---:|
| incomplete → `ms_draft.md` | **yes** | fired on save; surfaced the same report (MISSING 14·17 / UNSTAMPED 19·24 / PARTIAL 13·23) as feedback | ✅ |
| complete → `ms_final.md` | **yes** | no report (silent exit 0) | ✅ |

→ **The save is never blocked — the file is always created — and the audit fires
right after.** The incomplete manuscript was *annotated*, not stopped; the
complete one passed silently. This is the live proof that the frontmatter
PostToolUse hook actually fires in a real session and enforces by *surfacing*,
not by denying.

Registration note: the hook is declared in **`SKILL.md` frontmatter**
(`PostToolUse` / matcher `Edit|Write`), not in `settings.local.json` — Claude Code
auto-registers a skill's frontmatter hook. The live firing in Layer 2 is stronger
evidence of correct registration than reading a `/hooks` listing would be.

## What this proves (the talk's beat 3, reporting half)

1. **Routing then completeness.** The study is audited against TRIPOD+AI, the one
   guideline its design selects — not a generic checklist.
2. **The check cannot be skipped, but it does not block.** Both manuscripts were
   saved; the incomplete one was *annotated* (exit 2 = feedback to Claude), not
   stopped. This is the deliberate one-notch-softer enforcement: a missing
   reporting item is fixable, so it is surfaced, not denied.
3. **Silent skips are caught.** An item left unstamped (19, 24) is reported just
   like a MISSING one — completeness of the *audit* is enforced, not only
   completeness of the manuscript.

## Enforcement contrast with citation-verifier (the package's point)

| | citation-verifier | reporting-guidelines |
|---|---|---|
| hook event | PreToolUse | **PostToolUse** |
| decision | **deny** (block `[FABRICATED]`) | **annotate** (report gaps, save stands) |
| exit 2 means | write cancelled | feedback shown, write kept |
| why | a fabricated citation is not fixable | a missing item is fixable, progressive |

Same discipline/enforcement split, same checkpoint model (audit upstream, hook
reads markers), enforcement strength scaled to risk. Both verified live: citation
blocks the bad write; reporting lets the write stand and surfaces the gaps.

## Still pending (honest scope)

Decision logic **and** live firing are both done. Remaining for v1 is packaging
(the README that doubles as the talk). Out of scope for v1, by design:
STARD/RECORD/SPIRIT and other guidelines (added to the same routing frame, not
new skills); risk-of-bias tool integration; and any grading of prose adequacy —
the hook reads stamps, the adequacy judgement stays upstream with Claude.
