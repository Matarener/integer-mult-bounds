# Nonlinear and adaptive centre sharing keeps the fresh-information floor

**Scoped negative result; no new κ.** The selected record and frontier are unchanged.

[centre-causal-tangent](../centre-causal-tangent/README.md) (#3873) proves its 1,152-query floor for uniform
causal *linear* scalar-oracle sharing and lists "a lower bound against nonlinear or adaptive algorithms" as
not established. [centre-history-innovation](../centre-history-innovation/README.md) proves that no decoder,
even nonlinear, of the earlier centre history recovers the call-10 query, and that a fresh *linear*
observation needs complex dimension `m >= 8d`; fresh *nonlinear* observations are left open there.

This package closes that remaining case under the same premises:

- **Theorem 1.** Any fresh observation that is continuous, or semialgebraic (finitely many branches built
  from `+ - x`, division by nonzero values including the dyadic `/2, /4`, real constants, comparisons and
  adaptive reads), still needs **at least 8d complex coordinates** per future owner, the same as the linear floor.
- **Theorem 2.** On a finite b-bit grid the only escape is packing several values into wider words
  (Kronecker substitution). It conserves bits: the widths of the fresh coordinates sum to at least `16db`.
  In the rank-mass model a k-times wider coordinate is a k-times larger child, so the coverage mass
  `72w + 64` and deficit `w - 64` are unchanged.
- **Screen.** Regrouping the 64 centre mass into larger children, which bounds every packing, raises the
  [complex-local-word ceiling](../complex-local-word-ceiling/README.md) by at most **+0.67%**, before guard bits,
  carries, unpacking or hosting are charged. The card's two-call sharing budget (x1.90) needs the fresh
  information halved, which Theorems 1–2 exclude.

| Variant (centre mass 64 kept) | ceiling `a_hi` | x selected ceiling |
|---|---:|---:|
| selected: 8 x rank-8 | 0.00169005411 | 1.000000 |
| pack 2 totals: 4 x rank-16 | 0.00169362555 | 1.002113 |
| pack 4 totals: 2 x rank-32 | 0.00169720789 | 1.004233 |
| pack 8 totals: 1 x rank-64 | 0.00170080115 | 1.006359 |
| ideal regroup: fractional rank-72 | 0.00170141282 | 1.006721 |
| control: halved centre information (4 copies, charge 32) | 0.00321297289 | 1.901107 |

Exact rational brackets are in [RESULT.json](RESULT.json).

## Setting (inherited, not re-proved)

From centre-history-innovation, under its native common-frame and full-space cover-view premises:
`H` (all centre fields of calls 0..9 at every owner) and `Q` (the eight pre-transport fields of call 10 at
common owner `I`) are complex-linear on input differences, and `Q(ker H) = M^8`, `dim_C = 8d`.
Fix a complex subspace `V ⊂ ker H` with `Q|_V : V -> M^8` bijective. `V` has real dimension `16d`.

A sharing scheme for call 10 may use (1) the complete earlier history `H(x)` in any form, cached,
recombined or nonlinearly processed; (2) a fresh observation `E(x) ∈ R^n` (a complex coordinate counts as
two real ones), produced adaptively: which reads happen and what is computed may depend on `H(x)` and on
earlier fresh reads; (3) any decoder `D` with `D(H(x), E(x)) = Q(x)` on legal inputs. The "mutable
eight-slot cache with fresh reads" left open by the predecessor is an instance: the cache is a function
of `H`, the reads are `E`.

## Proofs

**Theorem 1.** On `V`, `H(x) = 0`, so the history gives no information and any adaptivity on it is one fixed
choice. `D(0, E(x)) = Q(x)` and `Q` is injective on `V`, hence `E` is injective on `V`.
Continuous case: no continuous injection of an open subset of `R^{16d}` into `R^n` exists for `n < 16d`
(invariance of domain / Borsuk–Ulam). Semialgebraic case: `V ∩ box` is the finite union of the semialgebraic
pieces on which the branches are fixed; one piece `P` has dimension `16d`; an injective semialgebraic map
preserves dimension, so `16d = dim E(P) <= n`. ∎

**Theorem 2.** The dimension argument fails only for maps with unboundedly many pieces, i.e. bit extraction
on an unbounded grid. On a grid `G ⊂ V` with `2^{16db}` points, `E` injective on `G` needs at least
`2^{16db}` distinct values, so the bit widths of its coordinates sum to at least `16db`. Kronecker packing
attains this, and one bit less collides (checked exhaustively on six small grids by `verify.py`). ∎
That such a grid is a legal fixed-width input set is an inherited premise: the predecessor notes that scaling
its constant witness gives a bounded dyadic counterexample but supplies no fixed-width right inverse.

## Scope and limits

- All premises of centre-history-innovation are inherited (native common-frame contract, full-space cover
  view, one future owner, call 10). Its verifier is replayed unchanged here; its compiler contracts are not rebuilt.
- This is an information floor. The step "8d fresh coordinates => 64 rank-mass units" is the separate
  rank-8-per-channel carrier premise of #3918; nonlinearity does not change it, and the screen bounds what
  any regrouping of that mass could gain.
- The screen uses the fixed selected local word, 112 ports, the nine-stage template and the coverage law.
  Changed words, templates or coverage laws are outside it.
- A terminal-only consumer that never forms the internal call-10 query is a changed contract and is not covered.

## Reproduce

From the repository root (Python 3.12, standard library; about 35 s, mostly the predecessor replay):

```sh
python3.12 -I -B research/centre-nonlinear-fresh-floor/verify.py
python3.12 scripts/research_package.py --package research/centre-nonlinear-fresh-floor
```

Expected: `PASS_CENTRE_NONLINEAR_FRESH_FLOOR premise=8edf9aec270e packing_best=x1.006721 controls=4 no_new_kappa`.
Controls: the halved-information lever reproduces x1.90; a rank-73 child, a mass-losing pack and a corrupted
predecessor digest are rejected. `--write` regenerates `RESULT.json`.

## Open next questions

Structured in [TASK.json](TASK.json):

1. **Terminal-only consumer.** Can a changed consumer avoid forming the internal call-10 query? First step:
   state the complete varying-source-and-target terminal map and test the 112 kernel witnesses of
   centre-history-innovation. Blocked by: no priced changed terminal contract.
2. **Carrier premise.** Does `8d` fresh coordinates force 64 rank-mass units for carriers other than rank-8
   channels? First step: price one alternative carrier with its restoration and hosting bill. The screen
   here caps its ideal gain at +0.67%.

## Credit

Builds directly on Jose Manuel (`jmbarrancoml`)'s centre-history-innovation and its credited lineage,
Clear1nsight's centre-causal-tangent (#3873), Douglas Colkitt's complex-local-word ceiling, the nonlinear
copy-floor line (#703, #785, #814, #888) and the centre-sharing budgets (#1791, #1888, #3075, #3548, #3948).
Prepared by Mark (Matarener) with substantial Claude (Anthropic) assistance. Apache-2.0.
