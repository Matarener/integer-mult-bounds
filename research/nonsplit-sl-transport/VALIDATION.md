# Validation boundary

Environment: CPython 3.12.14, macOS arm64. Standard library only. The published
PR records the final commit, export digest and portable replay receipt. These
are author-side checks with separate agent implementations, not independent
human review, proof-kernel acceptance or validation of the full multiplication
theorem.

## Exact checked domains

The independent verifier implements polynomial field arithmetic, Gaussian
elimination, model multiplication and coefficient-index tensor action itself.
It uses the retained recognizer and character constructor as test targets.

| Domain | Exact coverage |
|---|---|
| Unit-first bases of quadratic fields over F2, F3, F4 | All 2, 6, 12 bases respectively |
| Unit-first bases of the cubic field over F2 | All 24 bases |
| Primitive choices for those field bridges | All 112 maps across the 44 bases |
| Actual raw-tensor recognition and transport | Six fixtures over F2, F3, F4, F9, dimensions 2 through 7; nonsplit nilpotents, repeated and mixed types |
| Literal covariant action | All six fixtures; all six reject the omitted-inverse-transpose mutant |
| Determinant triples for a quadratic residue field over F9 | All 512 triples; 128 accepted transporters, 384 rejected; four labels |
| Repeated/mixed components and field choices | All six component orders times nine primitive choices: 54 cases |
| Alternate common reference presentations over F9 | Eight tensor pairs; labels consistently shift by field element 3 |
| Malformed inputs and false maps | 23 rejections, including a false absolute-Frobenius certificate over F4 |
| Equal ground dimension, different full local types | Two rejected comparisons |

The basis census counts bases and maps, not distinct multiplication tables.
There are respectively 1, 3, 6 and 8 distinct tables in its four rows. The
512-triple test is a complete determinant domain, not enumeration of all
matrix triples or all tensors. Every accepted transporter is checked by
independent literal multiplication and determinant calculations.

The six raw-recognition fixtures have 25, 49, 9, 36, 16 and 4 basis products,
respectively. Recognition is exercised on independently changed input/output
bases. The predecessor's full 72,353-tensor census is not repeated or counted
as new evidence.

## Discriminating controls

Changing a residue-field basis can change an unnormalized label. The F9
quadratic example has raw label 3 and corrected label 1. The F3 cubic example
has raw label 2 and corrected label 1 for each of the three field-isomorphism
choices. These are proper determinant subgroups, so the controls would fail
if the bridge determinant were omitted.

A supplied product with degree-one and degree-three factors over F3 is
explicitly reordered. Its odd block permutation changes raw label 2 to the
common-reference label 1. Repeated field components use different coefficient
bases, so testing their permutations also exercises field identification.

An absolute p-Frobenius map over a nonprime base is not K-linear. Its images
of a coefficient basis, incorrectly extended K-linearly, fail an independent
product identity and are rejected as a supplied certificate. The valid
q-Frobenius choices remain accepted. Controls also reject noncanonical and
Boolean coordinates, invalid primitive choices, split/nonreduced coefficient
algebras, unequal degrees, changed U/V/W maps, malformed heights, and missing
or wrong-degree reference fields.

## Commands and provenance

```sh
python3 -B scripts/research_package.py --package research/nonsplit-sl-transport
python3 -B scripts/check_research_commit.py --package research/nonsplit-sl-transport --check-source-history
```

Registered replay runs both `-I -W error -B` and `-I -W error -O -B` commands.
Both must print `PASS_NONSPLIT_SL_TRANSPORT` with identical reports. The
committed [RESULT.json](RESULT.json) contains the full report, including its
status. `verify.py --json` emits that canonical JSON directly. The verifier
does not modify the committed report.

All ten consumed predecessor inputs are authenticated before executing the
adapter. The adapter separately authenticates the retained origin manifest
and its nine entries, and compiles source bytes. The verifier also compiles
the adapter bytes directly, so a stale adapter bytecode cache cannot replace
the source. No foreign Git objects are needed at runtime. Original source
notices are retained.

The source-binding orientation command
`python3 -B scripts/research_selected_baseline.py` passed after restoring 1202
exact tracked files omitted by the sparse checkout. This authenticates the
selected source closure and metadata; it is not the selected scientific replay.

## Limits

The proof establishes the field bridge and its composition with the retained
recognition and character theorems. The finite checks do not independently
establish all predecessor hypotheses. The bridge is polynomial in residue
degree at fixed base field; the full reference tables and norm searches have
their explicit enumerative costs.

No selected cold replay, paid native caller, complete physical invoice, Lean
or Docker run was performed. No selected-frontier file is changed. The known
upstream planning-link repair is separately proposed in PR5659; local package
passes do not imply hosted CI success.
