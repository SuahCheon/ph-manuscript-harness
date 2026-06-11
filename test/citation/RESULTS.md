# Logic test — example manuscripts vs. the gate

Hook tested: `../../​.claude/skills/citation-verifier/scripts/block_fabricated.py`
(PreToolUse gate, container + local logic test). This verifies the *decision
logic* by feeding manuscripts to the hook as Write tool-call JSON. The live test
— that Claude Code actually fires the frontmatter hook in a session — is the
separate `LOCAL-TEST.md` procedure (confirmed live: B blocked, A saved).

Domain: an example neuro-symbolic AEFI surveillance manuscript. Grey-lit
sources are real to this domain: WHO AEFI causality classification, Brighton
Collaboration, KDCA pharmacovigilance guidance.

## Test manuscripts

| File | Contents | Purpose |
|------|----------|---------|
| `manuscript_A_clean.md` | PMID-VERIFIED ×2, GREY-LIT-WHO ×2, GREY-LIT-KDCA ×1 | A correctly-labeled manuscript should pass |
| `manuscript_B_seeded.md` | adds FABRICATED ×2 (year mismatch + non-existent PMID), UNVERIFIED ×1 (API timeout) | Seeded errors should block — and block *only* for the right reason |
| `manuscript_B_only_unverified.md` | B with all FABRICATED rewritten to UNVERIFIED | An outage-only manuscript must NOT be blocked |

## Results

| Manuscript | Labels present | Expected | Hook exit | Verdict |
|------------|----------------|:--------:|:--------:|:------:|
| A — clean | PMID-VERIFIED, GREY-LIT-* | pass (0) | 0 | ✅ |
| B — seeded | + FABRICATED ×2, UNVERIFIED ×1 | block (2) | 2 | ✅ |
| B — unverified-only | UNVERIFIED ×3, no FABRICATED | pass (0) | 0 | ✅ |

On block, stderr named the exact offending lines:

- `year/record mismatch [FABRICATED]` (Park et al. cited 2019, record reads 2021)
- `99999999 returns no record at all on lookup [FABRICATED]`

## What this proves (the talk's beat 3, citation half)

1. **Valid + grey-literature citations pass.** WHO/Brighton/KDCA grey lit is
   never blocked — it is legitimate public-health sourcing without a PMID.
2. **Only proven-wrong citations block.** A year mismatch and a non-existent
   PMID are caught at write time and named line-by-line.
3. **An outage does not punish a citation.** A manuscript whose only problem is
   "couldn't reach PubMed" (UNVERIFIED ×3) passes. Blocking is reserved for
   `[FABRICATED]` — the narrowed blade. This is the precise-enforcement claim,
   shown rather than asserted.

## Live firing (Claude Code session) — verified

Saving `manuscript_B_seeded.md` through Claude Code was **blocked** (the file was
not created) with the FABRICATED lines named; saving `manuscript_A_clean.md` was
**allowed** (file created). The frontmatter PreToolUse hook fires in a real
session — see `LOCAL-TEST.md`. The hook reads stdin as `utf-8-sig`, so a BOM
injected by a PowerShell native pipe or non-ASCII manuscript content does not
make it fail-open.
