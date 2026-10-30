# Fitting rank for odd binary types

I first use the standard binary dot product on V=F2^d, with d=5 or 6. Write
O={x:x dot x=1} and j=(1,...,1). An admissible type is a pair (q,w) in
O times O with w dot q=1. A port list may contain any finite multiplicities
of these types. For its v distinct port positions I define the binary mask

    B_st = w_s dot q_t.

I call a v-by-v matrix N over a field K fitting if N_ss is nonzero and
N_st=0 whenever s is different from t and B_st=1. I interpret the binary
entries as zero or one in K. I make no assumption that N is symmetric,
positive, integral, or has a prescribed factorization.

I prove, over every coefficient field K,

    d=6: rank_K N >= ceil(3v/32),
    d=5: rank_K N >= ceil(v/9).

These statements require the odd-type representation above. They are not
bounds for arbitrary binary matrices of rank five or six.
Section 5 extends the selector argument to every ambient dimension d>=2.

## 1. A triangular selector

Let a=e_0 and let W be the odd vectors with coordinate zero equal to zero.
For d=6, order W as follows, using binary integers for vectors:

    2,4,8,14,16,22,26,28,32,38,42,44,50,52,56,62.

For d=5 use its first eight entries. Equivalently, take e_1 plus the
subsets of (e_1+e_2,...,e_1+e_(d-1)), in binary subset order. For the
ordered sinks w_0,...,w_(2^(d-2)-1), select the types

    S_k = {(q,w_k): q in O, q dot w_i=1 for every i<=k}.

List the blocks S_k in increasing k, with any fixed order inside a block.
For d=5 append the type (j,j). Call the resulting ordered selector S.

For a row from block i and a column from block k>=i, their mask entry is
one by construction. Within each block all mask entries are one. The
appended d=5 column also has mask entry one against each preceding row,
because those sinks are odd. A fitting principal matrix on S is therefore
lower triangular with nonzero diagonal.

The same conclusion holds when I include every port occurrence of each
selected type. Distinct copies force zero cross entries because their
mask entry is one. Thus, if n_t is the multiplicity of type t,

    rank N >= sum_(t in S) n_t.                         (1)

The prefix sink ranks are 1,2,3,3,4,4,4,4,5,...,5. The vector j is
independent of their span: a dot j=1 while a annihilates W. The equations
q dot j=1 and q dot w_i=1 therefore have rank r+1 for a prefix of rank r.
They are consistent: each linear relation among the odd w_i uses an even
number of them, so the prescribed right sides satisfy that relation.
Independent linear forms give every remaining right side. Each block
therefore has 2^(d-r-1) labels q. I obtain:

| d | Prefix block sizes | Added type | Total |
|---|---|---|---:|
| 6 | 16,8,4,4,2,2,2,2,1,1,1,1,1,1,1,1 | none | 48 |
| 5 | 8,4,2,2,1,1,1,1 | (31,31) | 21 |

I count diagonal types (2,2),(14,14),(62,62) in d=6. In d=5 I count
(2,2),(14,14),(31,31). The executable certificates check these lists,
the complete selector and every triangular mask entry.

## 2. Symmetry and multiplicities

Binary isometries act on both components of a type. I also allow the
exchange (q,w) -> (w,q). Isometries preserve B; exchange transposes B.
The image of S therefore gives either a lower- or an upper-triangular
fitting principal matrix. Inequality (1) holds for each such image.

For d=6, the isometry group is transitive on the 32 odd vectors. To see
this, fix an odd q. Its orthogonal complement has characteristic vector
j+q of norm one; the orthogonal complement of that vector inside q-perp
is a nondegenerate alternating four-space. Choosing a symplectic basis
there gives the same orthogonal decomposition for any odd q. The
stabilizer of q acts transitively on the 15 nonzero vectors in that
alternating space. Every distinct odd w with q dot w=1 has the form
w=q+x for one of those 15 vectors. Thus admissible types have two orbits:
32 diagonal types and 480 cross types. S contains three and 45 respectively.

For d=5, j has norm one and V is the orthogonal sum of span(j) and a
nondegenerate alternating four-space H. Write q=j+x and w=j+y. The
admissibility equation is x dot y=0. Symplectic basis extension and
source/sink exchange give the following four orbits:

| Orbit | Description | Size | Selected |
|---|---|---:|---:|
| special | x=y=0 | 1 | 1 |
| one-special | exactly one of x,y is zero | 30 | 8 |
| diagonal | x=y nonzero | 15 | 2 |
| cross | x,y nonzero and distinct, x dot y=0 | 90 | 10 |

For the last row, each of 15 nonzero x has six nonzero orthogonal choices
y different from x. Any such pair extends to a symplectic basis. The
finite checkers also reconstruct these orbits from explicit isometries,
using different generator families.

Average (1) over the finite symmetry group. A type in an orbit A occurs
in a uniformly chosen image with probability |A intersect S|/|A|. I average
integer cardinalities as rational numbers, not matrices over K, so the
argument also covers fields whose characteristic divides the group order.
For d=6 both fractions equal 3/32. Hence rank N>=3v/32.

For d=5, write v_special, v_one, v_diagonal and v_cross for occurrence
counts, including repetitions. I obtain the stronger inequality

    rank N >= v_special + (4/15)v_one
              + (2/15)v_diagonal + (1/9)v_cross.        (2)

Every coefficient in (2) is at least 1/9, proving the stated uniform
bound. Taking ceilings is valid because rank is an integer.

## 3. Copy terms and linear rank slack

In the retained unit model, write N=sum_(l=1)^J r_l a_l^T. Define

    X_l = diag(r_l) B_lift diag(a_l),
    beta_l = rank_F2 B[supp(r_l),supp(a_l)],
    C = sum_l beta_l.

A term of charge zero has an all-zero mask rectangle, so its X_l is
zero. I may remove such terms and form a new fitting N from the remaining
terms. The new N still has rank at most their number J. I apply the rank
bound to this N; free terms cannot inflate the count needed below.

If every remaining beta_l is five, then in dimension six

    J >= ceil(3v/32),
    C >= 5 ceil(3v/32) >= (15/32)v.

The ratio 15/32=.46875 exceeds the source's .45 screen by 3/160. This is
a lower bound for the beta-five-only class. Lower-charge mixtures do not
inherit C=5J, and I make no claim that the complete small-unit lane is closed.

If each X_l has rational rank 16, the total rank satisfies

    sum_l rank X_l = 16J >= 16 ceil(3v/32) >= 3v/2.    (3)

Thus such a complete unit needs at least v/2 aggregate rank slack. This
conclusion does not assume that the totals are idempotent. It uses the
fitting mask; it is not an extension of the predecessor's invalid
homogeneous per-total trace rows.

For the proposed literal identity sum of rank-16 idempotents over a
characteristic-zero field, taking traces gives v=16J. This contradicts
(3) for v>0. Hence full-rank orbit-77 projectors alone cannot resolve I_v,
even with independent diagonal gauges, repetitions, either orientation
and arbitrary port multiplicities. The same contradiction applies to an
explicitly rank-additive assembly over any field.

Identity is essential to the trace corollary. A general fitting unit has
B_lift .* N=D with an arbitrary nonzero diagonal D. Row normalization
preserves fitting rank and support costs, but it may destroy individual
idempotency. I do not use it to convert an arbitrary idempotent sum D into
the identity case. The cost and rank-slack bounds themselves require only
the nonzero fitting diagonal.

## 4. Paired windows and remaining scope

For a bit twin whose actual window is h_b=rank_Q N, the bounds imply
v<=9h_b in dimension five and 3v<=32h_b in dimension six. In particular,
h_b<=5 permits at most 45 and 53 ports respectively; (2) can tighten the
first restriction. The previous source rows were v<=16h_b and v<=17h_b.
I do not replace the bit twin's copy invoice by the complex invoice.

The retained rank-16 projector remains valid as a local example. Its
rank-one scalar factor does not fit the complete unit mask. The checker
verifies its exact factor identity and rejects that attempted promotion.

I leave lower-rank totals, mixed charges, sufficiently non-additive
assemblies and changed label/mask contracts open. I supply no native
producer, complete supplier, selected-frontier update or new multiplication
exponent. The proof uses the explicit finite geometry above for a theorem
over arbitrary finite multiplicities; the bounded replays corroborate its
finite ingredients and failure controls rather than exhaust its quantifiers.

## 5. General ambient dimension

I now take any integer d>=2 and retain the same odd-type and fitting
conditions. I use the ordered affine flag from section 1 in the odd
hyperplane e_0-perp. The first sink contributes 2^(d-2) types. For each
prefix rank r=2,...,d-1, I have 2^(r-2) sinks, each contributing
2^(d-r-1) types. Thus the prefix selector has d*2^(d-3) types. For d=2
this expression equals one and there are no higher-rank prefixes.

For completeness, write the subset index as m. The sink w_m has low
coordinate 1+wt(m) modulo two and higher coordinates m. To select its
diagonal type, its pairing with w_0 forces wt(m) even. Pairing with all
earlier sinks then requires every bit through the highest bit of m to
be one. Hence m=2^(2t)-1, including m=0. I obtain d/2 diagonal types
when d is even and (d-1)/2 when d is odd.

For even d, the odd-vector stabilizer uses a nondegenerate alternating
space of dimension d-2, as in section 2. The admissible type orbits have
the following sizes and selector counts:

| Orbit | Size | Selected |
|---|---:|---:|
| diagonal | 2^(d-1) | d/2 |
| cross | 2^(d-1)(2^(d-2)-1) | (d/2)(2^(d-2)-1) |

At d=2 I omit the empty cross orbit. Both nonempty orbit fractions equal
d/2^d. The same multiplicity argument proves, over any coefficient field,

    d even, d>=2: rank N >= ceil((d/2^d) v).            (4)

For odd d, I append (j,j) and use the alternating space j-perp of
dimension d-1. Put t=2^(d-2) and n=2t-1. The four-orbit table becomes:

| Orbit | Size | Selected |
|---|---:|---:|
| special | 1 | 1 |
| one-special | 2n | t |
| other diagonal | n | (d-1)/2 |
| cross | n(t-2) | ((d-2)t-(d-1))/2 |

I count the one-special entries by taking q=j for each of the t prefix
sinks. At d=3 the cross orbit is empty and the other fractions give
rank N>=ceil(v/3). For odd d>=5 the cross fraction is

    rho_d = ((d-2)t-(d-1)) / (2n(t-2)).

I have t>d-1 for d>=5: it holds at d=5, and increasing d by two
multiplies t by four while increasing d-1 by two. Direct comparison
then gives rho_d <= (d-1)/(2n) <= t/(2n) <= 1. Thus

    d odd, d>=5: rank N >= ceil(rho_d v).               (5)

The stronger weighted bound uses the four individual orbit fractions.
Equations (4) and (5) recover the source cases 3/32 and 1/9. They concern
the same odd-type fitting model; no new native-cost or supplier conclusion
follows from changing the ambient dimension alone. `general.py` checks
the finite geometry for d=2,...,8 and the formula's edge cases. The
general proof uses the affine ranks and symplectic decompositions above,
not extrapolation from that replay.

Writing rho for the applicable uniform coefficient, the same rank-one
factorization argument gives J>=ceil(rho v). Constant-charge beta terms
therefore cost at least beta*ceil(rho v). Constant-rank R masked totals
need aggregate rank at least R*ceil(rho v). A literal identity sum of
rank-R idempotents over characteristic zero can exist only if R*rho<=1.
For example, in dimension five the charge-five-only floor is 5/9, and
rank-15 idempotents alone cannot resolve I_v. These are necessary tests
under the fitting model, not constructions or complete supplier prices.
