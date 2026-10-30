# Delaying public preparation through a shared component

This construction continues the verified shared587 relay and148 contraction.
Its source is `contracted-587-relay-WORD.json`, with canonical sorted-key JSON
SHA256 `95078b95bae0c56927f6daaa4430457cc43862c24a9db3b015bb1366e3381055`.
The underlying frozen word is PR5580, head
`6efa248cf456d6101d757e9d09ba29711d18a13a`.

This note proves the new component. The package verifier separately checks the
composed word, complete native/caller/ordinary bill and analytic predicates.

## The changed preparation

Write `P` for the public133 value copied into owned738. At its final line597,
public734 contains `x734-P/2`. All `x` variables below are arbitrary original
inputs; none is assumed zero.

At frame1031, before the relevant producer preparation, let the current public
values699,701,702,703 be `a,b,c,d`. The original preparation forms

* `696 = x696-a+b+c`;
* `700 = x700-b-c`, later updated to `700-d`.

The opposite coefficients of `b+c` permit a useful retiming. Public700 retains
that component after701 and702 have ascended and after `P` has become available.
Consequently696 need not ascend early just to read701 and702 separately.

After the last original zero-frame read of696, add `x700-x734` to696 while
all three fields remain at frame3. Delete its original ascent3-to1031 and
the original three additions from699,701,702. Immediately after734 receives
the owned value at597, perform

1. `MOVE 696,3,597`; `ADD 696,734,+1`;
2. `MOVE 696,597,1031`;
3. `ADD 696,699,-1`; `ADD 696,700,-1`.

The resulting value is exactly the original696 value minus `P/2`:

`x696+x700-x734 + (x734-P/2) - a - (x700-b-c)`.

The changed itinerary uses existing frames. The two new ascent ranks are1
and4, replacing the original rank5.

## Coupling the two later butterfly inputs

At this point, still before the original `700 -= 703` update, define

`S = current696 + current700 + current699 = Z-P/2`,
`Z = x696+x700`.

Add `S` into703 using three ordinary ADDs. Then add the same old `S` into700
using `SCALE 700,2`, `ADD 700,696,+1`, and `ADD 700,699,+1`. The subsequent
unchanged `700 -= 703` update cancels700's entire added quantity.

Thus the later696/703 butterfly receives perturbations `-P/2` and `Z-P/2`
in its two inputs. Its sum delivered to159 changes by `Z-P`. Its complementary
output delivered to222 changes by `-Z`. All other live-input effects cancel.

Delete the remaining owned738 read into159. That read originally added
`P/2`, later scaled by159's factor `-2`, so deleting it adds `P` to the final159
value. Combining the deletion with the changed butterfly leaves only

`out159 += Z`, `out222 -= Z`

on outputs whose final frames have dimension below nine.

Four initial common-zero-frame ADDs cancel these nuisance terms: subtract
both `x696` and `x700` from159, and add both into222. These are distinct
source and destination coordinates. Exact arbitrary-input replay verifies
the cancellation; it does not rely on clean helper inputs.

Owned738 now goes directly from591 to597, a rank7 descent. The intermediate
rank7 frame565 and its scalar contact are removed.

## Full-frame cleanup

Immediately before the original `ADD 133,288,1/2` at full frame127, exactly
five public rows still differ. Let `L=Z-P/2`. Their errors are

| Role | Error |
| --- | --- |
|696|`-P/2`|
|697|`L`|
|698|`-L`|
|700|`L`|
|703|`L`|

At this cut, the actual current rows satisfy

`133=P`, `696=x696-P/2`, `700=x696+2*x700-P/2`,

so `L=(current696+current700)/2`. All six involved rows are at127. First
subtract half of each carrier696 and700 from697 and703; add half of each
to698. Next scale700 by1/2 and subtract696/2, restoring `x700`. Finally add
133/2 to696, restoring `x696`. These nine operations restore every row
before the unchanged suffix. Source identities and operation ordering are
checked over all735 original-input columns.

## Invoice and exact verification

The public preparation replaces `H5` by `H1+H4`. Removing the last owned
contact replaces `H1+H6` by `H7`. The net paid change relative to the
shared587 candidate is therefore

`H4 + H7 - H5 - H6`.

For `H_r=r^t`, `0<t<1`, strict concavity gives
`H7-H6 < H5-H4`, so this change is strictly negative throughout that
range. This comparison is a transport statement, not by itself a new
complete multiplication bound.

The source-pinned `delayed.py` implements the component for either the
published PR5605 word or its commuting-cascade parent. It accepts only their
exact canonical payload hashes and checks the resulting full payload hash.
The standalone component has25187 events and adds18 ADDs and two SCALEs,
with no net MOVE-count change or new register. The full composition is described
in COMPOSITION.md and verified separately on every independent input.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agent derivations. Retained source lineage and licenses are credited in README.md.
Apache-2.0.
