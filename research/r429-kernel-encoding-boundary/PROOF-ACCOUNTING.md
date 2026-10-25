# Fixed ker R code and complete optimistic caller invoice

This review establishes an exact finite encoder certificate and a written
all-parameter rejection of one stipulated caller invoice. It does not admit a
native encoded supplier, prove an integer cleanup, or improve kappa.

The immutable source is the `coded-bit-boundary` package in the
`kappa-changed-endpoints-20261019T0153Z` run, at scientific pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. `INDEPENDENT-RESULT.json`
records byte hashes for the raw R438 word, pruned R429 word and saved B13
receipt. The independent checker imports none of the original producer.
The other B13 reviewer owns the native entrance and actual target-cut witnesses.

## 1. Basis objective and exact encoder

Let R be the actual rank-nine binary reader on 111 ports. The checker obtains
its nine complete rows by reverse adjoint propagation through the raw D and A
ADD programs, instead of the producer's forward symbolic propagation.
Write c_p for its column at port p. A set P of nine dependent ports supports
a systematic 102-input code precisely when the columns indexed by P form a
basis of F2^9. For F the other 102 ports, the parity values are uniquely
determined by

    R_P z_P = R_F z_F.

For each p let w_p count actual MOVE events on both source port p and target
port 111+p in the retained cheap R429 bulk. This is an event-count objective,
not a native rank objective or a parity-preparation objective.

The selected order is

    P = [22, 6, 9, 19, 46, 60, 61, 66, 72].

It has weights [4,5,5,5,5,5,5,5,5] and independent columns. The independent
certificate enumerates all 512 binary combinations of these columns, obtaining
each vector of F2^9 exactly once. It also enumerates the complete spans of all
columns with weight at most each threshold:

| MOVE-count threshold | Span dimension |
| --- | ---: |
| 4 | 1 |
| 5 | 9 |
| 6 | 9 |
| 7 | 9 |

There are no weights below four. Any basis can take at most one weight-four
column; its other eight columns cost at least five each. Its total weight is
therefore at least 4+8*5=44, attained by P. This proves global minimum weight
over all binary-column bases without enumerating all nine-subsets. As a second
certificate, every selected element in each outsider's fundamental circuit
has weight at most that outsider's weight (470 checked incidences).

The 512-entry inverse map reconstructs every coefficient of the systematic
encoder E independently and matches the saved 111-by-102 binary matrix.
Its free rows are the identity, so its rank is 102; complete multiplication
gives RE=0. The parity-row weights, in selected order, are

    48, 49, 58, 58, 51, 51, 53, 52, 50.

Their sum is 470. With the nine parity cells initially zero, the literal
systematic preparation adds each listed free field once into its parity row.
It uses 470 unit VALUE ADDs per bank. Its reverse uses another 470; preparing
and unpreparing source and target banks separately thus uses 4*470=1880.
This counts this literal encoder. It does not prove a minimum ADD count,
exclude sharing between parity rows, or price ADDRESS routing. In particular,
minimum MOVE event count does not imply minimum encoder complexity.

Deleting the actual first parity ADD changes RE from zero to a nonzero
matrix; the receipt retains the full nine residual packed rows. The scalar
kernel identity alone is not a native code-invariance assertion. The original
633-input scalar replay and native cut witnesses have separate owners and
are not promoted into an integer-zero or all-size interface by this review.

## 2. Domain and complete favorable model

Fix an **odd integer L >= 3**, write B=(L-1)/2, and set

    m = 1+7L,       V = 102,       h = 429.

Use the retained ordinary paired caller with L-1 public banks, each carrying
V arbitrary fields. Use exactly L copies of the unchanged cheap R429 bulk.
This is not the alternative L-public-bank diagonal topology. The source and
target have 111 physical paths per active call; only 102 arbitrary public
fields in each are useful data. The remaining nine in each are code parity
fields. All 222 source/target paths have native rank mass seven individually,
as the checker verifies on actual MOVE records.

The complete one-call bulk histogram is

    H_bulk = {1:1295, 2:1342, 3:79, 4:44, 5:93, 6:11, 7:9},
    sum_r r H_bulk[r] = 4986 = 2*111*7 + 429*8.

The selected 18 parity paths have actual histogram

    {1:15, 2:11, 3:6, 4:3, 5:2, 7:7},

of event count 44 and mass 126. Thus their selection does not change the
private rank-mass penalty: every choice of nine source and nine target paths
costs 18*7=126 in this fixed bulk.

Let c=floor(sqrt((m^2-1)/2)). To partition a positive idle rank s, write
s=ac+b, 0<=b<c, and use a copies of rank c plus rank b if b>0. This preserves
rank mass. For each of the following idle slots use multiplicity 2V:

* two copies of rank 14j for every 1<=j<=B-1;
* B-1 copies of rank 7.

This multiset is the original chronological slot list collected by equal
rank, not a replacement schedule. At B=1 it is empty. Its unmultiplied mass is

    2*14 sum_(j=1)^(B-1) j + 7(B-1)
      = 7(B-1)(2B+1) = 7L(L-3)/2.

The complete public idle mass is consequently 7VL(L-3).

For width-eight helpers set

    q=floor(m/8),       p=m-8q,       W_h=hL/q.

The invoice grants fractional, perfectly packed helper banks. Each such bank
gets its padding rank p, partitioned by the same cap. Thus its total padding
mass is W_h*p. The total stock and child mass in this favorable relaxation are

    W = V(L-1) + W_h,
    Q = 4986L + 7VL(L-3) + W_h*p.

This includes every bulk call, public idle interval, helper bank and pad in
the declared model. Encoder/decoder work, zero preparation/cleanup, native
entrances, primitive operations and physical ownership are granted free.
The parity cells are not extra independent public input fields and receive
no public endpoint credit. Fractional banks and free private storage are
explicit allowances, not constructions of legal integral helper owners.

L>=3 ensures B>=1, q>=2, nonnegative idle multiplicities and positive stock.
L=1 has q=1, but B=0 and the retained paired topology has no public banks;
the odd-L slot identity used here is inapplicable. The original generator is
only invoked at L>=3. Even L is outside the stipulated paired topology.
The independent checker rejects all such out-of-domain values explicitly.

## 3. Exact all-L deficit and every positive exponent

Since m-p=8q, helper stock minus padding contributes

    m W_h - W_h*p = 8hL.

Therefore

    D = mW-Q
      = V(L-1)(1+7L) - 7VL(L-3) - (4986-8h)L
      = V(L-1) + 14VL - 1554L
      = V(L-1) - 126L
      = -24L-102 < 0.

These algebraic equalities prove the result for every odd L>=3; no numerical
sample or finite enumeration substitutes for them. The saved L values
3,5,7,9,11,13,17 are independent checks of every serialized histogram
coefficient, stock, mass and deficit.

For this model all multiplicities are positive after deleting zero entries.
Every bulk child has 1<=r<=7<m. Every idle/padding piece has 0<r<=c<m.
Hence, for any real a>0,

    M(a) = sum_r H[r]*(r/m)^(1-a)
         > sum_r H[r]*(r/m) = Q/m > W.

The last strict inequality is exactly D<0. The complete optimistic moment
already fails at a=0 and fails for every a>0. This includes the previously
screened values .002, .003 and .005 without a numerical power evaluation.
Adding nonnegative work with the same m, W and bulk cannot repair the
inequality. A different stock allowance, endpoint contract, chronology,
operator-valued code, or changed native child realization is a different
model and requires its own complete invoice.

## 4. Controls and limits

The controls mutate real accounting inputs and are expected to alter the
certificate; they are not asserted to implement valid suppliers.

* Removing the actual 18 selected parity MOVE paths changes the L=3 deficit
  from -174 to +204. This exposes the false favorable result obtained by
  charging 204 useful paths while silently deleting the 18 code paths.
* Adding a hypothetical extra 102-field endpoint bank, together with its
  rank-(m-1) idle interval, adds 102m stock mass and 102(m-1) child mass.
  It changes D by +102, giving -72 at L=3. It is a sensitivity control for
  endpoint credit, not a legal hosting proof or a favorable result.
* Deleting one actual preparation ADD breaks RE=0. The full original code
  remains a positive cancellation control.

This accounting review proves no native reconstruction theorem, universal
encoding lower bound, full-rank reader tariff, all-size dispatcher, rounded
precision bound, integer restoration, physical tape realization or kappa.
It does not claim that this systematic code is the best possible code.

## 5. Predecessors and bounded overlap review

The actual word, reader and source/target paths come from the frozen
R438 transport rehost, R429 pruning, full compensation and native BIT sources
retained in the original package. The ordinary paired public-idle accounting
is inherited; it is not introduced here. The earlier retained paired-schedule
audit [PR3850](https://github.com/CrocSwap/integer-mult-bounds/pull/3850)
also uses L-1 public banks and idle mass 7L(L-3) per port. This review changes
the useful public width to 102 and retains all 18 private code paths.

[PR4033](https://github.com/CrocSwap/integer-mult-bounds/pull/4033) concerns
fixed R429 cold-factor/separate-reader costs for its stated full input
contract. This code instead restricts each 111-port bank to a 102-dimensional
subspace, so it is not a counterexample to that contract.
[PR4039](https://github.com/CrocSwap/integer-mult-bounds/pull/4039) retains
111 arbitrary fields and studies its FULL-target interface and caller
topologies. The present restricted-input invoice has different endpoint
credit and is not a contradiction of its conditional accounting.

Ali Romman's [PR1136](https://github.com/CrocSwap/integer-mult-bounds/pull/1136),
head `e6a8003673d55929be6925b22f9ee645d03c33c3`, already proves generic
binary-encoding/native-boundary obstructions and an algebraic two-block
escape for PR840's centered shear. Its full VALUE-domain conjugacy rank and
native-orbit hypotheses differ from this R429 scalar ker R code and its
ordinary paired invoice. It is prior related work, not a proof of the B13
claim. The exact proof and read-only PR metadata are retained alongside this
review; no historical verifier was rerun. The targeted local/PR lookup is
not an exhaustive literature or priority search, and no novelty guarantee is
made for the general kernel or encoding principles.

Substantial OpenAI Codex assistance. Apache-2.0; predecessor attribution and
their narrower contracts are retained. This is an independent computational
cross-check and written proof audit, not independent human or formal-kernel
verification.
