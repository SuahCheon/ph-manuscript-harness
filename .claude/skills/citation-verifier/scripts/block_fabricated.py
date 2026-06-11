#!/usr/bin/env python3
"""block_fabricated.py - PreToolUse gate for the citation-verifier skill.

Role: GATE, not verifier. Verification (PMID lookup, field matching) happens
upstream - Claude performs it with the PubMed MCP and writes the resulting
label into the manuscript. This hook only enforces the decision the label
already records.

What it blocks: only [FABRICATED] - a citation the upstream check *proved* wrong
(a non-existent PMID, or fields contradicting the record). Everything else
passes, including [UNVERIFIED], which marks a citation the check *could not
reach* (API outage, timeout). "Couldn't check" is not "is fake", so an outage
must never block a possibly-real citation; [UNVERIFIED] is a loud label, not a
stop. Verified and grey-literature citations carry their own labels
([PMID-VERIFIED], [GREY-LIT-*]) and pass through untouched.

Input  : tool-call JSON on stdin (PreToolUse schema).
Output : exit 0 = no decision, the write proceeds.
         exit 2 = blocking error, the write is cancelled and stderr is shown.

No third-party dependencies (json is stdlib), so it runs the same on Windows,
macOS, and Linux without jq or any external tool.
"""
import sys
import json

# Windows consoles default to a legacy code page (e.g. cp949), which can mangle
# non-ASCII bytes written to stderr. Force UTF-8 so the block message renders
# cleanly regardless of console encoding. (The message below is kept ASCII-only
# as a second layer, so it stays readable even if this reconfigure is a no-op.)
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

FABRICATED = "[FABRICATED]"


def main() -> int:
    # Read stdin as bytes and decode UTF-8 explicitly. Claude Code writes the
    # tool-call JSON as UTF-8; reading via sys.stdin.read() would instead use the
    # console locale (cp949 on Korean Windows), which mangles any non-ASCII
    # manuscript content and makes json.loads fail -> the gate would silently
    # pass (fail-open) a manuscript it never actually inspected. "utf-8-sig" also
    # absorbs a leading BOM if one is injected upstream (e.g. a PowerShell native
    # pipe), so the gate behaves the same regardless of how it was invoked.
    raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Malformed input is not a citation failure. Fail open on parsing so the
        # gate never blocks for reasons unrelated to verification.
        return 0

    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    # Write carries .content; Edit carries .new_string.
    text = tool_input.get("content") or tool_input.get("new_string") or ""

    # Guard: never gate the skill's own files. This SKILL.md documents the
    # [UNVERIFIED] token by name, so editing the skill must not trip its hook.
    norm = path.replace("\\", "/")
    if norm.endswith("SKILL.md") or "/.claude/" in norm:
        return 0

    if FABRICATED in text:
        offending = [
            f"{i}: {line}"
            for i, line in enumerate(text.splitlines(), 1)
            if FABRICATED in line
        ][:5]
        sys.stderr.write(
            "BLOCKED by citation-verifier: a [FABRICATED] citation cannot enter "
            "the manuscript.\n"
            "The upstream check completed and proved this wrong - a non-existent "
            "PMID, or fields contradicting the record.\n"
            "Resolve each one (supply the real PMID, correct the fields, or "
            "reclassify the source) before writing. If this is a just-published "
            "paper whose PMID is issued but not yet live, confirm it manually and "
            "override:\n"
            + "\n".join(offending)
            + "\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
