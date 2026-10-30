# Exact tariffs for rectangular duplications of the signed obstruction

produced by Nick Petalas

This is a **scoped proof with finite corroboration**. For arbitrary nonempty
row and column groups, it determines every minimal call-count profile and the
exact positive, equal-by-sign query tariff of the replicated signed connector
target. The extra calls must cover a whole group. Repeating only the cheapest
individual operator can be insufficient. There is no new kappa or complete
multiplication theorem.

The result extends the rectangular-target direction in
[#4258](https://github.com/CrocSwap/integer-mult-bounds/pull/4258), with symmetric
sign prices. It uses Ross Richardson's canonical obstruction, martinxxx9's
integer repairs, Sagar Thakrar's ternary repairs and the characteristic transfer
of [#4233](https://github.com/CrocSwap/integer-mult-bounds/pull/4233) as predecessor
results. Their results are dependencies, rather than the subject of an audit.

## Boundary and theorem

Let X0,X1,X2 partition the source indices and Y0,Y1,Y2 partition the output
indices. All six groups are nonempty and finite. Write G for this six-group
partition and N for its total size. Set

```text
C = [[1,1,1], [1,1,-1], [1,-1,0]]
M[i,j] = C[a,b] when i is in Ya and j is in Xb.
```

The arrays xj, yi and z are distinct, initially arbitrary elements of a finite
free module over a nonzero unital ring R of characteristic c. The maps Ai and
Bj are arbitrary compatible R-linear maps. They may be singular and need not
commute. Target duplication does not identify these maps or their data.
The permitted complete calls, each charged separately, are

```text
Bj^s: z  += s Bj(xj)
Ai^s: yi += s Ai(z)             s in {-1,+1}.
```

Sources are immutable, outputs are never read, and z must restore. The final
increment of yi is sum_j M[i,j] Ai(Bj(xj)). Each call preserves every other
data role and returns private scratch and heads. Coefficient preparation,
admission, instruction storage and control remain separately chargeable.
There are no extra connectors, frame operations or combined queries.

For any operator F let pF > 0 be its complete call price, the same for both
signs. Define P(H) = sum of pF over operators F in group H, S = sum_F pF, and

```text
alpha(c) = 0  if c = 2
           1  if c = 3
           2  if c = 0 or c >= 4.
```

**Theorem.** The exact minimum query bill over all finite legal words is

```text
OPT = 2 S + alpha(c) min_{H in G} P(H).
```

More strongly, in characteristic three the six Pareto-minimal occurrence
vectors are `nF = 2 + 1[F in H]`, one for each group H. In characteristic zero
or at least four they are `nF = 2 + 2*1[F in H]`. In characteristic two there
is just the vector with every nF = 2. These statements count both signs
together. They do not classify all signed words attaining a vector.

The unit-price optimum is `2N + alpha(c) min_H |H|`. When every group has two
members, the 6x6 target therefore needs exactly 24, 26 and 28 calls in
characteristics two, three and zero or at least four, respectively.

An asymmetric group example has source group sizes 2,1,1 and output group sizes
1,1,1. Prices in that order are `(1,100,10,10,10,10,10)`. Here S = 151 and the
cheapest whole group costs 10. The characteristic-zero optimum is **322**.
Using the cheapest individual price as the surcharge would give 304, which
does not meet the transversal obstruction.

## Proof

### Restriction to a transversal

Choose one operator from each group. Set every unchosen Bj to zero and ignore
every unchosen output. Delete their calls from any purported legal word.
Chosen readouts see exactly the same connector, and deletion cannot change a
chosen source or the connector restoration equation. The remaining word is a
legal canonical C program for arbitrary maps on those six selected operators.
Thus the canonical obstruction applies to every six-group transversal.

Every operator is active because every row and column of C is nonzero.
Restoration forces the signed occurrence sum of each Bj to vanish in the
prime subring of R. Eliminating arbitrary initial z dirt forces the same for
each Ai. One occurrence cannot vanish in a nonzero unital ring. Hence every
operator occurs at least twice.

For c >= 3, if each operator in one selected transversal occurs exactly twice,
its two signs must be opposite. A source prefix coordinate then takes values
in {0,1} or {0,-1}. Each paired readout coefficient belongs to {-1,0,1}.
These three elements have distinct images in characteristic c >= 3, as they
do in characteristic zero. A correct modular paired word for C would therefore
be an integer paired word for C. Richardson's
[#944](https://github.com/CrocSwap/integer-mult-bounds/pull/944) excludes such a
word. This is the no-aliasing transfer used in #4233; zero divisors introduce
no exception to the distinctness of these prime-subring elements.

Consequently every transversal contains an operator with more than two calls.
For c = 3 that operator has at least three calls. For c = 0 or c >= 4 it has
at least four: a sum of three signs is one of -3,-1,1,3, none of which vanishes
in those characteristics. These are necessary conditions on every finite
word, without any word-length cutoff.

### The whole-group step, the new lower bound

Let E be the set of operators with more than two calls. The preceding argument
says that E meets every transversal. A subset meets every transversal of six
nonempty groups if and only if it contains one whole group. Indeed, if no
group is contained in E, choose an operator outside E in each group to get a
disjoint transversal. The reverse implication is immediate.

Therefore some entire group H consists of operators with at least
`2 + alpha(c)` calls. Every other operator has at least two. This proves
componentwise domination of one displayed vector and the claimed weighted
lower bound. Characteristic two only needs the active-operator lower bound.

### Batching attains every displayed profile

For c = 0 or c >= 4, take martinxxx9's
[#1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088) integer repair
that calls the canonical operator corresponding to H four times, and every
other canonical operator twice. It is an integer identity, so it remains valid
over every R. For c = 3, use Sagar Thakrar's
[#1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349) repair with
the chosen canonical operator called three times and the others twice.

Replace each canonical Bj call by one call, with its sign, to every source
operator in Xj. Replace each canonical Ai call by one call, with its sign,
to every output operator in Yi. Each replacement is an actual sequence of
complete calls at fixed ports. No combined query is priced as one call.
Source batches leave z with the indicated sum of independent Bj(xj) terms.
Output batches visit distinct arrays without changing z. Thus every pair of
an output and source acquires exactly C[a,b] Ai(Bj(xj)), arbitrary initial
connector dirt cancels, and z restores. This proof uses only distributivity
and additivity, so it applies to noncommuting maps over every R.

In characteristic two, batch the following canonical twelve-call word:

```text
B0+ B1+ B2+ A0+ A1+ B2- A2+ B1- B0- A0- A1- A2-
```

Its integer target is `[[1,1,1],[1,1,1],[1,1,0]]`, which equals C modulo two.
It calls every operator twice. These constructions attain every displayed
profile. The six profiles are pairwise incomparable because the groups are
disjoint and nonempty. Componentwise domination now proves the Pareto claim
and completes the exact tariff proof.

## Finite evidence and reproduction

From the repository root, with the standard library of CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-duplication-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-duplication-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-duplication-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-duplication-tariff --check-source-history
```

Any CPython 3.12 interpreter can replace the local interpreter path. The direct
checks print `PASS_SIGNED_DUPLICATION_TARIFF` with:

- 30,618 construction cases, all six forced profiles for all 729 group-size
  vectors in {1,2,3}^6, in characteristics 0,2,3,4,5,8,12. Exact formal
  coefficients check every demanded pair, connector restoration and dirt.
- 2,240 optimal priced words, using uniform prices and seeded positive rational
  prices for all 64 group-size vectors in {1,2}^6 in those characteristics.
- 46,656 exceptional-operator subsets over the same 64 shapes, with all 729
  shape-specific transversals. Direct subset enumeration checks the cover
  equivalence, all minimal covers and the weighted minimum independently of
  the closed group formula.
- 504 literal two-coordinate dirty-array executions and inverse round trips,
  including independent noncommuting Ai,Bj matrices and four shapes of up to
  15 operators. Sources and connector restore exactly.
- 672 negative controls, consisting of 665 single-query deletions, the 304
  underbilling example and six invalid shape/price/characteristic inputs.

These checks test the new replication and cover extension. They do not replay
the predecessor canonical censuses. The two predecessor certificates are live
SHA-256-pinned inputs, used for their six anchors each. No predecessor
executable is imported. The unmerged #4233 theorem is cited at
`d56d43c726dddc37a97a5dabf9d13ef861394133`; no pending Git object or executable
is needed by replay. Its elementary no-aliasing argument is given above, and
#944 remains the credited finite obstruction dependency.

Every run generates a receipt bound to all package files and both live inputs.
Use `--receipt /path/outside/receipt.json` to save it outside the checkout.
No receipt is handwritten or committed. `VERIFY.json` registers normal and
optimized checks with warnings as errors and a 60-second limit per command.

## Obligation ledger and limits

The arbitrary-group-size theorem is a written scoped proof using the stated
predecessor lemmas. The finite domains corroborate it; they do not enumerate
all rings, prices or group sizes. Independent human and formal proof-kernel
review are unclaimed.

The exact query lower bound is proved, and a literal abstract-call word
constructively attains it. Fixed complete prices are assumptions of the query
model. A physical caller with this demand, instantiated complete prices,
preparation, routing, layout, precision, stock, control and supplier admission
are unknown. Unknown costs are not zero. There is no consumer bill or claimed
recursive gain for downstream cleanup to preserve. This is a local interface
result, with no further construction campaign undertaken. No selected cold
replay, Lean build or outer multiplication transfer was run.

The verifier is deliberately finite: group sizes are at most four, with at
most 24 operators, 96 queries per word and 144 pair coefficients. Its exhaustive
subset domain is at most 4096 subsets per shape. It has no recursion,
subprocess, dynamic code generation or network calls. Python requires managed
allocation, a deviation from Power of Ten rule 3. These fixed capacities bound
live mathematical state; the standard interpreter and JSON parser still
allocate internally. External certificate bytes come from the two hash-pinned
committed inputs. Each read is capped at 2 MiB and each metadata inventory at
16 rows. Revisit these limits before increasing evidence domains.
All functions stay under 60 lines, explicit exceptions survive optimized
Python, and warnings are errors. No repository-wide analysis configuration
is changed.

## Open next questions

1. What is the exact tariff if the two signs of each operator have different
   prices within a duplicated group? This matters because a common batched
   chronology may not attain the individually cheapest mixture of unary and
   four-call profiles. Start with one duplicated canonical operator and mixed
   sign preferences, retaining all other operators twice. Common-chronology
   attainment and a matching lower bound are open; #4241 alone does not settle
   them.
2. Which genuinely new 3x4 patterns have an exact tariff beyond row or column
   replication? Such patterns can have overlapping canonical obstructions
   without the complete-transversal structure used here. Start with one
   specified fourth column, derive its obstruction-cover lower bound and seek
   matching literal words. A general rectangular classification and a real
   physical caller are absent.

## Credit and provenance

Ross Richardson's #944 supplies the canonical signed obstruction, interface
and paired-path reduction. martinxxx9's #1088 supplies the six integer repairs.
Sagar Thakrar's #1349 supplies the six ternary repairs. Nick Petalas's #4233
supplies the characteristic transfer and #4258 identifies the rectangular
extension direction. This contribution supplies the transversal whole-group
lower bound, replicated attaining words and exact Pareto/tariff theorem for
arbitrary multiplicities. It claims no priority for modular cancellation or
standard batching.

The lineage includes Richardson's #934/#943 binary connectors, CubeJerry's
#889 signed fanout contract and Chafik Boukhalfa's #628 dirty commutator and
literal inverse convention. Their predecessor credit is retained. Frozen
packages and the selected record are unchanged. Source README and notice
provenance is pinned in [SOURCES.json](SOURCES.json).

Base `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7.
[Claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19085440).
Structured scope and next questions are in [TASK.json](TASK.json). Apache-2.0.
