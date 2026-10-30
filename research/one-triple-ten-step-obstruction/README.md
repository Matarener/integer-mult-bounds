# A single triple cannot complete a ten-step five-source connector

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Claim type: exact finite certificate with a written model reduction.**
A restored ten-step walk on five binary sources, with exactly one triple-source
step and nine singleton steps, cannot have every mask as a difference of two
prefixes. Among walks using every source, the sharp maximum is **30 of 32
masks**. This answers Open next question 1 of unpaidmoon's
[PR #4137](https://github.com/CrocSwap/integer-mult-bounds/pull/4137).

Consequently, every covering ten-step walk containing any source step of arity
at least three has source-leaf bill **at least 122** at prices
`(1,4,10,16,28)`. Aaron Wang's pair-source word already attains bill 120.
The new lower bound is strict; attainment of 122 is unclaimed.
There is no new kappa, supplier admission or complete multiplication theorem.

## Model and scope

Use Ross Richardson's paired-readout model: five immutable sources, one
arbitrarily dirty connector, 31 distinct nonzero output masks, two readouts per
output, and connector restoration. Each source step adds a nonempty subset of
sources. Each step is one query, and each included source pays its own leaf
price. Triple and higher-arity calls are charged operations.

For a source word `w=(s_1,...,s_10)`, let `q_0=0` and
`q_i=q_(i-1) XOR s_i`. Restoration means `q_10=0`. The available masks are
`D(w)={q_i XOR q_j: 0<=i,j<10}`. The credited prefix criterion says that the
paired readouts implement all requested masks exactly when `D(w)=F_2^5`.
The dirty connector cancels between each pair. This criterion and its arbitrary
linear-operator interpretation are inherited, not new results.

The certificate decides the finite source-word question. It does not execute a
native array program or certify physical frames, routing, source preparation,
scratch, tape, precision, recursive charges or a complete consumer invoice.
Specialized operators, additional connectors and more than two readouts per
output are outside this contract.

## Complete reduction and finite exclusion

Every coordinate in a covering walk must occur: otherwise all differences lie
in a coordinate hyperplane. Restoration makes every incidence positive and
even. One triple and nine singletons have total incidence 12, so the five
incidences must be `(4,2,2,2,2)` up to source permutation.

Rename the four-use source as coordinate zero. Rotate the unique triple to the
last step. A rotation translates every prefix by the same vector, preserving
all differences; it does not require a free physical operation. Thus all
candidates are exhausted by fixing the final triple and permuting the nine
singleton steps with the remaining incidences.

There are two types of triple:

| Triple includes the four-use source | Triple choices | Singleton multiplicities | Words per triple | Sharp mask maximum |
| --- | ---: | --- | ---: | ---: |
| Yes | 6 | `(3,1,1,2,2)` up to the other labels | `9!/(3!2!2!)=15120` | 30 |
| No | 4 | `(4,1,1,1,2)` up to the other labels | `9!/(4!2!)=7560` | 26 |

The primary census visits all `6*15120+4*7560=120960` words and finds zero
covers. No word is pruned. A lexicographic successor visits each multiset
permutation exactly once: it increases the rightmost increasable entry and
puts the suffix in its least ordering. The factorial count checks exhaustion.

A separate implementation places each label in disjoint subsets of the nine
positions. It checks all 15,120 and 7,560 words for the canonical triples
`{0,1,2}` and `{1,2,3}`. Its mask oracle uses intersections with XOR-translated
bitsets, rather than enumerating prefix pairs. The complete coverage histograms
agree. The primary census also checks agreement within each of the two source
permutation classes. Both algorithms are retained in this package.

The maximum 30 is attained by step masks

```text
1, 8, 1, 2, 1, 16, 4, 8, 16, 7
```

with prefixes

```text
0, 1, 9, 8, 10, 11, 27, 31, 23, 7, 0.
```

The verifier computes its two missing masks and every histogram afresh.
Thus 30 is a sharp finite maximum, and complete 32-mask coverage is impossible.
Walks with an unused source have at most 16 masks, so they do not enlarge it.

## The strict source-leaf gap

For any covering restored ten-step walk, write its positive even coordinate
incidences as `c_i`. The base incidences two on every coordinate cost
`2*(1+4+10+16+28)=118`. If total incidence is at least 14, its four additional
incidences cost at least four, giving bill at least 122, even after relabeling.

A bill at most 120 therefore forces total incidence at most 12. A step of
arity at least three rules out total incidence ten. At total incidence twelve,
there are exactly two excess incidences beyond ten singleton steps. Such a
word with a step of arity at least three must have exactly one triple and nine
singletons. The finite exclusion above rules it out. This proves the 122
lower bound without asserting that any word attains it.

This uses no replay of #4137's nine-point set exclusion, length floor or old
bill comparison. Those results and Aaron Wang's positive pair construction are
cited predecessors. The new computation is the previously open ten-step
one-triple case, not an audit of those predecessors.

## Reproduction and evidence

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/one-triple-ten-step-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/one-triple-ten-step-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/one-triple-ten-step-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/one-triple-ten-step-obstruction --check-source-history
```

Replace the absolute interpreter path with another CPython 3.12 installation
elsewhere. Both registered commands have 120-second limits and retain every
check under optimization. The verifier emits
`PASS_ONE_TRIPLE_TEN_STEP_OBSTRUCTION` inside a generated JSON receipt with
package SHA256 hashes. It writes no files. Redirect logs and receipts outside
the checkout. Historical source pins are provenance; no predecessor executable
or mutable external input is used by this certificate.

Seven invalid-word controls reject wrong length, zero, Boolean and out-of-range
steps, absence of the triple, changed incidence, and multiple triples.
All ten rotations of an attaining word preserve its complete difference set.
A planted full Gray-cycle cover exercises successful 32-mask recognition in
both implementations; a repeated-prefix fixture exercises duplicate handling.
These controls test the new census, not the predecessor results.

The prescribed card command was run once as orientation and passed
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The current selected-baseline metadata control also passed. Neither supplies
new evidence for this certificate. The selected full cold replay, Lean, Docker,
production native execution and independent scientific acceptance are unrun.

## Implementation bounds

The Power of Ten scope is the two new Python files. They use structured control
flow without recursion, network access, subprocesses or dynamic evaluation.
Every word has nine singleton positions and one triple; the primary loop has an
explicit `9!` cap with exact exhaustion checks. The independent placement loops
range over subsets of nine fixed positions. Bitset indices range over 32 masks
and five coordinates. Functions fit within 60 physical lines. Invalid words
raise exceptions, and the registered warning-strict checks remain active with
optimization. No external static analyzer or repository-wide diagnostic change
is claimed.

Rule 3 deviation: CPython and its standard library allocate managed objects.
The primary census streams words and retains at most 32 histogram counters,
one best ten-step word, eleven prefixes and a 32-element difference set per
iteration. The independent census streams nine-position placements and retains
32-bit prefix/difference bitsets and at most 32 counters. The package hash scan
is capped at 16 entries. These fixed domains bound live data; fixed allocation
is not claimed. Verification exercises both enumeration paths and their exact
bounds. A fixed-capacity implementation is a follow-up only if these domains
or the runtime contract change.

## Sources and credit

Credit **unpaidmoon #4137** for the explicit open question, charged triple
extension and earlier lower bounds; **Aaron Wang** for the pair-source word
and its 72-query interface; **Ross Richardson #943** for the universal dirty
connector model and prefix-difference criterion; and **Adam Gall** for the
fixed-alphabet all-tariff work credited by the predecessors. Their source
notices and results are unchanged. The source paths and exact blobs are
historical provenance in [SOURCES.json](SOURCES.json). No broader literature
priority is claimed for permutation enumeration or the prefix argument.

Canonical base is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
[TASK.json](TASK.json) refines the connector-alphabet card to its explicit
one-triple attainment question. Live open PRs, recent account PR bodies,
handoffs, local reservations, merged-title searches and all-main distinctive
README terms were checked before reserving the question. The overlap helper's
local coverage was sparse and its remote cache was historical; live queries
supplemented it. No search proves novelty against unpublished work.

Advance claim: [handoff #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214969).

## Open next questions

1. What is the exact minimum source-leaf bill for a covering ten-step walk
   containing a step of arity at least three? The strict 122 lower bound does
   not establish attainment. Start with incidence total 14 and price the full
   source profile before a search. No witness or exclusion there is supplied.
2. Is there a short structural proof of the sharp 30-mask ceiling? It could
   replace the census. Start with the five even and five odd prefix positions,
   distinguishing whether the triple contains the four-use coordinate. A
   structural argument for the sharp maximum remains missing.

The same questions, relevance and blockers are recorded in TASK.json. No
follow-on search is part of this contribution.
