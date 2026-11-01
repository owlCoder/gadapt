#!/usr/bin/env python3
"""Read-only I65 migration provenance gate against *committed* Git objects.

No optimizer imports, no branch modifications, no symlink restoration. Checks
source-commit blobs, HEAD canonical blobs and Git symlink content SHA-1.
This does NOT test execution compatibility of historical Python modules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import subprocess
import sys


def git(root: Path, *args: str) -> bytes:
    cp = subprocess.run(["git", "-C", str(root), *args],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise RuntimeError(f"git {args[0]} failed: {cp.stderr.decode(errors='replace').strip()}")
    return cp.stdout


def tracked_blobs(root: Path, ref: str) -> dict[str, tuple[str, str, int]]:
    """Full tree, using -z to preserve literal filename bytes safely."""
    raw = git(root, "ls-tree", "--full-tree", "-r", "-z", "-l", ref)
    out: dict[str, tuple[str, str, int]] = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, path_bytes = item.split(b"\t", 1)
        mode, typ, sha, size = meta.decode("ascii").split()
        if typ != "blob":
            continue
        path = path_bytes.decode("utf-8")
        if path in out:
            raise ValueError(f"duplicate tree path: {path}")
        out[path] = (mode, sha, int(size))
    return out


def blob_hash(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") +
                        b"\0" + payload).hexdigest()


def safe_path(p: str) -> bool:
    parts = PurePosixPath(p).parts
    return bool(parts) and parts[0] == "research" and all(
        x not in ("", ".", "..") for x in p.split("/")) and not p.startswith("/")


def audit(root: Path, manifest_file: Path, head: str = "HEAD") -> dict:
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    items = manifest["moved_files"]
    if not isinstance(items, list) or not items:
        raise ValueError("manifest must have a nonempty moved_files list")
    source_commit = manifest["source_commit"]
    original = tracked_blobs(root, source_commit)
    current = tracked_blobs(root, head)
    problems: list[str] = []
    old_paths: set[str] = set()
    new_paths: set[str] = set()
    view_paths: set[str] = set()
    for i, entry in enumerate(items):
        try:
            old, new, view = (entry[k] for k in ("old", "canonical", "view"))
            sha, mode, size, name = (entry[k] for k in ("sha", "mode", "bytes", "name"))
            if not all(isinstance(p, str) and safe_path(p) for p in (old, new, view)):
                raise ValueError("non-research or escaping path")
            if old != f"research/{name}" or new != f"research/legacy/flat/{name}":
                raise ValueError("unexpected source or canonical layout")
            if old in old_paths or new in new_paths or view in view_paths:
                raise ValueError("repeated manifest path")
            old_paths.add(old); new_paths.add(new); view_paths.add(view)
            if old in current:
                raise ValueError("old root path still tracked")
            expected = (mode, sha, size)
            if original.get(old) != expected:
                raise ValueError("source commit blob/mode/size mismatch")
            if current.get(new) != expected:
                raise ValueError("current canonical blob/mode/size mismatch")
            target = posixpath.relpath(new, posixpath.dirname(view))
            expected_link = ("120000", blob_hash(target.encode("utf-8")),
                             len(target.encode("utf-8")))
            if current.get(view) != expected_link:
                raise ValueError("view symlink target/mode/size mismatch")
        except (KeyError, TypeError, ValueError) as exc:
            problems.append(f"entry {i}: {exc}")
    if problems:
        raise ValueError(f"{len(problems)} provenance failure(s): " + "; ".join(problems[:12]))
    return {"status": "PASS", "count": len(items),
            "original_commit": source_commit,
            "current_commit": git(root, "rev-parse", head).decode().strip(),
            "checks": ["original_Git_blob_mode_size", "canonical_Git_blob_mode_size",
                       "view_symlink_content", "source_path_removed", "no_duplicates"]}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--manifest", type=Path, default=None)
    p.add_argument("--ref", default="HEAD")
    args = p.parse_args()
    path = args.manifest or args.root / "research/MIGRATION_MANIFEST_2026-11-01.json"
    try:
        result = audit(args.root, path, args.ref)
    except (OSError, ValueError, KeyError, RuntimeError) as ex:
        print(json.dumps({"status": "FAIL", "reason": str(ex)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
