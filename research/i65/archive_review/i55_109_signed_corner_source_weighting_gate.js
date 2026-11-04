/* Original I55 archive-only C1 signed-corner weighting and duplicate check.
 * Pure function: accepts original SHA-attested census/phase and original Git
 * blob-pinned 109-cell raw signed NPZ event ledger and source file roster.
 * Does not run an optimizer, PF/OPF, COCO, RNG, or statistical hypothesis test.
 * May be required from Node.js or evaluated as a standalone JS expression.
 */
(function () {
  "use strict";
  const SOURCE_COMMIT="6b56fbc53ffc4d275ecef5e911ea4663474c9a08";
  const SOURCE_TREE="f88d221152fcb4157a8e1151a11b53cdfe8180b7";
  const NPZ_MANIFEST="50ca2e96762447070a74309850cb1aa6586d3eb3";
  function requireTrue(ok,message) { if(!ok) throw Error("I55_FAIL_CLOSED: "+message); }
  function fresh() { return {cells:0,C1:0,negative:0,positive:0,first_negative:0,first_positive:0,repeat_negative:0,repeat_positive:0,both_sign_cells:0}; }
  function increment(to,entry) {
    to.cells++;to.C1+=entry.C1;to.negative+=entry.negative_corner_events;to.positive+=entry.positive_corner_events;
    const n=Number(entry.negative_corner_events>0),p=Number(entry.positive_corner_events>0);
    to.first_negative+=n;to.first_positive+=p;
    to.repeat_negative+=entry.negative_corner_events-n;
    to.repeat_positive+=entry.positive_corner_events-p;
    to.both_sign_cells+=n*p;
  }
  function groups(rows,key) {
    let r={};
    for(const row of rows) {
      const name=String(row[key]);
      if(!Object.prototype.hasOwnProperty.call(r,name))r[name]=fresh();
      increment(r[name],row);
    }
    return Object.fromEntries(Object.entries(r).sort(([a],[b])=>a.localeCompare(b)));
  }
  function same(a,b,name) {
    requireTrue(a&&b&&Object.keys(a).length===Object.keys(b).length&&
      Object.keys(a).every(k=>a[k]===b[k]),"group mismatch: "+name);
  }
  function ensureStratum(t,flag,phase,label) {
    requireTrue(flag&&phase,"missing original source stratum "+label);
    requireTrue(flag.flagged_cells.C1===t.cells,"source C1-positive cells "+label);
    requireTrue(flag.flag_occurrences.C1===t.C1,"source C1 events "+label);
    requireTrue(phase.C1_search+phase.C1_post===t.C1,"source phase C1 "+label);
    requireTrue(phase.C1_C2_search+phase.C1_C2_post===t.repeat_negative+t.repeat_positive,
      "source exact C1/C2 repeats "+label);
    requireTrue(phase.C1_post===0&&phase.C1_C2_post===0,"source unexpected C1 post phase "+label);
  }
  function ratio(n,d) {return d ? Math.round(n/d*1000000000)/1000000000:null;}
  function verify(raw,roster,census,phase) {
    requireTrue(raw&&roster&&census&&phase,"missing source data");
    requireTrue(raw.status==="PASS_109_OF_109_ORIGINAL_C1_POSITIVE_NPZ_SOURCE_GIT_BLOBS_AND_BINARY_X_C1_SIGN_REPLAY"&&
      raw.original_entries_rechecked===109&&roster.original_C1_positive_npz===109,
      "original C1-positive source scan not authenticated");
    requireTrue(raw.original_source_commit===SOURCE_COMMIT&&roster.original_commit===SOURCE_COMMIT&&
      census.original_source_commit===SOURCE_COMMIT&&phase.original_commit===SOURCE_COMMIT,
      "immutable source commit mismatch");
    requireTrue(roster.source_root_tree_sha1===SOURCE_TREE&&
      census.original_git_tree===SOURCE_TREE&&phase.source_root_git_tree===SOURCE_TREE,
      "original source tree mismatch");
    requireTrue(raw.original_620_source_manifest_sha1===NPZ_MANIFEST&&
      roster.original_full_620_manifest_blob_sha1===NPZ_MANIFEST&&
      phase.frozen_620_manifest_git_blob===NPZ_MANIFEST,
      "source NPZ manifest mismatch");
    requireTrue(raw.original_109_C1_source_roster_blob_sha1==="f1dd7d1b283eba1ee12562acaf22a144d9c525d5"&&
      raw.independent_js_decoder_git_sha1==="7c0d2bbf23cf7e1dea209651d3778cb0c3030711",
      "direct source provenance pin changed");
    requireTrue(census.original_620_full_attestation_gate_pass===true&&
      phase.all_620_original_npz_replayed_again===true&&
      phase.all_original_git_blobs_authenticated_again===true,
      "prior full original 620-source provenance absent");
    const records=raw.entries,expected=roster.entries;
    requireTrue(Array.isArray(records)&&Array.isArray(expected)&&records.length===109&&expected.length===109,
      "109 original signed-cell roster incomplete");
    let seen=new Set(),all=fresh();
    for(let i=0;i<109;i++) {
      const r=records[i],s=expected[i];
      requireTrue(r&&s&&typeof r.path==="string"&&!seen.has(r.path),"duplicate/missing signed NPZ "+i);
      seen.add(r.path);
      requireTrue(r.path===s.path&&r.source_git_blob_sha1===s.git_blob_sha1&&
        r.library===s.library&&r.function===s.function&&r.d===s.d&&r.seed===s.seed&&
        r.original_calls===s.calls&&r.C1===s.original_C1,
        "original frozen cell and Git blob mismatch "+r.path);
      const path="research/results/iteration55/traces/"+r.library+"/"+
        r.function+"_"+r.d+"_"+r.seed+".npz";
      requireTrue(r.path===path&&(r.d===2||r.d===10)&&
        ["plateau","sphere","rastrigin"].includes(r.function)&&
        Number.isInteger(r.seed)&&r.seed>=6000&&r.seed<=6004&&
        Number.isInteger(r.original_calls)&&r.original_calls>0,
        "invalid original source path/cell schema "+r.path);
      requireTrue(Number.isInteger(r.C1)&&r.C1>0&&
        Number.isInteger(r.negative_corner_events)&&r.negative_corner_events>=0&&
        Number.isInteger(r.positive_corner_events)&&r.positive_corner_events>=0&&
        r.negative_corner_events+r.positive_corner_events===r.C1,
        "original C1 cannot reconcile signed counts "+r.path);
      increment(all,r);
    }
    const byLibrary=groups(records,"library"),byFunction=groups(records,"function"),
          byDimension=groups(records,"d");
    requireTrue(Object.keys(byLibrary).length===8&&Object.keys(byFunction).length===3&&
      Object.keys(byDimension).length===2,"C1-positive original stratum coverage altered");
    same(all,raw.overall,"original signed overall");
    for(const [kind,calc,stored,frozen,prev] of [
      ["by_library",byLibrary,raw.by_library,census.by_library,phase.by_library],
      ["by_function",byFunction,raw.by_function,census.by_function,phase.by_function],
      ["by_dimension",byDimension,raw.by_dimension,census.by_dimension,phase.by_dimension],
    ]) {
      for(const [name,observed] of Object.entries(calc)) {
        same(observed,stored[name],kind+"/"+name);
        ensureStratum(observed,frozen[name],prev[name],kind+"/"+name);
      }
      const sum={};for(const k of Object.keys(all))sum[k]=Object.values(calc).reduce((a,x)=>a+x[k],0);
      same(sum,all,kind+"/all");
      requireTrue(Object.entries(frozen).every(([key,v])=>v.flag_occurrences.C1===
        (calc[key]?.C1??0)),"missing original zero-C1 strata "+kind);
    }
    ensureStratum(all,census.overall,phase.overall,"all sources");
    requireTrue(all.cells===109&&all.C1===2105&&all.negative===2050&&all.positive===55&&
      all.first_negative===97&&all.first_positive===52&&
      all.repeat_negative===1953&&all.repeat_positive===3&&all.both_sign_cells===40,
      "original signed source golden census changed");
    requireTrue(byDimension["2"].positive===55&&byDimension["10"].positive===0&&
      byDimension["2"].both_sign_cells===40&&byDimension["10"].both_sign_cells===0,
      "original signed direction/dimension mismatch");
    const onlyNegative=all.first_negative-all.both_sign_cells,
          onlyPositive=all.first_positive-all.both_sign_cells;
    requireTrue(onlyNegative===57&&onlyPositive===12&&
      onlyNegative+onlyPositive+all.both_sign_cells===109,
      "original unique-corner cell occupancy failed");
    const ordered=records.slice().sort((a,b)=>b.C1-a.C1||
      a.path.localeCompare(b.path));
    const top5=ordered.slice(0,5).reduce((s,x)=>s+x.C1,0);
    const libraryRepeat=Object.entries(byLibrary).map(([library,x])=>({
      library,repeats:x.repeat_negative+x.repeat_positive,
      repeat_share:ratio(x.repeat_negative+x.repeat_positive,
        all.repeat_negative+all.repeat_positive)
    })).sort((a,b)=>b.repeats-a.repeats||a.library.localeCompare(b.library));
    const topFour=new Set(libraryRepeat.slice(0,4).map(x=>x.library));
    const after=fresh();for(const row of records)if(!topFour.has(row.library))increment(after,row);
    return {
      schema:"I65_I55_109_ORIGINAL_C1_SIGNED_CALL_VS_FIRST_CORNER_WEIGHTING_V1",
      original_git_source_commit:SOURCE_COMMIT,
      source_original_109_npz_git_identity_and_c1_roster:"PASS_BY_PINNED_SOURCE_LEDGER",
      prior_original_full_620_source_ci:"PASS_41804478669",
      original_signed_observations:all,
      cells_only_negative:onlyNegative,cells_only_positive:onlyPositive,
      cells_both_signed:all.both_sign_cells,
      negative_fraction_all_C1_event_calls:ratio(all.negative,all.C1),
      negative_fraction_first_distinct_signed_corners_per_cell:
        ratio(all.first_negative,all.first_negative+all.first_positive),
      negative_fraction_exact_repeated_corner_events:
        ratio(all.repeat_negative,all.repeat_negative+all.repeat_positive),
      fraction_all_C1_events_that_are_exact_repeats:
        ratio(all.repeat_negative+all.repeat_positive,all.C1),
      most_active_five_original_C1_cells_events:top5,
      most_active_five_original_C1_cells_fraction:ratio(top5,all.C1),
      library_repeat_concentration_ranked:libraryRepeat,
      exploratory_exclude_top_four_repeating_libraries:{
        excluded_libraries:[...topFour],
        descriptive_remaining:after,
        negative_fraction_event_calls:ratio(after.negative,after.C1),
        negative_fraction_first_corners:ratio(after.first_negative,
          after.first_negative+after.first_positive),
        caveat:"POST_HOC sensitivity diagnostic; not an inferential estimate or preregistered exclusion."
      },
      causal_bug_or_general_optimizer_bias_established:false,
      new_optimizer_PF_OPF_COCO_runs:0,
      newest_head_Github_CI:"NOT_OBSERVED",
      scientific_status:"DRAFT / NO-FREEZE / NOT_ESTABLISHED"
    };
  }
  const api={verify,ratio};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  return api;
})()
