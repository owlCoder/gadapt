import copy
import math
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from i64_r_off_git_raw_recovery_gate import validate_r_records,verify_lineage,blob_sha1,PAIRS,BUILDS

@pytest.fixture(scope='module')
def minimal_records():
    records=[]
    for k in range(21):
        for cfg in ('gadapt','ipop'):
            for s in range(1,101):
                records.append({'task':{'k':k,'config':cfg,'seed':67_000_000+1000*(63+k)+s},'calls':12000,'ok':True,'events':[[1,30.],[25,20.],[12000,1.]]})
    return records

def test_frozen_pair_roster():
    assert len(PAIRS)==21
    assert PAIRS[0]==('sphere',2)
    assert PAIRS[-1]==('booth',2)

def test_original_shape_passes(minimal_records):
    r=validate_r_records(minimal_records)
    assert r['records_checked']==4200
    assert r['event_integrity']=='PASS'

def test_record_must_not_be_omitted(minimal_records):
    with pytest.raises(ValueError,match='record count'):validate_r_records(minimal_records[:-1])

def test_duplicate_seed_fails(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[1]['task']['seed']=a[0]['task']['seed']
    with pytest.raises(ValueError,match='Duplicate'):validate_r_records(a)

def test_wrong_seed_fails(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[0]['task']['seed']=1
    with pytest.raises(ValueError,match='seed'):validate_r_records(a)

def test_bad_event_order_fails(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[0]['events']=[[5,10.],[5,9.]]
    with pytest.raises(ValueError,match='event call'):validate_r_records(a)

def test_bad_event_value_fails(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[0]['events']=[[1,math.nan]]
    with pytest.raises(ValueError,match='Non-finite'):validate_r_records(a)

def test_rejected_failed_status(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[0]['ok']=False
    with pytest.raises(ValueError,match='Unsuccessful'):validate_r_records(a)

def test_best_so_far_monotone(minimal_records):
    a=copy.deepcopy(minimal_records)
    a[0]['events']=[[1,1.],[2,100.]]
    with pytest.raises(ValueError,match='Best value increases'):validate_r_records(a)

def test_manifest_exact():
    manifest={x:x+'_value' for x in BUILDS}
    d={'e_inputs':{'part':'sha'},'manifest':manifest}
    c={'e_inputs':{'part':'sha'},'manifest':manifest,'results':[{'identical':True} for _ in range(5)]}
    out=verify_lineage(d,{'e_inputs':d['e_inputs']},c)
    assert out['check_repro_witnesses']==5
    c['manifest']=dict(manifest,r_settings='other')
    with pytest.raises(ValueError,match='build mismatch'):verify_lineage(d,{'e_inputs':d['e_inputs']},c)

def test_git_blob_independence():
    assert blob_sha1(b'hello')=='b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0'
