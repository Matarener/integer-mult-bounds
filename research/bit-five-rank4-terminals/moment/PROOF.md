# Five-terminal BIT: complete-moment obstruction in the inherited coverage model

The frozen five-terminal word cannot support a joint target κ ≥ .002 under
the inherited odd-stage geometry and two-level child contraction. This remains
true after granting fractional owners, the best possible remainder ranks,
arbitrary additional full-progress stock, zero adapter cost, and zero BIT
fallback charge. In fact, the same obstruction holds through depth ten.
This is a bound on a specified complete pricing model, not a general BIT
lower bound or a rejection of the finite word.

The later `WINDOW-PROOF.md` strengthens this to every depth under the pinned
public controller chronology. The rank60 allowance below requires changing
that chronology and is unavailable in its actual public idle windows.

The exact finite word, integer restoration, and public Boolean action are
inputs established by the frozen producer and independent checker. They are
not reproved by this moment checker. No physical source-to-native compiler,
chronological owner allocation, rounded-error theorem, or outer release is
claimed here. Everything stays local; no new κ.

## Inputs and exact accounting

The portable checker authenticates three bundled files by fixed SHA256:
the frozen `FIVE-TERMINALS.json` profile, the R438 certificate at scientific
Git pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, and the controller source.
The full original handoff manifest and word were authenticated in the run
that produced this package. They are not runtime dependencies of this
arithmetic package. The actual literal word and independent operator audit
belong to the separately bound finite-word contribution; this package assumes
the authenticated local histogram and does not execute that operator check.
See `inputs/SOURCES.json` for hashes and provenance. No sources are modified.

The paid local histogram is

```
H = {1:1322, 2:1342, 3:79, 4:39, 5:102, 6:11, 7:18}.
```

It has 2913 children and mass C=5101. All 36005 scalar ADDs, nine rank-seven
COPYs and one private field remain. In particular,

```
C = 111*14 + 433*8 + 5*4 + 9*7 = 5101.
```

The old R438 local histogram is H+5e4, of mass5121. The changed five helpers
contribute 3484 ranks of helper progress instead of3504. Exactly20 progress
ranks and exactly20 local query ranks disappear together. No extra20 units of
zero-exponent deficit result.

For the original nine-stage, 32-replica public geometry, m=64, calls=288 and
live public stock W=28416. Write w=W/calls=296/3. The full coverage identity is

```
total rank mass/call = (m-1)w + 63 = 6279,
raw stock/call      = mw = 18944/3,
deficit/call        = w-63 = 107/3.
```

Consequently fully hosted old idle mass1158 becomes new idle mass1178. Holding
the old idle invoice fixed after deleting5e4 loses20 ranks of required global
progress. If instead a dedicated helper bank shrinks by its fractional
20/m units of stock, both its raw stock and its full progress bill shrink
by20; the zero-exponent deficit again does not gain20. Actual integral banks
and chronological restrictions can only make this favorable relaxation more
expensive.

## Fixed nine-stage bound, including inherited fallback

Use the raw moment convention

```
F(b) = sum_r Hglobal[r] * r * (m/r)^b,
F(b) < mW.
```

For every 0<r≤R, the cost per rank is `(m/r)^b ≥ (m/R)^b` when b>0.
The inherited two-level strict contraction `m² > 2r²` gives R=45 at m=64.
Thus even arbitrary fractional packing of all1178 idle ranks has cost at least

```
Fideal(b) = A64(b) + 1178*(64/45)^b,
Am(b) = sum_r H[r]*r*(m/r)^b.
```

The inherited conservative BIT fallback is
`τ(m) m^b` per child, where `τ(m)=32m²/10^16`. The smallest possible
fractional child count in this relaxation is `2913+1178/45`. Adding that
charge still gives only a lower bound on the actual complete bill: additional
owner splits, padding, adapters, private transformations or controller
children have not been constructed and have deliberately been priced at zero.

Exact rational enclosures give the following **positive excess** over raw
stock, per local invocation:

| b | optimistic excess, inherited fallback included |
|---|---:|
| .002 | > .67574751495063431348 |
| .003 | > 18.9419819069957543419 |
| .005 | > 55.6656543107476896324 |

Strict monotonicity gives unique optimistic roots. Adjacent exact endpoints
are certified on both sides, rather than inferring rejection from a failed
upper-bound test:

```
without fallback:  .001962938841610 < root < .001962938841611,
with fallback:     .001962938839480 < root < .001962938839481.
```

For comparison of the old and new *ideal* invoices, the maximum gain from
the five retirements is exactly

```
20*((64/4)^b-(64/45)^b)
  + τ(64)*(5-20/45)*64^b.
```

At b=.002 this is only .09711782074669793524... raw units per call. It is
not a20-unit net saving. Improving old owners as well is already granted by
the new all-idle-at45 lower bound above.

## All odd stage counts and arbitrary additional stock

The following is an all-parameter written proof, with exact finite endpoint
checks. Its premises are the **unchanged one-unpaid-coordinate coverage law**
and the same local H. For an odd integer L≥3, set

```
m = 7L+1,
w = 111(L-1)/L,
T = (m-1)w+63 = 777L-714.
```

Allow any additional independent full-progress stock X≥0, measured per local
invocation. Its complete progress mass is mX. The nonnegative remaining idle
mass must be `I=T+mX-C`. Hence

```
X ≥ Xmin = max(0,(C-T)/m).
```

This relaxes integrality, arbitrary dirty-input physical ownership and all
chronological windows. It also grants freely usable ideal channels. At depth d,
the strict halving rule is `m^d>2r^d`, so the cost per idle rank is greater
than `c=2^(b/d)`. A favorable lower bound on excess is

```
E(L,b,d,X) = Am(b) + (T+mX-C)c - m(w+X).
```

Increasing X by ΔX increases this expression by `mΔX(c-1)≥0`. Therefore the
most favorable stock is Xmin. For L=3,5,7, this gives I=0. At b=.002, exact
checks yield excesses greater than13.5540428589,3.8049595866,.8340592145,
respectively, independently of d.

For L≥9, Xmin=0 and I=777L-5815, giving

```
E(L,b,d) = Am(b) + (777L-5815)c - (777L-666-111/L).
```

Treat L as real. Since `Am(b)≥C` and `log(2)>2/3`,

```
dE/dL = 7b Am(b)/(7L+1) + 777(c-1) - 111/L²
      ≥ 7bC/(7L+1) + 518b/d - 111/L².
```

The strict elementary inequality `log(2)>2/3` follows already from the first
positive term of `2 atanh(1/3)`. Multiplying the last lower bound by the
positive `L²(7L+1)` produces

```
P(L) = (518b/d)L²(7L+1) + 7bC L² - 111(7L+1).
```

At b=1/500,d=2, write L=9+x. The coefficients of P in ascending powers of x
are exactly

```
(682923, 699447, 84917, 1813)/500.
```

Every coefficient is positive. Thus E increases on every real L≥9. Its exact
value at L=9 is greater than .66243383606313119872, even after permitting
the nonintegral ideal idle rank64/sqrt(2). Together with L=3,5,7, this proves
failure at b=.002 for every odd L≥3. Each child's raw moment is increasing in
b, so the same statement holds for every b≥.002; in particular .003 and .005.

The same proof strengthens the depth boundary. At d=10, write L=11+x. The
coefficients of P are exactly

```
(2402177, 2649087, 238623, 1813)/2500.
```

Again they are all positive. Exact lower bounds at L=9 and L=11 are
.00894020087916594600 and .01463184725423174600. Therefore all odd L≥3 fail
at b=.002 through depth10. Smaller d has larger c and cannot improve this.
These are global moment screens; they do not certify any depth's native
compiler or precision cost.

## Limits if contraction or coverage is changed

Granting even idle rank m, which is invalid as an actual recursive child,
sets c=1 and drops all idle pressure. With the same fixed H and coverage,
all odd L≥3 still fail at b=.002019323862. The checker verifies L=3,5,7,9,11,13
exactly and proves positive derivative for every real L≥13 using the same
polynomial with `518b/d=0`. Its weakest tested arity L=11 has the cap-free
root strictly between .002019323861174 and .002019323861175. Thus .003/.005
are excluded in this unchanged coverage model even without the depth guard.

There is a narrowly passing *unbuilt* .002 screen outside the inherited
depth-two contract: at L=9 allow fractional idle rank60. The minimum halving
depth for rank60 is11, since `64^11>2*60^11` but `64^10≤2*60^10`. With the
inherited fallback it leaves only

```
raw allowance/call = .00231398661483780488008...
```

for every extra obligation combined. There is no rank60 owner schedule,
source-to-native compiler or depth11 precision/tape proof in this result.
This fractional invoice cannot be used as a supplier. Its existence also
prevents promoting the inherited-model .002 obstruction into a universal
claim about arbitrary changed depth or changed ownership geometry.

New coverage with additional unpaid physical directions, fewer paid COPYs,
different public endpoints, higher-rank consolidation of local children,
changed local H, or useful partial progress across calls changes a premise.
Such proposals require a new complete operator and tariff and are not ruled
out here. A changed rounded precision envelope, by itself, does not change
the local H or coverage equations. The inherited104/192-bit cap failures are
not used as a mathematical obstruction: a valid dynamically charged128/256-bit
or other precision argument could repair precision without repairing the
moment failure.

## Joint and outer consequences

The previous modern planning transfer uses a common supplier exponent b and
produces K<b (its endpoint-24 construction approaches b from below). Thus a
joint κ≥.002 through that map requires both actual suppliers to have strict
complete moments at some common b>.002. The BIT lower-bound failure above is
already decisive for the inherited coverage/depth model, regardless of a
complex-side gain. The parent's current complex four-bank mass68/stock48
invoice independently has no positive deficit; it must not be combined with
this BIT local saving as if either side had passed.

No new joint parameter is claimed. If any changed supplier is eventually
constructed, the owner must bind its full histogram, fallback policy, precision
and row costs, integral whole-helper ownership and arbitrary-input hosting,
native ADDRESS and scalar interfaces, source access, physical storage,
halting/head return, all-size recurrence and every outer inequality at the
same b. The construction/owner and native/rounding specialists own those
separate obligations. This proof does not make any of them implicit.

## Reproduction, arithmetic and scope of evidence

Run from this directory:

```
python3 -B check_moment.py
python3 -O -B check_moment.py
```

The checker uses only Python's standard library, authenticates frozen sources,
and writes `RESULT.json` in this owned directory. Logs/exp use exact rational
atanh and positive Taylor series with explicit tails and outward rounding.
At every requested rational target, independent integer/rational-power tests
check each logarithmic enclosure by raising its rational endpoints to the
target denominator; no floating-point value decides a sign. Decimal strings
are display only. Five negative controls reject lost idle mass, inflated old
helper stock, rank46 at depth2, rank64 recursion and corrupted word identity.

This consists of an all-parameter written inequality proof and reproducible
finite exact arithmetic. It is neither an exhaustive construction search nor
a formal-kernel proof. Historical source premises remain explicit. Credit the
R438 and PR589 geometry, hosting and native-interface predecessors and the
frozen five-terminal producer/auditor; the predecessor joint-frontier screen
supplied the modern raw-moment and fallback conventions. This worker adds
the exact retirement invoice and all-arity/depth obstruction.

Apache-2.0; substantial OpenAI Codex assistance.
