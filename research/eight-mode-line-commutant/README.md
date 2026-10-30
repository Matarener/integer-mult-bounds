# Only the characteristic line commutes with a nonzero eight-mode code

For the actual PR5402/PR5578 physical provider, the code W E Z can commute
with a line Gaussian only in the characteristic direction, unless E=0.
This holds for every complex 8 by 8 scalar matrix E, every one of the 511
nonzero binary directions, and every positive lifted digit width. It covers
all mixed and coordinate mode projections, including oblique projections.
No new kappa is claimed.

This closes a specific cheap-decoder route for the current central Gaussian.
It also identifies the one direction that can support further work: the XOR
of all nine axes. Changing the scalar mode basis cannot create another such
direction. A caller must still pay for using the characteristic direction.

[PROOF.md](PROOF.md) gives the exact statement and all-width argument.
[RESULT.json](RESULT.json) records the replay.
[WITNESSES.json](WITNESSES.json) gives 64 independent constraints for each
of the 510 excluded directions. The verifier rebuilds all 32,640 rows from
exact physical recipes. It checks full rank modulo 1009, a separate rational
determinant for the central direction, every normalizer on all 512 addresses,
and both a deleted-constraint control and the characteristic positive control.
The source matrices and literal circuits have separate representation checks.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/eight-mode-line-commutant
```

Both normal and optimized commands must report
`PASS_EIGHT_MODE_LINE_COMMUTANT`. The registered replay is read-only.
`verify.py --emit` writes only the derived result receipt.

The work starts from canonical main
`6cf7a683f447b9f1e2333791907fd92be5009a63`, priority revision 7.
The selected record is unchanged. The original supplier-boundary card is
retained in `TASK.json`; its changed scope is this current code-consumer
boundary. [Discussion5619](https://github.com/CrocSwap/integer-mult-bounds/discussions/5619)
is the canonical investigation. Live PR and Discussion overlap was checked
before the claim and again before submission. The source endpoint and the
complete physical native/provider proof remain credited premises.
No full caller, compiler, precision, outer proof or formal kernel was rerun.
No global decoder impossibility or independent scientific acceptance is claimed.

## Open next questions

- Build and price an actual consumer that uses the characteristic direction.
  Its conversion and helper boundaries must be charged; commutation alone
  does not give a profitable supplier.
- Change the physical mode maps or permit address-dependent mode entries.
  Reconstruct the exact new commutator before using a cheap central decoder.

The structured first steps and blockers are in `TASK.json`.

## Credit

Dugongue PR5578, Dillon Amburgey PR5402, Chris R / Clear1nsight PR5407/5413,
Ali Romman PR5377/5383, Cao Yifan, Cinna Davis, zxv, Jacob Alan Sussman,
Ryanson Jonathan and all retained code/native/controller/compiler authors.
The source notice is retained in `inputs/ATTRIBUTION.md`.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
