# An optimal dyadic compiler for sector-shared Gaussian queries

For a map F=A(J)+B(J)Q over finitely many commuting ordinary involutions,
this package emits an exact dyadic word with

    max_sigma rank(B_sigma)

Gaussian queries. A matching lower bound covers arbitrary interleaved linear
queries, retained results and feedback in the stated alphabet, when I and Q
are independent in every sector. The usual lifted Gaussian with independent
spectator translations satisfies that condition for every width f>=3.
No new kappa or installed caller saving is claimed.

This makes the PR5578 T6 upper bound executable and optimal, and extends it
beyond two sectors. A verified 32-sector invertible map uses one query instead
of 32 separate sector queries. It also uses 2080 shifted ADDs, 34 CLEARs and
33 owned fields including outputs. Those costs must be paid by a caller.
The existing scalar role-gauge tariff rank(RM-MP) is exact in this alphabet;
sector sharing alone cannot improve an already factored boundary of that form.

Read [PROOF.md](PROOF.md), [packing.py](packing.py), and the exact
[RESULT.json](RESULT.json). The input format lists the matrices of A and B
by Boolean mask in `even` and `odd`. Mask bit zero represents J_0=Q squared.
All coefficients must be dyadic. The example is the credited PR5578 T7 map.

```sh
python3.12 -I -B research/optimal-sector-query-compiler/packing.py \
  research/optimal-sector-query-compiler/EXAMPLE.json \
  --output /tmp/sector-word.json
python3.12 -B scripts/research_package.py --package research/optimal-sector-query-compiler
```

The output path must not exist. Compilation does not overwrite source files.
The registered normal and optimized commands are read-only and report
`PASS_OPTIMAL_SECTOR_QUERY_COMPILER`.

The verifier checks all 6561 pairs of small two-sector matrices, 72 rectangular
cases, 72 role-gauge boundaries and 160 feedback words. It executes each emitted
word on all input and dirty-owned columns in the exact algebra. An independent
rank calculation checks the minimum. Literal tensor Gaussian matrices check
the two-field example at widths 1 through 4. Corrupt operation, sector and
cleanup controls reject.

The base is canonical main `6cf7a683f447b9f1e2333791907fd92be5009a63`, priority 7.
[Discussion5623](https://github.com/CrocSwap/integer-mult-bounds/discussions/5623)
records the live overlap check and the C8 handoff-led scope override.
`TASK.json` retains the original formal-interface card. This is a written
interface proof and exact compiler, not a Lean formalization.

The unchanged Smith utility is vendored from PR5615 head
`d914f77d948ac377bdb9823daca93d08913c3fa7`. `INPUTS.json` binds its exact bytes,
Git blob and public source path. The registered replay needs no pending Git
object. The main proof inputs have base provenance pins in `SOURCES.json`.
This is source authentication, not scientific acceptance of every source claim.

The minimum applies only to the declared scalar/involution alphabet and
single-field Q or Q inverse queries. All formal sectors must be faithful.
Other address maps, noncommuting coefficients, higher-rank queries and changed
snapshots are outside it. Output buffers contain the requested map of the
original inputs; they are not new independent productive helpers. No native
caller, precision, movement, compiler or outer budget has been certified.

## Open next questions

- Extract one actual caller section into the declared algebra on one lawful
  input snapshot. Compare its emitted query count and all ordinary costs with
  its current word. A formal coefficient match must precede target credit.
- Where the sharp role-gauge count is too high, change the complete boundary
  defect or the address alphabet. More feedback within the same algebra cannot
  improve that minimum.

Structured first steps and blockers are in `TASK.json`.

## Credit

Dugongue PR5578/5586 supplies the sector mechanism, example and caller target.
Ali Romman PR5615 supplies the unchanged Smith utility. Retain Cao Yifan,
DaysSky, Cinna Davis, Nick Petalas, Ryanson Jonathan, zxv, Jacob Alan Sussman
and all native/controller/compiler authors named in the pinned source notes.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
