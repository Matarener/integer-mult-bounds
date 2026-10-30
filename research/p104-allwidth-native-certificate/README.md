# All-width native certificate for the selected #5599 word

**Scoped positive result; no new κ.** Assumption ID `native_all_columns`, card
`uniform-transfer-audit`. The complete native layer of the selected P104 word
([PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), κ = 62009/20000000)
is certified at every column multiplicity `f ≥ 1`, by an independent method:

- all **2,887 distinct paid chart changes** `Γ_b Γ_a^{-1}`, the **540 helper normalizer pairs**
  (2,923 distinct maps) and the **208 main adapters** equal their compiler-lowered recipes
  (Gaussian monomial · rank-`r` Fourier child · Gaussian monomial) **entry by entry on dense
  512 × 512 exact matrices, including the absolute phase**;
- the operator's column support `2^r` gives `r = |dim b − dim a|`, the paid rank the invoice
  charges (rank mass 6,014 over 3,447 occurrences); helpers are strictly productive with the
  author's profile;
- the certified recipes are **byte-identical to the author's registered payload**
  (`RESULT.json` `native.recipe_payload_sha256`);
- every **distinct Gaussian monomial factor** is realized as a fixed `f`-independent list of
  `XROW`/`NOT`/`S`/`CZ`/`I` records (#5445 grammar), executed exhaustively at `f = 1` and
  sampled at `f = 2, 3`;
- the lift to every `f` is the factorwise tensor power (#5442 lemma); the verifier shows on the
  first MOVE (event 9589, `U = ((1+i)I + (1−i)X_11 Z_3)/2`) that the factorwise lift equals
  `U^{(⊗)f}` at `f = 2, 3` while the termwise lift of the two-term closed form does not.

[PROOF.md](PROOF.md) states the proposition, the dense method and the corollary.
[TASK.json](TASK.json) records the refined scope and the open physical questions.

## Why a second census

[#5837](https://github.com/CrocSwap/integer-mult-bounds/pull/5837) (unpaidmoon) proved the
scalar instructions of this word lift and asked whether its 3,447 MOVEs lift as group identities.
[#5894](https://github.com/CrocSwap/integer-mult-bounds/pull/5894) (DLamdata) traced that the
selected checker already compares signed Pauli images and the exact `|0>` column for every
distinct pair, replayed **one** pair independently, and wrote that a fresh census should be
justified as independent verification of existing coverage. This package is that verification,
for all 2,923 maps and 208 adapters, by a method that shares nothing with the selected checker:
no tableau, no sparse state column, no compiler semantics; full dense matrices, one exact matrix
product per pair, and column supports instead of the symplectic `X`-block for the rank. The
compiler supplies only the candidate recipe, and the payload hash binds those candidates to the
registered ones. The #5442 algebraic certificate covered the older #5413 caller; this is the
same certificate for the current selected caller, plus the #5445 record lists of its factors.

## Reproduce

Python 3.12 with NumPy 2.3.5 (`python3 -m pip install numpy==2.3.5`), from the repository root:

```sh
python3 -I -B research/p104-allwidth-native-certificate/verify.py
python3 -I -B research/p104-allwidth-native-certificate/test_verify.py
python3 -B scripts/research_package.py --package research/p104-allwidth-native-certificate --install-deps
```

`verify.py` prints progress lines and ends with

```text
PASS_P104_ALLWIDTH_NATIVE_CERTIFICATE pairs=2887 distinct_maps=2923 helpers=540 adapters=208 monomials=3711 frames=1089
```

and compares the rebuilt summary with [RESULT.json](RESULT.json) (about five minutes with four worker
processes, one BLAS thread each). The 3,711 distinct monomial factors need at most 96 records each (72 `XROW`),
under the 171-record grammar bound. `test_verify.py` runs ten rejecting controls in about a second. The NumPy
arrays hold only Gaussian integers far below `2^53`, so every product and comparison is exact;
`dense.py` asserts integrality and a `2^40` bound after every step.

## Open next questions

1. Place these record lists and the rank-`r` children in the actual #5599 caller layout with
   the compact-control front/back field reservations for every active slot pair, at the retained
   tariff, starting with event 9589. That is the physical half of `native_all_columns` for the
   current caller.
2. Execute the compact-control rotation scheme itself bit by bit at small `f, K, G` (the
   guard core is audited by seed71/seed73/carry-repair/seed29; the complete scheme with chunk
   swaps is not executed).

## Not claimed

No new κ, no selected-record change, no physical tape implementation, no claim on
`owned_erasure`, `compiler`, `precision_tape` or `analytic_recovery`, no independent human or
proof-kernel review. Credit is in PROOF.md §5. Prepared by Mark (Matarener) with substantial
Claude Code assistance. Apache-2.0.
