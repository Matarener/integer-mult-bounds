# Delayed-cover batches in the recursive allocator

A fresh delayed-cover row has W=L*H values, but a child which batches all H high
matrices has **volume V/L**, not V/W. This package gives an explicit invertible
address map for the final compiled template at every recursion depth. It keeps
all ancestor high matrices, unused fresh stock, body fields and return addresses.
It binds that map to the remaining variable-cover edge in PR5814.

The active-chain bound is `K*V*L/(L-1) <= 2*K*V` under the stated local macro
space premise. The full W^D reserve is still required; high-matrix batching does
not remove its digits. Private banks add local space and receive no productive
credit. The child weight can read ancestor high values while staying independent
of every fresh child role and cover value. See [PROOF.md](PROOF.md).

The cover, fresh-cylinder theorem, fixed-PR589 packet implementations and local
allocator are credited predecessors. The new result is their explicit
source-bound batch/fresh-stock interface and its all-depth volume/return proof.
This is a reference address model, not a physical dispatcher or a new cover.
It does not discharge local old-interchange, routing, fallback, numeric or
private-erasure implementations. No new kappa or frontier change is claimed.

Run `python3 -B scripts/research_package.py --package research/delayed-cover-batch-allocation`.
The standalone command is `python3 -B research/delayed-cover-batch-allocation/verify.py`.
Python3.12 and the standard library suffice. Eight complete finite domains are
checked against a separate coordinate-product oracle, including literal nested
return. The GL2 local-ring control covers all7,776 two-role rows. Seven invalid
claims are rejected. Exact counts and hashes are in `RESULT.json`.

## Open next questions

- Bind the old ordinary BIT local macros and their retained backing to the K*V
  space premise. The time bound alone does not prove this space bound.
- Implement the final compiled template's fixed-port dispatcher and generated
  ancestor-weight evaluator using these complete batch addresses. Charge all
  staging, route, fallback, marker and descriptor work.
- Bind actual child numerical precision and exact private return to that
  implementation, then review the full assumption boundary.

Sources: PR5814 head68614094a31bd483083cfaf1f8735ceb6aec5224;
main de5ec2e7a6074068452f45b1a191b5c72832df4a. Exact pins are in `SOURCES.json`.
Credit Mason Hale, Nick Petalas, Jose Manuel/jmbarrancoml, Cinna Davis, David
Arias, zxv and all retained BIT/compiler/cover authors. Ali Romman with
substantial OpenAI Codex assistance in proof, code and checks; no subagents.
Apache-2.0. No independent scientific acceptance is claimed.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
