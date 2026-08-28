---
name: generate-similar-photos
description: >-
  Generate new similar photos from source images using content descriptions and
  variant prompts (not augmentations). Resumable one-by-one generation via
  Cursor GenerateImage or batch via OpenAI API. Use when the user asks to
  generate similar photos, create training variants, continue/resume image
  generation, write descriptions.json, or build a similar-photo dataset.
---

# Generate Similar Photos

Create **new** photos that match the **content** of source images — same scene type, composition, and intent — but with different subjects/details. This is **not** augmentation (no crop, flip, blur, or color jitter).

## Directory layout

```
project/
├── source/              # originals (e.g. bad/)
├── similar/             # generated variants (e.g. bad-similar/)
│   ├── descriptions.json
│   └── generation_progress.json
└── generate_similar.py  # optional project copy of the script
```

Default script paths: `--source-dir source --out-dir similar`. For existing Desktop setup use `--source-dir bad --out-dir bad-similar --root ~/Desktop`.

## Phase 1: Write descriptions.json

Create `similar/descriptions.json` before generating. One entry per source image:

```json
{
  "IMG_0001.JPG": {
    "size": [1536, 2048],
    "content_description": "What is in the photo: subject, angle, lighting, context.",
    "variant_prompts": [
      "Photorealistic prompt for variant 1 — same content type, different details",
      "Photorealistic prompt for variant 2",
      "Photorealistic prompt for variant 3"
    ]
  }
}
```

**Rules for variant prompts:**
- Start with `Photorealistic` and match orientation (vertical/horizontal/overhead).
- Preserve scene **type** (car damage, map sign, accidental snapshot) — change make/model, location, wording.
- Match casual snapshot quality when sources are amateur phone photos.
- Provide **3 prompts per source** unless the user specifies otherwise.
- Output naming is automatic: `{stem}_similar_{1|2|3}{source_suffix}`.

**To bootstrap:** view each source image, write `content_description`, then draft 3 distinct variant prompts. See [reference.md](reference.md) for a full example entry.

## Phase 2: Generate images

Script location: `scripts/generate_similar.py` in this skill directory.

```bash
SCRIPT=~/.cursor/skills/generate-similar-photos/scripts/generate_similar.py
ROOT=/path/to/project

python3 "$SCRIPT" --root "$ROOT" --source-dir bad --out-dir bad-similar --status
python3 "$SCRIPT" --root "$ROOT" --source-dir bad --out-dir bad-similar --next
```

### Method A: Cursor GenerateImage (interactive, default when user says "one by one")

Loop until `--next` returns `ALL_DONE`:

1. Run `--next` → get `out_name` and `prompt`.
2. Call **GenerateImage** with `filename` = `out_name` and the prompt as `description`.
3. Run `--mark-done OUT_NAME` — copies from Cursor assets dir into `similar/` and updates progress.
4. Report progress with `--status`.

**Do not resize** generated images. Save at native resolution.

When user says **continue**, resume from `--next` without resetting.

### Method B: OpenAI API (unattended batch)

Requires `OPENAI_API_KEY` in env or project `.env`.

```bash
python3 "$SCRIPT" --root "$ROOT" --generate-one    # one image
python3 "$SCRIPT" --root "$ROOT" --generate-all    # all remaining
```

Uses `gpt-image-1` at 1024×1024. No resize applied on save.

## Commands reference

| Command | Purpose |
|---------|---------|
| `--status` | Progress count, last saved, next job |
| `--next` | JSON for next missing image (or `ALL_DONE`) |
| `--mark-done NAME` | Register file after GenerateImage |
| `--generate-one` | API: generate next missing |
| `--generate-all` | API: generate all remaining |
| `--reset` | Delete generated images, keep descriptions |

## Agent checklist

```
- [ ] Confirm source/ and similar/ paths with user (or infer from project)
- [ ] descriptions.json exists with variant_prompts for each source
- [ ] Run --status to see progress
- [ ] Generate one image at a time unless user asks for batch/API
- [ ] Always --mark-done after each GenerateImage
- [ ] Never resize outputs
- [ ] Report N/total after each batch
```

## Common user phrases

| User says | Action |
|-----------|--------|
| "continue" | `--next` → GenerateImage → `--mark-done` → repeat |
| "generate similar photos" | Start Phase 1 if no descriptions.json, else Phase 2 |
| "one by one" | Method A only |
| "generate all" / "batch" | Method B with `--generate-all` |
| "reset" | `--reset`, confirm with user first |

## Additional resources

- Full descriptions.json example: [reference.md](reference.md)
