# Arithmetic audit of PR #3653's conditional T488 composition kappa

Card `independent-moment`, scope changed (recorded in TASK.json). This package
independently reproduces the **arithmetic layer** of
[PR #3653](https://github.com/CrocSwap/integer-mult-bounds/pull/3653)
("Compose retimed T488 suppliers: conditional kappa 0.001730418899766071163804")
at its publication head `607a09ff441c79b215a8127a81f4cc70021d0d9b`.

No kappa is claimed, nothing is admitted, and the selected record
(kappa = 0.001672660197076918) is unchanged.

```sh
python3.12 -I -B research/t488-composition-arithmetic-audit/verify.py
```

Expected:

```text
PASS_T488_COMPOSITION_ARITHMETIC_AUDIT checks=11 controls=4 (RESULT match)
```

Python 3.12, standard library only. `--write` regenerates `RESULT.json`.

## What is reproduced

All inputs are constants quoted from the audited package's pinned `PROOF.md`
(SHA-256 `7a010afb7a01cded37b18561e903ca580eea5d838456cab0db061a13ad5fd04b`,
blob `7c4a28730db0c10218702a91cf8b42ac0591966b` at head `607a09ff`) and
cross-checked against its `README.md` (blob `f0f003474aa97ca112807829d281708795e0e228`,
SHA-256 `dac5a44abfe961bc86446a6ca6c3b6c76afe588d44c725911e7bd391b1c059b7`)
and `PUBLIC-VALIDATION.json` (blob `0225141ea2122d6035d08c1d5edd6a0695548961`).
The pinned PR #3642 endpoint is quoted from
`research/staged-release-retiming-t530/PROOF.md` at head
`6568db75adbb61437190545f6fef1534c70e91e5` (blob `54ec7d1ab72fd639a35bc1aa7127d1eb33719f01`,
SHA-256 `bee5879b1f48a5a4efec30f75f2f8a348f1bd1eaf5ddf04f7d92a9cf1a904125`).
These external bytes are hash-recorded here, not vendored; a reviewer fetches
the named pull-request head to confirm them.

1. **Aggregate identities.** Rank mass `sum_r profile[r]*r` equals
   `65088*488 = 31762944`; calls `4392 = 488*9`; live families
   `437248 = 896*488`; physical families `437757 = 437248 + 408 + 8 + 91 + 2`
   (408 helper families, 8 centers, 91 private zero buffers, 2 extra fields);
   helper roles `1791936 = 488*9*408`.
2. **Moment root bracket.** With
   `M(a) = sum_r profile[r]*r^(1-a) - 437248*73^(1-a)`,
   an 80-digit Decimal engine gives
   `M(0.001730418899766071163804) = -6.5209934656285285288167e-17 < 0` and
   `M(0.001730418899766071163805) = +2.4654911418492912121937e-17 > 0`,
   so the root lies strictly inside the published adjacent-decimal bracket. A
   160-digit evaluation agrees in sign, and a float engine corroborates the
   coarse signs `M(0) < 0 < M(0.002)` around the bracket.
3. **Local uniqueness.** `M'` at the bracket midpoint is about `+8.9865e7`, so
   the sign change is a genuine upward crossing; and
   `M(lo - 1e-24) < 0 < M(hi + 1e-24)`, so the bracket holds with margin one
   digit outside.
4. **Released string.** Lower endpoint minus `10^-46 - 10^-70` reconstructs the
   published released decimal
   `0.0017304188997660711638039999999999999999999998999999999999999999999999`.
5. **Delta against PR #3642.** `0.001730418899766071163804 -
   0.001730394391813963415120 = 0.000000024507952107748684`, exactly the
   published improvement; and PR #3642's own released string reconstructs from
   its endpoint by the same margin rule, so the comparison baseline is the
   pinned predecessor's published value, not a requote.
6. **Four rejection controls.** A one-unit profile shift (rank 1 -> 2), a wrong
   live count, a wrong width and a degenerate bracket each destroy the
   reproduced straddle/identity.

## What this does not establish

The audited claim is conditional and layered; this package touches only its
arithmetic. It does not replay the word, the literal owner allocation, the two
native providers, the seven admission stages or the full fresh-bootstrap
wrapper. It does not review the 654-file staged source manifest, and it
establishes no acceptance, supplier admission, formal-kernel proof,
independent-human review or selected-frontier change. The inherited all-size,
realization, hosting, precision/tape and analytic assumptions remain the
package's own listed obligations.

## Credit and attribution

PR #3653 and PR #3642 (roger-sato) supplied the audited constants and retain
their full credit lineage (PR #3605, Ross Richardson; PR #3633; hexapode's
PR #3626; and the retained infrastructure contributors recorded in their
packages). The independent arithmetic re-derivation, the two-engine bracket
check, the delta reconstruction and the controls here are new in this package.

Produced by Nick Petalas with AI assistance; independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

1. **Invoice-level audit.** Reproduce the bounded verifier of PR #3653 at its
   pinned head in a clean environment and compare its literal ownership and
   invoice outputs against the published profile; the full fresh-bootstrap
   wrapper replay (runtime unmeasured) stays open with the author's own
   handoff.
2. **Saturation check.** PR #3642's packing certificate bounds its fixed
   inventory's relaxation root by `0.001730418899766071163805`, and PR #3653's
   profile root sits exactly at that bound. Verify in exact arithmetic whether
   the composed profile's moment margin is zero there; if it is, the next gain
   needs a changed word, inventory or model, not another repacking.
