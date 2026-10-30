# Complete count vectors for the unsigned depth-three chain

## Contract and predecessor results

Let R be a nonzero unital ring of exact characteristic m >= 2. Four distinct
registers x,z1,z2,y contain arbitrary data in compatible R-modules. The source
x is immutable. The only complete operations, written as letters, are

```text
1: z1 += B1 x
2: z2 += B2 z1
3: y  += B3 z2
```

Each map is arbitrary and R-linear. Correctness means restoring z1,z2 and
adding c B3 B2 B1 x to y for every admissible map and dirty initial state,
where 1 <= c < m. No inverse call, extra register, direct composite operation
or free data operation is available. A call includes its own scratch and head
restoration. A scalar price p_l > 0 is fixed for each complete operation.
Word-dependent instruction, admission and routing costs are additional.

Nick Petalas's [PR4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249),
head `03b8a19d7442edebb3565064631f6ca2408d731e`, proves the unit-length law
3m except at (m,c)=(2,1),(3,2),(4,3), where it is 4m. Its interval-count
identity and balanced construction are recalled below to make this proof
self-contained. This contribution classifies the complete attainable count
set and gives its unequal-price and multiplicity consequences. The binary
weighted result already follows from the stronger arbitrary-workspace bound
in ToikY's [PR1662](../ut4-central-tariff-relaxation/README.md), and is not claimed new.

## The count classification

For a word w, let n_l count its occurrences of l. Define P(m,c) by

```text
P(2,1) = {(2,4,2)}
P(3,2) = {(6,3,3), (3,6,3), (3,3,6)}
P(4,3) = {(8,4,4), (4,8,4), (4,4,8)}
P(m,c) = {(m,m,m)} in every other case.
```

**Theorem 1.** A nonnegative integer count vector n is attained by a correct
word if and only if every n_l is divisible by m and n dominates some vector
in P(m,c) coordinate by coordinate. Thus P is exactly the Pareto-minimal
set, including the assertion for words of arbitrary length.

Let N_ij be the number of scattered subwords i(i+1)...j in w. Appending
letter j adds N_i,j-1 to N_ij for i<j, and increments N_jj. Induction gives

```text
z_j(final) = z_j(initial)
             + sum_{i<=j} N_ij B_j ... B_i z_{i-1}(initial).
```

Here z0=x and z3=y. Correctness is equivalent to all six interval counts
being zero modulo m except N_13=c. Sufficiency follows from this identity.
For necessity specialize every module to R and every map to the identity,
and turn on one initial register at a time. Exact characteristic makes an
integer multiple of 1 vanish exactly when divisible by m. This argument
requires no commutativity, invertibility or field hypothesis.

It follows that each n_l is a positive multiple of m. Zero occurrences of
any letter force N_13=0. For nonexceptional targets, this already proves
that n dominates (m,m,m). At (3,2) and (4,3), a balanced vector is impossible
by the finite census below. Therefore some coordinate is at least 2m, so
n dominates one of the three displayed profiles.

For (2,1), every correct word has at least four middle calls, regardless of
its number of outer calls. To see this directly, suppose there are exactly
two 2s. Let u and v be the counts of 1s preceding the first and second 2,
and let r and s be the counts of 3s following those 2s. Then

```text
N_12 = u+v,   N_23 = r+s,   N_13 = ur+vs.
```

The first two counts vanish in characteristic two, so u=v and r=s modulo
two. Consequently ur+vs=0. This contradicts c=1. The middle count is a
positive even integer, so it is at least four. Hence every feasible binary
vector dominates (2,4,2). This is a direct special-case proof of the
credited PR1662 middle bound, not a new binary lower bound.

All the exceptional minimal vectors are attained by these words:

```text
m=2, c=1: (2,4,2)  21232123
m=3, c=2: (6,3,3)  112113211323
          (3,6,3)  212232112233
          (3,3,6)  121332133233
m=4, c=3: (8,4,4)  1112113211123233
          (4,8,4)  2122232111222333
          (4,4,8)  1121323213332333
```

Each line is checked by the interval recurrence and independently by literal
dirty execution with noncommuting maps. For every other target PR4249's
balanced construction gives m occurrences of each letter. Its credited word is

```text
1^a 2 3^t 1^(m-2a) 2 1^a 2^(m-t-2) 3 2^t 3^(m-t-1),  at=c mod m.
```

For c<=m-2, use a=1,t=c. This also covers (3,1),(4,1),(4,2).
For c=m-1 and m>=5 except m=6, choose a unit 2<=a<=m/2 and
`t=-a^(-1) mod m`, so 1<=t<=m-2. Such a unit is a=2 for odd m;
a=m/2-1 for m divisible by four; and a=m/2-2 for m=2 mod four with m>=10.
The latter two are odd, and their gcd with m divides respectively two and
four. For (6,5), use the credited word `111122133232123233`.
Direct tracking in the displayed family gives

```text
N_12=m(m-1),  N_23=m(m-t),  N_13=at mod m.
```

Finally, appending m copies of any letter is an identity on all registers.
Starting from an attained minimal profile, this pads each coordinate by
any desired nonnegative multiple of m. This proves sufficiency for every
vector in Theorem 1, not merely the bounded vectors enumerated below. QED.

In characteristic zero the single-letter conditions force every count to
zero, so no unsigned word realizes a nonzero target. The zero target has the
empty optimum word and is outside Theorem 1's count classification.

## Exact tariff and optimal-word multiplicities

Write S=p1+p2+p3. Positive prices and Theorem 1 imply

```text
C(2,1) = 2S + 2p2
C(3,2) = 3S + 3 min(p1,p2,p3)
C(4,3) = 4S + 4 min(p1,p2,p3)
C(m,c) = mS otherwise.
```

Every optimum has a profile in P. Any strictly larger feasible vector costs
strictly more. Equal cheapest prices allow the corresponding minimal
profiles to tie. No arbitrarily long cheap-operation word can evade this
bound. The binary formula is the credited PR1662 theorem in this chain
model; the new cases are the complete characteristic-three/four alternatives
and the resulting all-characteristic count classification.

The exact numbers of words at the three single-doubling profiles, in order
(first, middle, last doubled), are

```text
(m,c)=(2,1):       (0,    4,    0)
(m,c)=(3,2):     (108,  180,  108)
(m,c)=(4,3):    (3520, 4288, 3520).
```

Thus in characteristic three the number of minimum-price words is
108 times the number of cheapest outer operations, plus 180 if the middle
operation is cheapest. In characteristic four replace 108 by 3520 and 180
by 4288. There are four binary minimum-price words for all positive prices.
These are finite exact counts, proved by the two exhaustive enumerations
below. They count literal words, without quotienting rotations or relabeling.

## Finite certificate and its completeness

The first engine fixes the counts (i,j,k) and stores a table indexed by
(d,e,f)=(N_12,N_23,N_13) modulo m. The single-letter residues are already
known from (i,j,k), so only m^3 entries are needed. The empty word initializes
one entry. A final 1 leaves (d,e,f) unchanged. A final 2 adds i to d. A final
3 adds j to e and d to f. Adding predecessor multiplicities gives every
literal word once, according to its unique final letter. The sum at each
count vector is checked against the multinomial coefficient.

For m=2,3,4, the engine covers every count vector in [0,2m]^3, for every
nonzero target residue. It compares nonemptiness to Theorem 1. This is
finite corroboration of the infinite count cone, not its universal proof.

The independent engine chooses the positions of the 1s, then those of the
2s among the remaining positions; the rest are 3s. It uses ordinary integer
pair and triple counts, then reduces only at the end. It exhausts the
balanced profile and all three single-doubling profiles. At the balanced
profiles, the possible restored target residues are {0}, {0,1}, {0,1,2}
for m=2,3,4. This proves the exceptional balanced exclusions. The two engines
agree on every residue multiplicity, not just nonemptiness or the headline
exception count. Each independent family has exactly
`binomial(i+j+k,i) binomial(j+k,j)` words.

An additional independent Dijkstra search on the full UT4(Z/m) group checks
all 64 integer price triples in {1,2,3,4}^3 for m=2,3,4 and every nonzero
target coefficient. Its 384 minima agree with the constructed tariff. This
search permits arbitrary word lengths and does not use the Pareto formula.
Positive weights ensure each settled state is processed once; at most three
relaxations per state bound the heap-removal loop by 3m^6+1.

All scientific checks use explicit errors and remain enabled under -O.
The verifier prints a generated receipt bound to every package file and live
input SHA-256. No receipt is handwritten. It writes no files.

## Implementation bounds

The verifier is standalone Python using the standard library. Control flow
is iterative. The count DP is restricted to 2<=m<=4, with at most 46,656
integer slots. Its independent census considers at most 900,900 words per
profile, each of length at most 16. Constructor checks use m<=32; exported
helpers reject m>128 and words longer than 1,536. Dense replay uses fixed
2x2 maps and four distinct two-coordinate registers. Functions remain below
60 physical lines, and every DP count has a multinomial invariant.

Power-of-ten rule 3 has a managed-runtime deviation: Python allocates integer
objects and temporary tuples during these bounded computations. The stated
finite domains bound live collections and integer bit lengths. The largest
DP total counts words of length 24 over three letters, hence is below 3^24.
The weighted oracle has at most 4^6=4,096 distance slots and 12,289
heap removals per run. There are no recursion, background tasks, dynamic
evaluation or external solver calls. Warnings-as-errors and the ordinary and optimized full replays
are the applicable interpreter checks. Ruff is not installed in the supplied
environment; no external static analyzer or type checker was run. An allocation-free implementation
would be needed only to embed the verifier in a runtime requiring fixed
allocation; it is not part of this finite certificate.
