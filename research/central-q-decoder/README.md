# A fully charged central-Q terminal decoder

**The exact endpoint repair is implemented; a profitable κ improvement is not established.** For a terminal Q⁻¹ P D x, the chronological decoder Q → P⁻¹ → Q returns the independent Gaussian target DQx. Its inverse code stages run in reverse chronological order, without assuming that codes commute with Q or with one another.

This package turns that elementary identity into an actual adapter for the pinned whole-K native data: scalar coefficients, signed normalizers, fresh-axis embeddings, owned storage, cleanup and both Gaussian charges are explicit. The emitter expands every ADD and owner operation. Counts are at the Gaussian/field-operation level; no complete machine tariff is claimed. A literal butterfly implementation also gives an oracle-free implementation with O(fN) scalar work; that variable-width work is not free in the recursion budget.

- Full-rank repair: two additional H1 jobs per owner, regardless of the number of code stages.
- Lower-rank repair: one H1 job per owner, returning D instead of DQ.
- Exact grid: g + 4m + 2⌈f/2⌉ fractional bits suffice for full repair.
- Rounded schedule: added Euclidean error is at most (2f + m)√N·2⁻ᴮ with one rounded output per unitary layer; the supplied native interpreter is exact.

For the inherited p19 planning inventory, repairing whole code words uses 38 H1 jobs per owner, versus 218 for a naive stage-by-stage repair. This comparison is not a saving over the selected multiplier. Even the cheaper lower-rank repair fails the full moment at the selected and tested open κ values. The complete p19 caller and an improved multiplier are not supplied.

[PROOF.md](PROOF.md) gives the universal sufficient results and their scope. [RESULT.json](RESULT.json) records exact replays and price checks. `decoder.py --stages 19` prints the compact chronological plan; its `literal_events` iterator expands all source-bound field operations. `--output FILE` refuses to overwrite an existing plan.

## Reproduce

Python 3.12+, standard library only; no Git, network, Lean or external libraries:

```sh
python -I -B research/central-q-decoder/verify.py
python -I -O -B research/central-q-decoder/verify.py
```

Checks include all 262,144 entries of K², 512 signed inverse normalizers, 1,536 lifted normalizer inverses, actual sparse native-code recovery at widths 1–3 and two genuinely noncommuting fresh stages, full event counts for 1 and 19 stages, and 27 exact rational rounding fixtures. Wrong inverse order, an omitted Gaussian and an omitted actual phase are rejected. Finite tests corroborate the written all-width proof; they are not Lean kernel verification or a full 2,744-cube physical replay. Hosted Linux CI has not been run.

## New E-adapter checkpoint

PR #5464 changed during this session to head 56ba6d7d609124d71c067d6a380caed573963f8f. [E-COMPOSITION.md](E-COMPOSITION.md) applies the generic decoder to its newly supplied three-stage E caller, retaining its local physical contracts and all field-level upper bills. This gives both H73 endpoints at an explicit extra cost of two H1 jobs per owner and three inverse-code evaluations. The completed bill fails the moment test too. The source E package was read and pinned; its full scientific replay was not rerun here. E is not unitary, so the K-specific dyadic-grid and unitary-rounding theorems are not applied to it.

## Current overlap and provenance

Canonical main was pinned to 32890bc5de034ab8fc93ac88ead7279a6a416d04. The current #5464 support appendix, at fc5e6f611eb7a1121be23d6748ecceb61533041e, explains why a fixed finite ordinary postdecoder cannot resolve its distinct-fresh terminal. This package explicitly pays the correction, respecting that result. Its scientific K data remain pinned to the earlier unchanged constructor payload, byte-compared with the latest head during this session. PR #5468 supplies numerical headroom on an unchanged complete profile, not permission to omit these new charges. PR #5467 and the preceding local programmable-stage package remain predecessors.

The shared Lean library supplied navigation to linear-isometry norm preservation (`Mathlib/Analysis/Normed/Operator/LinearIsometry.lean`). No local source path is part of the payload, no Lean theorem is newly checked, and no dependency on an unverified library hit is assumed: the norm argument is written out here. The bounded PR/Discussion search does not prove novelty; the elementary conjugation and stability identities are explicitly credited as classical.

## Open next questions

1. Can a changed caller supply the *current* Q-times-terminal value through an already paid query? Bind the exact input version, owner, frame and later uses first. This could remove one decoder charge; no such reuse is assumed here.
2. Can an overlapping-stage or earlier-readout construction retain every independent Gaussian target with a positive complete bill? Start with a fully emitted small instance and its endpoints, because the fixed distinct-fresh postdecoder is already covered by #5464.
3. If a profitable caller appears, bind these exact code/precision operations to its limb arithmetic, movement, storage, stock, compiler and analytic contracts. Decoder correctness alone does not admit those costs.

## Credit

THU New Media Research Center / #5464; Ali Romman / #5439; Dugongue / #4929 and #5467; Dillon Amburgey; Cinna Davis / #4470; Ryanson Jonathan / #4516; zxv (the retained exact interval engine); Cao Yifan; Jacob Alan Sussman; Chris R / Clear1nsight; and the retained native, helper, Clifford, compiler and analytic contributors. Existing source notices are preserved. Original adapter, checks and exposition prepared for Dugongue with substantial OpenAI Codex assistance by one solo worker. Apache-2.0.
