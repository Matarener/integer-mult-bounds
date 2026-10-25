# Formal scope

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.

The package includes `formal/BinaryCliqueCore.lean` and
`formal/ConsumerArithmetic.lean`, both importing only Lean `Init`. All six
declarations passed targeted Lean 4.21.0 checks with warnings treated as errors,
one Lean thread, and an external 512 MiB RSS watchdog. The files were checked
serially:

| Source | Result | Elapsed | Peak process-group RSS |
|---|---|---|---|
| `BinaryCliqueCore.lean` | PASS, exit zero | 1.417 s | 262.30 MiB |
| `ConsumerArithmetic.lean` | PASS, exit zero | 1.135 s | 235.02 MiB |

Status: **PASS** for these scoped formal results.

## Statements and explicit assumptions

`BinaryCliqueCore.lean` defines `binarySum zero add xs` as the right-associated
sum of a finite list. Its five declarations prove:

1. `detector_sum_zero`: an additive Boolean-valued detector vanishes on a sum
   when it vanishes on every summand.
2. `detector_sum_selected`: if a list has no repeated vectors, a detector which
   is one on one selected vector and zero on the others evaluates to one on
   their sum.
3. `compatible_clique_zero_sum_empty`: a distinct list of nonzero pairwise
   compatible vectors has zero sum only if it is empty. Pairing additivity
   detects every odd member of a putative relation. The remaining even members
   have pairwise distinct Boolean colors, so there are at most two. A nonzero
   singleton and two distinct vectors cannot have zero sum.
4. `compatible_transversal_zero_sum_empty`: for membership predicates `Z i`
   with pairwise trivial intersections, nonzero choices from distinct indices
   cannot collide. If all nonzero cross-choices are compatible, any finite
   zero relation among these grouped choices has an empty active index list.
5. `BinaryNine.clique_zero_sum_empty`: instantiate the clique theorem in the
   concrete binary space `Fin 9 → Bool`. Zero is pointwise false, addition is
   pointwise XOR, and the pairing is the XOR of coordinatewise AND over the
   explicit coordinate list `[0, 1, 2, 3, 4, 5, 6, 7, 8]`. All addition and
   pairing laws required by the abstract theorem are proved. Distinctness,
   nonzero vectors, orthogonality, and the even-color condition remain explicit
   premises.

`ConsumerArithmetic.lean` proves `copy_ge_seventy_two`: for arbitrary natural
numbers `COPY`, `m`, `s`, and `t`, the two explicit premises
`9 * m ≤ COPY + 9 * s + 9 * t` and `8 + s + t ≤ m` imply `72 ≤ COPY`.
This is only the arithmetic consequence. The file does not derive either
premise from ranks, dimensions, the Sylvester inequality, or E8 geometry.

In the first four declarations, the operations are parameters, not undeclared
axioms. Their exact laws are explicit premises:

- `add x zero = x` and `add x y = zero ↔ x = y`, the characteristic-two
  cancellation law;
- `β x zero = false` and
  `β x (add y z) = Bool.xor (β x y) (β x z)`;
- pairing zero for distinct compatible vectors;
- different Boolean colors for distinct even compatible vectors, where even
  means `β x x = false`;
- for the grouped-family corollary, trivial intersections and compatibility of
  all nonzero cross-choices, together with membership/nonzero conditions on
  the selected grouped vectors.

`BinaryNine.clique_zero_sum_empty` discharges the first two algebraic premise
groups for its concrete operations. It retains the geometric orthogonality and
even-color premises. Neither symmetry nor nondegeneracy of `β` is silently
assumed by the abstract proof. No fixed number of summands is assumed.

Each public theorem has a `#print axioms` audit. The successful checks reported
no axioms for `detector_sum_zero`, and only `propext`, `Classical.choice`, and
`Quot.sound` for the other four clique/grouping declarations. The arithmetic
theorem depends only on `propext`. There were no `sorryAx` dependencies or
compiler warnings. Neither source contains a `sorry` or custom
`axiom` declaration.

## Boundary of the formal result

This is a checked binary clique argument with a concrete nine-coordinate
instantiation, not a formalization of the complete E8 theorem over fields of
characteristic different from two. The identification of the E8 quotient with
the concrete binary coordinate space, its geometric color map, nondegeneracy,
and verification of the geometric compatibility premises are not formalized.
Neither are the construction of the annihilators `Z i`, their
intersection/cross-compatibility properties, the grouping of arbitrary scalar
relations, the equivalence with Mathlib `LinearIndependent`, the finrank
direct-sum budget, the scalar rank comparisons and field transfer, or the
derivation of the two Sylvester/deficiency consumer premises. Those steps
remain in PROOF.md; only their final natural-number consequence is separately
formalized in `ConsumerArithmetic.lean`.

The further singleton-pair classification and rank-(10,8) consequence in
`SPARSE-PAIR.md` are written proofs. No new formal declaration covers their
projective-ray classification, filtered-span basis bound or decoder assembly.

## Toolchain and replay

The repository's `formal/lean/lean-toolchain` pins
`leanprover/lean4:v4.21.0`. The checked sources need that Lean distribution and
`Init` only; they have no mathlib, external certificate, or package dependency.

From the isolated worktree root, the local cached invocation is:

```sh
../e8-formal-work/toolchain/lean-4.21.0-darwin_aarch64/bin/lean \
  --threads=1 -DwarningAsError=true \
  research/e8-one-coset-deficiency/formal/BinaryCliqueCore.lean

../e8-formal-work/toolchain/lean-4.21.0-darwin_aarch64/bin/lean \
  --threads=1 -DwarningAsError=true \
  research/e8-one-coset-deficiency/formal/ConsumerArithmetic.lean
```

The available cache is a local convenience, not a committed binary bundle. A
provisioned Lean 4.21.0 binary can run the same sources and flags directly. No
`lake` command or full build is required. The coordinating agent scheduled the
recorded replays under a separate 512 MiB RSS watchdog; the commands above alone
do not provide that external limit. Finish each command before starting the
next. No Lean jobs were run concurrently.

## Resource-limited drafts

Two exploratory mathlib drafts were preserved privately outside this package
and are not publication artifacts or formal claims. Their attempted checks
were stopped before compiler diagnostics by the 1024 MiB RSS watchdog:

| Draft | Result |
|---|---|
| Generic independent-transversal/direct-sum/finrank draft | STOPPED, 1033.16 MiB, 3.497 s; default Lean thread count |
| Generic orthogonal coefficient-detection draft | STOPPED, 1049.67 MiB, 3.266 s; one Lean thread |

These stops establish neither a theorem failure nor successful elaboration.
The Init-only sources replace their formal coverage in this package. Full Lean
project verification and clean toolchain provisioning were not run.
