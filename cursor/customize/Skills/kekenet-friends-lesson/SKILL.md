---
name: kekenet-friends-lesson
description: >-
  Download a kekenet Friends lesson audio, rename it to friends_sXXeYY_a/b.mp3,
  escape bilingual transcript into the next english_N.md, and append a matching
  item to michaelledger.github.io/blog/english.xml. Use when the user provides a
  kekenet.com/lesson link, asks to import a Friends English lesson, or mentions
  kekenet-lesson-dl / EscapeLineBreak for english blog episodes.
---

# Kekenet Friends Lesson Import

One kekenet lesson URL → one audio + one markdown + one `english.xml` blog item.

Canonical skill path (symlinked into `~/.cursor/skills/` for global use):

`/Users/gavinxiang/Downloads/ai-tools-private/.cursor/skills/kekenet-friends-lesson/`

## Paths

| Role | Path |
|------|------|
| Skill root | `/Users/gavinxiang/Downloads/ai-tools-private/.cursor/skills/kekenet-friends-lesson/` |
| Audio downloader | `/Users/gavinxiang/Downloads/Shell-Collection/Audio-Downloader/kekenet-lesson-dl.sh` |
| Line-break escaper | `/Users/gavinxiang/Downloads/Shell-Collection/EscapeLineBreak/` (`words.txt` → `shell.sh` → `escaped.txt`) |
| Audio output | `/Users/gavinxiang/Downloads/media` (git branch `audio/english/friends/seasonN`) |
| Markdown | `/Users/gavinxiang/Downloads/michaelledger.github.io/markdowns/english/english_{N}.md` |
| Catalog XML | `/Users/gavinxiang/Downloads/michaelledger.github.io/blog/english.xml` |

## Checklist

```
Progress:
- [ ] 1. Download audio
- [ ] 2. Rename to friends_sXXeYY_a|b.mp3
- [ ] 3. Extract bilingual transcript → EscapeLineBreak → english_{id}.md
- [ ] 4. Append english.xml <blog> item (id+1, today date, cover unchanged, audio basename only)
- [ ] 5. Summarize paths / id / title / audio name for the user
```

Do **not** git commit or push unless the user asks.

---

## Step 1 — Download audio

Ensure media repo is on the correct season branch before saving:

```bash
cd /Users/gavinxiang/Downloads/media
git checkout audio/english/friends/season9   # use seasonN from the lesson
```

Download into media root:

```bash
sh /Users/gavinxiang/Downloads/Shell-Collection/Audio-Downloader/kekenet-lesson-dl.sh \
  'https://www.kekenet.com/lesson/CATID-NEWSID' \
  -o /Users/gavinxiang/Downloads/media
```

CDN basename looks like `friendss09e16a.mp3` (no underscores).

---

## Step 2 — Rename audio

Target convention (must match existing files):

`friends_s{SS}e{EE}_{a|b}.mp3`

Examples:

| Downloaded | Renamed |
|------------|---------|
| `friendss09e16a.mp3` | `friends_s09e16_a.mp3` |
| `friendss09e17b.mp3` | `friends_s09e17_b.mp3` |

Rules:

- `a` → Part One; `b` → Part Two
- Zero-pad season/episode to 2 digits (`s09`, `e16`)
- Keep file in `/Users/gavinxiang/Downloads/media` (season branch working tree root)

Helper:

```bash
sh /Users/gavinxiang/Downloads/ai-tools-private/.cursor/skills/kekenet-friends-lesson/scripts/rename-friends-audio.sh \
  /Users/gavinxiang/Downloads/media/friendss09e16a.mp3
```

---

## Step 3 — Transcript → markdown

### 3a. Collect bilingual lines

Prefer the same kekenet mobile API used by `kekenet-lesson-dl.sh` (page HTML is JS-rendered). Helper writes plain multiline text for EscapeLineBreak:

```bash
sh /Users/gavinxiang/Downloads/ai-tools-private/.cursor/skills/kekenet-friends-lesson/scripts/fetch-lesson-text.sh \
  'https://www.kekenet.com/lesson/16442-474658' \
  /Users/gavinxiang/Downloads/Shell-Collection/EscapeLineBreak/words.txt
```

Output format for `words.txt` (one utterance per line, EN then CN alternating):

```text
English line one.
中文第一行。
English line two.
中文第二行。
```

Source: API `Data.content[]` fields `en` / `cn`. Skip empty pairs.

### 3b. Escape line breaks

```bash
cd /Users/gavinxiang/Downloads/Shell-Collection/EscapeLineBreak
sh shell.sh
```

Result: `escaped.txt` — single line with literal `\n` separators (also copied to clipboard).

### 3c. Write next markdown

```bash
NEXT=$(ls /Users/gavinxiang/Downloads/michaelledger.github.io/markdowns/english/english_*.md \
  | sed -E 's/.*english_([0-9]+)\.md/\1/' | sort -n | tail -1)
NEXT=$((NEXT + 1))
cp /Users/gavinxiang/Downloads/Shell-Collection/EscapeLineBreak/escaped.txt \
  "/Users/gavinxiang/Downloads/michaelledger.github.io/markdowns/english/english_${NEXT}.md"
```

Markdown body is **only** the escaped transcript (no frontmatter, no title). `english_N.md` number **equals** the new XML `<id>`.

---

## Step 4 — Append `english.xml`

Read the last `<blog>` block (max `<id>`) and insert a **new** item before `</blogs>`.

### Fields

| Field | Rule |
|-------|------|
| `<id>` | last id + 1 (same as markdown number) |
| `<date>` | today, format like `Jul 28, 2026` (`%b %-d, %Y`; on macOS use `date '+%b %d, %Y' \| sed 's/ 0/ /'`) |
| `<title>` | English episode title for this lesson (see below) |
| `<cover>` | **unchanged** — copy from the previous Friends item for the same season |
| `<audio>` | same URL prefix; **only** change the final filename to the renamed mp3 |

### Title format

```text
Friends S{SS}E{EE}: {English Episode Name}(Part One|Part Two)
```

Examples:

```text
Friends S09E16: The One With The Boob Job(Part One)
Friends S09E17: The One With The Memorial Service(Part Two)
```

How to build it:

1. Season / episode / part from CDN basename (`friendss09e16a` → S09E16 Part One) or Chinese title (`第9季:第16集 …(上|下)`).
2. English episode name: reuse the title already used for that `SxxExx` in `english.xml` if present; otherwise use the canonical Friends English episode title (e.g. Wikipedia / prior season entries). Do **not** leave the Chinese kekenet title in XML.
3. `(上)` / `a` → `(Part One)`; `(下)` / `b` → `(Part Two)`.

### XML item template (Friends season 9 style — no `<description>`)

```xml
    <blog>
        <id>539</id>
        <date>Jul 28, 2026</date>
        <title>Friends S09E18: Some Episode Title(Part One)</title>
        <cover>https://raw.githubusercontent.com/michaelledger/media/refs/heads/image/english/friends/cover/friends_season9_cover.jpg</cover>
        <audio>https://raw.githubusercontent.com/michaelledger/media/refs/heads/audio/english/friends/season9/friends_s09e18_a.mp3</audio>
    </blog>
```

Cover pattern for other seasons:

`.../image/english/friends/cover/friends_season{N}_cover.jpg`

Audio URL prefix must stay:

`https://raw.githubusercontent.com/michaelledger/media/refs/heads/audio/english/friends/season{N}/`

Only the trailing `friends_sXXeYY_a.mp3` (or `_b`) changes.

Preserve XML comment rules at file top (`&` → `and`, no raw `&rsquo;` / `<br/>` in titles/text).

---

## Step 5 — Report

Tell the user:

- Lesson title (EN XML title + Chinese source title)
- Audio path + renamed filename
- Markdown path (`english_{N}.md`)
- New XML id / date
- That media + site repos still need commit/push if they want remote update

---

## Notes

- One URL = one part (a **or** b), not both halves.
- Network calls to kekenet API may need full permissions (403 in restricted sandbox).
- Do not invent a new cover URL; clone the previous same-season cover.
- Early `english.xml` items may include `<description>`; new Friends items omit it — match the recent Friends blocks.
