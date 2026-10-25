# Complete binary refinement of the fixed CRT repair caller

This answers PR5105's first Open next question: lower its **complete**
finite-symbol program to a literal bit-operation program, including stencil
products, role registers, split/key, sorting, reinsertion and disposal.
It reuses PR4982's unchanged bit executor. PR4982's key and PR5015's isolated
radix algorithm are not rebuilt or claimed again.

The written [proof](PROOF.md) establishes source-step simulation for the
actual admitted u2/t2/y8 caller, arbitrary opaque 12-bit payload labels and
its admitted 32-bit ROM. A four-round static closure finds 4,932 canonical
values, all encodable in 13 bits. The complete 8,242-instruction source
compiles to 557,123 bit instructions using 31 tape roles and 14,839 finite
control bits. For T source instructions, its complete invocation bound is

    binary actions <= 101391 T + 29679.

Every runtime tape operand is a literal role selected by bit tests, and
every data access is one-bit read/write or unit bit-head movement. Stencil
field projection and role products are compiled finite decision chains.
The conservative constant includes the largest overapproximated aggregate
block; this is no speedup or new kappa claim. Input/ROM serialization,
raw-S production and variable geometry remain external.

The verifier uses the original PR5105 executor as its independent reference
for 63 instruction/alias/dispatch cases, checks all 4,096 payload encodings,
and detects wrong-role, short-stride and retained-control faults. It executes
2,862 actual producer boundaries and 43,130 complete key-cut boundaries on
persistent encoded tape objects. The key cut comes from the actual source
producer/scanner/split state and reaches its real continuation. Its entry
is encoded once; the scanner is not binary-replayed.

**The full binary layer is not executed.** Its correctness follows
conditionally from the complete source theorem and the written per-step
proof, not from claiming that the bounded cuts cover 2,944 keys or all
sorting passes. Source and proof review are AI-assisted, not independent
human or formal-kernel acceptance. Selected PR5413 and frozen sources stay
unchanged.

## Reproduce

Python 3.12, standard library only, a few seconds locally:

```sh
python3.12 -B scripts/research_package.py --package research/crt-complete-binary-refinement
python3.12 -O -B research/crt-complete-binary-refinement/verify.py
```

All declared live sources authenticate before assembly. Normal replay
compares the typed frozen receipt; only `--write-result` authors it.
Direct replay works in the official Git-free export. Compilation is fixed
source preprocessing; no input payload or ROM is an assembler argument.
The private blank backing and valid encoded entry contract are inherited;
this does not provide arbitrary-dirty-storage allocation or malformed-input
rollback.

## Open next questions

1. Budget a complete binary-layer replay using the source instruction census
   before spending billions of literal steps. This would corroborate the
   proof with a whole endpoint; it is not a prerequisite disguised as a
   passing partial replay here.
2. Bind encoded ROM/descriptor construction and raw-S production to this
   exact representation and ownership contract. Those missing producers,
   variable geometry and the full E(p,ell) bill block a uniform CRT claim.

Exact pins and structured questions are in SOURCES.json and TASK.json.
Canonical claim: [Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19172880).
Fresh entry overlap covered 342 open PRs and 4,736 discussion records.
Unpublished work and arbitrary diffs are outside that coverage.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retain PR5105/PR4982/PR5015 and the credited Cinna Davis, Hiroki KUMAZAKI,
ToikY, Jose Manuel, Ryanson Jonathan, unpaidmoon, codyw912, Douglas Colkitt
and underlying CRT/repair notices. Source retention is not scientific
acceptance.
