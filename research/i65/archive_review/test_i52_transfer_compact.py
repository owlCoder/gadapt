"""Small synthetic negative controls for the source-locked I52 audit."""
import importlib.util
from pathlib import Path
from fractions import Fraction
import pytest

p=Path(__file__).with_name('i52_transfer_compact.py')
spec=importlib.util.spec_from_file_location('i52_transfer_compact',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_full_fraction():
    r=m.chance_agreement(7,1,1,12)
    assert r['observed']['exact']=='19/21'
    assert r['kappa']['exact']=='83/104'

def test_complete_case_fraction():
    r=m.chance_agreement(7,0,1,10)
    assert r['observed']['exact']=='17/18'
    assert r['kappa']['exact']=='70/79'

def test_positive_negative_agreement():
    r=m.chance_agreement(7,1,1,12)
    assert r['positive_agreement']['exact']=='7/8'
    assert r['negative_agreement']['exact']=='12/13'

def test_expected_chance():
    assert m.chance_agreement(7,1,1,12)['chance_expected']['exact']=='233/441'

def test_empty_rejected():
    with pytest.raises(ValueError,match='empty'):
        m.chance_agreement(0,0,0,0)

def test_all_negative_no_positive_agreement():
    r=m.chance_agreement(0,0,0,2)
    assert r['positive_agreement'] is None
    assert r['kappa'] is None

def test_original_blob_fail_closed(tmp_path):
    dest=tmp_path/'research'/'results'/'iteration52'
    dest.mkdir(parents=True)
    for k in m.BLOBS:(dest/k).write_text('{}')
    with pytest.raises(ValueError,match='Git blob mismatch'):
        m.source(tmp_path)

def test_bad_roster_rejected():
    with pytest.raises((KeyError,ValueError)):
        m.compute({'per_library':{}}, {})
