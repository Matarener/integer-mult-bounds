# Exact weighted scratch for a five-node clean chain

This package proves a closed form for a reversible dependency chain with
arbitrary positive real node widths. The claim is a scoped mathematical proof
with exact finite corroboration. It is a side result about clean scratch
scheduling. It supplies no selected stock coefficient, physical implementation
or new kappa.

Let nodes 1 through 5 form a path. Node 1 has no parent; node i has parent i-1.
A move computes an absent node or erases a present node, and its parent must be
present for either move. External inputs remain available outside the scratch
count. Begin empty and end with exactly node 5. The scratch usage of a state S
is the sum of its positive widths w_i. Arbitrarily many recomputations are
allowed, provided the schedule is finite.

The exact minimum peak scratch is

```text
C(w) = w5 + max(w1+w2, w3+w4, w2+w3+min(w1,w4)).
```

Thus one of two fixed schedules is optimal for every width tuple. If w1<w4,
use the first schedule below; otherwise use the second. At equality either
works. This is a space optimum. No minimum operation-count claim is made.

## Proof of the lower bound

Take any successful finite schedule. Consider its last computation of node 5.
The suffix starts with nodes 4 and 5 present, and node 5 remains present
throughout. Node 4 must eventually be erased. At its first erasure in this
suffix, nodes 3, 4 and 5 are present. Every successful schedule therefore has
peak at least w3+w4+w5.

At that erasure of node 4, if node 2 is present, the schedule visits a superset
of {2,3,4,5}. If node 2 is absent, node 3 remains present just after the
erasure. Node 3 cannot be erased before node 2 has been computed. At the first
subsequent computation of node 2, its parent 1 is present and node 3 is still
present. The schedule then visits a superset of {1,2,3,5}. Consequently it must
visit at least one of these two four-node sets.

Every successful schedule also visits a superset of {1,2,5}. In the preceding
case where node 2 is initially absent, this already follows from its subsequent
computation. When node 2 is present at the first erasure of node 4, it must
eventually be erased, and that erasure requires node 1 while node 5 remains
present.

Positivity of the widths turns these mandatory sets into the lower bound

```text
max(w1+w2+w5, w3+w4+w5,
    min(w1+w2+w3+w5, w2+w3+w4+w5)) = C(w).
```

The argument uses the suffix after the final computation of node 5. It covers
schedules that compute and erase node 5 earlier, extra visits to any state, and
arbitrary recomputation of the other nodes.

## Two attaining schedules

A positive integer denotes computation and a negative integer denotes erasure.
Every displayed move has its parent present. All other states are subsets of
one of the two maximal states listed for that schedule.

```text
Via node 3, 13 moves:
  1, 2, 3, -2, -1, 4, 5, -4, 1, 2, -3, -2, -1
  maximal states: {1,2,3,5}, {3,4,5}
  peak A = w5 + max(w1+w2+w3, w3+w4)

Via node 2, 11 moves:
  1, 2, -1, 3, 4, 5, -4, -3, 1, -2, -1
  maximal states: {1,2,5}, {2,3,4,5}
  peak B = w5 + max(w1+w2, w2+w3+w4)
```

If w1<=w4, the four-node sum for A is the smaller one, and
w1+w2<=w1+w2+w3. Hence A=C(w). If w4<=w1, the four-node sum for B is the smaller
one, and w3+w4<=w2+w3+w4. Hence B=C(w). This attains the lower bound for every
positive real width tuple. For unit widths the optimum is four. Widths
(1,1,1,10,1) favor the first schedule, and (10,1,1,1,1) favor the second;
their respective peak charges are 12 versus 13.

## Reproduce and interpret the evidence

From the repository root, use the actual CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/weighted-five-node-chain/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/weighted-five-node-chain/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/weighted-five-node-chain
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/weighted-five-node-chain --check-source-history
```

The verifier builds every legal edge on all 32 states, independently of the two
supplied schedules. For every one of the 16,807 integer tuples in {1,...,7}^5,
a bottleneck shortest-path oracle agrees with C(w), a separate set-based
schedule replay attains it, and a capacity-bounded reachability check rejects
every strictly smaller capacity. Three width-independent separating-state
checks corroborate the proof's mandatory-set argument.

Controls reject nine invalid width inputs and seven invalid schedules. They
also distinguish merely visiting node 5, which needs three unit pebbles, from
the clean endpoint, which needs four. Weighted controls distinguish both
attaining branches, and the integer-width limit is exercised. All checks remain
enabled under optimized Python. The bounded numeric interface accepts integer
widths in 1..10^12. The written proof establishes the real-width theorem.

Standard output is a generated JSON receipt with the interpreter version,
counts, separating-state components and SHA256 hashes of every package file.
Use `--receipt /absolute/scratch/path/receipt.json` to save it outside the
package. Direct verification also works without Git or repository imports.
SOURCES.json pins only catalogue and selected-record provenance. No pending
predecessor source is needed to run this verifier.

## Scope, predecessor and credit

The operation contract is the pure reversible-pebble model in Ali Romman's
[PR #5780](https://github.com/CrocSwap/integer-mult-bounds/pull/5780), head
`0ed431c52085852999a5817e80b508c1b3c63f75`. Its
[model guide](https://github.com/aliromman/integer-mult-bounds/blob/0ed431c52085852999a5817e80b508c1b3c63f75/docs/research/reversible-pebble-schedules.md)
poses source-DAG and budget applications. That work supplies an exact bounded
planner for a supplied numerical instance. This contribution gives a universal
five-width threshold and two attaining schedules. Its verifier imports no
predecessor code and does not replay the predecessor's examples or tests.
Classical reversible pebbling retains its original credit.

This changes the `selected-stock-envelope` card to a small analytical side
result about a declared DAG. It does not bind that DAG to the selected producer.
A clean pebble represents stored pure data. It is not an arbitrary productive
dirty helper. Scratch charges exclude external inputs and the implementation
of compute/erase operations. Native legality, precision, physical movement,
dirty restoration, caller charges and all five framework assumptions remain
separate. No Lean, formal proof kernel, native replay, selected cold replay or
full multiplication theorem is claimed.

The formula, proof and finite corroboration were produced by Nick Petalas.
New material is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

- Extract an actual five-node pure dependency chain from a supplier, with legal
  compute and erase routines. Insert its widths into the formula and price the
  selected schedule's full operations. Native and dirty-state contracts are the
  blockers; the formula alone does not reduce selected stock.
- Determine the minimum operation charge at the optimal scratch capacity when
  computation and erasure have different prices. Begin with the same 32-state
  graph and retain both schedules as upper bounds. This package optimizes space
  only and does not claim either schedule minimizes those charges.

## Verifier bounds

The graph has 32 vertices and 96 directed edges. Each reachability queue removes
at most 32 distinct states. Each minimax run has at most 97 heap removals, since
each directed edge can relax only after its source is settled. The width sweep
has exactly 7^5 iterations. Supplied schedule length is capped at 31. Each
function is under 60 physical lines. Warning-strict ordinary/optimized replay
and source compilation provide the available Python diagnostics.

Python's managed runtime dynamically allocates objects, so Power of Ten rule 3
requires a deviation. The deviation is confined to this terminating verifier:
the graph, all queues and all state tables have the preceding fixed bounds,
widths are at most 10^12, and each tuple is released before the next one. The
compensating checks are the complete sweep and explicit exhaustion guards.
A fixed-memory implementation would be needed if this were reused inside a
runtime with allocation restrictions.

The failure-control helper uses indirect calls to exactly two local functions,
`capacity` and `replay`. This is a rule 9 deviation confined to the sixteen
invalid-input controls. Both call targets are explicit and their exceptions
are checked. Direct checks would replace this helper if either API changed.
