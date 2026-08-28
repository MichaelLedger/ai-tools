#!/usr/bin/env python3
"""Generate similar photos from content descriptions (not augmentations).

Resumable pipeline:
1. Read descriptions.json (content_description + variant_prompts per source)
2. Generate images one at a time
3. Save at native generated resolution (no resize)

Usage:
  python3 generate_similar.py --root /path/to/project --status
  python3 generate_similar.py --root /path/to/project --next
  python3 generate_similar.py --root /path/to/project --mark-done OUT_NAME
  OPENAI_API_KEY=... python3 generate_similar.py --root /path/to/project --generate-one
  OPENAI_API_KEY=... python3 generate_similar.py --root /path/to/project --generate-all
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

DEFAULT_SOURCE = "source"
DEFAULT_OUT = "similar"
DESCRIPTIONS_NAME = "descriptions.json"
PROGRESS_NAME = "generation_progress.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate similar photos from prompts")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: cwd)",
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=DEFAULT_SOURCE,
        help=f"Source images directory relative to root (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=DEFAULT_OUT,
        help=f"Output directory relative to root (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=None,
        help="Cursor assets dir for --mark-done copies (auto-detected if omitted)",
    )
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--next", action="store_true")
    parser.add_argument("--mark-done", metavar="OUT_NAME")
    parser.add_argument("--generate-one", action="store_true")
    parser.add_argument("--generate-all", action="store_true")
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> dict:
    root = args.root.resolve()
    source_dir = root / args.source_dir
    out_dir = root / args.out_dir
    descriptions_file = out_dir / DESCRIPTIONS_NAME
    progress_file = out_dir / PROGRESS_NAME

    assets_dir = args.assets_dir
    if assets_dir is None:
        slug = str(root).replace("/", "-").lstrip("-")
        candidate = Path.home() / ".cursor" / "projects" / slug / "assets"
        assets_dir = candidate if candidate.exists() else None

    return {
        "root": root,
        "source_dir": source_dir,
        "out_dir": out_dir,
        "descriptions_file": descriptions_file,
        "progress_file": progress_file,
        "assets_dir": assets_dir,
    }


def load_descriptions(paths: dict) -> dict:
    if not paths["descriptions_file"].exists():
        raise SystemExit(f"Missing {paths['descriptions_file']}")
    return json.loads(paths["descriptions_file"].read_text())


def load_progress(paths: dict) -> dict:
    if paths["progress_file"].exists():
        return json.loads(paths["progress_file"].read_text())
    return {"completed": [], "last_saved": None}


def save_progress(paths: dict, progress: dict) -> None:
    paths["out_dir"].mkdir(parents=True, exist_ok=True)
    paths["progress_file"].write_text(json.dumps(progress, indent=2) + "\n")


def iter_jobs(paths: dict, descriptions: dict):
    for source_name, entry in descriptions.items():
        source_path = paths["source_dir"] / source_name
        if not source_path.exists():
            continue
        prompts = entry.get("variant_prompts", [])
        for idx, prompt in enumerate(prompts, start=1):
            out_name = f"{source_path.stem}_similar_{idx}{source_path.suffix}"
            yield {
                "source_name": source_name,
                "out_name": out_name,
                "out_path": paths["out_dir"] / out_name,
                "source_path": source_path,
                "prompt": prompt,
                "variant_index": idx,
            }


def next_missing_job(paths: dict, descriptions: dict | None = None):
    descriptions = descriptions or load_descriptions(paths)
    for job in iter_jobs(paths, descriptions):
        if not job["out_path"].exists():
            return job
    return None


def save_like_source(img: Image.Image, out_path: Path, source_path: Path) -> None:
    ext = source_path.suffix.lower()
    rgb = img.convert("RGB")
    if ext in {".jpg", ".jpeg"}:
        rgb.save(out_path, "JPEG", quality=92, optimize=True)
    elif ext == ".png":
        rgb.save(out_path, "PNG", optimize=True)
    else:
        rgb.save(out_path, quality=92)


def mark_done(paths: dict, out_name: str) -> None:
    descriptions = load_descriptions(paths)
    job = None
    for candidate in iter_jobs(paths, descriptions):
        if candidate["out_name"] == out_name:
            job = candidate
            break
    if job is None:
        raise SystemExit(f"Unknown output name: {out_name}")

    out_path = job["out_path"]
    if not out_path.exists():
        assets_dir = paths["assets_dir"]
        if assets_dir:
            assets_path = assets_dir / out_name
            if assets_path.exists():
                paths["out_dir"].mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(assets_path.read_bytes())
            else:
                raise SystemExit(
                    f"File not found: {out_path} (also checked {assets_path})"
                )
        else:
            raise SystemExit(f"File not found: {out_path}")

    with Image.open(out_path) as img:
        w, h = img.size

    progress = load_progress(paths)
    if out_name not in progress["completed"]:
        progress["completed"].append(out_name)
    progress["last_saved"] = out_name
    save_progress(paths, progress)
    print(f"Registered {out_name} ({w}x{h}), no resize applied")


def print_status(paths: dict) -> None:
    descriptions = load_descriptions(paths)
    jobs = list(iter_jobs(paths, descriptions))
    done = sum(1 for j in jobs if j["out_path"].exists())
    progress = load_progress(paths)
    print(f"Progress: {done}/{len(jobs)} images saved")
    if progress.get("last_saved"):
        print(f"Last saved: {progress['last_saved']}")
    nxt = next_missing_job(paths, descriptions)
    if nxt:
        print(f"Next: {nxt['out_name']}")
        print(f"Prompt: {nxt['prompt']}")
    else:
        print("All done.")


def print_next(paths: dict) -> None:
    job = next_missing_job(paths)
    if not job:
        print("ALL_DONE")
        return
    print(
        json.dumps(
            {
                "out_name": job["out_name"],
                "source_name": job["source_name"],
                "prompt": job["prompt"],
            },
            indent=2,
        )
    )


def load_api_key(root: Path) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    for env_file in (root / ".env", root / "similar" / ".env"):
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("Set OPENAI_API_KEY or add it to .env in project root")


def generate_with_openai(prompt: str, api_key: str) -> Image.Image:
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        },
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    item = payload["data"][0]
    if "b64_json" in item:
        raw = base64.b64decode(item["b64_json"])
    elif "url" in item:
        raw = requests.get(item["url"], timeout=180).content
    else:
        raise RuntimeError("Unexpected OpenAI image response")
    return Image.open(BytesIO(raw))


def generate_one_job(paths: dict, job: dict, api_key: str) -> None:
    print(f"Generating {job['out_name']} ...")
    img = generate_with_openai(job["prompt"], api_key)
    paths["out_dir"].mkdir(parents=True, exist_ok=True)
    save_like_source(img, job["out_path"], job["source_path"])
    mark_done(paths, job["out_name"])


def generate_one_via_api(paths: dict) -> None:
    job = next_missing_job(paths)
    if not job:
        print("All images already generated.")
        return
    generate_one_job(paths, job, load_api_key(paths["root"]))


def generate_all_via_api(paths: dict) -> None:
    api_key = load_api_key(paths["root"])
    descriptions = load_descriptions(paths)
    jobs = [j for j in iter_jobs(paths, descriptions) if not j["out_path"].exists()]
    if not jobs:
        print("All images already generated.")
        return
    print(f"Generating {len(jobs)} remaining images (no resize)...")
    for i, job in enumerate(jobs, start=1):
        print(f"[{i}/{len(jobs)}]", end=" ")
        try:
            generate_one_job(paths, job, api_key)
        except Exception as exc:
            print(f"Failed on {job['out_name']}: {exc}")
            raise
    print_status(paths)


def reset_outputs(paths: dict) -> None:
    if paths["out_dir"].exists():
        for path in paths["out_dir"].iterdir():
            if path.name in {DESCRIPTIONS_NAME, PROGRESS_NAME}:
                continue
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                path.unlink()
    save_progress(paths, {"completed": [], "last_saved": None})
    print("Cleared generated images and reset progress.")


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)

    if args.reset:
        reset_outputs(paths)
    elif args.status:
        print_status(paths)
    elif args.next:
        print_next(paths)
    elif args.generate_one:
        generate_one_via_api(paths)
    elif args.generate_all:
        generate_all_via_api(paths)
    elif args.mark_done:
        mark_done(paths, args.mark_done)
    else:
        raise SystemExit(
            "Use --status, --next, --mark-done OUT_NAME, --generate-one, "
            "--generate-all, or --reset"
        )


if __name__ == "__main__":
    main()
