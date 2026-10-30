# The exceptional owned lifetime cannot lose a delivery stop in this model

This concerns owned role738 in the pinned PR5569 word. Unlike the other seven
owned lifetimes, its descending route has several recipient contacts. We ask
whether one stop can be removed by relocating these five delivery ADDs within
their recipient idle windows, or by replacing a delivery with an arbitrary
linear combination of public registers at one common chart. All surrounding
scalar events, dependencies and contact charts remain fixed. This is a broader
test than the original owned-holder scan, but still a local model.

## Delivery-frame intervals

Role738 is initialized at frame591 of dimension8, copies public role133 and
scales it by -1/2, then is cleared at frame597 of dimension1. Let its copied
value be D. Its five deliveries are:

| Recipient | Source event | Coefficient of D | Allowed contact dimension |
|---|---:|---:|---:|
|159|13412|-1|7|
|203|13414|2|6|
|148|13417|2|3 or4|
|710|13420|1|1|
|734|13422|1|1|

The intervals are derived, not assumed. Remove the nominated delivery from
its recipient's scalar chronology. Let A and B be the preceding and following
remaining scalar-contact charts. A public recipient at a new contact F needs
A subseteq F subseteq B. The descending owned route from591 to597 needs
597 subseteq F subseteq591. Therefore

```
span(A + 597) subseteq F subseteq B intersect 591.
```

Exact binary spans yield the table. For recipient148 the lower endpoint has
dimension3 and the upper endpoint dimension4; the other intervals are single
subspaces. Reordering cannot evade the resulting strict descending dimension
order. Every route still includes

```
8 -> 7 -> 6 -> {3 or4} -> 1.
```

For either choice the direct route through the mandatory stops has paid
rank histogram 2H1+H2+H3. Here H_d(t)=d^t for 0<t<=1. Recipient148's
own route is2->{3 or4}->5, with histogramH1+H2 in either case. Additional stops
cannot lower an increasing concave tariff; they split a rank into smaller
positive pieces. No paid stop disappears in this changed-contact family.

The feasibility and costs of other scalar events have not been weakened. The
table is already enough to rule out a gain from rearranging these deliveries.

## Why multiple public partners do not bypass one nominated delivery

The normalized public transfer matrix is invertible at every source cut. This
is certified structurally, without a large numerical rank calculation:

1. Public ADD and nonzero SCALE are elementary invertible row operations.
2. Each source owned lifetime copies one public producer and only scales that
   copy. The producer remains unchanged throughout the owned lifetime.
3. An ADD from that owned copy to a *different* public destination is therefore
   an elementary public shear by the still-present producer row.
4. INIT, CLEAR and MOVE do not change the normalized public rows.

The checker verifies all these conditions on the complete source program:
20,947 effective public ADDs, including33 owned-sourced shears, and707 nonzero
public SCALEs. Thus the735 current public rows form a basis at every cut.

For each cut, D consequently has a unique coordinate vector c in that current
public basis. Its initial vector is derived by exact symbolic replay to the
owned COPY. Thereafter coordinates can be transported exactly through each
elementary operation. For `row_r += q row_s`, the fixed functional's coordinates
change by `c_s -= q c_r`; for `row_r *= q`, they change by `c_r /= q`.
The checker confirms that c is exactly `-1/2` on role133 and zero elsewhere
both after the producer's final contributing event13376 and at the owned
copy/scale boundary13410. Earlier cuts are included through the same exact
coordinate propagation.

Any public-only linear combination equal to D must use every public row in
the nonzero support of c. Extra public partners cannot cancel this requirement,
because the entire public row family is a basis. At a single common contact,
all these necessary rows and the recipient must share a feasible chart.

The checker examines every boundary in each recipient's idle window after
removing its nominated delivery:

| Recipient | Inclusive preceding-contact boundary | Exclusive next contact | Cuts checked |
|---|---:|---:|---:|
|159|13363|15575|2212|
|203|13245|14027|782|
|148|13233|14018|785|
|710|817|13524|12707|
|734|804|14006|13202|

At all29,688 recipient/cut pairs, the necessary public support and recipient
contain a pair of incompatible scalar windows: some vector in one lower
boundary chart is absent from another upper boundary chart. This rules out
every common chart, not just the original delivery chart or listed frames.
The recipient's own coordinate in c is zero throughout each tested window,
so there is no omitted self-SCALE alternative.

Removing the nominated ADD is compatible with using the original donor rows.
Before that ADD nothing differs. Afterward and before the recipient's next
scalar contact, only its own row differs, by a multiple of D. The checked zero
recipient coordinate means the same coordinates on all other public rows still
represent D; those donors and their windows are unchanged. This is a test for
one nominated public replacement with its surrounding contacts fixed, not a
simultaneous synthesis theorem for multiple changed public dependencies.

These are necessary geometric tests over arbitrary rational coefficients.
They therefore rule out the narrower dyadic legal scalar model without a
separate dyadic synthesis search. The result is a source-derived obstruction,
not a failed search over possible partner counts or coefficients.

## Scope and controls

This does not exclude new owned copies, multiple-chart delivery networks,
changed surrounding scalar dependencies, changed source/terminal boundaries,
or a different target functional. In particular, public-basis uniqueness does
not make owned copies useless: a copy can carry the same value on a descending
chart precisely where its original public producer cannot go.

Four semantic controls reject changing a copied producer while its owned copy
is live, a zero public SCALE, an altered target functional, and a false zero
separating vector. A two-register positive control checks the direction of the
inverse covector update. The root package authenticates source bytes and checks
the entire original arbitrary-input map independently of this local gate.

No new kappa, global optimum, or general barrier to owned-temporary cleanup is
claimed. The useful conclusion is that a successor mechanism must change a
specific dependency or boundary rather than further optimize these five
fixed-neighbor delivery windows.

Source and contributor attribution are the same as README.md and inputs/README.md. Prepared with
substantial OpenAI Codex assistance; Apache-2.0.
