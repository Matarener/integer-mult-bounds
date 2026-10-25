# A direct one-pass twiddle header producer

This package constructs a streaming bit-register producer for the source's actual mixed-axis physical address order. It reads every address bit once, retains early low bits until their branch arrives, reuses those registers for the branches, and returns the exact forward or opposite exponent. No supplied circuit topology or address reread is needed.

[PROOF.md](PROOF.md) proves correctness for arbitrary finite shapes. For d participating axes and round h>0, let a be the number of extracted low bits that precede the branches. Its input-boundary data capacity is

    B = d*max(a,1) + h+1 bits.

An explicit Boolean implementation uses at most eight additional scratch bits. Shape descriptions, input-independent schedule/control, output storage and Python object overhead are separate. The executable counts actual AND/XOR calls, and the proof gives their exact bill and O(A*(h+1)+ell) random-access bit-work bound for an A-bit address. This is a register implementation, with no fixed-tape movement invoice.

The proof also establishes an exact lower bound at the earlier physical low-prefix cut. If b=(ell-1) mod K satisfies 1<=b<=h<ell-1, all d axes participate and the reader must distinguish exactly 2^(d*b) suffix functions. It therefore needs d*b bits at that cut. The construction uses d*b+h+1 data bits throughout input consumption, within h+1 bits of this lower bound. Exact optimal peak state count is unclaimed.

For ell=8,K=4,h=5 and twelve mixed axes, the prefix requires 36 bits although the final sum has six bits. The producer uses 42 data bits. A 64-axis ell=256,K=128,h=200 example requires 8128 prefix bits and uses 8329 data bits. These large counts are theorem instances with exact decimal receipts, not exhaustive large-address enumerations.

[RESULT.json](RESULT.json) records 704 complete small physical fixtures with 218136 address evaluations, 71 complete physical prefix/suffix classifications with 27744 evaluations, 378 wide evaluations and 19 boundary rejections. Every exponent agrees with both a direct named-bit formula and the pinned canonical circuit. Read-once consumption, EOF, register widths and actual gate counts agree. Three failed-input cases inspect actual private-register reset. Ten optimized CLI fault groups and a valid retry check scientific, cleanup, source and receipt failures. These finite checks corroborate the author-written proof. Independent human and formal proof-kernel review are unclaimed.

The result advances the physical-address producer handoff. PR3559 counted later canonical-cut states but implemented no producer; PR3550 interprets a supplied program with rereads. [COMPARISONS.json](COMPARISONS.json) records those contextual sources separately. Neither pending head is a proof premise or runtime input here. No fixed-tape compiler, encoded descriptor parser, address enumerator, signed packet/layer join, dirty-workspace caller, complete supplier, kappa gain or selected-frontier change is claimed.

## Reproduce

From the repository root with CPython 3.12 and an existing private external temporary directory:

    python3.12 -I -Werror -B research/streaming-twiddle-header/verify.py
    TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/streaming-twiddle-header/test_controls.py
    TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/streaming-twiddle-header
    python3 -B scripts/check_research_commit.py --package research/streaming-twiddle-header --check-source-history
    python3 -B scripts/export_research_package.py export --package research/streaming-twiddle-header --output /absolute/private/run/package.tar
    python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar

Run verify.py and test_controls.py directly from the export outside Git. Scientific replay needs only the standard library and the three canonical-main inputs pinned by [SOURCES.json](SOURCES.json). The external circuit oracle is authenticated and compiled from its bytes without reading its bytecode cache. The registered runner uses a fresh private cache for package imports; exports contain no bytecode. The default verifier checks the entire receipt; --record deliberately replaces it. Integers above 2^53 in receipts are decimal strings. [ENGINEERING.md](ENGINEERING.md) records implementation limits and diagnostics. These scoped commands do not run the selected full cold replay.

## Open next questions

Lower this direct producer to a fixed number of tapes, then join one actual signed-packet/layer round. Start with the twelve-axis ell=8,K=4,h=5 fixture and its necessary 36-bit prefix. Include the descriptor parser, all shape/program storage, spectators, heads, buffers, source preservation and dirty restoration in the complete consumer invoice. Stop if the consumer or its allowance is unspecified. [TASK.json](TASK.json) records that remaining boundary.

## Credit

Nick Petalas's canonical PR3522 supplies the named-slot and narrow-modulus premise and the independent circuit oracle. The retained transform source supplies the physical order and combined exponent. Credit Philipp/mightyOil's positional engine, Jose Manuel/jmbarrancoml's transform work, Douglas Colkitt, and the retained Nussbaumer/Quandalle and Harvey/van der Hoeven lineage. PR3559 and PR3550 are contextual predecessors under different cut or execution contracts. Frozen notices remain unchanged. New proof and code are by Nick Petalas under Apache-2.0.
