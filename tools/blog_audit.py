#!/usr/bin/env python3
"""Audit source posts without modifying their content."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS = [p for p in ROOT.glob("*/_posts/*.md") if p.name != "template.md"]
IMAGE = re.compile(r"!\[[^]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SECRET = re.compile(r"(?i)(?:password|passphrase|secret|api[_ -]?key|token)\s*(?:=|:)\s*(?!<|\$\{|\*{3}|\.\.\.)\S+")
DATE_PREFIX = re.compile(r"^0000-\d{2}-\d{2}-(.+)\.md$")


def warn(path: Path, line: int, message: str) -> None:
    print(f"WARN {path.relative_to(ROOT)}:{line}: {message}")


def post_url(path: Path) -> str | None:
    match = DATE_PREFIX.match(path.name)
    if not match:
        return None
    return f"/{path.parents[1].name.lower()}/{match.group(1)}"


def main() -> None:
    urls: dict[str, list[Path]] = defaultdict(list)
    warnings = 0
    for path in POSTS:
        url = post_url(path)
        if url:
            urls[url].append(path)
        else:
            warn(path, 1, "filename does not use the preserved 0000-XX-XX prefix")
            warnings += 1
        if path.name.endswith(".md.md"):
            warn(path, 1, "double .md extension changes the public URL")
            warnings += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        in_fence = False
        for number, line in enumerate(text.splitlines(), 1):
            if SECRET.search(line):
                warn(path, number, "possible credential literal; verify it is a disposable example or replace it")
                warnings += 1
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if re.search(r"`[^`]*!\[[^]]*\]\([^)]*\)[^`]*`", line):
                continue
            for source in IMAGE.findall(line):
                if re.match(r"^https?://", source):
                    continue
                if source.startswith("/assets/"):
                    if not (ROOT / source.lstrip("/")).is_file():
                        warn(path, number, "image points to a missing file below assets/")
                        warnings += 1
                    continue
                if re.match(r"^(file:|[A-Za-z]:[\\/]|\\\\|/(?:\.\./)+)", source):
                    warn(path, number, "image uses a local filesystem path; import it under assets/posts/images and use /assets/...")
                else:
                    warn(path, number, "image is not root-relative; it may break after publishing")
                warnings += 1
    for url, paths in sorted(urls.items()):
        if len(paths) > 1:
            print(f"ERROR duplicate output URL {url}")
            for path in paths:
                print(f"  - {path.relative_to(ROOT)}")
    print(f"Checked {len(POSTS)} posts; warnings: {warnings}; duplicate URLs: {sum(len(v) > 1 for v in urls.values())}")


if __name__ == "__main__":
    main()
