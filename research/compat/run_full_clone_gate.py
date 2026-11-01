#!/usr/bin/env python3
"""Opt-in, bounded, evidence-producing GAdapt migration regression gate.

NEVER starts experiments, installs dependencies or dispatches GitHub Actions.
Defaults to read-only preflight. --run explicitly opts into creating missing
legacy-root symlinks (after preflight) and running inexpensive historical tests.
The full-gate PASS is emitted only for an actual full, clean Git checkout under
Python 3.12 with all required tests successful and traceable logs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

STEPS = (
    ("compat_synthetic", "unit", ["-m", "unittest", "discover", "-s", "research/compat",
                                   "-p", "test_*.py", "-v"]),
    ("git_tree", "python", ["research/compat/check_migration_git_tree.py"]),
    ("restore_preflight", "python", ["research/compat/restore_legacy_paths.py", "--verify"]),
    ("restore_apply", "python", ["research/compat/restore_legacy_paths.py", "--apply", "--verify"]),
    ("restore_idempotence", "python", ["research/compat/restore_legacy_paths.py", "--apply", "--verify"]),
    ("import_smoke", "python", ["-c", "from gadapt.ga import GA; print('GA_IMPORT_OK')"]),
    ("environment_freeze", "python", ["-m", "pip", "freeze"]),
    ("i41", "pytest", ["-m", "pytest", "-q",
                        "research/test_iteration41_certified_temporal_rows.py",
                        "research/test_iteration41_property_falsification.py"]),
    ("i63", "pytest", ["-m", "pytest", "-q", "research/test_iteration63_replication.py"]),
    ("i64", "pytest", ["-m", "pytest", "-q",
                        "research/i64/test_e_common.py", "research/i64/test_e_algos.py",
                        "-k", "not pygad"]),
    ("i65", "pytest", ["-m", "pytest", "-q", "-rx", "research/i65"]),
)


def run_cmd(argv: list[str], *, cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=timeout, check=False,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


def sha256(s: bytes) -> str:
    return hashlib.sha256(s).hexdigest()


def allowed_python(candidate: Path, root: Path) -> tuple[bool, str]:
    if not candidate.is_file():
        return False, "Python executable not found: " + str(candidate)
    try:
        p = run_cmd([str(candidate), "-c", "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                    cwd=root, timeout=12)
        version = p.stdout.strip()
        return p.returncode == 0 and version == "3.12", version
    except (OSError, subprocess.TimeoutExpired) as ex:
        return False, str(ex)


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return run_cmd(["git", "-C", str(root), *args], cwd=root, timeout=20)


def prerequisites(root: Path, candidate: Path, expected_head: str | None) -> dict:
    errors = []
    p = git(root, "rev-parse", "--show-toplevel")
    if p.returncode or Path(p.stdout.strip()).resolve() != root.resolve():
        errors.append("NOT_A_FULL_LOCAL_GIT_CHECKOUT")
    h = git(root, "rev-parse", "HEAD")
    head = h.stdout.strip() if h.returncode == 0 else None
    if not head:
        errors.append("HEAD_UNAVAILABLE")
    if expected_head and head != expected_head:
        errors.append("HEAD_MISMATCH")
    branch = git(root, "symbolic-ref", "--short", "HEAD")
    if branch.returncode or branch.stdout.strip() != "main":
        errors.append("NOT_ON_MAIN")
    if git(root, "cat-file", "-e", "0e7cacda2040643a41ff923dd2a71ffbc3f5dfef^{commit}").returncode:
        errors.append("ORIGINAL_GIT_HISTORY_MISSING")
    # No tracked modifications: prevents testing an unknowable mixture.
    if git(root, "diff", "--quiet").returncode or git(root, "diff", "--cached", "--quiet").returncode:
        errors.append("TRACKED_WORKTREE_DIRTY")
    needed = [root / "research/MIGRATION_MANIFEST_2026-11-01.json",
              root / "research/compat/check_migration_git_tree.py",
              root / "research/compat/restore_legacy_paths.py",
              root / "research/i65/test_audited_budget.py"]
    if any(not f.is_file() for f in needed):
        errors.append("REQUIRED_REPOSITORY_SOURCES_MISSING")
    py_ok, version = allowed_python(candidate, root)
    if not py_ok:
        errors.append("REQUIRES_PYTHON_3_12")
    return {"status": "READY" if not errors else "BLOCKED", "errors": errors,
            "head": head, "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "python": str(candidate), "python_version": version, "root": str(root.resolve())}


def perform(root: Path, python: Path, directory: Path, timeout: int, expected: str | None) -> int:
    gate = {"gate": "GADAPT_FULL_CLONE_REGRESSION", "status": "BLOCKED",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "preflight": prerequisites(root, python, expected), "steps": []}
    if gate["preflight"]["errors"]:
        print(json.dumps(gate, indent=2))
        return 2
    if directory == root or root in directory.parents:
        print("BLOCKED: report directory must be outside repository", file=sys.stderr)
        return 2
    if directory.exists() and any(directory.iterdir()):
        print("BLOCKED: report directory already contains files", file=sys.stderr)
        return 2
    directory.mkdir(parents=True, exist_ok=True)
    exit_code = 0
    for name, _, argv in STEPS:
        cmd = [str(python), *argv]
        try:
            p = run_cmd(cmd, cwd=root, timeout=timeout)
            rc, output = p.returncode, p.stdout
        except subprocess.TimeoutExpired as ex:
            rc = 124
            output = (ex.stdout or b"")
            if isinstance(output, bytes):
                output = output.decode(errors="replace")
            output += f"\nTIMEOUT: {timeout} seconds\n"
        log = (directory / f"{len(gate['steps'])+1:02d}_{name}.log")
        log.write_text("$ " + " ".join(cmd) + "\n" + output, encoding="utf8")
        step = {"name": name, "command": cmd, "exit_code": rc,
                "status": "PASS" if rc == 0 else "FAIL",
                "log": log.name, "log_sha256": sha256(log.read_bytes())}
        # Validate restore really checked all manifest entries and was idempotent.
        if rc == 0 and name in {"restore_preflight", "restore_apply", "restore_idempotence"}:
            if "checked=341;" not in output or "hash_verification=enabled" not in output:
                step["status"] = "FAIL"
                step["failure"] = "RESTORE_COUNT_OR_HASH_VERIFICATION_MISSING"
            elif name == "restore_idempotence" and ("created=0;" not in output or "existing=341;" not in output):
                step["status"] = "FAIL"
                step["failure"] = "RESTORE_NOT_IDEMPOTENT"
        if rc == 0 and name == "git_tree" and '"count": 341' not in output:
            step["status"] = "FAIL"
            step["failure"] = "TREE_COUNT_MISSING"
        if rc == 0 and name in {"i41", "i63", "i64", "i65"} and " skipped" in output:
            # Some I64 PyGAD tests intentionally skip without MBENCH. Record
            # incomplete coverage rather than calling the full gate PASS.
            step["status"] = "PARTIAL"
            step["warning"] = "PYTEST_SKIPPED_TESTS"
        gate["steps"].append(step)
        if step["status"] != "PASS":
            exit_code = 1
            break
        if git(root, "rev-parse", "HEAD").stdout.strip() != gate["preflight"]["head"]:
            step["status"] = "FAIL"
            step["failure"] = "HEAD_CHANGED_DURING_TEST"
            exit_code = 1
            break
    if exit_code == 0 and git(root, "diff", "--quiet").returncode:
        exit_code = 1
        gate["integrity_error"] = "TRACKED_FILES_MODIFIED_BY_TESTS"
    gate["status"] = "PASS" if exit_code == 0 and len(gate["steps"]) == len(STEPS) else "FAIL"
    gate["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    report = directory / "gate.json"
    report.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": gate["status"], "head": gate["preflight"]["head"],
                      "steps": len(gate["steps"]), "report": str(report)}, indent=2))
    return 0 if gate["status"] == "PASS" else 1


def preserve_venv_python(path: Path) -> Path:
    """Make an absolute path without dereferencing a virtualenv's python symlink.

    On Linux, .venv/bin/python often points at the system interpreter. Calling
    Path.resolve() here discards the venv path and therefore its site-packages.
    """
    return Path(os.path.abspath(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--python", type=Path, default=None,
                        help="Path to pinned Python 3.12 interpreter (e.g., .venv/bin/python)")
    parser.add_argument("--expected-head", default=None,
                        help="Optional exact expected full Git SHA; fail if checkout differs")
    parser.add_argument("--run", action="store_true", help="opt into 341 symlink restore and bounded tests")
    parser.add_argument("--report-dir", type=Path, default=None,
                        help="required with --run; must be outside the repository")
    parser.add_argument("--timeout", type=int, default=120,
                        help="seconds per command, 1..120; no expensive experiments")
    args = parser.parse_args()
    root = args.root.resolve()
    python = preserve_venv_python(args.python if args.python is not None else root / ".venv/bin/python")
    if not (1 <= args.timeout <= 120):
        parser.error("--timeout must be 1..120")
    if not args.run:
        result = prerequisites(root, python, args.expected_head)
        print(json.dumps({"mode": "read_only", "preflight": result,
                          "next": "--run --report-dir /tmp/gadapt_regression_<id>"}, indent=2))
        return 0 if result["status"] == "READY" else 2
    if args.report_dir is None:
        parser.error("--report-dir required for --run")
    return perform(root, python, args.report_dir.resolve(), args.timeout, args.expected_head)


if __name__ == "__main__":
    sys.exit(main())
