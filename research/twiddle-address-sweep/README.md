# Stateful physical-address twiddle streams

The synthetic twiddle exponent can be maintained across a binary scan of physical addresses. This package constructs the stream on four sequential Boolean data tapes and proves O(M(A+ell)) charged data work for M records, with O(A+ell) data cells. Each address-bit flip updates a cached branch/low word and one narrow modular sum. There are exactly sum_j floor(M/2^j)<2M flips, including each post-header advance. A complete N=2^A cube has 2N-2 flips.

This changes the source contract from unrelated borrowed addresses to one owned odometer in canonical storage order. Under A=O(p), the data upper bound becomes O(Np) for the full stream, compared with O(Np^2) from repeating the independent-header data bound. It is an amortized asymptotic bound, not a measured speedup. The immutable shape scheduler and paused output consumer are supplied separately; their encoded control and physical consumption are excluded. No full uniform machine, supplier, kappa or selected-frontier improvement is claimed.

[PROOF.md](PROOF.md) gives the all-finite-shape arithmetic, head movement, restoration, exact invoice and complete obligation ledger. Capacity is A+max(1,d*(h+1))+h+1+ell+1 data cells plus at most twelve transient Booleans. All owned data and heads return blank/zero, including partial prefixes. Arbitrary dirty initial tapes are excluded. Only the current header is stored.

[RESULT.json](RESULT.json) records 480 complete fixtures and 110520 headers in both directions. Every output matches independently reconstructed named-bit arithmetic and the authenticated canonical circuit; every exact read/write/unit-move/gate/cell invoice agrees with a separate shape-only calculation. Another 277 prefix headers and 21 wide valid-state transitions cover long carry chains, early low-prefix bits and ell through 256. Wide states are installed diagnostically, not by a charged initializer or complete stream. The ell=4,K=2,mixed two-axis,h=2 full stream has 128 headers, 254 flips, 21 data cells and 18481/13621 charged operations forward/opposite. These are model counts, not CPU timings.

Fourteen malformed/single-use boundaries reject, an actual consumer exception after five headers clears every tape/head, and seven optimized CLI mutation groups fail before a valid retry. Independent human and formal proof-kernel review are unclaimed. Source/metadata integrity and scientific replay are separate checks.

## Reproduce

Use CPython 3.12 and a private external temporary directory.

```sh
python3.12 -I -Werror -B research/twiddle-address-sweep/verify.py
python3.12 -I -O -Werror -B research/twiddle-address-sweep/verify.py
TMPDIR=/absolute/private/run python3.12 -I -O -Werror -B research/twiddle-address-sweep/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/twiddle-address-sweep
python3 -B scripts/check_research_commit.py --package research/twiddle-address-sweep --check-source-history
python3 -B scripts/export_research_package.py export --package research/twiddle-address-sweep --output /absolute/private/run/package.tar
python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar
```

Extract the committed export into an owned external directory and run all three direct commands there. All runtime and inherited mathematical premises are committed in canonical ancestry and declared in [SOURCES.json](SOURCES.json)/[VERIFY.json](VERIFY.json); scientific replay needs no foreign Git object or network. The exporter does not run science. The executable caps ell<=256, axes<=64 and M<=4096; the universal claim rests on the written proof. [ENGINEERING.md](ENGINEERING.md) records code constraints and runtime deviations.

## Open next questions

Can an actual signed-packet consumer pause after each canonical address, consume this header and return its control/head leases within one complete paid allowance? First specify one ell=6,K=2,mixed-axis,h=4 caller and join its exact enumeration order, descriptor encoding, header observation, spectators, record spacing and cleanup. Encoded scheduler generation and physical packet integration are blockers. Another independent-header inverse or local constant does not resolve that boundary. [TASK.json](TASK.json) records this question and the bounded expansion decision.

## Credit and scope

Nick Petalas's canonical PR3522 circuit/proof and PR3571/PR3582 independent-header producers supply the credited context. The actual mathematical premises are the unchanged canonical circuit proof and retained transform; pending producer theorems are not imported. [COMPARISONS.json](COMPARISONS.json) separates those comparison heads from source ancestry. Credit remains with Philipp/mightyOil's positional engine, Jose Manuel/jmbarrancoml's signed-packet work, Douglas Colkitt and the retained Nussbaumer/Quandalle and Harvey/van der Hoeven transform lineage. New work is Apache-2.0; frozen sources and notices remain unchanged.
