# Cost and family decision for the source-bound producer/collector/consumer join

This note addresses PR3382's complete-cost question for the new, actual source
path. It provides a complete **direct logical operation inventory for the stated
open program**, a ledger of the additional obligations required by a physical
caller, and an inherited conditional stopping test. It does not price an
all-size implementation, declare a new recursive primitive, or admit the whole
P104 word.

## 1. The comparison that would answer the question

A meaningful comparison must implement the same external numerical map on the
same admitted input set, with the same declared frames, reads, dirty-state
restoration and endpoint ownership. If the reference is a physical-coordinate
map `A`, the coefficient-coordinate map `E^-1 A E` is a different numerical
contract until its caller and boundary conversions are specified. Its shorter
internal formulas cannot be compared to `A` after silently discarding those
conversions.

The scientific source is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, retaining ywz65's
[PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586), head
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`. Its chart is
`Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)`. The new numerical admission uses
PR3382's `B9`, on one common grid `2^-f`; multiplying the entire discussion by
that common scale does not change the stated integer divisibility conditions.

The actual producer dependency cone before event 2025 has 257 events and 58
initial dependencies: five dirty `D27` through `D31`, dirty `Q7`, and 52 distinct
`Y` banks. The producer result requires the six dirty banks in `B9` and all 52
initial `Y` banks in `4B9`. Adding the five dirty `G27` through `G31` banks in
`B9` gives the bounded 63-bank internal state through event 4516. These are
mutable numerical banks: the word transports the `Y` arrays too. A physical
borrowed-bank or aliasing manifest has not been supplied.

The open program retains **all actual outgoing reads**, not just the visibly
paired `G` readouts. The destinations are external states whose omitted
histories are not executed by this projection. Each port is the actual
`target += coefficient * current_source` at the recorded event and source
frame. Its increment is Gaussian integral on the admitted internal domain. It
can be added exactly to any current Gaussian target; preserving `B9` at that
target additionally requires the current target to be in `B9`. Neither the
initial `X` producer nor a later external transport is admitted by that local
observation.

## 2. Exact source inventory; no double counting

`cost_audit.py` independently walks destination-first writes backwards from the
six collector entrances. It then selects every write/transport on the 63 named
roles through 4516, the private collector at 2025–2039, and every outgoing ADD
read from those roles. It checks all retained source frames and all internal
target frames, binds every transport to its exact native recipe, and separately
counts both literal wrappers of each recipe. It imports no predecessor Python
implementation.

| Source scope | Events | Native transports | Native rank sum | ADDs |
| --- | ---: | ---: | ---: | ---: |
| Backward producer dependency cone, a subset of the next row | 257 | 200 | 354 | 57 |
| All retained internal work before event 2025 | 412 | 355 | 509 | 57 |
| Collector events 2025–2039 | 15 | 2 | 14 | 11 |
| Retained internal work after collector through 4516 | 149 | 35 | 58 | 114 |
| **Internal total** | **576** | **392** | **581** | **182** |
| **All outgoing ports** | **675** | **0** | **0** | **675** |
| **Open-program total** | **1251** | **392** | **581** | **857** |

The collector's zero and erase account for the two non-ADD/non-transport events.
The 257-event producer is not added again to the 576-event total. In particular,
`257 + 15 + 149` misses 155 retained precollector transports needed by the
complete internal paths and their ports.

| Port source and destination | Calls | Coefficients |
| --- | ---: | --- |
| `Y` to external `D` | 348 | signed quarters |
| `Y` to external `Q` | 171 | signed quarters |
| `G` to external `X` | 104 | 52 coefficients `-2`, 52 coefficients `+2` |
| Initial `Q7` to external `X`, events 492–543 | 52 | 39 coefficients `-2`, 13 coefficients `+2` |
| **All ports** | **675** | **220 coefficients `+1/4`, 299 coefficients `-1/4`, 91 coefficients `-2`, 65 coefficients `+2`** |

There are 83 distinct external target names: 24 `D`, seven `Q`, and 52 `X`.
These names are an interface inventory, not evidence that 83 fresh owned banks
exist or that their storage/routing is free. Their exact chronological records
and hashes are retained in the cost receipt.

## 3. Direct logical schedule and counts

The schedule uses 512 Gaussian coordinates per bank. A rank-`r` native call
executes `256*r` credited signed-floor pairs, with the actual archived right
wrapper followed by the native stages and the actual archived left wrapper.
Each pair has eight real add/subtract operations, four real floor halvings,
one Gaussian quarter turn and four real-component reads and writes. Each
wrapper uses Tekalign's separately specified one-zero-scratch cycle schedule:
`512 + number_of_cycles` Gaussian swaps and 512 unit-phase applications.
These are direct logical counts, not the Turing-machine price of indexed
array access or of a recursive child.

Every field ADD reads both source and destination and writes the destination.
A signed-quarter ADD forms each quotient with two exact real halvings per
component, without mutating its source. A doubled-source ADD additionally
performs one real doubling per component. Phase operations and doublings are
listed separately so a later physical implementation can assign their tariff
without double counting them as ordinary additions.

| Direct logical work for all 1251 retained events/ports | Count | Status |
| --- | ---: | --- |
| Signed-floor Gaussian pair applications | 148,736 | Exact source count |
| Real additions/subtractions in native pairs | 1,189,888 | Exact for the stated schedule |
| Real floor halvings in native pairs | 594,944 | Exact for the stated schedule |
| Gaussian quarter turns in native pairs | 148,736 | Exact for the stated schedule |
| Actual wrapper executions | 784 | Exact source count |
| Wrapper cycles | 23,822 | Exhaustively counted from pinned affine maps |
| Wrapper Gaussian scratch swaps | 425,230 | Constructive cycle schedule |
| Wrapper unit-phase applications, including identity cases | 401,408 | Constructive cycle schedule |
| Field ADDs, including every outgoing port | 857 | Exact source count |
| Real additions/subtractions in these ADDs | 877,568 | Exact for the stated schedule |
| Extra real doublings for 156 doubled-source ADDs | 159,744 | Exact for the stated schedule |
| Exact real halvings for 675 signed-quarter ADDs | 1,382,400 | Exact for the stated schedule |
| **Total real additions/subtractions, before doublings** | **2,067,456** | Exact for the stated schedule |
| **Total when each doubling is one real addition** | **2,227,200** | Same schedule, alternative tariff convention |

The direct component traffic is also retained: native pairs use 594,944 reads
and as many writes; wrapper swaps use 1,700,920 reads and as many writes; field
ADDs use 1,755,136 reads and 877,568 writes. Source reads are a subtotal of field
ADD reads, not an additional charge. Phase transformations act on the loaded
scratch value. Private `C` has 1,024 component initializations and 1,024 final
zero inspections. Semantic restoration of its value is a separate proof; a
frame-consistent erase instruction alone does not prove zero.

The core reference schedule holds `63*512 = 32,256` Gaussian state words,
512 private `C` words, one Gaussian wrapper scratch and four real pair-work
words. Its external target access is a port obligation. No physical owner
identity, dirty helper reuse or independently restored alias is inferred from
these array slots. A 512-entry wrapper plan may be compiled one wrapper at a
time, giving `O(784*512*9^2)` Boolean/control setup operations and `O(512)`
temporary plan entries in this direct indexing model. Setup, plan storage,
bit widths and address access are not zero-cost physical operations.

### A conservative width bound for the complete internal program

Let `H >= 0` be an integer bounding the absolute value of every initial real
component of the 63 admitted physical arrays, measured in common-grid integer
numerators. Each initial Gaussian array has Euclidean norm at most
`sqrt(2*512)*H = 32H`. Every native wrapper is a permutation followed by unit
Gaussian phases, and every coordinate `C` is unitary. Thus every partial
native prefix preserves that norm. The separately proved domain admission
identifies the literal floor word with these ideal prefixes.

Assign every initial bank a rational envelope `w=1`, in units of `32H`, and
assign the owned zero `C` envelope zero. A transport preserves `w`; an internal
ADD uses `w_target <- w_target + abs(coefficient)*w_source`. This triangle
bound deliberately ignores every cancellation. The exact source scan gives
maximum internal weight **49**, first attained at `G27` event 4165, and maximum
outgoing increment weight **50**, first attained at the `X28` port at 3250.
Therefore every internal payload component is bounded by **1568H**, and every
individual port increment component by **1600H**.

For the literal signed-floor pair, put `B=1568H`. If both input components
have absolute value at most the integer `B`, the difference has bound `2B`,
each signed floor of half that difference has bound `B`, the midpoint has
bound `2B`, the second output formula has bound `3B`, and the first output
formula has bound `5B`. Quarter rotation only swaps and negates components.
This proves the sufficient internal pair-work bound **7840H** without treating
negative division as truncation toward zero. A common signed core width `h`
with `2^(h-1)>7840H` is sufficient for these numerical values and arithmetic
temporaries. These are conservative bounds, not measured or minimal widths.

An outgoing target is different: if its current component bound is
`H_target`, the ADD requires capacity for `H_target+1600H`. That current bound,
its external intervening updates and its physical storage remain caller
obligations. The increment bound is not a bound on the complete target. Actual
numerical values on grid `2^-f` scale all these numerator bounds by `2^-f`.

## 4. Complete obligation ledger for a physical join

| Term | Current evidence | Remaining condition or charge |
| --- | --- | --- |
| Actual producer dependence and source reads | Source-bound 257-event cone; 58 initial dependencies | This is a sufficient input contract, not an arbitrary-input admission theorem |
| All 52 strengthened `Y` sources | Initial `4B9` is sufficient; native maps preserve the scaled module | An ordinary-input producer must prove it supplies `4B9`, or supply and pay for a map that changes the inputs and its consumer intertwiner |
| Six dirty producer entrances and five dirty `G` entrances | Declared initial `B9`, with actual empty initial frames | Caller-derived admission and ownership remain to be supplied |
| Internal arithmetic, private collector, downstream restoration | Exact admitted-domain theorem and finite source-bound checks in the producer/consumer work | The frame-path and literal-value certificates must be retained; no claim follows merely from equal final frame labels |
| Native pair, wrapper, quarter and ADD execution | Counts above for a specified direct logical schedule | All-size physical lowering at the actual layout/grid/widths is not established by these counts |
| 675 outgoing read ports | Every exact source, coefficient, frame and event is retained and charged | Recipient availability, current value/width, later consumer admission and external history remain caller obligations |
| Common grid and finite signed width | Constructive bounds `1568H` for internal payload, `7840H` for pair work and `1600H` for each outgoing increment | Actual entrance `H`, current external target widths, grid/field layout and physical guard/storage instantiation remain caller obligations |
| State storage and protected scratch | Constructive numerical array inventory | Physical tapes/records, owner map, alias exclusions, source borrowing, returned work and resident backing storage remain unproved |
| Codec or adapter work | Explicit encoder/decoder per-bank counts are known | Actual conversions at exposed boundaries, required copies and cleanup depend on the chosen external contract |
| Input-independent setup and control | Direct finite wrapper-plan construction has the bound above | Compiling/retaining/routing the actual physical descriptors and handling all caller rows is additional work |
| Recursive children and remaining coverage | Existing fixed-consumer profile/coverage test is inherited below | A changed profile needs its own complete bill; the 581 local rank sum is not a replacement for the full nine-call histogram |
| Outer multiplication transfer | None supplied by this local result | Complete corrections, chronological hosting, physical supplier admission and the transfer theorem remain separate obligations |

In symbols, a completed same-map bill must retain

`C_join = C_admission + C_adapter_in + C_setup + C_internal + C_ports`
`       + C_adapter_out + C_width/routing + C_owned_storage/cleanup`
`       + C_recursive + C_external_completion`.

These symbols are categories of obligations, not terms all measured in the
same unit. The direct logical vector above specifies part of `C_internal` and
`C_ports`. A physical time or space theorem must give each term a compatible
cost model and avoid overlapping charges. Unknown terms have not been assigned
zero. An identical operation stream at identical widths and layouts can be
cancelled from a comparison with the same reference caller; arithmetic identity
alone does not justify that cancellation.

## 5. When persistent coordinates remove conversions

The current positive contract may keep its admitted physical `B9`/`4B9` values
through producer, collector and consumer: no mathematical encode/decode occurs
between those operations. This is valid because admission is an explicit
entrance premise, not because arbitrary inputs can be renamed as lattice
values for free.

A coefficient-state implementation can likewise compose integral
intertwiners. If maps `A` and `B` have the same intermediate codec `E`,

`(E^-1 B E)(E^-1 A E) = E^-1 B A E`.

The intermediate pair cancels only when both implementations agree on the
actual representation, common grid, frame/address layout, ownership and
intermediate observation contract. A source port, restored borrowed copy,
different grid or externally visible intermediate physical value can require
an adapter that this identity does not remove. The raw-coordinate map and
the conjugated map must still be named separately.

For reference, a nine-bit in-place encoder has 2,304 pairs: 9,216 real
add/subtracts, 9,216 component reads and 4,608 writes. Its decoder has the same
counts plus 4,608 exact real halves. Encoding and decoding 63 mutable banks
once each would therefore add 1,161,216 real add/subtracts, 290,304 exact real
halves, 1,161,216 reads and 580,608 writes. This conditional reference does
not prepare `4B9` from arbitrary values, does not handle the 83 external target
interfaces, and does not copy/restore borrowed inputs. PR3382's six-bank cold
codec is not the price of this larger source contract.

## 6. Conditional stop for the unchanged outer consumer

This section restates an existing obstruction; it is not a new P104 barrier.
Jose Manuel first posted the finding in
[Discussion2619 comment18955566](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566).
Vasek (`flyingviper`) source-bound and audited it in
[PR2744](https://github.com/CrocSwap/integer-mult-bounds/pull/2744), head
`0166260409f55a56e7fefa48d859f7dd5b42b300`. The new local representation proof
does not supply a change to the following frozen profile or coverage premises.

Fix width `m=73`, `W=832` original live families, five calls of the PR2458
forward profile and four calls of either the PR2712 or PR2725 dual profile.
The rank-one through rank-eight profiles are

| Profile | Counts H1 through H8 | Rank mass |
| --- | --- | ---: |
| PR2458 forward | `(1216,74,86,104,48,42,68,8)` | 3070 |
| PR2712 dual | `(1498,60,74,92,58,56,92,8)` | 3542 |
| PR2725 dual | `(1502,58,74,93,57,56,91,9)` | 3542 |

Grant every call all `104*8 + 104*8 + 150*9 = 3014` persistent endpoint units.
Each original family has exactly one unpaid coordinate; private lifetimes
give no extra persistent credit. Remaining paid coverage, carried collectively
by whatever correction/helper/residual/idle children realize it, is at least

`I = 72*832 - 9*3014 = 32778`.

Assume every positive child rank is at most 73, all other charges are
nonnegative, and every finite number `B >= 0` of auxiliary banks is fully
paid: each adds 73 units of required coverage and one family to the denominator.
For `0 <= a < 1` and `0 < r <= 73`,

`(r/73)^(1-a) >= r/73`.

Consequently the normalized moment of this frozen consumer obeys

`M_B(a) >= [5*3070 + 4*3542 + 32778 + 73B] / [73(832+B)]`
`       = 1 + 1560 / [73(832+B)] > 1`.

At `B=0` the bound is exactly `599/584`. No unknown nonnegative admission,
codec, port, routing, cleanup or physical cost can turn this lower bound into
a successful `<1` screen. Fully paid storage cannot repair it either; the
positive margin gets smaller with larger finite `B`, but remains positive.
The small rational checker includes the failure control `B=22`: adding only
the denominator falsely gives `62296/62342 < 1`; paying the bank coverage gives
`63902/62342 > 1`.

This stop applies **only** while those exact profiles, call counts, width and
coverage law are retained. It does not exclude an actual coarsened/resynthesized
word, changed consumer, changed native-child interface, or replacement coverage
theorem. It does not derive a full consumer from this local source projection.
For the present unchanged-profile route, the family decision is to finish and
retain the producer/consumer contract, then stop supplier/owner expansion aimed
at a new selected saving. Reopen only for a concrete changed premise with a
new same-map, fully charged candidate bill that first survives its favourable
screen. Passing such a relaxation would justify the next bounded admission
experiment, not certify a supplier.

## 7. Physical context retained without importing its conclusion

Jose Manuel's
[PR3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087), head
`e7e49fb8176772c71ad7006920a407109a89e440`, supplies a source-relative physical
Gaussian-monomial refinement. Its common grid, signed-width guard, complete
outer rows/spectators, record encoding, protected outputs, clean work, ordinary
child assumptions and long-record regime must be instantiated before applying
its asymptotic tariff. A 512-coordinate numerical fixture does not establish
those hypotheses. The wrapper counts here give inputs to such an eventual
bill, not its conclusion.

Jose Manuel's
[PR3131](https://github.com/CrocSwap/integer-mult-bounds/pull/3131), head
`0c9e344d5a5295a218558fa4a51d867f39ff5311`, prices a dense **paired** floor
collector under its specified batching, residue-history, physical layout and
source assumptions. Its return uses the paired inverse. This task executes
every independently archived return recipe; in particular, PR3382 already
showed that its local actual `V` has 416 wrapper cycles/2,464 swaps across the
four wrappers, while the paired-inverse substitution has 384/2,432. A tariff
for the latter is not a byte-level implementation of the former on arbitrary
states. Domain-specific equality needs its own preserved proof and invoice.

The inspected pending
[PR3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385), frozen head
`7e5a187214126d31afc241a8f89f4a652352b58c`, joins the selected physical complex
controller/root-return contracts under its own exact source identities,
chronological hosting, word/profile, common grid, guard, field layout,
ordinary `B1/C0` children and physical-refinement hypotheses. This is valuable
context for what a complete bill contains. It does not authorize substituting
this new P104 open program or restricted initial module into that selected
controller for free. We did not replay or newly audit its all-size theorem or
hosted CI, and do not treat it as established admission of our 63-bank caller.

## 8. Sources, credit and reproducibility

The principal authenticated scientific bytes are:

| Input | SHA256 | Exact role |
| --- | --- | --- |
| `research/p104-rounded-collector/inputs/WORD.json` at main `6f100d4...` | `cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50` | Actual producer, internal path and outgoing reads |
| `research/p104-rounded-collector/inputs/NATIVE.json.gz` at the same main | `ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d` | Every literal native recipe and wrapper |
| `research/p104-consumer-budget-audit/README.md` at the same main | `13694215d0c1a245b392f7155e8395b9c4bad9c5db3558833c784d9449616417` | Inherited frozen-profile and coverage hypotheses |
| PR3382 `PROOF.md` at `2834523b1cd4ea83ba7a043e2e2f5f3332cf9909` | `1ca8c0e7e78f0f39de6cff7accc68ccd3901bfb50759bf7a2e2896bcf63bf081` | Module, direct logical codec and actual-`V` boundary |

[SOURCES.json](SOURCES.json) records the immutable runtime and retained
predecessor inputs, including their exact commits and byte hashes. Its
`context_sources` rows separately identify the inspected physical-context
proofs and manifests by immutable commit and hash. These context sources are
not imported by the verifier and need not be downloaded to replay this
package. PR3385's inspected bytes were checked against their advertised Git
blobs; that contextual check does not admit its theorem for this caller.

Predecessor credit remains with ywz65's corrected dual word and native data;
Arham Tahir's retained first-collector binding; Tekalign (`tekuuu`) for the
literal pair, cycle algorithm and logical ledger in PR3025, head
`a544ef068a46f4de3bc47d1d02149cbdc3ba547f`; Ross Richardson's PR3068 period
contract, head `7d2c519a1fdcc6bf66f6f08757eed7c48762d3f2`; PR3382's proved
phase-complete module and interface; Jose Manuel's original budget finding;
Vasek's PR2744 audit; and the physical contributors preserved in the context
manifests. The frozen profile heads are PR2458
`3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6`, PR2712
`afa5d6649460dcdb93489babd74f0ee9d01a4911`, and PR2725
`71d24b655c2fdddc063b9aaf285e8425ce197499`. Their alternative retimings are
not combined. The new cost work is the complete actual open-path inventory and
its interface audit, not a new origin claim for these algorithms or the
`599/584` obstruction. Substantial AI assistance is disclosed.

From the repository root, reproduce the source-bound producer, consumer,
independent checks and complete cost audit with:

```sh
python3 -B research/p104-newton-interfaces/verify.py
python3 -B -O research/p104-newton-interfaces/verify.py
```

The same commands apply at the root of the source-complete export, whose
retained files preserve their repository-relative paths. The verifier binds
the source and implementation bytes recorded in [SOURCES.json](SOURCES.json)
and [RECEIPT.json](RECEIPT.json); its replay contract is in
[VERIFY.json](VERIFY.json). It requires standard-library Python, with no Git,
network or native compilation during replay.

The separately callable `cost_audit.source_audit(source_root)` authenticates
the three cost inputs listed in that module and reconstructs only the source,
frame, operation and rational-bound evidence. The package verifier also runs
the separate semantic producer/consumer and independent array/path checks;
the cost-only function does not implicitly claim those proofs were executed.
