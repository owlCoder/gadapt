"""Synthetic and archived-derived regression guards for post-hoc influence analysis."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from i64_i2_posthoc_dropout_bootstrap import (
    source_arrays, point_contrasts, bootstrap,
    DOMINANT_ORPD_CELL, EXPECTED_FROZEN_POINTS
)
from i64_i2_cell_influence import CONFIGS


def arrays():
    d={}
    for ci in range(8):
        for c in CONFIGS:
            z=np.zeros((30,2))
            z[:,1]=1
            d[(ci,c)]=z
    return d


def test_reject_empty_cell_ids():
    with pytest.raises(ValueError,match='nonempty'):
        point_contrasts(arrays(),(),{})


def test_reject_repeated_cell_ids():
    with pytest.raises(ValueError,match='unique'):
        point_contrasts(arrays(),(0,0),{0:np.arange(30)})


def test_reject_invalid_cell():
    with pytest.raises(ValueError,match='Unknown source cell'):
        point_contrasts(arrays(),(8,),{8:np.arange(30)})


def test_reject_partial_seed_index():
    with pytest.raises(ValueError,match='Bad paired sample shape'):
        point_contrasts(arrays(),(0,),{0:np.arange(29)})


def test_reject_nonfinite_values():
    a=arrays();a[(0,'gadapt')][0,0]=np.nan
    with pytest.raises(ValueError,match='Bad archived cell array'):
        point_contrasts(a,(0,),{0:np.arange(30)})


def test_paired_dropout_straightforward():
    a=arrays();a[(3,'gadapt_hyb')][[14,17,27],:]=[1.,0.]
    allids=tuple(range(8));no3=tuple(x for x in allids if x!=3)
    x=point_contrasts(a,allids,{ci:np.arange(30) for ci in allids})
    y=point_contrasts(a,no3,{ci:np.arange(30) for ci in no3})
    assert x[2]==pytest.approx(-1/8)
    assert y[2]==pytest.approx(0)


def test_seeded_exploratory_bootstrap_repeatable():
    a=arrays();a[(2,'gadapt_hyb')][14,:]=[1.,0.]
    one=bootstrap(a,(1,2),seed=68,reps=70)
    two=bootstrap(a,(1,2),seed=68,reps=70)
    assert one==two
    assert one['kind'].startswith('EXPLORATORY')


def test_zero_contrast_on_synthetic_equal_algorithms():
    a=arrays()
    result=bootstrap(a,(0,1,2),seed=68,reps=15)
    assert all(x['estimate']==0 for x in result['contrasts'].values())


def test_derived_archive_full_point_replay():
    path=Path(__file__).parent/'i64_i2_archived_losses_derived_2026-11-03.npz'
    if not path.exists(): pytest.skip('Portable derived-loss fixture intentionally not committed')
    a,src=source_arrays(None,path)
    x=point_contrasts(a,tuple(range(8)),{ci:np.arange(30) for ci in range(8)})
    np.testing.assert_allclose(x,EXPECTED_FROZEN_POINTS,rtol=0,atol=1e-12)


def test_reject_simultaneous_sources():
    path=Path(__file__).parent/'no-such-file.npz'
    with pytest.raises(ValueError,match='exactly one'):
        source_arrays(path,path)
