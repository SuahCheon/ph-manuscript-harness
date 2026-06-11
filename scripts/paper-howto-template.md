# How to use this folder (Manuscript Harness)

This folder is a paper workspace with two enforcement skills installed under
`.claude/skills/`: **citation-verifier** (blocks fabricated citations at write
time) and **reporting-guidelines** (reports reporting-checklist gaps on save).

## The split: draft anywhere, enforce here

- **Drafting / brainstorming / literature work** — do it wherever you like
  (e.g. a claude.ai Project with this folder mounted via Filesystem MCP). This is
  convenient but **not enforced**: an MCP file write does not trigger the hooks.
- **Enforcement rounds** — run **Claude Code from inside this folder**. Only then
  do the hooks fire on the `Write` / `Edit` tool. Save drafts on the other side
  first; edit from one side at a time so a save does not overwrite the other.

## Writing one paper, start to finish

1. **Draft.** Write into `manuscript.md` (or other `.md` files here). No
   enforcement yet — draft freely.

2. **Enforcement round — open Claude Code in this folder.** Check the PubMed MCP
   is connected, then ask, in plain language:
   - *"Verify the citations in manuscript.md with citation-verifier."*
     Claude routes each citation (PubMed / Korean DB / grey literature), labels
     it, and on save a `[FABRICATED]` citation **blocks the write** and names the
     line. Fix it, reclassify it, or — for a genuinely just-published paper whose
     PMID is not yet live — confirm manually and override.
   - *"Check manuscript.md against the reporting guideline with
     reporting-guidelines."* Claude picks the EQUATOR checklist for the study
     design and stamps each item `PRESENT` / `PARTIAL` / `MISSING`. On save the
     gaps are **reported but the save is not blocked** — fill them over time.

3. **Repeat.** Move the checked text back to drafting, keep writing, run another
   enforcement round when enough has accumulated. The labels are HTML comments,
   so they travel with the file and stay invisible in rendered output.

4. **Before submission.**
   - Citations: no `[FABRICATED]` remains (the gate would have blocked it);
     resolve any remaining `[UNVERIFIED]` and confirm grey-literature sources.
   - Reporting: the last audit shows no `MISSING` / unstamped required items.
   - Optionally strip the `<!-- [...] -->` label comments from the submission
     copy (or keep them as an audit trail).

## Two boundaries to remember

- **Automatic verification covers the PubMed branch only.** Grey literature
  (WHO / CDC / KDCA / MFDS) and Korean DBs are *tagging-only* in v1 — you confirm
  the source yourself and the label records that you did; the tool does not
  machine-verify them.
- **Enforcement happens only in Claude Code.** While editing through a Project or
  any MCP path, the hooks do not run. Run the enforcement round in Claude Code
  from this folder to get the hard stop.

> Interpreter note: the hooks call `python`. On macOS / Linux, if only `python3`
> exists, set the `command:` field in each `.claude/skills/*/SKILL.md` frontmatter
> to `python3`.
