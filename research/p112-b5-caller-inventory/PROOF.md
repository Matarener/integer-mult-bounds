# A fixed conditional inventory for the historical b=5 cells

Let K have characteristic zero, let C be the P112 root-evaluation code,
and let q_1,...,q_n be independent vectors in K^112. Their binary weights
are ranks of the leading-one E8 labels on their supports. Write T for their
span and D=T intersect C. The callers considered here have dim(D)>=5,
5<=n<=5+t, t in {5,6}, weights in {2,...,7}, and strict excess
sum(w_i-2)<30. These are the explicit historical TWOSIDE hypotheses.

The result is a source-bound composition of six fixed contracts. Conditional
on the six stated contracts, all 38 original (5,5) survivors and 76 of the 77
original (5,6) survivors are excluded. The latter cell contains the former;
there are 77 distinct survivor profiles, not 115. The sole row uncertified
by this inventory is 2^5,6,7^5. This is neither a claim that it is globally
open nor a claim that it is realizable. A concurrent investigation targets
its common30 geometry; that new theorem is outside this frozen inventory.

## Sources, hypotheses and attribution

We inherit the P112 distance53, injective root evaluation and support caps

| binary weight | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|
| support cap | 2 | 4 | 8 | 12 | 20 | 36 |

The low-rank caps follow from the leading-one labels; the rank-five and
rank-six capacities and geometric code facts are inherited, not recomputed
here. Their exact proof context is in the retained input contracts. Historical
filter capacities are those of DreamingOfClouds's PR3154, including its
conditional rank-seven cap32 in the low-support tests. The historical filter
count is a source reproduction, not an independent audit of that reduction.

| Inventory key | Exact stated contract | Predecessor |
|---|---|---|
| rank6_29 | Three residual rank<=6 pieces outside one common cut<=29 intersect the restricted code in dimension<=1 | Nick Petalas, PR3262 |
| rank5_47 | Three residual rank<=5 pieces outside one common cut<=47 intersect the restricted code in dimension<=1 | Nick Petalas, PR3283 |
| six_support20_30 | Independent small pieces with support union<=30 and six independent endpoints each supported on<=20 coordinates have code intersection dimension<=4 | Nick Petalas, PR3205 |
| beta7p2 | Outside two fixed binary six-spaces and a common set<=2, qualifying residual-rank<=7 directions span<=4 | DreamingOfClouds, PR3154 FINITE, completed PROOF_MAP/full_b evidence; source-bound transfer in PR3289 |
| common23 | A common cut<=23 admits at most three projective residual-rank<=7 directions over characteristic zero | Chris R / Clear1nsight with Codex, PR3931 |
| common24 | A common cut<=24 admits at most two projective residual-rank<=7 directions over characteristic zero | Chris R / Clear1nsight with Codex, PR3960 |

PR3283 is the rank-five cut47 source. An exploratory private script used
3277 as a rule label; that number names an unrelated result and is not an
accepted citation in this inventory here. PREDECESSORS.json records exact scientific/public
heads. SOURCES.json binds canonical-main input bytes and the two retained
pending proof texts. Pending contracts remain conditional. No heavy
predecessor census, human approval or proof-kernel validation is claimed.

## Deletion and restriction transfer

Delete d independent pieces and let T' be the span of those retained. Then
codim_T(T')=d and dim(T' intersect C)>=dim(D)-d>=5-d. For a selected collection
of small pieces let S be their actual support union. Its cardinality is at
most the sum of the displayed individual support caps, without any assumption
of disjointness. Whenever that cap is below53, coordinate deletion pi_S is
injective on C. The small pieces vanish under pi_S, and binary support ranks
of the remaining endpoints cannot increase.

For either three-endpoint shortening theorem, select three endpoints and
n-6 small pieces, and delete the other three pieces. At least two code
dimensions remain. The common cap is respectively <=29 or <=47, hence
restriction preserves both. Their image lies in the span of the three
restricted endpoints, contradicting the stated dimension bound one.

For the six-endpoint theorem, select six endpoints and n-6 small pieces.
Delete no pieces, retaining at least five code dimensions. Endpoints of
binary rank<=6 have support<=20. A small support union<=30 therefore
contradicts PR3205 directly. This rule does not use a three-endpoint theorem
at a larger cut, and retains the collective independence hypothesis.

## Quotient transfer for the three direction contracts

Choose n-5 small pieces X with total support cap below53. Their images in
Q=T/D are independent: a relation would give a nonzero codeword supported
on S, below distance53, and independence of the original pieces ensures
that this proposed codeword is nonzero. Since dim(Q)<=n-5, these images form
a basis, so dim(Q)=n-5 and dim(D)=5.

Each of the five remaining pieces q_y has a unique combination a_y of X
such that c_y=q_y-a_y belongs to C. These five codewords are independent,
by their coefficients on the five distinct nonbasis pieces. Injective
root evaluation gives five independent directions h_y. Outside the ONE
common S, c_y agrees with q_y and thus has binary support rank<=7.
If the cap of S is<=23 or<=24, the respective common-cut contract admits
at most three or two projective directions. Each contradicts the required
five independent directions. There is no substitution of per-direction
small sets for one common set.

For beta7p2, partition X into indexed groups A,B,P whose weight sums in A
and B are each at most6 and whose support-cap sum in P is at most2.
Their support labels fit into two fixed binary six-spaces V_A,V_B. Let
S_P be the actual support union of P; it is one common set of at most2.
Outside Lambda(V_A) union Lambda(V_B) union S_P, c_y agrees with q_y.
All five directions therefore satisfy the inherited span<=4 contract,
a contradiction. The rational-kernel transfer to every characteristic-zero
K is recorded in the exact PR3289 input proof; no embedding K into R is
assumed. The old FINITE notes' unfinished state is superseded by the
retained PROOF_MAP and labelled full_b completion, all separately pinned.

## Exhaustive finite composition

The primary enumerates every sorted weight multiset, including those rejected
before any theorem is applied: 7,798 for (5,5), 12,166 for (5,6). On every
multiset its filter agrees with unchanged PR3154 bk2b.py. A separate checker
uses multiplicity vectors in excess coordinates and subset-sum packing,
imports no predecessor or primary executable, and reconstructs both complete
accepted sets. This independently agrees on38 and77 survivors.

For each of the six rules and each row, RESULT.json retains the number of
successful indexed assignments, the minimum capacity sum over the relevant
endpoint/basis class, and one complete literal witness when successful.
Equal-weight pieces have distinct indices. The primary shortening enumerator
chooses endpoints first; the separate implementation chooses small pieces
first. For beta7p2 the primary enumerates three-role strings, while the
separate checker chooses a cut subset and then splits its complement.
All690 rule/row combinations agree, including zero counts, minima and witness
membership. A minimum for beta7p2 is the unrestricted quotient-basis capacity
minimum; it is not a minimum under its packing constraints. The receipt's
unsuccessful beta count is the exhaustive packing result.

Disjoint primary attribution follows the displayed rule order:

| Cell | rank6_29 | rank5_47 | six_support20_30 | beta7p2 | common23 | common24 | Uncertified |
|---|---:|---:|---:|---:|---:|---:|---:|
| (5,5) | 34 | 1 | 0 | 2 | 1 | 0 | 0 |
| (5,6) | 61 | 6 | 2 | 2 | 3 | 2 | 1 |

These are recovered applications of credited results. Neither primary
attribution nor the addition of a coherent inventory claims a newly proved
geometric theorem or first exclusion of a profile. Other rules and literal
exclusions are intentionally outside this fixed inventory.

## Exact interface for the inventory gap

For 2^5,6,7^5 there are eleven pieces, strict excess29 and required code
intersection dimension at least5. The first six pieces have support-cap sum
5*2+20=30<53. Hence their images force quotient dimension6 and code-intersection
dimension exactly5. The five remaining rank-seven pieces yield five independent
code directions with residual rank<=7 after that same support union S.

All462 six-piece subsets have capacity sum at least30, with30 attained by
these first six pieces. This certifies the best sum of inherited individual
capacity bounds, not a lower bound on the actual union S. Actual support
overlap may reduce its size. The rank6_29, rank5_47 and six_support20_30
endpoint-compatible minima are respectively78,96,180; none meets its cut.
The beta7p2 packing has no success. The stated common23/common24 contracts
therefore leave this exact caller uncertified.

A uniform common30 theorem with span bound at most4 would exclude it, since
five independent directions are required. An arbitrary-cut witness admitting
five directions would only falsify that relaxation; it would not realize the
original independent pieces or their quotient coefficients. Conversely, a
separately verified common30 bound<=3 would complete the conditional77-row
inventory by this same quotient argument. The concurrent common30 work must
supply its own source pin, finite coverage and proof before that implication
can be promoted to a combined result.

## Scope and remaining obligations

This package authenticates sources and proves/replays the new composition.
The underlying geometric contracts, distance, capacities, characteristic-zero
normalization and original decoder reduction remain conditional mathematical
inputs with their published evidence status. The two cells are a historical
finite filter domain, not the entire current C5 frontier. Full C5, a global
P112 decoder floor, physical realization, supplier admission, multiplication
bounds and kappa are outside scope. Selected frontier remains unchanged.
