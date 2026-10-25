# Native observations, a complete local consumer, and a terminal decoder

Substantial OpenAI assistance; Apache-2.0. The source QQ16 construction,
retained mixed supplier and current-frame affine-map conventions are credited
through the pinned source files and the cumulative package's notices.

## Results

This directory closes two concrete operator contracts. Neither is a new
multiplication bound.

| Construction | Exact result | Native child bill | Owned full-cover fields |
|---|---|---:|---:|
| One current ordinary-Y observation | An owned completed-frame copy of the original hole-framed Y; source preserved | 1 H1 per copied port | 1 per live output |
| Fused current-pair acquisition and consumer | The complete repair `H_(s,t) B_t F_s(x,y)=(-y,x+y)` for the changed 104-port local pair | 208 H1 per pair | 17, all returned zero |
| Complete terminal content decoder | `D_final Q^-1 D_final^-1` for the literal nine-call, four-bank-pair content schedule | 832 H1 | 8, all returned zero |

The second construction is the most useful new closure. The sibling
`weighted-sideinfo` program acquires the needed current queries for 104 H1.
The complete consumer costs another 104 H1: eight selected X-to-Y transfers
and 96 ordinary Y corrections. It uses the same 17-field stock by consuming
selected observations early. There is no extra eight-field saved-Y bank.
See [PROOF.md](PROOF.md) for the complete formula and chronology.

The full literal local program has, **per pair**, 208 positive H1 children,
416 line-wrapper monomial maps, 8,800 further physical affine maps, and
42,016 real scalar primitives. These counts include the query acquisition,
all selected and ordinary output corrections, and retirement of all owned
fields. They exclude the producer's existing local core, the producer's
separate new wrappers, and the still-unconstructed global hosting and idle
profile. Every routed read is lowered to a map on its source, a distinct-target
scalar ADD, and the exact inverse source map. Sources can change during that
three-operation view and are restored when the view ends.

The terminal construction takes a different approach: normalize all current X
fields into the common final frame, invert the entire content word, then put
all X fields back. There are four pairs, hence **416 X fields**, not 104.
Two adapters on each of them cost 832 H1. This word has 1,664 line-wrapper
maps, 6,656 further physical maps, and 185,568 real scalar primitives. Its
complete schedule is bound to the retained owner template, including bridges
and the signed terminal exchange.

## What the paid bill says

The earlier changed-producer wrappers cost 64 H1 across the nine-call screen.
Both explicit routes therefore reach an extra native bill of **896 H1** when
the four local pair consumers are counted, or when the terminal decoder is
used. This numerical equality is not a proof that four local repairs can be
spliced into the retained nine-call controller. Later local calls lie on
different bank pairs and are separated by bridges. The terminal decoder
includes that full content schedule; the local-pair repair still needs a
global composition.

The inherited *relaxed* controller allowances from the frozen package are:

| Primitive target C | Inherited allowance | New 896-H1 bill exceeds it by |
|---|---:|---:|
| 0.001745 | 571.332681182781… | 324.667318817218… |
| 0.004 | 155.819896738978… | 740.180103261021… |

These are screens based on the old weight and idle accounting, not certified
moments for the changed 104-port geometry. They already reject the explicit
new native bill before new ownership or scalar/address-work obligations.
The retained outer conversion is `κ=C−10^-46−10^-70`; the ordinary
`C/(1+C)` conversion is not used by this retained package.

The 104-H1 query acquisition remains a real improvement over the earlier
16-H8 acquisition at this interface. However, keeping its four-pair bill of
416 H1 and the 64 producer wrappers leaves only 91.332681… at C=.001745 for
all consumers and other new costs. An equally distributed consumer allowance
would be less than 22.833171 H1 per pair, compared with the explicit 104.
More than about 78.045% of that consumer's native bill must disappear even
before hosting. At C=.004, the acquisition and wrapper bill alone fails.
That target needs an additional source, geometry, or normalized-operator
change, not just faster retirement of these query fields.

A more specific next target is to retain the eight selected transfers per
pair. They consume 32 of the remaining 91.332681… units, leaving less than
14.833171 H1 per pair for the ordinary response. If that response could be
realized through eight native rank-one channels, the total screen would be
544 H1 with 27.332681… left for other new native costs. This is an unproved
budget target. A candidate must realize the full operator-valued response
`K_s,U−K_t,U M^-1` in all distinct Y hole frames; scalar rank eight alone
does not establish such an implementation.

## Physical frame facts

Let `F_t` denote the completed rank `9+8t` frame. At a local repair boundary,
X is in `F_t` and Y at port p is in `F_t C_qp^-1`. A copied Y observation
therefore needs one positive `C_qp` to become a completed-frame field.
A completed correction needs one negative `C_qp` before adding to that Y.
The signed line recipes use positive H1 children with explicit linear and
translation wrappers; their complete 512-column local kernels are checked.

Owner routes are actual 73-dimensional binary matrices. They are never
collapsed to a single scalar owner. An owner map g is given its actual
translation δ so that its complete Z4 phase polynomial preserves `F_t`.
The inverse map includes its correct affine translation. This is why
completed-frame query synthesis is legal and ordinary uncorrected route
substitution is not.

The final named X and Y banks are not in identical physical frames. The
terminal exchange leaves X in `F_final C_qp` and Y in `F_final`, where
`F_final` is the completed rank-73 frame. Thus a content
correction must be conjugated by `D_final`; merely emitting `Q^-1` in the
current physical registers is not valid.

There is also an exact, restricted whole-word obstruction to moving away an
X-only subset of those final adapters. On the owner-constant all-ones payload
character, all actual corrected owner routes act identically, while every
port line acts by i. The dyadic Q matrix has one connected support component
containing all 416 X and all 416 Y fields; 173,400 off-diagonal nonzeros are
witnessed modulo 65,521. A commuting X-only adapter mask would have to be a
union of components, so no nonempty such mask works. This rejects a specific
commute-and-cancel strategy. It is not a lower bound of 832 children for
arbitrary new decoder synthesis or changed source encodings.

## Evidence and reproduction

Python 3.12 or newer, standard library only. The scripts support isolated
mode. From this directory:

```sh
python3 -I -O -B observation_probe.py --output /tmp/OBSERVATION-NEW.json --word-output /tmp/OBSERVATION-WORD-NEW.json
python3 -I -O -B consumer_probe.py --output /tmp/CONSUMER-NEW.json --word-output /tmp/CONSUMER-WORD-NEW.json
python3 -I -O -B controller_probe.py --output /tmp/CONTROLLER-NEW.json --word-output /tmp/CONTROLLER-WORD-NEW.json
```

The cumulative replay compares parsed outputs with the committed receipts.
The consumer needs the sibling `weighted-sideinfo` directory; its code,
literal word and receipt are byte-pinned in `sources/QUERY-SOURCE-PINS.json`.
The two underlying QQ16 data files are byte-pinned in `native_common.py`.
The complete retained owner template is independently byte-pinned in the
terminal decoder, and the extracted recipe must match it exactly.

| Program | Receipt and literal word | Main verification |
|---|---|---|
| `observation_probe.py` | `receipts/OBSERVATION.json`, `OBSERVATION-WORD.json` | Signed kernels, all new completed-frame maps, dirty-source and wrong-line controls |
| `consumer_probe.py` | `receipts/CONSUMER.json`, `CONSUMER-WORD.json` | Four stages, 208 independent current input fields, actual owner products, independent free-query consumer, 32 semantic controls |
| `controller_probe.py` | `receipts/CONTROLLER.json`, `CONTROLLER-WORD.json` | All 27 low-rank macros, both literal scalar inverse orders, both whole scalar-sector inverse orders, signed endpoint kernels, whole-Q commutation screen |

The consumer's operator proof is compositional. The acquisition prefix is
expanded on all independent data and initial owned dirt. The suffix is
expanded on 16 independent free query fields; substitution of the proven
prefix gives the data-dependent result. The actual same-port unit identities
then prove composition with the changed producer. The terminal proof likewise
composes individually checked transvections and elementary inverse words. No
receipt claims to have expanded an exponentially large 73-dimensional
whole-supplier matrix.

## Research direction after this closure

The ranked literature and its quantitative relevance are in
[PRIMARY-LITERATURE.md](PRIMARY-LITERATURE.md). The highest-value next target is
a functional correction interface: produce or consume the final low-rank
response without separately normalizing every ordinary Y target. A concrete
candidate is to inject the correction through an already paid compatible
scatter inside the rebased clean-J core. Such a proposal must match the
query's current physical gauge, every owner route, timing, arbitrary helper
restoration and actual final scatter. That compatibility is not proved here.

Another viable search changes the producer or the normalized code so the
required response already lives in the consumer's hole frames. Coherent
changes of coordinates alone do not alter a fixed normalized operator, and
scalar collapse of owner routes cannot establish this interface. The new
local closure provides exact targets and a complete invoice against which to
judge a replacement.
