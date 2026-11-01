#!/usr/bin/env python3
"""Safely restore historical research/<name> aliases in a local Git checkout.

A dry run (the default) does not mutate files. --apply makes only missing
symlinks after a complete preflight; --verify checks all original Git blobs.
Never run expensive scientific experiments from the curated studies/ views.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research" / "MIGRATION_MANIFEST_2026-11-01.json"


def preflight(items: list[dict], verify: bool) -> tuple[list[tuple[Path, Path]], int, list[str]]:
    """Examine *all* paths before creating the first symlink (fail closed)."""
    planned: list[tuple[Path, Path]] = []
    existing = 0
    problems: list[str] = []
    seen: set[Path] = set()
    for entry in items:
        old = ROOT / entry["old"]
        new = ROOT / entry["canonical"]
        if old in seen or old.parent != ROOT / "research":
            problems.append(f"invalid or repeated legacy path: {old}")
            continue
        seen.add(old)
        if not new.is_file():
            problems.append(f"canonical missing: {new}")
            continue
        if verify:
            result = subprocess.run(
                ["git", "-C", str(ROOT), "hash-object", str(new)],
                capture_output=True, text=True, check=False,
            )
            if result.returncode or result.stdout.strip() != entry["sha"]:
                problems.append(f"content SHA mismatch: {new}")
        if old.is_symlink():
            if old.resolve() == new.resolve():
                existing += 1
            else:
                problems.append(f"unexpected existing symlink: {old}")
        elif old.exists():
            problems.append(f"old name already occupied: {old}")
        else:
            planned.append((old, new))
    return planned, existing, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create missing aliases after successful preflight")
    parser.add_argument("--verify", action="store_true", help="verify canonical files against original Git blob SHAs")
    args = parser.parse_args()
    if not (ROOT / ".git").exists():
        print("STOP: not a local Git checkout", file=sys.stderr)
        return 2
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf8"))
        if not isinstance(data["moved_files"], list):
            raise ValueError("moved_files is not an array")
    except (OSError, ValueError, KeyError) as exc:
        print(f"STOP: manifest cannot be read: {exc}", file=sys.stderr)
        return 2
    planned, existing, problems = preflight(data["moved_files"], args.verify)
    if problems:
        for problem in problems[:40]:
            print("ERROR:", problem, file=sys.stderr)
        print(f"STOP: {len(problems)} preflight error(s); no aliases created", file=sys.stderr)
        return 1
    created = 0
    if args.apply:
        for old, new in planned:
            try:
                old.symlink_to(os.path.relpath(new, old.parent))
                created += 1
            except OSError as exc:
                print(f"STOP: cannot create {old}: {exc}", file=sys.stderr)
                return 2
    print(f"checked={len(data['moved_files'])}; planned={len(planned)}; "
          f"created={created}; existing={existing}; mode={'apply' if args.apply else 'dry-run'}; "
          f"hash_verification={'enabled' if args.verify else 'disabled'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
