# Conditional κ = 0.00272124 from fresh-helper boundary retiming

This changes the complete native p7 paid profile and proposes

```
T(n) = O(n (log n)^(1 - 0.00272124)).
```

The conditional saving exceeds [PR4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416)'s
`0.00268647` by **0.00003477 (about 1.2943%)**, and the pinned selected
`0.0023` by **18.31%**. This is a conditional construction submitted for review;
it does not change the selected record or establish an unconditional theorem.

The new lever is to optimize helper entrances and exits for **fresh independent
helper inputs**, rather than retain frames selected for a hosted owner fill.
Changing those boundaries together with scalar contact frames saves recursive
calls without changing the scalar order, coefficients, main operator, warp
contacts or owned center program. The exact finite patch changes **117 helper
entrances, 42 helper exits and 395 scalar contact frames**.

| Complete raw p7 invoice | PR4416 | This construction |
| --- | ---: | ---: |
| Independent productive fields | 7,688 | 7,688 |
| Paid calls | 55,998 | **53,133** |
| Productive rank mass | 131,723 | 133,718 |
| Paid rank mass | 131,115 | 133,110 |
| Rank-one surplus | 608 | 608 |
| Proposed conditional κ | 0.00268647 | **0.00272124** |

The call reduction is **2,865 (about 5.12%)**. These are finite instruction
counts, not measured runtime speedups. The changed masses illustrate why
counting calls or rank-one mass alone does not establish the saving: the exact
concave moment and complete consumer are checked separately.

## Native unit and exact evidence

For each forward or backward local invocation, the new productive helper
profile and complete paid profile are

```
H = {4:26, 5:2, 7:29, 8:42, 9:309},
P = {1:2253, 2:515, 3:445, 4:102, 5:40, 8:8}.
```

Every one of the 408 helpers has an independent arbitrary input. The center
remains separately owned, explicitly cleared, reused and uncredited. The
source p7 controller is unchanged: `pairs=7, keep_idle_mask=232127`. Its full
rational Laurent word is replayed; all 2,688 main idle calls are retained.
The complete new raw profiles are

```
T = {4:390, 5:30, 7:435, 8:630, 9:4635,
     25:448, 41:448, 57:448, 121:224},
P = {1:33795, 2:7725, 3:6675, 4:1530, 5:600,
     8:1464, 16:448, 32:448, 48:448}.
```

[PROOF.md](PROOF.md) proves the retiming equivalence and explains the complete
transfer. [CHANGES.json](CHANGES.json) is the explicit circuit patch;
`native.py` resynthesizes every transport and replays both orientations on all
632 arbitrary inputs using two retained literal interpreters. All new transport
edges and every distinct helper boundary are independently lowered and decoded
as exact Clifford operations, including their absolute phase. Unchanged
transport phase evidence and the original all-column/native model remain
inherited source premises.

`arithmetic.py` uses the unchanged interval engine of
[PR4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433). It certifies

```
0.0027212601275 < fixed-profile mixed root < 0.0027212601276.
```

An interval argument covers all real `0<C<1` and establishes this root as a
ceiling for this **fixed profile** with chronological products, paid target
completion and paid splitting. The declared κ leaves between `2.01275e-8` and
`2.01276e-8` headroom. A further gain needs another profile or interface; more
digits of this root are not another construction.

## Uniform supplier and complete consumer

At tested saving `0.00272125`, take tensor power 150, paid cutoff `10^150`
and completed minimum target `15^150`. PR4433's higher-moment paid-tail theorem
charges the original paid jobs and every added completion. The source integer
compiler and logarithmic majorant specify sufficient uniform rank

```
N = 2^349300000000.
```

The enormous tensor and uniform words are finite algorithmic prescriptions;
their instruction lists have not been materialized.

The old conservative BIT admission `0.0027` would cap this improvement. The
**unchanged** source BIT conversion already gives `0.0027418653797` before its
final relaxation. Admit it here at `0.00273`, retaining the same supplier,
cover, atom exponent `0.003`, stock bounds and adapter checks. All nine outer
cost rows, all 54 current predicates and three additional functional guards
are recomputed at the new κ. Controls reject retaining the insufficient old
BIT relaxation, closing the uniform or epsilon gap, omitting a paid center,
and corrupting only a compiled operation's global phase.

## Reproduce and inspect

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/fresh-helper-boundary --check-only
python3.12 -B scripts/research_package.py --package research/fresh-helper-boundary
```

Direct replay: `python3.12 -B research/fresh-helper-boundary/verify.py`.
Optional optimizer replay (C++20 compiler needed) is
`python3.12 -B research/fresh-helper-boundary/discover.py --output /tmp/new-discovery-directory`.
It writes a new patch and logs without replacing the submitted circuit.

Ordinary replay does not write; `--write-receipts` is an explicit authoring
option. `NATIVE-RESULT.json.gz`, `ARITHMETIC-RESULT.json` and `RESULT.json` contain
checked receipts. [VALIDATION.md](VALIDATION.md) records what was actually run.
[ATTEMPTS.md](ATTEMPTS.md) states the bounded discovery searches and their
limits. [FRONTIER-CHECKS.json](FRONTIER-CHECKS.json) records the requested
20-minute PR checks during this session.

Sources are pinned to canonical main
`3a23e9d9d2e67833515d1c60a17e966bcdcab43c`. The source files remain unchanged.
The exact card is retained as provenance; the user assigned a κ improvement,
so TASK.json explicitly changes its historical #4088 admission scope.

## Scope and credit

The source analytic decomposition, physical primitives and legal whole-job
normalizers, original all-column native semantics, finite-template closure,
fixed-tape model, fine-prime padding and exact recovery remain conditional
premises. Finite replay does not formally verify the full multiplication
proof. No practical implementation, global optimum, selected-frontier update
or independent human review is claimed.

Native supplier, p7 controller and higher-moment strictification: **zxv**.
Paid padding and p7 native predecessor: **1337isnot1337**, PR4416.
Mixed integer flow: **Jacob Alan Sussman**, Theorem 1G / PR4268.
Literal interpreter lineage: **Sagar Thakrar**, the retained frame-bill and
native-source contributors, and the PR4359 reconstruction. Exact Clifford
compiler and predecessor author notices remain in the pinned sources.
The outer parameter refill retains PR4405's source attribution. New boundary
retiming, resynthesis, exact arithmetic and integration were prepared for
**1337isnot1337 with substantial OpenAI Codex assistance**, Apache-2.0.
No subagents were used.

## Open next questions

The structured questions are in TASK.json. Further work could optimize two
different frame labels jointly, change scalar order or native geometry, or
reduce the finite compiler constants. The fixed-profile ceiling prevents
claiming another κ by merely retuning this same invoice. Independent review of
the retiming lemma, native source bindings and complete transfer is welcome.
