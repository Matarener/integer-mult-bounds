# Nine-term decoders of B-form realisations of P104 cost at least 56 (no κ claim)

**Status: research note. Written proof, exact finite checks, two recorded Kaggle census runs on top of the repo's
case-(b) census, and a Lean formalisation of the algebraic reduction. No κ claim, no supplier word.**
Only `research/p104-bform-nine-term-floor/` is added; nothing existing is changed.

## Claim (scope is part of the claim)

Setting of #2338 / research/nine-term-outside-colspace on #968's unit P104 (characteristic 0, dense label table,
cost `Σ_j rank_F₂ B[R_j, A_j]`). Let `M = D₁ G D₂ + c βᵀ` be a rank-9 **B-form** realisation of the P104 pattern
(`c_u β_s = 0` on orthogonal pairs; `D₁`, `D₂` diagonal, **singular `D` allowed**). Then **every nine-term decoder
`M = P Qᵀ` costs at least 56.**

| part | statement | status |
|---|---|---|
| Case I | `|supp c|, |supp β| ≤ 12` | PROVEN, Lean `BForm.caseI` (from S0, S1) |
| y = 0 | a term with zero column root part | PROVEN, Lean `BForm.yzero` |
| Case II/III | `|supp β| ≤ 4` (or `|supp c| ≤ 4`), any `D` | PROVEN reduction (Lean `BForm.caseII`, `caseIII`) to the census statement `CensusFact`; census RECORDED (Kaggle), 0 alive |
| coverage | S3: `|supp c| ≥ 13` forces `|supp β| ≤ 4` | CHECKED (`checks/bicliques.py`) |
| S0, S1, S2' | label caps, `|N(x)| ≥ 49`, span input with its 104 exceptions | CHECKED (`checks/spanlemma.py`) |
| lbz | exact root-rank bound after removing ≤ 4 non-orthogonal ports | CHECKED self-test (`checks/lbz.py`) |

Lean (`lean/`, Mathlib pinned as in research/p104-carrier-code-uniqueness): `BForm.bform_floor` builds without
`sorry`; axioms `propext`, `Classical.choice`, `Quot.sound`. The finite facts and the census enter as named
hypotheses (`Capacity`, `RootFact`, `SpanFact`, `BicliqueFact`, `CensusFact`); see `lean/README.md`.

**Overlap.** e8-rank9-realisations §5 lists the B-form decoder floor as open (Case B for `|supp c| ≥ 2`, special
`c, β`, singular `D`); a2-family-decoder-floors and a2-family-b-locus cover the A2 family. Nothing on main
(3f0152a32) proves a B-form floor on P104.

**Not covered.** Rank-9 realisations of P104 that are neither B-form nor A2 (their classification on P104 is
open; e8-rank9-realisations is for the full E8 unit); decoders with `≥ 10` terms; P112 and E8.

## Proof

[PROOF.md](PROOF.md). In short: the normal form `P = X U`, `Q = Y W`, `U Wᵀ = 1` of a nine-term decoder; Case I
by counting (eight terms with both root parts non-zero, each with `≥ 37` ports on both sides); in Cases II/III the
rows obey the M_J bound with the exact root rank after removing the `≤ 4` singular rows, and the columns can miss
a label class only at a survivor or at a port class (span lemma with the S2' exception). The repo's census, rerun
with port classes as extra column classes, repeated survivors and (for singular `D`) the root-rank bound `lbz`,
finds no configuration.

## Evidence

- `evidence/kaggle/floor-v2/`: S0-S3 run (Kaggle `p104-bform-floor` v2). That run used the uncorrected S2 and
  reported FAIL on exactly the 104 port pairs; `checks/spanlemma.py` now asserts that structure (S2').
- `evidence/kaggle/census-v1/`: repo pipeline regenerated (aut104, cliques, pairs_fast, cnt_P104.pkl from the
  recorded lb22), `cnt9b` control 701 / 0, `cnt9c` V0-V3: 701 configurations each, 0 alive.
- `evidence/kaggle/singular-v1/`: `lbz` self-test, `cnt104z` (415 pairs with `lbz ≤ 7`), `cnt9z` V3 (740 pairs,
  446 configurations, 0 alive).
- `kaggle/`: the drivers (code embedded; repo files from main 3f0152a32 / 463113d67, identical for this directory).

## Reproduce

```sh
python3 scripts/research_package.py --package research/p104-bform-nine-term-floor --check-only
python3.12 scripts/research_package.py --package research/p104-bform-nine-term-floor
```

The bounded verifier re-runs S0-S3 and the `lbz` self-test, authenticates the logs and reads the census numbers.
The full census replay (about 1.5 h on 4 cores) is the Kaggle drivers in `kaggle/`. Lean: `cd lean && lake exe
cache get && lake build`.

## Open next questions

1. Classify the rank-9 realisations of the P104 pattern (B-form, A2, or other): with this package and the A2
   floors, a positive answer would close case (c) of #2338 on P104 for nine terms.
2. Formalise the E8 hyperplane classification so that `RootFact` and `SpanFact` become Lean theorems.

## Credit

Prepared by Matarener with Claude (Anthropic) via Claude Code; Kaggle for the census runs. The census code is the
repo's research/nine-term-outside-colspace (DreamingOfClouds), extended. Apache-2.0.
