# Independent projector-phase and isolated dirty-contact audit

## Scope and sources

This audit independently recomputes the complete phase inventory and
specified isolated contact word from Ross Richardson's PR4204 geometry,
at the frozen predecessor head identified by the enclosing source pins.
Its sole scientific data input is the unchanged GEOMETRY.json.gz with
SHA256 `353220f1edf3a3afda11cd5073c5e55446c23c242969b16a361fa53b8e45dd7e`.
The predecessor PROOF-CONTACTS, README and NOTICE supply the declared
model and attribution. No predecessor check_geometry/check_endpoints,
control/verify implementation, native compiler or other checker was read
or imported to implement this primary program.

The audit establishes, for the provided nine-dimensional port/contact
data, all recorded phase descriptors and every isolated contact boundary
on arbitrary dirty complex input fields. It does not reconstruct the
original P112 port set, canonical positive-C endpoint gauges or native
compiler recipes, execute B4 or the scheduling DP, or construct a
compatible shared many-edge caller. The native rank convention is the
retained rank of the phase's binary quadratic polar matrix; its physical
lowering and monomial wrappers remain predecessor/separate obligations.

## 1. Direct binary projectors and exact phase arrays

The ambient space is F2^9, with parity dot product. For an orthonormal
basis U, the binary projector acts by

    P_U x = XOR_(u in U, dot(u,x)=1) u.

The program forms all nine columns by applying that formula to the nine
coordinate unit vectors. It then obtains all 512 images by the linear
recurrence

    P(x) = P(x with its lowest set bit removed) XOR P(lowest unit bit).

The frame's exact character exponent is `wt(P(x)) mod4`. No signed-C
factorization routine or predecessor phase table generates these values.
For a norm-one vector q, its perpendicular cap has projector I+qq^T,
implemented as `x XOR q` when dot(q,x)=1 and x otherwise. The cap ranks
are independently checked to be eight.

At each supplied contact the five basic arrays are for the source line
P=p_s, target/helper entrance line Q=O p_t as supplied, common frame L,
source cap S=(O p_s)^perp and target cap T=p_t^perp. The program checks:

- Every encoded port and partner is a nonzero norm-one nine-bit vector,
  and each supplied port/partner pair is perpendicular.
- The contacts are exactly all 5,824 ordered perpendicular pairs of the
  supplied 112 ports, without duplicates or omitted legal pairs.
- The chosen L basis is orthonormal, contains p_s and the target partner,
  and is contained in both required public caps.
- The contact dimension is one for identical entrance lines, two for
  distinct perpendicular lines, and three for distinct nonperpendicular
  lines. The supplied dimensions occur 104, 2,912 and 2,808 times.

The dimension-three lower-bound reason is that two distinct norm-one
vectors with dot product one have Gram matrix all ones, with a nonzero
radical. Their two-dimensional span is degenerate. A nondegenerate
two-dimensional contact containing it is therefore impossible, whereas
the supplied orthonormal three-frame is a checked witness. No general
classification of other geometries is inferred from this finite family.

Transitions use literal subtraction of complete exponent arrays modulo
four, never a rank-only or hash-only symbolic operator. The eight recorded
phase IDs are independently matched in order to

    P, Q, L, S, T, S-P, T-Q, T-P.

All 8,880 inventory records are reached by those actual phase IDs. The
source's actual native transitions are also computed in full: their
distinct hashes are not all inventory keys. The combined serialized
inventory/native union has 22,547 distinct phase arrays. One additional
computed zero array is the unused identity preparation in the direct
rank-one case; it is labelled auxiliary rather than counted as a new
serialized operator.

Interning retains the complete 512-byte exponent tuple. Reusing one SHA256
key requires exact tuple equality and equal polar columns; a hash match
alone is never used as mathematical equality. The source compressed hash
is an immutable provenance binding, separate from this exact comparison.

## 2. Quadratic descriptors and native rank

For a complete exponent array e(x), the program recomputes its constant,
nine linear coefficients and binary polar rows directly from values at
zero, unit vectors and pairs of unit vectors:

    c = e(0),
    l_j = e(e_j)-c mod4,
    2 B_ij = e(e_i XOR e_j)-e(e_i)-e(e_j)+c mod4.

The last expression must be even, including diagonal i=j. The supplied
quadratic_rows are the symmetric polar matrix B, including its diagonal;
they are not merely the off-diagonal coefficients of a polynomial.
The program compares the entire independently reconstructed descriptor,
including SHA256, linear_Z4, constant_Z4 and native_rank, for every one
of the 8,880 inventory records.

To relate this to projectors, the elementary binary identity

    wt(a XOR b)=wt(a)+wt(b)-2 wt(a AND b)

gives the polar matrix of wt(Px) as P^T P. For these symmetric idempotent
projectors this is P. Subtracting two Z4 phase arrays adds their polar
matrices over F2. The program independently compares the reconstructed
polar with the directly formed projector difference and obtains ranks
by Gaussian elimination on binary image vectors.

Thus a nested transition has the exact retained native rank
rank(P_after+P_before). Its value equals the dimension difference for
the checked nondegenerate nested spaces. This statement does not require
an orthonormal basis of the residual complement: such a complement may
be alternating. It is a finite rank audit of the stated phase operator,
not a replay of a Clifford compiler or its monomial maps.

Every ordinary projector phase fixes character zero. Adding the constant
one to an entire exponent array multiplies its operator by global i,
while leaving the polar, native rank and relative linear coefficients
unchanged. The audit checks this explicitly and also supplies a physical
Gaussian witness for an actual contact with that mutation. Rank alone
cannot certify the phase convention.

## 3. Exact typed word and arbitrary helper dirt

The source serializes an ordered operation list for coefficient +1. The
program reconstructs and compares every dictionary in that list, including
ADD destination/source/sign, native field, role label, full phase-array
hash and rank. It does not trust a physical_helper_return Boolean as a
substitute for checking the helper operation. The Boolean, signed ADD
count, rank histogram and rank mass are compared only after reconstructing
the actual word.

For f=1, the checked arrays satisfy P=Q=L. The specified word is direct
`y += a x`, then source exit S-P on x and target exit T-Q on y, with h
an arbitrary unchanged spectator.

For f=2 or 3, the chronological word for a in {-1,+1} is

    y -= a h;
    x <- i^(L-P) x;
    y <- i^(L-Q) y;   h <- i^(L-Q) h;
    h += x;   y += a h;   h -= x;
    h <- i^(Q-L) h;
    x <- i^(S-L) x;   y <- i^(T-L) y.

Here each exponent is evaluated at the same actual character. This
notation is the diagonal spectral action of the complete convolution
operators, not an unpaid physical frame change at entrance. All three
entrance raw fields are arbitrary.

Write a character's entrance values as

    x=i^P X, y=i^Q Y, h=i^Q H.

The first ADD and preparations give `x=i^L X`,
`y=i^L(Y-aH)`, `h=i^L H`. The three middle ADDs then leave
`x=i^L X`, `y=i^L(Y+aX)`, `h=i^L H`. The literal helper return restores
`h=i^Q H`, equal to its original raw entrance. Public exits produce
the exact raw-coordinate block map

    [[ i^(S-P),          0,       0 ],
     [ a i^(T-P),  i^(T-Q),       0 ],
     [         0,          0,       1 ]].

In particular, logical cancellation before the helper return is not
physical restoration. No input column for helper dirt is discarded.

The primary program executes the chronological word as a 3-by-3 matrix
over Gaussian-integer pairs, using exact quarter-turns and signed ADDs.
It checks the three independent raw-field columns against the displayed
map for every actual edge, character and sign. For sign -1 this is a new
execution of the specified signed word; the frozen source operation list
itself records only sign +1. This is not a replay of the predecessor's
original controller or a claim that its full program was executed.

All 512 characters form a basis of the complex address-field vector
space. The frame operators are diagonal in that basis and scalar field
ADDs do not mix characters. Consequently equality on all three columns
at every character proves the full linear boundary on arbitrary complex
raw fields, rather than merely on selected Gaussian test vectors. The
normalized Walsh representation changes no eigenvalues; one can equally
use the unnormalized characters chi_x(z)=(-1)^(x dot z).

## 4. Complete enumeration and cache dependency closure

The audit visits all

    5,824 * 512 * 2 = 5,963,776

edge/character/sign instances, representing 17,891,328 independent
raw input-column instances. Every instance constructs its key from its
actual recomputed phase arrays, then verifies the cached actual matrix
against the cached expected matrix.

The pure scalar matrix-action cache key is exactly

    (contact case f, P(x), Q(x), L(x), S(x), T(x), sign a).

The word's branch depends only on f. Every native rotation exponent is
one of the displayed differences of these five values, and every ADD
coefficient is determined by a or the fixed +/-1 constants. The expected
map has exactly the same dependency closure. No port identifier, basis,
unrecorded phase, source helper value or mutable state is used by either
pure function. Therefore equal keys imply identical complete matrix
calculations. The run computes 272 distinct cached scalar matrices; it
does not pretend to execute almost six million distinct matrix programs.
All almost-six-million actual instances are nevertheless enumerated and
checked, after the complete typed source binding for each edge.

Separate caches for projectors and phase transitions store complete
arrays and verify their exact equality when interned. The full 8,880
inventory reconstruction covers 4,546,560 exact exponent bytes, while
the larger serialized native-transition union is also explicitly formed.
The caches are finite computation reuse, not sampling of contacts,
characters, signs or dirty columns.

The replay writes nothing unless `--output` is supplied. Registered
commands can pass `--expected RESULT.json` to compare the entire freshly
computed structured receipt with the frozen one, including every count,
cache domain and concrete control witness. Such receipt equality is an
integrity/reproduction check; the full recomputation still occurs first.

## 5. Isolated invoice and concrete defect controls

Reconstructed native occurrence histograms and signed ADD counts are

| f | Native histogram | Rank mass | Signed ADDs |
|---|---|---:|---:|
| 1 | {7:2} | 14 | 1 |
| 2 | {1:4,6:2} | 16 | 4 |
| 3 | {2:4,5:2} | 18 | 4 |

Every helper preparation and return occurrence is charged, even when
its phase recipe equals another occurrence. The helper remains a full
arbitrary 512-coordinate field. A small native transition rank does not
imply reduced helper storage. The audit compares 57,512 serialized
ordered operations and 34,528 native occurrences over all contacts.

Four defective chronological words are actually evaluated: omitted
helper return, omitted dirt precompensation, wrong delivery sign, and
a uniform global-i source-exit shift. Each must produce a concrete
differing Gaussian output coefficient at some supplied contact,
character, input field and output field. The receipt records the
actual and expected Gaussian integers, not just an exception.

These coefficients are also genuine raw physical witnesses: place the
unnormalized character chi_x, with amplitude one, in the recorded input
field and zero in the other two fields. Every raw coordinate of that
input is +/-1, hence a Gaussian integer. At raw address z=0 the
character is one, so the listed actual/expected coefficients are the
actual/expected raw output values. This avoids treating a normalized
Walsh unit column with irrational entries as a Gaussian input.

The polar/rank test deliberately accepts the unchanged polar of the
global-i mutation; the exact phase/boundary control rejects it. All
operators in this spectral contact model commute as diagonal address
operators. These scalar tests do not claim to distinguish inverse order
for arbitrary noncommuting operators; any separate noncommutative oracle
has its own scope.

## Attribution and remaining obligations

Ross Richardson owns the retained paired-endpoint/order-three geometry,
isolated dirty-helper word and paid-return result, with substantial
OpenAI Codex assistance. Preserve the PR531/kernel92/PR533 and signed
PR425/433/523/531 lineage and the source NOTICE's credit to icekylinx,
chafreaky, Rohan Arun, DreamingOfClouds, Dugongue, eumemic and earlier
geometry/compiler contributors. This package adds a code-disjoint
projector/character recomputation, typed-word binding and explicit
Gaussian witness audit. It does not claim priority for the underlying
projector, Fourier, dirty-helper subtraction or binary linear algebra
identities. Substantial OpenAI Codex assistance; Apache-2.0. No human
review or formal-kernel verification is claimed.

## Open next questions

- Combine contacts only with an explicitly compatible chronological
  shared source/target/helper history and a complete paid invoice.
- Independently audit canonical endpoint gauges, actual native compiler
  lowerings, monomial maps, original ports, B4 and the finite scheduling
  DP if those additional predecessor claims are needed.
- Physical storage/access, complete helper ownership, precision, global
  power moments and the multiplication theorem remain separate.
  No selected frontier or kappa value changes here.
