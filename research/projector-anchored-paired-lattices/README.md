# Complete paired-lattice tests with projector anchors

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. No new kappa.

A complete family of rank-one projector blocks makes the common paired-lattice
problem decidable by one graph test. This extends the diagonal-only filter in
ywz65's [PR #2671](https://github.com/CrocSwap/integer-mult-bounds/pull/2671) to
every common paired rational lattice under an explicit anchor hypothesis.
The predecessor's test and rank bound are cited, not re-audited.

Put R=Z_(2), the rationals with odd denominators. Supply m orthogonal rank-one
projectors summing to I, each present as an actual block of an applied 2m by 2m
matrix. Every invariant lattice splits along their eigenlines. In an eigenbasis
C it is C diag(2^a_i) R^m, so existence is equivalent to the absence of a negative
cycle in the valuation graph. A checked negative cycle excludes every common
paired lattice in this anchored class. [PROOF.md](PROOF.md) proves this for every
finite rational input and gives the source-model boundaries.

The Walsh-projector family separates the two filters for every m=2^k>=2.
All projector diagonals are 1/m, so every original-coordinate diagonal gauge
fails. The non-diagonal Walsh basis makes all projectors integral. The m
rank-one paid labels multiply exactly to n_I. The existing mW rank floor
applies when its complete Borel-model premises are supplied. This is a family
missed by the diagonal filter, not a paid-rank improvement.

## Reproduction and evidence

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/projector-anchored-paired-lattices/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/projector-anchored-paired-lattices/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-anchored-paired-lattices
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-anchored-paired-lattices --check-source-history
```

Another CPython 3.12 path can replace the absolute path. The direct marker is
`PASS_PROJECTOR_ANCHORED_PAIRED_LATTICES`; registered replay also prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each direct run generates a JSON stdout
receipt bound to every package file's SHA256, without writing files or importing
predecessor executables. All contracts remain enabled under optimized Python.

The replay enumerates all 256 directed two-vertex graphs with each edge weight
in {absent,-1,0,1}. Independent min-plus closure and all three normalized
potentials (0,-1),(0,0),(0,1) agree. Four rational charts and all four matrix
block placements, with diagonal placements restricted to invertible graph
matrices, give 3,552 certificate problems: 1,528 feasible and 2,024 infeasible.
The separate checker reads original matrix entries and imports no graph solver.
The replay also checks Walsh dimensions 2,4,8, thirteen rejected input/certificate
controls and three scope controls. The generated receipt records these counts.
The quantified proof, rather than this finite corpus, establishes completeness.

The controls cover omitted precision shifts, wrong eigenbases, malformed cycles,
unapplied anchors in both producer and checker, non-projector anchor families,
inexact or oversized inputs, singular free reductions, an actually applied
inverse and the difference between integral and unit targets.

The public interfaces are `lattice.solve(anchors, applied)` and
`check.check(anchors, applied, certificate)`. The checker returns True for a
checked invariant lattice and False for a checked impossibility cycle.
Invalid inputs or certificates raise ValueError. The implementation accepts
1<=m<=8, at most 64 applied matrices, and integer/Fraction entries with numerator
and denominator lengths at most 64 bits. Rejected bounds are unsupported inputs,
not negative mathematical results. Certificates contain exact Fraction bases
and Python integers; a JSON interchange API is not supplied.

## Scope, sources and credit

The `bit-new-register-model` card is changed to an analytic obstruction filter
for rational Borel words. This is a side result on a register-model blocker,
without a new native alphabet or selected supplier. The base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the predecessor proof and README, catalogue and
selected record. The source's explicit non-diagonal-lattice direction motivates
the question; its original diagonal-only statement retains its scope.

Credit ywz65 for #2671's paired-diagonal graph filter, Sagar Thakrar for
#2613's 2-integral Borel corollary, eumemic for #288's general lattice method,
and Swapnil Jain for the retained rank functional. Orthogonal-idempotent
decomposition, the rank-one ideal calculation, Walsh orthogonality and graph
feasibility are classical. The contribution is the complete anchored interface,
separating family and certificate implementation. No literature-priority claim
is made for those ingredients. Existing files and credit remain unchanged.

The theorem requires one paired lattice shared across scalar roles and a
complete actual anchor family. The caller must supply the full applied list,
legal operations and formal endpoint. General unanchored inputs, distinct H/D
lattices and non-lattice representations are not decided. No physical basis
conversion, precision/stock/tape bill, native realization, selected scientific
replay, compiler or outer admission is supplied. The five selected framework
assumptions remain. Independent human and formal proof-kernel review are unclaimed.

All loops are bounded by the fixed corpus, matrix dimensions, applied-list limit
or at most m graph passes/cycle edges. Functions stay below 60 physical lines.
Python's dynamic exact arithmetic is a managed-allocation deviation from fixed
memory discipline; finite dimensions, input bit bounds and corpus bound live
resources. There is no recursion, dynamic code generation, network access or
scientific subprocess. Warning-strict execution and package replay are the
applicable diagnostics.

## Open next questions

1. Does an actual candidate Borel word expose a complete family of projector
   blocks at legal contacts? Extract its whole applied list and actual anchors
   before testing it. Native membership and endpoint validity remain prerequisites.
2. Can completeness extend to higher-rank orthogonal projectors? Start with two
   rank-two blocks. Their invariant summands need internal lattices, so scalar
   potentials alone no longer prove completeness.
