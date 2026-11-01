"""Research namespace: historical root imports require explicit path restoration.

Do not append research/legacy/flat to __path__. Many frozen modules compute
REPO, OUT, and source provenance from __file__; silently importing a relocated
file would change them. Run:
    python research/compat/restore_legacy_paths.py --apply --verify
in a local Git checkout *before* importing research.iterationXX modules.
"""
