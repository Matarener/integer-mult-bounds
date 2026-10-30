# Internal corroboration and its limits

Separate OpenAI Codex agents checked the source-specific phase algebra and
tensor argument. This is internal AI-assisted review, not independent human
acceptance or a proof-kernel result.

The kernel extension adds a separate native/frame/group implementation in
`independent_kernel.py`. It derives the provider kernel without importing the
primary interpreter, monomial evaluator or discovery eliminator, then checks
the resulting kernel against the original operator-valued histories. Scalar
augmentation is used for discovery, not as a substitute for that final check.
`INDEPENDENT-KERNEL-AUDIT.json` records the result. Normal and optimized runs
pass. The free-word corroboration uses the primary event interpreter with an
alternate algebra and is explicitly not an independent parser.

A separate read-only scope review found the input-fiber argument, raw-backward
R inverse, physical birth-frame conversion, fixed helper/owned values and the
eight partial-cache boundary consistent. That review also replayed the three
kernel scripts normally and with optimization. This is an internal AI-assisted
review, not external scientific acceptance. In the backward case, inability to
identify Y does not mean independence of Y when X is held fixed: the channel
can depend on X-Y.

The older scalar and finite-image corroboration below concerns the initial
publication. Its rank/ABI checks are optional direct entry points after the
kernel extension, rather than current registered proof dependencies.

- `phase_audit.py` uses the pinned signed Clifford evaluator and its absolute
  phase anchor, rather than the primary direct Gram-phase column formula.
  All 147,456 native variants and 36,864 product columns agree, including raw
  backward conjugation. Its phase controls remain active under `-O`.
- `independent_width1.py` separately implements exact Fraction elimination
  with a checked coordinate phase gauge. It recovers physical rank 214 and
  the four-term relation, then computes the actual quotient ranks 546/546,
  554/554 and 554/554 without modular inference. A phase error at input
  column one preserves the permutation and zero-address anchor while raising
  physical operator rank from 214 to 215. The optional author's normal replay
  passed in 90.663 seconds after adapting imports; the final whitespace-normalized
  source replay passed in 105.727 seconds. The
  self-contained receipt is `INDEPENDENT-WIDTH1.json`.
- A separate Gaussian-integer Gram implementation reproduced width-two rank
  215 and determinant 298401053 modulo 1000000009, in normal and optimized
  modes. The optional primary `verify.py` regenerates this certificate.
- A separate literal-normalizer implementation checked all 31,457,280 seed
  Gaussian-kernel entries, and independently reproduced the 1,012/59/59,708
  ABI image/product counts and set hashes. Static review found the required
  physical/logical commutation and finite-family tensor argument valid. The
  portable optional `abi_closure.py` regenerates the published certificate.

The current registered commands, source pins and KERNEL-PROOF.md are the
kernel reproduction path. The older internal Gram and normalizer audits are
corroboration, not additional standalone registered entry points.
Source-generation scripts were not changed to obtain these results.

Optional exact width-one corroboration:

```sh
python3 -I -B research/physical-zqy-scalar-span/independent_width1.py
```

It writes nothing by default and prints
`PASS_INDEPENDENT_EXACT_WIDTH1_PHYSICAL_QUOTIENT`. Its explicit `--write`
option regenerates the separate receipt. This older exact calculation is not
required by the kernel proof or current CI suite.
