"""Synthetic bootstrap tests only; not evidence of full archive reproduction."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from i64_i2_bootstrap_replay import cvar90,contrasts_at,reproduce
from i64_i2_cell_influence import N_CELLS,N_SEEDS,CONFIGS,CONTRASTS


def arrays():
    a={}
    for ci in range(N_CELLS):
        for config in CONFIGS:
            v=np.zeros((N_SEEDS,2),dtype=float)
            v[:,1]=1
            a[(ci,config)]=v
    return a


def test_cvar_top_three():
    v=np.array([0]*27+[1]*3,dtype=float)
    assert cvar90(v)==1.
    assert cvar90(np.array([0]*28+[1]*2,dtype=float))==pytest.approx(2/3)


def test_point_full_pairing():
    a=arrays()
    a[(3,'gadapt_hyb')][[14,17,27],:]=[1,0]
    x=contrasts_at(a,{ci:np.arange(30) for ci in range(8)})
    assert x[2]==pytest.approx(-1/8)
    assert x[3]==pytest.approx(-3/(8*30))


def test_fixed_rng_produces_repeatable_bootstrap():
    a=arrays()
    a[(3,'gadapt_hyb')][[14,17,27],:]=[1,0]
    x=reproduce(a,{},replicates=60,seed=68)
    y=reproduce(a,{},replicates=60,seed=68)
    assert x==y
    assert x['all_original_values_match'] is False  # synthetic test NOT the archived CI
    assert x['tstar']>=0


def test_reconstructs_zero_contrast():
    a=arrays()
    x=contrasts_at(a,{ci:np.arange(30) for ci in range(8)})
    assert np.all(x==0)


def test_detect_nonfinite_samples():
    a=arrays()
    a[(0,'gadapt')][0,0]=float('nan')
    with pytest.raises(ValueError,match='Nonfinite'):
        reproduce(a,{},replicates=3)
