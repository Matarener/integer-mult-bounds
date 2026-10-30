# Query Gram cuts for complete caller words

This package gives two necessary cuts for a changed global caller. They bound
both the number of independent outputs that can use one stage axis and the
number that must share two axes. The proof allows changed paid inputs and
arbitrary constant binary bases throughout the word. No earlier caller input
is held fixed. **No new kappa is claimed.**

The cuts turn two promising price relaxations into scoped obstructions:

| Caller family | Proven consequence for both pinned P104 bills |
| --- | --- |
| Shortest query count L=n+1, n>=4, arbitrary overlapping commuting involutive axis sets, full/thin calls, no idles | Complete target-minus-paid moment <= -8 for every normalized nondecreasing concave tariff; the bound is sharp |
| L=n+2, all full, separate ports, each disjoint eight-axis stage block used twice, no idles | Full stage capacity is impossible for n>=6; no caller with 2<=n<=50 passes a power-tariff saving >= .003 |
| Fourteen calls on twelve fields in the second family | Complete moment <= -368 for every such concave tariff; the optimistic raw crossing near .003393385 is not realizable |

The shortest-family statement has no upper size limit. The longer-family
capacity statement also has no upper size limit; its complete price rejection
is bounded as stated. These are written proofs with exact finite controls,
not extrapolations from search failures.

Section 9 also proves the shortest result for arbitrary scalar mixing
across all 104 ports, with total main dimension N=104n and L=n+1 calls.
Its block-simplex proof derives the required Gram matrix. The longer
paired-stage price statement keeps ports separate. The written arguments
extend to fields of characteristic two; the executable controls use F2.

## What the cuts measure

Normalize the central-query tangent terms as R_i=u_i v_i, with sum R_i=I.
The query Gram matrix K has entries v_i u_j. If axis x occurs in call set S,
has h_x charged one-field idle occurrences, and reaches r_x main jobs, then

```text
r_x <= 2|S| + h_x - rank K[S,S].
```

For two axes, put delta_x=2|S|+h_x-r_x and define delta_y in the same way.
Their target sets must have at least

```text
rank K[S,T] - delta_x - delta_y
```

common main jobs. At the shortest count the first cut becomes
`r_x <= |S|+(|S| mod 2)+h_x`. At one additional query, separate axis tests
can pass while their required intersections are impossible. Sections 2, 7
and 8 of [PROOF.md](PROOF.md) give the general cuts and this distinction.

There is also an inventory design condition. Write the net local rank mass
as `2*b*v+d`, where v is the port count and b is the transverse rank. If the
paid-minus-helper hinge sums remain nonpositive, a shortest no-idle caller
needs `d<v/2` before it can have a positive concave moment. Both pinned P104
bills have `d=56`, while `v/2=52`. Section 5 gives the proof. Satisfying this
necessary threshold would not by itself supply a caller.

## Use the filter

[cuts.py](cuts.py) accepts a JSON query frame and proposed target sets. Vectors
are binary integers. `u[i]` and `v[i]` describe the rank-one query R_i. Each
axis lists its call indices, target indices and optional `idle_terms`.
An axis can represent one whole disjoint stage block when all its axes have
the same occurrences and target set.

```sh
python3 research/shortest-controller-stage-capacity/cuts.py research/shortest-controller-stage-capacity/examples/six-query-positive.json
python3 research/shortest-controller-stage-capacity/cuts.py research/shortest-controller-stage-capacity/examples/fourteen-query-intersection-rejected.json
```

The first command returns `PASS_NECESSARY_CUTS_ONLY` and exit code zero.
The second returns `REJECT_NECESSARY_CUT` and exit code one. It passes every
separate capacity test but fails the intersection test. The proof excludes
all target assignments with full capacity in that family, not just this file.

A passing filter does not supply compatible native projectors, an operator
endpoint, paid scalar bases, helpers, ordinary maps or a compiler budget.
The retained six-query example is an actual binary operator word; it is a
positive control for the cut, and its complete P104 bill still loses.

## Evidence and reproduction

[RESULT.json](RESULT.json) records the exact checks. Two literal interpreters
agree on the five-query sharp word and the six-query longer control. The
replay checks 4,352 two/three-projector combinations, simplex identities
through 64 fields, the AB/BA kernel identity, intersection inequalities,
target-incidence maxima, complete helper/paid histograms and exact integer
root intervals. A deleted query, an invalid query frame, a non-idempotent
sum and the false extension of the shortest cut are discriminating controls.

```sh
python3.12 -B scripts/research_package.py --package research/shortest-controller-stage-capacity
python3.12 -I -O -B research/shortest-controller-stage-capacity/verify.py
```

Expected marker: `PASS_CALLER_STAGE_CAPACITY_CUTS`. The replay needs only
Python 3.12 and the standard library. It reads and compares the committed
receipt. `--write-result` is an explicit regeneration option. The direct
verifier also works in a source export containing the five declared inputs.
It authenticates those bytes before it loads the credited interpreter.

The local inventories are original P104 and PR5599 at
`09dd0965711ca7eeb169057a420abab1c9052137`. They are exact historical inputs,
not a claim about the strongest pending frontier. Both have complete net
rank mass 1720. Source pins and hashes are in [SOURCES.json](SOURCES.json).
Native and outer admission of those sources is inherited, not rerun here.
The negative necessary moment leaves no compiler or ordinary-work saving
to establish. [VALIDATION.md](VALIDATION.md) records the checks actually run.

The initial advancing-operator and repeated-stage searches are saved in
[discovery/README.md](discovery/README.md). Solver `unknown` stays unknown;
solver `unsat` is not a separately checked proof certificate. Those searches
are not dependencies of the theorem replay.

## Scope and coordination

The model is binary with independent commuting involutive coordinate axes.
Helpers are separate independent inputs. The principal obstructions permit
no idle maps. The generic cuts allow explicitly counted one-field idle
terms, but their concave cost needs a separate bill. Arbitrary complex or
even-denominator codes, noncommuting stages, unbounded-order advancing maps,
joint main/helper codes and different target contracts are outside the proof.

This is a user-directed change from the QQ16-specific card. It does not
complete that card's installed-protocol question. [TASK.json](TASK.json)
preserves the original card and states the changed scope. Canonical main was
refreshed from `5e0052ca0aa3036a3afa8b0438927377c8d97d53` to
`d7633ce230196a1d5d061347de7a0fd8be512ed6`; the frozen source pins remain.
Priorities and the selected record did not change at that checkpoint.
The final refresh to `6cf7a683f447b9f1e2333791907fd92be5009a63` also found
no change in those authorities. The source pins stay fixed.
[Discussion5593](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593)
is the canonical investigation. Local contact, helper-basis and G20 claims
are separate. No selected-frontier change or scientific acceptance is implied.

## Open next questions

- Extend the intersection bound to a quantitative rank loss that grows with
  caller size. Start from the rank-two complement and allow unsaturated
  stage classes and permit coupled ports. This could close more of the
  longer-caller domain. The separate-port proof only forces one lost
  stage occurrence; its complete size bound does not cover coupled ports.
- Search a changed caller with more queries, mixed calls or partially
  overlapping axis blocks. Apply both cuts before a full polynomial search,
  then verify the whole endpoint and complete bill. The filter is necessary
  only; no such favorable word is supplied here.
- Test the advancing operator route in characteristic zero. The recorded
  rational four-field screen is negative and the six-field screen timed out.
  An infinite-order stage is outside the involutive-axis obstruction. A
  surviving word still needs native maps, helpers and complete pricing.
- Independently review the normalization, private-axis extension and joint
  incidence argument. Start with Sections 2, 4, 7 and 8 of the proof. Finite
  controls do not replace a proof audit or a formal kernel.

## Credit

Cinna Davis / 1337isnot1337 supplies the minimum-query simplex, private-stage
projector obstruction, five-query sharp word and controller lineage. The
new contribution is the rank/intersection cut, its application to coordinate
reuse, the paired-stage packing obstruction and the complete concave price
test. Elementary rank and convexity tools are standard; no claim of worldwide
priority is made for those tools.

Credit the P104 productive-helper and source-word authors, the PR5565 cascade
and PR5599 helper-split authors, Jacob Alan Sussman's productive recursion,
the native suppliers, Cao Yifan/zxv compiler and moment work, and all retained
precision and analytic sources. Source-specific notices remain unchanged.
The equality cuts in Ali Romman's PR5588 motivated this whole-word search.
Prepared for Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
