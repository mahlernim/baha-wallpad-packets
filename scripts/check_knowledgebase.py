#!/usr/bin/env python3
"""Check local links and complete BAHA frame examples; never access devices/network."""

import re
import sys
from collections import Counter
from functools import reduce
from operator import xor
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FRAME = re.compile(r"(?<![0-9A-Za-z])02(?:[ \t]+[0-9A-Fa-f]{2}){6,}(?![0-9A-Za-z])")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ID = re.compile(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', re.IGNORECASE)


def anchors(text):
    """GitHub-style heading IDs, plus explicit stable source IDs."""
    result = set(EXPLICIT_ID.findall(text))
    counts = Counter()
    for heading in HEADING.findall(text):
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        number = counts[slug]
        counts[slug] += 1
        result.add(f"{slug}-{number}" if number else slug)
    return result


def check(root=ROOT):
    errors = []
    frame_count = 0
    link_count = 0
    documents = sorted(p for p in root.rglob("*")
                       if p.suffix in (".md", ".html") and ".git" not in p.parts)
    texts = {p.resolve(): p.read_text(encoding="utf-8-sig") for p in documents}
    for path, content in texts.items():
        label = path.relative_to(root)
        for line_number, line in enumerate(content.splitlines(), 1):
            for match in FRAME.finditer(line):
                frame = bytes.fromhex(match.group())
                frame_count += 1
                problems = []
                if frame[-1] != 0:
                    problems.append("terminator is not 00")
                if len(frame) != frame[4] + 7:
                    problems.append(f"length {len(frame)} != DL + 7 ({frame[4] + 7})")
                checksum = reduce(xor, frame[:-2], 0)
                if checksum != frame[-2]:
                    problems.append(f"checksum {frame[-2]:02X} != {checksum:02X}")
                if problems:
                    errors.append(f"{label}:{line_number}: " + "; ".join(problems))
            if path.suffix != ".md":
                continue
            for match in LINK.finditer(line):
                target = match.group(1).strip().strip("<>")
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                destination = ((path.parent / unquote(parts.path)).resolve()
                               if parts.path else path)
                link_count += 1
                if not destination.exists():
                    errors.append(f"{label}:{line_number}: missing local target {target}")
                elif parts.fragment and destination.suffix == ".md":
                    target_text = texts.get(destination)
                    if target_text is None:
                        target_text = destination.read_text(encoding="utf-8-sig")
                    if unquote(parts.fragment) not in anchors(target_text):
                        errors.append(f"{label}:{line_number}: missing fragment {target}")
    return errors, len(documents), frame_count, link_count


def main():
    errors, documents, frames, links = check()
    for error in errors:
        print(error)
    print(f"Checked {documents} documents, {frames} complete frame occurrences, "
          f"{links} local links: {len(errors)} errors.")
    print("Symbolic/partial frames and external URL availability are not checked. "
          "Byte checks do not prove hardware behavior.")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
