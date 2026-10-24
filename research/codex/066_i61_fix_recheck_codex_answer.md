**FIX FIRST.** Read-only and result-blind; no prohibited results or logs opened.

| Remaining item | Status |
|---|---|
| Fallback tree verification | **Closed:** existing tree is removed and freshly extracted from `17e9ce7`. |
| Gate exceptions | **Closed:** ordinary execution exceptions produce a failed attempt and permit fallback. |
| Both attempts bound + hash chain | **Partial:** available attempts, embedded manifests and complete regression stdout/stderr are hash-bound. Downstream verification omits archive/test-source revalidation and selected-attempt provenance comparison. |
| Test import order | **Closed:** I61 imports before I56. |
| Output hashes + recursive chain + create-once | **Closed at consumption:** published output hashes and recursive input bindings are verified; completed stages reject reruns. |
| Power/analyse revalidation | **Partial:** both now publish through `finish()`, but its dependency validation remains incomplete. |
| select_b/fxt witnesses | **Closed:** both are witness sources and explicit check inputs. |
| Unplanned units | **Closed:** analysis rejects unexpected units, unknown arms and duplicate arm records. |

Exact remaining edits:

1. In [`verify_gate()`](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:142), load the selected attempt; require its `passed`, compare its embedded build manifest with `manifest_gate` using `same_provenance`, and recheck its archive and regression-test-source hashes. Those source hashes are currently checked only during `select_gate()`.

2. In [`finish()`](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:187), compare the verified gate/roster hashes with `before["gate_sha256"]` and `before["roster_sha256"]`; also compare gate provenance with `after`. For each input, retain the direct hash comparison **and call `verify_chain(producer, after)`**. Currently a transitive ancestor can change during a stage without preventing publication.

3. Bind `manifest_frozen.json.gz`’s hash in the completed `test_ref` manifest and verify that binding recursively and before later publications. In [`stage_test_ref()`](/Users/danijel/Desktop/gadapt/research/iteration61_replication.py:748), capture that hash **after writing the freeze, before executing references**. Later stages must check the original binding, alongside frozen choices/build checks. `finish()` currently ignores frozen-manifest changes.

Normal-order trace: **no spurious STOP found on the passing path** through gate → dev_ref → select_b → fxt → stopcheck → rehearsal → power → test_ref → test → check → analyse. `publish()` never re-enters the create-once guard. The freeze written inside `test_ref` therefore does not block its publication. Check’s new select_b/fxt dependencies have completed producer manifests by then.

Publishing diagnostics before a protocol STOP is intentional; subsequent reruns correctly require a new experiment directory.

Validation: an in-memory execution of the actual provenance helpers passed all ten post-gate publications and confirmed the final-validation gaps above. I did not rerun the reported 12-test suite.