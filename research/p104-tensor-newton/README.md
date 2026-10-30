# Sharp P104 Newton entrance at every payload depth

For every positive integer `lambda`, the unchanged PR2586 payload lift has the
same sharp independent source divisibility exponents as the nine-bit result:

```text
104 Y inputs        4 B_(9 lambda)
 78 N inputs        2 B_(9 lambda)
176 other inputs      B_(9 lambda)
```

Here `B_n = [[1,0],[1,1+i]]^tensor-n Z[i]^(2^n)`. Inputs may be arbitrary
nonseparable arrays across the nine-bit blocks. Every literal event, complete
block wrapper and coordinate stage stays in this module; signed-floor native
arithmetic agrees with the exact map and all eight owned private banks erase
as literal zero. A common grid scale may multiply the entire contract.

This closes the tensor-depth extension explicitly left unrun in
[PR3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406). It inherits
[PR3416](https://github.com/CrocSwap/integer-mult-bounds/pull/3416)'s exact
phase-sensitive native covariance and the credited all-rank Newton theorem of
Clear1nsight/PR3382. The two predecessor proof texts are retained unchanged.
Their original commits, paths, blobs and hashes are in [SOURCES.json](SOURCES.json).
No predecessor executable is imported or described as freshly rerun.

[PROOF.md](PROOF.md) proves the universal statement. The lift replaces each
native payload map by its tensor power, retaining every scalar ADD coefficient.
Tensor-powering the entire register program would change the problem.
The source's exact rational coefficient trace is independent of lambda.
Integral tensor lattice automorphisms then give both sufficiency and sharpness.

The stronger global module matters. Merely requiring every one-block slice to
belong to its one-block Newton module is insufficient. The embedded function
`pi*x_0*x_9` passes both sets of slice tests, but two block butterflies produce
a nonintegral value. The verifier includes this counterexample. Conversely,
its full depth-two fixture `1+pi^2*x_0*x_9` has a nonzero two-block determinant
and lies in B_18.

## Evidence and reproduction

The new checker independently reconstructs all 5,398 scalar events and checks
all 182 sharp source witnesses using separate reverse covectors. It authenticates
all 1,245 native records, 2,070 chronological occurrences and 2,490 wrappers.
The actual rank-seven recipes at events 2031 and 2033 are executed at depth two
on all 262,144 Gaussian coordinates of the nonseparable fixture. Every pair is
compared with an independent exact Gaussian formula; the full return is exact.
The forward result is also unchanged when the block-stage order is reversed.
[RECEIPT.json](RECEIPT.json) is regenerated and compared in full.

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -Werror -B research/p104-tensor-newton/verify.py
python3.12 -I -O -Werror -B research/p104-tensor-newton/verify.py
python3.12 -I -O -Werror -B research/p104-tensor-newton/test_verify.py
python3.12 -I -Werror -B scripts/research_package.py --package research/p104-tensor-newton
```

The first three commands work in a Git-free source export with the declared
inputs at their relative paths. They write no scientific output. Set `TMPDIR`
to an external owned directory for test/runner scratch. To regenerate a separate
receipt, pass `verify.py --write-receipt NEW_PATH`; overwriting is refused.
The function-level and actual optimized CLI controls reject changed quarters,
wrong dirty cleanup, incorrect frame/native bindings, singular wrappers, omitted
tensor constant phases, nonintegral signed pairs, source-byte changes, missing
sources and Boolean expected-receipt drift.

## Scope and price

The all-depth claim is proved by the written tensor/module argument and the
source scalar certificate. The fixture is one complete depth-two native round
trip, not the whole depth-two word. The predecessor covariance certificate,
a complete depth-two word replay, tensor compiler, all-size supplier theorem,
formal proof kernel, actual caller admission, numerical heights, physical
ownership/routing and recursive cost are unrun or inherited as stated.

The source exponent count is not an arbitrary-input precision saving. The full
public entrance has Gaussian index `2^((179*n+572)*2^n)` at `n=9 lambda`.
This restrictive domain becomes larger in dimension with depth. Preparing it
and recovering a caller's requested map need their own intertwiners and bill.
PR3423's unfavorable unchanged-profile stop remains in force. There is no
new supplier, kappa or selected-frontier claim, and no further construction
round is proposed by this package.

## Open next questions

Can an actual caller supply these all-depth modules and consume their chart
outputs at a favorable complete cost? Start with an explicit caller, a paid
module-compatible codec/intertwiner and its dirty-state contract. Ownership,
numerical widths and a changed favorable complete bill are blockers.
[TASK.json](TASK.json) records that question and the changed card scope.
The active external-675-recipient audit and the parallel correlated first-cone
module question remain separate investigations.

## Credit and implementation limits

Nick Petalas. Apache-2.0. Credit Clear1nsight for PR3382's all-rank Newton
construction and PR3423's interfaces, ywz65 for PR2586, Tekalign for signed-floor
and phase-sensitive comparison conventions, Ross Richardson, Arham Tahir,
Alejandro Zarzuelo Urdiales, Jose Manuel and the retained native, geometry,
compiler and precision lineage. Classical Barnes-Wall provenance remains with
Nebe, Rains and Sloane. Retained predecessor bytes and original notices are
unchanged. TASK.json records the review status.

Build the Lever produced the rerunnable source-bound certificate. Prove It
Works required the actual nonseparable tensor fixture and real CLI rejection
controls. Separate Before Serializing Shared State kept the worker and output
paths separate and used process-held OS locks for shared Git writes.

Power of Ten bounds the word to 5,398 events, 358 public roles, 1,245 native
classes and rank at most nine. Finite diagnostic depth is at most two, with
262,144 Gaussian coordinates. New functions stay within 60 physical lines.
All assertions affecting acceptance use exceptions and survive optimization.

Rule 3 deviation, verify.py. Python exact integers and lists allocate during
verification; this is a bounded functional reference, not an allocation-free
runtime. Live arrays have at most 262,144 entries, at most five diagnostic
arrays coexist and scalar rows have at most 359 by 358 rational entries. The
native plans have at most 2,490 by 512 address/phase entries and 2,070 bounded
occurrence references. Source and fixture sizes are fixed; overflow is impossible
for Python integers.
The public replay and source-failure paths verify the control. A production
backend must provide its own fixed capacities and numerical height bound.

Rules 8 and 9 deviation, test_verify.py. runpy loads only the one fixed sibling
verify.py to exercise its functions under isolated Python. It imports no
predecessor module and generates no code. The real optimized subprocess CLI
controls separately exercise the public entry point. A future installed Python
package could replace this test-only loader; that packaging change is outside
this scoped mathematical contribution.
