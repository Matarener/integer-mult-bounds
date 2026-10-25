# Conditional outer saving 0.00247755 with a specified uniform rank

This result uses the modified native invoice and tensor construction in
`NATIVE.md` and `TENSOR.md`, together with the native, finite-precompilation,
delayed BIT cover, precision/storage, and inherited outer hypotheses of
zxv's PR4359 at `da637c87c89482bc4c86be36bd0071b3d400dbed`. It does not
independently formalize those hypotheses or change the selected frontier.
Apache-2.0; substantial OpenAI assistance.

The native productive-job construction is credited to zxv's PR4359 and
integer mixed flow to Jacob Alan Sussman's Theorem 1G. The outer slack
family and ledger are retained from PR4405, commit
`873d1b3c96a83b701a5c0bba8e37a861e6672fef`, which credits @Vlado-V's
PR1673, @jeremykothe2's PR1758, @chafreaky's PR1786 and the earlier lineage.

## Exact result and source changes

The proposed conditional running-time bound is

```
T(n) = O(n (log n)^(1-kappa)),    kappa = 0.00247755.
```

The gain is `0.00017755` over PR4359's `0.0023` and `0.00017246` over
PR4405's `0.00230509`. These differences compare exponent savings.

The source-bound native invoice uses a fresh arbitrary field for every
original native helper, restores the 56 complete rank-eight owned-center
jobs, and pays every retained idle window as one complete transform.
It gives no productive credit to owned storage. Its exact moments use

```
targets = {5:196, 6:126, 7:392, 8:651, 9:1491, 25:448, 57:224},
paid    = {1:17409, 2:4991, 3:1568, 4:714, 5:140, 8:504, 16:448}.
```

The native target and paid total ranks are 47075 and 46851. This invoice
has paid ranks above its smallest target. `TENSOR.md` therefore supplies a
new finite construction before using the original strict-separation compiler.
The modified invoice alone is not being admitted directly.

At the exact tested saving `C_test=0.00247756`, put `tau=1-C_test`, and let
`P_tau` and `T_tau` be the paid and target moments. The certificate proves

```
P_tau/T_tau <= 1 - 1/10^9,
46851/(4^C_test * T_tau) < 999/1000.
```

Tensor 15000 copies using the chronological construction, and split each
paid rank larger than `4^15000` into consecutive disjoint pieces of at
most that rank. The normalized paid moment of this explicitly defined
finite mixed unit is strictly less than

```
1/(1 + 15000/10^9) + 2*(999/1000)^15000 < 1.
```

Its paid ranks are at most `4^15000`, while target ranks range from
`5^15000` through `57^15000`. Thus the original compiler's strict separation
is restored. Tensoring and splitting preserve a positive rank-one surplus,
because `47075^15000 > 46851^15000`.

## An explicit uniform rank for this large mixed unit

Write `v=15000` for the tensor exponent, and set

```
kappa   = 0.00247755,
d       = (C_test-kappa)/7 = 1/700000000,
uniform = kappa+6*d = 1734291/700000000,
t       = 1-C_test,
z       = 1-uniform,
z0      = (t+z)/2,
delta   = z0-t = 1/1400000000.
```

The source rank parameters satisfy `m=57^v`, `k_min=5^v`, and
`r_max<=4^v`. Since `4^8<5^7`, the exit exponent is strictly below `7/8`.
We may use `h=1/8` in the source/exit proof. At ambient rank `x>=m`,

```
m E(x)/x < m^h*r_max*x^(-h)
          < 2^B*x^(-h),       B=(2+6*h)*v=41250.
```

The second strict inequality follows from `4=2^2` and `57<2^6`. The exact
complement coefficient is `eta=z0*m^(z0-1)`. Because `z0>1/2`,

```
-log2(eta) < 1+6*v*(1-z0).
```

Consequently the entirely rational choice

```
H0 = ceil((B*delta + 1+6*v*(1-z0))/(h*delta)),
H1 = floor(H0*(1-z0)/(z-z0))+1
```

has the same strong-induction property as PR4405's improved compiler bound.
For `x>=2^H0`, the exit coefficient is below `eta`. For smaller `x`, the
elementary rank-one bound `L(x)<=x` supplies the induction base. Hence
`L(x)<=A*x^z0`, with `A=(2^H0)^(1-z0)`, for every positive integer rank.
The strict final inequality gives `L(2^H1)<(2^H1)^z`.

The exact integers are

```
H0 = 2508580090000,
H1 = 8701218254312470001,
N  = 2^8701218254312470001.
```

The final strict power gap is `1/1400000000`. The verifier checks that
`H0>=6*v`, so the induction threshold exceeds the whole finite base range.
It rejects reducing either integer by one in these sufficient formulas.
This is not a minimal-rank assertion.

The tensorized mixed unit and the compiled uniform instruction word have
not been materialized. They are finite exact program recipes, with fixed
numbers of fields and instructions defined by the native tensor schedule,
rank splitting, and source integer compiler. Their astronomically large
constants make this an asymptotic construction.

## Complete outer parameters

Use the PR4405 slack family with the new `kappa`, `C_test`, and `uniform`:

```
b=kappa+5*d,  a=kappa+4*d,  q=kappa+3*d,
epsilon=1-d, beta=1-3*d, r0=d/10, stop=d, layout=d.
```

Keep the admitted ordinary BIT saving `0.0027`, its atom exponent `0.003`,
Strassen exponent `45/16`, theta power `2`, halo power `48`, and core
power `128`. The new tested saving remains below `0.0027`, and the slack
family's algebra applies with `C_test<0.0025` and `d<1/3000`.

The frozen ledger function checks all 54 named outer predicates and three
additional functional predicates. It verifies all nine cost rows exceed
the proposed `kappa`. The main transform remains limiting, with exact gap

```
131141607 / 30625000000000000 > 0.
```

PR4405's separate audit compared the inherited 63-row ledger with this
54-row ledger: all 50 common predicates and all nine cost formulas agreed;
the 13 omitted entries only compared against older historical endpoints.
Raising kappa preserves those comparisons. This package executes the
current 54 admission/reporting predicates and three functional predicates;
it does not rerun superseded historical suppliers.

The new uniform word must use its own scalar, row-stock, movement, and
semantic-precision constants under PR4359's `FINITE-TEMPLATE-CLOSURE.md`.
No old small-word numerical constant is reused. The fixed rational
`epsilon<1`, `beta<epsilon`, and positive stopping exponent leave the
required absorption powers positive. The ordinary BIT template remains
the source's independently compiled and covered template.

## Replay and remaining work

```
python3 -I -O -B research/pr4359-tensor-strictification/endpoint.py
```

The script first runs the exact source-bound native and tensor certificates,
then instantiates the new compiler rank and retained outer ledger. Mutation
controls reject closed precision/uniform gaps, an unfunded outer point,
and an insufficient BIT saving. The complete package verifier authenticates
all source bytes and dependencies.

The result remains conditional on the written tensor closure and the source
native, storage, precision, analytic, fixed-tape, and recovery hypotheses.
Finite arithmetic checks are not a full formal multiplication-theorem proof.
Next questions include independently formalizing tensor closure, optimizing
the tensor power/cutoff for smaller sufficient ranks, and improving the raw
native invoice beyond these source-proven changes.
