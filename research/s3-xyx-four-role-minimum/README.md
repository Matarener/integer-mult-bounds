# A fourth dirty role does not lower the S3 xyx double minimum

**Finite exact minimum. No new κ.** The selected record is unchanged.

## Result

In `M4(F2[S3])`, with paid labels `x = (1 2)`, `y = (2 3)` and calls

```text
D_N(g) = I + ([g] + [e]) N,    g in {x, y},
```

where `N` ranges over all 120 rank-one idempotents of `M4(F2)`, the target

```text
diag([xyx], [xyx], [e], [e])
```

needs exactly **six** paid calls. Roles 2 and 3 are arbitrary dirty roles that
must be returned unchanged. No word of length at most five over the 240 paid
factors equals the target. The direct word `x y x` on role 0 followed by
`x y x` on role 1 attains six.

This answers open question 1 of Wentao Li's
[PR #4084](https://github.com/CrocSwap/integer-mult-bounds/pull/4084)
([`research/s3-three-role-xyx`](../s3-three-role-xyx/README.md)), which proves
the same minimum with three roles. The answer is no: a fourth restored dirty
role does not save a call. The statement covers four roles only.

## Method

`Phi : F2[S3] -> M2(F2) x F2[C2]` sends `[g]` to `(rho(g), c^sign(g))`, where
`rho` is the action of `S3` on the three nonzero vectors of `F2^2`. The
verifier checks that `rho` and `sign` are homomorphisms and that `Phi` is
bijective on the six basis elements, so `Phi` is an algebra isomorphism and
acts entrywise on `M4`. In the `C2` block every paid factor is `I + delta N`
with `delta = c + 1` and `delta^2 = 0`, so a word maps to
`I + delta * (sum of its N)`. In the `M2` block a paid factor is a transvection
of `F2^8` with rank-one difference `(u (x) p)(v (x) q)^T`.

Each paid factor is an involution, so the inverse of a word is the reversed
word. The target has a word of length at most five exactly when
`ball(I,3)` meets `T * ball(I,2)`. The verifier builds `ball(I,2)`
(layers `1, 240, 32650`), forms `T * ball(I,2)`, and tests every element of
`ball(I,2)` and every one-call extension. There are zero hits. The `M8(F2)`
image alone already has zero hits, so the `C2` block is not needed for this
target.

## Controls

- Three-role calibration: the same engine gives ball layers
  `[1, 56, 1750, 45396]`, equal to the pinned
  [PR #4084 certificate](../s3-three-role-xyx/CERTIFICATE.json). This checks
  the encoding against a fully different implementation; it is not a new check
  of that result.
- An independent engine multiplies directly in `M4(F2[S3])`. Its `ball(I,2)`
  maps under `Phi` to exactly the fast engine's set of 32,891 states.
- Every paid factor squares to the identity in both engines.
- Positive controls: the same search finds words of length at most five for
  `diag([xyx],[xy],[e],[e])` and `diag([x],[y],[xy],[e])`, whose direct
  words have lengths 5 and 4.
- The direct six-call word equals the target in `M4(F2[S3])`. Each of its six
  one-call omissions does not.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -I -B research/s3-xyx-four-role-minimum/verify.py
python3.12 -I -O -B research/s3-xyx-four-role-minimum/verify.py
python3.12 -B scripts/research_package.py --package research/s3-xyx-four-role-minimum
```

Each direct run prints `PASS_S3_XYX_FOUR_ROLE ... short_hits=0
rho_quotient_hits=0 direct=6 target_minimum=6` in about 11 seconds.

## Scope and limits

This is a finite exact minimum for one target, four roles and the stated
optimistic unit-cost alphabet. It does not cover five or more roles, other
`S3` targets, free address maps, native source generation, hosting, or any
supplier price. No κ, selected result or multiplication theorem changes.

## Open next questions

1. Does a fifth or any larger number of restored dirty roles lower the
   six-call minimum? Three and four roles give six, and a uniform answer would
   close the workspace question for this target. A first step is a uniform
   argument in the `M_{2m}(F2)` block, where the restricted transvections
   already exclude length five at four roles. Five roles have 992 factors, so
   `ball(I,2)` has up to about `5 x 10^5` states (an estimate, not computed),
   which is slow for this pure-Python search.
2. Is the `rho` quotient enough for every role count? At four roles the
   `M8(F2)` image alone excludes length five. Characterizing products of at
   most five such transvections that act as the partial swap on two coordinate
   planes would give a cleaner certificate. Only the four-role observation is
   available here.

## Credit

The target, alphabet, three-role minimum and this open question are from
Wentao Li / VictorLiwentao's PR #4084. The alphabet lineage includes Cinna
Davis's two-register `S3` census
([`research/bit-s3-two-target-census-seed36501`](../bit-s3-two-target-census-seed36501/README.md))
and the two-dimensional representation bound of PR #3893. The four-role
search, its controls and this note were produced by Nick Petalas. Apache-2.0.
