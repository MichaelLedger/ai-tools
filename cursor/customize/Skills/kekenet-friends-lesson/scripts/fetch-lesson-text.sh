#!/usr/bin/env bash
# Fetch kekenet lesson bilingual transcript into EscapeLineBreak words.txt format.
#
# Usage:
#   fetch-lesson-text.sh https://www.kekenet.com/lesson/16442-474658 [words.txt]
#   fetch-lesson-text.sh 474658
#
set -euo pipefail

API="https://mob2015.kekenet.com/keke/mobile/index.php"
AES_KEY="51E881E6F2A6Y9K8"
AES_IV="9F0885C2D686C418"

INPUT="${1:-}"
OUT_FILE="${2:-/Users/gavinxiang/Downloads/Shell-Collection/EscapeLineBreak/words.txt}"

[[ -n "$INPUT" ]] || {
  echo "Usage: $0 <kekenet-lesson-url|news_id> [words.txt]" >&2
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}
need curl
need jq
need openssl
need xxd
need python3

NEWS_ID="$(
  printf '%s' "$INPUT" \
    | sed -E 's#.*/lesson/##' \
    | sed -E 's#[?#].*$##' \
    | sed -E 's#.*/##' \
    | sed -E 's#^[0-9]+-([0-9]+)$#\1#' \
    | tr -d '[:space:]'
)"

if ! [[ "$NEWS_ID" =~ ^[0-9]+$ ]]; then
  echo "Could not parse lesson id from: $INPUT" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

APTIME="$(date +%s)000"
REQ="$(jq -nc \
  --arg id "$NEWS_ID" \
  --argjson aptime "$APTIME" \
  '{
    Method: "web_waikan_wkgetcontent",
    Params: { id: $id, version_flag: 1 },
    Token: "",
    Terminal: 13,
    Version: "4.0",
    UID: "",
    AppFlag: 18,
    Sign: "",
    ApTime: $aptime,
    ApVersionCode: 100
  }')"

curl -fsSL "$API" \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://www.kekenet.com' \
  -H 'Referer: https://www.kekenet.com/' \
  -A 'Mozilla/5.0' \
  --data-binary "$REQ" \
  >"$TMP/resp.json"

CODE="$(jq -r '.Code // .code // empty' "$TMP/resp.json")"
if [[ "$CODE" != "200" ]]; then
  echo "API error (Code=$CODE): $(jq -r '.Msg // .msg // empty' "$TMP/resp.json")" >&2
  exit 1
fi

KEY_HEX="$(printf '%s' "$AES_KEY" | xxd -p | tr -d '\n')"
IV_HEX="$(printf '%s' "$AES_IV" | xxd -p | tr -d '\n')"
IS_DECODE="$(jq -r '.IsDecode // 0' "$TMP/resp.json")"

if [[ "$IS_DECODE" == "1" ]]; then
  printf '%s' "$(jq -r '.Data // empty' "$TMP/resp.json")" | xxd -r -p \
    | openssl enc -d -aes-128-cbc -K "$KEY_HEX" -iv "$IV_HEX" \
    >"$TMP/data.json"
else
  jq -c '.Data' "$TMP/resp.json" >"$TMP/data.json"
fi

TITLE="$(jq -r '.title // empty' "$TMP/data.json")"
PLAY="$(jq -r '.playurl // .mp3 // empty' "$TMP/data.json")"

python3 - "$TMP/data.json" "$OUT_FILE" <<'PY'
import json, sys
from pathlib import Path

data = json.load(open(sys.argv[1], encoding="utf-8"))
out = Path(sys.argv[2])
content = data.get("content") or []
if not isinstance(content, list):
    raise SystemExit("Unexpected content shape (expected list of en/cn lines)")

lines = []
for item in content:
    if not isinstance(item, dict):
        continue
    en = (item.get("en") or "").strip()
    cn = (item.get("cn") or "").strip()
    if not en and not cn:
        continue
    if en:
        lines.append(en)
    if cn:
        lines.append(cn)

if not lines:
    raise SystemExit("No en/cn lines found in lesson content")

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {len(lines)} lines → {out}")
PY

echo "Lesson : ${TITLE:-?}"
echo "Audio  : ${PLAY:-?}"
echo "Text   : $OUT_FILE"
