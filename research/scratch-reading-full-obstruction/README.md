# Scratch access does not rescue two elementary FULL shears

This scoped algebraic proof is produced by Nick Petalas. It answers the
scratch-reading follow-up in unpaidmoon's
[PR #5843](https://github.com/CrocSwap/integer-mult-bounds/pull/5843).
Either shear may read or write any owner, including dirty scratch. Under
the stated low-grade transverse and free-control hypotheses, its projected
image still has rank at least `(n-1) dim B`. Two pure high-grade targets
with restored identity scratch have rank only `(n-2) dim B`, so remain
impossible. No new kappa is claimed.

[PROOF.md](PROOF.md) states and proves the more general filtered-algebra
theorem. The new step chooses the first read-coordinate kernel regardless
of which owner the shear reads. It requires no commutation or domain
property. Its lower bound is sharp in the declared algebraic class.

## Reproduce

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/scratch-reading-full-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/scratch-reading-full-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/scratch-reading-full-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/scratch-reading-full-obstruction --check-source-history
```

The standalone command prints `PASS_SCRATCH_READING_FULL_OBSTRUCTION` in
its JSON result. Both registered checks run the same finite domain under
normal and optimized execution. They write nothing into the checkout.

## Finite evidence

The checker constructs `F2[S3^3]`, dimension 216, with the dimension-eight
subgroup algebra of `{identity,(01)}^3`. Grade counts coordinates outside
that subgroup. The projection retains grades at most two. Diagonal units
have grade at most one. The two target units have grade three.

Every ordered pair of distinct first-shear owners and every ordered pair
of distinct second-shear owners is checked for each of four explicit
coefficient/diagonal/free-control fixtures, at n=2,3,4. This gives 736
cases, including 512 with a scratch read, 512 with a scratch write and
176 with a scratch-to-scratch shear. The categories overlap. In 368 cases
the diagonal transverse factors remain identity on scratch, as in the
predecessor's setup; the rest exercise the theorem's wider diagonal class.
These are fixed fixtures, not every group-algebra coefficient or control.

Direct binary elimination finds full projected rank in all 736 cases:
16 cases at rank 16, 144 at rank 24 and 576 at rank 32. It separately
checks rank `(n-1)*8` on the actual first-read kernel, the projected target,
and whole maps with outer subgroup-algebra controls. Bitset coefficients
lift to integral group-algebra coefficients. Full rank modulo two also
certifies full rational rank for those lifted whole-word fixtures.

Separate equality examples attain the sharp `(n-1)*8` lower bound. The
controls exercise a too-low cutoff, a nonfree middle matrix, a nonunit
diagonal and an additional third query, plus noncommutativity, a nonzero
nilpotent free coefficient and a rejected same-owner shear.
The runtime JSON is generated from the arithmetic and records its scope.

## Sources and limits

The exact question source is #5843, pinned in [TASK.json](TASK.json).
[SOURCES.json](SOURCES.json) pins the main-branch grade proof from Chris R /
Clear1nsight #4920 and the distinct joint-bank theorem of thu-nmrc #5200
as provenance. They are cited premises, not audited deliverables or runtime
imports. Credit unpaidmoon for the question and clean-output argument,
Chris R / Clear1nsight for the full-monomial grade framework, thu-nmrc for
joint-main-bank stability, and their retained predecessor lineage.

The finite checker uses a small untwisted group algebra. It does not
reconstruct the physical Clifford macro. The written proof covers twisted
algebras when the stated filtration and bimodule hypotheses hold. The
source application's all-large-width implication uses #4920's separation
lemma. No new sufficient width, native/compiler/precision/tape/outer replay,
formal proof-kernel review, or independent human acceptance is claimed.
The selected frontier is unchanged. New material is Apache-2.0.

The chosen card's baseline command passed source-binding orientation.
The actual scope changes from helper construction to the explicit
scratch-access obstruction, as recorded in TASK.json. This rules out one
escape before anyone pays for a larger native or invoice search.

## Open next questions

Can a changed FULL macro with two independent query source coordinates
evade this obstruction at a favorable complete tariff? First specify a
legal macro and its complete target, transverse, restoration and paid-call
contract, then compute its projected image. The proof uses one read
coordinate per shear. No physical macro or complete invoice for that
changed premise is supplied here. TASK.json records the same question.

## Engineering notes

The verifier has no recursion, dynamic code generation or external
dependencies. Its fixed algebra has 216 basis elements, at most four owners
and at most 32 domain columns. All loops are bounded by these declarations
or finite case products. Python requires dynamic integer and collection
allocation; those dimensions bound live data. Each function is below 60
lines. Acceptance uses explicit exceptions and remains active under `-O`.
