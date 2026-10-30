# A simple-graph obstruction for early-helper BIT controllers

No controller in the stated simple support-graph model can close its diagonal
Q/D targets. The model permits two arbitrary helper columns per call,
including writes outside that call's D support. The obstruction is the last
call: its restricted q matrix must be diagonal, which cannot contain the
required nonzero main Jordan chain. The complete kappa calculation does not
improve.

Read [the proof](PROOF.md), [exact verification result](RESULT.json), and
[positive control](CONTROL.json). The publication base is
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. The package has no executable
source dependency outside its own directory. [SOURCES.json](SOURCES.json)
pins the task catalogue and selected record as historical provenance only.

## Exact scope

Each call has a coordinate rank-four D support and a q coefficient R, with
q squared zero. The two main directions obey Ru=0 and Rw=u with u nonzero.
The two helper columns are arbitrary. Columns outside the support are zero;
rows outside it can be nonzero. Every field belongs to one or two calls, and
two call supports intersect in at most one field. The commuting D symbols
are formally independent. The target is diagonal, with either QD or D-only
on each field. There are no paid thin calls.

The proof covers any finite number of calls in this class. It does not cover
parallel edges, more than two owners per field, non-coordinate supports,
dependent D symbols, or another native main block. A failed solver search is
not used as the proof.

The positive control uses two calls and four parallel edges. It satisfies the
main chains and the complete formal endpoint. Its declared complete recursive
invoice has a rank deficit of 126, so it supplies no kappa gain. It also shows
why the simple-graph hypothesis must not be removed.

## Preserved solver evidence

The [solver manifest](solver-evidence/MANIFEST.json) pins 80 recorded outcomes.
K4 and K4 minus one edge are UNSAT in each of their 24 orders. Three further
parallel-edge tests are UNSAT: a two-call double edge in both orders, a
three-call doubled path in all six orders, and a four-call (2,1,2) path in all
24 orders. These last 32 cases are finite solver-dependent evidence. There
is no all-parallel-graph theorem or retained solver proof certificate.

The exact solver code is [solver_search.py](solver_search.py). The publication
work did not repeat these failed discovery searches. Their solver version is
`z3-solver==5.3.1.0`. Solver times are historical measurements and can change.

## Reproduce the mandatory checks

Use Python 3.12. No third-party package is needed.

```sh
python3 -B research/bit-simple-graph-obstruction/verify.py
python3 -O -B research/bit-simple-graph-obstruction/verify.py
python3 -B scripts/research_package.py --package research/bit-simple-graph-obstruction --check-only
python3 -B scripts/research_package.py --package research/bit-simple-graph-obstruction
```

Expected direct output:

```text
PASS_BIT_SIMPLE_GRAPH_OBSTRUCTION fixtures=48 diagonal_cases=3840 control=PASS solver_run=false new_kappa=false
```

The verifier checks the last-call coefficient fixtures, all diagonal chain
cases, and a literal exact group-ring product for the positive control. It
also checks the native role bases, helper-column updates, and complete target
debit. It rejects a changed q coefficient, a missing target Q, a zero main
chain, and application of the simple-graph lemma to parallel edges. Its check
of the frozen solver receipts is an integrity check only.

The direct verifier works in the committed export without Git. The registered
metadata command uses Git for provenance. Optional solver replay is separate:

```sh
python3 -m pip install -r research/bit-simple-graph-obstruction/requirements-solver.txt
python3 research/bit-simple-graph-obstruction/solver_search.py --suite simple --all-orders --out /tmp/bit-graph-simple.json
python3 research/bit-simple-graph-obstruction/solver_search.py --suite parallel --all-orders --out /tmp/bit-graph-parallel.json
python3 research/bit-simple-graph-obstruction/solver_search.py --suite control --out /tmp/bit-graph-control.json
```

A different satisfying control can be returned by the solver. The mandatory
verifier checks the retained control directly, without invoking Z3.

## Open next questions

The [task record](TASK.json) asks whether a caller can change an essential
support hypothesis and still close at a favorable complete bill. Start with
one literal word and all helper target debits. No funded candidate outside
the theorem's scope is supplied. A larger graph scan without such a changed
contract is not a next step justified by this package.

## Credit

The controller model is motivated by the forward BIT early-query interface
and the entrance method of
[PR #5388](https://github.com/CrocSwap/integer-mult-bounds/pull/5388), whose
[pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/568717635d8d11175a80024c9c596e16f54b1ea4/research/native-helper-query-bank/PROOF.md)
is conceptual credit, not an executable dependency. The declared arithmetic
control uses the retained
[PR #589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) and
[PR #555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) profile in
[the pinned BIT reconstruction](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/kappa-rebuild/bit/README.md).
Its [source notice](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/e8-bit-p111-tuned/NOTICE.md)
credits eumemic with substantial Anthropic Claude assistance and retains the
earlier contributors.

The parallel controller researcher identified the complementary two-FULL
comparison and a degree-two precursor. This last-call proof, the solver
model, exact checker, and package have substantial OpenAI Codex assistance.
New files are Apache-2.0. This is author-side evidence, not an independent
human review or supplier admission.
