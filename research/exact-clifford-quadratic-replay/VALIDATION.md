# Verification record

Host: macOS arm64, CPython 3.12.14, standard library only. Canonical base:
`df0137efd35e11b4445734bf612bdd4c7ebc330c`. Priority revision 7 and selected
conditional kappa .00310045 are unchanged. No subagents were used.

The current selected-baseline command passed its source-binding check. The
historical generic baseline command has an incompatible selected-certificate
schema; that failure is not treated as a mathematical defect. The current task
picker resolves it to scripts/research_selected_baseline.py.

The original complete replay was profiled before implementation. Native recipe
decoding was the main measured hot path. The new engine changes the state
representation instead of repeating PR662's existing gate-table cache.

The following registered check passed on the final implementation:

```sh
python3.12 -B scripts/research_package.py --package research/exact-clifford-quadratic-replay
```

It runs four commands: full new verification in normal and optimized Python,
and the all-actual-state literal cross-check in both modes. Warning-strict and
isolated flags are set. Every command compares its complete deterministic
receipt. New checks use explicit exceptions rather than removable assertions.

The engine suite checks 7322 states, 618544 amplitudes, 2728 affine assignments,
18724 twice-product assignments, 6096 phase substitutions and 160 exact inverses.
It exercises independent-root, odd-elimination and even-restriction updates.
Every basis input is covered through width 4; widths 5 through9 use a specified
small set per circuit prefix. The corpus is deterministic, not an exhaustive
Clifford-group enumeration. The all-width statement is supplied by the proof.
Large full-support examples at widths 16, 32, 64 pass exact inverse insertion,
whole-circuit inversion and absolute-phase rejection without vector expansion.

The separate actual-state pass checks 8634 evaluations and 4420608 vector entries,
including one deliberately wrong global-phase recipe. It compares exact
Gaussian numerators and dyadic denominators, then the whole source RESULT.
The output is CROSS.json. No sampled amplitude or pass-marker-only comparison
replaces those checks.

Thirteen malformed circuits reject. The semantic controls include a wrong
absolute phase with an unchanged tableau, a changed input Z with an unchanged
zero column, and explicit amplitude witnesses for wrong phase, denominator and
support certificates. Two source-proof omission controls reject a missing
grade check and a missing tail transfer. A positive unmodified syntax binding
is checked first. The complete source's eleven controls also remain in every
full replay.

An actual byte appended to the frozen Clifford module is rejected before
source import. The original bytes were restored. All 35 frozen inputs are
checked by INPUTS.json. Frozen carriage returns and source notices are preserved.

BENCHMARK.json records three alternating fresh-process rounds for each of the
literal, table and quadratic engines. Every scientific stdout hash is
`af07db48cceab79f0ffecaa1fe5f91b8806ba9bd2c78ebbb4b5d4a15fd407a46`.
Every complete canonical scientific-result hash is
`a501b899b5f70e7cde6a10af4e4c2530cf9f4cb6ba53504828bf855ed3b74093`.
The medians are 57.623512584, 17.591124834 and 11.149205750 seconds. The corresponding
speedups are 5.168396196 and 1.577791748. The ranges and machine details remain in
the receipt. These are local wall times with variable host load, fresh Python
processes and warm operating-system caches. No portable speed threshold is an
acceptance condition. A complete mathematical result match is mandatory.

Exact committed-byte, official export and sealed Git-free checks are separate
publication gates. Their final outcomes are recorded in the PR and canonical
Discussion. Full-history ancestry preflight is unavailable in this shallow
checkout. Hosted CI, independent human review, proof-kernel acceptance, the
selected cold replay and a rounded physical multiplier were not established
by this package. Existing source framework assumptions remain.
