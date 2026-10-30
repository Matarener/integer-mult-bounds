# Partial formalization

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.

These files use Lean4.21.0 and mathlib commit
`308445d7985027f538e281e18df29ca16ede2ba3`, matching the repository's
`formal/lean/lean-toolchain` and `formal/lean/lake-manifest.json` pins.
With that environment and its dependencies already installed, run from
`formal/lean`:

```sh
lake env lean ../../research/e8-marked-d0-invoice/formal/PrivateLabels.lean
lake env lean ../../research/e8-marked-d0-invoice/formal/CarrierParity.lean
lake env lean ../../research/e8-marked-d0-invoice/formal/ActualCoefficientMap.lean
lake env lean ../../research/e8-marked-d0-invoice/formal/PrivateIncidence.lean
```

`PrivateLabels.lean` constructs the actual coefficient-recovering linear
functionals from the leading coordinate and private pairings. It proves
linear independence of the private labels and exclusion of every frame
label from their span. It does not assume either conclusion as a hypothesis.

`CarrierParity.lean` expands the three-label quadratic form and proves the
carrier-plus-unit contradiction from its actual polar/augmented-beta data.

`ActualCoefficientMap.lean` starts from an actual basis and quotient splitting.
It derives the high coordinates by projecting the basis expansion, then proves
the negative low-coordinate formula for A. Neither resulting identity is an
assumption. The actual coefficient space and dual basis are retained.

The first three files compiled without warnings using cached dependencies at these
pins. The printed axiom sets are `propext, Classical.choice, Quot.sound` for
the private-label and coefficient-map endpoints and `propext, Quot.sound` for
the parity endpoints.
There are no placeholders, custom axioms or unsafe declarations.

`PrivateIncidence.lean` derives the four-private-root bound from actual
four-element supports, private matched axes and even pairwise intersections.
With at least two private roots it bounds ALL corrected-high frame axes by
four, including possible weight-nine highs. It proves that a quartet
exhausts those axes, constructs the omitted-unmatched-axis bijection and
proves that every frame axis is missed by a quartet root. A concrete quartet
has every finite-incidence hypothesis checked by kernel `decide`.
This fourth file compiled without warnings at the same pins; all seven
printed endpoints use only `propext, Classical.choice, Quot.sound`.
It does not assume any target cardinality bound. The E8 incidence and actual
high-duality bridges supplying its hypotheses remain external.

The E8 root/label instantiation, finite normal-family tables, raw shape/cap
deductions, complete case assembly and
actual-decoder consumer remain written proofs and executable finite checks.
These four files are not a formalization of the whole marked invoice.
