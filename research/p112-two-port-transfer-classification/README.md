# Exact two-port transfers for the thirty non-Fano placements

Twenty-nine of PR3547's thirty exact placements admit a coherent GF4 boundary
map and preserve the actual-reader pair floor through every finite graph at
the same three terminals. The unique exception, marks E,F and ports E+G,F+G,
admits no coherent map over any characteristic-two field, in any dimension.
Nevertheless all thirty single-hub stars admit GF4 transfers. At the exception,
the new map uses the hub direction in unreplaced queries.

## Scope and evidence

[PROOF.md](PROOF.md) defines coherence, proves the arbitrary-graph criterion
and the exceptional impossibility, and gives the complete constructive table.
[MAPS.json](MAPS.json) fixes every indexed column. A coherent map must preserve
the difference of the two port images. A star map can change unreplaced queries
using the hub direction. The exceptional positive map therefore proves only
its single-hub result; arbitrary graph-dependent transfers there remain open.

The exact old points are E,F,G,E+F,E+G,F+G,E+F+G. Marks are 01,03,34, and each
row chooses two of its five unmarked ports. Old fields have characteristic
zero; terminal representatives and scalings are fixed. These conclusions do
not automatically cover other marked pairs or scalings.

Two separate exact programs agree on all 3,312 compared subsets, 2,060 true
source and 2,736 true reader premises, all thirteen premises used by the
impossibility proof, and the complete ordered predicate stream. The primary
uses rational/GF4 elimination. The second uses integer minors and all GF4
linear annihilators, without importing the primary. The stream SHA256 is
`894a6e5f59113123150a7803bcaab8bf6514c8ee5052a077135261bc0a187c5f`.
The finite programs certify these premises. The written projection and
impossibility arguments supply the unbounded statements.

The original supplied maps admit thirteen coherent placements. The table
repairs sixteen failed placements; PR3557 already repaired one of those, so
fifteen coherent placements are new relative to that follow-up. The initial
all-thirty-coherent hypothesis was refuted. The unique obstruction and its
separate hub-dependent repair state the resulting boundary precisely.

The consequence is the original actual-reader tariff `m_A+m_B` in the
retained complete-plane binary Gram model, with arbitrary external readers.
This extends a scoped lower-bound family. No cheaper literal bill, physical
supplier, kappa gain or selected-frontier change is claimed. Independent human
and formal proof-kernel review are unclaimed.

## Reproduce

Use CPython 3.12 and its standard library. From the repository root, with an
existing private temporary directory:

```sh
TMPDIR=/your/private/tmp python3.12 -W error -B scripts/research_package.py --package research/p112-two-port-transfer-classification
python3.12 -W error -B scripts/check_research_commit.py --package research/p112-two-port-transfer-classification --check-source-history
```

The registered commands run `verify.py`, `independent.py` and `test_controls.py`
under optimized Python. The controls corrupt a coherent query, the exceptional
hub coordinate, case coverage, the field polynomial, the expected count and a
live source. Both real checker CLIs must reject each fault and pass after
restoration. The twelve rejections and fourteen positive runs use exclusive
owned regular byte copies with distinct source/destination inodes.

The same three scripts can be run directly with `python3.12 -W error -O -B`
on a Git-free committed export, preserving the two declared source paths.
[SOURCES.json](SOURCES.json) pins the canonical inputs and provenance;
[ORIGINS.json](ORIGINS.json) records original credit.
[COMPARISONS.json](COMPARISONS.json) separates the pending PR context. No foreign Git objects or network are needed by scientific replay.
[VALIDATION.md](VALIDATION.md) records the checks and limitations.

## Open next questions

Does the exceptional interface admit a transfer for every finite graph when
the map may depend on that graph? The one-hub construction makes this a real
remaining question, despite the fixed-boundary obstruction. Start with two
hubs and a cycle. Its proof must allow unreplaced query images to use internal
directions, so the coherent criterion cannot answer it.

A physical improvement needs an exact literal operator outside the proved
family, with every rectangular charge and a justified complete consumer bill.
No such cheaper operator is supplied. [TASK.json](TASK.json) gives the concrete
next tests and blockers. Larger/repeated interfaces, other characteristics,
masked identities, physical acquisition, coefficient execution, dirty
restoration, frames, hosting, precision, stock, all-size/compiler admission,
complete suppliers and the multiplication theorem remain open.

This is a changed algebraic scope under `coverage-law-change`. The original
card asks for a replacement coverage identity and a paid endpoint program;
its full acceptance gate is unmet. No dependent physical construction round
is proposed.

## Credit

Nick Petalas. The proof retains Philippe Van Velzen's expanded-identity method,
ctoth's coverage question, the actual-reader lineage through PR3414, PR3463,
PR3472, PR3489, PR3491 and PR3505, and the non-Fano/graph work in PR3506,
PR3524, PR3535, PR3547 and PR3557. The generic support-to-tariff proof and
original templates are declared canonical inputs. Their predecessor credit
remains intact. New work is Apache-2.0.
