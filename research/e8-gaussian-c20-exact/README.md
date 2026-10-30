# Gaussian E8, c = 20: exact certificates (no κ claim)

This package continues §13–§16 of `research/e8-decoder-floors-and-cold14-notes/` (merged in #620). It covers Gaussian E8: 60 ℚ(i)-lines in dimension 4, with the F2 decoder pattern and Theorem-C cost Σβ_j. A decoder beats real E8 only if its cost is ≤ 42. Earlier sections exclude every decoder with c ≤ 19 totals (§15–§16). This package handles **c = 20**.

## Result

| cost cap | cases (deficient-type orbit splits of §16) | status |
|---|---|---|
| ≤ 41 | 20 | **all 20 EXCLUDED, exact certificates** |
| ≤ 42 | 21 | **16 EXCLUDED, exact certificates**: cases −1, 1, 2, 4, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22. **Open:** cases 5, 6, 17, 18, 23 |

Hence **no 20-total Gaussian decoder costs ≤ 41**. Cost 42 is excluded in 16 of its 21 cases. The remaining five sit within 1 of the counting threshold (LP gap < 1), and their branch-and-bound runs had not finished at submission.

**Caveat.** These five may be feasible for the counting relaxation itself. In nearby sub-families a counting-feasible integer solution of cost 42 exists. If so, they can only be closed through the F2 pattern, for example with the exact 2×2 support lemma of §16, and not by this counting model.

## Method

Each case is the §16 covering/packing integer program for c = 20 at the given cost cap: μ ∈ ℤ≥0^60 plus type columns, with clique capacities taken from the deficit budget. `ebb4.py` is an exact branch-and-bound:
- LP relaxations are solved with HiGHS;
- every bound is recomputed from **dyadic-rounded dual multipliers**, checked in exact integer arithmetic;
- probing and reduced-cost fixing are recorded as certified tightening steps;
- symmetry is reduced by each case's stabilizer in the order-11,520 line group.

A certificate records every leaf: its path, the tightenings and the dual vector. `ecert.py` re-checks it **without floating point**: every leaf's exact bound is below the target, and the leaves cover the search space.

## Reproduce

```sh
PY=python3 sh research/e8-gaussian-c20-exact/verify.sh /fresh/dir
# … verified 35 / 35 certificates EXCLUDED (exact)
```

- Requirements: Python 3.11+, numpy, scipy and highspy.
- The script rebuilds the type tables (`hits_table.py` → `orbits.py` → `types_e.py 256` → `dom.py` → `lift_prep.py`; `flats_Gauss.pkl` comes from §14's package), unpacks the gzipped certificates and verifies each one.
- `logs/ecert_all.txt` is our full run over all 36 certificates: **36 / 36 EXCLUDED (exact)**.

**Case 22 (cost ≤ 42) is not shipped:** its certificate is 349 MB, over GitHub's file limit. Its SHA-256 is in `certs/cert_20_42_22.pkl.sha256`, and our exact verification of it is in `logs/ecert_all.txt`. To regenerate it (deterministic, about 1 h), run from a directory holding the rebuilt tables:

```sh
python3 -B ebb4.py 20 42 22 10000000 certs/cert_20_42_22.pkl && python3 -B ecert.py certs/cert_20_42_22.pkl
```

## Files

- `scripts/`:
  - `ebb4.py`: solver;
  - `ecert.py`: exact verifier;
  - `model.py`: case model;
  - `types_e.py`, `dom.py`, `lift_prep.py`, `orbits.py`, `hits_table.py`, `flats.py`, `lines.py`, `f2check.py`: table generators from §14–§16.
- `certs/`: 35 gzipped certificates, plus the case-22 hash.
- `logs/`: the exact verification log and the solver logs.

**Credits.** This builds on the Gaussian-E8 line of §10–§16 and the floors of #595 and #446. Related scoped results: #738, #767, #770, #801, #868, #888, #2066. Prepared by Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
