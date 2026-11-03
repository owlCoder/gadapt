"""Synthetic tests for exact counter vs bool counter distinction."""
import copy
import pytest
from i55_i50_numeric_vs_boolean_audit import compare_pair


def fixture():
    old = {"cells": []}
    new = {"cells": []}
    keys = ["C1","C2","C3","C4","C5","R1","R2","R3","D2"]
    for seed in range(30):
        cell = {"function": "plateau", "d": 2, "seed": seed,
                "error": None, "flags": {k: 0 for k in keys}}
        old["cells"].append(copy.deepcopy(cell))
        new["cells"].append(copy.deepcopy(cell))
    return old, new


def test_exact_match_no_changes():
    a,b=fixture()
    got=compare_pair(a,b)
    assert got["compared"] == 30
    assert got["numeric_change_cells"] == 0
    assert got["presence_change_cells"] == 0


def test_c1_count_change_but_not_presence_change():
    a,b=fixture()
    a["cells"][1]["flags"]["C1"] = 2
    b["cells"][1]["flags"]["C1"] = 3
    got=compare_pair(a,b)
    assert got["numeric_change_cells"] == 1
    assert got["presence_change_cells"] == 0
    assert got["differences"][0]["numeric_differences"] == {"C1": [2, 3]}


def test_c2_zero_to_one_changes_presence():
    a,b=fixture()
    b["cells"][1]["flags"]["C2"] = 1
    got=compare_pair(a,b)
    assert got["numeric_change_cells"] == 1
    assert got["presence_change_cells"] == 1
    assert got["differences"][0]["presence_differences"] == {"C2": [0, 1]}


def test_original_emukit_combination():
    a,b=fixture()
    a["cells"][1]["flags"]["C1"] = 2
    b["cells"][1]["flags"]["C1"] = 3
    b["cells"][1]["flags"]["C2"] = 1
    got=compare_pair(a,b)
    assert len(got["differences"]) == 1
    assert got["differences"][0]["numeric_differences"] == {"C1":[2,3],"C2":[0,1]}
    assert got["differences"][0]["presence_differences"] == {"C2":[0,1]}


def test_missing_cell_is_an_error():
    a,b=fixture();b["cells"].pop()
    with pytest.raises(ValueError,match="roster"):
        compare_pair(a,b)


def test_original_timeout_not_counted_as_disagreement():
    a,b=fixture()
    a["cells"][0]["error"]="timeout"
    got=compare_pair(a,b)
    assert got["compared"] == 29
    assert len(got["skipped"]) == 1
