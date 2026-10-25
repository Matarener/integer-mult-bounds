# An interacting ten-helper packing gain

This is a conditional finite construction on exact PR3375
`62fd8039cc40749cea6238e7807db9a63b4d6765`. The local word, helper inventory,
144-call order, physical families, chronological windows and complete physical
invoice remain fixed. No selected result or supplier premise changes.

## Literal program

Indices refer to the complete 69,120-row owner array, starting at zero.
An owner bin is `(owner_replica, child, port)`.

1. Swap the placements of rows `(42540, 43909)`, of widths 8 and 7.
2. On that intermediate map, rotate the placements of
   `(47357, 16407, 11607, 8944, 6491, 1796, 0, 18745)` forward.
   Each row receives the next row's placement, and the last receives the first.
   The first six widths are 8; the last two are 9.
3. After each step compact every affected bin to a prefix, ordered by its
   existing offset and then row index. Logical roles and widths stay fixed.

Exactly ten helpers relocate. Twenty-three serialized rows change, including
offsets. In shared bin `(1,14,56)`, original rows 42540 and 47357 both leave.
Their widths total 16; incoming rows 43909 and 18745 have widths 7 and 9.
This interaction lies outside a one-original-departure/arrival-per-bin cycle.
PR3369 proves such a restricted obstruction on its older PR3359 map; it is not
an obstruction to this construction.

| Bin | Initial residual | After swap | Final residual |
|---|---:|---:|---:|
| `(1,14,56)` | 0 | 1 | 0 |
| `(14,4,14)` | 3 | 2 | 2 |
| `(1,2,74)` | 3 | 3 | 4 |

All other residuals stay fixed. The first step alone makes the moment worse.
It replaces rank 3 by ranks 1 and 2, and
`1 + 2^p > 3^p` for `0 < p < 1`. A search that only accepts improving or
neutral intermediate profiles can miss this program.

Both complete intermediate and final owner maps satisfy the independent
R1-R7 and X1-X2 audit: helper inventory, physical family identity and uniqueness,
actual event-stream windows, prefix capacity, disjoint slices, complete profile
and disjoint pending axes. The unchanged strict admission independently emits
and audits the final physical construction. The intermediate is a search
witness; it does not add a runtime operation to the final supplier.

## Exact moment inequality and price

Set `p = 1-a`. For every real `0<a<1`, strict concavity gives

`2^p + 4^p < 2 * 3^p`.

Thus replacing two rank-three idle children with ranks two and four strictly
reduces the completed recursive moment. All paid local children and additional
charges remain unchanged. Rank mass remains 1,041,408 and deficit remains 5,120.

The native exact primitive endpoint is
`838217298632056517939 / 500000000000000000000000`.
Both rational moment engines accept it and reject its next `10^-24` grid point.
The unchanged strict admission, native and conservative seven-step bootstraps,
and all 47 strict outer inequalities per path establish

`kappa = 83681443396347 / 50000000000000000 = 0.001673628867926940`.

The exact gain over PR3375 is `186019627 / 10^18`.
The conservative path gives `0.001673628865074167`. Complex still binds.
The unchanged local-profile packing ceiling and the attained fraction are
recorded as exact rationals in `RESULT.json`.

The complete typed physical invoice equals selected1094's invoice except for
three authenticated source identifiers. No charge, key, array order or value
type is omitted from that comparison. Prefix 397 stays paid at 512, and the
physical row coefficient remains 16,469. Actual charts decrease from 10,005 to
10,004 without reducing the retained invoice.

## Evidence boundary and credit

The 240-row predecessor patch reconstructs the exact PR3375 map from canonical
PR2169 bytes. Its canonical payload hash matches the retained original PR3375
result. The original construction, predecessor patch, proof and README are
retained byte-for-byte. Replay requires no pending Git object, network or solver.
The independent direct reconstruction agrees on every final owner row.

The first strict attempt rejected an inherited chart nomination of 10,005
because the unchanged emitter/auditor measured 10,004. The candidate metadata was
corrected, and a fresh full eleven-stage run passed. No checker condition changed.

This proves no packing optimum, universal obstruction, new all-size/compiler
lemma or unconditional multiplication theorem. Common-label/mutable-source,
whole-call hosting, precision/tape, exact recovery, analytic transfer and bit
H1-H5 assumptions remain inherited. Local provider evidence is authenticated
retained evidence, not a fresh full cold native reconstruction.

Credit Pierre / hexapode for PR3375 and PR3359, Nick Petalas for
PR3366/3354/3338, Gonzalo Mier for PR3308, Philippe Van Velzen for PR2169,
and the retained Jeremy Kothe, Rohan Arun, Hao Yan, George Lydakis and Josie
Elliston compiler, bit, owner and moment lineage. New material by Nick Petalas
is Apache-2.0. Substantial AI assistance was used for this investigation.
