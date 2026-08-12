#!/usr/bin/env python3
"""Create a post without putting its publication date in the public URL."""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def next_sequence(post_dir: Path) -> int:
    highest = 0
    for path in post_dir.glob("*.md"):
        match = re.match(r"0000-(\d{2})-(\d{2})-", path.name)
        if match:
            highest = max(highest, int(match.group(1)) * 100 + int(match.group(2)))
    return highest + 1


def sequence_prefix(number: int) -> str:
    return f"0000-{number // 100:02}-{number % 100:02}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("category", help="Existing top-level category, e.g. WebLogic")
    parser.add_argument("slug", help="URL-safe title part, e.g. jdbc-store-recovery")
    parser.add_argument("--title", required=True)
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--date", help="Publication date/time in ISO form; defaults to now in +09:00")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.slug):
        parser.error("slug may contain only letters, digits, dot, underscore, and hyphen")
    post_dir = ROOT / args.category / "_posts"
    if not post_dir.is_dir():
        parser.error(f"category does not exist: {post_dir}")

    when = args.date or dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %z")
    tags = ", ".join(tag.strip() for tag in args.tags.split(",") if tag.strip())
    number = next_sequence(post_dir)
    path = post_dir / f"{sequence_prefix(number)}-{args.slug}.md"
    if path.exists():
        parser.error(f"refusing to overwrite existing post: {path}")

    image_dir = f"/assets/posts/images/{args.category}/{args.slug}"
    content = f'''---
layout: post
title: "{args.title.replace('"', "'")}"
description: ""
date: {when}
tags: [{tags}]
typora-root-url: ../..
---

# 1. Issue

<!-- SR symptom, customer impact, and a safely anonymized scope. -->

# 2. Cause

<!-- Evidence-led diagnosis. Clearly separate confirmed cause from hypotheses. -->

# 3. Solution

<!-- Corrective action, safe commands, prerequisites, and rollback considerations. -->

# 4. Verification

<!-- Observable result that proves the solution; include a safe test when possible. -->

# 5. References

<!-- Official public documents or safe external references. -->

<!-- Images for this post belong in {image_dir}/ -->
'''
    path.write_text(content, encoding="utf-8", newline="\n")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
