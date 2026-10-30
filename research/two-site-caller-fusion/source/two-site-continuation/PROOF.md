# Two-site physical continuation

This is a changed complete caller at q2 and q3, with all original fields
arbitrary and independent. It improves the pinned mass from stock+8 to stock+4.
It does not give a positive stock deficit or a kappa improvement.

The input is an event-only copy of the repaired simplified two-fusion caller.
The exact event input has SHA256
`412e126144828455ebfa9d7baafb392e6f8cc5ff956876884451c59545765cfa`.
The current used-only recipe binding separately pins repaired
`SIMPLIFIED-FUSIONS.json` at
`4491cfe2a1f3e48510b33403b9b50c704865c3b1dc6d659ef5157840654e8fc3`
and its manifest at
`dde942457256b0f037a65eebeb5df822fe4d8911c0441657816c77a4c20c6f1c`.
No inherited H/L, inverse-row or inventory metadata is assumed.

## Exact two-site equation

At first unary site i replace G_i by X G_i. At later unary site j replace G_j
by Y G_j. Let V=E_j...E_(i+1), and let C be the correction required immediately
after the old E_j when a specified native tail subset is deleted. Then

```
C = Y_j V X_i V^-1.
```

Writing A=V e_(bank_i), B=e_(bank_i)^T V^-1 gives
`V X_i V^-1=I+A(X-I)B`, with `BA=I`. Every row other than bank_j imposes a
linear operator equation on X. If one such equation has invertible single
Clifford-ray left/right factors, it determines X uniquely. Every coefficient
and the resulting Y bank factor is then checked. The finite q2 screen covers
15 nonempty tail-native subsets and703 prefix unary-site pairs,10,545 cases.
Its single-ray-equation branch accepts183 Clifford pairs, none below mass80.
This is not a general two-site lower bound: it records unresolved strata.

For a nonzero off-bank right side H, one surviving Clifford ray h in
`A X B=H` must equal a X b up to phase for some rays a,b. Thus X lies in the
finite canonical-ray list `a^-1 h b^-1`. The auxiliary cover verifies all
Gaussian-unit phases and every remaining coefficient. Homogeneous equations
with zero right side are retained as separate strata, not discarded. Distinct
uniform Clifford tensor rays can be separated for sufficiently large tensor
power; no finite-f numerical independence is assumed for these all-f equations.

## The constructive isolated stratum

The successful pair has the transported whole-bank direction isolated in both
row and column. The required correction C is also only that bank. At this cut
the two replacement operators U,W need satisfy

```
W = L U^-1 R,
L = C_jj A_j G_i,
R = A_j^-1 G_j.
```

All these are actual unitary Clifford families; no nonunit inverse is an
implementation primitive. Let r(T) be the native B-block rank. Subadditivity
gives `r(L)<=r(W)+r(R)+r(U)` and the reverse inequality with L,R exchanged.
Consequently `r(U)+r(W)>=|r(L)-r(R)|`.

The lower bound is constructively attained. Offline selected-native lowering
gives exact signed, phase-complete Bruhat factorizations

```
L = L_left F_a L_right,
R = R_left F_b R_right.
U = R_left L_right.
```

U is a physical monomial. Therefore
`W=L_left F_a F_b R_right`, whose native arity is `|a-b|`; the overlapping
canonical chirps square to a Pauli translation. Neither L nor R is executed.
Only the emitted physical monomial U and one selected-native implementation
of W are executed. General physical Gaussian quadratic-phase monomial adapters
are permitted here; restricting the first replacement to X-character monomials
would miss the construction.

At q2 the changed sites are31(query3 source swap,bank2) and51(query4 source
swap,bank1), and the deleted tail is the whole U-coordinate recovery of arity6.
The actual ranks are a=4,b=2, giving new site ranks0,2. At q3 the changed sites
are39(query3 source swap,bank2) and97(query6 source swap,bank1), the same tail
recovery is deleted, and a=8,b=6, again giving new site ranks0,2. These are
literal event indices in the pinned event-only fixture, not inferred source
positions in a modified word.

The complete histograms are respectively

```
q2: H2=36,H4=1; mass76; stock6*12=72.
q3: H2=64,H4=1; mass132; stock8*16=128.
```

The target remains exactly diag(F_k J) on every independent original input,
including the two original pivot owners and every public field. All right
gauges remain in the exact operator. The general Clifford tensor algebra checks
the full matrix, full inverse and both inverse orders for every positive f.
These q2/q3 facts are not promoted to an all-q formula.

## Phases, native lowering and paid scans

Each emitted unary is one fixed one-coordinate Clifford O, tensor-lifted f
times, with an explicit Gaussian-unit scalar for each f mod4. This keeps the
global i applied once per whole field, rather than once per tensor coordinate.
The native W child and its inverse are lowered independently with exact
Gaussian phase. The admitted current-event schema binds every unchanged native
to the repaired source recipe, including its embedding. Only used forward and
inverse recipe definitions remain in the pool.

Every physical D/P/X/unit instruction is a paid full-field scan. The first new
monomial has its actual literal circuit recorded. The later native child uses
two four-instruction monomial adapters plus at most one extra global-unit
control, in addition to the one native child. Their scan counts are independent
of f; their address/phase arithmetic still requires the usual explicit local
controller cost. The selected children have arity2f or4f at ambient12f/16f,
strictly below the pinned proper child cap. No dirty helper or private zero
field is introduced.

The serialized inverse is generated from the actual current circuits, phases
and recipe pointers, then replayed independently. A forward recipe pointer
substituted into an inverse native event is rejected. A Gaussian phase changed
only at f=2 mod4 is rejected while f1 is unchanged. Omitting the changed free
monomial alters original-input columns. These controls test operator/native
admission, rather than merely the internal inverse matrix.

## Bounded continuation and remaining gap

After the q2 mass76 word, the bounded continuation removes any nonempty subset
of the remaining3 tail native sites and tests every two-prefix-unary pair in
the isolated-whole-bank stratum. There are7 subsets and703 pairs. It finds no
eligible isolated correction;34 pairs fail two-sided isolation and4,887 have
a correction involving more than one bank. This does not exclude a coupled
two-bank correction, more changed sites, different source/response chronology,
or an outer boundary with different required outputs.

Positive native saving still requires crossing the remaining four mass units
and satisfying the complete outer cost/owner/phase interface. Neither the
finite exact census nor the isolated-pair rank lemma is a lower bound for
arbitrary callers, and no formal-kernel theorem is claimed.
