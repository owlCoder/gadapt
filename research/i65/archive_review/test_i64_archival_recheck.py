"""Synthetic and source-snapshot arithmetic tests; no optimizer and no PF."""
import copy
import gzip
import json
from pathlib import Path

import pytest
from build_source_extracted_ledger import SRC, make_ledger
from i64_archival_recheck import (
    ARCHIVES, arithmetic_checks, git_blob_sha, open_pinned,
)


def test_source_extracted_snapshot_passes_all_arithmetic_checks():
    got = arithmetic_checks(SRC)
    assert got['total'] == 41
    assert got['passed'] == 41
    assert got['all_pass']


def test_tool_ledger_does_not_claim_raw_bootstrap_reproduction():
    ledger = make_ledger()
    assert ledger['all_pass']
    assert 'Original bootstrap resampling NOT_RECOMPUTED' in ledger['not_done']
    assert 'Raw optimizer stochastic runs NOT_RECOMPUTED' in ledger['not_done']
    assert len(ledger['verified_blob_ids']) == 7


def test_detects_wrong_r_orthogonal_contrast():
    altered = copy.deepcopy(SRC)
    altered['R']['estimates'][3] += 0.01
    a = arithmetic_checks(altered)
    assert not a['all_pass']
    assert any(not c['pass'] and 'R c4' in c['name'] for c in a['checks'])


def test_detects_wrong_i2_hybrid_cvar():
    altered = copy.deepcopy(SRC)
    altered['I2']['aggregate']['gadapt_hyb']['cvar90'] -= 0.1
    a = arithmetic_checks(altered)
    assert not a['all_pass']
    assert any(not c['pass'] and 'I2 CVaR(IPOP)-CVaR(H)' in c['name'] for c in a['checks'])


def test_detects_wrong_nonrot_e3_tail():
    altered = copy.deepcopy(SRC)
    altered['E3']['contrasts']['1.5*CVaR_nonrot(M)-CVaR_nonrot(H)']['estimate'] = 0.7
    a = arithmetic_checks(altered)
    assert not a['all_pass']
    assert any(not c['pass'] and 'E3 non-rotated 1.5' in c['name'] for c in a['checks'])


def test_detects_misrepresented_e3_hypothesis_label():
    altered = copy.deepcopy(SRC)
    altered['E3']['H64g2'] = 'supported'
    a = arithmetic_checks(altered)
    assert not a['all_pass']
    assert any(not c['pass'] and c['name'].startswith('E3 H64g2') for c in a['checks'])


def test_verify_compressed_git_blob_identity(tmp_path, monkeypatch):
    doc = {'v': 0.25}
    raw = gzip.compress(json.dumps(doc).encode(), mtime=0)
    target = tmp_path / 'research' / 'results' / 'fake' / 'analysis.json.gz'
    target.parent.mkdir(parents=True)
    target.write_bytes(raw)
    monkeypatch.setitem(ARCHIVES, 'TEST', ('fake/analysis.json.gz', git_blob_sha(raw)))
    assert open_pinned(tmp_path, 'TEST') == doc
    target.write_bytes(raw + b'bad')
    with pytest.raises(ValueError, match='blob mismatch'):
        open_pinned(tmp_path, 'TEST')


def test_incorrect_e_contrast_is_rejected():
    altered = copy.deepcopy(SRC)
    altered['E']['contrasts']['dA|ipop']['estimate'] += 0.001
    check = arithmetic_checks(altered)
    assert check['passed'] < check['total']


def test_opposite_i2_is_not_a_claim_of_significant_feasibility_loss():
    check = arithmetic_checks(SRC)
    c = next(x for x in check['checks'] if x['name'].startswith('I2 feasibility contrast'))
    assert c['pass']
    assert SRC['I2']['contrasts']['P(H)-P(IPOP)']['upper'] > 0
    assert SRC['I2']['contrasts']['CVaR(IPOP)-CVaR(H)']['upper'] < 0
