# Uniform CRT evaluator bound, with constant 1

**Scoped counting proof. No new κ.** The selected conditional exponent is
unchanged.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to one proposition. Cinna
Davis's PR #4100 states

```text
E(p, ell) <= C 2^{4 ell} (p+2)^{16}
```

for the sequential Beneš and CRT control evaluator, and then uses

```text
2^{-G} E(p, ell) <= C 2^{-60 ell} (p+2)^{-48}.
```

The October 21 coverage map of #4100 still lists the full uniform `E(p, ell)`
evaluator, starting from CRT data rather than from an encoded permutation, as
unaudited. PR #4192 prices the Beneš component once a permutation is already
encoded. This package prices the missing reconstruction and the four rotation
networks together, and names the constant.

For every integer `p >= 2` and `ell >= 1`, and for every CRT group whose bit
length is at most `p` and every batch of at most `8(p+2)` axes, the procedure
in [PROOF.md](PROOF.md) uses at most `2^{4 ell} (p+2)^{16}` bit-steps. The
constant may be `C = 1`. The same inequality is exactly the displayed guard
amortization. The size paragraph of #4100's `PROOF.md` gives group bit length
at most `p`; the factor 8 is this package's explicit batch cap, not a new
parameter of that construction.

The executed checker agrees with the retained `benes` compiler on 90 rotation
networks, checks 44 CRT offset fixtures, and rejects a non-invertible prefix
and a non-permutation. The bit-step count itself is the counting argument, not
a finite-state tape trace. Reservoir placement, the ordinary interchange
callee, sparse repair, native execution, and the outer multiplication theorem
are not proved here.

Nearest open work, and why this is different: PR #4192 prices the Beneš
component after the permutation is encoded and leaves CRT reconstruction open.
PR #4187 assumes the uniform evaluator and prices only the last-K branch.
PR #4321 compares a guard-density window with the printed `2^{-G} E` display
and does not derive `E`. PR #4174 prices reservoir placement, not this
evaluator.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/crt-uniform-evaluator --check-only
python3.12 -B research/crt-uniform-evaluator/verify.py
```

The verifier prints `PASS_CRT_UNIFORM_EVALUATOR`.

## Open next questions

1. Replay one root-axis query on a single arena, in the sense of PR #4192,
   where every logical access scans the whole arena rather than one table.
   That schedule is more specific than the per-table scans priced here. The
   first step is to feed this package's CRT offset into that arena and compare
   the touch count with `2^{4 ell} (p+2)^{16}`. It is blocked because #4192
   starts from an encoded permutation and is not replayed here.
2. Use `C = 1` inside the reservoir and ordinary-callee argument of `CRT.md`
   §3–§4, including the finite range that falls back to elementary
   multiplication. The first step is the `H >= G` comparison at the stated
   `G`. It is blocked because placement geometry is a separate obligation
   (PR #4174) and is not an input to this evaluator.

## Credit

Cinna Davis supplies the CRT construction, the `E(p, ell)` shape, and the
retained `benes` routine in PR #4100. ToikY's PR #4192 is the predecessor
Beneš-scan audit and states this full-evaluator follow-up; this package does
not depend on its unmerged bound. The coverage map in PR #4311 records that
the evaluator was still open. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Apache-2.0. No independent human review or proof-assistant
acceptance is claimed.
