# B-form floor on P104: RootFact and SpanFact as theorems, Cases II/III without the census (no κ claim)

**Status: research note, follow-up to PR6188 (research/p104-bform-nine-term-floor, merged). Hand proofs, a Lean
formalisation of the two E8 facts, and a short replacement of the Case II/III census by counting plus one finite
lemma (computed). No κ claim, no supplier word.** Only `research/p104-bform-hand-closures/` is added; nothing
existing is changed.

## Claims (scope is part of the claim)

Setting of PR6188: #968's unit P104, characteristic 0, dense label table, cost `Σ_j rank_F₂ B[R_j, A_j]`, rank-9
B-form realisations `M = D₁ G D₂ + c βᵀ` (singular `D` allowed), nine-term decoders.

| # | statement | status |
|---|---|---|
| 1 | **RootFact**: every `x ≠ 0` is non-orthogonal to `≥ 49` ports | PROVEN by hand ([hand/HAND-ROOTFACT.md](hand/HAND-ROOTFACT.md)) and in Lean (`BForm.E8h.rootFact_h`) |
| 2 | **SpanFact**: the corrected span lemma of PR6188 with its 104 port exceptions | PROVEN by hand ([hand/HAND-SPANFACT.md](hand/HAND-SPANFACT.md)) and in Lean (`BForm.E8h.spanFact_h`) |
| 3 | `BForm.bform_floor` with RootFact and SpanFact discharged | PROVEN in Lean (`BForm.E8h.bform_floor_P104_h`); remaining hypotheses `Capacity`, `BicliqueFact`, `CensusFact` |
| 4 | **Cases II/III (any `D`) cost `≥ 56` without the census**: at most one big term has `d ≥ 3` (and `d ≤ 4`), so `≥ 6` pairwise compatible label planes would be needed; Lemma P: there are at most 3 | PROVEN from Lemma P ([PROOF.md](PROOF.md) §4); Lemma P CHECKED (`checks/planes.py`, `checks/cliq.py`) |

Lean `#print axioms` for the three theorems: `propext`, `Classical.choice`, `Quot.sound`. No `sorry`. The finite
checks are kernel computations (`decide +kernel`) on small lists; the whole project builds in about 35 minutes on
Kaggle (4 cores, peak 10.8 GB, about 35 minutes including the Mathlib cache; log `evidence/kaggle/lean-build.txt`).

Item 4 replaces, for Cases II/III, the repo census (`cnt9b`), its propagation bound `lb`, survivor and port
classes, the clique and support filters and PR6188's runs `cnt9c` V0-V3 / `cnt9z` V3 by: the label caps
`f(1..8) = 1, 2, 4, 8, 12, 20, 36, 60`, the pair condition of the M_J bound, and Lemma P (15240 compatible plane
pairs, every plane in at most two of them, no 4 pairwise compatible planes). Only "no 6 pairwise compatible
planes" is used, so the margin is large.

**Overlap.** PR6188 left "formalise RootFact/SpanFact" as its open question 2; this answers it. PR6198
(e8-odd-characteristic-spans) proves other E8 span facts (S1, S2, S3′, W2 of PR2819) over odd characteristic; no
overlap with RootFact/SpanFact. Nothing on main (a5bff3bf1) proves these facts or replaces the census.

**Not covered.** Lemma P is computed, not proved by hand: the root-normal case has no slack (pairs with 3 or 4
uncovered ports exist and are excluded only by the non-orthogonality of the exceptional ports, `evidence/rootcase.txt`).
§4 is not formalised in Lean (`CensusFact` stays a hypothesis there). Unchanged from PR6188: rank-9 realisations of
P104 that are neither B-form nor A2, `≥ 10` terms, P112, E8.

## Files

- `PROOF.md`: the proofs (summaries of the hand proofs, the Lean structure, Cases II/III in full).
- `hand/`: hand proofs and their exact finite checks (`check_hand_rootfact.py` < 1 s, `check_hand_spanfact.py` ~1 min).
- `lean/`: Lake project (Lean v4.33.0-rc1, Mathlib 55b7917b as PR6188). `BForm/E8h/` is new; `BForm/E8/{Data,Defs,
  Bridge,Labels,Normal}.lean` hold the port data and labels; the eight PR6188 files are byte-identical copies.
  `lean/gen/` regenerates `E8h/{Data,Cert,LvEq,SpanData}.lean` from `data/`.
- `checks/`: `fk.py`, `f56.py` (label caps), `planes.py` + `cliq.py` (Lemma P), `sizes.py` (shapes of compatible
  pairs), `rootcase.py` (root-case margins), `maxu.py` (largest union of two live sets).
- `data/`: port coordinates (doubled D8) and labels.
- `evidence/`: logs of the local runs and `evidence/kaggle/` (Kaggle `matare/p104-bform-hand-pkg`: Lean build with
  axioms, Lemma P re-run, hand checks, `f(k)`). Logs are `.txt` because the repo ignores `*.log`.
  `sizes.txt`: the run also tried a union-only graph that was too large and was stopped; that part was removed
  from `sizes.py`, the two printed lines are complete.
- `checks/labels.py` builds the 511 label classes directly as E8 modulo 2 (no networkx); they are the same 511 odd
  sets as `setup9.load('P104')` (checked when the scripts were switched). The logs in `evidence/` and `evidence/kaggle/`
  were made with the `setup9` classes, the `FULL=1` re-run uses `labels.py`; only index-free numbers are compared.

## Reproduce

```sh
python3 scripts/research_package.py --package research/p104-bform-hand-closures --check-only
python3.12 scripts/research_package.py --package research/p104-bform-hand-closures
FULL=1 python3 -B research/p104-bform-hand-closures/verify.py      # also re-runs Lemma P (~12 min)
cd research/p104-bform-hand-closures/lean && lake exe cache get && lake build && lake env lean BForm/E8h/AxiomsH.lean
```

## Open next questions

1. A hand proof of Lemma P, or of its weaker form "compatible planes have disjoint live sets", which already gives
   `k ≤ 5`. First step: the root-normal case through the quadratic form of E8/2E8 (two affine hyperplanes of the
   half `H_y` are parallel or miss a quarter); blocked by the zero margin noted above.
2. Formalise §4 in Lean, which would discharge `CensusFact`.
3. Unchanged from PR6188: classify the rank-9 realisations of the P104 pattern.

## Credit

Prepared by Matarener with Claude (Anthropic) via Claude Code; Kaggle for the runs. Uses PR6188 and the repo's
research/nine-term-outside-colspace (DreamingOfClouds). Apache-2.0.
