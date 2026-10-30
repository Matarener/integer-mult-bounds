# Certified endpoint refinement of PR3857

This package refines the same conditional multiplication construction to

```
kappa = 0.00173057843726624681874071321804985755655644807397156243331276259008002643975681
      - 10^-102 - 10^-126.
```

The strict gain over PR3857 is approximately 7.6259e-61. This is a numerical refinement, not a new geometry or additional verification coverage merely from more digits. The seven-rank profile, 323,069 physical families, 91 private zero buffers, and 2,048-bit payload allowance are unchanged.

The regenerated concrete Lean certificates compile and target-module kernel replay passes with Lean 4.34.1 and pinned Mathlib. Python 3.12 scientific and corruption checks pass. Full native caches, all-size compiler/hosting, source, precision/tape/recovery, analytic and BIT assumptions remain inherited. No fresh complete native-chain run, all-imports fresh kernel replay, independent human review, or unconditional multiplication theorem is claimed.

## Reproduction

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/staged544-refined-endpoint
python3.12 -B scripts/check_research_commit.py --package research/staged544-refined-endpoint --check-source-history
```

The portable verifier can also run directly as `python3.12 -B verify.py` inside this directory. It regenerates finite scientific evidence and checks proof-source bindings; it does not invoke Lean. To reproduce the separate formal checks, enter `lean/`, install the pinned toolchain, then run:

```sh
lake exe cache get
lake build
lake env leanchecker AnalyticCertificate
```

See VALIDATION.json and evidence/ for the completed checks. Tiny sign summaries inherited from the 60-decimal display may round to zero; exact rational comparisons and the dyadic/Lean margins retain their strict signs.

## Open next questions

- Can the exact finite moment certificate be composed with a formal all-size supplier and outer-transfer theorem? Start by connecting the strict moment hypothesis to the pinned profile. The implementation and compiler assumptions remain the blocker.
- Which changed supplier can improve the attained staged544 profile? Screen an exact operator change against the complete inventory cost before native admission. A material gain requires such a construction rather than further endpoint digits.

Prepared by hexapode with substantial OpenAI Codex assistance. Dugongue's PR3857 dyadic evaluator, generic Lean proofs, formal logarithm bounds, and inherited physical/outer engines retain their attribution and licenses. The construction retains ChaloupeMusic/PR3815, hexapode/PR3802, dataisfire/PR3734 and all source ancestry credited in NOTICE and predecessor/PROOF.md.
