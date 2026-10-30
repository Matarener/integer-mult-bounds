# Adaptive compiler width from multiplicative shells

For a fixed target/paid rank alphabet, adjoin its height base M and let r
be the rational rank of the prime-valuation vectors. This package proves
an effective bound of K(ell+1)^(r-1) on the number of semigroup products in
[M^ell,M^(ell+1)). It answers Open next question 1 of Nick Petalas's
[PR5962](https://github.com/CrocSwap/integer-mult-bounds/pull/5962).

Applied to the unchanged level-LCM divisor of codyw912's
[PR4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638), it gives

| Fixed adaptive regime | New upper bound for log B_N |
| --- | --- |
| z=max(0,1-g log_M k0)>0 | O(N^z (1+log N)^r) |
| z=0 | O((1+log N)^(r+1)) |

The historical p16 source has r=11 and z=3/5. Its bound improves from
O(N^(3/5)(1+log N)^12) to O(N^(3/5)(1+log N)^11). **The compiler and its
actual widths are unchanged.** This is a conditional compiler-size result,
not a new multiplication exponent or a physical memory/runtime reduction.
The effective constant can be large; it is an upper bound, not an optimum.

[PROOF.md](PROOF.md) proves the shell lemma, states every inherited compiler
hypothesis, derives an explicit integer bit envelope and separates z=0.
The new shell argument uses r-1 integer forms whose common kernel is the
height-base direction. Each fiber contributes at most v_p(M) points to a
half-open shell. Ordinary prime factorization and linear algebra are not
claimed as new; the source-bound shell and compiler application are the
contribution.

## Exact caller and predecessor scope

The caller is `research/adaptive-chronological-batching/batching.py`:
`compile_widths`, `batch_rows` and `multiplier`. The consumed theorem is
that package's `WIDTH.md` sections 1-4. Its executable uses cutoff n0=m and
positive a,b, hence g=a+b>=2. The general written theorem also permits
n0>=m and g>=1; the executable fixtures do not claim those extra modes.
The proof retains paid rank one, nonempty sources, every chronological cut,
all source-count primes and the inherited child-decrement bound.

The p16 binding reads the exact `rank-convergence/BENCHMARKS.json` entry
and its named `compact-joint-compiler/arithmetic/RESULT.json`: m=145,
k0=4, M=1024, g=2, W=10928, P=64620. An independent integer determinant
of a full 11-by-11 valuation minor is -1. The relation
1024^2=4^(5*2) verifies z=3/5 without floating point. The conservative shell
constant used here is 1104622125411204510010.

PR4638 head `385a4436a47ea8e80cc1503948fe7a36e1b1c5af` supplies the
adaptive compiler and level-LCM theorem. PR5962 head
`6f87acd840f31a092238ecf7e5c455289430878a` supplies the default-height
multiplicative-rank result and this open question. Both are archived,
partially reviewed sources; their scientific assumptions are used explicitly.
Their original files are unchanged. SOURCES.json pins the retained bytes at
base `721c03822c421b7f7fcbb2598993b947c4d88419`.

## Bounded verification

From the repository root with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/adaptive-shell-width
python3.12 -I -W error -B research/adaptive-shell-width/verify.py
python3.12 -I -O -W error -B research/adaptive-shell-width/verify.py
```

The direct checker is read-only and works in the official Git-free export.
It authenticates all live inputs, then executes the authenticated standalone
predecessor `batching.py` as the object under test. No predecessor scientific
verifier or pricing engine is imported. The semigroup and rank oracles are
independent of that source implementation.

The first Python 3.12 run takes under one second and reports:

- 372 generator/base fixtures, 21,754 member occurrences in 3,054 shells,
  with 20,547 quotient fibers. Multiplicative closure agrees with an
  independent integer-by-integer divisibility oracle. Small valuation ranks
  agree with independent Leibniz minors.
- Three unchanged executable compiler fixtures across both z regimes:
  257 compiled ranks and 1,856 batch rows, including the height boundary at
  cap 16. The all-prime level-LCM divisor divides every actual width, and
  the new exact bit envelope bounds that divisor. Source plateau and child
  decrement checks retain the actual caller boundary.
- Ten rejecting source/domain/semantic controls: invalid bases/generators,
  bad source bytes, missing fiber multiplicity, missing M direction or
  quotient coordinate, closed shell endpoint, z=0 misuse and omitted paid
  generator.

Finite checks corroborate the written theorem and source bindings; they are
not an all-size compiler or native proof. The caller fixtures are small
abstract rules, while the p16 check binds the actual historical profile;
no full p16 compiler is materialized. Validation contains no Python asserts.

## Limits and next questions

This is the alternative adaptive compiler, **not selected PR6030's default
strictified compiler**. The selected result remains conditional kappa
0.003125804 under all five assumptions. Native/all-column semantics,
whole-job adapters, owned erasure, chronological correctness, physical
allocation, routing, precision, tape costs, outer transfer and exact recovery
are not discharged. No Lean, Docker or full selected/historical replay is run.
Independent human and formal-kernel review are unclaimed.

### Open next questions

1. Can exact source valuations or a tighter shell constant improve a named
   finite bound? Retain the actual per-level LCM and compare a proved tighter
   quotient box; the present asymptotic improvement alone does not establish
   a practical finite saving or a lower bound.
2. Which physical resource bound can use this envelope? Bind an emitted
   adaptive program to actual banks, routes and scratch before claiming any
   memory or runtime reduction. These native and physical contracts remain
   the blocker. TASK.json records the precise first steps and limitations.

## Coordination and attribution

Canonical claim: [Discussion6076](https://github.com/CrocSwap/integer-mult-bounds/discussions/6076).
Base main `721c03822c421b7f7fcbb2598993b947c4d88419`, priority8. Preclaim
cached overlap covered 341 open PRs, 5,722 Discussion records and all 8,348
tracked local README/TASK notes. Specific terms led to PR5962's open question;
no competing shell result surfaced. This is bounded text coverage, not a
novelty certificate or a search of arbitrary diffs/unpublished work.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance and a
separate read-only AI proof review. Credit Nick Petalas for PR5962, codyw912
for PR4638, Mihir Srivastava for PR4507/4586, zxv for PR4436/4483, Jacob Alan
Sussman for the integer compiler, Ryanson Jonathan and Cinna Davis for the
retained flow/native lineage, and all source-specific predecessors.
New work is Apache-2.0; no third-party source is modified or vendored.
