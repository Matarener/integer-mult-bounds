# Exact LU growth after old-H Schur truncation

A scoped written proof derives positive no-pivot LU pivots and the four
retained factor caps for the actual `tau_P(S)` produced by
`physical-gaussian-core`. The key step preserves strict row dominance and
charges elimination multipliers against decreasing row mass. It also yields
`||L|| <= 32p` and `||U^-1|| <= 512p²`, without changing online precision.

[PROOF.md](PROOF.md) states all quantifiers. Global original-H positive
diagonal, gap at least `1/(8p)`, norm below two, exact source correspondence
and the caller’s boundary bandwidth remain explicit hypotheses. This is not
a production coefficient certificate or a complete multiplication theorem.

The exact arithmetic controls cover signed, nonsymmetric matrices and
arbitrary principal interiors. The source adapter observes unchanged encoded
Axis/Window setup, including every write of the actual Doolittle call, then
compares it with independent rational trailing-Schur elimination. Its retained
p16/P24 period-crossing fixture is finite source-binding evidence only.
It passed with eight source rows, three interior rows, five boundary rows
and all 30 actual factor-write states checked. The separate rational family
covers 144 systems and 504 elimination stages.
Nearest-rounding, wrong-reference, zero-gap and norm-hypothesis controls
separate the proof from nearby false claims.

## Reproduce

Python 3.12, standard library only, from repository root:

```sh
python3.12 scripts/research_package.py --package research/old-h-rounded-schur-lu-growth --check-only
python3.12 -I -B research/old-h-rounded-schur-lu-growth/verify.py --algebra-only
python3.12 scripts/research_package.py --package research/old-h-rounded-schur-lu-growth
```

The registered normal and optimized runs execute original encoded setup;
each has a 300-second bound. `RESULT.json` is a mandatory exact typed receipt.
Source hashes are authenticated before source imports. The source contract,
pins and declared input closure are in TASK/SOURCES/VERIFY.json. Historical
catalogue and selected-result provenance are not live scientific inputs.

## Limits

Exact rational setup, reductions, serialization, page preparation and cleanup
retain their original costs. Verification observations are not free algorithm
storage. No online BandedSolve, inverse-block application, normalization,
changed headroom allocation or selected-frontier update is claimed.

## Open next questions

Bind the original-H coefficient gap/norm and period-cut boundary bandwidth
to production coefficient receipts. Start with directed weight/kernel
intervals and the source’s cut geometry; do not extrapolate the finite fixture.

## Credit

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Retains Jose Manuel/jmbarrancoml’s PR3851 physical producer, Hiroki
KUMAZAKI/kumagi’s PR5319 released factor-cap question, James Reed’s distinct
factor-margin arithmetic, and the attributed Gaussian/physical-word lineage.
Frozen inputs and their notices remain unchanged.
