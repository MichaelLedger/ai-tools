# descriptions.json Reference

## Schema

```json
{
  "<source_filename>": {
    "size": [<width>, <height>],
    "content_description": "<neutral description of what is in the source>",
    "variant_prompts": [
      "<prompt for similar_1>",
      "<prompt for similar_2>",
      "<prompt for similar_3>"
    ]
  }
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `size` | Optional | Source dimensions; informational only |
| `content_description` | Yes | Used when writing prompts; not sent to image API |
| `variant_prompts` | Yes | One prompt per variant; sent to generator |

Output files: `{stem}_similar_{n}{suffix}` e.g. `IMG_0053.JPG` → `IMG_0053_similar_1.JPG`.

## Example entry

Source: vertical car interior road-trip photo.

```json
{
  "IMG_0009.JPG": {
    "size": [1536, 2048],
    "content_description": "Vertical interior car photo from rear seat looking forward. Four people in black leather seats of a modern van/SUV. Driver in white shirt, elderly woman in striped shirt in middle row, rural road and green fields visible through windshield. Dashboard with infotainment screen, overhead console showing temperature.",
    "variant_prompts": [
      "Photorealistic vertical POV from third row of a Toyota Sienna minivan, family road trip, three passengers seen from behind in grey cloth seats, highway and trees through windshield, daylight, casual in-car snapshot",
      "Photorealistic vertical interior photo from back seat of a Honda Odyssey, two adults and a child in front rows, suburban street visible ahead, black leather interior, natural daylight through windows",
      "Photorealistic vertical candid photo from rear bench of a Volkswagen Caravelle on countryside road, four travelers in dark seats seen from behind, rolling green hills through front glass, dashboard lights on, travel photo"
    ]
  }
}
```

## Prompt writing tips

1. **Match format** — vertical/horizontal/overhead/close-up must match the source.
2. **Swap specifics** — brand, location, color, text language; keep category (map sign, damage photo, selfie).
3. **Match quality** — accidental blur, harsh shadow, rain droplets on signs when the source has them.
4. **Avoid copying** — no identical license plates, logos, or named people from the source.
5. **Photorealistic prefix** — improves consistency across variants.

## Progress file

`generation_progress.json` is auto-maintained:

```json
{
  "completed": ["IMG_0001_similar_1.JPG", "..."],
  "last_saved": "IMG_0001_similar_1.JPG"
}
```

Resume logic: first source in descriptions order whose `{stem}_similar_{n}` file is missing.
