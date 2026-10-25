# One P112 co-delivery block with exact native frame recipes

**Constructive local result and a consumer-boundary cost; no new supplier or κ.**
Four independent query payloads on the named selected P112 tetrad can each be
transferred at native rank one. This package supplies actual Clifford recipes,
exact Gaussian phase checks and a chronological scratch/ADD word. It also
constructs the version whose outputs meet the abstract frame-zero centre-reader contract:
that version needs rank-four transfers, not the rank-one tariff alone.

The selected conditional κ remains **0.001672660197076918**. No complete
construction exceeding 0.002 has been established.

## Fixed object and source binding

Use selected port labels, in local order,

```
319, 289, 274, 268, 140, 146, 161, 191
```

They occur at selected port indices `110,21,37,47,46,36,20,111`. The verifier
reads their actual destination-first scatter coefficients S and the centre-frame normals from
the authenticated selected1094 archive. The full integer matrices E and U are
explicit in verify.py. They are the first tetrad's eight-by-four signed query
matrix and the unimodular kernel-row output change from the P112 coefficient
work. Write

```
K = E E^T,  M = U E,  D = S^T(M-E).
```

The first four rows of M vanish. All four query columns are independent:
`E^T E=8I4`. Here D has just two nonzero entries, `D[6,2]=1/2` and
`D[7,2]=-1/2`. Therefore

```
S^T(d + M E^T x) - D E^T x = S^T(d + K x).
```

This identity includes arbitrary dirty port contents d. It does not assume
d=0 or a second retained dirty stream. The verifier checks all 25 independent
scalar columns: eight sources, eight dirty ports, eight dirty centre accumulators
and one owned private array whose initial value is explicitly cleared.

The selected cut is **ports <- ports + S centres**, with centre inputs
unchanged. It is not the transposed readout `centres <- centres + S^T ports`.
Ross Richardson's [PR3632](https://github.com/CrocSwap/integer-mult-bounds/pull/3632)
(`7e7a889cbf6da2c4461af806fe52a888c621a7e7`) identifies this distinction.
The first three contracts below are explicitly defined abstract co-delivery
modules. A fourth contract executes the actual scatter direction as a control;
none is silently substituted into the selected complete word.

## The native construction

Let `F(V)` be the retained exact canonical Clifford frame on a binary subspace
V. Let `F=F(F2^9)` and `C_q=((1+i)I+(1-i)X_q)/2`. Frames and phases are literal
operators, not just dimension labels. The named spans are

```
A = span(319,289,274,140),             dimension 4
B = span(30,45,268),                  dimension 3
B = A intersect span(140,146,161,191)^perp.
```

Both active centre normals, 97 and 76, annihilate B. Exact native lowering gives:

| Actual frame conversion | Rank |
| --- | ---: |
| Each source C_q to F(A) | 3 |
| F(A) to source exit F | 5 |
| F(A) to F(B) | **1** |
| Initial target I to F(B) | 3 |
| F(B) to the appropriate target exit F C_q^-1 | 5 |
| F(A) to frame I | **4** |

For each of four terms, clear the owned private array, initialize that zero
array in frame F(A), and form `E[:,k]^T x` by eight signed same-frame ADDs.
Transfer it to F(B), scatter M's four nonzero port coefficients, and emit D's
centre correction where required. After its last read, clear the private array.
One array suffices for all four terms; four independent transfers are still
charged. The source and destination data-frame movements are fully counted.
There is no unpaid nonzero reset or borrowed-workspace discard.

Degenerate subspaces require the general canonical Clifford frames. Restricting
frames to products of translation roots can make this same transfer appear to
cost five. The actual general-frame recipe has rank one; this package does not
present the restricted-family obstruction as a native impossibility theorem.

## Four completed module contracts

All sources enter as `C_q x_q` and finish as `F x_q`. Initial ports and centres
are arbitrary arrays in frame I. Let q denote the corresponding port or centre
normal in the following table.

| Module | Port output representation | Active centre representation and content | Full profile | Rank mass |
| --- | --- | --- | --- | ---: |
| Framed centres | `F C_q^-1 (d + M E^T x)` | `F C_q^-1(c - D E^T x)` | `{1:4,3:14,5:14,8:4}` | 148 |
| Frame-zero centres | Same port exits | `c - D E^T x`, frame I | `{1:4,3:13,5:12,8:4}` | 135 |
| Abstract frame-zero reader | `d + M E^T x`, frame I | `c + S^T(d+Kx)`, frame I | `{3:8,4:4,5:8}` | 80 |
| Actual frame-zero scatter and K product | `d + S p + K x`, frame I | Original centre inputs p, unchanged in frame I | `{3:8,4:4,5:8}` | 80 |

Inactive centres remain untouched in frame I. The abstract zero-reader module
uses the transpose of the eight nonzero S coefficients on its returned ports,
after applying the source-side correction. The actual-scatter control instead
executes the original destination-first direction and emits E rather than M
into all eight ports; it preserves every centre input. Its sources already finish at F.
The different terminal contracts explain the different masses; **80 is not a
cheaper replacement for the 148 contract**. Returning all its eight port arrays
later to `F C_q^-1` would add eight rank-eight moves, giving mass 144, and still
would not identify it with a complete selected provider.

The frame-zero-centre variant requires one extra rank-three return, on the only
query with centre correction. The zero-cut variant returns all four queries to
I. Its four rank-four drops cannot be priced as four rank-one drops merely
because the support-pairing matrix has rank one.

The first three modules use 48 unit complex ADDs, two half-unit ADDs and five explicit
CLEARs. The abstract zero-reader version also uses eight quarter-unit ADDs. The actual-
scatter control uses 64 unit ADDs, eight quarter-unit ADDs and five CLEARs. With allowances
8/10/12 real scalar primitives per unit/half/quarter ADD and two per CLEAR, the
respective nonrecursive allowances are 414, 414, 510 and 618 per array coordinate.
These constants omit native-child execution and address/layout costs; those
are separate obligations. Every native child in these modules is proper when
compared with the selected width 73, but this is no complete moment bill.

## Exact verification and tensor scope

```sh
python3.12 -B scripts/research_package.py --package research/p112-codelivery-native-block
```

The verifier authenticates executable source bytes before loading the retained
compiler and its separate Gaussian interpreter. It checks 23 distinct lowered
recipes, including signed Pauli actions and exact global phases. The rank-one
transfer is additionally checked on every one of its 512 Gaussian basis columns.
Wrong centre signs, reversed selected-scatter operands and wrong native global
phases fail. The rank-four drop is
a positive control for the changed zero-frame obligation. New guards remain
active under optimized Python; the independent interpreter supplies explicit
checks beyond the compiler's internal assertions.

Exact nine-axis operator equalities tensor to every positive coordinate count f
on arbitrary payloads, with each global phase raised to f. Scalar ADDs are valid
because their operands have the same exact tensor frame. This is the algebraic
tensor extension of these module identities, **not admission of a fixed-tape
caller, recursive hosting, precision, stock, or the multiplication theorem**.

`verify.py --write` regenerates only RESULT.json. Ordinary replay is read-only;
no selected cold replay, Lean run, or shared artifact regeneration is required.

## Open next questions

The module gives the local native COPY constructor that a coefficient-only
rank-one calculation lacked. It preserves arbitrary data and returns its one
owned private array to zero. It does not show that the selected producer supplies
these eight C_q sources at the required chronological cut, nor that the modified
port output is an admitted independent-port primitive. `M E^T` has four zero
rows and is deliberately not the old full endpoint. No unchanged coverage law
or hypothetical rank-32 repacking is used to manufacture a κ estimate here.

The first remaining question is whether an actual producer and consumer can use
one of these **specified** output contracts. Bind one selected prefix/suffix to
the module and replay all source/helper columns, including its changed port map.
The fixed-zero reader is available only for the defined transposed-reader
contract. The actual-scatter control preserves the selected operand direction; the
framed version needs a caller that accepts its listed frames. A concrete source
binding, owner/private-array acquisition, physical address cost, precision and
complete bit-side improvement remain missing. Stop expansion if those costs
consume the apparent saving. The two-unpaid-coordinate outer interface remains
unproved; neither a rank-one recipe nor a small module mass establishes it.

## Credit and status

This follows Gonzalo Mier's P112 coefficient-fusion work in
[PR3604](https://github.com/CrocSwap/integer-mult-bounds/pull/3604), the selected
port-binding witness in [PR3566](https://github.com/CrocSwap/integer-mult-bounds/pull/3566),
and the local co-delivery calculation in `research/p112-centre-co-delivery`.
The explicit matrices included here make this one-block result independent of
those pending scripts at replay time. The concurrent [selective co-delivery audit, PR3691](https://github.com/CrocSwap/integer-mult-bounds/pull/3691)
(`b37d0e75433837482c351863a672543056f95bd5`) already checks the abstract
composition and a losing port repair, and explicitly leaves physical rank-one
COPY construction unresolved. This package adds that native module, not a
refutation of its port-defect finding. The direction correction in PR3632
is retained in the actual-scatter control.

The retained Clifford compiler and its
separate Gaussian interpreter come from the credited P104 native-channel and
source-code work. The selected word, root geometry and cut retain their source
attribution. No novelty is claimed for canonical frames or tensoring identities.

Base main is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6;
the explicit donor assignment changes the original card to completing this
specific native boundary. This is author-checked evidence, not independent human
or proof-kernel review. Prepared by Gonzalo Mier with substantial OpenAI Codex
assistance. Apache-2.0.

Overlap refresh on 2026-10-18 covered all 484 open PRs at 20:35:45 UTC
and 2508 Discussion records at 20:36:21 UTC. The exact heads and bodies of
PR3632 and PR3691 were read before finalizing scope. This is not a novelty
certificate and excludes unpublished work and arbitrary code diffs.
