# Generated native witnesses versus checked witnesses

The current caller producer generated selected-native recipes for q=2,3.
The publication verifier consumes those fixed recipes; it does not repeat
the expensive native synthesis. Every original-column, phase and inverse
obligation remains checked. The relevant distinction is below.

| Original synthesis/check | Registered fixed-witness check |
|---|---|
| `ce.lower_child(op)` generates left/right monomials and one selected native child. | Require every retained recipe, validate its dimensions, coefficient domains, invertible address maps, symmetric quadratic and phase data, then reconstruct it independently. Missing evidence fails. |
| `same(compiled,op)` compares the signed tableau and actual Gaussian global phase. | Reconstruct the source tableau from its literal physical circuit and the compiled tableau from the fixed monomial/native/monomial recipe. Compare both. Separately compare the complete source column computed by an independent integer Walsh transform with a direct physical expansion of the recipe. A wrong global phase preserves the tableau but rejects here. |
| `rec['rank']==r` checks the synthesized tariff. | Recompute source B-rank and compare it with the selected native arity and every event's paid rank. A changed rank rejects. |
| `check_literal_family` compares the actual physical source with the all-f X-character family. | Unchanged and executed by `joint_tail.produce(lower=False)`, including all four f phase residues. Every retained event also matches its fixed recipe's embedding and once-per-whole-field phase tag. |
| Full physical word, original H/L columns, both inverse orders and the completed target are checked. | Unchanged and executed. Only the generated-recipe fields and generation-mode flag are omitted from this first comparison; the fixed-recipe checker then validates every omitted recipe and every use of it. |
| Omitted original-t restoration and final-extraction public readers reject. | Unchanged and executed. The independent literal inverse-row audit additionally rejects a missing f-dependent target-J unit invisible at f=1. |

For a Clifford operator, equality of all signed Pauli images fixes the
operator up to a scalar. One exact nonzero input-column equality fixes
that scalar, so the combined check covers the complete operator including
Gaussian phase. The checker evaluates all coefficients of that source
column, using integer Gaussian numerators and powers of two. This is not
a brute-force enumeration of every physical input column, a formal-kernel
proof, or a hardware promise of a clean helper. The full caller proof
retains every original independent input field.

The source-side oracle accumulates affine X-character addresses and sums
of parity phases directly from literal P/C/Pauli-D/X/phase events, then
uses an integer Walsh transform. The recipe-side oracle expands the
physical monomial maps and the actual C branches. It does not call native
synthesis or trust a reported tableau as the source operator.

An equivalent compensated left/right scalar phase gauge is accepted.
An uncompensated global phase and an inflated native rank reject. Every
paid native forward/inverse event must have an existing recipe, correct
embedding, exact one-coordinate source action and the all-f unit tag.
This pointer check caught an inverse-recipe naming defect during packaging;
the source owner corrected the identifiers before publication. Its complete
old receipt is reconstructed from compact metadata splices and authenticated
against its original SHA before the same rejection is executed. Operator,
phase and rank assertions were retained.

`BINDINGS.json` records exact original and adapted source bytes. All source
loads compile the authenticated bytes directly, without bytecode caches,
with historical assertions enabled even under an optimized parent Python.
The old local resource/factory checks remain separate entrypoints, and the
new all-q telescope proof remains distinct from its finite free-word grid.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
