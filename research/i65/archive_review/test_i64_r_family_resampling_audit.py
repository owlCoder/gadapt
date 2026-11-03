import json
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).parent))
from i64_r_family_resampling_audit import FAMILIES, CONTRASTS, git_blob, get_rows, stress, run

LEDGER=Path(__file__).parent/'I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json'

def test_ledger_frozen_source_and_point():
    _,s=get_rows(ledger=LEDGER)
    assert s['provenance']['approximate']
    assert abs(s['point'][3]-0.07079177983539131)<1e-9
    assert s['family_matrix'].shape==(9,4)

def test_rastrigin_drop():
    v=run(ledger=LEDGER,replications=2000)
    assert abs(v['leave_one_family_out_c4']['rastrigin']-0.040866088)<1e-8
    assert v['leave_two_family_out_below_0_05']==8
    assert v['leave_two_family_out_total']==36

def test_order_and_weight():
    _,s=get_rows(ledger=LEDGER)
    assert len(FAMILIES)==9 and CONTRASTS[-1]=='c4'
    assert np.allclose(s['family_matrix'][:,3],s['family_matrix'][:,1]-s['family_matrix'][:,2])

def test_deterministic_bootstrap():
    mat=np.zeros((9,4),dtype=float);mat[:,3]=np.arange(9)*0.02
    a=stress(mat,replications=2000,seed=7001)
    b=stress(mat,replications=2000,seed=7001)
    assert a==b
    assert 0<a['proportion_resampled_c4_above_0_05']<1

def test_all_identical():
    mat=np.full((9,4),0.02)
    r=stress(mat,replications=1000)
    assert abs(r['percentile_envelopes']['c4']['p2.5']-0.02)<1e-12
    assert r['proportion_resampled_c4_above_0_05']==0

def test_no_unverified_inputs(tmp_path):
    p=tmp_path/'fake.json';p.write_text(json.dumps({'R':{'source_blob_sha1':'0'*40}}))
    with pytest.raises(ValueError,match='source'):get_rows(ledger=p)

def test_ledger_required(tmp_path):
    with pytest.raises(ValueError):get_rows()
    with pytest.raises(ValueError):get_rows(analysis=tmp_path/'a',ledger=LEDGER)

def test_unexpected_roster(tmp_path):
    v=json.loads(LEDGER.read_text());v['R']['pairs']=v['R']['pairs'][:-1]
    p=tmp_path/'ledger.json';p.write_text(json.dumps(v))
    with pytest.raises(ValueError,match='roster'):get_rows(ledger=p)

def test_bad_original_blob(tmp_path):
    p=tmp_path/'analysis.json.gz';p.write_bytes(b'not original')
    with pytest.raises(ValueError,match='blob'):get_rows(analysis=p)

def test_replication_bound():
    with pytest.raises(ValueError):stress(np.ones((9,4)),replications=0)
