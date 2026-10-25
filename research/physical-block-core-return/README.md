# Block boundary result at the normalized Core return

This package carries the actual real/imaginary block-boundary result through
unchanged `Core.second_cell` and `normalize_cell`, then the original disk guard
and complex output order. PR5483/PR5499 stop before this caller boundary.
The adapter compares retaining both selected streams with paying two actual
regathers, including page rescans, child returns, cleanup and retained backing.

[PROOF.md](PROOF.md) derives explicit seven-stage perturbation and magnitude
recurrences from the stored Interior coefficients. It supplies sufficient
intermediate width and final disk conditions; no unspecified inverse constant
or numerical equality with old scalar BandedSolve is used. The exact numerical
reference is the supplied rounded block-factor function. Production Gaussian
coefficient admission, original-S error, full first-pass/block headroom and
complete old-H defect remain separate.

On the same calibration packet, retaining selections pays29,995,126 tape
operations and22,910 retained owner cells; regather pays30,220,120 and22,478.
Retain saves224,994 operations but uses432 more retained owner cells. Common
physical preparation pays946,116 operations separately. This is a measured
time/storage tradeoff, not a universal speedup over scalar Core.

The five-row supplied-factor calibration executes both interior passes for
both components, B4, physical pack/unpack, a cropped return and nonzero final
output. Its boundary diagonal is explicitly1/64 to make normalization visible;
this is not presented as a global-Gaussian matrix. An independent seven-stage
Fraction oracle checks the full complex return and rational numerical ledger.

```
python3.12 -I -B research/physical-block-core-return/verify.py
python3.12 -I -O -B research/physical-block-core-return/verify.py
python3.12 -I -O -B research/physical-block-core-return/test_integrity.py
python3.12 -B scripts/research_package.py --package research/physical-block-core-return --check-only
```

`--write` explicitly generates RESULT.json; ordinary replay compares the entire
receipt. Python3.12 standard library only. Metadata runner, committed-source
history and explicit-input export are separate integrity checks, not theorem
acceptance. Validation outcomes and unrun obligations are in VALIDATION.md.

Base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7. Claim:
[Discussion4182 comment19173370](https://github.com/CrocSwap/integer-mult-bounds/discussions/4182#discussioncomment-19173370).
Overlap covered359 open PRs and4760 Discussion records at2026-10-25T04:32:48Z
and04:33:47Z, plus the root preclaim delta. Coverage is advisory, not proof of
novelty. The R17 analytic task stops at Exponentials/Axis and does not overlap.

## Open next questions

- Bind production coefficient intervals and first-pass/block error to the
  complete return ledger, retaining original-S perturbation separately.
- Compare a real fast boundary supplier's full normalized-call price; no net
  speedup over old scalar Core, recursive paid-job saving or new κ is claimed.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0. Credit Jose
Manuel/jmbarrancoml's Core and calibration, Chafik Boukhalfa's interior inverse
and retained runtime, PR5483's physical layout and PR5499's two-column kernel.
PREDECESSOR records exact retained/adapted helper bytes and public commit;
main scientific inputs and frozen archives remain unchanged. Runtime replay
needs no foreign unmerged Git object.
