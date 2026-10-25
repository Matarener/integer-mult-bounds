# An exact width gate for one two-FULL caller

This is a source-specific negative result. It concerns a literal exact integer
representation and a uniform width tariff. It does not exclude every exact
implementation, every BIT controller, or the two-FULL idea itself. It gives no
new kappa.

## Declared model

Use the retained round-three source at base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. Its decompressed payload SHA256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The two calls use the forward and backward source orientations. Each call keeps
all 632 persistent roles, 408 independent helper inputs and outputs, and the
single reused owned center C0. Each orientation has 3,298 paid occurrences.
The two helper banks are distinct.

The caller is read from right to left:

```text
S_e D2 U(Q) D1 L(-Q^-1) B S_e^-1,
B = [[1,-1],[1,0]],    S_e = diag(1,e),    e = 2^-k.
```

Q is the common one-axis Gaussian. D1 and D2 act on separate fresh eight-axis
blocks. The operators and the retained boundary maps are ideal and exact.
The source charts and the declared target invoice are inherited from
[PR #4966](https://github.com/CrocSwap/integer-mult-bounds/pull/4966).
No independent operator errors are introduced.

The width policy has four premises:

1. At each paid occurrence, store the full exact register value as integer
   numerators. A fixed denominator or one shared exponent is permitted.
2. Choose that occurrence's width before the data is known. It must hold for
   every permitted input at that occurrence. Different occurrences can have
   different widths.
3. The raw invoice funds leading width `k+o(k)` at each occurrence. The leading
   recursive charge is linear in this width.
4. Take `k -> infinity` at fixed native rank and fixed fiber/column
   multiplicity f. A separately funded width comparable with k is outside
   this comparison.

The multiplicity f is fixed as well as the rank. A tensor frame can add a
denominator-width offset of order f. Thus this proof does not infer the same
leading charge when f grows with k. No growing-multiplicity limit is claimed.

These are cost-model premises, not conclusions about every arithmetic method.
In particular, the sum below is a sum of uniform site charges. A separate
worst-case witness for each site does not prove the same sum for an adaptive
per-input width policy.

## The two-band lemma

Let p and q be fixed, nonzero dyadic rational numbers. Let

```text
c = max(0, v2(p) - v2(q)).
z(A,B) = p A / 2^k + q B,
0 <= A < 2^(k-c),    0 <= B < 2^k,    k > c.
```

There are exactly `2^(2k-c)` distinct values z. For if two values are equal,

```text
p (A-A') = -2^k q (B-B').
```

If `B=B'`, then `A=A'`. Otherwise the 2-adic valuation gives
`v2(A-A') >= k + v2(q) - v2(p) >= k-c`. Thus `A-A'` is a multiple of
`2^(k-c)`. Its absolute value is smaller than this number. It is zero, and
then `B-B'` is zero. This proves injectivity for every integer `k>c`.

Any injective exact encoding of this scalar range needs at least `2k-c`
information bits. This is a classical counting argument applied to the two
independent source amplitudes. It is not a new general information theorem.

For literal integer numerators, a shared exponent cannot remove the leading
width. Write `p=2^a u` and `q=2^b v`, where u and v are odd integers. Take
`A=1` and `B=2^(k-1)`. For all sufficiently large k,

```text
z = 2^(a-k) [u + v 2^(2k-1+b-a)].
```

The quantity in brackets is an odd integer. Its bit length is `2k-O(1)`:
the nonzero second term has this bit length and the first term is fixed.
For `k>a`, the displayed numerator is already reduced. Any other integer
numerator for the same dyadic value, with a power-of-two denominator, is at
least as wide. A common exponent for more than one component can add zeros;
it cannot shorten this reduced numerator. Thus a uniform literal numerator
width at this site is at least `2k-O(1)`.

Multiplication by a fixed nonzero Gaussian dyadic vector preserves the number
of distinct values. At least one real or imaginary component is a fixed
nonzero dyadic multiple of z, so the same leading numerator bound holds there.
At fixed multiplicity, boundary denominators change only the constant term. They are not
set to zero or granted for free.

## Binding the lemma to the source

The live dependency
`research/two-full-border-paid-precision/independent-review/invariance/check_invariance.py`
checks every one of the 42,898 source events. It checks all common-frame scalar
contacts, paid frame changes, warp incidences, final frames, owned-center
rules, and boundary markers. It verifies all 72 binary warp matrices and all
four signed/oriented zero-address phases.

Under its inherited exact moving-frame semantics, a paid transition changes
the physical frame and leaves the logical value unchanged. Each logical warp
has a homogeneous binary address map and a quadratic phase with no constant
term. It fixes `delta_0` with phase one. The `phase` records are section labels.
Boundary adapters change the physical reference, not the logical value.
The audit retains the 82 early, identity X-exit markers per orientation. It
does not silently assume that these markers occur in their final frame.

It follows by induction that logical multiples of `delta_0` follow the exact
rational scalar program. This is a logical-frame invariant. It does not say
that every physical map fixes physical `delta_0`. The inherited interpretation
of the primitives as exact Gaussian operations is not a new physical replay.

Set the original main X input to zero. The first call has a main input channel
scaled by `e^-1`. At one port, a suitable original Y input is a scalar multiple
of `Q delta_0`; it makes source logical X a multiple of `delta_0` and logical
Y zero. For the second call, use a scalar multiple of `Q D1^-1 delta_0`.
It makes both source logical main inputs equal multiples of `delta_0`, up to
a common sign. These are the retained unitary boundary substitutions from
PR #4966. Each is a separate allowed input choice.

Choose that main amplitude as B after the `e^-1` scaling. The original main
amplitude is then `B/2^k`. Choose one fresh helper input in that call's entrance
frame with logical amplitude `A/2^k`. The helper boundary has no e factor.
The two amplitudes vary independently. Other input channels can be zero.
A fixed rescaling puts their joint norm below one if required and leaves the
leading width bound unchanged.

For each source orientation, the new checker propagates 520 independent
columns: 112 main channels in this restricted caller pattern and all 408
helper inputs. It checks the complete endpoint on this subspace and every
helper return. This is not a new full 632-input endpoint proof.
Immediately before each paid occurrence, it records the first nonzero main
coefficient q and helper coefficient p, when both exist. The logical value
on this input slice is `p A/2^k + q B`. The physical frame is invertible, so it
does not identify two such values.

The census gives:

| Source orientation | H1 | H2 | H3 | H4 | H5 | H8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Forward | 1587 | 258 | 362 | 70 | 28 | 8 |
| Backward | 1576 | 148 | 380 | 95 | 12 | 0 |
| Total | 3163 | 406 | 742 | 165 | 40 | 8 |

The certificate contains all 4,524 witnesses, with source event, owner, input
indices, exact coefficients and c. In all of them, `c<=2`. A single input is
not claimed to maximize all these occurrences. The uniform site-width premise
is what permits the sum of their separate required widths.

## Complete declared invoice

Both source calls retain all their productive helper targets. Their combined
helper profile is twice `{4:28,7:7,8:47,9:326}`. The declared main target adds
224 rank-17 outputs. The disjoint-axis splits are `4=3+1`, `5=3+2` and
`8=3+3+2`. They give:

```text
targets        = {4:56,7:14,8:94,9:652,17:224}, mass 10750;
raw paid       = {1:4656,2:920,3:1386},         mass 10654;
width-charged  = {1:7819,2:920,3:1386},         mass 13817.
```

The extra charge is only one leading H1 at each of the 3,163 witnessed
original rank-one occurrences. No width claim for an internal factor of a
higher-rank split is needed. The other wide-cut counts remain information
only. Scalar work, storage and routing cannot reduce this lower invoice.

For the power tariff `r^t`, `0<=t<=1`, every target rank is at least four and
every charged paid rank is at most three. Therefore

```text
T_t <= 4^(t-1) * 10750,
P_t >= 3^(t-1) * 13817,
T_t/P_t <= (4/3)^(t-1) * 10750/13817 <= 10750/13817 < 1.
```

This rejects every such moment for the stated uniform width policy. It does
not depend on a numerical root or an independent-error model.

## Evidence and limits

The written valuation and numerator arguments cover every sufficiently large
k under the stated premises. The verifier gives finite corroboration for all
75 coefficient pairs in the source certificate. It checks injectivity at k=5,
exact reduced numerators at k=32 and k=64, and six separate paid-cut executions
with four scalar inputs each. Removing all independent helper inputs removes
every two-band witness. Four in-process controls reject a false valuation
loss, a zero band, a missing final owned clear and a float in an exact receipt.
Isolated normal and optimized processes reject changed source bytes and a
changed witness coefficient.

The result leaves open adaptive widths, joint symbolic state, changed scalar
words, changed helper boundaries, another cost law, and already funded larger
widths. It does not prove Gaussian/frame compatibility for recursively
substituted approximate children. No full physical Gaussian implementation,
uniform compiler, outer multiplication replay, or new kappa is supplied.

Prepared by Ali Romman, with substantial OpenAI Codex assistance. The actual
source, caller, moving-frame audit and earlier contributors retain their credit
as stated in README.md and the pinned source files. Apache-2.0.
