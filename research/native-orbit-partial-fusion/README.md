# Variable-volume orbitwise partial fusion

For the selected target195/donor521 boundary, allow a partition into coordinate
orbit blocks of unequal volumes and choose independently how many of the second
child's tensor directions to move into the first child. The native ranks become
`f+k, f-k` on each block. The exact required transfer is `B_K y/2`.

**Result:** this entire family fails the uniform optimistic cost screen, even
with arbitrary feedback and any number of restored dirty helpers inside each
block. If `W = sum(block_volume * k)`, additional arithmetic is at least `W`,
while the available recursive saving is at most `A delta f^(-alpha) W`, where
`delta = 2-2^(1-alpha)`, `0<alpha<1`, and fixed `A` uses the same arithmetic
units. This applies even when the partition and every `k` depend on `f`.

The proof in [PROOF.md](PROOF.md) combines Clifford tensor orbit structure,
combinatorial support growth and a convex chord inequality. It extends the
full-fusion endpoint considered by PR3989/PR4009 to every partial cut and their
heterogeneous block combinations. It is a scoped obstruction, not a universal
lower bound for sparse programs or actual optimal native runtimes. No new
kappa or selected-frontier change is claimed.

## Exact scope

Each block is a union of full joint Pauli orbits. The first and last native
calls act only on the target with ranks `f+k` and `f-k`. Between them, the
adapter may use arbitrary monomial-source shears, mixtures and restored dirt,
but every shear processes the whole block. There are no intervening native
calls, cross-block mixing, masked sub-block operations or data-dependent
partitions. Native hosting, routing and precision are optimistically granted
free for the screen; no physical supplier is admitted.

The lower bound uses a legal input with target and dirt zero, donor a coordinate
basis vector. The required adapter output has `2^k+1` nonzeros in total. At
least `k+1` shears are necessary because one shear at most doubles total support.
The original adapter uses one ADD. Convexity then bounds the recursive saving
per additional processed coordinate uniformly across the partition.

## Evidence and reproduction

```sh
python3.12 scripts/research_package.py --package research/native-orbit-partial-fusion
python3 -B research/native-orbit-partial-fusion/verify.py
```

The standard-library verifier authenticates the canonical selected archive and
reconstructs 1,536 literal child columns, all128 joint coordinate orbits and the
full intervening dependency region. It checks 3,184 complete reduced two-payload
basis cases for every `k` at `f=1,2,3,4`, plus96 heterogeneous-block basis cases,
the exact direct monomial expansion, and four rejected construction mutations.
Integer support checks and8,384 high-precision convexity checks are controls;
the written argument establishes the quantified all-f theorem. This is not
exhaustive enumeration of the literal `512^f` payload for f>1, a formal-kernel
proof, or a complete multiplication theorem.

## Overlap and expansion decision

Canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision6.
Parent entry checked all733 open PR bodies including drafts at10:46UTC on
2026-10-19, plus current handoffs and active discussion claims; later checkpoint
through PR4033 at11:05UTC found no same scoped result. Wider discussion/closed
coverage is partial. Directly read #3975, #3989, #4009, #4023 and #4027.
PR4023 concerns a fixed-carrier query bound with swap-algebra bridges; PR4027
changes a different H6 factor. Neither is this selected partial-fusion invoice.
The cached local helper was also attempted; no novelty claim rests on it.

The result rules out expanding this particular orbitwise model. Granting
smaller coordinate masks or cross-block interaction would change the proof's
premise and requires a new invoice before implementation growth.

## Open next questions

Can masked operations within one orbit, cross-block mixing, or overlapping
native supports achieve the same restored boundary with a smaller total
processed volume? First specify one exact operation and charge source access,
all native operands, phase/basis conversion, precision and dirty restoration.
The present argument deliberately does not bound that model. Structured scope,
stop rule and next question are retained in [TASK.json](TASK.json).

## Credit

Gonzalo Mier / PR3975 supplied the selected sequential caller. Clear1nsight's
PR3989 and PR4009 provide the phased Pauli boundary and earlier feedback
analysis; `exact.py` retains their adapted Gaussian/recipe decoder. Credit
Cinna Davis / PR1836, Adam Gall's heterogeneous interface audit, Arham Tahir /
PR1920, ToikY / PR1924, and the selected PR1094/PR679 source lineage.

Prepared by Clear1nsight with substantial OpenAI Codex assistance. A separate
Codex agent reviewed the conceptual proof; this is not independent human or
formal-kernel acceptance. Apache-2.0.
