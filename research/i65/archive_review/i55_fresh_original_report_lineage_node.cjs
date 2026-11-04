"use strict";
/* Date-safe, fail-closed SHA256 lineage of fresh original I55 CI outputs.
 * Immutable original source identities stay pinned, but runtime-dated JSON
 * descendants must link to the current full report, not a historical SHA.
 * This does not run an optimizer, simulator, or new scientific experiment.
 */
const fs = require("node:fs");
const crypto = require("node:crypto");
const path = require("node:path");
const SOURCE = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08";
const TREE = "f88d221152fcb4157a8e1151a11b53cdfe8180b7";
const MANIFEST = "50ca2e96762447070a74309850cb1aa6586d3eb3";

function fail(why) { throw Error("FRESH_ORIGINAL_SOURCE_FAIL_CLOSED: " + why); }
function requireTrue(condition, why) { if (!condition) fail(why); }
function integers(...values) { return values.every(Number.isSafeInteger); }

function part(c, p, label) {
  requireTrue(c && p && c.flag_occurrences && c.flagged_cells,
    "missing original stratum: " + label);
  const c1 = p.C1_search + p.C1_post;
  const c2 = p.C2_search + p.C2_post;
  const repeats = p.C1_C2_search + p.C1_C2_post;
  const cells = c.flagged_cells.C1;
  requireTrue(integers(c1, c2, repeats, cells, c.original_calls, p.calls) &&
    c.flag_occurrences.C1 === c1 && c.flag_occurrences.C2 === c2 &&
    c.original_calls === p.calls && repeats >= 0 && repeats <= c1 &&
    cells >= 0 && cells <= c1 && p.C1_post === 0 && p.C1_C2_post === 0,
    "original C1/C2/calls/phase mismatch: " + label);
  const first = c1 - repeats;
  const both = first - cells;
  const one = cells - both;
  requireTrue(both >= 0 && both <= cells && one >= 0,
    "impossible original corner occupancy: " + label);
  return {C1:c1, C2:c2, calls:p.calls, repeats, C1_cells:cells, first, both, one};
}

function loadCurrent(dir = ".") {
  function fetch(file) {
    const raw = fs.readFileSync(path.join(dir, file));
    return {raw, json:JSON.parse(raw.toString("utf8"))};
  }
  const full = fetch("i55_620_original_readonly_audit.json");
  const census = fetch("i55_620_original_flag_census.json");
  const phase = fetch("i55_620_npz_phase_duplicate_context.json");
  const currentSha = crypto.createHash("sha256").update(full.raw).digest("hex");
  const f = full.json, c = census.json, p = phase.json;
  requireTrue(f.status === "PASS" && f.full_attestation_pass === true &&
    f.optimizer_or_power_flow_executed === false &&
    f.manifest_git_blob === MANIFEST &&
    f.original_git_tree?.source_commit === SOURCE &&
    f.original_git_tree?.original_root_tree_sha1 === TREE &&
    f.original_git_tree?.exact_tree_manifest_match === true &&
    f.original_git_tree?.original_npz_tree_entries === 620 &&
    f.npz_byte_gate?.full_git_blob_pass === true &&
    f.npz_byte_gate?.raw_bytes_verified === 620 &&
    f.original_trace_replay?.npz?.full_raw_trace_pass === true &&
    f.original_trace_replay?.npz?.checked === 620,
    "immutable original Git/620-NPZ full attestation mismatch");
  requireTrue(c.original_620_full_attestation_sha256 === currentSha &&
    p.full_attestation_json_sha256 === currentSha &&
    c.original_620_full_attestation_gate_pass === true &&
    c.original_source_commit === SOURCE && p.original_commit === SOURCE &&
    c.original_git_tree === TREE && p.source_root_git_tree === TREE &&
    c.original_manifest_git_blob === MANIFEST &&
    p.frozen_620_manifest_git_blob === MANIFEST &&
    p.all_original_git_blobs_authenticated_again === true &&
    p.all_620_original_npz_replayed_again === true &&
    p.all_frozen_objectives_and_flags_matched_again === true &&
    p.source_npz_count === 620,
    "current full/census/phase lineage or source authentication mismatch");
  const overall = part(c.overall, p.overall, "overall");
  requireTrue(JSON.stringify(overall) === JSON.stringify({
    C1:2105, C2:18779, calls:295445, repeats:1956,
    C1_cells:109, first:149, both:40, one:69
  }) && c.overall.valid_cells === 620 &&
    p.overall.post_calls === 1200 && p.overall.C2_search === 17579 &&
    p.overall.C2_post === 1200,
    "frozen original population totals mismatch");
  for (const [key, count] of [["by_library",21],["by_function",3],["by_dimension",2]]) {
    const left = c[key], right = p[key];
    requireTrue(left && right && Object.keys(left).length === count &&
      Object.keys(right).length === count &&
      Object.keys(left).every(name=>Object.hasOwn(right,name)),
      "original stratum coverage mismatch: " + key);
    const parts = Object.keys(left).map(name=>part(left[name],right[name],key+"/"+name));
    for (const field of Object.keys(overall)) {
      requireTrue(parts.reduce((n,item)=>n+item[field],0) === overall[field],
        "original stratum sum mismatch: " + key + "/" + field);
    }
  }
  requireTrue(p.by_dimension["2"]?.C1_search === 919 &&
    p.by_dimension["10"]?.C1_search === 1186,
    "frozen original dimension-specific C1 counts mismatch");
  return {full:f, census:c, phase:p, current_full_sha256:currentSha};
}
module.exports = {loadCurrent};
