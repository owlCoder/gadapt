"use strict";
/* Date-safe SHA256 lineage of freshly generated original I55 CI outputs.
 * Git blobs / original immutable source IDs remain fixed; derived JSON bytes
 * may change if their attestation carries a new execution date.
 * Read-only: no optimizer, simulations, experiment or network.
 */
const fs=require("node:fs");
const crypto=require("node:crypto");
const SOURCE="6b56fbc53ffc4d275ecef5e911ea4663474c9a08";
const TREE="f88d221152fcb4157a8e1151a11b53cdfe8180b7";
const MANIFEST="50ca2e96762447070a74309850cb1aa6586d3eb3";

function loadCurrent(dir=".") {
  function fetch(file) {
    const raw=fs.readFileSync(dir+"/"+file);
    return {raw,json:JSON.parse(raw.toString("utf8"))};
  }
  const full=fetch("i55_620_original_readonly_audit.json");
  const census=fetch("i55_620_original_flag_census.json");
  const phase=fetch("i55_620_npz_phase_duplicate_context.json");
  const currentSha=crypto.createHash("sha256").update(full.raw).digest("hex");
  const f=full.json,c=census.json,p=phase.json;
  if(f.status!=="PASS"||f.full_attestation_pass!==true||
     f.manifest_git_blob!==MANIFEST||
     f.original_git_tree?.source_commit!==SOURCE||
     f.original_git_tree?.original_root_tree_sha1!==TREE||
     f.npz_byte_gate?.full_git_blob_pass!==true||
     f.npz_byte_gate?.raw_bytes_verified!==620||
     f.original_trace_replay?.npz?.full_raw_trace_pass!==true||
     f.original_trace_replay?.npz?.checked!==620||
     c.original_620_full_attestation_sha256!==currentSha||
     p.full_attestation_json_sha256!==currentSha||
     c.original_source_commit!==SOURCE||p.original_commit!==SOURCE||
     c.original_git_tree!==TREE||p.source_root_git_tree!==TREE||
     c.original_manifest_git_blob!==MANIFEST||p.frozen_620_manifest_git_blob!==MANIFEST||
     p.all_original_git_blobs_authenticated_again!==true||
     p.all_620_original_npz_replayed_again!==true)
    throw Error("FRESH_ORIGINAL_SOURCE_FAIL_CLOSED: current full/census/phase output lineage differs");
  return {full:f,census:c,phase:p,current_full_sha256:currentSha};
}
module.exports={loadCurrent};
