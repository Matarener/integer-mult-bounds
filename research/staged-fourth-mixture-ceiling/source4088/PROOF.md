# Finite mixed-provider construction and exact moment

Prepared by Cinna Davis with OpenAI Codex assistance. Apache-2.0.

## 1. Sources and common interface

The immediate source is PR4085 at `c5854c77620723aae6914c32122870519a6f820d`,
composing receiver sharing with PR4076 at
`9744f9df268590295a9872b1952c695a678192b9` on the PR3945/3734 staged544 lineage.
PR4085 replaces the two helper544-to672/676 reads by a three-shear shared
receiver circuit. The resulting THREE words here are byte-identical exports;
the same rewrite is explicitly included in each FOUR word. Both orientations have 632 live registers and
91 private dirty buffers. Their endpoint map is `(x,y,h,b) -> (x,y+x,h,b)` in
the retained free-native-operator model, together with the dual and cleanup
boundary contracts. Ports, removed registers, native lenders, native matrices,
wrappers, cuts, protected terminals, source order and the owner template retain
those source contracts.

## 2. Fourth-entry word

In each retained three-entry word, helper 601 enters at `span(45)`. Raise this
to `span(127,45)`. Delete the four quarter-weight reads into targets
183, 202, 175 and 123. Before the original chronological event 10515, the exact
prefix propagation of `v=e601-e602` has

`M v - e601 = -e602 + (1/2)e123`.

Every encountered native/correction consumer annihilates that prefix vector.
Place `123 += 601/2` at that cut and slide `602 -= 601` through its commuting
range to original event 11161. Event numbers refer to the pinned PR4085 event
list; the literal record is the definitive source-bound construction.

The exact frame solver supplies explicit gate frames, and cleanup is regenerated
from the complete changed word. For verification, no prefix argument or solver
output is trusted in isolation: the retained exact symbolic interpreter runs all
723 independent input symbols through both complete orientations and compares
forward, dual, reverse pullback and cleanup endpoints. All private buffer symbols
return identically and have zero leakage into live outputs. Omitting or reversing
either release is rejected even after regenerating its cleanup.

A separate binary-basis ledger and the point-set ledger agree on

`L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8`,

`L4 = L3 + 2 H1 + 3 H3 - 3 H4`.

Only helper 601 changes hosted width, from 8 to 7. The local paid-rank change is
`2 + 3*3 - 3*4 = -1`. Both new words additionally pass fresh native transport,
ledgers, local replay, wrappers and phases, including all-column native recipes.
These finite native checks do not establish the inherited all-size hypotheses.

## 3. Explicit mixed schedule and owner construction

The unchanged order contains all nine stages for each of 360 replicas, respecting
per-replica stage order. At time `t=0,...,3239`, use the fourth-entry variant of
the original orientation exactly when `t mod 3 = 0`. Thus there are 1080 fourth
calls and 2160 third calls. `MIXED-DISPATCH.json` lists every choice.

Each variant has the same required endpoint and interface. Substituting one
correct implementation for another therefore preserves composition of the parent
operator, provided each call receives its declared legal hosted slices. The
explicit dispatch is a fixed finite table. It adds no new recursive call; the
retained uniform-implementation hypotheses must cover its fixed selection logic
and all four finite words, as they cover the predecessor's two orientations.

For every owner and child, the verifier derives `(capacity,lo,hi]` from the
retained execution schedule and actual call order. A row `(t,h,o,c,p,z)` of the
new fill must satisfy:

- exactly one row for each ordered `(t,h)`, over all 3240*408 roles;
- `lo < t <= hi` for that exact owner/child and a valid port `p`;
- no repeated owner source-family/port in a call;
- offset `z` equal to the accumulated earlier widths of that exact bin;
- accumulated width plus the actual selected provider's helper width at most
  the child's capacity.

The verifier also checks that different children of a common owner family have
disjoint call windows. It scans all 725760 bins, including empty bins. The
resulting idle counts are exactly

`I = 22785 H3 + 1625 H5 + H16 + 2 H32 + 138490 H48`.

The independent operator replay uses PR4085's unmodified exact Z4-polynomial
normalizer and event-level observer definitions. It checks every literal role
strictly after its last scalar observation and before its original idle endpoint,
productive/helper nonaliasing, disjoint slices of each original phase-axis list,
and the exact complementary residual. No axes move between child slots.
All 10,416 phase identities at the 112 ordered ports and the complete signed
eight-stream scalar controller hold. These polynomial identities hold for every
character; adding the identities modulo four extends them to every positive
tensor multiplicity. The hosted-factor collapse uses the freshly scanned mixed
fill, not a retained certificate for a different dispatch. Native endpoints and
common-cover embeddings remain the declared source interface.

This is an integer, chronological, distinct-family witness. The discovery LP and
its floating-point solves are unnecessary for this proposition.

## 4. Complete cost and comparison

The full profile is `2160 L3 + 1080 L4 + I`, namely

`8060040 H1 + 2310120 H2 + 751785 H3 + 327240 H4 + 66425 H5 + 25920 H8 + H16 + 2 H32 + 138490 H48`.

Relative to PR4085, idle changes by

`-57 H3 - 265 H5 + H16 + 2 H32 + 52 H48`.

Its rank mass is 1080, exactly balancing the local rank-mass reduction -1080.
The total paid rank mass remains `65088*360`.

Let `M(k)=sum_r n_r r^(1-k) - (896*360)73^(1-k)`. Dividing by
`73^(1-k)` gives a strictly increasing function of `k`, since every paid rank is
strictly below 73 and every count is positive. The retained rational logarithm
and alternating-exponential remainder bounds certify

`M(0.001730978305075885693430) < 0`,

`M(0.001730978305075885693431) > 0`.

The exact interval endpoints are in RESULT.json and regenerated by price.py.
The same engine freshly certifies PR4085's earlier bracket. All signs and the root comparison use rational enclosures.
After subtracting the retained `10^-46 + 10^-70` outer padding, the new endpoint
still exceeds PR4085's upper endpoint by more than
`7.885876721990690*10^-9`.

The conditional outer conclusion uses the same analytic, source, hosting,
precision, tape, recovery and BIT transfer hypotheses as the predecessor, with
the explicit finite mixed dispatch above. This package does not report a fresh
full ordinary/outer admission release. Source-registry integration and that
end-to-end replay are a separately identified remaining obligation; the finite
construction and complete moment comparison stand independently of such a run.
