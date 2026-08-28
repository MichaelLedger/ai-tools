#!/usr/bin/env bash
# Rename kekenet Friends CDN audio to local convention:
#   friendss09e16a.mp3 → friends_s09e16_a.mp3
#
# Usage:
#   rename-friends-audio.sh /path/to/friendss09e16a.mp3
#   rename-friends-audio.sh /path/to/friendss09e16a.mp3 /Users/gavinxiang/Downloads/media
#
set -euo pipefail

SRC="${1:-}"
OUT_DIR="${2:-}"

[[ -n "$SRC" ]] || {
  echo "Usage: $0 <downloaded-mp3> [output-dir]" >&2
  exit 1
}
[[ -f "$SRC" ]] || {
  echo "File not found: $SRC" >&2
  exit 1
}

BASE="$(basename "$SRC")"
# Accept friendss09e16a.mp3 / friends_s09e16_a.mp3 / FriendsS09E16A.mp3
LOWER="$(printf '%s' "$BASE" | tr '[:upper:]' '[:lower:]')"

if [[ "$LOWER" =~ ^friends_?s([0-9]{1,2})_?e([0-9]{1,2})_?([ab])\.mp3$ ]]; then
  SS="$(printf '%02d' "$((10#${BASH_REMATCH[1]}))")"
  EE="$(printf '%02d' "$((10#${BASH_REMATCH[2]}))")"
  PART="${BASH_REMATCH[3]}"
elif [[ "$LOWER" =~ ^friendss([0-9]{2})e([0-9]{2})([ab])\.mp3$ ]]; then
  SS="${BASH_REMATCH[1]}"
  EE="${BASH_REMATCH[2]}"
  PART="${BASH_REMATCH[3]}"
else
  echo "Unrecognized Friends audio name: $BASE" >&2
  echo "Expected like: friendss09e16a.mp3" >&2
  exit 1
fi

NEW_NAME="friends_s${SS}e${EE}_${PART}.mp3"
DIR="${OUT_DIR:-$(dirname "$SRC")}"
DEST="${DIR%/}/${NEW_NAME}"

SRC_ABS="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
DEST_ABS="$(cd "$DIR" && pwd)/$NEW_NAME"

if [[ "$SRC_ABS" == "$DEST_ABS" ]]; then
  echo "Already named: $DEST"
  exit 0
fi

mv "$SRC" "$DEST"
echo "Renamed: $BASE → $DEST"
