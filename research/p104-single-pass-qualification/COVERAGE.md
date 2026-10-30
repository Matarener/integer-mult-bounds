# Coverage preservation

The source is the complete official PR #5831 export at `7c5eb98e7439d778141d63e801e53d4cd7e1d587`, containing the unchanged PR #5826 source at `58f93cf41751920f3d6766a39caccc2974ce18b0`. `source.py` authenticates every outer file/mode and the entire archive before importing; the original source context authenticates the nested archive and checks every declared contract edit. Frozen files and the arithmetic backend are not edited.

| Obligation | Frozen full qualification | Proposed qualification |
|---|---|---|
| Integer complete contract | Exact `contract.calculate(p, Engine(reference))` | Same calculation, with an observational proxy that forwards every call |
| Fraction complete contract | Unchanged `original.calculate()` | Same function and newly loaded original module, observed via a scoped module-factory seam; restored in `finally` |
| Actual dimensions | 25,984 events, 799 coordinates, every arbitrary-input/native/ownership check | Same word in both complete calculations |
| Source result | Both complete encoded outputs equal original RESULT | Same two checks plus full output equality |
| Ideal metadata and local weights | Extra full reference and integer ideal passes, compared | Compare complete deep-copied first-pass outputs from the two independent calculations |
| Actual error trace and all signed witness dictionaries | Extra reference/integer error passes, compared | Compare complete deep-copied first-pass outputs from the two independent calculations |
| Final transpose scores and signed coefficients | Each full calculation calls unchanged `reverse_all` and checks all values/hashes | Unchanged in both calculations |
| Attaining prefix/input fixtures | Each complete contract uses unchanged `reverse_cut` and literal `execute` | All retained; no sampled rows |
| Additive COPY/reset semantics | Both complete contracts run every original residual fixture and six rejections | All retained; malformed-word calls still reach the backend and cannot replace the actual observation |
| Dyadic finite differential | Original seeded 120 programs/4,240 events, complete trace/witness and reverse equality | Call original `fixtures` unchanged with raw independent reference and integer backend |
| Integer validity failures | Nondyadic scalar, inexact division, nondyadic weight | All three retained |
| Precision guards and scale | Prefix/public/owned 26/23/22, coefficient scale 55 | Exact same receipt, not a weaker subset |
| Source isolation | Distinct Fraction module and explicit contract/backend under authenticated source context | Same source authentication and distinct modules; no cross-backend value sharing |
| Timeout | Original full qualification 180 seconds | 180 seconds; unchanged numerical or proof limits |
| Shared tooling tests | Full CI plan has 513 tests and 22 platform skips | No shared script, test, wait, fixture or skip changes; nominated group all ten pass in profile |

The omitted repeated calculations are deterministic calls of byte-identical functions with identical complete inputs inside one successful invocation. The replacement observations retain their complete output values. This is intra-invocation common-work elimination; it is not an independent extra scientific oracle. The two arithmetic representations and all original literal/transpose oracles still execute independently. Cold process/source authentication occurs on every qualification. Nested source scratch keeps the predecessor's private writable semantics; this contribution adds no claim that it is sealed.

## Observation lifetime and failure rules

A context binds the canonical complete word. Only the actual successful ideal and trace calls can be recorded, once each. The trace must use the observed ideal's exact weights and operation set. Arguments are checked before/after invocation, outputs are deep-copied, and snapshots are hashed again at consumption. Each backend has a separate context. Outputs cannot be consumed until the full enclosing contract has succeeded, and can be consumed only once. A backend exception on the actual word aborts its observations. Any exception in the complete candidate/parallel Fraction calculation aborts both contexts. The source module factory is restored even on failure. Nothing is persisted between commands.

The finite feasibility gate uses the real frozen backends, a valid five-event COPY/SCALE/CLEAR word, complete fresh reruns, and 27 explicit failure/isolation controls. It runs both normally and under `-O`; checks use explicit exceptions. The original finite corpus and original scientific rejections are additional coverage.

## Limits

This covers the frozen contract only. Different source bytes, word, weights, operations, ownership semantics, backend or oracle require a fresh binding and feasibility gate. Assisted local review and CI do not prove the multiplication theorem, supplier admission, exact physical reset, a funded kappa gain or independent human review.
