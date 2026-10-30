# A rematched P112 pairing with exact plane-mask fitting rank 34

**Finite algebraic result. No native copy price, supplier or new κ.** The selected
record is unchanged.

[PR #2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484) proves that
for PR1825's fixed matching of the 112 P112 ports into 56 Gram-`I2` planes, the
strict plane-port mask of PR1889 has exact scalar fitting rank **49** over every
field. Its open question 2 asks whether another perfect matching gives less.

**Yes: [CERTIFICATE.json](CERTIFICATE.json) gives a matching with exact fitting rank 34 over every field.**

## Model

The model and labels are PR2484's, and its checking functions are imported
unchanged. Ports `i, j` may be matched iff `q_i.q_i = q_j.q_j = 1` and
`q_i.q_j = 0`. A fitting `K` has `K_ii = 1`, and `K_ij = 0` whenever `i ≠ j`
and the planes at `i` and `j` are not orthogonal. All other entries are free.
The matching is the only thing that changes.

## Result

- **Upper bound 34.** The certificate lists 34 disjoint supports: two per colour
  class of a proper 17-colouring of the plane non-orthogonality graph.
  `K = Σ 1_S 1_Sᵀ` fits the mask (PR2484's `check_fitting_supports` and
  `check_mask_entries`; 11,440 forced entries), and its rank is 34 mod 2, 3 and 1000003.
- **Lower bound 34.** The certificate lists 17 pairwise non-orthogonal planes.
  On their 34 ports every forced entry is fixed, so every fitting `K` contains
  `I_34` as a principal submatrix, and `rank K ≥ 34` over every field.
  This is PR2471's clique argument applied to the new matching.
- **Control.** PR2484's exact clique DP still gives 24 on PR1825's matching.
  Merged supports, a non-orthogonal pair and PR1825's rank-49 supports applied
  to the new pairs are all rejected.

**How far this method can go.** Pairwise orthogonal Gram-`I2` planes have
orthonormal, hence independent, spanning labels, so at most `⌊9/2⌋ = 4` fit in
`F2^9`. Colourings therefore need at least 14 classes, i.e. 28 supports. Fourteen
classes would need a partition of the labels into 14 orthonormal 8-frames. The
labels have 4,032 such frames (288 per label). Randomized packing and local
search found at most **12** disjoint frames, and a bounded exact-cover search
found no partition into 14. The construction here is 12 frames plus an exactly
coloured 16-label remainder (five more classes).

**Related work checked.** PR2118 (`paired-plane-local-swap-seed9c65a5`) already
rematched two edges of PR1825's matching, but to lower a different quantity, the
B14 support-pairing invoice (126 → 96), not this fitting rank. PR3045 and PR1744
bound fitting ranks for port-level root-code masks; PR3045's P112 floor of 64 is
for square root-code decoders, not this plane-level mask (where PR2484's 49 is
already lower). No earlier package, open PR or discussion post found during a
2026-10-17 search reports a plane-mask fitting rank below 49.

## Why it matters, and what it does not show

The plane-port coverage law leaves two unpaid coordinates per family, the
largest single lever in `levers.py` (3.77× ideal). [plane-port-copy-budgets](../plane-port-copy-budgets/README.md)
puts its break-even copy charge near 160 per call. The channel count is an
algebraic floor on that decoder's scalar channels, now 34 instead of 49 for a
suitable matching.

It is **not** a copy price. No native implementation, dirty-input endpoint,
restoration or precision bill is claimed. The scalar-mask obstruction
(`paired-plane-scalar-mask-obstruction`), the native payload checks and other
PR1825-specific results must be rechecked on this matching before relying on it.

## Reproduce

```sh
python3 -B research/paired-plane-rematch-rank34/verify.py      # ~3 s
python3 scripts/research_package.py --package research/paired-plane-rematch-rank34 --check-only
```

`verify.py --write` regenerates RESULT.json. It needs the standard library only.
`discover/` keeps the randomized search scripts as provenance; they use local
absolute paths and are not part of verification.
Registered replay passes locally with Python 3.12.10 (`PASS_REGISTERED_RESEARCH_PACKAGE`).

## Open next questions

1. What is the minimum fitting rank over all matchings: 28 to 34? A first step is to
   prove or refute that 12 is the maximum number of disjoint orthonormal 8-frames.
   Thirteen or fourteen would give 30 or 28 supports.
2. Does the native plane-port contract survive the rematch, and at what copy price
   per channel? A first step is to rerun the scalar-mask obstruction and native
   payload checks on these planes.

## Credit

1337isnot1337 (PR2118) for the first local rematch of these planes; ywz65 (PR2471) for the model, clique bound and bracket; thakrarsagar (PR2484) for the
exact rank 49, the verifier functions reused here, and the open question; Cinna
Davis (PR1825 matching, PR2126 fit); Adam Gall (PR1889 mask); ctoth (plane-port
law, discussion 1587). Found and checked by Claude (Anthropic) via Claude Code, in a
session donated by Mark. Apache-2.0. No human or formal review is claimed.
