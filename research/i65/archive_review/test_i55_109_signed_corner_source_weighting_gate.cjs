/* Node 22 standard-library-only original I55 source-evidence gate tests.
 * Run after the existing original 620-source full-clone census and phase audits:
 * node --test research/i65/archive_review/test_i55_109_signed_corner_source_weighting_gate.cjs
 * This DOES NOT execute any optimizer, objective, PF/OPF or COCO experiment.
 */
"use strict";
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const test=require("node:test");
const assert=require("node:assert/strict");
const api=require("./i55_109_signed_corner_source_weighting_gate.js");

const DIR=__dirname;
const ROOT=path.resolve(DIR,"../../..");
const LEDGER="I65_I55_ORIGINAL_109_C1_POSITIVE_NPZ_SIGNED_CORNER_DIRECT_BINARY_REPLAY_2026-11-04.json";
const ROSTER="I65_I55_109_C1_POSITIVE_NPZ_ORIGINAL_SOURCE_ROSTER_2026-11-04.json";
function gitBlob(raw) {
  return crypto.createHash("sha1").update(Buffer.from("blob "+raw.length+"\0")).update(raw).digest("hex");
}
function loadPinnedGit(file,expectedBlob) {
  const raw=fs.readFileSync(path.join(DIR,file));
  assert.equal(gitBlob(raw),expectedBlob,"Original Git blob SHA-1 mismatch: "+file);
  return JSON.parse(raw.toString("utf-8"));
}
const ledger=loadPinnedGit(LEDGER,"7f1716b061d703d5ab8c367d73386371dcb9d7a9");
const roster=loadPinnedGit(ROSTER,"f1dd7d1b283eba1ee12562acaf22a144d9c525d5");
// Unlike immutable original NPZ/blob hashes, newly generated JSON carries a
// fresh attestation date. Verify CURRENT full -> CURRENT census/phase SHA
// lineage and original frozen Git identities, not yesterday's output SHA.
const {census,phase}=require("./i55_fresh_original_report_lineage_node.cjs").loadCurrent(ROOT);
const copy=value=>structuredClone(value);
function failsClosed(label,mutation) {
  test(label,()=>{
    const l=copy(ledger),r=copy(roster),c=copy(census),p=copy(phase);
    mutation(l,r,c,p);
    assert.throws(()=>api.verify(l,r,c,p),/I55_FAIL_CLOSED:/);
  });
}
test("full original SHA-authenticated source corner reweighting",()=>{
  const result=api.verify(ledger,roster,census,phase);
  assert.equal(result.original_signed_observations.C1,2105);
  assert.equal(result.original_signed_observations.negative,2050);
  assert.equal(result.original_signed_observations.positive,55);
  assert.equal(result.original_signed_observations.first_negative,97);
  assert.equal(result.original_signed_observations.first_positive,52);
  assert.equal(result.original_signed_observations.repeat_negative,1953);
  assert.equal(result.original_signed_observations.repeat_positive,3);
  assert.equal(result.cells_only_negative,57);
  assert.equal(result.cells_only_positive,12);
  assert.equal(result.cells_both_signed,40);
  assert.equal(result.most_active_five_original_C1_cells_events,851);
  assert.deepEqual(result.exploratory_exclude_top_four_repeating_libraries.excluded_libraries,
    ["bofire","baybe","evolopy","emukit"]);
  assert.equal(result.exploratory_exclude_top_four_repeating_libraries.descriptive_remaining.C1,118);
  assert.equal(result.new_optimizer_PF_OPF_COCO_runs,0);
});
failsClosed("modified original positive sign count rejected",(l)=>l.entries[0].positive_corner_events++);
failsClosed("duplicated original NPZ path rejected",(l)=>l.entries[1].path=l.entries[0].path);
failsClosed("missing one original NPZ row rejected",(l)=>l.entries.pop());
failsClosed("replaced original Git NPZ blob SHA rejected",(l)=>l.entries[0].source_git_blob_sha1="a".repeat(40));
failsClosed("modified original signed total rejected",(l)=>l.overall.negative--);
failsClosed("forged original Git tree rejected",(_,r,c)=>c.original_git_tree="b".repeat(40));
failsClosed("modified original source C1 library cell population rejected",(_,r,c)=>c.by_library.baybe.flagged_cells.C1++);
failsClosed("modified original C1/C2 exact-repeat count rejected",(_,r,c,p)=>p.by_function.plateau.C1_C2_search++);
failsClosed("modified original immutable source roster rejected",(_,r)=>r.entries[0].git_blob_sha1="c".repeat(40));
failsClosed("forged original dimension rejected",(l)=>l.entries[0].d=10);
failsClosed("forged zero-C1 library flags rejected",(_,r,c)=>c.by_library.cma.flag_occurrences.C1=1);
failsClosed("forged original source root ref rejected",(_,r,c,p)=>p.original_commit="d".repeat(40));
