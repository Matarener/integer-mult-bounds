# Paid pairing of the literal future-query sources

Chris R / Clear1nsight with OpenAI assistance. Apache-2.0.

This construction modifies the actual canonical PR2707 word pinned in
`SOURCES.json`, using the streamed, deferred-output lifetime idea of PR4015.
PR3985 supplied the recovery/fusion problem and PR4003 identified the exact
borrowed-Y residual. The contribution here is a new scalar arithmetic DAG for
that same full recovery demand; it does not eliminate a native child.

## Identity and paid schedule

At the second-query cut, let `v_p = [g2,p] W_p` denote the logical value in an
owned bank after the charged CLEAR, copy from the **actual corrected** `W_p`,
stage-2 map and negative Gaussian line. Its physical frame is F16. Each source
occurs in four query rows, with coefficients `R[k][p]` in `{−1,+1}`.
All 104 ports in `U ∪ T` are used exactly once. Thus both the prefix correction
inside `W_U` and the literal `W_T` contribution are retained.

For a pair `p,q` having the same four-row support, normalize the two sources
separately into `D=v_p` and `E=v_q`. Let `m` be the number of their four
coefficients that agree. First consume all differing coefficients with two
ADDs per row. Only then execute the paid ADD `D += E`. For each agreeing row,
with common sign `s`, execute the single ADD `Q_k += s D`. In a differing row
we have already added `R[k][p] v_p + R[k][q] v_q`; in an agreeing row,
`s(v_p+v_q)` is exactly the same contribution. No equality of routed payloads,
no free projection and no global sign normalization is assumed.

The pair uses `2(4−m)+1+m = 9−m` unit ADDs instead of eight. The actual
packet admits 48 pairs with `m=3` and four with `m=2`. Its 52 pairs therefore
use 316 query unit ADDs instead of 416, saving 100. `choose_pairs` performs
exhaustive deterministic matching only within each actual same-support group
(of four or eight ports); any optimality statement is restricted to that
pair template. This is not a global arithmetic-circuit lower bound.

The response is unchanged: for every `p∈A`, form
`−(1/4) Σ_k R[k][p] Q_k` in F16, apply the positive line, apply the inverse
stage-2 map and add into `W_p`. The exact canonical prefix and suffix are
retained except for the ten deferred definitions described below.

## Owned-bank lifetime

Eight query roles and the two normalized sources use ten deferred output
banks: Q0..Q7 occupy Z1,Z2,Z3,Z4,Z5,Z6,Z8,Z9, and D,E occupy Z10,Z11.
These are existing members of the 224 owned outputs. Every host has exactly
one original CLEAR/current and one copy from its borrowed X source before the
query cut, and no other reference before the cut ends. Those definitions are
moved, not credited as eliminated work. Every host is CLEARed and recopied
from its original X source after the query and response and before the exact
original suffix resumes. The actual restored event indices are recorded in
`CONSTRUCTION.json`.

Each query role is initialized by a charged CLEAR. Each D/E use starts with a
charged CLEAR and X-independent copy from its current W source. The unhosted
construction would clear all ten temporary roles on exit; hosting replaces
those terminal resets with the moved, already charged output definitions.
The tenth host is necessary for the second source E. There are no added owned
banks and no native operation overlaps the preserved private sweeps. The
original private peak of 16 remains; the new future block uses zero private
banks. This is a logical owned-bank statement, not a six-tape physical ABI
certificate or a reduction in allocated output storage.

## Invoice and numerical boundary

The emitted word has 3,713 events, 1,820 unit ADDs, 896 quarter ADDs, 416
CLEARs, 352 maps and 224 rank-one native line calls (448 wrappers).
Under the existing tariff its scalar allowance is
`8×1820 + 12×896 + 2×416 = 26144`. The PR4015 word has allowance 26944;
the improvement is exactly 800. Relative to PR3985's 27184 it is 1040,
including PR4015's preceding lifetime work. Native counts, child sizes and
all 224 requested outputs remain the same. Map costs and other separate
physical liabilities must not be folded into this scalar number.

Reassociation and reordering change intermediate values and rounding errors.
PR4043's identical-trace transfer is therefore inapplicable. A fresh finite-
precision and intermediate-range certificate, physical placement/traffic
pricing, and recursive caller applicability remain obligations before this
local reduction could affect a global bound or selected kappa. There is no
claim here of a measured runtime gain, native saving or improved kappa.

## Reproduction and independent checks

`construction.py` consumes only authenticated packet/route data and the
canonical word supplied by its caller; it imports no predecessor executable.
The retained word SHA256 is
`b4f2b5662734178d02a5d620ebd071bc284abd4d9b6dbe11b5d9646455a0f021`.
The full construction and its pairing/lifetime receipt regenerate exactly.
The package verifier checks exact routed linear expressions and complete
quadratic frame phases, all 224 original outputs, all 224 independent-current
outputs, the preserved intermediate checkpoint, and every borrowed current
value and frame. The independent accounting/pair-identity module additionally
checks the literal coefficient partition and tariff without using this
constructor's invoice function. See the final verifier receipt for executed
checks and rejection controls.

A separate read-only construction check authenticated every `SOURCES.json`
entry before loading canonical executable code, regenerated the canonical and
candidate words and the complete construction receipt, and passed both full
replays (original input plus checkpoint; independent arbitrary current input).
Two full-replay controls were also rejected: moving the first `D += E` before
its differing-row reads keeps every invoice count but produces wrong output
Z0; deleting the tenth host's restored X-copy produces wrong output Z7, the
first affected output encountered by the checker. Event anchors refer to the
retained word above: overwrite 1714, differing reads 1710–1713, and tenth-host
copy 2517 (all zero-based).
