# QQ16 parking with its global-root cutoff

**Scoped proof with exact finite corroboration; no new kappa.** The literal
historical QQ16 child backend stops at `w < 73 or w**1000 < d`, where d is
the global root-width descriptor. This package extends Nick Petalas's
[#4865 fixed-cutoff parking law](../qq16-parking-power-law/README.md) to that
varying cutoff and determines the exact selected-C row-division depth.
It answers part of that package's second open question. The complete
matched QQ16 cost comparison remains open.

Put `T_d=max(73,ceil(d**(1/1000)))`, `C=255331/7168`, `a=3456/25`, and let s
be #4865's existing moment root. For w>=T_d, the normalized parking mass is
bounded uniformly by

\[
\frac{((w+a)/(T_d-1+a))^s-1}{C-1}
\le H_d(w)\le
\frac{(w/\lfloor T_d/73\rfloor)^s-1}{C-1}.
\]

In fact `H_d(w)=Theta((w/T_d)**s)` uniformly for w>=T_d. Thus the diagonal
recurrence has `H_d(d)=Theta(d**(999*s/1000))`, with constants independent of d.
This concerns normalized current-bank parking volume;
physical volume, admission and the complete cost are additional obligations.
The fixed-cutoff theorem remains unchanged and correctly scoped.

The maximum-rank path
`w -> 48 floor(w/73)`, stopped at T_d, gives the exact division depth D_d(w).
Equivalently, the smallest widths reaching j divisions are `B_1=T_d` and
`B_(j+1)=73 ceil(B_j/48)`; this supplies a separate exact depth oracle.
Every selected-C row division is positive and exact precisely when
`(14336 Gamma)**D_d(w)` divides the positive incoming row count. At the
historical `d=isqrt(2**16949)`, the depth is **13997**, versus the existing
cutoff-free sufficient depth **13999**. This does not install smaller root
stock. [PROOF.md](PROOF.md) proves the envelope, its changing-root consequence,
the exact divisibility statement and logarithmic depth bounds.

## Evidence and reproduction

```sh
python3 -B scripts/research_package.py --package research/qq16-root-cutoff-parking --check-only
python3 -B scripts/research_package.py --package research/qq16-root-cutoff-parking
```

Expected scientific status: `PASS_QQ16_ROOT_CUTOFF_PARKING`. Python 3.12 and
the standard library suffice. The registered normal and optimized runs are
read-only and compare the full deterministic [RESULT.json](RESULT.json).
Only `verify.py --write` regenerates that receipt.

The checker uses exact rational dynamic programming at ten cutoffs and every
width 0..8192, an independent breadth census on 70 boundary/large-width cases,
30 exact 1000th-power boundaries, and all 584 rank/residue inequalities.
It checks the full-volume cancellation and exact stock powers at three
integer Gamma calibrations. The giant historical root is checked by a single
maximum path and independent inverse thresholds, without constructing its
bank, row count or full tree.

The source probe extracts the unchanged `Machine.node` and `prepare_child`
methods from authenticated bytes and runs them over exact integer descriptor
operations. It checks cutoff equality, no repeated post-remainder test,
child width/rows, unchanged global d and the complete spectator rectangle.
Its Tape/Count primitives are explicitly test interpreters: this is **not**
physical payload execution or an audit of primitive implementations. Executed
source mutations change equality, global-root forwarding, rows and spectator
tails; arithmetic discriminators cover a frozen cutoff, a repeated test and
an insufficient affine shift. One-short stock is rejected on every tested
nonterminal maximum path, and a row-count size bound is distinguished from
exact divisibility. Dropping rank 48 underestimates the tested tree depth.
Receipt controls reject duplicate keys and boolean/float substitutions for
integer fields.

The finite checks corroborate the written universal proof. They do not
numerically certify a new moment root or rerun #4753's literal-word census.
The existing root bracket is cited only for orientation. No full supplier,
selected cold replay, Lean, Docker, native payload, hosted CI or independent
human review is claimed.

Resource limits: fixed ten-cutoff arrays of 8193 entries, breadth width at most
65536, at most 4096 states/64 levels per census, and a 40000-step maximum-path
cap. The largest checked root has fewer than 21000 bits. No proof-relevant
subprocess or third-party package is used. Source pins cover every external
input; package-local files are the remaining execution closure.

## Scope and coordination

Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7,
card `joint-query-controller`, refined scope in [TASK.json](TASK.json).
The [claim is in Discussion #4744](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19173694),
following [#4865's released result](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133932).
[SOURCES.json](SOURCES.json) freezes current-base bytes and the historical
provenance. This is the original backend retained by #4166/#4753, not a new
analysis of the currently selected #5413 supplier.

No family expansion is justified by this result. The exact current-bank
parking term is only one removed expense. Candidate-only work, other parked
roles, restores, all retained later calls and finite control remain charged
or explicitly unresolved. Root-dependent bounds alone cannot decide the
complete D* versus B* inequality.

## Open next questions

1. Can the exact depth replace the conservative RootPlan stock exponent?
   First bind padding, root-prefix geometry and every consumer of the original
   depth to one admitted root family. The arithmetic divisibility result does
   not check those contracts, and no stock replacement is installed here.
2. What bounds every candidate-only positive interval in the nonterminal
   D* versus B* comparison? Start from the actual unmatched Compact/native
   interval and its full geometry in the #4744 handoff. The missing upper
   invoice remains the decision blocker; another descendant census is not
   sufficient. See the structured obligations in TASK.json.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Nick Petalas's #4865 (`8f8f518bd1a40baa30434ab18e86fd851d122b28`) supplies
the weighted-leaf identity, two potential functions, sharp affine shift and
fixed-cutoff exponent law. Brian/JoyboyBrian's #4753
(`44e2c79344e0090d4e829e0dde4f533d8d0273ec`) supplies the complete histogram,
global cutoff, fresh-row/full-bank interpretation and physical parking floor.
Chris R/Clear1nsight's #4166/#4167/#4172/#4177 and recursive-binding work
supply the installed caller and comparison boundaries. Jose Manuel supplies
the original physical machinery; ywz65, Sagar Thakrar, Tekalign, Ali Romman,
Arham Tahir and the retained source notices keep their predecessor credit.

The new contribution is the cutoff-uniform theorem, changing-root consequence,
exact selected-tree stock-depth characterization and source-bound checks.
No literature-priority claim is made for finite-tree potentials or monotone
path arguments. Apache-2.0. Substantial AI assistance covers derivation,
implementation, checking and writing; no independent human or formal-kernel
acceptance is asserted.
