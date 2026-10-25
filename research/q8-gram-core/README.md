# A call Gram normal form for formal Q8 words

Every normalized binary rank-one paid word has a simultaneous scalar core
of dimension `rank(YX)`. Its call Gram matrix YX and ordered labels classify
that reduced sequence up to scalar GL basis change. The [proof](PROOF.md)
preserves all active diagonal targets and restored arbitrary dirty inputs.
An exact identity fixture reduces from two roles under either separate
PR3487 reduction to one under the simultaneous reduction.

The second result is a necessary-and-sufficient binary matrix criterion
for any exact-length all-negative positive-Q8 endpoint. It replaces an
unbounded dirty-workspace choice with a call-indexed Gram matrix.
[gram.py](gram.py) checks a candidate. [system.py](system.py) exports an
exact SMT-LIB system with variable ordered labels and all eight Q8
coefficients. The seven-call three-negative cases remain unsolved.
Two short solver probes timed out; neither is an exclusion.

This is a partial mathematical result on the formal nonabelian register
model, answering the invariant part of [PR3487's released handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3487).
It does not change the paid operation alphabet or establish a physical
supplier. The selected frontier is unchanged.

## Reproduce

Use Python 3.12, standard library only. From the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/q8-gram-core
```

From a Git-free package export, run these exact commands, substituting its
package directory for PACKAGE. No repository, network, compiler or solver
is needed for these checks.

```sh
python3.12 -I -Werror -X pycache_prefix=PRIVATE_EMPTY_CACHE PACKAGE/verify.py
python3.12 -I -Werror -X pycache_prefix=PRIVATE_EMPTY_CACHE PACKAGE/test_package.py
```

The scripts explicitly add their own source directory under isolated mode.
PRIVATE_EMPTY_CACHE is a fresh external cache path. The replay compares a
source-bound receipt, the full Hamilton regular action, every binary Gram
candidate through three calls, and the independent binary-eigenspace
criterion. [RESULT.json](RESULT.json) gives exact finite coverage and
export identities. [VALIDATION.md](VALIDATION.md) describes controls and
limits. These checks support the uniform written proof; they do not prove
the seven-call systems unsatisfiable.

To export one exact-length decision system to a fresh output path:

```sh
python3.12 -I -Werror -X pycache_prefix=PRIVATE_EMPTY_CACHE PACKAGE/system.py \
  --calls 7 --i-targets 3 --j-targets 0 --output seven-3-0.smt2
python3.12 -I -Werror -X pycache_prefix=PRIVATE_EMPTY_CACHE PACKAGE/system.py \
  --calls 7 --i-targets 2 --j-targets 1 --output seven-2-1.smt2
```

Each system is existential over every ordered i/j label list. A solver
answer is separate evidence. Any proposed satisfying model must be
reconstructed with normal_form and checked in the full formal algebra.
The same commands with `--calls 3` or `--calls 5` describe those exact
lengths. No padding argument joins the lengths. Existing output paths
are refused.

## Sources and scope

Nick Petalas, Apache-2.0. Credit Tuafo/PR2900, ywz65/PR2587 and PR3487 for
the image, coefficient-support, Sylvester and common-kernel reductions.
The quotient and rank-factorization facts are standard linear algebra.
The ordered-call application and exact Q8 criterion are the additions.
The retained predecessor proof and full source identities are in
[inputs/RETENTION.json](inputs/RETENTION.json). Its exact pending-head bytes
are committed here; no foreign Git ancestor is assumed. Its finite native
census is not a runtime or mathematical dependency of this self-contained
normal-form proof. PR3471/3499 retain their finite minima and tariffs.

Every role is dirty, every paid projector has binary rank one and is
idempotent, and only binary scalar GL mixing is free. No clean allocation,
erasure or free address map is introduced. The written core theorem is
uniform over finite dimensions; the executable verifier caps roles and
calls at sixteen. Independent human and formal proof-kernel review are
unclaimed. Physical implementation, full caller/consumer bill, supplier,
new kappa and the general three-negative minimum remain unclaimed.

## Open next questions

- Solve or certify the `(3,0)` and `(2,1)` systems at lengths 3,5,7. Start
  with one declared solver and retain a checkable unsatisfiability proof
  or independently verified witness. Timeouts do not settle these systems.
- Find a sign-sensitive invariant of the two nilpotent blocks in the
  seven-call five-role core. It could close the workspace gap without
  enlarging the native census. The current character fixes their size,
  but does not constrain the full central coefficients enough.
- Bind a completed formal saving, if found, to an actual paid caller and
  physical invoice. The normal form does not remove those implementation
  obligations or justify another construction round by itself.
