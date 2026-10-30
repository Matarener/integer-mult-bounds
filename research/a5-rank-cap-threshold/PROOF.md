# Sharp rank cap for the A5 conjugate-pair word

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let K be any field and V any finite-dimensional K-vector space. Work in the
full formal matrix algebra End_K(V)[A5], with scalar operators commuting with
group basis elements. Set x=(12)(34) and y=(135), with right-to-left permutation
composition. Let P,Q be nonzero idempotents with PQ=QP=0, of ranks r,s.
All of V has arbitrary initial data; the complementary space is restored.
For each g in {x,y}, one paid call is

```text
F_g(N) = I + ([g]-[e])N,      N^2=N,      1 <= rank(N) <= h.
T = I + ([xy]-[e])P + ([yx]-[e])Q.
```

Let h be a positive integer with h >= max(r,s). The exact minimum number
of paid calls for T is

```text
3, if h >= r+s;
4, if max(r,s) <= h < r+s.
```

This holds with any finite number of additional restored dirty roles and with
arbitrary free scalar GL(V) maps. It counts paid calls only. It assigns no
physical or recursive price to a higher-rank call or to scalar mixing.

## Attribution and new step

Wentao Li's #4089 proves the binary r=s=h=1 case at arbitrary role count,
following Cinna Davis's #2246 finite-width result and question. In particular,
the support filter and the forced middle matrix P+Q in that special case
are predecessor ideas. We cite them without replaying their implementations.
The new step changes the paid alphabet: higher-rank idempotents are legal.
It gives the exact three/four-call transition for arbitrary r,s over every
field, together with an attaining three-call construction. It does not claim
that the rank-one lower-bound method or coordinate batching is new.

## Free scalar maps

Move any scalar GL(V) maps through the paid factors by conjugation.
Conjugation preserves idempotence and rank. The group-algebra augmentation
maps each [g] to 1, hence sends each paid factor and T to I. Therefore the
residual scalar map is I. A normalized paid word suffices for the lower bound;
the literal scalar maps and their physical costs are not classified.

## Support lower bound

Every group label in a product expansion is an ordered subsequence of its
paid labels. No word of length at most two has both xy and yx in its support.
Among the eight length-three words over {x,y}, only xyx and yxy do. This is a
finite permutation statement for these particular x,y, independent of K and
V. The verifier checks all fifteen label words of length zero through three
by expanding every ordered subsequence. Since P and Q are nonzero and xy,yx
are distinct group elements, T requires both coefficients. Thus at least
three paid calls are necessary. A direct hand check of the full-length
products is xxx=x, xxy=y, xyy=xy^2, yxx=y, yyx=y^2x and yyy=e for the six
nonalternating words. Their proper subsequences contain at most one of xy,yx;
direct permutation multiplication gives xy^2 != yx and y^2x != xy.
The two alternating words contain both xy and yx as length-two subsequences.

## Every three-call word pays middle rank r+s

Consider F_x(A)F_y(B)F_x(C). Write each factor as (I-N)+[g]N.
The labels xyx, xy, yx and y have the following coefficients:

```text
[xyx]  ABC
[xy]   AB-ABC
[yx]   BC-ABC
[y]    B-AB-BC+ABC.
```

These four group elements are distinct; xyx and y are absent from T.
Matching coefficients gives ABC=0, AB=P, BC=Q, and then B=P+Q.
All identities use integer coefficients and subtraction only, so they hold
in every characteristic. We did not assume that A,B,C are idempotent or
that any factor is invertible in this necessity argument.

For F_y(A)F_x(B)F_y(C), use the distinct labels yxy, xy, yx and x:

```text
[yxy]  ABC
[xy]   BC-ABC
[yx]   AB-ABC
[x]    B-AB-BC+ABC.
```

They give ABC=0, BC=P, AB=Q and again B=P+Q.

Because P,Q are orthogonal idempotents, V is the direct sum of im P,
im Q and ker P intersect ker Q. The map P+Q is identity on the first two
summands and zero on the third. Hence rank(B)=rank(P+Q)=r+s. A cap below r+s
therefore excludes every three-call implementation, including arbitrary
noncoordinate couplings and restored spectators.

## Attainment

The direct four-call word is

```text
F_x(P) F_y(P) F_y(Q) F_x(Q) = T.
```

Each coupling has rank r or s, so it is legal for h>=max(r,s).
When h>=r+s, the shorter word is

```text
F_x(P) F_y(P+Q) F_x(Q) = T.
```

On im P it acts by xy; on im Q it acts by yx; on the common kernel it is
identity. P+Q is itself idempotent. Its ranks are r,r+s,s, so every call
is legal exactly at the stated sufficient cap. The reversed alternating
word F_y(Q)F_x(P+Q)F_y(P) also attains T. These are full operator identities,
not target-row observations or finite-column assumptions.

Both the four-call word and the three-call word have total coupling rank
2(r+s). Thus one paid-call overhead disappears at this rank threshold, but
the proof makes no claim of lower total rank mass, native speed or kappa.
Together with the lower bounds this proves the theorem. Stop here.

## Limits

The theorem requires full formal group-algebra equality, these two labels,
orthogonal idempotent target blocks and h>=max(r,s). It does not determine
the optimum when a target block itself exceeds the cap, a minimum under an
arbitrary rank-dependent tariff, or a physical implementation cost. The
necessity proof applies even to non-idempotent paid couplings, but the
specified legal alphabet and the attaining constructions use idempotents.
Independent human and formal proof-kernel review are unclaimed.
