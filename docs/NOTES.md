# Development notes — citation-verifier

Working notes for known limitations and deferred work. These are carried into
the README at deploy time.

## Hook enforcement: frontmatter is the single source, but consider a settings.json safety net

The PreToolUse gate is defined in `SKILL.md` frontmatter so the discipline and
its enforcement ship together in one git-deployable directory. That is the
intended design and it wins on update atomicity: a single `git pull` brings the
rule and the hook registration forward at the *same* version, with no drift and
no shared-file merge conflicts.

The tradeoff: **a frontmatter hook only fires while the skill is active.** A
hook registered in `.claude/settings.json` fires regardless of skill state. So
if a manuscript file is edited in a turn where citation-verifier was not
consulted, the frontmatter hook can have a blind spot. For a tool whose whole
identity is *enforcement*, that gap matters.

**Future work — hybrid model.** Keep the frontmatter hook as the single source
of truth and the carrier of the deploy narrative, and *additionally* register
the same `block_fabricated.py` gate in `.claude/settings.json` as an
always-on safety net. Cost: the "one source of truth" property is slightly
diluted (the gate now lives in two places). Benefit: the block fires even when
the skill is not active. Decide based on how strict the always-on requirement
is in real use; for v1, frontmatter-only is fine and the gap is worth
naming honestly in the talk as "enforcement design must account for activation
scope."

## Path placeholder: revisit when CLAUDE_SKILL_DIR is fixed

The frontmatter args path is hardcoded to
`${CLAUDE_PROJECT_DIR}/.claude/skills/citation-verifier/scripts/block_fabricated.py`.
This assumes the skill is installed under that exact name and location. The
natural placeholder would be `${CLAUDE_SKILL_DIR}` (auto-resolves to the skill's
own directory), but its substitution is currently unreliable (claude-code issue
#36135). When that is fixed, switch to `${CLAUDE_SKILL_DIR}` to remove the path
rigidity. Until then: **on redeploy or rename, check the args path.**

## Interpreter name on Windows

The hook calls `python`. On macOS / Linux the interpreter is usually `python3`.
Confirm in the target environment and match the frontmatter `command`.

## stdin encoding (applies to both hooks)

Both hooks read stdin as bytes and decode `utf-8-sig`, not via `sys.stdin.read()`.
Claude Code writes the tool-call JSON as UTF-8; reading with the console locale
(cp949 on Korean Windows) mangles non-ASCII manuscript content and makes
`json.loads` fail, which would make the gate fail-open silently. `utf-8-sig` also
absorbs a leading BOM injected by a PowerShell native pipe, so the manual test
harness and the live hook behave the same. See `test/*/LOCAL-TEST.md` §3.
