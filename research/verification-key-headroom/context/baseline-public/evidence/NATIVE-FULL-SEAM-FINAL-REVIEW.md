# Native full-qualification seam: final static review

**No remaining concrete blocker was found in the requested static scope after the boundary repairs below.** The repaired native implementation may proceed to the parent's fresh complete cold B/C gate. This is a source review, not an independent execution, memory-safety proof for arbitrary Python callbacks, or performance admission.

Reviewed C source: `78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb`.
Reviewed `full.py`: `ce6f15ca892db095d4b9f79b58cb3c199b18da341def761c577cc8651abc0cc0`.
Reviewed `fraction_table.py`: `d70f8095002ffedb06fd6851e5b6d127e2f24c3ad31404130216345416159cf4`.

## Boundary repairs confirmed

- Cache construction now fetches each token with checked `PySequence_GetItem`, owns that result, releases it on rejected type/range, and transfers it into the immutable snapshot tuple on success. The earlier unchecked caller-list access is gone.
- Contribution member reads now check each result immediately; scalar Event initialization stops immediately if the numerator getter fails before reading the denominator.
- `checked_compute` resolves raw Contributions MRO dictionaries through `type.__getattribute__`, requires an exact staticmethod and exact FunctionType, then checks code shape, defaults/closure and effective captured builtin abs. Qualification no longer invokes an arbitrary compute descriptor or treats a plain method as equivalent.
- The native loader compiles a read-only snapshot of authenticated bytes and rejects cached-module/source-digest disagreement.

Parent reports a failed attempt to force constructor GC interleaving: its callback did not run inside the constructor. That attempt and draft remain preserved. The replacement deterministic ownership test supports metadata lifetime behavior; it does **not** empirically exercise the previously hypothesized GC interleaving. The checked item-read source fix removes the unchecked access without that empirical claim.

## Complete seam inspection

The outer authenticated PR5848 export supplies `candidate.py`. `full.py` requires exactly one literal Observation seam and adds the native error-trace wrapper only for the original `noisy_precision` module at that seam. The existing Observation wrapper still surrounds it.

The following remain in the frozen candidate code and are not replaced:

- The separately loaded integer Engine and its Observation.
- The independently loaded reference module used by the original 120-program differential and integer guards.
- Full expected contract-result equality, six source semantic controls, reverse-all/cut and literal checks performed by the original contract.
- Complete ideal/weight and actual trace/witness comparisons between the retained observations.
- Original observation lifecycle/error/alias controls in `candidate.main` and the exact frozen final receipt comparison.

The C branch first executes the full native finite entry, including its inherited gates and cold build, then invokes the original candidate main with that single seam changed. The native actual wrapper checks route selection, exact table counters and the complete output digest. Its capture predicate uses program length; that identifies the sole call only because this exact frozen `calculate` invokes that module's `error_trace` once. Do not generalize the predicate into a general-purpose actual-word classifier. A direct complete word equality assertion would be clearer if this wrapper is later generalized.

The stale-module cleanup is limited to `source` and `observe` modules whose files belong to expired owned temporary exports. The fresh package is then placed first on the import path. No accepted numeric result is reused; only already loaded native code is reused within the one C process. Cache/Event state remains per trace.

## Measurement and claim boundary

The complete benchmark must use **outer command wall and total user/system CPU including children**. The returned/printed `qualify` seconds exclude the preceding native finite suite and its build, so they cannot decide the threshold. Each fresh C process must pay its own compile/link/load cost.

The predecessor's four custody controls are a separate registered-verification obligation outside its declared qualification benchmark. They must remain in the final registered verification; this seam review does not silently count them as executed by `full.py`.

Parent subsequently reports the completed fresh-process B,C,C,B,B,C measurements:

| Complete qualification median | Baseline | Native candidate | Saving |
| --- | ---: | ---: | ---: |
| Wall seconds | 40.516155579 | 32.771296680 | 19.1155% |
| Total CPU seconds | 40.33 | 32.74 | 18.8197% |

All complete scientific receipts, native counters and full output digests reportedly agree. Parent also reports a complete optimized run passing at 32.5805 wall / 32.51 CPU seconds. These are parent-run local measurements, not executions independently repeated by this static reviewer. They supersede the earlier feasibility model as the parent's evidence for clearing the mandatory 15% threshold in both metrics. They are not a hosted-CI performance claim or a guarantee for another interpreter, compiler or machine.

The final package should retain registered finite/native checks, the cold compilation path and four inherited custody controls, with the expensive full replay explicitly opt-in as planned. Preserve exact sources, complete timing receipts, earlier failures and negative micro findings. All implementation blockers identified in this review are resolved in the reviewed source. Further optimization, including any C arithmetic port, requires a separate bounded round after publication; no such round was started here.

No compiler, native import, numerical test, replay or external publication was performed by this reviewer. This addendum supersedes the three outstanding implementation items in `NATIVE-CACHE-CODE-REVIEW.md`; its raw-packet/stable-runtime and coverage boundaries remain applicable.
