#!/usr/bin/env python3
"""Normalize referenced post images to assets/posts/images/<Category>/<slug>.

The filename sequence prefix is intentionally not part of the image URL.  The
stable, human-readable post slug is the part after ``0000-XX-XX-``.
Run without --apply for a report.  With --apply, files are moved and Markdown
references are rewritten together.  A conflicting destination is never
overwritten.
"""
from __future__ import annotations

import argparse
import re
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS = list(ROOT.glob("*/_posts/*.md"))
IMAGE = re.compile(r"!\[([^]]*)\]\((/assets/posts/images/[^)\s]+)([^)]*)\)")
PREFIX = re.compile(r"^0000-\d{2}-\d{2}-(.+)\.md$")


def desired_url(post: Path, old_url: str) -> str:
    matched = PREFIX.match(post.name)
    if not matched:
        raise ValueError(f"unexpected post filename: {post.relative_to(ROOT)}")
    return f"/assets/posts/images/{post.parents[1].name}/{matched.group(1)}/{Path(old_url).name}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="move assets and rewrite Markdown")
    args = parser.parse_args()
    plans: list[tuple[Path, str, str]] = []
    usage: dict[Path, set[str]] = defaultdict(set)
    for post in POSTS:
        text = post.read_text(encoding="utf-8", errors="replace")
        for _, old, _ in IMAGE.findall(text):
            old_path = ROOT / old.lstrip("/")
            new = desired_url(post, old)
            if not old_path.is_file():
                print(f"MISSING {post.relative_to(ROOT)} :: {old}")
                continue
            plans.append((post, old, new))
            usage[old_path].add(new)

    errors = 0
    for old_path, destinations in usage.items():
        if len(destinations) > 1:
            errors += 1
            print(f"SHARED {old_path.relative_to(ROOT)} has multiple target folders: {sorted(destinations)}")
    for post, old, new in plans:
        if old == new:
            continue
        print(f"MOVE {old} -> {new}  ({post.relative_to(ROOT)})")
    if errors or not args.apply:
        print(f"Planned references: {len(plans)}; conflicts: {errors}; apply: {args.apply}")
        raise SystemExit(1 if errors else 0)

    replacements: dict[Path, list[tuple[str, str]]] = defaultdict(list)
    for post, old, new in plans:
        if old == new:
            continue
        old_path = ROOT / old.lstrip("/")
        new_path = ROOT / new.lstrip("/")
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if new_path.exists() and old_path.resolve() != new_path.resolve():
            raise RuntimeError(f"refusing to overwrite existing asset: {new_path}")
        if old_path.resolve() != new_path.resolve():
            shutil.move(str(old_path), str(new_path))
        replacements[post].append((old, new))
    for post, pairs in replacements.items():
        text = post.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        post.write_text(text, encoding="utf-8", newline="")
    print(f"Normalized {sum(len(v) for v in replacements.values())} image references in {len(replacements)} posts.")


if __name__ == "__main__":
    main()
