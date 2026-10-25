# Original complex-root address partition

Copyright 2026 Sagar Thakrar. Apache-2.0. Prepared with substantial OpenAI
Codex assistance, including separate same-session proof, implementation and
adversarial-review agents. This is not independent human acceptance.

This package independently checks the original
[PR3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385) root's
internal address boundary: reserved leaves, row padding, recursive core
descriptors and removal of padded rows. The exact source is
`7e5a187214126d31afc241a8f89f4a652352b58c`, retained unchanged on canonical
main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Conditional result

For `a=q0+qF` and `c=D-a-qB>0`, the three calls act on original selected
indices `D-a..D-1`, `0..qB-1`, and `qB..D-a-1`, respectively. Thus they
partition exactly the D axes at positions `right+rho+j*K`. The core field
identity is

```text
core_front + 3H + cK + core_back = (D-q0)K + right.
```

[PROOF.md](PROOF.md) derives the complete address/row serialization and
shows that padding preserves every original prefix, row, address, field
and component. Appended rows stay zero under the **completed rowwise linear
recursive endpoint**, even if intermediate machine steps mix rows. The
unchanged zero check then permits removal. The production stock law gives
the already-claimed strict volume factor below two.

These are conditional source refinements. The leaf and recursive tensor
endpoints, numerical admissibility and physical ownership remain explicit
premises. No new tensor identity or padding factor is claimed.

## Added verification coverage

The original joined fast-root fixture uses spacing one, residue zero, no
spectators, one coefficient/outer row, and no added rows. Its stream tests
exercise spacing and padding separately. The newer T74 outer-format adapter
tests spectators and multiple fields/rows in direct roots while retaining
root correctness.

Here the unchanged `reserved_leaves`, `apply_leaf`, `accept` and `fast_core`
code executes with real encoded Counts, tapes, row padding and transfers.
Declared leaf and recursive **permutation endpoints** move coordinate-tag
records along the selected axes. Independent expectations use the original
address formula, and every recursive descriptor is checked. These endpoints
are layout witnesses; they do not execute C arithmetic or the production
recursive machine.

The reduced plans use spacing two, residue one, nonzero spectators, two
coefficient fields and two outer rows. Their stock is three, with `q0=2`,
so sixteen original rows are padded to eighteen **for each prefix**.
Plans are supplied explicitly and satisfy the address identities only:
for example, their `H=G=1` does not satisfy production `H=dG`.
The fixtures do not execute `RootPlan.compute` or certify production
admissibility. The written proof states the general plan identities separately.

The two fixtures carry 8,192 and 32,768 distinct sixteen-bit records.
The inherited `Layout.bit_position` conversion is checked for both leaves,
the core and the full address, and distinguishes the opposite residue.
This regression was added after adversarial review caught a reversed-residue
convention in the initial test oracle; the retained receipt uses the corrected
least-significant-bit convention. Six negative controls reject source drift,
wrong residue, wrong core width, wrong prefix count, an omitted reserved leaf
and nonzero returned padding.

## Reproduction and sources

From the repository root with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/complex-root-address-refinement
```

[VERIFY.json](VERIFY.json) registers ordinary and isolated optimized
warnings-as-errors checks. [SOURCES.json](SOURCES.json) pins the complete
live source closure, including the inherited physical-cohort archives.
No predecessor files are changed. [RESULT.json](RESULT.json) records exact
fixture digests and rejection controls.

Both registered commands passed on CPython 3.12.15/Linux. Metadata checks
passed, and all eleven live controller inputs were separately compared
with their original PR3385 Git bytes.

## Attribution and limits

Jose Manuel (`jmbarrancoml`) supplied PR3385's root, plan, physical streams
and source chain. Its original proof already gives the tensor split,
padding/carving argument and volume bound. Nick Petalas's
[PR3493](https://github.com/CrocSwap/integer-mult-bounds/pull/3493) checks
the changed T74 outer dimension/format boundary and retains root correctness.
The authenticated runtime setup/cleanup follows Sagar Thakrar's
[PR3464](https://github.com/CrocSwap/integer-mult-bounds/pull/3464).
All retained source notices and archive attribution remain intact.

This contribution adds independent source binding, an explicit address
derivation and a combined nontrivial layout fixture. It does not prove
recursive/native arithmetic, the numerical normalization/truncation chain,
production parameter computation, full O73/GL64 execution, a uniform cost
invoice, changed T74 correctness or an outer multiplication theorem. The
selected frontier is unchanged. The proof is written mathematics, not a
proof-assistant kernel certificate.

## Open next questions

* Independently refine a remaining original recursive arithmetic or factory
  implication. Resolve the current Discussion handoff and exact sources
  first; this package's permutation endpoints cannot discharge it.
* Before reusing the result for a changed T74 caller, compare its current
  root/plan descriptors and endpoint contracts. This audit binds only the
  original PR3385 source.

Structured first steps and blockers are recorded in [TASK.json](TASK.json).
