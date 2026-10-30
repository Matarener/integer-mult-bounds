# A current-budget obstruction for one fixed unpooled moment contract

This is an exact rational screen for the published PR #4067 unpooled OQ4 host,
not a runtime lower bound or a universal R437 exclusion. It fixes the paid
profile, productive normalization and moment-certification route below.
All source files are the exact current-main bytes pinned in SOURCES.json;
the predecessor host implementation is read as data, not imported or executed.

## Source model and destination budget

The frozen HOST-RESULT gives the new paid profile

```
{1:380448, 2:400288, 3:22464, 4:26592, 5:29376,
 6:17376, 7:26496, 26:32, 42:384}.
```

It has rank mass 1,808,352, dimension 64 and productive width W=28,416.
These are supplied predecessor host results, not a new reconstruction of the
288 calls or 125,856 hosted owner occurrences. The source `host.py:price`
uses the moment `sum n_r*(r/64)^(1-c)/W`, after adding the nonnegative rank-one
bad-event surcharge `32*64^2*E/10^16`, where E is the total paid count.

Delete that surcharge and every other added cost as a favorable relaxation.
For c>=0 define the fixed optimistic moment

```
M0(c) = sum_r [n_r*r/(64*28416)] * exp(c*log(64/r)).
```

The **budget-contract premise** is that the proposed retained admission route
requires `M0(c)+D(c) <= 1`, where every added normalized charge D(c) is
nonnegative. Some source contraction arguments require a strict inequality;
failure even of this weak version suffices here. This premise is about that
moment-certification method. An upper-bound recurrence with a failed moment
does not prove a lower bound on actual runtime, exclude a different analysis,
or make the underlying algorithm impossible.

The pinned selected CLAIM distinguishes three quantities:

```
ordinary BIT saving = 8590884599/2500000000000,
admitted BIT saving s = 17/5000,
whole multiplication kappa = 62009/20000000.
```

The first is strictly larger than s. Thus s is a favorable ordinary-slot
target for this screen; the smaller whole multiplication kappa is not the
ordinary moment target. No selected frontier is changed.

## Exact lower certificate

For x>=1,

```
log(x) >= 2*(x-1)/(x+1).
```

For example, the difference vanishes at x=1 and its derivative is
`(x-1)^2/[x*(x+1)^2] >= 0`. Also `exp(y) >= 1+y` for every real y.
All supplied ranks satisfy `0<r<64`, and c>=0, so these inequalities give

```
M0(c) >= L(c),
L(c) = sum_r [n_r*r/(64*28416)] * [1+2*c*(64-r)/(64+r)]
     = A + B*c,
A = 18837/18944,
B = 227656981418642299/126181391898481920 > 0.
```

No numerical logarithm, exponential approximation or root search is needed.
Exact rational evaluation at the freshly bound budget gives

```
L(17/5000) = 37130213109568854799/37112174087788800000,
L(17/5000)-1 = 18039021780054799/37112174087788800000 > 0.
```

Consequently, for **every** c>=17/5000 and **every** nonnegative added charge
D(c), `M0(c)+D(c) >= L(c) >= L(17/5000) > 1`. There is no feasible point
with c in that range for the fixed budget contract. By contrast,
`M0(0)=L(0)=18837/18944<1`; this is a positive-saving obstruction, not a claim
that the zero-saving host fails.

## Conditional ordinary-saving bridge

The retained PR #3690 transfer text fixes `c=1/576` and sets ordinary saving
`a=c*(1-c)`. Its physical estimates retain the historical restriction
`17/10000<c<1/512`, plus the changed-program refinement, stock, history,
primitive-cost and other framework premises. None is newly proved here.
Its text does not by itself establish physical refinement of this changed
PR #4067 host; only its algebraic saving law is reused as a declared bridge.

For the budget screen, declare only the favorable bridge `0<=a<=c`.
This follows from `a=c*(1-c)` in its nonnegative-saving range. If an attempt
to fill the retained ordinary slot requires a>=s and uses this bridge, then
c>=s, contradicting the fixed moment-contract bound above. The actual pinned
ordinary saving is larger than s and therefore also cannot be reached by
that unchanged contract and bridge.

Allowing all c>=s deliberately relaxes the historical physical range to make
the necessary algebraic test favorable. It does **not** extend PR #3690's
physical transfer theorem to c=s or to any new parameter. Within its original
range, c<1/512<s already prevents reaching this slot. The rational certificate
shows that merely relaxing that range while retaining this invoice, moment
gate and a<=c bridge still cannot certify the current target.

## What this adds and what it leaves open

PR #3668 already reports an earlier R437 invoice and historical c comparison;
PR #3700 audits the earlier OQ4 invoice/root and its outer convention;
PR #4067 certifies the local carrier improvement and charged fixed-host root.
This package claims none of those constructions, roots or replay results as
new. It supplies a short, source-bound implication for the revision-8 admitted
ordinary budget: even the zero-surcharge relaxation of the unchanged unpooled
invoice fails its retained moment gate at that budget and every larger c.
Another root digit, a reduced nonnegative surcharge or completing stock work
alone cannot change this particular budget decision.

A changed paid profile, productive width, target allocation, moment analysis
or transfer law is outside the proposition. In particular, the released
[pooled allocation handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3967#issuecomment-6267387753)
already reports a local-only allocation audit with a **different** paid
profile. It does not yet give a complete pooled price or regenerated physical
source catalogue. This result neither calls that allocation unperformed nor
excludes it. Full native/ordinary compilation, caller integration, reverse
precision charges, physical/stock costs and general R437 possibilities remain
open. No whole multiplication kappa or supplier admission follows.

Credit Chris R/Clear1nsight (#4067) for the carrier, complete fixed host and
price; ai-nanachi (#3647) and Ali Romman (#1043) for the retained R437 word;
Sagar Thakrar (#3700/#2423) for the OQ4/invoice lineage; zxv (#3690) for the
ordinary transfer; unpaidmoon (#4147) for the reverse-envelope distinction;
Rohan Arun and the retained pooling/native/compiler/physical/analytic authors.
This scoped certificate/proof was prepared by ToikY with substantial OpenAI
Codex assistance in separate primary, oracle and review contexts. Apache-2.0;
retain NOTICE. No independent human or proof-kernel acceptance is claimed.
