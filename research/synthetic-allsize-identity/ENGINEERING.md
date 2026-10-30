# Verification contract and limits

Build the Lever led to `verify.py`, which authenticates canonical source bytes,
checks the coefficient-path congruence and executes the retained indexed
engine over exact integer module columns. Prove It Works led to real optimized
CLI success and corrupted-source/receipt rejection in `test_controls.py`.
Separate Before Serializing Shared State led to a private worker branch/output
directory and process-held locks for the shared Git metadata and task reservation.

The written proof is the evidence for universal quantifiers. The finite receipt
checks 349,524 input/output path pairs, 1,980 layouts, 13,020 chunk rounds,
450 ring-module columns over 29 shapes, and base change to Z/2, Z/4, Z/9 and
Z/15. Integer equality is stronger than equality after any one base change.
The odd composite rings additionally check normalized composition with an
actual modular inverse of M. The characteristic-two fixture is nonzero with
zero opposite composite; normalization is deliberately unavailable there.
Another 116 fixtures check the explicit first-round kernel in the proof of
the sharp invertibility boundary over Z/2, Z/4, Z/6 and Z/10.

The retained engine and its original notices are unchanged. Its direct calls
use only valid plans returned by its own bounded fixture inputs. It supplies
indexed algebra, not a fixed-tape realization. The new character oracle does
not import its layout, movement, butterfly, or monomial implementations.

All new functions are below 60 physical lines. Loops have fixed finite outer
domains. Path pairs have at most nine axis bits and r<=2048. Layouts have at
most 48 named bits, represented as lists, without allocating 2^48 records.
Matrix fixtures enforce at most five address bits and ell<=4, so each matrix
column has at most 32*16 integer entries. CLI subprocesses have a 120-second
timeout. Test copies and temporary directories close on every exit. Explicit
`need` checks remain active under `-O`.

Power of Ten deviations apply only within this isolated verifier:

- Rule 3, fixed memory. Python and the retained engine allocate managed
  integers/lists while computing. The fixed ranges above bound live payloads;
  receipt hashing is incremental. Runtime allocator internals are uninspected.
  A fixed-buffer port would be needed for a fixed-capacity runtime requirement.
- Rules 8 and 9, runtime import. `importlib` loads exactly one authenticated,
  canonical engine path. Its targets are `plan` and `execute`; every return is
  checked against separate algebra or a stated mutation predicate. The CLI
  source-corruption test verifies rejection before that import. Static linking
  is a possible follow-up if the repository supplies a stable module namespace.
- Rule 10, diagnostics. Scoped Ruff E4/E7/E9/F and warnings-as-errors scientific
  execution are the local diagnostics. There is no project-wide static type
  migration. The opt-in manifest registers both scientific and CLI checks.

The exact proof does not cover Q_p between rounds, production native/refinement,
borrowed tape restoration, runtime or storage invoices, the Gaussian maps,
outer recovery, or a complete multiplication theorem. No Lean, Docker, full
selected replay or production supplier execution is part of this validation.
Independent human and formal proof-kernel review are unclaimed.
