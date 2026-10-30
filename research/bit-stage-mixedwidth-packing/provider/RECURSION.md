# PR4183: transfer of the saving through a matched complete recurrence

This note concerns the exact PR4183 head
`928066009267fb32ab2c1a29b50fa3093ea18aef` and canonical source
`12fa8c5c844be21bfefb38a19503fbd867a11244`. The complete finite moment
improves after idle closure and fallback. The companion `caller.py` now
binds both words to the retained all-size logical caller, yielding the
`p=1` stopped recurrence below under its explicit root-coupled contracts.
The stronger finite source invoice and physical transfer retain their
separate premises. The result is a strict improvement of a recursive
majorant; pointwise runtime ordering is not a conclusion.

## Complete finite inputs

The ambient parent has `m=64`, nine stages, 32 replicas and 111 ports:

```
local invocations N = 9*32 = 288
live public families W = 2*4*111*32 = 28416
physical families W+9 = 28425
local helper residual widths = 433 copies of 8 and 5 copies of 4
local helper progress = 3484
copied-total rank = 9*7 = 63
local data progress = 111*14 = 1554
local paid rank mass = 3484+63+1554 = 5101.
```

The actual chronological owner construction determines a nonnegative integer
remainder histogram `I[r]`, including every nonzero pending-axis complement.
It must have total rank mass `339264`. In contrast, the all-width-eight R438
word has remainder mass `333504`. The extra `5760=288*20` is mandatory:
deleting the five rank-four terminal calls returns exactly those ranks to
idle work. It gives no additional zero-exponent deficit.

The independently checked compacted fill has, per replica,

```
I_rep = {2:420,4:435,6:444,7:666,8:6,10:9,14:4,16:3,34:1,42:10}.
```

There are additionally 222 zero remainders per replica, which are omitted
as calls. There are 1998 nonzero children and 10602 ranks per replica.
The global remainder histogram is `I=32 I_rep`; it is the same for both
compared words.

For either frozen five-terminal word or the PR4183 word under the *same
owner construction*, the complete paid histogram is

```
P[r] = 288 H[r] + I[r].
```

Its complete mass is `1808352` and its deficit is

```
64*28416 - 1808352 = 10272 = 32*(8*111 - 9*63).
```

Thus private reserves are not counted as profitable live stock. The
chronological bridge bill is `6*(4-1)*111*32=63936` unit ADDs. There are
`9*288=2592` COPY/ERASE episodes. Neither the bridge nor private charge
vanishes when the local query count decreases.

## Normalized recursion and complete comparison

Write `E=sum_r P[r]`, `epsilon=10^-16`, and `B=32*m^2*E`.
The inherited conservative BIT charge treats each paid request separately:
its exceptional classes have fraction at most epsilon and use at most
`32*m^2` children of width at most `f=floor(n/m)`. The corresponding moment
is

```
mu_P(b) = (sum_r P[r]*(r/m)^(1-b)
           + epsilon*B*(1/m)^(1-b))/W.
```

The raw residual, equivalent after multiplication by `mW`, is

```
F_P(b) = sum_r P[r]*r*(m/r)^b
         + lambda*E*m^b - mW,
lambda = 32*m^2/10^16 = 2/152587890625.
```

This is the ordinary BIT surcharge convention. The complex supplier's
native-exact license does not remove this BIT charge. Each rank is positive
and less than 64, so the moment is strictly increasing in b. A lower endpoint
requires an upper residual bound below zero, while an excluded endpoint
requires a lower residual bound above zero.

For the bound logical caller's moment, take one fixed odd prime `q>2^80`.
Its exact endpoint construction applies to every odd prime and every
`w>=1`. Its actual route implementation consumes the full fixed dyadic
orthogonal charts and uses their transposes; it does not execute the
historical rational Gaussian factorization. The separate finite G240
selector tariff below retains that factorization's admissible-prime
denominator exclusions. Each actual request is a split rank-r idempotent conjugated by a
fresh `g in GL64(Z/q^w)`. The nonzero-minor argument bounds its bad low
classes by `2*64^3/q<10^-16`; the whole high packet inherits that decision.
This is applied separately to each paid request. There is no simultaneous
all-label goodness premise and no extra union factor over the catalogue.
New fixed dyadic charts do not alter that generic degree bound. Using the
fallback allowance for a different child implementation would require that
implementation's own bound.

For the matched owner construction PR4183 changes exactly

```
P_new-P_frozen = 288*(e7-e6-e1),   E_new-E_frozen = -288.
```

Consequently, for every `0<b<1`,

```
F_frozen(b)-F_new(b)
  = 288*64^b*[1+6^(1-b)-7^(1-b)+lambda] > 0.
```

Strict subadditivity of `x^(1-b)` proves the sign. This includes all idle
closure and conservative fallback costs. With positive roots below one, it
implies that the new complete moment root is strictly larger. This compares
the actual two complete histograms; it does not follow from rank mass alone.
At b=0 the ordinary rank mass ties, and only the decreased fallback allowance
provides the tiny strict difference.

The complete profiles are:

| Rank | Frozen five-terminal | PR4183 |
|---:|---:|---:|
|1|380736|380448|
|2|399936|399936|
|3|22752|22752|
|4|25152|25152|
|5|29376|29376|
|6|17376|17088|
|7|26496|26784|
|8|192|192|
|10|288|288|
|14|128|128|
|16|96|96|
|34|32|32|
|42|320|320|
|Total calls|902880|902592|

`price.py` certifies the following strict adjacent root brackets, including
the conservative BIT fallback:

| Complete finite construction | Lower endpoint | Upper endpoint |
|---|---:|---:|
|Original all-width-eight R438|.001734846264120199151475|.001734846264120199151476|
|Frozen five-terminal, new matched owners|.001737388318390108294399|.001737388318390108294400|
|PR4183, same owners|.001737631818486007553483|.001737631818486007553484|

The original R438 comparison uses its actual emitted profile, not an ideal
all-rank-42 remainder allowance. The five-terminal improvement and the
subsequent carrier improvement are separated in the table. The latter
increases the finite root by an amount strictly between
`0.000000243500095899259083` and `0.000000243500095899259085`.
At `b=139/80000=.0017375`, the frozen moment exceeds one while PR4183's
is below one. At `b=.002`, the complete global raw saving exceeds
`1.663199991846095434838270235`; both complete moments still exceed one.

The first arithmetic method uses a positive rational atanh series for
logarithms, a positive exponential series and explicit tails, with outward
rounding on a `2^-224` grid. The independent method uses
`(1-z)^(-b)=sum_n (b)_n z^n/n!`, with integer-grid rounding on `2^-192`
and a geometric tail. No floating point decides an endpoint sign; Decimal
only nominates adjacent `10^-24` grid points. Both methods prove an upper
bound below one at every lower endpoint and a lower bound above one at
every upper endpoint.

Composition through two levels preserves the ordering. If the inherited
uniform normalized child contract applies at both levels, the product
majorant has moment `mu_P(b)^2`; the difference is
`(mu_frozen-mu_new)*(mu_frozen+mu_new)>0`. Floors and the fallback maximum
can be bounded by the increasing proposed power majorant. This is not a
pointwise comparison of measured runtimes or an assumption that every actual
runtime is monotone.

In particular, replacing `T(6f)+T(f)` by `T(7f)` need not reduce an arbitrary
cost function: the three values could be `1,1,10`. The proven comparison is
of the complete power majorants used by the recursive induction. The
902592/902880 counts are per complete finite template; they are not total
counts after recursively expanding every child.

The actual bound trace exhibits the stopping-threshold difference:

| Literal request | Parent width | Child width | Dispatch |
|---|---:|---:|---|
|New rank seven|576|63|Leaf|
|New rank seven|640|70|Internal|
|Frozen rank six|640|60|Leaf|
|Frozen rank six|704|66|Internal|

These four cases are exercised in `CALLER.json`. Thus neither fewer
per-template requests nor a stronger sufficient moment asserts fewer
total recursive invocations or machine steps at every finite width.

## Exact precision and finite source-routing invoice

The frozen positive majorants are `F=8402567,R=630744`; PR4183's are
`F=8401795,R=630740`. The inherited envelopes are

```
P5 = 64 F^3 R^2
P9 = 2^18 F^5 R^4.
```

For both words they require 114 and 211 bits, respectively. The old 104/192
caps fail. Rounding charges upward to a multiple of 64 gives **128/256**;
this change must be disclosed in any native checker adaptation. The new
finite majorant decreases, but does not cross a charged-precision boundary.
This exact integer-lift bound is not an exact rounded COPY cleanup theorem.
These scalar-envelope charges belong to the inherited finite invoice.
They are distinct from the variable address-atom precision w in the
logical caller.

The historical nine-stage invoice is explicit. Let G bound all changed
route/terminal chart factors in the same elementary coordinate alphabet,
with every source selection and inverse charged. Define

```
unit = 288*local_ADDs + 63936
J = 8*32*9*(222+438) + 8*28416 + 2*9*32*438 + 2*2592
high = 16*(64^2+1)^2
good = 8*64^2+8
compiler = 128*(2*64)^3
selectors = 2*9*32*((28416-1) + 438*64*G)
C = unit + J*high + J*28425 + E*(good+compiler)
    + 16*64^3 + 2592 + selectors + P9 + 1
C2 = (C+1)^2*(E+1)^2.
```

The old source used
`G=max_route_factors+144+2+(m-1)+m`; changed charts must justify a new G,
not silently reuse that term. Literal exact address-coordinate operations
enter C here, while a recursive payload permutation must enter P. A claim
that they are merely finite or invertible is not a complete tariff.

The owner certificate replays all changed charts in the unit ADD, NEGATE,
DOUBLE, HALF and SWAP alphabet. It finds at most 151 primitives per
64-coordinate chart sigma, 302 for its application on both address halves,
and 604 for the complete chart/inverse pair. Its field has no extra scratch
cell. The inherited rho15 Gaussian factorization has at most 240 factors,
under its retained finite denominator exclusions. A bound `q>2^80` alone
is not asserted here to discharge those exclusions.
We deliberately retain the legacy 144, 2, 63 and 64 terms and overcharge
the new complete chart pair again inside the outside factor two:

```
G = 240+144+604+2+63+64 = 1117.
selectors = 18051931584
J = 2005440.
```

These are explicit coordinate-operation charges under the inherited selector
implementation contract. They are not a proof that this primitive executes
in the claimed time on a fixed physical tape.

The complete frozen/new unit ADD totals are `10433376/10416672`.
The nonprefix parts of C are exactly
`781063758501377/780986439633857`, respectively, both below `2^50`.
Both complete C values need 211 bits, and both C2 values need **460 bits**,
so the charged depth-two allowance remains **512 bits**. These are actual
arithmetic comparisons, stronger than the sufficient `2^210` nonprefix
budget. With this common overcharged G, the Boolean candidate has smaller
ADD count, E and P9, so C and C2 strictly decrease.

The inherited row coefficient remains
`2*(64^2+1)+9909+252=18355<20161` if the same row theorem applies. The
largest rank is at most 42, giving `2*42^2=3528<4096=64^2`.

Finite prefix increases change absorption cutoffs, rather than the above
moment exponent, *provided* that the all-size compiler and common-grid
contracts charge the operations as stipulated. This proviso is mathematical,
not an implementation detail.

## Bound all-size logical caller and remaining physical interfaces

The stronger ideal `O(V)` local-overhead transfer remains conditional:

```
T(n) <= (sum_r P[r] T(r floor(n/64))
         + epsilon B max_{1<=j<=floor(n/64)} T(j))/W + C,
```

with bounded positive-width leaves. A strict moment below one proves a
power bound by proper-width induction. This requires actual child volume
`V/W`, pointwise spectator restoration, a uniform C, compatible fresh
row stock, exact returned child operators and physical routing at the
claimed cost.

The new `caller.py` supplies source-bound Catalogue and Topology instances
for both literal words to the unchanged generic executable. Candidate and
frozen catalogues have 28206 and 28215 canonical paid labels, respectively.
The exact `CALLER.json` profiles agree with the two complete profiles above.
The same installed topology is passed through every recursive Frame;
native request templates, coefficient grammar and completed return
protocol are retained. `CALLER-PROOF.md` gives the all-size endpoint
induction and distinguishes its finite probes from full-payload execution.
The finite Frame probes use controlled 23-bit child bodies and stock U=11;
they check context propagation and return, not the full compatible-stock
execution. Prime-three operator probes likewise do not test the
`q>2^80` moment domain. The all-size conclusion uses the written
source-bound induction and the stock contract below.

This executable has the baseline primitive tariff `p=1`: routes and
ordinary leaf atom swaps cost `O_q(wV)`. Its source-bound stopped recurrence
is

```
T(n,w) <= Cw                                      (0<n<64),
T(n,w) <= sum_r (P[r]/W) T(r floor(n/64),w)
          + epsilon B/W max_{1<=j<=floor(n/64)}T(j,w)
          + C(n+w)                                (n>=64).
```

Here atom precision w is fixed across one root's descendants. Retain the
original root e, canonical minimal residue/index widths, the encoded
source grammar, and the coupling

```
w>=ceil(e^(17/10000)), n<=e,
2^(h+1)<=8e^2, 17(h+1)<=20051w.
```

The retained preparation argument makes C uniform over these contexts;
C depends on fixed q and the finite provider. Use their maximum as a
common C for the matched two providers. Unrelated long histories or padded
numerical words retain their explicit preparation charges. If
`mu_P(0)<=1-delta_1` and `mu_P(b)<=1-delta_b`, proper-width induction gives

```
T(n,w) <= (C/delta_1)*n + (C/delta_b)*n^(1-b)*w.
```

For the explicit separating rate `b=139/80000`, `price.py` proves
`mu_P(0)<199/200` and `mu_P(b)<1-1/2400000`. A concrete majorant is

```
T(n,w) <= 200 C n + 2400000 C n^(1-b) w.
```

The proof is strong induction on positive n. The linear part pays the
`Cn` toll, and the second part pays `Cw` because `n^(1-b)>=1`. Each
fallback width lies between one and f and is bounded by the increasing
majorant; no monotonicity of T is assumed. Leaves below 64 are covered
by the same constants. The time constant C in this implication is a
uniform primitive-cost constant, not an assertion that the displayed
finite integer coefficient alone establishes that uniform bound.

The compatible row divisor remains

```
K(w)=lcm(28416,28425)*|GL64(Fq)|*q^(4096(w-1))
    =269241600*|GL64(Fq)|*q^(4096(w-1)),
D(n)=0 (n<64), otherwise 1+D(42 floor(n/64)).
```

Using `t*K(w)^D(n)` fresh rows, with positive integer t, gives the actual
child stock

```
U=t*9475*K(w)^(D(n)-1).
```

Every positive child width c obeys `c<=42 floor(n/64)<n`, so monotonicity
of D gives `K(w)^D(c) | U`. The child receives U separately from the
address-spectator product U*B and receives the complete current directory.
Old high fields stay spectators. The runtime check that U is divisible
by 9475 is weaker than the full root-stock premise; it does not replace it.
After j internal dispatches, stock is
`t*9475^j*K(w)^(D(e)-j)`, with excess powers retained for shorter branches.
Capacity is not divisibility, and row padding must be performed once with
pointwise restoration before removing padded rows.

Both providers fit the inherited logical storage ledger: 660 ordinary
roles plus private work fit its 680-packet allowance, their label counts
are below 28278, matrix dimensions are unchanged, and the topology cache
is shared by every descendant of a fixed catalogue. Under the stated
minimal-width/history domain and root numerical arenas of capacity
`2^24`, the bound is `11 V_root+F_q'` live logical symbols. The changed
finite source table changes F_q'; no physical tape or arena/template
cleanup implementation is inferred from that logical reserve.

Under the retained ordinary borrowing wrapper, choosing `w=ceil(e^b)`
gives conditional ordinary interchange saving `b(1-b)`. A larger admissible
b below 1/2 improves this quantity. The chosen `b=139/80000` exceeds
`17/10000`, so this precision choice satisfies the retained lower coupling.
This remains a conditional outer-wrapper implication; its implementation
and numerical cutoffs are not supplied by the caller adapter.

The companion owner proof extends the chart identity and separated low
classes to complete local-ring packets, preserving carries and using the
inverse rather than the transpose of a general GL matrix. This supplies
the uniform owner algebra. `caller.py` now binds the new native labels,
terminal charts and COPY guards to the exact generic coefficient grammar.
The companion source-cut certificate verifies the actual current source50
row at each new read, allowing its intervening temporary mutations.
These bindings and the retained all-size implementation close the logical
`p=1` caller obligation. They do not supply a physical compiler.

This exact logical construction assumes completed exact callees. If rounded
callees are substituted, approximate source subtraction does not establish
an exact ERASE; their return/cleanup theorem remains necessary. Physical
source access, fixed tapes, complete storage, fast routing/leaf primitives
and the outer wrapper retain their own obligations.

The rate `139/80000` is therefore a valid stopped-recurrence rate for the
new bound logical caller on the stated admissible domain, and exceeds the
frozen owner's complete moment root. This conclusion combines the price
certificate with the new source binding; pricing alone would not prove it.
The adapter consumes authenticated unchanged source bytes and does not
alter the historical selected provider or admit the faster selected H2
tariff.

## Comparison to the selected multiplication result

The selected complex endpoint is
`67018507072324140917/40000000000000000000000`
(`0.001675462676808103522925`), with native complex surcharge disabled and
BIT surcharge enabled. Its selected bit endpoint is
`0.001733427039589844234749`. The selected overall kappa is
`836330098538459/500000000000000000`.

A changed bit root above that complex endpoint leaves the current assembly
complex-bound. The source assembly chooses a strict internal rate below
`min(bit_root,(1-beta)*complex_rate)`, bootstraps the ordinary interchange,
then applies the balanced outer map. Therefore even a rigorously admitted
bit improvement does not yield a larger selected kappa with this unchanged
complex supplier. A direct comparison of a local bit root to kappa is not
a joint-assembly proof.

## Source pins and attribution

The concrete new logical binding uses `caller.py` with SHA256
`eda0aedcd1b57451c9fb3ad3b9e696dd3601dc7e956ef55d16819b32a42c6c88`
and `CALLER.json` with SHA256
`e78211b1044de8381fa8bbe1ad674b6ebf5b970e206841216cb91e67b186ce2e`.
Its 84 unchanged source files are authenticated by `CALLER-SOURCES.json`.

At canonical base `12fa8c5c844be21bfefb38a19503fbd867a11244`:

- `research/r438-native-rehost/CERTIFICATE.json`,
  SHA256 `6da8c593257c8440f0fe35488d941715d953d715e2e464ffdfffff7ed31eee9c`.
- `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py`,
  SHA256 `4bf6768224a3fac81ccda26df24f3763f9a4fbc35ad62bef2888595cdae519fe`.
- `research/selected-bit-recursive-caller/PROOF.md`,
  SHA256 `552fa306d5cc228f4d8d8553f8ac5fc6a738ef2b66a2cb765ba0638cd229794d`.
- `research/lean-stopped-recurrence-audit/sources/pr2234/PROOF.md`,
  SHA256 `74cc8de20f21acb5123fe2d20996fe0925ea6e51b3dec633bd5221fb719b3344`.
- `notes/batched-bit-rows.tex`,
  SHA256 `ef72c0ead19373cbc19c8a3aacb44dd0f75353ee5f4d055f775a986a4878022c`.
- `research/community-frontier1094-audit/ASSEMBLY.json`,
  SHA256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.

The moment, two-level tariff, controller and owner mechanisms are credited
to the retained R438/PR589 lineage; the all-size stopped recurrence and
compatible stock are Jose Manuel's PR2234 and the later logical caller by
David Arias. The generic mixed-width transfer is icekylinx's prior work.
This note derives the matched PR4183 substitution and its precise limits.
Written and checked with substantial OpenAI Codex assistance; no independent
human review, new formal-kernel theorem or selected supplier admission.
