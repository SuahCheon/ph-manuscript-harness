---
name: citation-verifier
description: >-
  Verify citations in public health and medical manuscripts by routing each
  reference to the correct source of truth, attaching a verification label, and
  blocking citations proven fabricated (a non-existent PMID or contradicted
  fields) while letting merely-unconfirmed ones through with a loud label. Use
  this skill whenever the user is writing, reviewing, or finalizing a manuscript
  and inserts, edits, or asks to check a citation — including author, year,
  title, journal, PMID, or DOI — even if they do not explicitly say "verify."
  Public health writing relies heavily on grey literature (WHO, CDC, KDCA, MFDS
  guidance) that has no PMID/DOI and is invisible to ordinary citation checkers,
  so this skill must be consulted instead of assuming a generic reference manager
  covers it. Trigger on phrases like "check this citation," "is this reference
  real," "I cited X et al.," or any reference list review.
---

# Citation Verifier (Codex port)

Verify each citation in a public-health / medical manuscript against the *right*
source of truth, attach a label recording what was checked, and **stop any
citation proven fabricated** before it reaches the committed manuscript.

> **Enforcement on this runtime.** This is the Codex port of the Claude Code
> skill. The *discipline* (route → label → decide) is identical and travels
> unchanged. Only the enforcement point differs: Codex's hooks intercept the
> Bash tool, not Write/Edit, so there is no write-time gate. The decision is
> therefore enforced at the **git pre-commit boundary** by
> `codex/hooks/manuscript_precommit_check.py` (see `codex/INSTALL.md`): a
> citation labelled `[FABRICATED]` **aborts the commit**; every other label
> passes. Same rule (`[FABRICATED]` → deny, everything else → allow), bolted to
> commit instead of to the write syscall. The full rationale lives in the
> Claude Code skill at `.claude/skills/citation-verifier/SKILL.md`.

## Core principle

A citation checker that only knows PubMed is wrong for this domain. Public
health citations split three ways, and roughly a third have no PMID and no DOI.
So this skill routes first, verifies within the branch, then records an
enforcement decision as a label. The rule is *let correct citations through but
stamp them; stop the ones proven wrong*. Grey literature and verified references
are normal — they pass with a forced label. A citation that the lookup proved
wrong (a non-existent PMID, contradicted fields) is an error, not a source, and
its `[FABRICATED]` label is what the commit gate rejects. This is designed
deference: block only what is proven wrong, and leave every genuine judgement
call to the human by labelling rather than gatekeeping.

## Step 1 — Route every citation into one of three branches

| Branch | Source type | Examples | How to verify |
|--------|-------------|----------|---------------|
| **A. English-language academic** | Peer-reviewed, indexed in PubMed | most journal articles | Look up via PubMed (MCP); match author / year / title / journal against the PMID record |
| **B. Korean medical** | Korean academic DBs | KoreaMed, KMbase, RISS | Match against the Korean DB record (tagging-only in v1; see Scope) |
| **C. Grey literature** | Government / international-body publications, no peer review | WHO, CDC, KDCA, MFDS guidance | No PMID/DOI exists — confirm the issuing organization and document; absence of an index hit is expected, not a failure |

Routing hints: a PMID or journal name → Branch A. A Korean-language author/journal
→ Branch B. An issuing *organization* rather than a journal (WHO, CDC, 질병관리청,
식약처) → Branch C.

## Step 2 — Verify, and separate "failed" from "unavailable"

This distinction decides whether a citation is blocked, so do not collapse it.

- **Verification *failed* (proven wrong).** The lookup completed and the answer
  is negative: a syntactically valid PMID the index returns *no record* for, or a
  record whose author/year contradicts the citation. Checked and absent — the
  signature of a hallucinated citation. This is `[FABRICATED]`.
- **Verification *unavailable* (couldn't check).** The lookup could not complete
  — API outage, timeout, rate limit. The citation might be perfectly real. This
  is `[UNVERIFIED]`.

Do not treat a brand-new paper as "unavailable": an unresolved *PMID* points to
fabrication far more often than to indexing lag. The rare genuine case
(just-published, PMID issued but not yet live) is handled by the human override
on the commit (`git commit --no-verify`), not by weakening the rule.

## Step 3 — Decide and label

Each citation gets exactly one label. The label is forced onto the citation; the
commit gate reads it.

| Label | Branch / status | Enforcement decision |
|-------|-----------------|----------------------|
| `[PMID-VERIFIED]` | A; PMID found and fields match | **allow** + force label |
| `[KOREAMED]` | B; matched (or tagged) against Korean DB | **allow** + force label |
| `[GREY-LIT-WHO]` / `[GREY-LIT-CDC]` / `[GREY-LIT-KDCA]` / `[GREY-LIT-MFDS]` | C; grey literature, organization recorded | **allow** + force label |
| `[UNVERIFIED]` | Lookup could not complete — real-or-not unknown | **allow** + a loud label |
| `[FABRICATED]` | Lookup completed and the citation is proven wrong | **deny** (aborts the commit) |

The four `allow` rows are not a soft pass: the label is mandatory, so the
verification status travels with the text and a human can always see it.
`[UNVERIFIED]` is the loudest allow label — "this was never confirmed, confirm it
yourself" — but it does not block, because an outage is not evidence of
fabrication. Only `[FABRICATED]` is blocked.

Do **not** delete, rewrite, or silently "fix" a fabricated citation. Surface it
with its label; the human decides (correct it, supply the real PMID, or
reclassify it). At commit, the gate refuses any manuscript still carrying a
`[FABRICATED]` label and names the offending lines.

## Output format

For a single citation: report the branch, the label, the decision, and (for a
block) the specific reason. For a reference list: one row per citation with its
label and decision, with `[FABRICATED]` entries grouped at the top, then
`[UNVERIFIED]` entries as the ones still needing a human check.

## Scope (v1)

- **In scope:** three-branch routing, PubMed verification (Branch A), labeling
  for all branches, commit-time blocking of `[FABRICATED]`, and the
  failed-vs-unavailable split that keeps an API outage from blocking a
  possibly-real citation.
- **Out of scope:** scraping Korean DBs or grey-literature sites. Branch B and C
  are **tagging-only** here — the label records *what kind* of source it is and
  that a human must confirm it. Scraping is a later phase.

## Why a commit gate and not a reference manager

A reference manager answers when asked and indexes what has a PMID/DOI. It goes
silent on grey literature, it never intercepts a citation, and it never refuses
one. This skill (1) routes the third of public-health citations ordinary tools
cannot see, (2) makes verification a label forced onto the text rather than a
search the writer must remember to run, and (3) stops a proven-wrong citation at
the commit — the last boundary before it enters the shared repository — instead
of discovering it in peer review.
