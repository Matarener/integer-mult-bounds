# Executed sequential control for synthetic twiddle headers

A four-role tape interpreter now executes the exact address-to-exponent circuits from PR3522. Unary operands direct only unit head movements and sequential cell reads. Both borrowed strings and their head positions return unchanged; the private wire tape returns blank. [PROOF.md](PROOF.md) proves the all-finite-program statement and an exact read/write/move invoice, including program scans and restoration.

The supplied unary program occupies O(p^2) cells under the source parameter bands. This deliberately larger storage differs from the predecessor's written O(p log p) binary-index simulation and remains explicit in the bill. It is absorbed asymptotically by the source's O(rp) per-record allowance under the stated exponential comparison bands. No production shape-to-program compiler, address incrementer, signed-packet/layer join, complete caller, supplier or new kappa is claimed.

[RESULT.json](RESULT.json) records 4,440 exact synthetic headers across 240 programs, including 168 complete small address domains, 16 wider headers through ell=48 and 768 generic circuit cases. Every run matches a separately derived exact operation and cell formula. The largest tested program has 173,135 cells, 422 gates and 1,655,279 executed tape primitives. Thirteen malformed boundaries reject before tape execution. The host emulator's allocations and arithmetic are distinct from the finite-alphabet tape invoice.

Run from the repository root with CPython 3.12 and an existing private external temporary directory:

```sh
python3.12 -I -Werror -B research/synthetic-twiddle-tapes/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/synthetic-twiddle-tapes/test_controls.py
TMPDIR=/absolute/private/run python3.12 -B scripts/research_package.py --package research/synthetic-twiddle-tapes
python3 -B scripts/check_research_commit.py --package research/synthetic-twiddle-tapes --check-source-history
python3 -B scripts/export_research_package.py export --package research/synthetic-twiddle-tapes --output /absolute/private/run/package.tar
python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar
```

The committed Git-free export runs verify.py and test_controls.py directly. All input bytes are authenticated before predecessor code is loaded. The CLI controls run actual optimized subprocesses and require their intended diagnostics. Invalid admitted-machine interruptions do not have a transactional rollback contract.

The baseline is canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. [SOURCES.json](SOURCES.json) pins the exact predecessor runtime, proof premise and retained transform source in that ancestry. Live overlap at 2026-10-18 04:57 UTC covers 248 open PRs and 2,370 Discussion records with complete pagination and no warnings. It excludes arbitrary diff content and a complete closed-PR scan. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19011206) carries the current status.

## Open next questions

Join one mixed-axis round to PR3516's signed polynomial packet routine, supplying encoded shape/topology production and address progression. Charge all program storage, caller counters, spectators, buffering and physical head positions before invoking the normalized layer/root. This would test whether the separate control/data programs compose within the source allowance. The full ordinary/native/hosting and outer transfer obligations remain separate. [TASK.json](TASK.json) records this handoff.

## Sources and credit

Nick Petalas, Apache-2.0. This is a successor to PR3522's explicit circuit and written scan proof, not an independent reimplementation of that circuit or a first encoded phase operation. Credit Philipp/mightyOil's positional synthetic-layout engine, Jose Manuel/jmbarrancoml's signed packing and PR2298/PR3087 physical transform work, Douglas Colkitt and the retained synthetic transform source, including its Nussbaumer/Quandalle and Harvey/van der Hoeven lineage. PR3516 supplies the separate signed data routine and is comparison/handoff context, not a mathematical or runtime dependency here. Frozen inputs and their notices are unchanged.
