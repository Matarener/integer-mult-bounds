# Independent PR3734 involution and native boundary check

## Result and scope

The new checker reconstructs the involutory local component directly from the
authenticated PR3734 base and extra programs, then verifies the added intrinsic
native lines at their actual modern entrance and exit gauges. It does not recover
or rerun the missing historical `modern.py`.

Both providers pass 632 independent live input columns, including 112 sources,
112 targets and 408 arbitrary helpers. All 91 owned cleanup buffers and the
serial query accumulator return to zero. The added positive and inverse line
recipes pass 8,192 exact Gaussian columns per provider. Their global phases,
directions, modern endpoint frames and placement are checked separately from
the formal scalar/free-warp replay.

The complete conditional local rank profile is

```
{1: 2448, 2: 725, 3: 224, 4: 102, 5: 20}, rank mass 5078.
```

The retained scalar allowance is 179,900 real primitives per local call in
either orientation. This allowance excludes the separate recursive, native
address, precision, hosting and global terminal invoice. No kappa increase is
established by this component.

## Sources

PR3734 is pinned at `fa041037a3374eaa08feeca0b26a5d6893194147`, package
`research/staged544-producer-return`. Its self-contained replay archive has
SHA-256 `e74d545c18f77b7a9b8f0cc3d4901a87bb686888edaf3e41b30e5b2748751041`.
The reviewed `full_replay.py --extract-only` command authenticated and exported
every member of that archive. Its native receipt has SHA-256
`7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93`.

The source BORROW word hashes are

| Provider | SHA-256 |
|---|---|
| base | `5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699` |
| extra | `965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e` |

Both normalize to the same literal modern local program pair, compressed SHA-256
`441693817d93306d7a81aa463e98638ba69a7787e76bd4d9e8d2b5698248de35`.
The new checker authenticates the canonical word, program, native recipes and
residual recipes against the pinned native receipt before using them.

The exact positive/inverse line recipes and Gaussian-dyadic interpreter come
from the attached repository's `research/native-source-codes` package. Their
hashes are enforced in the checker and recorded in the result. The old recipe
construction is retained with attribution to Ali Romman and its predecessor
authors; this round adds the modern source binding, independent component
construction and explicit native boundary integration.

## Reconstruction of the clean core

Remove the entire eight-centre phase while retaining every persistent climb,
warp, adapter, helper wrapper, cleanup and zero-buffer event. Propagate the
resulting word over rational coefficients and noncommuting free warp symbols.
The forward omitted-centre endpoint is exactly

\[
(x,y,h)\longmapsto (x,y+Jx-KHh,h),\qquad J=I-KR.
\]

The checker derives the endpoint first. Independently reading the original
centre cut gives eight rows \(R\) and \(H\), and the full endpoint comparison
proves \(K=R^T/4\), \(RK=14I\) and the displayed dirty error \(-KHh\).
The dirty rows contain 367 helper coefficients; the image \(K\) contains 448
coefficients. Computing the eight dirty queries serially therefore costs
815 ADDs and 16 CLEARs.

Every helper read or changed by this correction has initial frame I and a FULL
terminal frame. No entering or hyperplane-ended helper is used before its
required wrapper. The forward correction adds \(KHh\) to the target before the
core. Its backward companion adds \(-H^TK^Ty\) to the helper bank. Both produce
the complete clean-J maps and restore every arbitrary helper.

## Involution and sparse correction

The pivot set is

```
0, 7, 20, 27, 36, 46, 57, 111.
```

Let \(P\) equal \(K\) on these rows and zero elsewhere. The checker establishes
\(RP=I\). Put \(A=12P-K\), \(G=I+AR\), and \(C=12PR\). Then

\[
RA=-2I,\qquad G^2=I,\qquad JG=I+C.
\]

The serial source word computes row \(R_kx\) before scattering column \(A_k\).
Since \(R_iA_k=-2\delta_{ik}\), that scatter does not change any later query.
This is checked against the complete emitted endpoint, and costs 896 ADDs and
16 CLEARs. Computing the eight nonzero rows of \(C\) costs 432 ADDs and
16 CLEARs.

## Actual physical boundary composition

For port \(p\), the retained external local gauges are

\[
X_{\rm in,p}=C_{q_p},\quad Y_{\rm in,p}=I,\quad
X_{\rm out,p}=C_{\rm full},\quad
Y_{\rm out,p}=C_{\rm full}C_{q_p}^{-1}.
\]

In the backward call, the sparse repair is performed before every retained
entry adapter. The accumulator first contains \((Cy)_p\) in gauge I. The
retained positive-line recipe applies exactly \(C_{q_p}\); the accumulator is
then added to physical \(X_p\), which has the same gauge. Applying \(G\) to the
I-gauge Y bank and running the clean core gives

\[
x+Cy-JGy=x-y,\qquad y\longmapsto Gy.
\]

In the forward call, the complete clean core and all cleanup/wrappers run first.
The source bank is then uniformly in gauge FULL, so scalar application of
\(G\) is legal. Form \(-(CGx)_p\) in the FULL accumulator. Apply the retained
inverse-line recipe \(C_{q_p}^{-1}\), and add it to physical Y at its actual
FULL-hole gauge. Since all translation roots commute,

\[
C_{q_p}^{-1}C_{\rm full}=C_{\rm full}C_{q_p}^{-1}.
\]

The checker verifies this composite as an exact Clifford operator including
global phase. The normalized target is

\[
y+Jx-CGx=y+Gx.
\]

Thus the complete changed normalized content maps are

\[
B_G(x,y,h)=(x-y,Gy,h),\qquad
F_G(x,y,h)=(Gx,y+Gx,h).
\]

The generic scalar interpreter itself still works in normalized coordinates.
It is the separate literal native recipe check, actual-gauge access checker
and ordered composition above that justify normalization of the new line
events. This is stronger than substituting an unverified scalar action for
them, while retaining the original common-frame/compiler premise.

## Verification and limitations

Run from the conversation workspace:

```
python -B recovered-involutory/modern_native_component.py
```

Each provider prints `PASS_MODERN_INVOLUTION_LOCAL_NATIVE_BOUNDARIES`.
The result and emitted programs are in `modern-native-results`. The
`NATIVE-LINE-LOWERING` files give the actual two monomial maps and positive
rank-one child, in execution order, for every positive/inverse repair.
Negative controls omit a required intrinsic line and change line direction or
global phase. All are rejected.

The checker independently replays persistent and owned frame chronology, but
authenticates and reuses the original Clifford, warp and residual recipe
certificates. It does not regenerate the entire native compiler backend or
claim that the unchanged stock driver accepts this new endpoint schema.
The positive/inverse line recipes and their modern phase composition are
freshly checked. The routed controller, terminal decoding, consumer ownership,
all-size realization and complete precision/tape/address invoice remain open.

## Open next questions

Can a complete routed consumer use this local saving while paying less than
504 additional rank mass per nine-call cover? The tested full-field H8 consumer
in the attached survey fails its reviewed 69.75-field rank bound. Typed
observations, paid retained state and changed routes must be specified as
actual operators and priced; the current component does not grant any of them.

New research and implementation used substantial OpenAI Codex assistance under
the user's direction. This is independent implementation within the same
AI-assisted project, not independent human review. Apache-2.0.
