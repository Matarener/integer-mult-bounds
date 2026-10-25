# Verification coverage

The result is a written characteristic-zero proof with explicit inherited
written dependencies (DEPENDENCIES.md). The Python replay certifies its stated
finite inputs and actual-basis controls. The Lean file proves a reusable
additive restriction core. Neither constitutes a complete formal E8 invoice
theorem, and finite coefficients are not substituted for arbitrary fields.

## Registered replay

```sh
python3 scripts/research_package.py --package research/p112-d3-actual-invoice --check-only
python3 scripts/research_package.py --package research/p112-d3-actual-invoice
```

Python 3.12, standard library only. Direct standalone replay, including from
a Git-free committed export:

```sh
python3 -I -O -B research/p112-d3-actual-invoice/verify.py
```

All scientific assertions use explicit exceptions, so optimization does not
disable them. The direct verifier authenticates the sole live source's SHA256
before parsing its literal SIMPLE basis; it executes no source module.
Package modules are loaded from their exact source bytes, without ambient
module or bytecode substitution. The registered launcher separately checks
all declared source/provenance pins against Git.

The deterministic RESULT.json includes every scientific counter and package
file hash except itself. Regenerate it only by explicit `verify.py --emit`;
normal replay compares the full recomputed JSON and changes no files.

The replay checks:

* Exhaustive integer profiles: eight threshold/eta cases, 19 actual-profile
  occurrences, exact c9 allowances/correction counts, and 381/680 generic
  tail profiles with maximum capacities 40/41. The intrinsic E8 exclusions
  are separately declared inputs, not something the arithmetic checker proves.
  The eta upper endpoint is derived from the raw budget and c9>=0.
* Adapted t2 arithmetic: six necessary minimum profiles, fifteen actual
  profiles and all c9/correction ledgers. Adapted t3 arithmetic: ten all-low
  profiles through inside sum 32, twenty high-containing candidates and
  fifteen transferred residual profiles; sum 33 has a separate merge ledger.
  Their geometric exclusions and correction-pair merge remain written proofs.
* The root-model checker uses frame_pair_geometry.py's E8 reconstruction
  to enumerate all 43,180 affine six-sections,
  full-root spectrum 24/28/32/36, all 5,440 maximal36-root sections and all
  14,794,080 unordered distinct maximal pairs. Their intersection histogram
  is 6:913,920;10:8,225,280;12:5,140,800;20:514,080. The universal
  union bound is computed as max(36+32,66)=68 from this measured spectrum
  and maximal-pair union maximum, then matched to the sharp witness. The sharper
  union 66 statistic applies only to pairs of 36-root sections. An explicit
  disjoint mixed 36/32 pair attains the universal full-root bound68. A changed
  normal-coset equation is rejected by the same section validator.
* All 56 ordered frame pairs, 1792 one-site completion deletions and 224 complete
  characteristic-zero support strata for the new frame-cut argument. All 2,040 matched G2 cuts are also checked, with sharp minimum 24 missing target sites.
* All 42,840 matched two-axis G4 residuals. A fundamental-relation criterion
  proves rank 8 and no coloop. Direct low-pivot elimination independently
  checks 1,271,200 deletions over all 31,711 distinct residual supports.
* A rational actual basis with dim S=11, dim T=6, d=3 and r=1. All actual
  duals are nonzero, raw sum 84 and invoice 83; this is outside the theorem's
  raw budgets and supplies nonvacuity rather than sharpness. The true-T
  certificate covers all 43,435 rank 7 binary flats (43,180 nonempty affine
  sections). Full modular minors handle 43,174 sections. On the six remaining
  sections an EXACT rational low-column rank is used before comparing a
  full modular lower bound; no unsound modular rank-difference inference is used.
* Five profile mutations, four frame-geometry mutations, a genuine false
  matched-live-label G4 counterexample, and omission of one genuine low
  generator from the same S. An exact 12-term singleton-pivot Gram factorization
  checks actual ranks (9,11), nonparallel actual rows and binary cost 84; wrong
  pivot sign and omission of an actual term yield explicit matrix mismatches.
  The omitted-low-generator control recovers a genuine low word outside
  the falsely declared low space.

The double-seven finite input is computed twice: flat_union.py reuses
frame_pair_geometry.py's E8 roots and polar labels; canonical_union.py uses
q(x)=x0*x1+x2*x3+x4*x5+x6*x7, imports no package model and directly checks
both sharp-fixture label ranks. The independent implementation is
canonical_union.py; flat_union.py is not a third model reconstruction.
Both full section/pair spectra and derived universal bounds must agree.
The canonical wrong-coset control preserves both fixture sizes and ranks
but creates a16-root overlap, which the ordinary validator rejects.
These are separate AI-prepared implementations, not independent human review.
The PASS summary reads counters from the computed result, and the consumer
fixture directly requires its measured cost to equal 84.

Full G4, double-seven and true-T checks were run serially under a 256 MiB process-tree RSS
watchdog. Its sampled peaks are observations, not rigorous peak-memory bounds.
Timing and RSS logs live in the private local evidence, rather than in proofs.

## Partial Lean core

Using the pinned Lean 4.21.0 toolchain, sequentially:

```sh
lean -DwarningAsError=true research/p112-d3-actual-invoice/formal/OutsideRestriction.lean
lean -DwarningAsError=true research/p112-d3-actual-invoice/formal/FiniteOutside.lean
```

No Mathlib build is required. The first four declarations prove equality of additive
maps from a C+L cover, injectivity on Ann(L), vanishing from the cover, and
extraction of outside-relation coefficients. The two equality declarations
use `Quot.sound` through function extensionality. The vanishing and coefficient
declarations have no axioms. FiniteOutside adds six declarations, including
one additive helper, and constructs finite scalar combinations from individual
actual coordinate-map laws and biorthogonality; all six have no axioms. Both
exact files compiled without warnings.

The dimension bridge C+L=S, actual vector-space/basis/E8 instantiation, root-system field transfer, geometric exclusions and
full invoice case assembly remain unformalized. See formal/README.md.

## Integrity and unrun coverage

The final local evidence also checks registered metadata, committed file/source
history, official export integrity, Git-free optimized replay, attribution and
`git diff --check`. These integrity checks do not establish the mathematics.

Not run: hosted CI, repository-wide builds, full historical predecessor suites
or independent human review. The complete predecessor written proofs are
explicit dependencies rather than a claim of new formal verification.
