#!/usr/bin/env python3
"""manuscript_precommit_check.py - git pre-commit gate for Manuscript Harness.

Why this file exists (the Codex / cross-runtime enforcement point)
------------------------------------------------------------------
On Claude Code the enforcement is a frontmatter PreToolUse hook that intercepts
the Write/Edit tool the instant a citation is written. Codex's hook system
(as of 2026-06) intercepts only the Bash tool - Read / Write / Edit / Apply-Patch
do NOT fire PreToolUse or PostToolUse - so write-time interception is unavailable
on that runtime. The enforcement therefore moves to the next boundary a hook can
actually reach: the git commit. Same discipline, same labels; the brake is bolted
to the commit instead of to the write syscall. (Rules travel; enforcement is
bolted to the runtime.)

Two checks, two enforcement strengths (unchanged from the Claude Code skills):
  - citation-verifier   : a [FABRICATED] citation BLOCKS the commit (exit 1).
  - reporting-guidelines : missing / partial / unstamped reporting items are
                           REPORTED but never block the commit (annotate only).

The checks run over the *staged* content of manuscript .md files (exactly what
is about to be committed), excluding the project's own machinery (skill files,
docs, README, tests, the port directory) so a commit is never gated by its own
example tokens.

Usage
-----
  - As a git hook: invoked with no args; reads the staged file list itself.
  - Quick manual test: pass file paths as args; it reads those from the working
    tree instead of the index.

No third-party dependencies (subprocess + re are stdlib); runs the same on
Windows (Git Bash), macOS, and Linux.
"""
import sys
import re
import subprocess

# Windows consoles default to a legacy code page (cp949 etc.); force UTF-8 so the
# report renders cleanly. Messages below are kept ASCII-only as a second layer.
try:
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FABRICATED = "[FABRICATED]"

# Required-item count per v1 guideline (labels live in SKILL.md, not here, so
# this stays a pure marker-reader). Mirrors the reporting-guidelines hook.
ROSTERS = {
    "STROBE": 22,
    "CONSORT": 25,
    "PRISMA": 27,
    "TRIPOD+AI": 27,
}
DECL_RE = re.compile(r"\[REPORTING-GUIDELINE:\s*([^\]]+?)\s*\]")


def is_manuscript(path):
    """A staged .md path we should check: a manuscript, not project machinery."""
    norm = path.replace("\\", "/")
    if not norm.lower().endswith(".md"):
        return False
    base = norm.rsplit("/", 1)[-1]
    if base == "SKILL.md" or base.lower().startswith("readme"):
        return False
    for seg in (".claude/", ".codex/", "codex/", "docs/", "test/", "tests/"):
        if norm.startswith(seg) or ("/" + seg) in norm:
            return False
    return True


def staged_md_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "-z"],
        capture_output=True,
    )
    names = out.stdout.decode("utf-8", "replace").split("\0")
    return [n for n in names if n and is_manuscript(n)]


def staged_content(path):
    # The staged blob (":path") - exactly what is about to be committed.
    out = subprocess.run(["git", "show", ":" + path], capture_output=True)
    return out.stdout.decode("utf-8-sig", "replace")


def worktree_content(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8-sig", "replace")


def find_fabricated(text):
    return [
        (i, line)
        for i, line in enumerate(text.splitlines(), 1)
        if FABRICATED in line
    ]


def reporting_gaps(text):
    """None if no audited declaration; else (name, tally|None, missing, unstamped, partial).

    tally is None when the manuscript is complete (every required item PRESENT).
    """
    decl = DECL_RE.search(text)
    if not decl:
        return None
    name = decl.group(1).strip().upper()
    if name not in ROSTERS:
        return None
    stamp_re = re.compile(
        r"\[" + re.escape(name) + r"-(\d+):\s*(PRESENT|PARTIAL|MISSING)\s*\]"
        r"[ \t]*(.*)",
        re.IGNORECASE,
    )
    present, partial, missing, stamped = set(), {}, {}, set()
    for m in stamp_re.finditer(text):
        item_id = int(m.group(1))
        status = m.group(2).upper()
        note = re.sub(r"\s*-->\s*$", "", m.group(3)).strip()
        stamped.add(item_id)
        if status == "PRESENT":
            present.add(item_id)
        elif status == "PARTIAL":
            partial[item_id] = note
        else:
            missing[item_id] = note
    required = set(range(1, ROSTERS[name] + 1))
    unstamped = sorted(required - stamped)
    missing_ids = sorted(i for i in missing if i in required)
    partial_ids = sorted(i for i in partial if i in required)
    present_count = len(present & required)
    if not missing_ids and not unstamped and not partial_ids:
        return (name, None, [], [], [])
    tally = (present_count, len(partial_ids), len(missing_ids),
             len(unstamped), len(required))
    return (name, tally,
            [(i, missing[i]) for i in missing_ids],
            unstamped,
            [(i, partial[i]) for i in partial_ids])


def main(argv):
    if argv:
        files = [(p, worktree_content(p)) for p in argv]
    else:
        files = [(p, staged_content(p)) for p in staged_md_files()]

    blocked = False
    lines = []

    for path, text in files:
        # citation-verifier - blocking
        fabs = find_fabricated(text)
        if fabs:
            blocked = True
            lines.append(
                f"BLOCKED [citation-verifier] {path}: a [FABRICATED] citation "
                "cannot be committed."
            )
            for i, line in fabs[:10]:
                lines.append(f"    {i}: {line.strip()}")
            lines.append(
                "    Resolve each (supply the real PMID, correct the fields, or "
                "reclassify the source), then re-stage and commit."
            )
        # reporting-guidelines - annotate only, never blocks
        rg = reporting_gaps(text)
        if rg and rg[1] is not None:
            name, tally, missing, unstamped, partial = rg
            pc, pa, mi, un, req = tally
            lines.append(
                f"REPORTING AUDIT [reporting-guidelines] {path}: {name} - "
                "commit NOT blocked."
            )
            lines.append(
                f"    PRESENT {pc} / PARTIAL {pa} / MISSING {mi} / "
                f"unstamped {un}  (required {req})"
            )
            if missing:
                lines.append("    MISSING:")
                lines += [f"      - {name}-{i}" + (f"  ({n})" if n else "")
                          for i, n in missing]
            if unstamped:
                lines.append("    UNSTAMPED:")
                lines += [f"      - {name}-{i}" for i in unstamped]
            if partial:
                lines.append("    PARTIAL:")
                lines += [f"      - {name}-{i}" + (f"  ({n})" if n else "")
                          for i, n in partial]

    if lines:
        sys.stderr.write("\n".join(lines) + "\n")
    if blocked:
        sys.stderr.write(
            "\nCommit aborted by Manuscript Harness (citation gate). A proven-"
            "wrong citation does not enter the repository.\n"
            "If this is a just-published paper whose PMID is issued but not yet "
            "live, confirm it manually and override with 'git commit "
            "--no-verify'.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
