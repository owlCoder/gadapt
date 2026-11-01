#!/usr/bin/env python3
"""Opt-in restoration of old research/<basename> paths for legacy experiments.

Default: dry-run. --apply: create missing *symlinks*, never overwrite.
--verify: check byte identity against old Git blob hashes with git hash-object.
This does NOT validate scientific results or dependency compatibility.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research" / "MIGRATION_MANIFEST_2026-11-01.json"

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--apply", action="store_true", help="create only missing old-path symlinks")
    cli.add_argument("--verify", action="store_true", help="check canonical file git SHA identities")
    args = cli.parse_args()
    if not (ROOT / ".git").is_dir():
        raise SystemExit("STOP: run from an actual local Git checkout")
    data = json.loads(MANIFEST.read_text(encoding="utf8"))
    count, existed, errors = 0, 0, []
    for item in data["moved_files"]:
        original = ROOT / item["old"]
        canonical = ROOT / item["canonical"]
        if not canonical.is_file():
            errors.append("canonical missing: " + str(canonical))
            continue
        if args.verify:
            run = subprocess.run(["git", "-C", str(ROOT), "hash-object",
                                  str(canonical)], text=True, capture_output=True)
            if run.returncode or run.stdout.strip() != item["sha"]:
                errors.append("content SHA mismatch: " + str(canonical))
        if original.is_symlink():
            if original.resolve() == canonical.resolve():
                existed += 1
            else:
                errors.append("unexpected existing symlink: " + str(original))
        elif original.exists():
            errors.append("old name already occupied: " + str(original))
        elif args.apply:
            original.symlink_to(os.path.relpath(canonical, original.parent))
            count += 1
    print("checked=%s; created=%s; existed=%s; errors=%s; mode=%s" %
          (len(data["moved_files"]), count, existed, len(errors),
           "apply" if args.apply else "dry-run"))
    for e in errors[:40]:
        print("ERROR:", e, file=sys.stderr)
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
