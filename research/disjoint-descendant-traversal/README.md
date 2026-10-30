# Twenty-two fewer historical disjoint-triple helper roles

This finite certificate constructs the h=22 disjoint-triple sum map with
**30,676 additions and 32,216 reversible roles**, saving 22 of each against
the 30,698-addition construction in ToikY's [PR #981](https://github.com/CrocSwap/integer-mult-bounds/pull/981).
The complete historical three-stage scalar bound falls by **1,252,204,800**.
There is no new kappa or selected-frontier change.

The new step changes a proper descendant, a domain #981 explicitly excluded.
It preserves #981's root split 11+11, root target-cardinality order
`(1,2,3,0)`, reversed root channel `(1,1)`, point order, summation trees and
first-decomposition support interning. Inside every encountered
`D_(2,2)(11)` subproblem, keep its 5+6 split but reverse the factor order
in channel `(1,1)`. Both orders have the same unshared cost 146.
Different intermediate supports change which decompositions survive global
interning and pruning. [PROOF.md](PROOF.md) gives the exact map and accounting
argument. This is an improvement to this cited historical construction;
no global circuit optimum or broader literature-priority claim is made.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/disjoint-descendant-traversal/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/disjoint-descendant-traversal/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/disjoint-descendant-traversal
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/disjoint-descendant-traversal --check-source-history
```

Other machines may replace the absolute interpreter path with their CPython
3.12 executable. The final marker is
`PASS_DISJOINT_DESCENDANT_TRAVERSAL additions=30676 roles=32216 no_new_kappa`.
Default replay writes no files. Its computed stdout receipt includes all
package and live-input SHA256 hashes, the environment and elapsed time.
There is no handwritten receipt.

The new checker reconstructs every active integer support from the literal
addition DAG, separately constructs every desired disjointness row and checks
all **2,371,600 coefficient positions**, including zeros. It independently
replays the compiled embedding and checks its source, output, freshness and
slot-alias conditions. The retained frame checker checks both physical
orientations, with 104,897 distinct nontrivial transitions. One dense integer
roundtrip uses deterministic dirty initial values in all 32,216 roles; its
universal justification is the elementary inverse in PROOF.md, not sampling.
Six rejecting controls cover a wrong output, duplicate summand, cycle,
corrupt cached support, missing paid role and aliased fanout. All mutations
are restored before a final successful map and embedding replay.

Predecessor values are cited from #981, not re-established here. Its census
and verifier are not replayed. This package constructs and checks only the
new circuit. The first strict improvement ended the search; no optimality
claim or complete negative census is attached to earlier unsuccessful probes.

## Complete historical bill

The unchanged historical contract retains the intersection-two circuit,
23 centres, joins, source access, weighted injection, all four mixers or
inverses, dirty restoration and all three tensor stages.

| Quantity | Cited #981 | New circuit |
| --- | ---: | ---: |
| Disjoint additions | 30,698 | 30,676 |
| Disjoint reversible roles | 32,238 | 32,216 |
| Total side roles | 49,332 | 49,310 |
| Mixer additions | 86,344 | 86,300 |
| Complete signed invocation steps | 410,056 | 409,880 |
| Complete three-stage scalar bound | 2,917,466,428,800 | 2,916,214,224,000 |
| W | 241,405,164,000 | 241,300,813,600 |
| s | 2,570,482,081,921,600 | 2,569,370,958,862,400 |

Here `v=1540`, `m=10648`, `L=3600088800` and `W*m-s=104350400`.
The verifier computes the new bill and the retained `E=64(W+m+1)^3` guard.
It does not calculate a new logarithmic saving or compose a supplier with
current BIT or outer budgets.

## Scope and limits

Scientific base is canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
The selected binding-only orientation passed. This is a declared change
from `complex-rank-shape-decoder` to a historical circuit side result.
The selected P104 supplier is a different construction. Improving this old
finite invoice does not discharge its compiler, ownership, all-column native,
precision/tape or analytic recovery assumptions. No selected cold replay,
full multiplication theorem, new native kernel, exact h22 residual-basis
construction, all-size compiler or physical rounded multiplier is supplied.
Independent human and formal proof-kernel review are unclaimed.

Only this package is new. [SOURCES.json](SOURCES.json) pins the imported
constructor, its executable dependency closure and the proof and comparison
sources. Frozen predecessors and their credit lines are unchanged.
[VALIDATION.md](VALIDATION.md) records local checks and implementation limits.

## Open next questions

1. Does an explicit physical caller benefit from this descendant sharing
   mechanism in a competitive current supplier? Start with one named
   disjoint-subset component and its complete boundary invoice. No such
   component or compatibility with selected P104 is established here.
2. Can one prove a bound on the benefit of changing a single proper
   descendant's factor order under first-decomposition interning? Start with
   the two 146-cost factorizations and the supports they create. This package
   certifies one example and supplies no universal sharing bound.

These questions are unreserved. TASK.json records the same questions and
remaining blockers.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
ToikY's #981 supplies the root recipe and root-traversal improvement;
Curtis Dransfield's #863 supplies the preceding tied-root construction.
Douglas R. Colkitt supplies the disjoint-subset recurrence, support interning,
reversible compiler, phase enclosure and historical signed-invocation and
stopped-recurrence accounting. Their retained notices and predecessor
attribution continue to apply. The new result is the descendant factor-order
change, its 22-role improvement and the accompanying finite certificate.
