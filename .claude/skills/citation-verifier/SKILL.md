---
name: citation-verifier
description: >-
  Verify citations in public health and medical manuscripts by routing each
  reference to the correct source of truth, attaching a verification label, and
  blocking citations proven fabricated (a non-existent PMID or contradicted
  fields) while letting merely-unconfirmed ones through with a loud label. Use this skill whenever the user is
  writing, reviewing, or finalizing a manuscript and inserts, edits, or asks to
  check a citation — including author, year, title, journal, PMID, or DOI — even
  if they do not explicitly say "verify." Public health writing relies heavily on
  grey literature (WHO, CDC, KDCA, MFDS guidance) that has no PMID/DOI and is
  invisible to ordinary citation checkers, so this skill must be consulted
  instead of assuming a generic reference manager covers it. Trigger on phrases
  like "check this citation," "is this reference real," "I cited X et al.," or
  any reference list review.
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        # Gate, not verifier. Verification happens upstream (Claude + PubMed
        # MCP) and writes the label into the text; this hook reads the label and
        # blocks the write when a [FABRICATED] citation (proven wrong) tries to
        # enter the manuscript. [UNVERIFIED] (couldn't check) passes through.
        # Bundling it here is the point: the discipline (SKILL.md) and its
        # enforcement (this hook) travel together in one git-deployable
        # directory — which is exactly what an MCP server cannot carry.
        - type: command
          # Exec form (args) avoids shell quoting. CLAUDE_PROJECT_DIR is the
          # documented, reliably-substituted placeholder; CLAUDE_SKILL_DIR is
          # avoided because its substitution is currently unreliable.
          # On Windows the interpreter may be "python" rather than "python3".
          command: "python"
          args:
            - "${CLAUDE_PROJECT_DIR}/.claude/skills/citation-verifier/scripts/block_fabricated.py"
          timeout: 10
          statusMessage: "Citation gate: checking for [FABRICATED]…"
---

# Citation Verifier

Verify each citation in a public-health / medical manuscript against the *right*
source of truth, attach a label recording what was checked, and **block any
citation that cannot be verified** before it reaches the manuscript.

## Core principle

A citation checker that only knows PubMed is wrong for this domain. Public
health citations split three ways, and roughly a third of them have no PMID and
no DOI at all. So this skill routes first, verifies within the branch, then
makes an enforcement decision.

The enforcement rule is **not** "block everything" and **not** "block nothing."
It is: *let correct citations through, but stamp them; stop the ones that are
wrong.* Grey literature and verified references are normal — they pass, but the
label is forced onto them so the verification trail is never lost. A citation
that cannot be confirmed (a non-existent PMID, a hallucinated or contradicted
reference) is an *error*, not a normal source, and it is blocked at the point of
writing. This is designed deference: the tool narrows what it blocks to what is
actually wrong, and leaves every genuine judgment call (is this grey-lit source
the right one?) to the human by labeling rather than gatekeeping.

## Step 1 — Route every citation into one of three branches

Inspect the citation and decide which branch it belongs to. The branch
determines how it gets verified.

| Branch | Source type | Examples | How to verify |
|--------|-------------|----------|---------------|
| **A. English-language academic** | Peer-reviewed, indexed in PubMed | most journal articles | Look up via PubMed MCP; match author / year / title / journal against the PMID record |
| **B. Korean medical** | Korean academic DBs | KoreaMed, KMbase, RISS | Match against the Korean DB record |
| **C. Grey literature** | Government / international-body publications, no peer review | WHO, CDC, KDCA, MFDS guidance | No PMID/DOI exists — confirm the issuing organization and document rather than expecting an index hit |

Routing hints: a PMID or a journal name points to Branch A. A Korean-language
author/journal points to Branch B. An issuing *organization* rather than a
journal (WHO, CDC, 질병관리청, 식약처) points to Branch C.

## Step 2 — Verify within the branch

- **Branch A:** Call the PubMed source and compare the cited author, year,
  title, and journal to the retrieved record.
- **Branch B:** Compare against the Korean DB record. (In the current scope,
  scraping is out — verification here may be tagging-only; see Scope below.)
- **Branch C:** There is no index to hit. Record the issuing organization and
  the document identity; do not attempt to "find a PMID." Absence of a PMID is
  expected, not a failure.

### Separate "verification failed" from "verification unavailable"

This distinction decides whether a citation is blocked, so do not collapse it.

- **Verification *failed* (proven wrong).** The lookup succeeded and the answer
  is negative: a syntactically valid PMID that the index returns *no record*
  for, or a record whose author/year actively contradicts what was cited. A PMID
  that resolves to nothing is not "couldn't check" — it is *checked and absent*,
  the signature of a hallucinated citation. This is `[FABRICATED]`.
- **Verification *unavailable* (couldn't check).** The lookup itself could not
  complete: a PubMed/CrossRef API outage, a network timeout, or a rate-limit
  block. The citation might be perfectly real; we simply have no answer right
  now. This is `[UNVERIFIED]`.

Do not treat a brand-new paper as "unavailable." New work is normally cited by
DOI or as a preprint, not by a PMID that exists-but-is-not-yet-indexed, so an
unresolved *PMID* points to fabrication far more often than to indexing lag.
The rare genuine case (just-published, PMID issued but not yet live) is handled
by the human override on the block message, not by weakening the rule.

## Step 3 — Decide and label

Each citation gets exactly one label *and* an enforcement decision. The label is
forced onto the citation; the decision determines whether the write proceeds.

| Label | Branch / status | Enforcement decision |
|-------|-----------------|----------------------|
| `[PMID-VERIFIED]` | A; PMID found and fields match | **allow** + force label |
| `[KOREAMED]` | B; matched (or tagged) against Korean DB | **allow** + force label |
| `[GREY-LIT-WHO]` / `[GREY-LIT-CDC]` / `[GREY-LIT-KDCA]` / `[GREY-LIT-MFDS]` | C; grey literature, organization recorded | **allow** + force label |
| `[UNVERIFIED]` | Lookup could not complete — API outage, timeout, rate limit. Real-or-not unknown | **allow** + force a loud label |
| `[FABRICATED]` | Lookup completed and the citation is proven wrong — non-existent PMID, or fields contradicting the retrieved record | **deny** (block the write) |

The four `allow` rows are not a soft pass. The label is mandatory: a citation
goes through only *with* its stamp attached, so the verification status travels
with the text and a human can always see it. That forced stamp is itself the
enforcement — the writer cannot silently drop it. `[UNVERIFIED]` is the loudest
of the allow labels: it tells the human "this was never confirmed, confirm it
yourself," but it does not stop the write, because an outage is not evidence of
fabrication.

### Handling `[FABRICATED]` — block, don't pass

When the lookup completed and the citation is proven wrong — a PMID that returns
no record, or fields that contradict the retrieved record — **block the write**
and report the specific reason, e.g.:

- *"BLOCKED — PMID 99999999 returns no record."*
- *"BLOCKED — cited as Smith 2021, PubMed record reads Smith 2019."*

Do **not** delete, rewrite, or silently "fix" the citation, and do not let it
through with a warning. Catching a fabricated citation at the moment it is
written and then waving it through would make the check advisory; blocking is
what makes it a discipline. The human decides what to do (correct it, supply the
real PMID, or reclassify it), but a citation proven wrong does not enter the
manuscript on its own. The block message should remind the human that a
just-published paper whose PMID is issued-but-not-yet-live can be confirmed
manually and overridden — the rare false positive is resolved by the human, not
by relaxing the block.

Three sources, one rule that tracks *correctness, not source type*:

- Grey literature is **blocked from nothing** — a legitimate source that simply
  lacks an index.
- `[UNVERIFIED]` is **not blocked either** — "couldn't check" is not "is fake";
  an outage must not punish a possibly-real citation. It is labeled loudly so
  the human finishes the check.
- `[FABRICATED]` is **blocked** — the one case where the tool actually proved
  the citation wrong.

This is the precise shape of designed deference: block only what is proven
wrong; for everything uncertain, label and defer to the human.

## Output format

For a single citation, report: the branch, the label, the enforcement decision,
and (for a block) the specific reason. For a reference list, return one row per
citation with its label and decision, and group blocked `[FABRICATED]` entries
at the top so they are seen and resolved first, with `[UNVERIFIED]` entries
listed next as the ones still needing a human check.

## Scope (v1)

- **In scope:** three-branch routing, PubMed verification (Branch A), labeling
  for all branches, blocking of `[FABRICATED]` citations, and the
  failed-vs-unavailable split that keeps an API outage from blocking a
  possibly-real citation.
- **Out of scope:** scraping Korean DBs or grey-literature sites. Branch B and
  Branch C verification is **tagging-only** in this version — the label records
  *what kind* of source it is and that a human must confirm it, rather than
  asserting the source was machine-verified. Scraping is a later phase.

## Why this is a skill and not a reference manager

A reference manager answers when asked and indexes what has a PMID/DOI. It goes
silent on grey literature, it does not intercept a citation at the moment it is
written, and it never refuses one. This skill exists to (1) route the third of
public-health citations that ordinary tools cannot see, (2) make verification a
label that is forced onto the text rather than a search the writer has to
remember to run, and (3) stop an unverifiable citation at the point of writing
instead of discovering it in peer review.
