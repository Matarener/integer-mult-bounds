# Physical block arithmetic for the actual two-component RHS

The actual Gaussian RHS caller supplies real and imaginary columns, but the
inverse-block consumer computed all B padded columns. This package checks the
inactive columns physically and computes only the first two. It preserves the
original exact term order, wide precision, rounding sites, page layout, full
padded output, protected owner and cleanup. B<=2 retains the original kernel.

For K=ceil(n/B), the B>2 complete scalar count falls from
`2(2K-1)B³` to `4(2K-1)B²`. The mandatory actual-Core B4 gate compares complete
physical consumer invocations, not just these counts: the two-boundary-row
case falls from 7,017,713 to 4,200,707 reads/writes/unit moves, while owned
retained backing falls from 9,953 to 9,731 cells. Scalar calls fall 128→64.
The cross-block five-boundary-row B4 case falls from 21,413,925 to
12,862,809 operations and from 13,697 to 13,511 retained cells. B1/B2
preserve output but incur small encoded dispatch overhead.
All padded output bytes agree with the unchanged consumer and an independent
Fraction oracle; same-owner reuse preserves the exact bill and backing.

[PROOF.md](PROOF.md) establishes the source-relative zero-column invariant and
complete local tariff. This is an ordinary scalar-arithmetic saving. It does
not change recursive paid profiles, establish a new κ, install the normalized
Core second pass or supply the proposed seven-product kernel. Exact
LU(round_P(S)) remains the supplied reference; the old scalar BandedSolve has
a different rounding contract. Arbitrary disjoint dirty spectators are
preserved; owned scratch retains the original blank-entry requirement.

The verifier executes unchanged actual `Core.gather`/`Core.first_cell` for
both components. The two-cell eight-row fixture gives five boundary rows and
a nonzero cross-block dependency; B1/B2 exercise fallback. Separate physical
controls distinguish early per-term rounding, omitted active columns and
nonzero inactive input, with successful reuse after rejection.

```sh
python3.12 -I -B research/physical-two-column-boundary-kernel/verify.py
python3.12 -I -O -B research/physical-two-column-boundary-kernel/verify.py
python3.12 -B scripts/research_package.py --package research/physical-two-column-boundary-kernel
```

Use Python3.12 and the standard library. `--write` explicitly generates a
receipt; normal replay authenticates source/helper hashes and compares the
complete typed receipt. Inputs and original runtime archives are declared
for committed Git-free export. [VALIDATION.md](VALIDATION.md) records evidence
and unrun obligations; finite checks are not independent human or formal proof.

Canonical claim: [Discussion4182 comment19173186](https://github.com/CrocSwap/integer-mult-bounds/discussions/4182#discussioncomment-19173186).
Base32890bc5de034ab8fc93ac88ead7279a6a416d04, priority7. Fresh overlap covered
352openPRs and4747Discussion records at2026-10-25T04:13:18Z/04:14:44Z. The
nearest completed scope is PR5483's RHS transport, which does not change this
kernel. Coverage does not prove novelty or rule out unpublished work.

## Open next questions

- Bind the actual block-aware second-cell/normalization error and width ledger.
- Identify a real many-field supplier before changing R=2 to arbitrary fields.
- Price actual seven-product tape quadrants and parked recursion before using
  a subcubic matrix bound.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0. Credit Jose
Manuel/jmbarrancoml's Core, runtime and block handoff; PR5483's actual RHS
binding; Vlado Vojdanovski, Cinna Davis, Chafik Boukhalfa and the retained
Gaussian/FFT/tape lineage. `source_pair.py` and `rhs_layout.py` retain PR5483
bytes; `source_fixture.py` adds the stated two-cell case. PREDECESSOR records
public source hashes and credit; all runtime helper bytes are self-contained.
No foreign unmerged Git object is required for replay or source-history checks.
