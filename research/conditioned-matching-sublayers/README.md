# Sharp interpolation for conditioned matching layers

This contribution was produced by Nick Petalas. Apache-2.0.

## Result and scope

This resolves a conditioned version of the primitive-alphabet question in Brian / JoyboyBrian's
[PR #4976](https://github.com/CrocSwap/integer-mult-bounds/pull/4976),
[Open next questions](../matching-sublayer-norm/README.md#open-next-questions).
That package supplies the matching-cut identities and the unrestricted
`sqrt(2)` bound. We add a two-sided local gate bound and prove the smaller,
sharp factor

```text
rho(K) = sqrt(2 K^2 / (1 + K^2)),    K >= 1.
```

Here K bounds the Euclidean operator norm of every complete gate and its
inverse. The factor is one for unitary layers and strictly below sqrt(2) for
any finite K. The claim type is a scoped written mathematical proof, with exact
finite corroboration. It is neither a finite census theorem nor a complete
multiplication theorem. No supplier admission, new kappa or selected-frontier
change is claimed.

The sharpness statement concerns an individual adjacent-boundary norm
implication, with arbitrary invertible surrounding operators. We prove all
four implications below. Optimality under additional simultaneous constraints
coupling all four surrounding operators is not claimed.

## Weighted Gram theorem

Work over a finite-dimensional complex Hilbert space. Let G be invertible,
let E be an orthogonal projection commuting with G, and put

```text
H = E G + (I-E),    q = K^2,
q^(-1) I <= G* G <= q I,    c = q/(1+q).
```

For a matching layer, E selects the supports of complete gates. Unused
coordinates carry the identity. The two-sided bound holds for the whole
layer because its gates act on disjoint orthogonal supports.

Commutation with E also holds for G* and G*G. The following identity proves
the theorem:

```text
c (I + G*G) - H*H
 = [ E (q I - G*G) + (I-E) (q G*G - I) ] / (1+q)
 >= 0.                                                       (1)
```

Each bracketed term is positive semidefinite on its own orthogonal support.
For every matrix A of compatible size, congruence by A and evaluation on a
unit vector therefore give

```text
||H A||^2 <= c (||A||^2 + ||G A||^2).                         (2)
```

The same proof applied to G* and then adjointed gives

```text
||A H||^2 <= c (||A||^2 + ||A G||^2).                         (3)
```

In particular, two adjacent bounds at most F imply a partial-layer bound
`rho(K) F`. More generally adjacent bounds a,b imply
`sqrt(q/(1+q)) sqrt(a^2+b^2)`. This improves the corresponding generic
adjacent-boundary sum-of-squares estimate under the added gate hypothesis.

The proof uses no dimension bound, invertibility of A, rationality condition
or restriction to real coefficients. The finite checker below uses rational
matrices, including realifications of complex matrices.

## All four matching-cut operators

Use the predecessor's column convention and complete boundaries

```text
P1 = G P0,    S0 = S1 G.
```

At a partial layer let `J = (I-E)G + E`. Since `G=JH=HJ`, the four operators
and applications of (2)-(3) are

```text
P     = H P0:            use (2) with G, E, A=P0
P^-1  = P0^-1 H^-1:     use (3) with G^-1, E, A=P0^-1
S     = S1 J:           use (3) with G, I-E, A=S1
S^-1  = J^-1 S1^-1:     use (2) with G^-1, I-E, A=S1^-1.
```

G^-1 and G* have the same two-sided cap K as G. The two complete neighbors
in each application are exactly the corresponding prefix, suffix or inverse
neighbors. Thus if each pair has a common bound F, all four partial operators
have bound `rho(K) F`. No commutation between E and P0 or S1 is assumed.

For arbitrary segments whose two endpoints independently have bound
`rho(K) F`, submultiplicativity gives `rho(K)^2 F^2`.
This is an exact-operator implication. It does not count rounding events or
change a stored-component width or fractional grid.

## Sharpness of the factor

Fix any real K>=1. In dimension two take

```text
G = diag(K,1/K),    E = diag(1,0),    H = diag(K,1),
A_epsilon = [[1,0],[K,epsilon]],    epsilon > 0.
```

A_epsilon is invertible. Both adjacent norms tend to `sqrt(1+K^2)` as
epsilon tends to zero, while `||H A_epsilon e0|| = sqrt(2) K`.
Consequently no smaller uniform factor than rho(K) can replace it in the
common-F implication, even with invertible surrounding operators and two
scalar matching gates. Adjointing the construction and replacing G by its
inverse gives the same optimal constant in the other three individual
implications. At K=1, equality already follows from the identity layer.

The finite checker does not approximate singular values. For rational K and
epsilon it upper-bounds both adjacent squared norms by their squared
Frobenius norms and lower-bounds the partial norm on e0. This gives the exact
lower bound

```text
2 K^2 / (1+K^2+epsilon^2),
```

which converges to rho(K)^2. The written limit proves sharpness for every K;
finite witnesses only corroborate it.

## Unitary and shear alphabets

For a unitary matching layer, any subset of its whole gates is unitary.
All four partial norms equal their respective neighboring norms. Thus the
unitary butterfly part of the retained alphabet has no interpolation loss.
This statement is about whole gates, including their complex phases.

For a shear `S_t = [[1,t],[0,1]]`, set u=|t|. Its Gram eigenvalues have
product one and sum `2+u^2`, so its norm and inverse norm both equal

```text
K_t = (sqrt(u^2+4)+u)/2.
```

For any matching of such shears with |t|<=u, the new bound becomes

```text
rho_t^2 = 2 K_t^2/(1+K_t^2) = 1 + u/sqrt(u^2+4).             (4)
```

It is sharp even for two copies of the same shear at magnitude u. For u>0,
let v+ and v- be unit right singular vectors of S_u with singular values
K_t and K_t^-1. For `G=S_u direct-sum S_u`, selecting only its first gate,
take `x=(v+, K_t v-)`. The norms of x and Gx both equal `sqrt(1+K_t^2)`;
the partial image has norm `sqrt(2) K_t`. Extend this rank-one input map to
invertible matrices tending to it, as in the preceding construction.
A complex phase of t is removed by diagonal unitary conjugation, so the
same statement holds for complex shears. The u=0 case is the identity.

For unit shears, (4) is `1+1/sqrt(5)`, strictly below two. An explicit
limiting vector is `(1,phi,phi^2,-phi)`, where `phi=(1+sqrt(5))/2`.
The rational checker uses Fibonacci ratios tending to phi and invertible
extensions. Its gate-cap fixtures use the rational enclosure
`K_t^2 < 21/8` at u=1, rather than claiming floating-point certification of
the irrational endpoint.

## Evidence and reproduction

From the repository root, use CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/conditioned-matching-sublayers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/conditioned-matching-sublayers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/conditioned-matching-sublayers
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/conditioned-matching-sublayers --check-source-history
```

The direct checker prints a generated JSON receipt binding all five package
files by SHA256. It writes no output files and imports no predecessor code.
Local normal and optimized checks pass 64 matching cases, 512 Gram checks,
512 four-way context checks, 55 diagonal and 13 unit-shear invertible
sharpness witnesses, and 15 rejection controls. These are executed cases,
not a count of distinct equivalence classes. Both registered checks pass.
Its exact Schur-complement PSD check includes zero-pivot rejection. It checks
both sides of (1), PSD, both gate caps, inverse/adjoint/complement variants,
and four-way congruences in dense noncommuting contexts. Fixtures include
rational unitary rotations, real unit shears, and realified complex unit
shears, with whole-gate selections and coordinate permutations. The receipt
enumerates every executed fixture, inequality, witness and rejection control.

Controls reject malformed inputs, split gates and invalid upper/inverse caps.
They also exhibit a split-unitary failure, a missing-inverse-cap failure,
a false no-loss bound and an undercut sharp factor. These tests corroborate
the new lemma; they do not replay #4976's scientific certificate.

The missing-inverse-cap example has `G=diag(2,1/4)`,
`H=diag(2,1)` and `A=[[1,0],[7/4,1/100]]`. Its first-column lower bound,
divided by the larger adjacent squared Frobenius norm, exceeds `8/5`.
Thus even an invertible context can violate the proposed K=2 factor when
only the upper gate cap is assumed.

The implementation bounds matrix dimensions at eight, fixture families at
three, masks at four, contexts at two and witness loops at thirteen. Every
loop has a finite bound. Python/Fraction dynamic allocation is a managed-runtime
deviation from fixed storage. The finite dimensions and fixed rational fixture
generators bound live data. The ten-entry rejection table uses fixed pure
validation callables, a limited indirect-call deviation. All invariant checks
use explicit exceptions and remain active under -O. Warning-strict normal and
optimized commands are registered. No shared configuration is changed.

## Limitations

E must commute with G and select complete orthogonal gate supports. Cutting
inside a two-wire gate can violate even the unitary no-loss conclusion.
The inverse cap is needed for (1) and for the sharp common-F claim at general
K. The checker includes counterexamples to dropping these hypotheses.

No coefficient preparation, multiply/add/round kernel, temporary width,
physical tape execution, supplier invoice or universal multiplier is supplied.
The written proof is not a formal proof-kernel artifact. Independent human
and formal proof-kernel review are unclaimed. Hosted CI is pending at initial
publication. The selected construction and all predecessor files are unchanged.

## Open next questions

Can one actual compensated-shear layer use its exact two-sided gate cap to
reduce a complete precision allocation? First extract that layer's coefficients,
compute a certified cap and substitute rho(K) into the same complete caller
budget. The remaining blockers are rounding-event accounting, temporary widths
and source-specific physical costs. A smaller exact operator envelope alone
does not establish a smaller valid production grid. No further construction
search is justified by this lemma alone.

## Provenance and overlap

Base `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The selected baseline command returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`;
no selected scientific replay was run. The original coverage-law-change card
is retained verbatim in TASK.json. Scope changed to a numerical matching-boundary
side result because #4976 poses this precise missing primitive-alphabet step.
It can reduce a precision envelope, without changing productive target credit.

Credit Brian / JoyboyBrian for #4976, its four matching-cut identities and
explicit open question; Jose Manuel / jmbarrancoml for the retained rational
FFT/Full numerical contracts; Vlado Vojdanovski for matching scheduling; and
Chafik Boukhalfa for phase construction. The Gram-order argument and shear
singular-value calculation use elementary linear algebra. We claim this scoped
refinement and its sharp witnesses, not priority for those background methods.
Source pins are provenance-only. No predecessor implementation is imported.
Armin Pourshafeie / apoursh's #5240 already gives the split-unitary row-splice
warning; it is used here only as a rejection control. Nick Petalas's #4829
gives absolute cut norms for a particular dirty Toeplitz circuit. The new
quantity here is a conditioned adjacent-boundary interpolation factor; that
earlier circuit theorem and its open caller questions are not extended.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19218968).
Live open PRs, recent account work, the latest handoff comments and active
Discussions were checked before claiming. Searches of merged work and main
used matching/sublayer, the factor's shape and conditioning terms. Coverage is
advisory; unpublished work and every historical diff were not exhausted.
