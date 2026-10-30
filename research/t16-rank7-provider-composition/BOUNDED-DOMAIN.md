# Omitted full-bin patterns after PR3457

PR3457 optimizes a chronological dictionary containing every capacity-8 and capacity-16 pattern, but only the pooled optimum patterns at capacities 32 and 48. Its new feasible construction does not establish a chronological packing optimum.

The changed domain adds precisely `[7,7,9,9]` at capacity 32 and `[7,7,7,9,9,9]` at capacity 48. A floating LP reduced-cost screen nominates eligible groups; those numerical results are discovery aids, not proof inputs. A global 90-second integer attempt produced no incumbent. A local repair keeps every other group's pattern counts and role flow fixed and frees only the nominated group plus groups currently serving the nominated calls' width-7/9 demands. One initial repair and a bounded pass over 29 further capacity-32 nominations yielded the retained literal certificate. No claim of exhaustion outside these named neighborhoods is made.

The independent certificate replay checks every integer flow, actual event window, bin degree, source-derived helper width and both provider bindings. All 144 calls and 58,752 helpers remain complete. The resulting idle delta relative to PR3457 is

`-229 H1 + 110 H2 + H3 - 2 H5 + 2 H8`.

For `H_r = 73^a r^(1-a)`, `0<a<1`, rewrite this as

`110(H2-2H1) + (H3-3H1) + 2(H8-H5-3H1)`.

Strict concavity/subadditivity makes each term negative. Rank mass is conserved exactly. Thus the complete local profile strictly improves throughout the relevant exponent interval, independently of the optimizer objective. Both exact moment engines give complex endpoint `0.001727254340596650594393`. Complete physical/controller/outer admission remains a separate required replay; the prior fresh native cache is reused with its original authentication.

The retained fill uses 115 capacity-32 bins of the newly admitted `[7,7,9,9]` pattern. The capacity-48 candidate pattern was allowed in discovery but is unused in this certificate; no gain is attributed to it.
