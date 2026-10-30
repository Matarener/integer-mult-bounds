# A 6600-call seven-source full ternary connector

The unsigned dirty connector with seven immutable sources and all 2186
nonzero coefficient rows over F3 has a **6600-call construction**, improving
[#4256](https://github.com/CrocSwap/integer-mult-bounds/pull/4256)'s upper
bound of 6603 by three complete calls. This answers its open question 2 with
a small improvement. The claim type is a **finite construction certificate**,
with the prefix identity explaining why the certified word works in every
compatible dimension. No exact optimum, new kappa or supplier admission is
claimed. The cited lower bound from
[#4244](https://github.com/CrocSwap/integer-mult-bounds/pull/4244) remains
6588, so the current cited interval is 6588 <= OPT_3(7) <= 6600.

## Exact interface

For each j = 0..6, x_j is immutable. The connector z and all distinct outputs
y_v are arbitrarily dirty. For every nonzero v in F3^7 the required action is

```text
y_v += sum_j v_j A_v B_j x_j;     z and every x_j are unchanged.
```

The maps are arbitrary compatible F3-linear maps, including singular and
noncommuting maps. Only unsigned complete calls are permitted:

```text
B_j: z += B_j x_j
A_v: y_v += A_v z
```

Every call restores its private scratch and heads. Outputs are observed only
after the batch and cannot be borrowed. There are no inverses, direct A_v B_j
calls, extra connectors, frames, source mutation or free copies. The word is
independent of data and map entries. This is the full-demand interface of
Nick Petalas's #4238/#4244, building on the credited connector lineage below.
The number priced here is complete calls at unit prices. Physical costs that
are not part of those complete primitive implementations remain additional.

## Certificate and argument

Use this 42-event source word, with one digit denoting the source index:

```text
260536506545241601014125215430234634321306
```

Each of the seven source labels occurs six times, so the connector is
restored in characteristic three. Let q_t be the vector of source counts
modulo three before event t, for t = 0..41. The closing boundary is q_42 = 0
and duplicates q_0. The verifier enumerates all
binomial(44, 3) = 13244 boundary triples with repetition and checks

```text
{q_a + q_b + q_c : 0 <= a <= b <= c < 42} = F3^7.
```

For each nonzero row v, take its lexicographically first such triple and
place its three A_v calls at those boundaries. Several readouts at the same
boundary mean consecutive calls. Readouts do not change z, so all chosen
triples can be scheduled together, in boundary order. At boundary t,

```text
z = z_initial + sum_j (q_t)_j B_j x_j.
```

The three readouts add three copies of A_v z_initial, which vanish, and
sum_j v_j A_v B_j x_j. This uses only linearity and never interchanges A_v
and B_j. Each target receives exactly its required increment. The total is

```text
42 source calls + 3 * (3^7 - 1) readouts = 42 + 6558 = 6600.
```

The predecessor #4256 has 45 source calls and the same 6558 readouts, giving
6603. Both totals and the shared row/readout counts are checked numerically
by the arithmetic above. No predecessor census or theorem is reverified.

The source path was found by a bounded swap search starting with six uses of
every source. Search stopped at the first covering path. Discovery is not
part of the certificate: the explicit word and exhaustive triple check are
sufficient, and no search-failure or optimality claim is made.

## Evidence and reproduction

The standard-library verifier writes no files and imports no predecessor
code. It checks all 2187 rows including zero using both packed base-three
arithmetic and a separately written tuple computation. It then emits and
replays all 6600 calls using a generic coefficient ledger. That ledger tracks
incoming dirt and each B_j x_j separately, with A_v acting on the left.

Eight dense executions use dimensions 1..4, two fixtures per dimension, dirty
connectors and outputs, and explicit singular noncommuting maps in dimensions
at least two. Six mutations must fail: a dropped source call, a dropped
readout, a misrouted output, relabelled source calls, an appended source call,
and execution in characteristic six. The last control detects the unpaid
assumption that three readouts always cancel incoming dirt.

From the repository root, with CPython 3.12:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f3-ternary-seven-source/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/f3-ternary-seven-source/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f3-ternary-seven-source
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f3-ternary-seven-source --check-source-history
```

Expected marker: `PASS_F3_TERNARY_SEVEN_SOURCE`, with `calls=6600`,
`rows=2186`, `source_calls=42`, `dense_cases=8` and `rejected_controls=6`.
The generated stdout receipt binds the counts to SHA256 hashes of all five
package files. No hand-written receipt or generated replay output is stored.
[SOURCES.json](SOURCES.json) pins historical provenance at the public base.
The pending predecessors are citations rather than executable dependencies.

The code is nonrecursive, and every loop is bounded by fixed certificate
sizes, at most 64 source events, 2186 rows and dense dimension four. Each
function is shorter than 60 physical lines. Python-managed allocation is an
explicit Power of Ten deviation: dynamic objects are required by the runtime;
live verification storage is bounded by these fixed domains. There is no
unbounded input, background process or generated file. Warnings are errors
in both registered modes; checks use explicit exceptions and remain enabled
under optimization.

## Limits and family decision

This finite certificate supplies an upper bound. It does not exclude shorter
words or improve #4256's asymptotic exponent. The interval's lower endpoint
is the cited result of #4244 and is not a new proof here. A proof-kernel build,
independent human review and the selected cold replay are unclaimed and unrun.

The call count is proved for the abstract interface. A concrete consumer for
full ternary demand is unknown. Coefficient preparation, physical dispatch,
stock, hosting, precision, tape costs and complete supplier admission remain
unknown. Unknown costs are not zero. No selected source, frontier, shared
code or predecessor package changes.

The catalogue card asks for an alphabet extension. This is explicitly a
changed scope: the alphabet is retained and a full-demand finite upper bound
is improved. The family decision is to finish this small result and stop.
There is no downstream implementation campaign or claim that the complete
consumer fits a supplier budget.

## Open next questions

Structured questions are in [TASK.json](TASK.json).

1. Is the cited lower bound 6588 attained? Start with a restored 30-event
   source path covering all ternary rows by triples, or a word that trades
   source calls for extra readouts. An unsuccessful search is not exclusion.
2. Can the 42-event path yield a smaller leading constant in an all-n
   construction? A lifting argument must preserve all triple decompositions
   and charge every source event, rather than merely multiplying palette
   sizes. No such lifting is supplied here.
3. Does a concrete caller need every ternary row? Identify its complete maps,
   dirty-state contract and physical invoice before extending this family.

## Credit

This contribution was produced by Nick Petalas. Nick Petalas's #4256 posed
the seven-source upper-bound question and supplied the 6603-call torus-block
baseline; #4238/#4244 introduced full ternary demand and its cited lower
bounds. Credit #4231 for the unsigned ring interface, Riquelme Soares's
#4189 for the unsigned F3 predecessor, Ross Richardson's #943/#934 for the
prefix-connector and Gray-block lineage, conorholds's #2208 for block palettes
and all-word counting in different alphabets, and ywz65 for the five-source
contract map. No priority is claimed for elementary prefix sums or dirty
cancellation. Predecessor credit is unchanged. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.
