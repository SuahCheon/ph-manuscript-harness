# Curation — what was already out there, what we kept, what we changed

The real learning goal of phase 1 is *not* inventing a citation checker. It is
**curating**: scanning what already exists, selecting the pieces that fit a
public-health discipline, and reshaping them into one installable package. This
document records that selection judgment — including the discovery that a
sophisticated citation gate already exists, which makes the curator's job
(differentiate, don't reinvent) the actual work.

Three source collections were surveyed, all following the open Agent Skills
standard (agentskills.io), all cross-runtime (Cursor / Claude Code / Codex):

| Collection | What it is | Scale | License* | Domain center of gravity |
|------------|-----------|-------|----------|--------------------------|
| **ARS** (Imbad0202/academic-research-skills) | A research→write→review→revise→finalize pipeline with a built-in citation verification gate | multi-skill suite, v3.11.x | CC-BY-NC (per concept note) | general academic; economics / finance / social science |
| **K-Dense** (K-Dense-AI/scientific-agent-skills) | Ready-to-use scientific skills + scientific databases | 138 skills, 78+ DBs | MIT (per concept note) | biology / chemistry / medicine / drug discovery |
| **medsci-skills** (Aperivue/medsci-skills) | A physician-researcher's clinical-manuscript pipeline with reference verification + 32-guideline reporting audit | 42 skills, v3.x | MIT | public-health / clinical medicine; radiology, DTA, EMR, SR/MA |

\* Licenses are taken from the concept note (ARS, K-Dense) or the repo (medsci)
and **must be re-confirmed against each repo before any fork or redistribution.**

---

## Part 1 — Deep comparison: ARS citation-gate vs. our citation-verifier

The headline finding: **ARS already ships a citation gate, and a serious one.**
It is motivated by the same problem we are (Zhao et al.'s ~146,932
hallucinated-citation finding), it is deterministic, and it sits at a defined
boundary in the writing pipeline. So "we built a citation gate" is not a
contribution. The contribution is what is different.

### Where ARS and our skill agree (so we did not reinvent these)

- **Same threat.** Hallucinated / fabricated citations are the enemy in both.
- **Determinism over vibes.** Both treat verification as a deterministic check,
  not a soft "please double-check."
- **Two-stage enforcement.** ARS runs an *advisory* verifier at the Phase 4→5
  boundary and a *hard* gate at the formatter stage. This is the same
  double-safety idea our concept note sketched ("formatter REFUSE list as a
  second safety net"). ARS having actually built it validates the pattern.
- **Plain-Python, stdlib, cross-runtime.** Same engineering shape; same
  `python` vs `python3` portability footgun we already noted.

### Where we differ (the actual contribution)

| Axis | ARS citation-gate | Our citation-verifier | Why the difference matters |
|------|-------------------|------------------------|----------------------------|
| **Verification source** | Crossref + pdftotext first-party; Semantic Scholar client | PubMed (biomedical) + Korean DBs + **grey literature** | ARS's sources are DOI-anchored. **Grey literature (WHO/CDC/KDCA/MFDS) has no DOI/PMID, so it is invisible to a Crossref-based gate.** This is the gap we fill. |
| **Branching axis** | *Error type* — 5 temporal failure modes (retrospective arithmetic, anachronistic citation, comparator unmaterialized, causal inversion, deictic present) | *Source type* — PubMed / Korean DB / grey literature | Different axes. ARS asks "what kind of error?"; we ask "what kind of source?" Public-health citation risk is dominated by source type, not temporal logic. |
| **Enforcement strength** | Advisory at Phase 4→5, hard at formatter | Per-branch decision at write time: `allow`+forced-label for valid/grey, `deny` for `[FABRICATED]` | We pull the hard stop forward to the *moment of writing* and make it source-aware: grey lit is never blocked, proven-wrong citations always are. |
| **Enforcement mechanism** | Pipeline-stage boundary inside ARS's own orchestration | Claude Code `PreToolUse` hook on the Edit/Write tool call | ARS enforces *within its pipeline*; we enforce at the *runtime tool boundary*, so the gate fires even outside a dedicated pipeline. |
| **Domain** | General academic | Public health / medicine | Grey-literature weight is the domain difference, not a feature toggle. |

### What we should *borrow* from ARS (curation cuts both ways)

Selecting is not only rejecting — ARS has ideas worth adopting:

1. **Claim–reference alignment audit.** ARS audits whether a citation actually
   *supports the claim it is attached to* (claim_audit / claim_intent_manifest),
   not just whether the reference exists. Our v1 only checks existence. This is
   a strong **v2 candidate** — "the PMID is real" is weaker than "the PMID
   supports this sentence."
2. **Two ordered gates, never short-circuited.** Worth keeping the advisory→hard
   layering in mind for reporting-guidelines and v2, rather than relying on a
   single chokepoint.
3. **Temporal failure patterns (esp. P2 anachronistic citation).** Our
   `[UNVERIFIED]` "year contradicts the record" check is a blunt version of
   ARS's P2. ARS's taxonomy could sharpen what counts as a mismatch.

### One-line framing for the talk

> A capable citation gate already exists. It is DOI-anchored, so it goes blind
> exactly where public health lives — the grey literature with no DOI. Our job
> was not to build a gate; it was to re-aim one at the third of our citations
> that the existing tools cannot see, and to make the stop fire at write time.

---

## Part 2 — Selection judgment over K-Dense (138) + ARS categories

Phase-1 goal is to *demonstrate the judgment of choosing*, not to integrate
everything. Here is the keep/drop reasoning. For most of K-Dense the honest
result is "not applicable" — and that rejection, with its reason, is the
deliverable.

### K-Dense (138 skills) — mostly out of scope, by design

| K-Dense cluster | Keep for our package? | Reason |
|-----------------|:---:|--------|
| Cancer genomics, drug-target binding, molecular dynamics, RNA velocity | ✗ | Bench/omics science; no overlap with citation or reporting discipline. |
| Cheminformatics, structural biology | ✗ | Same — wrong layer of the research stack. |
| Scientific **databases** (78+: PubMed-adjacent, ClinicalTrials, etc.) | ◐ *reference only* | A medical DB connector *concept* is adjacent to Branch A/B verification, but K-Dense's are bench-science DBs. Note the pattern, don't import the skill. |
| Scientific writing / schematics (e.g. CONSORT diagram generation, seen in K-Dense's scientific-writer) | ◐ *reporting-guidelines candidate* | CONSORT is on our EQUATOR list. The *diagram generator* is a format aid, not a checklist enforcer — borrow the CONSORT awareness, not the skill. |
| Everything else (geospatial, time-series, ML resource discovery) | ✗ | Out of domain. |

**Net from K-Dense: ~0 skills imported, 2 ideas noted.** That is the correct
outcome — a 138-skill science library is mostly irrelevant to a public-health
*citation/reporting discipline*, and saying so precisely is the curation.

### ARS — selected as template + differentiation anchor, not bulk import

| ARS piece | Use | Reason |
|-----------|-----|--------|
| citation-gate (verification logic, label idea) | **differentiation anchor** | Compared in Part 1; we re-aim it at grey literature + PubMed + write-time hook. |
| SKILL.md / pipeline structure | **format template** | How a mature multi-skill suite is laid out; a shape reference for our package. |
| claim-audit / two-gate / temporal patterns | **v2 backlog** | Borrowed ideas, deferred (Part 1, "what we should borrow"). |
| Economics / finance / social-science content | ✗ | Wrong domain. |

---

## Part 3 — Deep comparison: medsci-skills, the closest neighbor

K-Dense left a hole (public-health / medical domain pieces). The collection that
actually fills it is **Aperivue/medsci-skills** — 42 skills, MIT, a
physician-researcher's clinical-manuscript pipeline. It is a far sharper
comparison than ARS, because it is *in our exact domain*: PubMed, reporting
guidelines, and even Korean clinical context. Tellingly, medsci's own README
draws the K-Dense line for us — it points wet-lab / genomics users to K-Dense
and positions itself as clinical-manuscript-only, confirming our Part 2
rejection from the other side.

### Where medsci is ahead of us (most places)

| Capability | medsci | our citation-verifier (v1) |
|------------|--------|----------------------------|
| Citation verification | `verify-refs` + `search-lit` across PubMed / Semantic Scholar / CrossRef, BibTeX provenance tags | PubMed branch only; Korean/grey are tag-only |
| Reporting guidelines | `check-reporting` covers **32** guidelines + RoB tools (STROBE, STARD, TRIPOD, PRISMA, CONSORT, …) | reporting-guidelines covers 4 (STROBE, CONSORT, PRISMA, TRIPOD+AI) |
| Pipeline | 42 skills, end-to-end IRB→submission, skills chain each other | two skills |
| Korean context | KNHANES/NHANES, `kr` de-id locale, KJR formatting, Korea regulatory | planned KoreaMed/KMbase (not built) |
| Provenance / audit | arXiv-published "auditable trail" architecture | none |

Honest reading: medsci already does most of what we set out to build, more
deeply, under MIT. Building citation verification from scratch would be
re-inventing. So the curator's move is not to compete on verification — it is to
**stand on medsci and add the three things medsci does not do.**

### Where we differ — and it is exactly the enforcement axis

medsci's reference labels are **OK / MISMATCH / UNVERIFIED / FABRICATED** — the
same four-way distinction we adopted (we map FABRICATED→deny, UNVERIFIED→pass).
We borrowed that split rather than inventing it. But the *enforcement* around it
is deliberately soft:

- `verify-refs` enforcement is an **env var**, `MEDSCI_VERIFY_REFS_MODE`, whose
  default `auto` only blocks when both `SSOT.yaml` and a migration marker exist,
  otherwise it merely **warns**.
- The write-time hook is **documented but not shipped** — the user installs it
  locally if they want it.
- medsci's own arXiv paper frames the contribution as an **"auditable trail"**
  that *surfaces* defects, explicitly *not* a verdict — gates that reveal, more
  than gates that stop.

That is the whole gap we occupy. Same verification taxonomy, opposite
enforcement posture.

### The enforcement spectrum

Plot the tools on a single axis from "reveal" to "stop," and the design tradeoff
becomes legible:

| Strength | Example | False-positive cost | Catches "forgot to check" | Risk user disables it |
|----------|---------|:---:|:---:|:---:|
| off / warn | medsci default (legacy/no-marker) | none | weak | low |
| advisory | ARS Phase 4→5 verifier | low | medium | low |
| opt-in hook (PostToolUse, unshipped) | medsci write-time guard | medium | medium | medium |
| **PreToolUse · deny · bundled** | **ours, naive** | **high** | **strong** | **high** |
| **+ designed deference (block only `[FABRICATED]`)** | **ours, precise** | **medium** | **strong** | **medium** |

The last row is the position we actually hold, and it is now backed by code, not
rhetoric: we sit at the strongest enforcement point (PreToolUse, deny, bundled
in frontmatter), but we narrowed the blade so only a *proven-wrong*
`[FABRICATED]` citation is blocked. `[UNVERIFIED]` — "couldn't check," e.g. an
API outage — passes with a loud label, because an outage is not evidence of
fabrication. That single split (built in `block_fabricated.py`) buys back a
column of false-positive cost while keeping the strongest "forgot to check"
defense.

### Why the industry keeps enforcement soft — and our answer

Everyone — ARS, medsci — keeps enforcement advisory or opt-in for real reasons:
false positives stop legitimate work; "verification failed" often means the API
was down, not that the citation is fake; and a gate that blocks too often gets
switched off, so a *weaker* gate paradoxically enforces for longer. We do not
dismiss these. Our answer is not to abandon enforcement but to **shrink its blade
to what is provably wrong**, leaving everything uncertain (grey literature,
unreachable lookups) to a label and a human. We keep enforcement hard precisely
*because* we made it narrow.

### What we borrow from medsci (curation cuts both ways)

1. **The four-way reference status (OK/MISMATCH/UNVERIFIED/FABRICATED).** Already
   adopted into our label set.
2. **`check-reporting`'s 32-guideline coverage** is the reference target for our
   reporting-guidelines skill — we do not need to assemble checklists from
   scratch; we routed four (STROBE/CONSORT/PRISMA/TRIPOD+AI) into the same
   single-skill frame and grow by adding guidelines, not skills.
3. **The "auditable trail" framing** — surfacing defects with re-executable
   evidence — is a good v2 direction for making our block decisions inspectable.
4. **Korean-context patterns** (de-id locale, journal formatting) show how to
   localize without hardcoding; relevant when we build the KoreaMed branch.

---

## Curation conclusion

1. **"Invent vs. curate" is settled empirically.** ARS and medsci both already
   had citation gates; the concept note's premise — that the pieces exist and
   the skill is to *select and reshape* them — is now demonstrated, not asserted.
   We even borrowed medsci's four-way reference taxonomy directly.
2. **Our differentiators are three, and they survive even the closest neighbor.**
   Against medsci — which out-depths us almost everywhere — what remains ours is
   (a) grey-literature branching, (b) Korean citation DBs, and (c) enforcement
   posture: PreToolUse · deny · bundled, narrowed to `[FABRICATED]`. The first
   two fall out of the source-type axis that DOI-anchored tools cannot cover; the
   third is the "reveal vs. stop" gap that the whole industry leaves open.
3. **We stand on medsci, not against it.** The honest curation move is to take
   medsci as the foundation (verification depth, 32-guideline coverage, the
   reference taxonomy) and add only what it does not do. We are the *braking*
   specialist to medsci's capable engine.
4. **The standard reinforces our discipline/enforcement split.** ARS, medsci,
   and K-Dense all ride the agentskills.io standard across runtimes — but that
   standard carries the *discipline* (SKILL.md), while the *enforcement* (the
   hook) stays Claude Code-specific and outside the portable standard. The
   industry's own portability story stops exactly where ours says it should:
   rules travel, enforcement is bolted to the runtime.
