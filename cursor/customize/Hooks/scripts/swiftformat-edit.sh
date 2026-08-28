#!/usr/bin/env bash
#
# Created by Gavin Xiang on 8/28/26.
#
# Cursor afterFileEdit hook: run swiftformat on Swift files the agent edits.
# Always exits 0 - a formatting failure must never block an edit.

set -uo pipefail

input=$(cat)

SWIFTFORMAT="$(command -v swiftformat 2>/dev/null || true)"
[ -x "$SWIFTFORMAT" ] || SWIFTFORMAT=/opt/homebrew/bin/swiftformat
[ -x "$SWIFTFORMAT" ] || exit 0

PYTHON="$(command -v python3 2>/dev/null || true)"
[ -x "$PYTHON" ] || PYTHON=/usr/bin/python3
[ -x "$PYTHON" ] || exit 0

# The payload shape varies by Cursor version, so walk the whole JSON tree and
# pick up anything that looks like a path to an edited file.
files=$(printf '%s' "$input" | "$PYTHON" -c '
import json, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

paths = []

def collect(value):
    if isinstance(value, str):
        paths.append(value)
    elif isinstance(value, list):
        for item in value:
            collect(item)
    elif isinstance(value, dict):
        for key in ("file_path", "filePath", "path", "absolute_path", "uri"):
            if key in value:
                collect(value[key])
        for key in ("edits", "files", "changes"):
            if key in value:
                collect(value[key])

collect(data)

seen = set()
for path in paths:
    if path.startswith("file://"):
        path = path[len("file://"):]
    if path.endswith(".swift") and path not in seen:
        seen.add(path)
        print(path)
')

[ -n "$files" ] || exit 0

while IFS= read -r file; do
    [ -f "$file" ] || continue
    "$SWIFTFORMAT" "$file" >/dev/null 2>&1 || true
done <<<"$files"

exit 0
