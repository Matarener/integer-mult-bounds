# The selected pre-B cut is a scatter: exact orientation and restoration audit

This is a finite source-bound correctness result. It supplies a corrected
arbitrary-dirty word but no recursive cost saving or new conditional kappa.
The selected record at the pinned base is `0.001672660197076918`; this package does not change it.

The audited PR3604 head is `9a56309846c262238de04138d14d8bc32ec83d77`.
Its consumer verifier is byte-identical to the initially audited head
`30968c83f160011b5f435380746f0e57e64517d0`. The newer input-side correction
and square-completion notes do not change those literal operand assignments.
Canonical main is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
`SCATTER-SOURCES.json` pins the original files by Git blob and SHA-256, and
pins the selected archive and its canonical/native members. Original source
files are retained unchanged. Gonzalo Mier's P112 consumer work, the P112
geometry and integer kernel completion, selected port map, gauge44 construction,
and native-lift authors retain their respective attribution. This audit was
prepared with substantial OpenAI Codex assistance; new work is Apache-2.0.

## 1. Actual operator at the selected cut

Write `d` for the 112 output vectors immediately before the centre phase and
`p` for its eight private centre vectors after their respective rank-eight
descents to frame zero. The selected cut is

```
d <- d + S p,       S has shape 112 by 8.
```

Each component may be an arbitrary complex vector on all 512 native addresses.
The scalar matrix `S` has 176 nonzero coefficients. The canonical instruction

```
["add", 118, 57, 1, 4, null]
```

means destination `L[118]` receives `(1/4) L[57]`. Its native expansion is

```
["scalar", ["add", ["L",118], ["C",1], 1,4], 0].
```

Private `C[1]` was copied from carrier `L[57]` and descended to frame zero.
The verifier checks this destination-first interpretation against all 176
canonical/native coefficients and replays the full forward program under this
interpretation over all 704 normalized ordinary scalar columns.

Consequently, `S^T y` is an abstract readout associated with this matrix; it is
not the selected native operation. In PR3604's canonical prefix and canonical
`B` projections, `gate[1]` and `gate[2]` are also assigned the opposite source
and destination meanings. Those projected dirty-response and post-B records
do not certify the selected literal forward map. This does not refute the
valid abstract matrix identities that their matrices satisfy.

## 2. Correct basis covariance and a minimal witness

Let `U` be one of the predecessor's eight-by-eight integer unimodular target
basis changes. If the entire target vector is represented as `z=U d`, then
the scatter must change by

```
S_scatter = U S,
z <- z + (U S) p = U(d + S p).
```

For comparison, `S_reader=U^{-T}S` satisfies the valid abstract identity

```
S_reader^T U y = S^T y.
```

These are different covariance laws. The hybrid reader retains the first four
rows of `S` and takes the last four rows of `U^{-T}S`; it has no automatic
scatter interpretation.

The first tetrad has coordinates `(0,1,2,3)` and ports in `U` order

```
[110,21,37,47,46,36,20,111].
```

Its first basis row is `[-1,0,0,1,1,0,0,-1]`. Set all eight dirty output
coordinates to zero and `p=e_7 v` for any nonzero native 512-vector `v`, using
zero-based centre index seven. The first transformed output, role `L[222]`,
receives

| Scatter matrix | Coefficient of `v` at first transformed output |
| --- | ---: |
| Correct `U S` | `-1/2` |
| Full inverse-transpose reader `U^{-T}S` used as scatter | `-1/4` |
| Hybrid reader used as scatter | `0` |

The executable asserts these exact values. The predecessor's four zero rows
in `U K`, with `K=E E^T` for the tetrad decoder, therefore do not establish
four zero rows in the actual selected centre update: `U S` has nonzero top
rows in every one of the fourteen tetrads. The top-four supports in the first
three blocks are `11,6,6`.

This local witness is reachable under the arbitrary-input contract. Before the
centre phase, the selected program contains only ordinary ADDs, nonzero
scales, invertible native climbs and invertible endpoint/residual adapters.
It has no clear or copy. Its 704 ordinary roles therefore undergo an invertible
map. The eight carrier roles `[92,57,81,224,11,240,9,256]` are distinct and
disjoint from `L[112:224]`. Set the output vectors to zero, seven carriers to
zero, and carrier seven to the inverse-descent image of `v`; invert the ordinary
prefix to obtain allowed initial inputs. All native recipes remain the pinned
ones; their invertibility is inherited from the selected finite construction.
One may scale `v` to clear the finitely many dyadic denominators if an integer
grid is desired. No zero-dirty restriction is imposed on other initial roles.

After the centre phase, the selected ordinary suffix from `B` onward consists
again of ADDs, nonzero scales and invertible native operators. It neither clears
ordinary roles nor uses private centre roles. Thus a nonzero cut defect cannot
vanish from the complete ordinary endpoint. The verifier explicitly checks
these prefix/suffix instruction inventories. As a second full-word control,
installing the hybrid as a scatter inside the same basis sandwich preserves
the common-frame labels and recursive bill but fails the complete endpoint.

## 3. A corrected literal word with complete dirty restoration

There is a simple in-place repair that needs no retained dirty baseline:

```
1. U on the chosen output tetrads in frame zero;
2. the existing centre-copy/descent/clear phase, scattering with U S;
3. U^{-1} on those output tetrads in frame zero;
4. the unchanged B, cleanup, endpoint adapters and full-frame cleanup.
```

For every dirty `d` and every private centre value `p`,

```
U^{-1}(U d + U S p) = d + S p.
```

The carriers are disjoint from the changed outputs, so their copies and
descents do not change. Each private centre still lives only between its old
copy and clear, and each new scatter ADD occurs while that private value and
every output operand have frame zero. `U^{-1}` is installed after the last
private clear and before `B`. The suffix therefore receives precisely the same
ordinary vectors and frame labels as before. Arbitrary helper columns and all
endpoint/restoration identities follow by substituting the exact same-frame
identity into the existing native word, rather than by assuming a separately
available baseline.

The executable emits this replacement for three and fourteen tetrads and checks
all 704 normalized ordinary scalar columns, every scalar common-frame condition,
every final ordinary frame label and every private zero endpoint. The
512-address statement is an all-vector matrix identity at the changed boundary;
it is not a sampled native-address test. Unchanged Clifford recipes are reused,
not freshly re-certified here. Omitting the entrance `U` gives
`U^{-1}d+S p` and is deliberately rejected on initial dirty output columns.

## 4. Complete cost of this word

The supplied integer synthesis of each `U` uses 21 signed ADDs, two swaps and
one sign change. A swap is expanded into three signed ADDs and one sign change,
so each direction is exactly 27 ADDs and three sign scales, with no extra role.
Its inverse has the same counts. This is a concrete upper-cost construction,
not a claim that the basis word is shortest.

| Tetrads changed | Old/new cut ADDs | Extra scalar ADDs | Extra sign scales | Total extra scalar operations | Recursive histogram delta |
| --- | ---: | ---: | ---: | ---: | --- |
| 3 | `176 -> 181` | 167 | 18 | 185 | zero |
| 14 | `176 -> 214` | 794 | 84 | 878 | zero |

For all fourteen blocks, the scatter supports are
`17,14,14,17,13,18,18,14,14,13,17,14,14,17`, summing to 214.
Thus the corrected scatter alone adds 38 coefficient incidences. The three-block
prefix adds five. The table includes both basis directions and every replacement
coefficient. It retains every existing centre copy/descent, child, residual
adapter, endpoint adapter and cleanup operation. There is no extra private
stream, duplicated `B`, extra role or omitted restoration step.

The full recursive histogram is exactly unchanged: `Delta H_r=0` for every rank.
Under the existing recursive moment objective this word supplies zero raw
recursive saving. Its positive extra scalar work cannot be counted as a
conditional-kappa improvement. No physical scalar-to-child tariff is invented
to convert these scalar counts into a favorable moment. Rounded execution,
intermediate magnitude bounds and unchanged precision admission have not been
proved; those would be additional obligations for using the corrected word.

## Reproduction and covered domain

```
python3.12 -I -O -B research/p112-scatter-orientation/verify.py
```

Expected package status: `PASS_P112_SCATTER_ORIENTATION_NO_NEW_KAPPA`.
The child scatter certificate additionally reports
`PASS_SELECTED_CUT_SCATTER_ORIENTATION_AND_DIRTY_SANDWICH_NO_NEW_KAPPA`.
The independent direction checker reparses all 176 cut bindings and rejects
a reversed-operand event without importing the candidate producer.

This covers the pinned selected forward cut, all fourteen source-bound tetrads,
the explicit three-/fourteen-tetrad sandwiches, exact complex vector arithmetic,
arbitrary ordinary dirty inputs and the existing literal native contracts. It
does not exclude changed producer words, a correctly transposed full supplier,
other decoder factors, other completions or shared-cost constructions. A full
transposition would require transposing the complete producer, interfaces and
restoration, rather than reading the selected scatter as a readout.

Open next questions are a complete changed decoder producer with actual
consumer direction, a favorable fully charged recursive histogram, precision
and physical storage admission, whole-call hosting and all-size outer transfer.
The result is a finite exact certificate and written operator proof, not a
formal-kernel proof or a complete multiplication theorem.
