#!/usr/bin/env python3
"""Validate FRESH I55 original-source outputs by their linked input identities.

The old full-620 report contains a runtime date, so its SHA256, and the
SHA256 of descendant census/phase reports, legitimately change across days.
Do not require yesterday's output byte hash. Fail closed on immutable
original Git identifiers, current full-report SHA linkage, frozen C1/C2
population and all original per-stratum C1/C2 totals instead.
No optimizer, physics/AC/OPF, COCO or original objective evaluation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_COMMIT = '6b56fbc53ffc4d275ecef5e911ea4663474c9a08'
SOURCE_TREE = 'f88d221152fcb4157a8e1151a11b53cdfe8180b7'
MANIFEST_BLOB = '50ca2e96762447070a74309850cb1aa6586d3eb3'


def verify(full_bytes: bytes, census_bytes: bytes, phase_bytes: bytes) -> dict:
    full, census, phase = (json.loads(data) for data in
                           (full_bytes, census_bytes, phase_bytes))
    def require(ok: bool, why: str) -> None:
        if not ok:
            raise ValueError('FRESH_ORIGINAL_SOURCE_FAIL_CLOSED: ' + why)
    current_full_sha = hashlib.sha256(full_bytes).hexdigest()
    require(full.get('full_attestation_pass') is True and full.get('status') == 'PASS'
            and full.get('optimizer_or_power_flow_executed') is False,
            'Fresh 620-source attestation must PASS without optimizer/physics')
    tree = full.get('original_git_tree', {})
    require(tree.get('source_commit') == SOURCE_COMMIT and
            tree.get('original_root_tree_sha1') == SOURCE_TREE and
            tree.get('exact_tree_manifest_match') is True and
            tree.get('original_npz_tree_entries') == 620,
            'Original Git commit/root tree/620 NPZ roster mismatch')
    require(full.get('manifest_git_blob') == MANIFEST_BLOB and
            full.get('npz_byte_gate', {}).get('full_git_blob_pass') is True and
            full['npz_byte_gate'].get('raw_bytes_verified') == 620 and
            full.get('original_trace_replay', {}).get('npz', {}).get('full_raw_trace_pass') is True and
            full['original_trace_replay']['npz'].get('checked') == 620,
            'Original manifest, 620 binary Git blobs or frozen trace replay failed')
    require(census.get('original_620_full_attestation_sha256') == current_full_sha and
            phase.get('full_attestation_json_sha256') == current_full_sha and
            census.get('original_620_full_attestation_gate_pass') is True,
            'Fresh census/phase lineage not bound to THIS successful full report')
    require(census.get('original_source_commit') == SOURCE_COMMIT and
            phase.get('original_commit') == SOURCE_COMMIT and
            census.get('original_git_tree') == SOURCE_TREE and
            phase.get('source_root_git_tree') == SOURCE_TREE and
            census.get('original_manifest_git_blob') == MANIFEST_BLOB and
            phase.get('frozen_620_manifest_git_blob') == MANIFEST_BLOB,
            'Original census/phase source commit/tree/manifest identity differs')
    require(phase.get('all_620_original_npz_replayed_again') is True and
            phase.get('all_original_git_blobs_authenticated_again') is True and
            phase.get('all_frozen_objectives_and_flags_matched_again') is True and
            phase.get('source_npz_count') == 620,
            'Fresh phase audit has not fully replayed 620 authentic NPZ')

    def validate_part(c: dict, p: dict, label: str) -> dict:
        c1 = p['C1_search'] + p['C1_post']
        c2 = p['C2_search'] + p['C2_post']
        rep = p['C1_C2_search'] + p['C1_C2_post']
        c1_cells = c['flagged_cells']['C1']
        require(c['flag_occurrences']['C1'] == c1 and
                c['flag_occurrences']['C2'] == c2 and
                c['original_calls'] == p['calls'] and
                0 <= rep <= c1 and 0 <= c1_cells <= c1 and
                p['C1_post'] == p['C1_C2_post'] == 0,
                'Original C1/C2/phase/calls stratum differs: ' + label)
        first, both = c1 - rep, c1 - rep - c1_cells
        one = c1_cells - both
        require(0 <= both <= c1_cells and one >= 0,
                'Impossible signed-corner occupancy: ' + label)
        return dict(C1=c1, C2=c2, calls=p['calls'], repeats=rep,
                    C1_cells=c1_cells, first=first, both=both, one=one)

    overall = validate_part(census['overall'], phase['overall'], 'overall')
    require(overall == dict(C1=2105, C2=18779, calls=295445, repeats=1956,
                            C1_cells=109, first=149, both=40, one=69),
            'Frozen original 620-source population changed')
    require(census['overall']['valid_cells'] == 620 and
            phase['overall']['post_calls'] == 1200 and
            phase['overall']['C2_search'] == 17579 and
            phase['overall']['C2_post'] == 1200,
            'Original population/phase exposure differs')
    for key, expected_count in (('by_library', 21), ('by_function', 3),
                                ('by_dimension', 2)):
        left, right = census[key], phase[key]
        require(len(left) == expected_count and set(left) == set(right),
                'Original stratum coverage differs: ' + key)
        parts = [validate_part(left[name], right[name], key + '/' + name)
                 for name in sorted(left)]
        for field in overall:
            require(sum(row[field] for row in parts) == overall[field],
                    'Original ' + key + ' sum mismatch for ' + field)
    require(phase['by_dimension']['2']['C1_search'] == 919 and
            phase['by_dimension']['10']['C1_search'] == 1186,
            'Original 2D/10D C1 source context changed')
    return {
        'schema': 'I65_I55_FRESH_620_ARCHIVED_SOURCE_OUTPUT_LINEAGE_V1',
        'status': 'PASS_FRESH_REPORT_CHAIN_AND_ORIGINAL_SOURCE_CENSUS',
        'original_source_commit': SOURCE_COMMIT,
        'original_root_tree': SOURCE_TREE,
        'original_620_manifest_git_blob': MANIFEST_BLOB,
        'current_full_attestation_sha256': current_full_sha,
        'current_census_sha256': hashlib.sha256(census_bytes).hexdigest(),
        'current_phase_sha256': hashlib.sha256(phase_bytes).hexdigest(),
        'source_620_npz': 620,
        'original_counts': overall,
        'date_field_does_not_require_historical_output_sha_match': True,
        'new_optimizer_PF_OPF_COCO_runs': 0,
        'scientific_status': 'DRAFT / NO-FREEZE / NOT_ESTABLISHED',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', required=True, type=Path)
    parser.add_argument('--census', required=True, type=Path)
    parser.add_argument('--phase', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    opts = parser.parse_args()
    result = verify(opts.full.read_bytes(), opts.census.read_bytes(),
                    opts.phase.read_bytes())
    text = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n'
    if opts.output:
        opts.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
