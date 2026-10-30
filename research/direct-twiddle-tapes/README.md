# Direct one-pass twiddle arithmetic on four data tapes

This package executes the retained synthetic transform's address-to-exponent arithmetic through current-cell reads/writes and unit head moves. Four Boolean tapes hold the borrowed address, recycled pending/branch bank, narrow accumulator and complete output. Every address cell is read once. The machine returns its head without rereading, preserves its bits, returns both private tapes blank and returns all heads to zero.

The immutable shape scheduler is supplied separately. Its parsing, counters and instruction-generation costs are excluded. This closes the direct producer's sequential data-access/restoration subtask with an author-written all-finite-shape proof. It does not implement a complete encoded uniform controller or packet/layer consumer.

For d participating axes, round h and a early lower positions per axis, put P=max(1,d*max(a,1)). For physical address length A, exact data capacity is

    A + P + h+1 + ell+1 Boolean cells,

plus at most eight transient Boolean values. [PROOF.md](PROOF.md) derives exact per-role reads/writes/unit moves and Boolean counts, bounded by 20*(A+ell+1)^2 charged data operations. Under the source's A=O(p) band this is O(p^2) data work and O(p) data cells. Shape control, Python objects and diagnostics are separate. No total-machine comparison or measured speedup is claimed.

The ell=8,K=4,h=5 twelve-axis example, three long and nine short, uses 138 data cells including input/output and 2292 charged operations forward, 2252 opposite. The ell=256,K=128,h=200 mixed two-axis example uses 1223 cells and 282645/281240 operations. These are exact data-tape/logical counts, not CPU timings. [RESULT.json](RESULT.json) records 700 complete small fixtures and 203896 addresses, 30 wide evaluations, fifteen boundary rejections and three actual failed-read restoration/retry cases. Independent named-bit arithmetic, canonical circuit and shape-derived bills agree. Ten optimized actual CLI fault groups reject semantic, movement/restoration, source and receipt corruption.

This refines Nick Petalas's PR3571 direct register producer, which left unit-head lowering open. PR3550's compact supplied-circuit interpreter has a different program/reread contract; PR3559 classifies residual-state cuts. [COMPARISONS.json](COMPARISONS.json) records exact comparison heads/documents outside canonical ancestry pins. No pending theorem is imported: arithmetic and physical bills are proved here from the three canonical inputs in [SOURCES.json](SOURCES.json), also declared by [VERIFY.json](VERIFY.json). Canonical circuit/proof and frozen transform notices remain unchanged.

Credit remains with Nick Petalas and the retained synthetic-control lineage, including Philipp/mightyOil's positional engine, Jose Manuel/jmbarrancoml's signed-packet work, Douglas Colkitt and the retained Nussbaumer/Quandalle and Harvey/van der Hoeven sources. Apache-2.0.

## Reproduce

Use CPython3.12, standard library only, with an existing private temporary directory outside the checkout.

```sh
python3.12 -I -Werror -B research/direct-twiddle-tapes/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/direct-twiddle-tapes/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/direct-twiddle-tapes
python3 -B scripts/check_research_commit.py --package research/direct-twiddle-tapes --check-source-history
python3 -B scripts/export_research_package.py export --package research/direct-twiddle-tapes --output /absolute/private/run/package.tar
python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar
```

Unpack the committed export outside Git and run its verify.py normally and with -O, then test_controls.py using the private TMPDIR. All scientific/control dependencies are committed and declared; no foreign Git object, network or pending branch is needed. Metadata/pin checks use repository history. Final session receipts record actual executed HEADs and source/export before/after hashes. Finite success does not establish independent human/formal acceptance or a complete multiplication theorem.

## Open next questions

Can an encoded uniform fixed-tape scheduler generate these accesses and feed an actual signed packet consumer with an affordable complete bill? Start with ell=8,K=4,h=5 and twelve mixed axes. Specify encoded shape/descriptor leases and the exact header-to-packet boundary. Charge parsing, counters, program/descriptor cells, enumeration, spectators, all movement and required dirty restoration. Stop if those contracts/allowances are unavailable. [TASK.json](TASK.json) records the changed scope and blocker.

No full caller, arbitrary dirty-private contract, native/root/ordinary refinement, analytic transfer, supplier, new kappa or selected-frontier change is claimed. [ENGINEERING.md](ENGINEERING.md) records runtime deviations and verification limits.
