#!/usr/bin/env python3
"""post_write_reporting_check.py - PostToolUse checkpoint for reporting-guidelines.

Role: CHECKPOINT, not auditor. The audit (which guideline applies, whether each
item is adequately reported) happens upstream - Claude runs the checklist and
writes a [REPORTING-GUIDELINE: NAME] declaration plus one [NAME-ID: STATUS] stamp
per item into the manuscript. This hook fires AFTER the save, reads only those
markers, and reports the gaps.

It does NOT block. At PostToolUse the write has already happened, so exit 2 here
surfaces the audit to Claude as feedback - it does not and cannot undo the save.
That is the design: a missing reporting item is fixable and progressive, so the
enforcement is one notch softer than citation-verifier's PreToolUse deny. The
check cannot be skipped (it runs on every manuscript save), but it annotates
instead of blocking.

What counts as a gap, for the guideline named in the declaration:
  - an item stamped MISSING               (required, not addressed)
  - a required item with no stamp at all  (the check was silently skipped)
  - an item stamped PARTIAL               (addressed but incomplete)
The audit passes (exit 0) only when every required item is stamped PRESENT. A
file with no [REPORTING-GUIDELINE: ...] declaration is treated as not-under-audit
and passes silently - the skill discipline is what adds the declaration.

Input  : tool-call JSON on stdin (PostToolUse schema).
Output : exit 0 = no gaps (or nothing to audit); nothing surfaced.
         exit 2 = gaps found; the report on stderr is shown to Claude. The save
                  is NOT reverted - this is an annotation, not a block.

No third-party dependencies (json + re are stdlib), so it runs the same on
Windows, macOS, and Linux without jq or any external tool.
"""
import sys
import re
import json

# Windows consoles default to a legacy code page (e.g. cp949), which can mangle
# non-ASCII bytes written to stderr. Force UTF-8 so the report renders cleanly.
# (The messages below are kept ASCII-only as a second layer.)
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Required item-ID roster per v1 guideline. The hook needs only the *count* of
# required IDs - the human-readable item labels live in SKILL.md, not here, so
# the hook stays a pure marker-reader and never judges prose. Adding a guideline
# later is one line here plus its roster in SKILL.md.
ROSTERS = {
    "STROBE": 22,
    "CONSORT": 25,
    "PRISMA": 27,
    "TRIPOD+AI": 27,
}

DECL_RE = re.compile(r"\[REPORTING-GUIDELINE:\s*([^\]]+?)\s*\]")


def required_ids(name):
    n = ROSTERS[name]
    return set(range(1, n + 1))


def main() -> int:
    # Read stdin as bytes and decode UTF-8 explicitly. Claude Code writes the
    # tool-call JSON as UTF-8; reading via sys.stdin.read() would instead use the
    # console locale (cp949 on Korean Windows), which mangles any non-ASCII
    # manuscript content and makes json.loads fail -> the audit would be silently
    # skipped (fail-open). "utf-8-sig" also absorbs a leading BOM if one is
    # injected upstream (e.g. a PowerShell native pipe), so the gate behaves the
    # same regardless of how it was invoked.
    raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Malformed input is not an audit failure. Fail open on parsing so the
        # checkpoint never fires for reasons unrelated to reporting.
        return 0

    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    # Write carries .content; Edit carries .new_string.
    text = tool_input.get("content") or tool_input.get("new_string") or ""

    # Guard: never audit the skill's own files. This SKILL.md documents the
    # marker tokens by name, so editing the skill must not trip its own hook.
    norm = path.replace("\\", "/")
    if norm.endswith("SKILL.md") or "/.claude/" in norm:
        return 0

    decl = DECL_RE.search(text)
    if not decl:
        # No guideline declared -> treat as not-under-audit, pass silently.
        return 0

    name = decl.group(1).strip().upper()
    if name not in ROSTERS:
        # A guideline we do not yet roster (STARD, RECORD, SPIRIT, ...). Out of
        # v1 scope; do not invent an audit for it. Pass silently.
        return 0

    # Parse one stamp per item for THIS guideline. Build the stamp pattern from
    # the declared name so the '+' in TRIPOD+AI is matched literally and never
    # confused with another guideline's stamps.
    stamp_re = re.compile(
        r"\[" + re.escape(name) + r"-(\d+):\s*(PRESENT|PARTIAL|MISSING)\s*\]"
        r"[ \t]*(.*)",
        re.IGNORECASE,
    )

    present = set()
    partial = {}   # id -> trailing note
    missing = {}   # id -> trailing note
    stamped = set()
    for m in stamp_re.finditer(text):
        item_id = int(m.group(1))
        status = m.group(2).upper()
        # Markers are HTML comments, so the trailing "-->" leaks into the note;
        # strip it (and any whitespace) so the report stays clean.
        note = re.sub(r"\s*-->\s*$", "", m.group(3)).strip()
        stamped.add(item_id)
        if status == "PRESENT":
            present.add(item_id)
        elif status == "PARTIAL":
            partial[item_id] = note
        else:
            missing[item_id] = note

    required = required_ids(name)
    unstamped = sorted(required - stamped)
    missing_ids = sorted(i for i in missing if i in required)
    partial_ids = sorted(i for i in partial if i in required)
    present_count = len(present & required)

    # Pass only when every required item is stamped PRESENT.
    if not missing_ids and not unstamped and not partial_ids:
        return 0

    def line(item_id, note):
        return f"  - {name}-{item_id}" + (f"  ({note})" if note else "")

    out = [
        f"REPORTING AUDIT (reporting-guidelines): {name} - NOT blocked, the "
        "manuscript was saved.",
        "This is a completeness check; resolve the gaps below before submission.",
        f"PRESENT {present_count} / PARTIAL {len(partial_ids)} / "
        f"MISSING {len(missing_ids)} / unstamped {len(unstamped)}  "
        f"(required: {len(required)})",
    ]
    if missing_ids:
        out.append("MISSING (required, not addressed):")
        out += [line(i, missing[i]) for i in missing_ids]
    if unstamped:
        out.append("UNSTAMPED (required item never assessed):")
        out += [f"  - {name}-{i}" for i in unstamped]
    if partial_ids:
        out.append("PARTIAL (addressed but incomplete):")
        out += [line(i, partial[i]) for i in partial_ids]

    sys.stderr.write("\n".join(out) + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
