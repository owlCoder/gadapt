"""Checks for source-extracted numeric snapshot, not a raw-archive replay."""
import json
from pathlib import Path
import pytest
from build_observed_influence_ledger import assemble


def test_original_r_contrasts_from_rounded_21_pair_ledger():
    a=assemble()['R']
    assert len(a['pairs'])==21
    assert sum(x['weight'] for x in a['pairs'])==pytest.approx(1)
    assert a['max_abs_deviation_from_original'] < 1e-8
    assert a['original_exact_point']['c4']==pytest.approx(.07079177983539131)


def test_r_family_loo_concentration_not_new_inference():
    a=assemble()['R']
    f=next(x for x in a['family_leave_one_out'] if x['removed']=='rastrigin')
    assert f['c4']==pytest.approx(.04086608820833334,abs=1e-8)
    assert f['c4']<.05<a['original_exact_point']['c4']
    assert len(a['family_leave_one_out'])==9


def test_r_dim_loo_descriptive_only():
    a=assemble()['R']
    assert len(a['dimension_leave_one_out'])==3
    assert next(x for x in a['dimension_leave_one_out'] if x['drop_d']==7)['c4']==pytest.approx(.051943029,abs=1e-8)


def test_i2_aggregates_exact_point_reconstruction():
    b=assemble()['I2']
    assert len(b['cells'])==8
    assert b['aggregate_from_original_run_records']['ipop']['P']==pytest.approx(.7708333333333333)
    assert b['contrasts_from_original_run_records']['CVaR(IPOP)-CVaR(H)']==pytest.approx(-.12530676111239542,abs=1e-13)


def test_i2_dominant_cell_and_7_cell_loo():
    b=assemble()['I2']
    dominant=b['dominant_cell']
    assert dominant['index']==3
    assert dominant['contrast']==-1
    assert dominant['share_of_net_negative_point_estimate']==pytest.approx(.9975519189,abs=1e-8)
    assert dominant['mean_without_this_cell']==pytest.approx(-.00035058412845,abs=1e-11)


def test_i2_no_witness_seed_forensics():
    b=assemble()['I2']
    s=b['observed_infeasible_seed_forensics']
    assert s['gadapt_hyb']==[68003015,68003018,68003028]
    assert s['gadapt']==[68003023]
    assert s['ipop']==[]
    c=next(x for x in b['cells'] if x['cell_index']==3)
    assert [c['configs'][v]['feasible_count'] for v in ('gadapt','gadapt_hyb','ipop')]==[29,27,30]


def test_cvar_saturation_retains_feasibility_information():
    a=assemble()['I2']['cells']
    c=a[4]['configs']
    assert {v:c[v]['cvar90'] for v in c}=={'gadapt':1,'gadapt_hyb':1,'ipop':1}
    assert [c[v]['feasible_count'] for v in ('gadapt','gadapt_hyb','ipop')]==[0,1,5]


def test_all_original_inference_labels_preserved():
    b=assemble()['I2']
    assert b['original_preregistered_decisions']=={'H64h1':'undecided','H64h2':'opposite'}
    assert b['analysis_level'].startswith('ORIGINAL_RUN_RECORD')
    assert len(b['source_git_blobs']['I'])==len(b['source_git_blobs']['I2'])==8


def test_ledger_disk_is_reproducible():
    expected=assemble()
    actual=json.loads((Path(__file__).parent/'I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json').read_text())
    assert actual==expected
