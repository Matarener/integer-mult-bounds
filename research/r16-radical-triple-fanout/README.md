# Exact tariff for three independent radical demands

**Scoped written proof with exact finite corroboration; no new kappa.**
For three arbitrary dirty rows over the sixteen-element ring

    R16 = F2[e,h,z]/(e,h,z)^2,
    lambda = (e,h,e+h+z),

this package determines the exact cost for every six strictly positive
receiving-row prices. The price envelope has **ten indispensable linear
terms**, with matching words and a lower bound covering every finite
interleaving. The theorem extends to every commutative unital local ring
whose three demand classes in `m/m^2` are linearly independent over `R/m`.
Neither finiteness nor `m^2=0` is needed for that extension.

This answers the non-zero-sum, three-generator question explicitly left in
lee-phys [#5259](https://github.com/CrocSwap/integer-mult-bounds/pull/5259).
That predecessor's nineteen-term theorem concerns nonprincipal **zero-sum**
triples. Here the sum is z, and its cheaper two-insertion families do not
supply the requested endpoint. Ali Romman's
[#5310](https://github.com/CrocSwap/integer-mult-bounds/pull/5310)
classifies source-insertion feasibility; it does not settle this total tariff.

## Contract and theorem

Let R be a commutative local ring with `1 != 0`, maximal ideal m and residue
field `k=R/m`. Assume

    lambda_i in m,  i=0,1,2,
    [lambda_0], [lambda_1], [lambda_2] are k-linearly independent in m/m^2.

There are exactly three independent arbitrary dirty rows `a_i in R^w`,
`w >= 1`, and one disjoint preserved source `p in R^w`. A fixed finite
straight-line word must send each row to `a_i+lambda_i p` for every input.
The only gates are

    P_i(beta):   A_i <- A_i + beta p,       price mu_i > 0;
    E_ij(alpha): A_i <- A_i + alpha A_j,    price c_i > 0, i != j.

Every coefficient and ordered pair is available. Prices are finite,
stationary, coefficient-independent complete abstract prices; ADD prices
depend only on the receiving row. Zero-coefficient gates may be deleted.
There are no auxiliary rows, clearing operations, observations, adaptive
branches or free basis changes. An inverse execution has its own bill.

**Theorem.** For distinct i,j,k define

    D       = mu_0 + mu_1 + mu_2,
    T_i     = 2mu_i + 2c_j + 2c_k,
    R_ij;k  = 2mu_i + mu_j + 2c_k.

Then the exact optimum is the minimum of D, the three T terms and the six R
terms. Equivalently, writing `{i,j}={0,1,2}\{k}`,

    B_k = mu_i + mu_j + min(mu_i,mu_j) + 2c_k,
    OPT = min(D,T_0,T_1,T_2,B_0,B_1,B_2).

Each of the ten expanded terms is uniquely cheapest for some strictly
positive prices. This is a complete **price envelope**, not a claim that
these ten count vectors form the complete componentwise Pareto frontier.
The distinction matters in the two-root, two-insertion case below.

For R16, `m=(e,h,z)`, `m^2=0`, and `k=F2`. The coefficient matrix of
`(e,h,e+h+z)` in the basis `(e,h,z)` is triangular with diagonal entries 1,
so the hypothesis holds. With common prices `mu_i=mu` and `c_i=c`,

    OPT = min(3mu, 2mu+4c).

The switch is at `mu=4c`. With unequal prices `(mu;c)=(3,5,10;1,3,2)`,
the optimum is **15**, attained by `R_01;2`. With `(1,9,9;1,1,1)`, it is
**6**, attained by `T_0`.

## Lower bound for arbitrary interleavings

Track the three dirt coefficients and the source coefficient in each row.
The dirt matrix starts at I. Every ADD is an invertible elementary row
operation, and an insertion does not affect dirt. Thus every prefix and
suffix dirt matrix is invertible. Correctness on all inputs forces the
final dirt matrix to be I and the final source column to be lambda. Scalar
inputs already force these identities; they also suffice for every width w.

### Incoming-row return lemma

A row cannot receive exactly one nonzero ADD in a restoring word. Suppose
its only incoming ADD is `E_ij(alpha)`, and let M be the preceding invertible
dirt matrix. Row i has remained the standard row e_i. The update changes it
to `e_i+alpha m_j`, where m_j is row j of M. No subsequent operation changes
this dirt row. Restoration would imply `alpha m_j=0`; right multiplication
by `M^-1` gives `alpha e_j=0`, hence `alpha=0`, a contradiction.

Consequently, a row with a nonzero demand and no insertion must receive at
least two ADDs. With no incoming ADD its source coefficient would stay zero;
exactly one is excluded by the lemma. This is the incoming-row argument
credited to #3063/#4916/#5163 and used in #5259. It applies to the **total**
number of incoming ADDs, not separately to each directed edge.

### Two insertions must both use units

If the insertion coefficients are beta_t and their rows are r_t, linearity
of the source column gives the exact identity

    lambda = sum_t (L_t e_(r_t)) beta_t,                         (1)

where L_t is the invertible matrix of all ADDs after insertion t. Later
insertions add their own terms and do not change this propagation rule.
Equation (1) permits arbitrary earlier/later insertions, cancellations and
feedback through other rows.

Every element of a local ring is either in m or is a unit. There is no
zero-insertion solution because all three demands are nonzero.

* With one insertion having a unit coefficient, reduction of (1) modulo m
  gives a nonzero field scalar times a column of an invertible matrix. That
  column cannot vanish, whereas lambda reduces to zero. If instead the
  coefficient lies in m, reducing (1) modulo `m^2` places all three demand
  classes in the span of one class. Both possibilities contradict the
  hypotheses. Thus at least two insertions are necessary.
* With exactly two insertions and exactly one unit coefficient, the same
  reduction modulo m leaves one nonzero invertible-matrix column and gives
  a contradiction. If neither coefficient is a unit, both lie in m. For
  `beta in m`, the class of `a beta` in `m/m^2` equals the residue of a times
  the class of beta. Therefore (1) puts the three demand classes in the span
  of the two insertion classes, which has dimension at most two. This also
  contradicts independence.

Hence **every solution with exactly two insertions has two unit insertion
coefficients**. This conclusion does not rule out such words: the matching
T words below use two units. It rules out the rank-two nonunit mechanism.

### Classify the insertion support

Write S for the set of rows receiving nonzero insertions, and K_i for the
number of nonzero incoming ADDs into row i.

1. If S contains all three rows, the bill is at least D.
2. If `S={i}`, the preceding argument forces at least two insertions into i.
   The other two rows have nonzero demand and no insertion, so `K_j,K_k>=2`.
   The bill is at least T_i.
3. Let `S={i,j}` and let k have no insertion, so `K_k>=2`. If row i receives
   at least two insertions, the bill is at least `R_ij;k`; the same conclusion
   with i,j interchanged holds if j receives at least two.
4. The only remaining case has exactly one insertion in each of i and j.
   Both insertion coefficients are units. If i received no ADD, its final
   source coefficient would equal its sole unit insertion coefficient,
   contrary to `lambda_i in m`. Thus `K_i>0`, hence `K_i>=2` by the return
   lemma; likewise `K_j>=2`. Every such word costs at least

       mu_i+mu_j+2c_i+2c_j+2c_k
         = (T_i+T_j)/2 + c_i+c_j
         > min(T_i,T_j).                                      (2)

   It therefore cannot be cheapest at any strictly positive price vector.

These alternatives exhaust all finite words and prove the stated lower
bound. In particular, (2) is a **price-dependent comparison with a pair of
other words**, not componentwise domination by a single count vector. It
establishes the envelope without classifying all unexposed Pareto vectors.

## Matching words

All words below are listed in chronological order. For any current dirty
rows, the echo

    E_ji(a), P_i(b), E_ji(-a)

increments root i by `b p` and receiver j by `-ab p`, while restoring all
original dirt. Indeed j first becomes `A_j+a A_i`, root i then becomes
`A_i+b p`, and the last gate leaves `A_j-ab p`. This calculation remains
valid when A_i and A_j already contain source contributions.

Set `u_i=lambda_i-1`. Since `lambda_i in m`, u_i is a unit. Independence
makes every lambda_i nonzero. Thus all coefficients in these words are
nonzero and their displayed count vectors are exact.

* **D:** `P_0(lambda_0), P_1(lambda_1), P_2(lambda_2)`.
* **T_i:** for the other two rows j,k, use

      E_ji(-lambda_j), P_i(1), E_ji(lambda_j),
      E_ki(-lambda_k u_i^-1), P_i(u_i), E_ki(lambda_k u_i^-1).

  The first echo delivers lambda_j to j, the second delivers lambda_k to k,
  and i receives `1+u_i=lambda_i`. The bill is `2mu_i+2c_j+2c_k`.
* **R_ij;k:** use

      E_ki(-lambda_k), P_i(1), E_ki(lambda_k),
      P_i(u_i), P_j(lambda_j).

  The echo delivers lambda_k to k; the last two insertions leave the
  remaining demands. The bill is `2mu_i+mu_j+2c_k`.

For R16, signs disappear, `u_i=1+lambda_i` is self-inverse and
`lambda_k u_i^-1=lambda_k`. In particular a six-gate T_0 word is

    E_10(h), P_0(1), E_10(h),
    E_20(e+h+z), P_0(1+e), E_20(e+h+z).

These constructions attain every term of the lower envelope. Combined with
the preceding exhaustive lower bound, they prove the theorem for arbitrary
strictly positive real prices, independently of finite computation.

## All ten terms are necessary

Prices below are ordered `(mu_0,mu_1,mu_2;c_0,c_1,c_2)`.

| Unique minimum | Positive prices | Value | Next smallest term |
| --- | --- | ---: | ---: |
| D | `(1,1,1;1,1,1)` | 3 | 5 |
| T_0 | `(1,3,3;1,1,1)` | 6 | 7 |
| R_01;2 | `(1,2,5;1,2,1)` | 6 | 7 |

Row permutations expose all three T and all six R terms. A uniquely
minimizing term remains so in a neighborhood of its witness prices, so it
cannot be omitted from the formula. The verifier checks all permutations.

The rank hypothesis is substantive. For the lower-rank demand `(e,h,e+h)`
in the **same R16**, the predecessor M word

    E_01(1), E_20(1), P_0(e+h), P_1(h), E_20(1), E_01(1)

is correct and costs **14** at `(3,5,10;1,3,2)`, less than the present
formula's **15**. Its classes are dependent; the theorem does not apply.
The current three-generator target cannot use this cheaper word.

## Finite evidence and reproduction

`verify.py` is self-contained standard-library Python. Source files are
historical provenance, not runtime inputs. The coordinate ring interpreter
checks all commutative ring axioms, identifies the unique maximal ideal and
its square, and enumerates **every** ordered demand triple satisfying the
independence hypothesis in these three rings:

| Ring | Size | Size of m | Size of m^2 | Accepted triples |
| --- | ---: | ---: | ---: | ---: |
| `F2[e,h,z]/(e,h,z)^2` | 16 | 8 | 1 | 168 |
| `F3[e,h,z]/(e,h,z)^2` | 81 | 27 | 1 | 11,232 |
| `(Z/4)[x,y]/(x,y)^2` | 64 | 32 | 4 | 10,752 |

The first two counts are `|GL_3(F2)|=7*6*4` and
`|GL_3(F3)|=26*24*18`. In the third ring, `m=(2,x,y)` and
`m^2={0,2x,2y,2x+2y}`; there are `168*4^3` independent triples.
This last fixture tests the extension beyond square-zero maximal ideals.

The checks cover 22,152 demands, 221,520 words and 1,772,160 formal
forward/inverse column evaluations. For the requested R16 demand they also
check all `16^4=65,536` scalar dirty/source inputs for each of ten words in
both directions: 1,310,720 literal evaluations. Eleven controls exercise
rank loss, a unit demand, nonlocality, missing dirty preparation, an
odd-characteristic sign error, omission of a necessary unit inverse,
the false per-edge return lemma and nonpositive prices.

An independent implementation packs the complete `3 x 4` coefficient
matrix into 48 bits and uses bit arithmetic for R16. All 1,048,576 packed
coefficient/row products are compared with the coordinate implementation.
Bidirectional Dijkstra then permits every nonzero coefficient for every
one of the three insertion and six ADD locations: **135 neighbors per
state**, with no restriction on intermediate dirt, source support, unit
coefficients or gate patterns. It has no formula-derived cutoff or initial
upper bound. It stops only when its queue lower bound meets the best
complete path. Guards at 50,000 settled states and 1,000,000 combined
discovered states (checked before each expansion) raise an error rather
than certifying an unfinished search. Every returned path is replayed in
the coordinate interpreter and its bill is recomputed.

The four price queries use `(1,1,1;1,1,1)`, `(1,10,10;10,1,1)`,
`(1,2,10;10,10,1)` and `(1/2,2/3,3/4;1,4/3,5/4)`. Their exact optima are
respectively `3`, `6`, `6` and `23/12`, covering strict D, T and R regimes
and nonintegral prices.
These queries corroborate the proof; they are not an exhaustive price scan
or the justification for the all-ring/all-real-price theorem. An exploratory
search at `(1/2,4/3,7/3;2/3,3/4,1/5)` was interrupted before certification;
another at `(1/2,1,5/2;1/2,1,2/3)` hit a resource guard. Neither is counted
as evidence. The registered cases use bounded representative prices.

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/r16-radical-triple-fanout --check-only
python3.12 -B scripts/research_package.py --package research/r16-radical-triple-fanout
```

`VERIFY.json` registers isolated, warning-strict normal and optimized
Python 3.12 executions. Direct exported-source replay is also supported:

```sh
python3.12 -I -W error -B research/r16-radical-triple-fanout/verify.py
python3.12 -I -O -W error -B research/r16-radical-triple-fanout/verify.py
```

The script reports `PASS_R16_RADICAL_TRIPLE_FANOUT no_new_kappa` on success.
Checks use explicit exceptions, so `-O` does not disable them.

Local validation used CPython 3.12.13 on macOS 26.7.1 (x86_64). Both
registered commands and metadata/source pins pass; one direct normal replay
took 11.83 seconds, a single-run observation rather than a benchmark. The
four search queries settled 8,465 entries in total. Three disposable
optimized-script mutations were rejected: charging a T word for only one
insertion, deleting its first dirty preparation, and replacing the required
unit inverse by 1. These checks do not require an installed solver or network.

## Provenance, overlap and limits

Base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, refreshed at
entry on 2026-10-29 UTC. Exact Git-blob and SHA256 pins are in `SOURCES.json`.
`TASK.json` retains priority revision 8 and the original `bit-helper-contract`
card, explicitly recording the donor-assigned algebraic scope change.
No random card was drawn or rerolled.

The immediately preceding overlap snapshot completely paginated 328 open
PRs at 17:27 UTC and 5,940 Discussion/comment/reply records at 17:30 UTC.
Entry checks refreshed main, current coordination threads and all-state PR
searches for the nonprincipal/three-generator and e,h,z fanout problem.
At the 17:54 UTC submission checkpoint, canonical main remained unchanged;
the refreshed discussions/handoffs/fanout thread and all-state PR searches
found no updates since the snapshot and no same-scope result or active claim.
The local
note scan covered 42 packages and omitted 8,581 tracked notes in the sparse
checkout; it was not treated as a complete repository-history review.
This is a bounded project-overlap check, not a proof of global novelty.

The source pins all resolve at the base commit, which is the direct parent
of this contribution. The optional full-history preflight is not claimed:
this is a shallow checkout. Hosted CI and independent review are separate
pending steps; no selected-operator, Lean, Docker or historical suite replay
is needed for this isolated five-file addition.

The written lower bound requires mathematical review. Finite replay is not
proof-kernel verification, independent human approval or admission as a
multiplication supplier. This package does not settle directed-edge tariffs,
nonlocal rings, dependent demand classes, extra helpers or all unexposed
Pareto vectors. Applying a word physically requires pricing coefficients,
source access, routing, precision, stock and the full H2/K interface. The
selected frontier is unchanged and no new kappa is claimed.

## Open next questions

The structured questions are also recorded in `TASK.json`.

1. Determine the **complete Pareto frontier** for the requested R16 demand.
   The exact positive-price envelope can omit unexposed vectors. The first
   unresolved branch is one unit insertion in each of two different rows:
   classify which restoring count vectors are attainable, beginning with
   `(P_i,P_j,P_k)=(1,1,0)` and `K=(2,2,2)`. Equation (2) settles their price
   relevance but neither their existence nor componentwise minimality.
2. Determine the tariff with independently priced directed ADD edges.
   This matters when two parents feeding the same row have different costs.
   Begin with a cheap directed three-cycle and full dirt tracking. The
   present incoming-row lemma loses edge information; the five-ADD identity
   in the verifier rules out simply imposing two calls on every used edge.

These are proposed follow-ups, not overlap reservations or claims of novelty.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in source
inspection, derivation, implementation, checking and writing. No subagents
or independent reviewers were used. Apache-2.0.

The interpreter, count bookkeeping and bidirectional shortest-path method
adapt lee-phys #5259/#5514, pinned here; predecessors remain unchanged.
Credit Ali Romman #5266/#5310 for source-insertion feasibility, lee-phys
#5139/#5163/#5259 for ideal invariance, the local-ring boundary and the
non-zero-sum handoff, Nick Petalas #5208/#4916 for the equal-demand theorem
and ring-valued contract, Krzysztof Wojt #5045 for source-count classification
and two-row restoring words, Ross Richardson #3063/#3121 for tariff and
dirt-restoration arguments, and Cinna Davis, Anthony, Oscar Fennell,
Tekalign and the retained lineage. The new step is the independent-class
obstruction to nonunit two-insertion words, the two-root price comparison,
and the matching ten-term envelope over general commutative local rings.
