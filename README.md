# Manuscript Harness

*📖 English · [한국어](README.ko.md)*

**The public-health manuscript harness — enforcement, not assistance.**

Manuscript Harness is two Claude Code skills that hold a manuscript to a
discipline at the moment it is written — verifying citations and auditing
reporting-guideline completeness — and *enforce* that discipline through hooks
rather than merely offering to help. A harness is not a service. It is tack: it
does not add power, it constrains the power that is there so it pulls in one
direction. These skills do not write your paper faster; they make it impossible
to quietly skip the checks that a careful author would run.

---

## The problem

A medical author working with an AI assistant already has good tools. A PubMed
connector answers when asked. A project remembers what the paper is about. But
neither *stops a mistake*:

- **A connector verifies on request, not on write.** It will look up a PMID if
  you ask — it will not intercept a hallucinated citation the instant it lands in
  your draft.
- **A project stores context, it does not run a checklist.** It remembers the
  study; it does not tell you that STROBE item 12 is missing.
- **The hardest third of public-health citations is invisible to all of them.**
  WHO, CDC, KDCA, and MFDS guidance — the grey literature that public-health
  writing leans on — has no PMID and no DOI, so a Crossref- or PubMed-anchored
  checker simply cannot see it.

Capable citation gates already exist (ARS, medsci-skills — see
[`docs/CURATION.md`](docs/CURATION.md)). They are DOI-anchored, and they keep
enforcement soft (advisory, or an opt-in hook the user must install). Manuscript
Harness is not a re-invention of verification. It is a re-aiming of it at the
sources the existing tools go blind to, and a hardening of *when* the check
fires.

---

## Why a harness

The industry has spent its harness engineering on *traction* — scaffolding that
lets an agent do more on its own. Far fewer people build the other half:
*braking* — scaffolding that constrains an agent so it stays on the rails of
accountability. An engine and a brake cannot share a design. Build a brake like
an engine and the car cannot move; ship a car with no brake and you are gambling
with the driver's life.

These skills are brakes. The design rule throughout is **designed deference**:
block or flag only what is provably wrong or demonstrably incomplete, and leave
every genuine judgment call to the human by labelling rather than gatekeeping. As
the model underneath gets stronger, a braking harness should get *tighter*, not
thinner — a smarter model writes more plausible fabricated citations, which are
harder, not easier, to catch.

---

## Two disciplines, two enforcement strengths

The package is two skills whose enforcement strength is scaled to how
recoverable the failure is.

| | [`citation-verifier`](.claude/skills/citation-verifier/SKILL.md) | [`reporting-guidelines`](.claude/skills/reporting-guidelines/SKILL.md) |
|---|---|---|
| Failure it guards | a fabricated citation — **not recoverable**, trust breaks on contact | a missing reporting item — **recoverable**, completed over many edits |
| Hook event | `PreToolUse` (before the write) | `PostToolUse` (after the save) |
| Decision | **deny** — a proven-wrong citation never enters the manuscript | **annotate** — the save always stands; gaps are surfaced |
| What fires it | a `[FABRICATED]` label in the text | any required checklist item not stamped `PRESENT` |
| Division of labour | Claude verifies upstream (PubMed MCP) and writes the label; the hook reads the label and enforces | Claude audits upstream against the checklist and stamps each item; the hook reads the stamps and reports the gaps |

This asymmetry *is* the thesis: a harness does not block uniformly. It matches the
strength of the brake to the cost of the failure.

### citation-verifier — route, label, block only what is proven wrong

Every citation is routed into one of three branches by **source type**, because
public-health citation risk is dominated by where a reference comes from:

- **Branch A — English-language academic** → verified against PubMed.
- **Branch B — Korean medical** (KoreaMed / KMbase / RISS) → tagged (DB scraping
  is out of scope in v1).
- **Branch C — grey literature** (WHO / CDC / KDCA / MFDS) → has no PMID/DOI;
  the issuing organisation is recorded, absence of an index hit is *expected*.

Each citation carries exactly one label, and only one of them blocks:

| Label | Meaning | Decision |
|-------|---------|----------|
| `[PMID-VERIFIED]` | found in PubMed, fields match | allow + force label |
| `[KOREAMED]` | matched/tagged against a Korean DB | allow + force label |
| `[GREY-LIT-WHO/CDC/KDCA/MFDS]` | grey literature, organisation recorded | allow + force label |
| `[UNVERIFIED]` | lookup *could not complete* (API outage, timeout) | allow + a loud label |
| `[FABRICATED]` | lookup *completed and proved it wrong* (no such PMID, or contradicted fields) | **deny** |

The narrowed blade is the point. `[UNVERIFIED]` — "couldn't check" — is **not**
blocked, because an outage is not evidence of fabrication. Only `[FABRICATED]` —
checked and absent — is stopped. We sit at the strongest enforcement point
(PreToolUse, deny, bundled) yet pay a lower false-positive cost than a naive
block-everything gate.

### reporting-guidelines — route to one checklist, stamp every item

The study design selects one EQUATOR guideline, and the manuscript is audited
against its full item set:

| Study design | Guideline (v1) | Items |
|--------------|----------------|:-----:|
| Observational (cohort, case-control, cross-sectional, surveillance) | STROBE | 22 |
| Randomised controlled trial | CONSORT 2010 | 25 |
| Systematic review / meta-analysis | PRISMA 2020 | 27 |
| Diagnostic / prognostic prediction model, incl. ML / AI | TRIPOD+AI 2024 | 27 |

Claude declares the active guideline and stamps every required item
`PRESENT` / `PARTIAL` / `MISSING` as HTML-comment markers. On save, the hook
reads the declared guideline's roster and reports every item that is `MISSING`,
`PARTIAL`, **or never stamped** — an unstamped item is a silently skipped check,
so completeness of the *audit* is enforced, not only completeness of the
manuscript. The save is never blocked; the report is the enforcement.

Guidelines grow by **adding to this one skill's routing frame** (STARD, RECORD,
SPIRIT are the next slots), never by splitting into per-guideline skills — the
structure borrowed from medsci's 32-guideline `check-reporting`.

---

## It actually fires

Both hooks were verified live in a Claude Code session, not just unit-tested.
(Decision-logic and live-firing records: [`test/citation/RESULTS.md`](test/citation/RESULTS.md),
[`test/reporting/RESULTS.md`](test/reporting/RESULTS.md); procedures in each
folder's `LOCAL-TEST.md`.)

- **citation-verifier:** asked to save a manuscript seeded with two
  `[FABRICATED]` citations, Claude Code's `PreToolUse` hook **blocked the write**
  and named the offending lines — the file was never created. The clean
  manuscript **saved normally**. A manuscript whose only flaw was `[UNVERIFIED]`
  ×3 also **passed** — the blade stays on fabrication.
- **reporting-guidelines:** asked to save an incomplete manuscript, the
  `PostToolUse` hook let the file **save** and then surfaced the exact gaps
  (`MISSING 14·17 / UNSTAMPED 19·24 / PARTIAL 13·23`). The complete manuscript
  **saved with no report**.

The contrast is the proof: the brakes are *different strengths* and both engage
on their own. When citation-verifier blocked, Claude did not silently rewrite the
citation — it offered the human three options (fix / reclassify / override).
Deference shows up in the model's behaviour, not only in the hook.

---

## Why git, not MCP

A reasonable question: why ship this as a git directory instead of an MCP server?
Because **the enforcement cannot be carried by MCP.**

- MCP can host the *verification logic* — "what to check." A tool answers when
  it is called.
- MCP cannot host the *enforcement point* — "when to stop." A hook intercepts the
  write itself; it is bolted to the runtime, not invoked on request.

Wrap a harness in MCP and the enforcement falls out; what is left is a tool you
have to remember to call — which is exactly the soft posture this project exists
to replace. So the discipline (`SKILL.md`) and its enforcement (the hook,
bundled in the same frontmatter and directory) travel together as one
git-deployable unit. The same reason a Claude Code *plugin* skill is not allowed
to define hooks: enforcement is runtime-bound by design.

> **MCP-undeployability is not a limitation; it is the evidence.** A tool that
> can be repackaged as a callable service was never enforcing in the first place.

This is also why the portable Agent Skills standard carries the *discipline*
across runtimes but leaves the *hook* runtime-specific: rules travel, enforcement
is bolted down.

---

## Install

Requires [Claude Code](https://code.claude.com) and Python 3 (stdlib only — no
third-party packages).

1. Clone the repo and use it as your project root, or copy the two skills into
   an existing project:
   `git clone https://github.com/SuahCheon/ph-manuscript-harness` — the skills
   are already under `.claude/skills/` (`citation-verifier`,
   `reporting-guidelines`). To add them to a different project, copy those two
   directories into that project's `.claude/skills/`.
2. Start Claude Code **from the project root** (the hooks use
   `${CLAUDE_PROJECT_DIR}` to find their scripts).
3. Interpreter name: the hooks call `python`. On macOS / Linux change the
   frontmatter `command` to `python3`.
4. Allow the skills on first use (Claude Code will prompt), or add
   `Skill(citation-verifier)` and `Skill(reporting-guidelines)` to your local
   settings. `settings.local.json` is machine-specific and git-ignored; the
   hooks themselves live in each `SKILL.md` frontmatter and ship with the repo.
5. Verify with the `LOCAL-TEST.md` procedure in `test/citation/` and
   `test/reporting/`.

The hooks read stdin as UTF-8 (`utf-8-sig`), so non-ASCII (e.g. Korean)
manuscript content and a BOM injected by a Windows PowerShell pipe do not make
them fail silently.

---

## Scope and honest boundaries (v1)

**In scope:** three-branch citation routing with PubMed verification and
write-time blocking of `[FABRICATED]`; four-guideline reporting audit
(STROBE / CONSORT / PRISMA / TRIPOD+AI) with save-time gap reporting; both
enforced by bundled Claude Code hooks.

**Out of scope, by design:**

- Scraping Korean DBs or grey-literature sites — Branch B/C are tagging-only;
  the label records *what kind* of source it is and that a human must confirm it.
- More reporting guidelines (STARD, RECORD, SPIRIT) and risk-of-bias tools —
  added to the same routing frame later.
- Claim-level adequacy: the reporting hook reads stamps; whether a section truly
  satisfies an item is Claude's upstream judgement, not the hook's.
- Claim–reference alignment ("does this PMID support *this sentence*") — a strong
  v2 candidate borrowed from ARS.

---

## Curation, not invention

The intellectual work here was **selecting and reshaping** existing pieces, not
building a citation checker from scratch. Capable gates already exist; this
package stands on the closest neighbour, **medsci-skills** (MIT), takes its
verification depth and four-way reference taxonomy
(OK/MISMATCH/UNVERIFIED/FABRICATED), and adds only the three things it does not
do: grey-literature branching, Korean citation DBs, and a harder enforcement
posture (PreToolUse · deny · bundled, narrowed to `[FABRICATED]`). The full
keep/drop reasoning — including why a 138-skill bench-science library was the
right thing to *reject* — is in [`docs/CURATION.md`](docs/CURATION.md).
Development notes and known limitations: [`docs/NOTES.md`](docs/NOTES.md).

## Credits and license

MIT ([`LICENSE`](LICENSE)). Built on the open Agent Skills standard
(agentskills.io). Compared against and indebted to **ARS**
(academic-research-skills, CC-BY-NC) and **medsci-skills** (Aperivue, MIT);
re-confirm each upstream license before redistribution. Reporting checklists are
the EQUATOR Network guidelines (STROBE, CONSORT 2010, PRISMA 2020, TRIPOD+AI
2024), cited to their published item sets.
