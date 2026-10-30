# Three neutral helper relations remove paid calls

This construction starts from the exact PR5627 word at
`ed4dc88a09a7d201971f6603b8c2074e95dd9c32`. It keeps all 743 independent
inputs, all 535 helper targets and the 104 main pairs. The selected frontier
is unchanged. The five source framework assumptions and the helper endpoint
contract remain.

## 1. The boundary identity

Write the scalar state in native normalized coordinates. Let h be a helper
with initial chart S and final chart F. At a chronological cut, suppose h
and each cancellation supplier are at F. Suppose the exact prefix rows give

```math
r_h-\sum_j b_j r_j=c x_h+\sum_{j\ne h} a_j x_j.
```

Every input on the right has initial chart S, and c is a dyadic unit. Suppose
there is no later source read of h. Before the word, apply
`h += -a_j/c * j` for every j other than h. At the cut, apply
`h -= b_j * j` and then `h *= 1/c`. The resulting h is exactly the original
independent input x_h. Delete the later scalar operations whose destination
is h. They have no effect on another output.

The source returns every helper unchanged and has no helper contribution
to a main output. Thus the input basis change can affect only the old h
output. The cut repairs that output exactly. No helper is set to zero,
no new input is created and no productive target is removed or added.
All basis coefficients are dyadic, and every SCALE has a dyadic inverse.

The constructor checks the complete prefix relation, common charts, the
last-read condition, the exact removed operations and the full arbitrary-input
endpoint after each step. It also checks that the complete chronological
subsequence of owned operations is unchanged.

## 2. Exact witnesses

The cuts below are zero-based and refer to each successive word after
transport coalescing. `WITNESS.json` retains the full event anchors and vectors.
Here `e_j` denotes the j-th independent input.

| Helper | Cut | Final chart | Prefix row after cancellation |
| ---: | ---: | ---: | --- |
| 291 | 10627 | 234 | -2 e291 - e293 + 2 e39 + 2 e303 |
| 321 | 11072 | 237 | e321 - 2 e320 - 2 e34 + 2 e330 |
| 369 | 11718 | 243 | e369 + 2 e383 - 2 e372 - 2 e3 - 2 e382 - 2 e378 |

Their cancellation vectors are respectively
`{293:-1}`, `{22:2,320:-3/2,330:2}`, and
`{368:-3/2,26:2,378:-2}`. All initial basis operations use chart 3.
The three steps remove six, five and five old scalar cleanup events.
The inserted cancellation and input operations are included in the cost.

## 3. The paid change

The removed cleanup contacts let main roles 55, 49 and 80 bypass one
intermediate chart each. Their old paths are

```text
role 55: 722 -> 234 -> 127
role 49: 734 -> 237 -> 127
role 80: 749 -> 243 -> 127
```

Each path has ranks 1 and 5. The new direct path has rank 6. For chart
operators C_A, C_B and C_D, the exact product is

```math
(C_D C_B^{-1})(C_B C_A^{-1})=C_D C_A^{-1}.
```

No scalar operation uses that role between these transports. The chronological
replay checks strict chart containment, and the native verifier checks the
exact signed map and global phase. This identity applies at every positive
tensor width under the retained native implementation assumption.

The local paid delta is `-3 H1 -3 H5 +3 H6`. Every target stays fixed.
For 0<t<1, the complete target-minus-paid moment therefore increases by

```math
54[1+5^t-6^t]>0.
```

This is a changed physical invoice. It does not add predecessor kappa gains.
The alternative PR5613 inventory has 72 additional H5 paid calls and 72
additional H5 targets. It has the same signed source moment, but this package
uses only the smaller PR5627 inventory.

## 4. Complete cost and verification

The final local word has 25,448 events, 743 independent inputs, 535 helpers,
nine owned roles, eleven owned lifetimes and peak owned occupancy two.
Its paid profile is

```text
{1:2197, 2:456, 3:494, 4:91, 5:160, 6:21, 7:15}.
```

The complete caller retains 18 full forward calls, 15 thin query sites,
3,120 whole idle jobs and 3,328 main targets. Its complete invoice has
66,492 paid calls and 12,958 productive targets. The rank-mass surplus is 760.
Helpers, native normalizers, main adapters, basis operations, COPY/CLEAR,
all owned lifetimes, routes, thin queries and idles are charged.

A separate dense integer transpose checks all 565,504 matrix entries.
The native check verifies 2,916 distinct maps. The physical caller verifies
all 7,488 contacts, 53,248 central-square columns and complete main phases.
Two rational interval engines check the same complete moment.

The exact raw crossing lies in
`(0.00310626336369, 0.00310626336370)`. The claim is `0.00310626335`, tested
at `0.003106263355`. The gain over PR5627's claim is `0.00000185789`,
about 0.05985%. This is a small gain.
The raw ceiling is proved only for this fixed invoice on `[0,0.0034]`.
Its headroom above the claim is between `1.369e-11` and `1.370e-11`.
It is not an optimum over constructions.

The source strictification parameters remain: power 1024, cutoff 17,
target floor 18, tail offset 1/5, reserve 10^-12 and tail decay 39/40.
The compiler checks its finite integer threshold, the preceding integer,
initial range, shifted exits and complement capacity. All 54 strict outer
conditions and four functional conditions pass. The ordinary BIT contract
remains 0.0034.

The local scalar allowance is 220,208 and the local route allowance is
5,172,000, below the retained 10^7 bound. The complete ordinary-work bound
is 184,647,552, below 10^9. Fewer than 26,000 scalar events and the checked
coefficient bound retain the source growth bound. The paid native rank sum
is 5,986 per local word. No growth or route cost is omitted.

The huge uniform word and complete rounded multiplier are not materialized.
These are author checks by the same AI-assisted author. Independent scientific
acceptance and a proof-kernel theorem remain absent. Source native, owned
erasure, uniform compiler, precision/tape and analytic recovery assumptions
remain. The package makes no large-gain or global-optimum claim.
