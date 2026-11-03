"""Synthetic S0 21-cell ranking tests."""
import copy
import pytest
from i64_s0_cell_ranking import compare_s0


def fake():
    cells={}
    for j in range(21):
        k=f'f{j}|2'
        d,e=(1.,2.) if j<14 else ((3.,2.) if j<20 else (2.,2.))
        ad,ag=(0.4,0.5) if j<17 else (0.6,0.5)
        cells[f'{k}|de']={'gap_median':d,'A_mean':ad}
        cells[f'{k}|gadapt']={'gap_median':e,'A_mean':ag}
    return {'descriptive':cells}


def test_ranking_logic_supports_14_vs_6_and_17_vs_4():
    s=compare_s0(fake())['summary']
    assert s['expected_count_pattern']
    assert s['DE_better_final_median']==14
    assert s['GAdapt_better_A']==17


def test_ranking_logic_falsifies_incorrect_counts():
    x=fake()
    x['descriptive']['f0|2|de']['gap_median']=3.
    assert not compare_s0(x)['summary']['expected_count_pattern']


def test_missing_cell_rejected():
    x=fake()
    del x['descriptive']['f0|2|de']
    with pytest.raises(KeyError):compare_s0(x)


def test_wrong_cell_count_rejected():
    x=fake()
    del x['descriptive']['f20|2|de']
    del x['descriptive']['f20|2|gadapt']
    with pytest.raises(ValueError,match='21'):compare_s0(x)
