# Exact gate setup reuse inside one literal interpreter

The object is the complete PR #5818 qualification at `a0171b8d2f942cdfc5295307548fe484c570b1ba`, retaining exact PR #5757 `53006fe6031dab5c23d5b7d1cf6a92f411a04a68`. The second sparse literal interpreter and quadratic engine are unchanged and share no new setup cache with the dense literal interpreter.

## What the profile permits

There are 17,651 distinct width/circuit keys among 17,651 actual state inputs: a whole-circuit tableau cache has no hits. Tableau construction takes 7.222 seconds in the profiled run, too little to meet the requested 15% whole-run threshold even if removed. This rejected nomination is preserved in PROFILE.json.

The dense literal state loop takes 117.684 seconds. Its P gates compute the same pure address map for every amplitude; its D gates compute a fixed quadratic phase for every amplitude. The actual corpus visits 37,924 P and 47,273 D gates. Setup reuse is limited to their independently computed scalar tables, not state vectors, accepted results or the other interpreter's data.

## Exactness and complete keys

Fix a valid width `0 <= n <= 9`. For a P gate define `images[x] = original_mv(rows,x)` for every `0 <= x < 2^n`. For a D gate define `phases[x] = original_qvalue(Q,alpha,x,n)` on the same domain. Both functions are the unchanged helpers captured from this dense literal compiler; no quadratic engine or sparse-interpreter result is consulted.

The cache key is the complete typed immutable pair `(n, gate)`, including every matrix row and every phase coefficient. Lists are recursively copied to tuples. Boolean/float aliases, shape changes and unsupported widths reject before lookup. A hit returns the same immutable integer tuple a fresh evaluation would compute. The LRU stores at most 512 tables, each with at most 512 entries; source-key storage is additional. Eviction merely requires recomputation; exceptions are never accepted or cached. Bounds concern this frozen source and declared width/key domain, not arbitrary-size compiler workloads.

## Source-bound method derivation

The complete original `Op.zero_state` text is pinned by SHA256 `ebb92d6870d73dc452faf6d8c3c62710539ffb9bae3a5588dc694fe2693c6509`. The AST transformer requires exactly one P branch, one D branch, one `mv(e[1],x)` and one `qvalue(e[1],e[2],x,self.n)` call. It adds one setup retrieval at the start of each of those branches and replaces only those two scalar calls with indexed lookups. All other statements are retained. The derived AST has SHA256 `eb4c3f7790c6b262fb0e4167b26be34f358d82498606d1ba9b448716274fe5b8`.

For every amplitude address the replacement value equals the original pure function by construction. Therefore the vector after a P gate, including zero entries, is identical; after a D gate every signed Gaussian amplitude and absolute phase is identical. The C/X/global-phase arithmetic, gate chronology and all denominator/divisibility reductions are untouched. Induction over the unchanged circuit loop proves equality of the returned complete dense vector and denominator on this domain. Fresh output allocation is unchanged; no mutable state-vector answer is stored.

The hook applies only when the unchanged cross checker loads `selected_cross_literal_compiler`. The original source execution and original adapter controls execute before that point. The loader and method are restored in `finally`, and exactly one installation plus actual bounded cache hits are required. The second literal interpreter, its tableaux and its own existing implementation are unchanged. These are still two separate arithmetic implementations, although the dense one now reuses its own exact setup.

## Full qualification and failure coverage

The original complete RESULT/CROSS comparisons remain active. They bind all actual state-call counts, all 17,651 inputs, 9,037,312 amplitude entries per literal interpreter, exact denominators and trace SHA256 `73ac04db73d83151efb474925d48298664cc7490d31bdec7a70dcf79b448f481`. Every amplitude comparison still occurs; no sampling, orbit quotient, cached PASS or stored state vector replaces one.

All PR #5818 stage/contamination/exception and source-custody controls are retained. Every positive run also executes original PR #5757 controls: the adapter corpus, complete cache/type/mutation/capacity/eviction checks, three proof-omission controls and explicit optimized width rejection. The new finite setup corpus independently compares the original dense method with its derived method on 1,522 complete state cases and 22,700 amplitude entries, including four width-nine cases. It tests complete keys, changed inputs/phase/width, immutable results, numeric aliases, bounded capacity, eviction, uncached exceptions and the literal-method source pin. Normal and deliberate optimized validation remain separate.

The complete original PR #5818 package is retained as its authenticated official 45-file export. All member hashes, inventory and head are checked before imports; private baseline and scientific source exports are Git-free/read-only and checked after success. An unmerged Git object is not a runtime dependency. No frozen predecessor, source word, scientific receipt or selected metadata is edited.

## Limits and attribution

The PR #5818 single-process source-sharing boundary remains: this is not a second cold source replay. This proof concerns exact verification computations, not native provider legality or a multiplication theorem. The five framework assumptions, conditional kappa and selected record remain unchanged. Same-agent implementation/checking and hosted CI do not constitute independent human or proof-kernel acceptance. Performance is a source/host-bound measurement, not a universal guarantee.

Ali Romman supplied the original dense/sparse interpreters, PR #5704 engine, PR #5757 integration and controls; PR #5816 supplied Linux qualification and the guard; PR #5818 supplied single-pass orchestration. Preserve their full native/controller/compiler/helper/BIT/classical stabilizer notices in the retained bundle and NOTICE. New setup derivation, controls, profiling and validation: Chris R / Clear1nsight with substantial OpenAI Codex assistance, no subagents. Memoization and tabulation are standard techniques. Apache-2.0.
