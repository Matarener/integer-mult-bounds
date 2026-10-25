# Shared-source tours and the independent helper-dirt bill

This is a scoped failure of one query-sharing mechanism on the selected packet,
with a separate four-ADD scalar sharing control. It is not a universal
noncommuting tariff. All payloads are arbitrary Boolean
functions; `+` is XOR. Address pullbacks `p,q,r` are exact involutions, with no
commutation assumption. We first work in the full group algebra
`F2[C2*C2*C2]`; reduced words form its basis. Algebraic identities descend to
every admitted address action. A formal *nonidentity* needs a separate guard
before it is used as a failure witness in a quotient address representation.

## A genuine shared-source identity, and its limits

For invertible operators A and B, the chronological word

```
x <- A x;  y += x;  x <- B A^-1 x;  z += x;  x <- B^-1 x
```

has endpoint `(x,y+A x,z+B x)` on three independent dirty inputs. The source
returns exactly to its entering state. The only target reads are of x; no
target dirt is used as a source. With separate source tours as comparator,
and a literal implementation price C for each specified transport, the bill is

```
shared:   C(A) + C(B A^-1) + C(B^-1) + 2 ADD
separate: C(A) + C(A^-1) + C(B) + C(B^-1) + 2 ADD.
```

This formula charges *the current relative pullback* `B A^-1`, not B. If A=p
and B=qp for noncommuting involutions, chronological
`p, ADD_y, q, ADD_z, q, p` costs four queries versus six separate queries.
The last two gates must be q then p. Reversing their order leaves the source
with operator `qpqp`, which is nonidentity in the free product. This is a
positive control only: the actual selected packet does not require these two
shears as its complete endpoint.

If source x cannot be temporarily warped, use an arbitrary dirty helper h.
Write T for the preceding complete source tour, with h in place of x, including
the target ADDs. Execute `h+=x; T(h); h+=x; T(h)`. The two tours contribute
`A(h+x)+Ah=Ax` and `B(h+x)+Bh=Bx`, and h is restored. This costs twice the
entire query tour, four target ADDs, and two COPY-as-ADDs. It uses one arbitrary
dirty helper, with no erase or assumed zero. Charging the echo is essential.
For the prefix control its invoice is eight queries and six scalar ADDs.
Separate dirty-helper realizations of the same two shears cost twelve queries
and eight scalar ADDs, but are a different interface from mutable-source tours.

## The actual packet has independent dirt columns

The source audit identifies source17, helper444 and helper413, all in frame509
at the two selected ADDs (records 23325 and 23333). The affected scalar prelude
is an invertible map L. In chronological order its changed rows are

```
h444 += x17 + a271 + b293 + c352 + h413(old) + d468 + e470
h413 += x17 + a271 + b293 + c352 + f371 + e470.
```

The helper413 term in the first row means the current coordinates must be
used; treating both helpers as simply `d+x` in a common old coordinate system
would lose a real cross term. Let d and e denote the displayed rows with just
their x17 term omitted. These are independent dirt-bearing linear forms,
since deleting those two source ADDs leaves an invertible scalar word L0.

The primitive queries are p on helper413 at record23405 (frame509 to390,
rank2) and q on helper444 at23424 (509 to392, rank2). Their address labels
do not commute. Gates on distinct helper slots do commute as operators if
the surrounding reads and delivery cuts are suppressed; these are different
statements.
The required helper values at these deliveries are `p(d+x)` and `q(e+x)`
(with d/e labelled by their own helper). Source-only sharing produces
`d+px` and `e+qx`. The absent terms are `(p+1)d` and `(q+1)e`.
They cannot be supplied from x, whose input is independent of every helper.

More invariantly, the pair-query abstraction has endpoint `F0=D L`, where
D is identity on the source and the appropriate diagonal p,q on the helper
rows. Thus `F0 L^-1=D`. In the slightly larger checked packet, the retained
read605 and rank1 move give `F=K D L`, with
`K=R413(r) ADD(413,605)`, so `K^-1 F L^-1=D`. K is retained paid work,
not a free map. Scalar sharing has not removed the heterogeneous diagonal
demand on independent inputs. These are reductions of contracts, not lower
bounds for an enlarged noncommuting alphabet.
In particular, diagonal S3/D8 results from a different alphabet are not imported.

The source audit also expands the scalar state at cut23339 in its original
public/helper coordinates (integer signs are retained here, then reduced
modulo2 for this Boolean proof):

```
V413 = h413-h469-h605+x87+x17+x22+x33+x60+x67+x92
V444 = h444-h369+x77+x17+x22+x33+x60+x87+x38+x92.
```

Both contain `C=x17+x22+x33+x60+x87+x92`, but C is not an available
clean operand. The six original sources have frames509,182,185,62,189,184,
respectively. The same-frame scalar sum `V17+V271+V293+V352+V470`
instead contains independent helper dirt. We do not price either sum as free;
the concrete repaired word moves only the already available source17.
Distinct h413 and h444 pivots certify independent residual dirt even after
the common original-source terms are removed.

## Exact compensating word and full price

There is a simple fully paid repair, which makes the missing work explicit.
Remove only the two x17 ADDs from L. Retain both original helper queries.
Immediately after the p-query, before the next helper413 read/update, execute

```
x17 <- p x17; helper413 += x17; x17 <- p x17.
```

Immediately after the q-query, execute

```
x17 <- q x17; helper444 += x17; x17 <- q x17.
```

Each source excursion returns source17 to frame509 before any other reader.
The original source17 contributions are restored at each required delivery,
and each helper's entire independent dirt is transported by its retained
original query. No new helper, source copy, scalar basis change, CLEAR,
zero-initialization assumption, or deferred source restoration is used.
Both copied source ADDs are relocated, not added to the scalar count.

The nearby fixed gates `helper413 += source605` at23406 and its rank1 move
390 to517 at23407 illustrate why one cannot wait until the helper444 event.
After the later move the missing pullback is `rp`, not p. Our exact checker
includes both gates and rejects the stale-p compensation. The source audit
must separately verify that helper444 has no intervening consumer of its
temporarily omitted x term and source17 remains unchanged across each window.
The algebra does not grant that scheduling premise for free.

Writing H2 for the charged rank2 query price, the selected-job comparison is

| Work | Original | Repaired source tours |
|---|---:|---:|
| Original helper rank2 queries | 2 | 2 |
| Added source rank2 queries, including returns | 0 | 4 |
| Selected source ADDs | 2 | 2 |
| New helpers / CLEAR / hidden copy | 0 | 0 |

The complete delta is **+4 H2**, strictly unfavorable whenever H2>0. All
unselected scalar gates and the rank1 helper413 move are identical. The checker
prints the displayed formal subword's bill: 14 scalar ADDs and one rank1 query
in either word, with two versus six rank2 queries. This subword suppresses
unchanged intervening gates and source-preparation transports; it is not the
full contiguous native packet. The source audit bills those unchanged records
in the complete comparator. In a caller that also literally
reverse-inverts this entire edited non-target word, all four added source
queries occur again: the delta is **+8 H2**. This second invoice is conditional
on that caller's cleanup exclusions, not an assumed global supplier delta.

The general reason source-only compensation cannot work is a block invariant:
source warps and target additions sourced solely from x keep the helper-dirt
coefficient block equal to identity. The required block contains p and q.
This proves failure for every number of source-only excursions and arbitrary
scalar linear combinations of the shared source. A proposed mechanism that
mixes independent helper dirt back into a source is outside this class and
needs a new full word; we assert no tariff for it. Even in the repaired class,
we claim the invoice of the displayed schedule, not universal optimality.

## A separate scalar sharing control that does save four ADDs

There is a useful positive composition in the actual fanout prelude, distinct
from reducing paid queries. Let `a=h444`, `b=h413`, `u=V468`, `v=V371`,
and `C=V17+V271+V293+V352+V470`. Evaluate these entering values at cut23325,
after retiming v371's existing arrival to frame509 and before any prelude ADD.
C contains arbitrary dirt and need not be prepared in a helper. The old
13 ADDs have full integer endpoint

```
a' = a+b+u+C;  b' = b+v+C.
```

Move the existing arrival of v in frame509 earlier, subject to the separately
audited source window. Add C's five actual operand registers to b and then
add v to b (six ADDs). Now execute `a+=b; a+=u; a-=v` (three ADDs).
Using the *current* b row gives
`a+(b+v+C)+u-v = a+b+u+C`, exactly as required. All operands may be dirty;
the signs prove the identity over the integers, not just modulo2. No clean
copy of C, extra helper, source warp, query, scalar inversion or erase is
introduced. Both p and q queries and every later gate remain unchanged,
so their noncommuting labels do not invalidate the exact whole-word equality.

The forward delta is **-4 ADD, zero queries, zero new helpers**. The frozen
R438 Uinverse cleanup is an expanded source-subtraction word, not the literal
inverse of these 13 ADDs; it is unchanged and contributes **zero** additional
saving. Thus the actual full forward word saves four ADDs, not eight.
If one executes a separate complete literal inverse of the changed word,
that inverse also has four fewer ADDs, for eight fewer across that separate
forward-plus-inverse experiment. That is not a second saving in the frozen
forward supplier. The recursive query histogram and its moment are unchanged.

The exact checker verifies this nine-ADD construction over the full integer
group algebra, its composition with the retained queries and their
noncommuting address labels, and
its complete literal inverse. A sign mutant changing the last `a-=v` to
`a+=v` passes the Boolean endpoint but fails over the integers by `2v`.
This makes the integer-lift distinction observable. The [source audit](../source-audit/README.md)
supplies the literal retiming recipe and its current-frame proof; algebraic endpoint
equality alone does not establish that the arrival can be moved.

## Verification, source credit, and open obligations

Run `python3 -I -B algebra/check_shared_source.py` from this package. The script
uses complete finite-support coefficient rows in the *infinite* free product;
it is not a sampled function test or a small nonfaithful address matrix. Its
normal-form multiplication is exact because cancellation of adjacent equal
involution letters is the unique free-product reduced-word algorithm. It
checks every independent input coefficient, all untouched identity rows,
the intermediate helper413 delivery, and literal reverse-inverse cleanup.
It rejects omitted dirt queries, a missing echo inverse, noncommuting inverse
misordering, a stale downstream pullback, and the integer scalar-compensation
sign defect. These are finite exact checks
of explicit words; the displayed algebra supplies the all-input written proof.

An actual-address failure of the omitted dirt queries does not need faithfulness
of the whole group algebra. For any nontrivial partial swap p, choose a moved
address a and helper dirt the delta function at a, with all other inputs zero.
Then `(p+1)d` is nonzero on the two-point orbit. Bijectivity of the scalar
prelude L0 permits that d with arbitrary prescribed spectator values. The
actual projector rank2 certifies such a moved address exists; a concrete
address witness may be attached by the source audit. Positive identities
already descend to every actual action, regardless of representation kernel.

Credit: reversible source-tour cancellation and dirty echo are standard linear
circuit identities, not claimed novel here. Related prior work includes
Yiyang Lu's PR2857 (head `0b2e2537b368a0cade07ce3f71452ea018ebe394`) for
current-coordinate compensation; Marius-Paul Dumitrean's PR2733 (head
`a63c55ff56aaa8645d64d1162d1f017b59ded42a`) and David Arias's PR2766 (head
`e6df920cd0110e4b629e2ad84eddcb539001e174`) for rederived pullbacks and
actual-cut composition; the gauge44-leaver8 historical source at
`87db776d70ad1d28a27e9f7906237e5a279414f3` for the failure of clean maps
that ignore entering dirt. Those sources are methodological leads, not
certificates of this word. The predecessor noncommuting proof supplied only
the diagonal-contract contrast; its finite S3/D8 checks were not repeated.
The new work here is the source17 packet's explicit compensation and surcharge,
plus the independently dirty scalar-prelude composition supplied by this run's
source audit. That scalar construction saves ADDs while retaining every query.

Open next questions: a favorable mechanism must exploit independent dirt
processing, a cheaper legitimate relative transport, or changed delivery cuts;
none follows from shared source17 alone. This local proof does not settle
arbitrary noncommuting mixing, physical owner assignment, native phases,
all-size precision/storage, recursive moments, or conditional kappa. There is
no favorable recursive-query delta to transfer, and no native or formal-kernel
claim. The exact source/projector evidence and literal full-word invoice are
owned by this package's [source audit](../source-audit/SOURCE-AUDIT.json) and
[full invoice checker](../check_invoice.py); the [source notes](../SOURCE-NOTES.md)
retain predecessor pins and construction attribution.
