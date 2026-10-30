# Exact tariffs for three orthogonal Boolean demands

**Scoped written proof with exact finite corroboration; no new kappa.**
For three arbitrary dirty rows over `F_2^3`, demand
`((1,0,0),(0,1,0),(0,0,1))` has an exact **twenty-five-term** optimum at
all positive source-insertion and destination-row ADD prices. Every listed
price term is attained and indispensable. The proof applies to any three
nonzero pairwise orthogonal elements of any commutative unital Boolean ring.

This resolves Open next question 2 of lee-phys's
[PR #5304](https://github.com/CrocSwap/integer-mult-bounds/pull/5304),
head `c8bf34c359b3a12f112078f0072b4ecc7a942109`. That theorem concerns
zero-sum demands `(3,5,6)`, not the present `(1,2,4)` (bitmask notation).
Ali Romman's [#5310](https://github.com/CrocSwap/integer-mult-bounds/pull/5310)
already determines the minimum source-insertion count; this contribution
prices the complete restoring word. The new steps are the sharp weighted
one-insertion bound, the exclusion of the two-fixed-parent branch, and
matching non-zero-sum constructions. The proof is self-contained.

## Contract and exact formula

Let R be a commutative unital Boolean ring, `1 != 0`, so `x^2=x` for all x.
Expanding `(x+1)^2=x+1` gives `2x=0`. There are exactly three independent
arbitrary dirty rows `a_i in R^w`, w >= 1, and a disjoint preserved source
`p in R^w`. For every input, a fixed finite word must produce

    A_i = a_i + lambda_i p,  i=0,1,2.

The only gates are

    P_i(beta):   A_i <- A_i + beta p,       price mu_i > 0;
    E_ij(alpha): A_i <- A_i + alpha A_j,    price c_i > 0, i != j.

All ring coefficients and ordered row pairs are allowed. Prices are finite,
stationary, coefficient-independent complete abstract prices. There are no
extra rows, observations, adaptive choices, clearing or free basis changes.
All original dirt columns must return; separate inverse execution is charged
separately. Zero-coefficient gates can be deleted since prices are positive.

**Theorem.** Assume every lambda_i is nonzero and
`lambda_i lambda_j=0` for distinct i,j. Set `g=lambda_0+lambda_1+lambda_2`.
For distinct i,j,k and arbitrary h in `{0,1,2}`, define

    D       = mu_0 + mu_1 + mu_2,
    T_i     = 2mu_i + 2c_j + 2c_k,
    B_k     = mu_i + mu_j + 2c_k + min(mu_i,mu_j,2c_i,2c_j),
    U_(i,h) = mu_i + 2(c_0+c_1+c_2) + 2c_h.

Then the exact optimum over every allowed finite word is

    OPT = min(D, T_0,T_1,T_2, B_0,B_1,B_2,
              min_i(mu_i) + 2 sum_i(c_i) + 2 min_i(c_i)).

Expanding the minima gives 1 D term, 3 T terms, 12 B terms and 9 U terms:
**25 indispensable linear price terms**. Minimizers in the last term may
choose the insertion row and the cheapest ADD row independently.
The formula and an attaining word require a constant number of comparisons
once the ring hypotheses and prices are supplied; testing those hypotheses
or implementing the abstract primitives is not included.

For the requested ring, encode `(x_0,x_1,x_2)` as `x_0+2x_1+4x_2`.
Addition is XOR, multiplication is AND, identity is 7, and demand is `(1,2,4)`.
At `mu=(10,100,100), c=(1,1,1)`, the exact cost is **18**; the zero-sum
predecessor's value 16 is inapplicable. With common prices mu and c,

    OPT = min(3mu, mu+8c).

Indeed the other potentially competitive term is `2mu+4c`, the arithmetic
mean of these two quantities. The transition is `mu=4c`; two-insertion
words also tie there. A one-insertion word needs at least eight ADDs and
can attain that number. For root 0 and the extra two ADDs charged to row 0:

    E_02(4), E_01(2), E_20(4), E_10(2), P_0(7),
    E_10(2), E_20(4), E_01(2), E_02(4).

## Algebra and the incoming-row return lemma

Orthogonality gives `g lambda_i=lambda_i` and
`(lambda_0,lambda_1,lambda_2)=(g)`. Also `g!=lambda_i` for each i: multiply
an alleged equality by any other nonzero lambda_j. No lambda_k belongs
to `(lambda_i,lambda_j)` when i,j,k are distinct, since multiplying such
an expression by lambda_k would imply `lambda_k^2=lambda_k=0`.
In particular each pair of principal demand ideals is incomparable.
Finiteness of R and a decomposition into fields are not assumed.

Let P_i count nonzero source insertions into i, and K_i count all incoming
nonzero ADDs. Prefix dirt matrices are invertible: each elementary row ADD
has an inverse (the same gate here), and P gates do not change dirt. Testing
each original input column separately forces the final dirt matrix to be I.

**Return lemma.** A row cannot receive exactly one nonzero ADD. Before
its only `E_ij(alpha)`, its dirt row is e_i. If the prefix dirt matrix is M,
after that gate its dirt row is `e_i+alpha m_j`. No later gate changes this
dirt row. Restoration would give `alpha m_j=0`; multiplying by `M^-1`
gives `alpha e_j=0`, hence alpha=0, a contradiction. Thus every used ADD
destination has K_i>=2. A nonzero-demand row with no insertion needs ADDs
and consequently K_i>=2.

This is the credited incoming-row argument of #3063/#4916/#5163. It does
not say every used directed edge occurs twice; a control retains the
five-ADD identity from #5163 that disproves that stronger statement.

## The new one-insertion lower bound

Suppose exactly one insertion `P_i(beta)` occurs. Write M for the ADD-only
prefix dirt matrix and L for the ADD-only suffix dirt matrix. Restoration
requires `LM=I`, and the final source column is `L(beta e_i)=lambda`.
Thus every lambda_r is a multiple of beta, and `L^-1 lambda=beta e_i`
expresses beta as a combination of the demands. Hence `(beta)=(g)`.
A principal ideal in a Boolean ring has a unique generator: writing
`beta=xg` and `g=y beta` yields `beta g=beta` and `beta g=g`, respectively.
Therefore **beta=g**. This uses the ideal invariant from #5139/#5310.

**Column lemma.** Any ADD-only word taking `g e_i` to lambda costs at least

    c_0+c_1+c_2 + min(c_0,c_1,c_2).

Every row must be an ADD destination: the two other rows start at zero and
end nonzero, and row i starts at g and ends at `lambda_i!=g`. Three gates
would therefore update each row exactly once. At the sole update of i,
its parent j has source coefficient either zero (before j's sole update)
or lambda_j (after it). The zero case cannot change g. In the other case,
`g+alpha lambda_j=lambda_i` is impossible: multiplying by the remaining
lambda_k gives `lambda_k=0`. Thus at least four gates are necessary, at
least one into each row. Their positive-price bill is at least the stated
sum plus the cheapest possible fourth gate. The argument covers arbitrarily
long words, since any word has at least those counts.

Apply this lemma both to the suffix and to the inverse prefix. Indeed,
`M^-1=L`, so each maps `g e_i` to lambda. Inversion preserves the number of
gates charged to each destination. The original prefix and suffix therefore
cost at least twice the column bound. Including the insertion gives

    bill >= mu_i + 2 sum_r(c_r) + 2 min_r(c_r).

This proves the one-insertion part for arbitrary interleavings: with one P
there is exactly an ADD prefix and an ADD suffix, and neither is free.
It also explains why charging only one extra ADD beyond the old six-ADD
return bound would be insufficient. No insertions cannot supply nonzero demand.

## The multi-insertion lower bound

Now suppose there are at least two insertions. Let S be their row support.
This classification adapts #5259/#5304; the final case changes because the
present third demand is outside the ideal of the other two.

* If S contains all rows, the counts dominate D.
* If `S={i}`, then P_i>=2 and K_j,K_k>=2, giving T_i.
* If `S={i,j}`, then K_k>=2. A repeated insertion in i or j gives respectively
  `2mu_i+mu_j+2c_k` or `mu_i+2mu_j+2c_k`.
* Otherwise P_i=P_j=1. If i or j receives any ADD, the return lemma gives
  respectively `mu_i+mu_j+2c_k+2c_i` or `mu_i+mu_j+2c_k+2c_j`.
* The only remaining possibility has K_i=K_j=0. The insertion coefficients
  must then be lambda_i and lambda_j, since these rows never receive ADDs.
  Row k can acquire only source coefficients in `(lambda_i,lambda_j)`;
  its target lambda_k lies outside that ideal. This case is impossible.

Taking the minimum of the four feasible terms for S={i,j} gives B_k.
The proof covers feedback, cancelling insertions, arbitrary coefficients
and arbitrary word lengths. Together with the one-insertion bound it proves
the displayed lower bound for every word and every strictly positive real price.

## Matching constructions

All words below are chronological; i,j,k are distinct. An echo

    E_ji(a), P_i(b), E_ji(a)

returns all dirt, adds b to i's source coefficient and adds ab to j's.
This holds even when i already has a source coefficient: its pre-existing
value cancels between the two E gates. In characteristic two each gate is
its own inverse; reverse the gate order to invert a word.

| Family | Nonzero counts in `(P_0,P_1,P_2,K_0,K_1,K_2)` | Number |
|---|---|---|
| D | all P_i=1 | 1 |
| T_i | P_i=2, K_j=K_k=2 | 3 |
| R_(i,j;k) | P_i=2, P_j=1, K_k=2 | 6 |
| M_(i,j;k) | P_i=P_j=1, K_i=K_k=2 | 6 |
| U_(i,h) | P_i=1, all K_r=2, with two additional ADDs into h | 9 |

**D:** insert `P_i(lambda_i)` in each row.

**T_i:** use

    E_ji(lambda_j), P_i(g), E_ji(lambda_j),
    E_ki(lambda_k), P_i(g+lambda_i), E_ki(lambda_k).

Row i receives `g+(g+lambda_i)=lambda_i`. The echoes give lambda_j to j
and `lambda_k(g+lambda_i)=lambda_k` to k.

**R_(i,j;k):** use

    E_ki(lambda_k), P_i(lambda_i+lambda_k), E_ki(lambda_k),
    P_i(lambda_k), P_j(lambda_j).

The echo gives lambda_k to k; the two i insertions sum to lambda_i.
The j insertion is direct. These are the first two expanded B terms.

**M_(i,j;k):** let the two-gate suffix C be

    E_ki(lambda_k), E_ik(lambda_k).

It sends `(lambda_i+lambda_k)e_i` to `lambda_i e_i+lambda_k e_k`.
Execute `C^-1, P_i(lambda_i+lambda_k), C`, followed by `P_j(lambda_j)`.
The conjugation restores dirt and has two ADDs each into i and k. These
are the other two expanded B terms (choose which insertion row receives ADDs).

**U_(i,h):** build a four-gate suffix C taking `g e_i` to lambda, with
one gate into each row and one extra into h. If h=i, use

    E_ji(lambda_j), E_ki(lambda_k), E_ij(lambda_j), E_ik(lambda_k).

The first two gates fill j,k; the last two remove lambda_j and lambda_k
from g at i. If h is another row, relabel it j, let k be the third row,
and write `q=lambda_j+lambda_k`. Use

    E_ji(q), E_ki(lambda_k), E_ij(q), E_jk(lambda_k).

Its source column, in i,j,k order, evolves as

    (g,0,0) -> (g,q,0) -> (g,q,lambda_k)
            -> (lambda_i,q,lambda_k) -> (lambda_i,lambda_j,lambda_k).

Here `q^2=q`, `g+q=lambda_i`, and `lambda_k^2=lambda_k`. Execute
`C^-1, P_i(g), C`. Dirt returns and the inserted column becomes lambda.
The extra two ADDs can therefore be placed in **any** row h, independently
of the insertion row i. This attains every U term and the weighted column bound.

All coefficients in these words are nonzero: sums of distinct nonzero
orthogonal demands cannot vanish. Thus the displayed counts are exact.
Every lower-bound price term is attained, completing the theorem.

## Every price term is necessary

The following strictly positive price vectors uniquely minimize the indicated
term among all 25. Permuting row labels supplies the remaining terms. Direct
substitution into the table verifies the strict inequalities; the verifier
checks all permutations with exact arithmetic.

| Unique minimum | `(mu_0,mu_1,mu_2,c_0,c_1,c_2)` | Value |
|---|---|---|
| D | `(1,1,1,1,1,1)` | 3 |
| T_0 | `(1,3,3,1,1,1)` | 6 |
| R_(0,1;2) | `(1,2,5,1,2,1)` | 6 |
| M_(0,1;2) | `(3,5,10,1,3,2)` | 14 |
| U_(0,0) | `(5,9,9,1,2,2)` | 17 |
| U_(0,1) | `(7,12,12,2,1,2)` | 19 |

This is an exact **price envelope**, not a claim that these are every
componentwise minimal attainable count vector. The one-insertion lower
bound is weighted; it does not prove componentwise domination by one U
vector when different rows carry the excess prefix and suffix gates.
The possible additional, unexposed Pareto vectors are a separate question.

## Bounded verification and limitations

The self-contained standard-library verifier checks all ordered nonzero
orthogonal demand triples over `F_2^n`, n=3,4,5, including proper demand
ideals. It checks all 25 words and inverses on all four formal input columns,
then all scalar inputs for the requested eight-element instance. It also
checks every strict price exposure and the uniform-price corollary.

An independent source-column Dijkstra search permits every nonzero coefficient
and every directed ADD, for each root and each destination-price vector in
`{1,2,3}^3`. Its 81 exact answers corroborate the column lemma and the
sharp weighted bound. This projection alone does not check dirt restoration.

A separate packed-state bidirectional Dijkstra search tracks all nine dirt
and three source coefficients and allows all 63 nonzero gates. It has no
word-length cutoff, formula-dependent pruning or restriction to displayed
constructions. The sum of the frontier minima certifies the best meeting
cost. Rational prices are scaled exactly to integers, and each returned path
is replayed by the coordinate-arithmetic interpreter. Its five price queries
cover D/T/R/M and a rational fixture; the U branches are corroborated by the
column searches and full endpoint replay, not by those five full-state queries.
The all-price theorem rests on the written proof, not on finite sampling.

```sh
python3.12 -B scripts/research_package.py --package research/orthogonal-boolean-fanout --check-only
python3.12 -B scripts/research_package.py --package research/orthogonal-boolean-fanout
python3.12 -I -W error -B research/orthogonal-boolean-fanout/verify.py
```

Recorded finite coverage: 456 demand triples, 11,400 words, 91,200 formal
forward/inverse column checks, 204,800 literal input checks, all 25 strict
exposures, 81 column-distance queries and ten controls. Five full-state
shortest-path queries settle 90,347 states in total, counted separately by
direction and query; their optima are 3, 6, 6, 14 and 41/15. Controls distinguish
nonorthogonal demands, zero demands, omitted dirt preparation, the wrong
Boolean identity, an invalid per-edge return bound and nonpositive prices.
The registered normal and optimized Python 3.12 runs agree. Three disposable
optimized-mode mutations reject an underpriced one-insertion branch, an
omitted suffix gate and incorrectly forcing the cheapest extra ADDs to use
the insertion row.

Independent human review and proof-kernel acceptance are unclaimed.
Independently priced directed edges, extra helpers, restricted coefficients,
non-Boolean rings and a complete Pareto census are outside this theorem.
Physical source access, coefficient production, routing, precision, stock
and supplier admission remain separate; the selected frontier is unchanged.

## Sources and coordination

Scientific base: canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`,
priority revision 7. TASK.json retains the historical `bit-helper-contract`
card and explicitly records the donor-assigned algebraic scope change.
SOURCES.json pins the merged predecessor proof/code bytes at this main base.
No predecessor executable, historical Git object, network or third-party
library is required for direct verifier execution.

Entry checks on 2026-10-25 covered 371 open PRs (05:34 UTC) and 4,779
Discussion records (05:37 UTC), both with complete remote pagination, plus
all-state targeted PR searches and current #1166/#5030 reads. No resolving
result or same-scope active claim appeared within that coverage. Sparse
historical notes, arbitrary diffs and unpublished work remain coverage limits.
The public #5030 predecessor leaves this exact question unreserved.
Submission freshness and publication status are recorded with the contribution.

## Open next questions

1. Determine the complete aggregate Pareto frontier for this same demand.
   Start with eight-ADD one-insertion words having incoming counts
   `(3,3,2)` and its permutations, for each insertion row. The
   tariff proof permits them but neither constructs nor excludes them;
   deciding them separates exposed price-envelope vectors from all Pareto vectors.
2. Determine the tariff with independently priced directed ADD edges. Begin
   with a common insertion price, unit prices on a directed three-cycle and
   a common positive reverse-edge price. The present row-price column lemma
   loses parent identities and cannot by itself supply that lower bound.

These are suggested next obligations, not reservations or novelty guarantees.
Structured first steps and blockers are in TASK.json.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in source
inspection, derivation, implementation, checking and writing. No subagents
or independent reviewers were used. Apache-2.0. The interpreter and full-state
Dijkstra infrastructure are adapted from lee-phys #5304, which adapted #5259;
those packages also supply the insertion-support framework and return lemma.
Credit Ali Romman #5266/#5310 for source-insertion feasibility, lee-phys
#5139/#5163 for ideal invariance and the local-ring boundary, Nick Petalas
#5208/#4916 for equal-demand tariffs and the ring-valued contract, Krzysztof
Wojt #5045 for support classification and restoring words, Ross Richardson
#3063/#3121 for tariff/restoration arguments, and Cinna Davis, Anthony,
Oscar Fennell, Tekalign and the retained earlier fanout lineage.
