# Partial Lean coverage

`formal/CutCore.lean` imports only `Init` under Lean 4.21.0, pinned by the
repository input `formal/lean/lean-toolchain`. No Mathlib dependency is needed.
Run the pinned executable sequentially:

```sh
lean --threads=1 -DwarningAsError=true research/e8-coupled-coordinate-floor/formal/CutCore.lean
```

The core declarations are:

| Declaration | Coverage | Reported axioms |
|---|---|---|
| `cut_contradiction` | Additive evaluation-map contradiction with its scalar laws explicit | none |
| `below_floor_forces_critical_state` | Below-floor tariffs force equality, zero surplus, rebate one, free pivot | propext, Classical.choice, Quot.sound |
| `strict_basis_floor_pays_rebate` | Strict basis slack pays the sole rebate | propext |
| `floor_of_critical_state_impossible` | Arithmetic reduction plus separately supplied critical-state obstruction | propext, Classical.choice, Quot.sound |

`formal/PartialBasis.lean` additionally proves
`equality_forces_zero_missing_low`: from r≤8, the actual-basis inequality
72+8d+κ≤W+r, W=72, and d=1⇒κ≥1, it derives d=0. This is the arithmetic
step in EXTENSIONS.md §4, with the geometric hypotheses still supplied
externally. Its reported axiom is propext. Run this file with the same Lean
command and flags.

The additive map in the first declaration is evaluated on actual abstract
vectors. Its addition law, scalar zero/one separation, quotient relation and
annihilation assumptions are explicit hypotheses; they are not generated
from a Mathlib linear functional here. Likewise the tariff assumptions are
not linked formally to binary support ranks. Standard axioms are printed
by the file, and warnings are treated as errors.

Not formalized: the E8 root/label bridge, the singleton classification,
the root-system/parabolic and Fourier arguments, weighted root-swap input,
field transfer, actual equality-basis geometry, exact decoder assembly,
and concavity. Exact Python certificates check their stated finite inputs;
they are not proof-kernel verification of these written universal arguments.
The registered Python replay does not silently run Lean. No repository-wide
Lean build or hosted CI is claimed.
