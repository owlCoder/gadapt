"use strict";
/* Standalone synthetic regression tests for date-safe current-run Node custody.
 * No archived NPZ reader, optimization, power flow or COCO execution.
 */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const {loadCurrent} = require("./i55_fresh_original_report_lineage_node.cjs");
const SOURCE = "6b56fbc53ffc4d275ecef5e911ea4663474c9a08";
const TREE = "f88d221152fcb4157a8e1151a11b53cdfe8180b7";
const MANIFEST = "50ca2e96762447070a74309850cb1aa6586d3eb3";
const encode = data => JSON.stringify(data, null, 2) + "\n";
const sha = data => crypto.createHash("sha256").update(encode(data)).digest("hex");

function stratum(C1,C2,calls,repeats,cells,extra={}) {
  return {
    census:{original_calls:calls, flagged_cells:{C1:cells}, flag_occurrences:{C1,C2},...extra},
    phase:{calls,C1_search:C1,C1_post:0,C2_search:C2,C2_post:0,
      C1_C2_search:repeats,C1_C2_post:0}
  };
}
function fixture() {
  const full = {
    date:"2026-11-04", status:"PASS", full_attestation_pass:true,
    optimizer_or_power_flow_executed:false, manifest_git_blob:MANIFEST,
    original_git_tree:{source_commit:SOURCE, original_root_tree_sha1:TREE,
      exact_tree_manifest_match:true, original_npz_tree_entries:620},
    npz_byte_gate:{full_git_blob_pass:true,raw_bytes_verified:620},
    original_trace_replay:{npz:{full_raw_trace_pass:true,checked:620}}
  };
  const census = {original_source_commit:SOURCE,original_git_tree:TREE,
    original_manifest_git_blob:MANIFEST,original_620_full_attestation_gate_pass:true};
  const phase = {original_commit:SOURCE,source_root_git_tree:TREE,
    frozen_620_manifest_git_blob:MANIFEST,all_original_git_blobs_authenticated_again:true,
    all_620_original_npz_replayed_again:true,
    all_frozen_objectives_and_flags_matched_again:true, source_npz_count:620};
  const overall = stratum(2105,18779,295445,1956,109,{valid_cells:620});
  overall.phase.post_calls=1200;
  overall.phase.C2_search=17579;
  overall.phase.C2_post=1200;
  census.overall=overall.census;
  phase.overall=overall.phase;
  for (const [group,names] of [
    ["by_library",Array.from({length:21},(_,i)=>"library_"+i)],
    ["by_function",["plateau","sphere","rastrigin"]],
    ["by_dimension",["2","10"]]
  ]) {
    census[group]={};phase[group]={};
    for (const [i,name] of names.entries()) {
      const s=group==="by_dimension" ? (i===0 ? stratum(919,18779,10000,795,84) : stratum(1186,0,285445,1161,25)) :
        (i===0 ? stratum(2105,18779,295445,1956,109) : stratum(0,0,0,0,0));
      census[group][name]=s.census;
      phase[group][name]=s.phase;
    }
  }
  return {full,census,phase};
}
function createRun(t, mutate=()=>{}, relink=true) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(),"i55-lineage-test-"));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const d=fixture();
  const oldSHA=sha(d.full);
  d.census.original_620_full_attestation_sha256=oldSHA;
  d.phase.full_attestation_json_sha256=oldSHA;
  mutate(d);
  if (relink) {
    d.census.original_620_full_attestation_sha256=sha(d.full);
    d.phase.full_attestation_json_sha256=sha(d.full);
  }
  for (const [key,file] of [["full","i55_620_original_readonly_audit.json"],
    ["census","i55_620_original_flag_census.json"],
    ["phase","i55_620_npz_phase_duplicate_context.json"]])
    fs.writeFileSync(path.join(dir,file),encode(d[key]));
  return {dir,oldSHA,newSHA:sha(d.full)};
}

test("synthetic valid current full/census/phase SHA lineage passes",t=>{
  const x=createRun(t);
  assert.equal(loadCurrent(x.dir).current_full_sha256,x.newSHA);
});
test("next-day date change with both freshly relinked children passes",t=>{
  const x=createRun(t,d=>{d.full.date="2026-11-05";});
  assert.notEqual(x.oldSHA,x.newSHA);
  assert.equal(loadCurrent(x.dir).current_full_sha256,x.newSHA);
});
test("next-day full with stale child SHA is rejected",t=>{
  const x=createRun(t,d=>{d.full.date="2026-11-05";},false);
  assert.throws(()=>loadCurrent(x.dir),/FRESH_ORIGINAL_SOURCE_FAIL_CLOSED/);
});
test("stale phase link alone is rejected",t=>{
  const x=createRun(t,d=>{d.phase.full_attestation_json_sha256="0".repeat(64);},false);
  assert.throws(()=>loadCurrent(x.dir),/FRESH_ORIGINAL_SOURCE_FAIL_CLOSED/);
});
test("forged source Git tree rejected even with recomputed child links",t=>{
  const x=createRun(t,d=>{d.full.original_git_tree.original_root_tree_sha1="f".repeat(40);});
  assert.throws(()=>loadCurrent(x.dir),/FRESH_ORIGINAL_SOURCE_FAIL_CLOSED/);
});
test("altered frozen C1 occurrence count rejected",t=>{
  const x=createRun(t,d=>{d.census.overall.flag_occurrences.C1=2106;});
  assert.throws(()=>loadCurrent(x.dir),/frozen original population totals mismatch|original C1\/C2/);
});
test("per-library source stratum mismatch rejected",t=>{
  const x=createRun(t,d=>{d.census.by_library.library_0.original_calls+=1;});
  assert.throws(()=>loadCurrent(x.dir),/original C1\/C2\/calls\/phase mismatch/);
});
test("phase objective and flag source replay must be authenticated",t=>{
  const x=createRun(t,d=>{d.phase.all_frozen_objectives_and_flags_matched_again=false;});
  assert.throws(()=>loadCurrent(x.dir),/current full\/census\/phase lineage/);
});
