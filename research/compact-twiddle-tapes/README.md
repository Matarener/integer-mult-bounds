# Compact binary programs for synthetic twiddle tapes

A supplied binary-index AND/XOR program can produce the exact synthetic twiddle header on five fixed tape roles, preserve borrowed program/address bytes and heads, and return both private tapes blank. [PROOF.md](PROOF.md) proves the claim for every finite topological circuit and derives an exact primitive and storage invoice. The executable caps its admitted domain at 4,096 wires and 200,000 program symbols.

The changed contract replaces PR3534's supplied unary operands with binary operands and a private counter tape. A normalized binary decrement detects zero while shortening its top marker, so no full-width zero scan is needed at each step. Under the canonical circuit's source bands, this combines O(p²) read/write/unit-move primitives per header with O(p log(p+2)) charged storage. This removes the logarithmic time factor from PR3522's written compact-program scan simulation. Program, address, output, markers, spare blanks and both private tapes are charged. Encoding, host admission/allocation/instrumentation and final observation are outside that primitive invoice. This is a sequential tape model, not integration into the production tape library.

For B=A+G+2, H=ceil(log2 B), supplied program length L, c_j=A+2+j and h(w)=max(1,bit_length(w)), put

```text
F(w) = 8h(w)+27+17w-5popcount(w)
T = 8A+2Q+5B+2L+31
    +sum_j[4c_j+9+F(a_j)+F(b_j)] +sum_t[4+F(w_t)]
C = L+A+B+Q+H+10
```

[RESULT.json](RESULT.json) records 1,412 synthetic headers across 52 programs, including complete address domains through seven bits and wider headers through ell=48. A separate integer exponent oracle and independent invoice agree on every run. Another 365 generic/borrow-chain cases cover 53 programs. Direct access checks cover every index from 0 through 1,023, including every borrow/marker-shortening boundary in that domain. Fourteen invalid input/resource cases reject. The largest fixture executes 4,180,246 primitives and occupies 8,300 cells, including a 7,608-symbol program. For that same canonical topology, the retained unary formula gives 211,847 program cells and 212,526 total cells. This combines the unary interpreter's O(p²) time bound with compact program storage. It is not a strict primitive/cell improvement for every small circuit or a timing benchmark. [COMPARISONS.json](COMPARISONS.json) preserves the exact baseline origin, bytes and calculation separately from actual proof/runtime inputs.

Eight actual optimized CLI fault groups test arithmetic, move counting, binary decrement, private erasure, program-head return, changed source, missing source and the scientific receipt. A valid optimized retry must succeed. [ENGINEERING.md](ENGINEERING.md) states the model, resource bounds and Python deviations. The all-finite-program conclusion follows from the written proof, not extrapolation from finite tests. Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, with CPython 3.12 and an existing private external temporary directory:

```sh
python3.12 -I -Werror -B research/compact-twiddle-tapes/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/compact-twiddle-tapes/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/compact-twiddle-tapes
python3 -B scripts/check_research_commit.py --package research/compact-twiddle-tapes --check-source-history
python3 -B scripts/export_research_package.py export --package research/compact-twiddle-tapes --output /absolute/private/run/package.tar
python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar
```

The exported files run verify.py and test_controls.py directly outside Git. [SOURCES.json](SOURCES.json) pins the canonical circuit runtime, its actual mathematical proof premise and the retained transform source. All three are authenticated before loading the circuit. The selected record and original card are historical provenance. No foreign pending Git object or network is needed for scientific replay. The bounded hook is not a complete selected cold replay, Lean proof or supplier admission.

## Open next questions

The borrowed program and physical address are still supplied. Implement encoded shape/topology and address production, then connect one mixed long/short header to the actual signed packet and normalized layer. Record every descriptor/address/header movement, spectator, buffer and head return. This would close the control/data caller boundary; the present separate routines do not settle it. Production native/root/ordinary/hosting and outer recovery remain blockers. [TASK.json](TASK.json) records this one next question and its first step.

No new supplier, kappa or selected-frontier change is claimed.

## Credit

Nick Petalas's canonical PR3522 circuit and its proof are actual dependencies. His pending PR3534 unary interpreter is the separately retained comparison. Credit Philipp/mightyOil's positional engine, Jose Manuel/jmbarrancoml's transform and signed-packing work, Douglas Colkitt, and the frozen Nussbaumer/Quandalle and Harvey/van der Hoeven source lineage. Frozen source notices remain unchanged. New package code and proof are by Nick Petalas under Apache-2.0.
