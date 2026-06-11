#!/bin/sh
# new-paper.sh - set up a fresh manuscript folder wired for Manuscript Harness.
#
# Usage:   scripts/new-paper.sh <target-folder>
# Example: scripts/new-paper.sh ~/papers/2026-aefi
#
# Copies this repo's .claude/skills/ into <target-folder>/.claude/skills/ so that
# running Claude Code from <target-folder> finds the citation-verifier and
# reporting-guidelines skills (and their write-time hooks) via
# ${CLAUDE_PROJECT_DIR}. Creates an empty manuscript.md if none exists.
# Paths resolve relative to this script, so the repo can live anywhere.
set -eu

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "usage: $0 <target-folder>" >&2
  echo "example: $0 ~/papers/2026-aefi" >&2
  exit 2
fi

# Repo root = parent of this script's directory (scripts/ sits at the repo root).
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$SCRIPT_DIR/.." && pwd)
SRC="$REPO/.claude/skills"

if [ ! -d "$SRC/citation-verifier" ] || [ ! -d "$SRC/reporting-guidelines" ]; then
  echo "error: skills not found under $SRC" >&2
  echo "run this from a clone of the Manuscript Harness repo." >&2
  exit 1
fi

mkdir -p "$TARGET/.claude/skills"
rm -rf "$TARGET/.claude/skills/citation-verifier" "$TARGET/.claude/skills/reporting-guidelines"
cp -R "$SRC/citation-verifier"    "$TARGET/.claude/skills/"
cp -R "$SRC/reporting-guidelines" "$TARGET/.claude/skills/"

if [ ! -e "$TARGET/manuscript.md" ]; then
  printf '# (new manuscript)\n' > "$TARGET/manuscript.md"
fi

if [ ! -e "$TARGET/HOWTO.md" ] && [ -e "$SCRIPT_DIR/paper-howto-template.md" ]; then
  cp "$SCRIPT_DIR/paper-howto-template.md" "$TARGET/HOWTO.md"
fi

echo "Manuscript Harness: set up '$TARGET'."
echo "  copied skills: citation-verifier, reporting-guidelines"
echo "  created: manuscript.md (edit this), HOWTO.md (how to use this folder)"
echo
echo "Next: open a terminal in '$TARGET', start Claude Code there, then ask e.g.:"
echo "  - verify the citations in manuscript.md with citation-verifier"
echo "  - check manuscript.md against the reporting guideline"
echo "(The hooks call 'python'; on macOS/Linux set the SKILL.md frontmatter"
echo " 'command' to 'python3' if 'python' is absent.)"
