# Exact rational query cost for cubic-reader repair

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Scoped proof with exact finite corroboration. No new kappa.** For every
integer r>=2, retain r children `y += a^3; a += b` and defer their source
restorations. The minimum appended signed cube-query count over rational
source linear forms is exactly two if

```
(2r^2-2r-1)/12 is a rational square,
```

and exactly three otherwise. Over the reals it is always two. Thus rational
source frames impose a cost invisible in the real relaxation. [PROOF.md](PROOF.md)
derives the defect, proves necessity by coefficient comparison, constructs
attaining schedules and includes every source restoration.

The first discriminator is r=3, whose criterion value is 11/12. Its rational
repair needs three queries. At r=14 the value is 121/4, and the optimal repair
from the actual final source `a_entry+14*b` is

```
a -= 4*b
y -= (91/11)*a^3
a -= 11*b
y += (91/11)*a^3
a += b
```

Every source and output starts arbitrary; b stays unchanged. Original child
calls remain intact. No entry snapshot or clean scratch is assumed. The
fourteen-child program saves eleven source-shift events and adds two cube
queries. Its complete backend tariff still includes the displayed nonunit
coefficients, private restoration, source access and physical implementation.
This is not a claim that the resulting program is cheaper.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cubic-reader-rational-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/cubic-reader-rational-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cubic-reader-rational-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cubic-reader-rational-repair --check-source-history
```

Replace the absolute interpreter path with a local CPython 3.12 executable on
another machine. The direct success marker is
`PASS_CUBIC_READER_RATIONAL_REPAIR`, in a generated JSON receipt bound to the
SHA256 hashes of all six package files. No receipt is hand-written and the
verifier writes nothing. Both registered commands have a 120-second limit.

[verify.py](verify.py) checks eager, repaired and inverse maps by full cubic
polynomial convolution, rather than relying on coordinate-basis inputs. It
also executes dirty integer and rational triples, scans the square criterion
through r=10,000, and compares both directions of the two-cube coefficient
equations on a fixed rational slope set. The scan lists the exact two-query
arities in its bounded domain. The all-r lower bound rests on the written
proof, not extrapolation from that scan. Mutation controls omit restoration,
omit or reverse the last cube correction, and reverse chronology; separate
controls check the arithmetic boundary and the failure of basis-only tests.

## Provenance and limits

This changes the `joint-query-controller` card to a self-contained nonlinear
interface side result. Its connection is the cost of preserving original
recursive calls while repairing their shared source at a later boundary.
No current supplier with these indivisible cubic readers is identified.
The positive-control command `scripts/research_selected_baseline.py` passed
with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. That is orientation, not a
scientific replay. At canonical base
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8, the selected
record resolves to PR6030, kappa .003125804. Older priority prose still names
PR5599; this package follows the selected record and changes neither.

Credit Sricharan Vagvala / theon199's [PR #1532](https://github.com/CrocSwap/integer-mult-bounds/pull/1532)
for the quadratic fixed-reader/paid-repair interface and its square-query
floor, Adam Gall / PR1205 for linear observation, and Hanson Sun / PR1246 for
paid linear repair. Their computations are cited premises, not rechecked
deliverables. Classical binary-form power decompositions retain their credit,
including Carlini, Catalisano and Geramita's
[Waring-rank work](https://arxiv.org/abs/1110.0745). No general Waring-rank
theorem or literature-priority claim is made. The new result is the exact
arithmetic-sensitive cubic interface criterion and its restoring schedules.

[SOURCES.json](SOURCES.json) pins the predecessor README, task card and selected
record as historical provenance. There are no external scientific runtime
inputs and no predecessor program is imported. Live PRs, current handoffs,
local reservations, recent account work and merged README/PR searches were
checked. The overlap cache's sparse local-note inventory is incomplete, so
absence of a match is not proof of novelty. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272267)
states the same delivered mathematical scope.

The theorem excludes output feedback, altered child interiors, intermediate
observations, nonlinear source maps, approximate queries and finite fields.
Source-frame and coefficient work is paid separately from query count. No
physical native realization, precision or stock bound, all-size compiler,
complete caller invoice, selected assumption discharge, Lean build, Docker
replay or complete multiplication theorem is supplied.

The verifier has no recursion, subprocess, dynamic evaluation or input CLI.
Its arities are bounded by 10,000, full polynomial programs by r=64, and
numeric programs by r=32. States contain at most five cubic monomials; all
event lists have finite capacities derived from these bounds. Every function
is below sixty lines and checks use explicit exceptions under optimized Python.
Python managed allocation is a Power of Ten rule 3 deviation, bounded by the
fixed fixture sizes. The two callback targets used only for rejection controls
are a rule 9 deviation. Warning-strict normal and optimized replay provide the
available diagnostics; no external static analyzer or proof kernel is claimed.

## Open next questions

1. Which admissible dyadic coefficients permit the same two-query minimum?
   Rational square roots alone do not ensure that query weights and source
   shifts are dyadic. Start with the two normalized slopes and weight forced
   by the proof. The missing step is a prime-denominator classification.
2. Does an actual recursive supplier expose indivisible cubic readers for
   which the complete r=14 tariff beats eager restoration? Start by pinning
   its child return map and pricing every displayed query and source shift.
   No such admitted backend or physical coefficient implementation is supplied.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
