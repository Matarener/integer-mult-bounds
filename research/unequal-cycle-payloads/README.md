# Exact query dimension for unequal cycle payloads

For a five-cycle fitting matrix with identity diagonal blocks of arbitrary
nonnegative sizes `d_0,...,d_4` and zero ordered nonneighbor blocks, the exact
minimum rank over **every field** is

```
max(max_i(d_i + d_(i+2)), ceil(sum_i d_i / 2)).
```

[PROOF.md](PROOF.md) proves the lower bound by subspace intersections and
constructs an attaining matrix. Free blocks can be rectangular, nonsymmetric
and noncommuting. [cycle.py](cycle.py) computes a compressed optimum using
five edge counts and five private counts, with constant many integer operations
and O(b) bit cost for b-bit dimensions. Expanding or moving payloads has a
separate cost.

The retained equal-block result explicitly excludes unequal port dimensions.
This extension handles skewed, odd-total and zero-size payloads without an
optimization solver. For example `(100,1,1,1,1)` needs 101 query coordinates,
although the rounded half-total is only 52; five unit payloads need three,
although every nonneighbor pair has size two.

The actual PR2484 core `[13,23,35,16,34]` and its separated 22 planes give an
exact **54-port principal-mask** formula: add the 44 separated port dimensions
to the five-cycle optimum, combining the two widths within each core plane.
The source-bound seed-40 example has core widths `(5,8,8,5,4)` and separated
dimension 101: its 131-by-131 principal matrix has rank 116. Uniform port width
d recovers the predecessor's 49d obstruction. This is a lower bound for the
complete unequal-width 112-port mask, not an assertion of full-mask attainment.

## Reproduce

Base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`; standard-library Python 3.12.
Exact source blobs and SHA256 values are in [SOURCES.json](SOURCES.json).

```sh
python3.12 -B scripts/research_package.py --package research/unequal-cycle-payloads
```

Expected: `PASS_UNEQUAL_CYCLE_PRIMARY`, `PASS_UNEQUAL_CYCLE_INDEPENDENT`,
`PASS_UNEQUAL_CYCLE_CONTROLS` and a successful package replay.
The individual Git-free command is
`python3 -I -B research/unequal-cycle-payloads/verify.py --suite primary`;
use `independent` and `controls` for the other suites. Keep the three declared
source inputs at their relative paths. Replays compare complete canonical typed
receipts without modifying files.

Primary checks cover all 1,024 vectors in `{0,1,2,3}^5`, with exact ranks over
GF(2), GF(3) and GF(101), plus 80 seed-40 512-bit recipes and a 10,001-bit case.
An independent implementation enumerates all integer edge-capacity solutions
on those vectors and **17,859 arbitrary directed binary fitting matrices**:
all 32 dimension patterns in `{0,1}^5`, plus `(2,1,1,1,1)`.
It reconstructs source orthogonality from explicit nine-component vectors.
These finite checks corroborate the written proof; they are not its replacement
or a formal verification of the multiplication theorem.

Controls reject incomplete formulas, invalid dimensions, undercharged channels,
wrong geometry and corrupted inputs. A forbidden block with zero trace that
kills the all-ones vector demonstrates why full ordered zero blocks are required.
[RESULT.json](RESULT.json) records all coverage; [VALIDATION.md](VALIDATION.md)
records publication checks.

## Scope

This counts linear query-vector capacity. It does not price native copies,
source access, frame changes, dirty restoration, recursive children or precision.
No supplier, selected frontier or κ changes. It applies to the pinned old matching;
PR3335's different matching and the concurrent equal-width/native-tariff checks
answer different questions and are not dependencies.

## Open next questions

- **Full unequal 112-port mask:** choose a nonuniform width vector and try to
  attain this principal lower bound. Remaining ports may force a larger rank;
  a complete construction or stronger bound is the next obligation.
- **Physical realization:** specify source/target charts and price all copies,
  helpers, frame changes and restoration for one recipe. A query dimension
  saving alone cannot establish a supplier improvement.

Assignment seed 40, structural decoder research. Candidate selection and stopping
rule are in [TASK.json](TASK.json). Credit thakrarsagar/PR2484, ywz65/PR2471,
the retained `paired-plane-block-rank` proof, the classical block-fitting and
[fractional Haemers framework](https://arxiv.org/html/1802.00476v2),
Cinna Davis/PR1825, Adam Gall/PR1889, ctoth, Philippe Van Velzen and the selected
E8/P112 lineage. Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
