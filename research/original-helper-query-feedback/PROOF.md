# Original-forward helper-query feedback

## Source and input contract

The source is the original forward native word with 632 arbitrary independent
persistent inputs: 112 x fields, 112 y fields and 408 helper fields. Its moving-
frame endpoint is `(x,y+x,h)`. Its eight center calls and owned temporary remain.
The verifier replays all source endpoint rows and checks that its 358 cold-helper
first departures equal the complete matrix T from PR5388. All 112 selected
first events, owners, frames and ranks agree with that bank. This comparison
uses the original word, not the center-free producer consumed by PR5388.

Let xi be the independent cold-helper coordinates and let w=D_K xi. The
predecessor's in-place scalar program applies T inverse. Its original first
query at selected slot j has physical frame E_j and argument K_j xi_j.
The monomial words K_j and O_j satisfy

```text
O_j E_j K_j = Q,        K_j R = R K_j,
Q^2 = X_central,        Q^4 = I.
```

Every displayed identity is checked with its signed Clifford tableau and exact
zero-state amplitudes. Q squared is an ordinary Pauli permutation. All scalar
coefficients remain outside tensor powers. The fixed native lift applies each
operator identity to the active axes and preserves arbitrary spectator data.
Thus the identities hold at every allowed positive fiber width under the
inherited native implementation and cost assumptions.

The 112 adapted H1 children are relocated to an entrance prologue, before
T inverse. For each selected coordinate, copy w_j into a cleared raw field,
execute its actual adapted source child, copy that physical result into a
cleared observation field, and apply O_j to the observation. The source child
is relocated, not duplicated. The three live values are then

```text
w_j   = K_j xi_j
raw_j = E_j K_j xi_j
obs_j = Q xi_j.
```

## One exact feedback shear

For h different from k, change `xi_k` to `xi_k+Q xi_h`. Keep the three live
representations consistent by these changes:

```text
w_k   += K_k obs_h
obs_k += Q^2 K_h^-1 w_h
raw_k += O_k^-1 Q^2 K_h^-1 w_h.
```

The first is K_k times the required argument increment. The second is Q times
that increment. For the third, the query identity gives

```text
O_k^-1 Q^2 = E_k K_k Q.
```

Hence the raw increment is the actual query E_k applied to the new argument.
No new Gaussian query is needed: K_k, Q squared, K_h inverse and O_k inverse
are monomial maps. The verifier checks their Fourier rank, literal compilation,
signed tableaux and absolute phases. Merely changing w_k would leave the held
raw result and observation stale.

Use one owned scratch field a for the following literal sequence:

```text
CLEAR a; COPY a <- obs_h; apply K_k to a; ADD w_k += a;
CLEAR a; COPY a <- w_h; apply Q^2 K_h^-1 to a; ADD obs_k += a;
apply O_k^-1 to a; ADD raw_k += a; CLEAR a.
```

Chart changes on a come from the stated physical monomial maps. They are not
free nonzero retags. The source field h is unchanged during this shear because
h differs from k. Therefore the sequence preserves the three displayed
invariants and is an invertible elementary change on the xi coordinates.
Induction proves the same fact for any finite ordered sequence. It permits a
later shear to read or change a coordinate used by an earlier shear.

## Resume the original source and return every field

After all feedback, apply the unchanged T inverse program to w. At each of the
112 original query cuts, the persistent field is again w_j in chart zero.
Its stored raw field is E_j w_j. Replace that original child by a whole-field
swap, including its chart tag, then clear only the owned duplicate. This puts
the persistent field in exactly the physical state that the source child
would produce on the updated independent input.

The first-departure rows have no main-input coefficient. Each prefix identity
holds on every helper column, so it remains true after this operator-valued
linear substitution. Induction through the replacement cuts proves the entire
original source endpoint on the changed inputs. Every other source operation,
including all eight centers and inherited phase/adapter records, is retained.
The source never reads the separately held observations.

The source leaves each helper in its old physical output chart. Apply the
predecessor's 26 H5 and six H1 completion recipes to the non-full cold returns.
All 358 cold fields now have the same full-R chart. Apply the scalar program T
and the selected K inverses. The source proof gives the final cold outputs
`R S(Q) xi`, where S(Q) is the ordered feedback shear word. The other 50 helpers
retain their original jobs. The main source endpoint is unchanged. Clear all
owned observations after their last use; raw fields and scratch already hold
zero. No persistent input direction is erased.

S(Q) is invertible, but it depends on Q. This proof does not supply an ordinary
inverse decoder for S(Q). Consequently it does not permit independent H9 target
credit on the original xi inputs. A completed caller must consume or remove
this code and prove its own targets. The copied observations add no independent
productive input or job.

## Exact accounting and verification

The original paid profile is `{1:2201,2:412,3:510,4:127,5:40,8:8}`. Relocation
and feedback preserve that profile. Return completion adds six H1 and 26 H5.
The final paid profile is `{1:2207,2:412,3:510,4:127,5:66,8:8}`. With no feedback,
the autonomous helper profile changes from `{4:28,7:7,8:47,9:326}` to
`{4:2,7:7,8:41,9:358}`. Before feedback this is a legitimate source-bound
completion comparison. Its signed difference is positive at every concave
hinge below rank nine and zero in rank mass. It is a strict cost increase
for 0<t<1, not a paid-profile improvement.

The relocated bank uses 224 new owned fields, 224 COPY, 448 CLEAR and 112
whole-field/chart swaps. The two basis programs use 6,420 ADD and 408 SCALE.
Input, output, response and completion words use at most 400 monomial field
maps. Each nonempty feedback sequence adds one reused owned field and, per
shear, two COPY, three ADD, three monomial maps and three CLEAR. The source's
original ordinary operations and owned center temporary remain additional.
All original owned inputs may start arbitrary. Only owned fields are cleared.
Fixed rational scalar coefficients, field traffic and monomial maps still need
ordinary and precision funding in any eventual multiplication construction.

The primary replay represents each input by an independent free-word column.
It checks 632 original columns and 226 arbitrary owned columns for five shears
`(0,1),(1,0),(1,2),(2,111),(111,0)`, plus the empty sequence. A separate elementary
update of the independent xi rows supplies the expected feedback endpoint.
The full source replay checks every replacement cut, all persistent rows,
all final charts, the paid profile and every owned return. The exact physical
check covers all 112 query identities and all 32 completions. Seven deliberate
changes must fail: stale raw data, stale observations, one Q instead of Q
squared, a swap without chart transport, uncleared initial scratch, live final
scratch, and an omitted completion. These finite controls support the written
induction; they are not formal-kernel verification of all callers or widths.

No backward interface, complete caller, full precision/compiler bill, BIT
transfer, supplier admission or new multiplication exponent follows.
