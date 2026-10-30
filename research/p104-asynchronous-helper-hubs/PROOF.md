# Temporal helper splits and complete price

## 1. Exact source and interface

The source is PR5774 at `7d6ec0cdef31d0c37b7d2563e709979caa0d5eae`.
Its full official export is retained in `inputs/pr5774-source.tar`.
The verifier checks its archive digest, manifest, exact source pins and every
payload before import. Each nested archive retains its own source checks.
PLAN.json binds the source and every step by canonical JSON SHA256.

Use decoded scalar coordinates. The source endpoint is

```text
T = I + sum e_(r+112) e_r^T, over the 104 live ports r.
```

Let G be the independent helper coordinates whose entrance frame is zero and
whose exit frame is the full nine-dimensional space. T is the identity on G.
All public inputs are arbitrary. Every owned input column must be erased by
INIT and return zero. No new public input is treated as clean storage.

## 2. Time-separated collection and injection

Fix a frame F, a physical helper h, and a cut at which h occupies F.
A collection plan adds scalar multiples of actual earlier fields at F into
one owned buffer. Its complete input row is c, supported on G.
An injection plan adds multiples of that buffer into actual later fields at F.
Its complete output column is d, also supported on G. Require

```text
c d = 1, and d_h != 0.
```

The plans may use different fields at different times. Every collection occurs
at or before the cut. Every injection occurs at or after it. The verifier
computes c by the full rational prefix history and d by the full reverse
rational suffix history. It checks all public and dirty owned coordinates,
not only the helper block. No inverse of a possibly singular prefix is used.

A contact inside a MOVE needs an actual subdivision of that paid native query.
For a forward path A to B, require A strictly contained in F strictly contained
in B. Reverse owned paths use the reverse inclusions. The emitted word contains
both queries. Their native maps compose to the original map with its exact
phase. Their separate recursive costs replace the original cost.

Choose an invertible dyadic basis Q on G such that

```text
Q e_h = d, and c Q = e_h^T.
```

The fixed constructor first adds `-c_j` times coordinate j into h for j!=h,
then scales h by d_h, then adds `d_j/d_h` times h into each j!=h.
The unit pairing proves both identities. Each emitted SCALE has an invertible
dyadic coefficient under the exact scalar checker. All three plans have d_h=1.
Apply Q in the common initial frame. Apply Q inverse in the common final frame.
These operations affect only G, so Q commutes with T.

Initialize the owned buffer at the first collection. The complete collection
now puts the original independent input x_h in that buffer. At the cut, let y
be the current value in the physical field h. Introduce a fresh independent
public input z at F. The two scalar swaps

```text
swap(h, buffer)
swap(fresh, buffer)
buffer <- buffer - h
```

leave h=x_h, fresh=y and buffer=z-x_h. Each swap is three ADDs and a SCALE by -1.
Retire h at F. Rename its entire remaining source trajectory to fresh. Thus the
old continuation starts with exactly its old value y. The later injection plan
adds d(z-x_h) to the complete source output. Clear the buffer after its last use.

Before the terminal basis inverse, the continuing source coordinates have
output `T Q x + d(z-x_h)`. After that inverse they have

```text
T x + e_h(z-x_h).
```

The continued h coordinate is therefore z. The retired physical field holds
x_h at F. Every other output retains its prescribed arbitrary-input value.
This gives two independent targets of ranks dim(F) and 9-dim(F) in place of
one rank-nine target. It proves the scalar construction for all inputs.

The proof uses the actual temporal row and column, a real pivot at the cut,
legal boundary bases, a charged owned lifetime and paid interior access.
A static unit pairing without those conditions is insufficient.

## 3. Three fixed constructions

Time2 equals twice the source event index at a boundary. An odd value denotes
the midpoint of that indexed query. Each row below refers to its own exact
step input; event numbers change after each construction.

| Step | Pivot | Frame | Cut time2 | Collection contacts | Injection contacts | Added queries | New target ranks |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 696 | 1031 | 27044 | 1 | 4 | 1 | 5,4 |
| 2 | 623 | 117 | 26314 | 1 | 5 | 1 | 5,4 |
| 3 | 585 | 245 | 34391 | 2 | 1 | 2 | 8,1 |

In step 1 the buffer collects field696 at time 27026. It injects at times 27044,
27501 and27516. The odd contact subdivides an owned query. Step2 retains its
buffer from time 26314 through 32701 and subdivides a public query. Step3
collects `-field438` and later `field585`; the full row is exactly e_585.
It splits two rank-two queries into rank-one pairs. Every exact operand,
coefficient and original query is in PLAN.json and WITNESS.json.

The final word has 770 public inputs and 25 owned labels, 27 owned lifetimes,
and peak 13 live owned fields. It has 25,973 instructions. All 795 labels fit
the retained 1,000-slot allowance. Each added buffer is initialized, retained,
used and cleared at F; it has no uncharged native MOVE.

## 4. Full invoice and conditional exponent

Write H_r=r^t for t=1-kappa. Relative to PR5774, the local deltas are

```text
Delta P = 4H1 - 2H2 + 2H3 + 2H4 - 2H7,
Delta T = H1 + 2H4 + 2H5 + H8 - 3H9.
```

The net signed gain is
`-3H1 + 2H2 - 2H3 + 2H5 + 2H7 + H8 - 3H9`.
This package certifies its effect at the stated exponent. It does not claim
that this expression is positive for every 0<t<1.

The local paid profile is
`{1:2235,2:452,3:498,4:98,5:159,6:7,7:8}`.
The helper profile is
`{1:26,2:5,3:4,4:105,5:8,7:7,8:22,9:385}`.
The unchanged physical p16/a7 caller has 18 forward local calls, 15 thin query
shears and 3,120 whole idle jobs. The full invoice has 66,906 paid calls and
13,444 targets. The rank surplus is 760. Both the literal caller census and
a separate count by its two path lengths produce the same invoice.

The exact native replay checks 2,926 distinct maps and absolute phases,
1,124 helper normalizers and 208 main adapters. It checks the physical caller's
main contacts, central translations, full main targets and whole idle ranks.
The forward rational replay and independent dense integer transpose each
check all 632,025 endpoint coefficients.

Two rational interval engines check the complete power sums. The raw crossing
lies strictly in `(0.00312265047577,0.00312265047578)`. A derivative bound makes
it unique on [0,.0034]. The claimed saving is 0.00312265044; the tested saving
is 0.003122650445. The gain over PR5774 is 0.00000072917, about 0.0233565%.
It is not a one-percent improvement.

Completion uses cutoff 16, floor 17, tail offset 1/7, power 1024, reserve 10^-12,
decay 125/128 and tail block 128. Exact upper bounds for alpha, gamma and delta
are respectively

```text
0.999999999968708948987649151977
0.975717331211066859570647494583
0.953059856502973038954315738823
```

The verifier checks all three tail ratios, both decay blocks, completion,
splitting, rounding, complement capacity and the finite compiler threshold.
All 54 strict and four functional outer predicates pass. Admitted BIT .0034
remains above the tested saving.

The scalar allowance is 224,990 units. The local route allowance is 5,313,000;
their sum is below 10^7. The complete ordinary bound is 184,647,552, below 10^9.
The source scalar growth bound `2^(16*26000)` still covers this word.
The paid native rank mass is 5,918. The corresponding tensor norm bound is
retained. These are declared bounds, not measured attained norms.

## 5. Checks and scope

Ten mutations must fail: omitted collection, omitted injection, an omitted
paid access query, omitted CLEAR, a wrong fresh entrance, an old helper target,
an omitted owned label, an omitted caller translation, an omitted invoice
query and an invented target. The native checker also rejects a wrong phase.
Normal and optimized replay use explicit checks, not Python assertions.

Discovery used a finite-field temporal span search, then exact rational
construction. It found the same three splits first on PR5751. This package
rebuilds them on the stronger published PR5774 word. The search used greedy
support choices; it does not prove optimality. Discovery software is not a
proof dependency. The fixed rational plan and exact histories supply every
construction choice.

The five inherited framework assumptions remain. The huge uniform word and
rounded multiplier are not materialized. Independent acceptance remains open.
The selected frontier is unchanged. Prepared by Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0; all predecessor credit is in NOTICE.
