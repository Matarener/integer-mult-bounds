# A uniform seven-call lower bound for three negative Q8 targets

Three targets in `{zi,zj}` need at least seven positive i/j calls in the full
formal F2[Q8] model, with binary rank-one idempotents and any finite restored
dirty workspace. The direct construction takes nine calls. The exact minimum
is therefore seven or nine; this package does not decide between them.

This closes the exact-length-three/five questions left by
[PR3517](https://github.com/CrocSwap/integer-mult-bounds/pull/3517).
Its scalar-core theorem reduces arbitrary workspace to a finite call-indexed
test. Two separately implemented complete censuses reject all candidates at
those lengths, comparing every formal coefficient. The seven-call case stays
open. The selected frontier and kappa are unchanged.

## Result and evidence

[PROOF.md](PROOF.md) gives the uniform workspace reduction, complete coverage
argument and scope. [RESULT.json](RESULT.json) binds the census and controls
to the exact scientific source bytes. [VALIDATION.md](VALIDATION.md) records
the implementation checks and limits.

The primary census covers all 64 diagonal-one Gram matrices at three calls
and all 1,048,576 at five calls, without word-order or basis symmetry pruning.
The first-order equations leave 4 candidates at three calls and 16,340 at
five. None has the required negative endpoint. The independent census uses
dot products, explicit row spans and faithful Hamilton permutations, and
tries every label list without the primary label pruning. Complete counts
and endpoint streams agree.

The replay also compares all 530 Gram/label words through three calls at
5,222 target-rank valuations. All eight direct nine-call target lists pass,
all 72 one-call deletions fail, and 320 faithful input columns include two
arbitrary independent dirty spectators. Three optimized behavioral test
groups reject actual action, multiplication, enumeration and endpoint faults,
invalid input, a corrupted receipt and output-file collisions.

This is a computer-assisted scoped lower bound, with a written all-workspace
reduction. Independent human and formal proof-kernel review are unclaimed.
No physical Q8 caller, completed supplier invoice or multiplication theorem
is supplied. A lower bound in this formal model is not a new kappa.

## Reproduce

Python 3.12, standard library only. Run from the repository root, with TMPDIR
set to an owned external directory:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-short-negative-gram
python3.12 -B scripts/check_research_commit.py --package research/q8-short-negative-gram --check-source-history
```

After exporting committed package bytes, these scientific commands need no
Git, network, solver, compiler or predecessor checkout:

```sh
python3.12 -I -Werror -B research/q8-short-negative-gram/verify.py
python3.12 -I -O -Werror -B research/q8-short-negative-gram/test_package.py
```

Both entrypoints explicitly import their own package directory. Use a fresh
private `-X pycache_prefix=...` when running amid existing Python caches. The
registered runner supplies its own fresh cache namespace. `verify.py --output
PATH` creates a new receipt and refuses to overwrite an existing file.

## Sources and credit

Canonical baseline is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. SOURCES.json pins the canonical task catalogue and selected record
as provenance. The exact pending PR3517 proof premise is retained unchanged
at `inputs/pr3517-PROOF.md`; RETENTION.json gives its original commit, path,
Git blob and SHA256. Replay does not fetch that commit. No pending foreign
head is represented as canonical ancestry. COMPARISONS.json separates nearby
context and credit sources from the used PR3517 proof premise.

Nick Petalas's PR3517 retains the scalar core and exact Gram criterion;
PR3471 retains the finite three-role negative-triple minimum, PR3487 the
workspace reductions, and PR3499 the scoped weighted tariffs. Credit Tuafo,
ywz65, Aaron Wang, Cinna Davis, steph4n-gh and the register-model lineage as
recorded in the retained proof. Arham Tahir's PR3137 physical compiler and
PR3461 scalar preparation have separate costs. This package adds only the
complete short-length exclusions and their uniform lower-bound consequence.

## Open next questions

- Decide the exact seven-call systems for shapes `(3,0)` and `(2,1)` with
  a checkable witness or complete certificate. PR3517 provides the starting
  criterion; the remaining two essential dirty blocks and the large search
  space are the blockers. A checked nine-call minimum or cheaper seven-call
  word would resolve the current formal gap.
- Bind an actual Q8 caller to the physical action, scalar preparation,
  chronology, restoration and complete invoice. This matters because formal
  calls alone do not establish a supplier saving. No such caller is supplied.

TASK.json gives the structured scope, stop rule and remaining obligations.
