# Validation

Scientific freeze: `371ae2857654cd3e6588cce81067f2bccb5ed935`.
Base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
Publication changes only this document and spacing in TASK/VERIFY descriptions;
all proof, code, certificate, input and receipt bytes remain unchanged.

The registered Python 3.12.14 replay passed all three suites. Committed-byte
and source-history preflight passed for all 15 package/input files. A checked
committed export passed every direct suite under Python 3.14.7 with `-I -B -O`,
read-only files/directories and no Git on PATH. Its 16 files including the export
manifest were byte-identical after replay. A temporary actual CLI mutation from
integer rank 32 to float 32.0 in RESULT.json failed with
`complete typed receipt differs` under optimized Python.

The optional discovery was replayed with Python 3.12.14, python-sat 1.8.dev24,
CaDiCaL 1.9.5 and six 1.17.0. It completed 79 solver instances and returned exactly
the committed groups: 78 four-group reports, then the first five-group witness.
Negative solver reports are not proof-checked and support no impossibility claim.
The positive certificate, actual strict mask, forced I32 and tariff are checked
without the solver. The larger timed-out pilots are delimited in PROOF.md.

The independent checker reconstructs 50,176 plane-vector pairings, all 11,392
forced scalar entries, dense ranks over GF(2), GF(3), GF(1000003), the complete
plane tariff and all 224 source/dirty-target columns of the ordinary field
program. This is finite corroboration of the written all-field argument, not
formal verification of the multiplication theorem or a physical native replay.

Before publication canonical main was refreshed and remained unchanged. The
snapshot contained 283 open PRs; issues and recent canonical claims were checked.
A [near-simultaneous full-partition claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007973)
appeared twelve seconds before this investigation's original orbit claim and
after its preclaim snapshot. The completed result instead repairs 24 ports and
uses eleven full frames, giving exact rank 32; it leaves fourteen-frame packing
open. That concurrent investigation supplies no dependency or evidence here.

No new κ, full native bill, supplier admission or independent human review is
claimed. Predecessor credit and all scope limits are in README and PROOF.
