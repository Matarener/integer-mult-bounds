# A two-frame obstruction for nine canonical delivery channels

Prepared for Nicholas with substantial OpenAI Codex assistance, 2026-10-27.
Apache-2.0. This is a scoped mathematical argument with an exact finite
certificate, not independent human review or proof-kernel verification.

## 1. Contract and relation to other work

Fix the source, canonical ground-to-frame delivery, immutable original-mode
payloads and common-fixed-vector scalar quotient of Ali Romman's PR5745 at
`e82b64e91e57c838ff2028bcf2219203966bf9ed`. Retain arbitrary rational scatter
and arbitrarily many contacts in one fixed frame for each channel. Preserve
all main and Y outputs. Quotient only helpers whose original frame is ground,
as in that predecessor. The original mode matrix R satisfies RR^T = 56 I8.

Let D be the eight-dimensional output subspace spanned by the desired main
mode vectors R^T, with all other retained outputs zero. For frame g, let S_g
be the span over Q of all its endpoint impulse responses, over every time in
the fixed word. Any one-frame immutable channel has a response in S_g.
Arbitrary scatter and availability are granted, so a negative result in this
model also applies to a more restrictive chronological implementation.

Write r(g) for the canonical transport grade. On this source it is the
dimension of the recorded binary frame. A positive-grade delivery costs H_r,
where H_r is positive and nondecreasing. Ground delivery may be granted free.
No concavity or power-law assumption is made in the theorem below.

PR5745 proved the 8 H8 lower bound for at most eight channels and for any
number of individually clean channels. PR5755 gives a different rank-one
channel bound. During the final overlap search we also found PR5823, head
`0893a8f9b10a8134bd556bf458c0b9563841b83e`, which proposes the bound for
any finite channel count under H_r = r^q H1, 0 < q <= 1. Its full certificate
was not replayed here. The present result covers at most nine channels under
the broader class of nondecreasing tariffs, with a different pairwise
certificate and a separately implemented response census. It must not be
presented as the first solution for power tariffs or as leaving that entire
finite-channel question unanswered.

## 2. Source-bound two-frame lemma

For every pair of available frames g,h with r(g),r(h) < 8, including g=h,

    (S_g + S_h) intersect D = {0}.                         (1)

This is the new finite, source-specific certificate. It is stronger than
requiring S_g intersect D = {0} for each individual frame.

Split output vectors into mode and nuisance components. Any rational
projection onto D supplies such a direct-sum decomposition. For example,
for main output x use m=Rx/56 and nuisance x-R^T m, and retain Y and the
non-ground-helper outputs as nuisance. The restriction of the nuisance map
to each low-grade S_g is injective because S_g intersect D is zero.

In exact row elimination, nuisance coordinates precede mode coordinates.
A pivot in a mode coordinate is precisely a nonzero clean response. First
reduce each S_g. Then reduce every S_g+S_h. If their nuisance pivot sets are
disjoint, no nonzero vector can belong to both nuisance images: the leading
coordinate of an intersection vector would have to be a pivot of both.
Such a pair cannot acquire a new clean response. All other pairs are reduced
explicitly, with rational arithmetic and no coefficient cutoff.

The certificate covers 879 nonzero low-grade temporal response spaces:

| Grade | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Frames | 1 | 115 | 169 | 168 | 66 | 46 | 146 | 168 |

There are 385,881 different-frame pairs and 879 same-frame cases. The
predecessor-coordinate calculation reduces 57,550 pairs explicitly and
disposes of 328,331 by disjoint nuisance pivots. Exactly 3,782 pairs have
nonzero nuisance intersection; none has a nonzero clean response.
Frames with no retained endpoint response cannot help any correction.

## 3. Nine-channel rank argument

Absorb target signs and normalization into the payload coefficients. For k
channels write their response columns as V=(M;N), with mode matrix M and
nuisance matrix N. A complete correction is equivalent to some k by 8 matrix
B satisfying

    M B = I8,       N B = 0.                              (2)

Hence rank(B)=8 and rank(N) <= k-8.

For k<8, (2) is impossible. For k=8, N=0; each nonzero response is clean,
so at least eight channels have grade at least eight. This also handles k=9
with N=0: rank(MB)=8 requires at least eight nonzero clean columns.

Now take k=9 and rank(N)=1. The column space of V contains D by (2), and
also contains a nonclean column, so rank(V)>=9. Since V has nine columns,
rank(V)=9: all nine response columns are linearly independent.

Suppose two columns v_i,v_j use grades below eight. Neither can be clean,
by (1) with g=h, and neither can be zero, by independence. Their nuisance
columns are therefore nonzero multiples alpha_i n, alpha_j n of the same
nuisance vector. The vector

    alpha_j v_i - alpha_i v_j

is nonzero by independence, has zero nuisance, and belongs to S_g+S_h.
This contradicts (1). Thus at most one channel has grade below eight.
At least eight channels have grade at least eight, and therefore

    total canonical delivery charge >= 8 H8.              (3)

This proves (3) for every k<=9, including repeated frames, arbitrary
same-frame temporal reuse and joint nuisance cancellation. The eight-channel
attainment already supplied by PR5745 shows that the minimum among all
at-most-nine-channel schemes is exactly 8 H8. No new physical attainment
is constructed in this package.

## 4. Independent computational check and controls

The first route reuses PR5745's authenticated cuts.py and inputs.py. Its only
in-memory instrumentation exposes the already-computed temporal bases in
the return value; it changes no arithmetic or event selection. It reproduces
the original 5,331 states, 3,963 projected columns and 5,715 temporal
observations. The predecessor's own clean-response counts agree as well.

The second route, independent.py, does not import predecessor executable
code. It walks all 22,585 source events, observes each changed adjoint field
column and uses the orthogonal mode projector m=Rx/56 instead of the
predecessor's selected-coordinate left inverse. It processes 15,752 nonzero
low-frame contacts, 14,816 distinct frame/column pairs and 12,240 distinct
raw columns. Undoing both projections gives exactly the same S_g for every
one of the 879 frames, checked by exact subspace inclusion and dimension.

Under the second coordinate system 280,364 pairs need explicit elimination;
105,517 have disjoint pivots. It independently obtains the same 3,782
nonzero nuisance intersections and zero clean pairs. Both routes use Python
Fraction arithmetic. They share the pinned source data and mathematical
scalar-quotient premise; this is not independent human review.

Controls verify detection of two-channel cancellation, rejection of false
cancellation between independent nuisance coordinates, and accumulation of
cancellation across different times. A ten-channel abstract positive control
demonstrates the exact boundary of the argument: three low-channel responses

    (n1;0), (n2;0), (n1+n2;e1)

have zero clean intersection for every pair, yet their combination with
coefficients (-1,-1,1) produces e1. Seven clean columns e2,...,e8 complete
the target. This example is not asserted realizable in the fixed source;
it shows why the pair lemma alone does not settle k>=10.

## 5. Consequences and remaining scope

Nine channels cannot save any canonical paid allowance relative to the eight
removed H8 calls. Extra nonnegative gathering, restoration and ordinary
charges cannot create a paid saving that already fails this relaxed test.
The comparison does not assert that every equal-paid implementation has the
same ordinary-operation bill, or re-run the physical word of PR5745.

This proof does not address ten or more channels under arbitrary monotone
tariffs. For the project-specific concave power tariffs, see the separately
published PR5823 result, whose full computational certificate remains
outside this package's validation. Changed words, moving frames, changed
native/address contracts and payloads recomputed from changed live data are
outside the fixed contract. No multiplication exponent improvement follows.

## References and attribution

- Ali Romman, PR5745, https://github.com/CrocSwap/integer-mult-bounds/pull/5745
- flyingviper, PR5720, https://github.com/CrocSwap/integer-mult-bounds/pull/5720
- flyingviper, PR5755, https://github.com/CrocSwap/integer-mult-bounds/pull/5755
- Ali Romman, PR5823, https://github.com/CrocSwap/integer-mult-bounds/pull/5823
- Retained source authors: Cao Yifan, Cinna Davis, Dugongue, and all original
  native/mode/controller contributors and notices in the unchanged archive.

The original mode matrix, source word, canonical delivery model, scalar
quotient, clean-channel theorem and eight-channel attainment are predecessor
work. New work here is the two-frame certificate, nine-channel consequence,
orthogonal all-event check, and explanatory boundary controls.
