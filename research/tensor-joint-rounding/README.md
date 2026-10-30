# A smaller stored-factor Tensor rounding allowance

This package was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For the unchanged five-stage arithmetic interface of Hiroki KUMAZAKI's
[PR #5295](https://github.com/CrocSwap/integer-mult-bounds/pull/5295), the
stored-factor complex rounding bound improves from

```text
sqrt(2) [2^-p + 2^(2sigma-P) (n+6)/4]
```

to the strictly smaller bound

```text
sqrt(2) [2^-p + 2^(2sigma-P) (n+2)/4].
```

The reduction is exactly `sqrt(2) 2^(2sigma-P)` in the sufficient allowance.
The program and its intermediate records are unchanged. The improvement uses
the dependence between the final two residuals. It does not remove either
rounding operation or declare its residual zero. The coefficient-sensitive
bound below improves the final-grid term as well.

This is a numerical side result for the `centre-path-sharing` card. It does
not eliminate a physical centre operation or supply an invoice improvement.
The predecessor's five-residual identity, its existing valid coarse bound and
its computed-input telescope are credited mathematical inputs, not audited or
replayed here. No new kappa or selected-frontier change is claimed.

## Interface and result

Let `p>=1`, `sigma>=0` and `P>=p+2sigma` be integers. Set
`Q=2^P`, `h=2^-p`, `lambda=2^(2sigma)` and `d=P-p-2sigma`.
For an integer `u` and nonnegative integer `s`, define signed truncation
`t_s(u)=sign(u) floor(abs(u)/2^s)`. Apply it componentwise to complex integer
pairs. Use the stored nonnegative integers

```text
0 <= A_j,K_l,B_z <= Q,    0 < C <= Q/4,
a_j=A_j/Q, k_l=K_l/Q, b_z=B_z/Q, c=C/Q.
```

The existence of such a positive integer `C` implies `P>=2`. The input has
complex integer numerators `v_j` on the p-grid. No input norm restriction is
needed for this stored-factor rounding statement. Retain exact integer
products, promotion, convolution and the stated crop. For each target `z`,
all `n` source indices are valid in its convolution row. The arithmetic is

```text
w_j = t_P(A_j 2^(P-p) v_j)
y_l = t_P(sum_j K_(l-j) w_j)
z_z = t_P(B_z y_(n-1+z))
f_z = t_P(C z_z)
o_z = t_d(f_z).
```

Its exact stored-factor comparison row is

```text
(Wx)_z = lambda c b_z sum_j k_(n-1+z-j) a_j (v_j/2^p).
```

Write `D=2^(P+d)` and `g=gcd(C,D)`. Then

```text
|o_z/2^p - (Wx)_z|
 < sqrt(2) [h(1-g/D)
             + (lambda/Q)(c b_z sum_j k_(n-1+z-j) + c b_z + c)]
 < sqrt(2) [h + (lambda/Q)(n+2)/4].                 (A)
```

The tail term `h(1-g/D)` is the exact maximum scalar tail defect when its
integer input `z_z` ranges freely. Its complex analogue is exactly
`sqrt(2) h(1-g/D)` when the two integer components range freely. These are
sharp tail statements. Neither whole-row bound in (A) is claimed sharp,
because the earlier computed stages may restrict the tail's attainable inputs.

## Proof

For integers `u` and nonnegative `a,b`,

```text
t_b(t_a(u)) = t_(a+b)(u).                            (B)
```

For `u>=0`, write `u=2^(a+b)q+2^a r+s`, where `0<=r<2^b` and
`0<=s<2^a`. Both sides equal `q`. Oddness gives the negative case. This
includes a zero shift. Thus the actual last two operations satisfy

```text
o_z = t_(P+d)(C z_z),
tau_z = o_z - C z_z/D.
```

Every scalar residue `C z_z mod D` is a multiple of `g`. Conversely every
multiple of `g` occurs, since multiplication by `C/g` permutes the residues
modulo `D/g`. On nonnegative inputs the discarded fractional part therefore
ranges from zero to `(D-g)/D`. Signed truncation has the same absolute
maximum on negative inputs. This proves the sharp tail formula, including
`g=D`, when it is zero. Independent real and imaginary components give its
sharp complex version.

Use the predecessor's first three computed-operand residuals,

```text
rho1_j = w_j - Q a_j (v_j/2^p)
rho2_z = y_(n-1+z) - sum_j k_(n-1+z-j) w_j
rho3_z = z_z - b_z y_(n-1+z).
```

Each scalar component has absolute value below one. Substitution now gives
the exact joint-residual identity

```text
o_z/2^p - (Wx)_z
 = (lambda/Q) [c b_z sum_j k_(n-1+z-j) rho1_j
                 + c b_z rho2_z + c rho3_z] + h tau_z.      (C)
```

The combined tail is related to the predecessor's residuals by
`h tau_z = (lambda/Q) rho4_z + h rho5_z`. Bounding these two terms
independently discards the relation (B). The present proof bounds their
actual sum, without assuming that arbitrary residuals share this bound.

Apply the triangle inequality to (C), with the sharp tail bound. The first
three complex residuals have modulus strictly below `sqrt(2)`. The
coefficient of `rho3` is positive because `c>0`, so their total bound is
strict even if some other coefficients vanish. Finally,

```text
c b_z sum_j k_(n-1+z-j) + c b_z + c <= n/4 + 1/4 + 1/4.
```

Since `g/D>0`, this proves both inequalities in (A).

As an arithmetic corollary, an allowance `sqrt(2) 2^-p (1+epsilon)` is
sufficient whenever

```text
(n+2) / [4 * 2^(P-p-2sigma)] <= epsilon.
```

For the declared one-source row and `epsilon=1/2`, one extra work bit above
`p+2sigma` suffices by this test. The predecessor's coarse test needs two.
This compares sufficient rounding tests. It is not a minimum work-precision
claim, a production-page example or an installed precision policy.

## Evidence and reproduction

The standalone verifier uses only exact integers and `Fraction`. It imports
no predecessor executable. It authenticates the pinned predecessor proof and
prints a generated receipt binding every package file's SHA256.

Its fixed finite domains cover:

- 262,208 signed consecutive-truncation cases, including zero shifts.
- 304 coefficient/shift systems and 224,272 signed tail inputs, directly
  checking the maximum against the gcd formula and attaining it in every system.
- 164,700 scalar rows in five precision/scale configurations and widths one
  and two, with independent Fraction execution and the exact identity (C).
  These include 25,920 rows with nonzero opposite input values and 73,200
  rows with zero extraction shift. The former count describes the inputs,
  without asserting that every weighted convolution cancels.
- 14,406 complex rows with both inputs in the declared p-grid unit disk.
  The complex inequality is checked by squaring exact rational quantities.
- Ten invalid argument rejections, four arithmetic boundary controls and
  four nonzero transported-term omission witnesses. The controls distinguish
  floor division, a nonexpansive-rounding shortcut, forgetting normalization
  when extraction has zero shift, and dropping the coefficient gcd.

From the worktree root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/tensor-joint-rounding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/tensor-joint-rounding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/tensor-joint-rounding
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/tensor-joint-rounding --check-source-history
```

The direct marker is `PASS_TENSOR_JOINT_ROUNDING`; the generic runner reports
`PASS_REGISTERED_RESEARCH_PACKAGE`. Any CPython 3.12 path can replace the
local interpreter. Direct replay works in a Git-free export containing the
package and its one declared predecessor-proof input. Source-history checks
require full Git history. Every registered check has a 120-second limit.

The written proof is universal within the stated arithmetic interface;
finite checks corroborate it. Independent human and formal proof-kernel
review are unclaimed.

## Implementation constraints

The verifier has no recursion, subprocesses, generated code or mutation of
source files. Every loop ranges over a fixed finite domain. The largest
individual Cartesian row family has 36,000 cases; each tail scan has at most
4,097 integers, and each composition scan has 262,208 cases. Functions stay
below 60 physical lines. Explicit exceptions keep all checks active under
optimization. Package and predecessor files are bounded before hashing.
Warning-strict ordinary and optimized runs provide the available diagnostics;
no external static analyzer is installed in the research interpreter.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates integers and Fractions during exact arithmetic. Fixed domains,
width at most two, shifts at most 15 in executed cases, and fixed-size result
records bound live mathematical data. There is no accumulated row history.
A fixed-storage exact implementation would require a separate native checker;
revisit that choice if these finite domains grow. Standard-library iterator
and arithmetic dispatch are a rule 9 deviation with fixed known targets and
no callbacks, plugins or dynamic imports. This keeps the checker standalone.

## Limitations

This is a bound against the exact stored-factor row. Coefficient enclosure,
production Gaussian tails and original-coordinate producer admission remain
inherited and separate. PR #5295's computed-input telescope can use a smaller
local stored-factor defect, but its full analytic and physical hypotheses
are not discharged here. No actual physical Tensor prefix, coefficient
catalogue, native backend, compiler, tape caller, selected scientific replay,
Lean or Docker run is performed. Work widths, runtime, storage, dirty return,
chirp/compression, final Fourier accuracy and the complete multiplication
theorem are outside this contribution. The five selected framework assumptions
remain open. This result neither supplies nor prices a physical optimization.

## Open next questions

1. Can the actual producer use a smaller work precision while preserving
   coefficient enclosures, production tails and every operand-width gate?
   Begin with one complete admitted page and compare all precision conditions.
   This arithmetic allowance alone does not settle the other conditions.
2. What is the sharp whole-row error for a fixed stored page? Start by
   characterizing the reachable residues of `z_z`, rather than treating it
   as a free integer. Earlier truncations and signed convolution couple those
   residues, so the sharp tail bound need not be attained by a whole row.

## Sources and credit

Hiroki KUMAZAKI, `kumagi`, supplied PR #5295's five-residual identity,
coarse local bound, computed-input telescope and precision boundary, at head
`351975ee703ec5aa1b18f70f73700d434026199a`. Its `PROOF.md` is pinned by
Git blob and SHA256 in `SOURCES.json`, and authenticated before replay.
JoyboyBrian's [PR #5056](https://github.com/CrocSwap/integer-mult-bounds/pull/5056),
head `fe624453057b7f0cb42870a594d314a148b9fb84`, supplies the preceding
norm invariant. Jose Manuel, `jmbarrancoml`, supplied the physical expansion
and its original accuracy proposition, retained at
`1a86a8fb73bb7a0982fff99852a031832c191902`. Dugongue's Gaussian row bounds
and the coefficient, Gaussian, chirp, word, native and manuscript contributors
retain their predecessor credit. No source or notice is modified or copied.

Signed integer quotient composition and the gcd image of a cyclic group are
classical. The new contribution is their joint-residual application to this
five-stage interface, the strictly smaller stored-factor bound, its sharp
free-input tail constant and the standalone verifier. No general literature
priority for the elementary identities is claimed.
