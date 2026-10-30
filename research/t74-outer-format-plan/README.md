# T74 root dimension and outer component-order adapters

This package fills PR3477's explicit dimension/format handoff to PR2298.
The retained encoded RootPlan now accepts the fixed exponent `1/40`; a physical
tape adapter reverses each complete signed component before and after the root.
The joined `OuterLayer` uses the actual computed width and whole-packet count.

The [conditional proof](PROOF.md) checks the complete reservation/guard geometry
and O(V) conversion cost for arbitrary complete packets. It retains the T74
native, hosting, ordinary and root-correctness premises. The exact-K routing
bottleneck and selected frontier are unchanged. No new supplier or integer
exponent is claimed.

`ROOT-PLAN.patch` is the complete delta from the retained plan. Its default
exponent stays `997/1000`. Instantiate `RootPlan` from `outer_root_plan` with
`dimension_exponent=(1,40)`, pass that plan to the existing physical root
constructor, then wrap the root in `OuterLayer`. Its `run` takes the same seven
encoded descriptors as that root. Inputs and outputs are MSB-first signed
width `p+2` components, real before imaginary. Consume outputs before reuse.
`prepare.py` assembles the exact retained runtime under an external directory.

## Reproduction and evidence

Use Python 3.12 and an existing external private TMPDIR:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t74-outer-format-plan
```

The registered commands execute the source-closed physical checks and optimized
CLI mutations. `RESULT.json` binds exact outputs for exhaustive signed packets,
encoded floor-root boundary plans, malformed input/reuse controls and complete
reduced root returns with nonzero spectators and multiple coefficients/rows.
`verify.py --write-receipt PATH` regenerates the receipt for comparison.

All 74 retained runtime files are byte-authenticated by `RETENTION.json`.
Canonical bytes are explicit live inputs. The other 38 files are retained
unchanged under `retained/`, with their original notices. The original archive
and public comparison heads/blob IDs/SHA256 are recorded in SOURCES.json.
The two conditional T74 proof premises are retained verbatim under `premises/`,
with exact origin hashes and credit. Other public comparisons are receipts.
There is no fetch step or dependency on an unmerged Git object. Existing
source activation temporarily loads its closed nested archives; those private
directories are explicitly closed before interpreter exit.

The universal statement comes from the written argument. The finite execution
uses a reduced native binding and guard and does not run production T74 native
objects, the full multiplier, Lean or Docker. The original large supplier and
outer proof obligations remain conditional. ENGINEERING.md records validation,
controls and retained-code limits.

## Open next questions

Review the production T74 source-relative refinement and then connect this
adapter to the actual outer caller with its full analytic/error/packing chain.
Start with one literal completed outer synthetic round using the retained
T74 root constructor, this explicit plan and the existing MSB-first packet.
Production native/ordinary/hosting premises and impractical production constants
remain blockers. Another weaker-route parameter optimization is not proposed.

## Attribution

Nick Petalas. Apache-2.0. Jose Manuel's PR3477 supplies the physical T74 root
and identifies this boundary handoff. His PR3385 supplies the retained encoded
RootPlan, root/grid execution and physical cohort. His PR2298 supplies the
outer parameter, signed-format and full cost contracts. Marius-Paul Dumitrean's
PR2979 supplies the T74 word/profile. The retained sources preserve the
compiler, geometry, native, fixed-tape, parking, numerical and hosting lineage,
including Douglas Colkitt, Philipp, Jeremy Kothe, Cinna Davis and Sagar Thakrar.
No frozen predecessor bytes or source-specific notice is changed.
