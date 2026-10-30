# Independent C09 cubic review — PASS

Reviewed the complete proof and checker, both frozen mathematical sources, the
frozen README and earlier review, and the final output inventory. No mathematical
or control correction remains requested. The individual-factor pivot prose is
now correctly distinguished from the accumulated `P22=1+ba` entry.

The reviewed final candidate is bound by these SHA-256 values:

| File in `c09-cubic/` | SHA-256 |
|---|---|
| `check.py` | `57c4c002d8bff4ee863a6d8ef359df5532b18b5d3d0fa3b16525f265f16734f1` |
| `PROOF.md` | `d29a6316a0075be95265cfa3336700c690357923687f0a732edc90de3506461e` |
| `CHECKS.json.gz` | `88623b95217b8ec844b0de70d9937ec5a98504c726d061b632d21cc428dd824c` |
| Raw complete receipt | `ed54e928ba5278c58db459a3c69de1cc6c59070f384e254c518d67fff66f31dd` |
| `OUTPUT-INVENTORY.json` | `37d3d3b7cad7e5d5a4afa1cafdffea493c165cb6374b6a7aa8e71baed1c15779` |

The normalization is chronological: immediately before a paid query the
augmentation is `B0`; the new left factor is
`I+(N^e-1)s B0^-1 e_i e_j^T B0`. Updating the augmentation to `E_ij(s)B0`
then preserves `B^-1 W`. Free constant bridges cancel on the same left side.
No paid factors have been commuted. Determinant one then requires `3 | n`.

For the three-bank obstruction, rational rank provides three independent
directions. Any three of four cyclic positions are consecutive, and invertible
cyclic rotation preserves the central target. The two principal minors of
`C3 C2 C1` give the nonrational ratio `-zeta`. This genuinely permits arbitrary
scalar-polynomial coefficients with constant rational directions. It does not
permit operator-dependent direction vectors.

For the wider mixed alphabet, `E=GVU/t` is an idempotent of rank `n`, so
`rank(B-tG^-1)=k-n` is an equality. The complementary triangular split requires
the two specific powers. At `k=4r`, both rational coefficient matrices must have
the same image and kernel. Rank equal to the nonzero diagonal multiplicity
forces zero to be semisimple; it does **not** assume semisimplicity at the
nonzero eigenvalue. The degree-`k` polynomial projectors therefore have the
claimed image and kernel, while their complementary diagonals make equality
impossible. The strict integer bound and power-balance corollary follow.

The layer proofs preserve their premises. Disjoint matching perturbations
annihilate one another before constant conjugation, so a complete normalized
layer is square-zero even if its coefficients mix the two powers. The two-layer
inverse has the reversed factor order and equal trace. The four-layer result
requires each layer to be pure with a rational matrix. Its types must alternate;
cyclic rotation alone gives the displayed order. Splitting both primitive-field
coefficients gives the stated defects, and substitution produces exactly
`DG-(A+AB)=(e+f-3Df)/3`. Only a hypothetical central endpoint sets `e=f=0`.
The subsequent `2DAB=AB` and `D^2=0` contradiction is valid. Four internally
mixed layers are correctly left unresolved.

The matching invoice includes every inactive bank, giving
`mass=60ns+16k` and `D=24n-16k`. Its use is conditional on the stipulated
profile and actual legal matching schedule. Three- and six-bank failures for
positive exponent follow because contracting-child power contributions exceed
their rank mass. No positive wider-bank invoice, native bridge, restored helper,
source transport, or physical implementation is inferred.

`independent_check.py` uses only ordinary rational matrices; it imports no
candidate or historical arithmetic. The full three-cycle represents the entire
ring on `(1,N,N^2)`, while a distinct two-dimensional matrix is used only for
the necessary primitive specialization. The fresh check verifies every prefix
of all four normalization fixtures, all nine independent full-ring columns,
the excluded four-factor identity and literal inverse, the augmentation-only
defect, both nontrivial-Jordan projector formulas, the complete interaction
defect, both pure-layer coefficient identities, and the literal pair inverse.
All twelve independently implemented mutations fail their named predicates and
are then accepted with only those predicates deleted. Normal and `-O`
Python3.12 records are byte-identical.

Independent evidence pins:

| File | SHA-256 |
|---|---|
| `independent_check.py` | `bd6dd0d297f259756f6ea3c1555a05b5232ad568fd8d16d079f8b397876c8cdc` |
| `INDEPENDENT-CHECKS.json.gz` | `32604d0af7774963dde86bc56ad45390a34d71b6711cb85ae56353198f6a7eca` |
| Raw independent receipt | `ce4da1d81691dbfd67e5d98c60316f296a23101a0aa6cb1dce335397a32d4ba8` |

The candidate's 27 controls were also inspected: they use actual altered
operators, directions, projectors, layer defects and invoice data; intended
predicate errors are matched and guard-deletion execution occurs outside the
rejection handler. Captured source bytes are authenticated before unchanged
`compile(...,dont_inherit=True,optimize=0)` execution. Both complete original
receipts retain all typed fields, including augmentation and historical scope.
This review does not duplicate the candidate's entire replay or claim formal
proof-kernel acceptance. It is an independent mathematical/source review with
the separate finite exact checks described above, not independent human review.

Reproduction from a package containing the retained historical receipt:

```
python3.12 -B independent_check.py \
  --historical-receipt /absolute/path/CUBIC-FOUR-CALL-GATE.json \
  --output /absolute/external/new-independent.json
```

No candidate files, Git state, or external records were modified by this review.
