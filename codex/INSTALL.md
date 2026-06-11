# Codex port — install & test

This directory is the **Codex / cross-runtime** edition of Manuscript Harness.
The skills' discipline is the same as the Claude Code edition under `.claude/`;
only the *enforcement point* moves, because of one current Codex limitation.

## Why this port exists

On Claude Code the enforcement is a frontmatter `PreToolUse` / `PostToolUse`
hook that fires the instant a manuscript is written. **Codex's hook system (as
of 2026-06) only intercepts the `Bash` tool** — `Read` / `Write` / `Edit` /
`Apply Patch` do not fire `PreToolUse` or `PostToolUse`. So write-time
interception is unavailable on Codex, and Codex hooks are still an experimental,
feature-flagged capability (disabled on Windows).

Rather than weaken the tool to advisory-only, the enforcement moves to the next
boundary a hook *can* reach reliably and cross-platform: the **git commit**. A
git `pre-commit` hook scans the staged manuscripts and applies the same two
decisions, with the same asymmetry as the Claude Code skills:

| Skill | Decision at commit | Why |
|-------|--------------------|-----|
| `citation-verifier` | a `[FABRICATED]` citation **aborts the commit** | a fabricated citation is not recoverable |
| `reporting-guidelines` | gaps are **reported, commit proceeds** | a missing reporting item is fixable and progressive |

This is the project thesis made literal: *rules travel; enforcement is bolted to
the runtime.* The discipline (SKILL.md) is unchanged; the brake is bolted to the
commit instead of to the write syscall.

## What is here

```
codex/
├── INSTALL.md                          (this file)
├── hooks/
│   ├── pre-commit                      (sh wrapper: resolves python, runs the checker)
│   └── manuscript_precommit_check.py   (the gate; stdlib only)
└── skills/
    ├── citation-verifier/SKILL.md      (same discipline, no frontmatter hook)
    └── reporting-guidelines/SKILL.md   (same discipline, no frontmatter hook)
```

## Install

### 1. Skills (the discipline)

Copy the two skill folders into Codex's skills directory:

- Project-scoped: `.codex/skills/` (shared via git)
- or personal: `~/.codex/skills/`

```sh
mkdir -p .codex/skills
cp -r codex/skills/citation-verifier   .codex/skills/
cp -r codex/skills/reporting-guidelines .codex/skills/
```

Codex reads each `SKILL.md`'s `name` + `description` and loads the body when a
task matches. (The Claude Code editions under `.claude/skills/` carry a `hooks:`
frontmatter block; these Codex editions omit it on purpose — Codex would ignore
it anyway, and leaving it out avoids implying an enforcement Codex does not run.)

### 2. Enforcement (the commit gate)

Point git at the bundled hooks directory:

```sh
git config core.hooksPath codex/hooks
```

On macOS / Linux, make the wrapper executable (and persist the bit in git):

```sh
chmod +x codex/hooks/pre-commit
git add --chmod=+x codex/hooks/pre-commit
```

On Windows, Git for Windows runs the `#!/bin/sh` wrapper through its bundled
bash, so no `chmod` is needed; the wrapper auto-detects `python` vs `python3`.

> **Note — `core.hooksPath` is one setting per repo.** If you already use it for
> other hooks, merge instead: keep your existing hooks dir and have its
> `pre-commit` also call
> `python "$(git rev-parse --show-toplevel)/codex/hooks/manuscript_precommit_check.py"`.

## Test (5 minutes)

The gate scans **staged `.md` files that are manuscripts**, excluding the
project's own machinery (`SKILL.md`, `.claude/`, `.codex/`, `codex/`, `docs/`,
`test/`, `README*`). So put test manuscripts at a normal path like the repo
root.

```sh
# 1) Fabricated citation -> commit MUST fail
printf '# demo\nBad cite. <!-- [FABRICATED] no such PMID -->\n' > ms_demo.md
git add ms_demo.md
git commit -m "try fabricated"        # expect: BLOCKED, commit aborted

# 2) Fix it -> commit passes
printf '# demo\nGood cite. <!-- [PMID-VERIFIED] -->\n' > ms_demo.md
git add ms_demo.md
git commit -m "clean"                 # expect: succeeds

# 3) Reporting gaps -> commit PASSES, gaps reported
printf '# demo\n<!-- [REPORTING-GUIDELINE: STROBE] -->\n<!-- [STROBE-1: PRESENT] -->\n' > ms_rep.md
git add ms_rep.md
git commit -m "incomplete reporting"  # expect: REPORTING AUDIT printed, commit succeeds

# 4) Deliberate override of a real fabricated block
git commit --no-verify -m "override"  # expect: succeeds (human override)
```

Quick logic check without committing (reads the working tree, not the index):

```sh
python codex/hooks/manuscript_precommit_check.py ms_demo.md
echo "exit=$?"      # 1 if a [FABRICATED] line is present, else 0
```

## Honest boundaries

- **The gate fires at commit, not at write.** A fabricated citation can exist in
  the working tree; it is stopped when you try to commit it. That is one notch
  later on the enforcement spectrum than Claude Code's write-time deny — still a
  hard stop, but at the commit boundary.
- **Bundling is looser than on Claude Code.** There the discipline and its hook
  ship in one skill directory. Here the discipline is in `.codex/skills/` and the
  enforcement is a git hook enabled by `core.hooksPath`; a clone does not enforce
  until that one git setting is set. (This split is itself the evidence:
  enforcement is bolted to the runtime, not carried inside the portable skill.)
- **No-python = inactive gate.** If no `python` is found, the wrapper prints a
  warning and lets the commit through rather than blocking every commit. Treat
  that warning as "the gate is not running."
- **Codex-native hooks instead.** If/when Codex wires `PreToolUse`/`PostToolUse`
  to Write, the same `manuscript_precommit_check.py` logic can move into a Codex
  `[hooks]` table in `config.toml`; until then the commit gate is the robust,
  cross-platform choice.
