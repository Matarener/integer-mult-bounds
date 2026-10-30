# A split determinant does not imply radical reachability

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped algebraic proof with finite corroboration.** Over every
field K, let R=K[x,y,z]/(x,y,z)^2. On exactly three roles, allow paid factors
I+uv^T with u in R^3 and v in K^3, and arbitrary free GL_3(K) maps. Put

```text
A = [[0,1,0], [0,0,1], [0,0,0]],
B = [[0,0,0], [1,0,0], [0,-1,0]],
M = xI_3+yA+zB.
```

Then M is unreachable at every finite paid length, although its homogeneous
determinant is the completely split polynomial

```text
det(XI_3+YA+ZB) = X^3.
```

This answers the sufficiency question in Open next question 2 of
[PR #4776](https://github.com/CrocSwap/integer-mult-bounds/pull/4776)
negatively. Its two-generator determinant classification does not extend by
testing determinant splitting alone. A common left eigenrow is an additional
necessary condition. No new kappa, supplier admission or complete multiplication
theorem is claimed.

## Proof

### The common-row condition with several radical generators

The first-zero scalar-prefix argument of
[PR #4773](https://github.com/CrocSwap/integer-mult-bounds/pull/4773)
extends to any finite number of independent square-zero generators. Here is
the extension needed for this example.

Let R=K[t_0,...,t_s]/(t_0,...,t_s)^2 and let an endpoint on n roles be

```text
M=t_0 I_n + sum_(j=1)^s t_j A_j.
```

If M is reachable in the same alphabet, the A_j have a common nonzero left
eigenrow over K, with a possibly different eigenvalue for each j.

Conjugation by any G in GL_n(K) preserves the paid alphabet. Moving all free
maps to the right therefore writes an alleged word as M=F_L...F_1 G. The
scalar coefficient of its paid prefix eventually becomes zero. At the first
such step, let H be the preceding nonzero scalar prefix and write

```text
F_k=I+(a+sum_j t_j b_j)v^T,  T=I+av^T,  TH=0.
```

A rank-one perturbation of I has nullity at most one. Thus T is singular,
v^T a=-1, H=a r^T for some nonzero row r^T, and v^T T=0. In particular
psi=v^T H=-r^T is nonzero. If C_j is the t_j coefficient before this step,
its new value is D_j=T C_j+b_j psi. Consequently

```text
v^T D_j=alpha_j psi,  alpha_j=v^T b_j,  for every j=0,...,s.
```

After the scalar prefix becomes zero, later radical coefficients contribute
nothing because all products of radical generators vanish. Let S be the
product of the later scalar factors. The final coefficients are S D_j G.
The t_0 coefficient is I_n, so S and D_0 are invertible and alpha_0 is
nonzero. With w^T=v^T S^-1, a nonzero row, we have

```text
w^T = v^T D_0 G = alpha_0 psi G,
w^T A_j = v^T D_j G = (alpha_j/alpha_0) w^T.
```

This proves the condition for arbitrary finite length and arbitrary free
base-field maps. It does not assert that a common eigenrow is sufficient.

### The counterexample violates that condition

For the displayed A, A^3=0. If w^T A=lambda w^T and w is nonzero, then
lambda^3=0, hence lambda=0 over a field. Writing w^T=(a,b,c) gives
w^T A=(0,a,b), so every left eigenrow is (0,0,c), with c nonzero. But

```text
(0,0,c) B=(0,-c,0)
```

is not a multiple of (0,0,c), in any characteristic. The two matrices have no
common left eigenrow. The condition just proved excludes M at every length.

The determinant calculation is over Z[X,Y,Z], so it survives passage to
every field, including characteristic two:

```text
XI+YA+ZB = [[X,Y,0], [Z,X,Y], [0,-Z,X]],
det(XI+YA+ZB) = X(X^2+YZ)-YZX = X^3.
```

The determinant here is the homogeneous polynomial of the coefficient
matrices. The determinant of M inside R is zero and carries no such information.
The example therefore passes precisely the polynomial splitting condition
left open by #4776, while failing the new common-row test.

## Evidence and reproduction

The standalone verifier imports no predecessor executable. It performs an
integer polynomial determinant expansion, with all six permutations and all
27 coefficient choices per permutation. No numerical substitutions are used
to infer the identity.

It enumerates every nonzero row and every possible scalar eigenvalue over
F2, F3, F5, F7 and F11. The nonzero-row counts are respectively
7, 26, 124, 342 and 1,330. In each field the A eigenrows are exactly the
nonzero multiples of the third coordinate row, the B eigenrows are exactly
the nonzero multiples of the first, and their intersection is empty. The
universal conclusion rests on the proof above, rather than this finite list.

Two reachable controls delete zB or yA. Their literal three-factor
column-replacement words use increasing column order for A and decreasing
order for B. A separate paid-operation interpreter agrees with the target
matrix action on every one of the 4,096 vectors in R^3 over F2 for each
control, giving 8,192 action comparisons. No coordinate is assumed initially
zero. Reversed execution order and each single omitted factor change the
corresponding matrix endpoint. A sign control replaces -E32 by +E32 and
obtains X^3-2XYZ over Z. Ring controls check both mixed and repeated radical
products vanish.

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/split-determinant-radical-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/split-determinant-radical-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/split-determinant-radical-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/split-determinant-radical-obstruction --check-source-history
```

Another CPython 3.12 path can replace the local path. Expected scientific
marker: `PASS_SPLIT_DETERMINANT_RADICAL_OBSTRUCTION no_new_kappa`.
Each run generates a stdout receipt with SHA256 hashes of all five package
files and writes nothing. No receipt is hand-written or committed.

## Scope and limitations

The ring kills all products of radical generators. Right vectors and free
maps are over K, and there are exactly three physical roles in the example.
Restored auxiliary roles, ring-valued free maps and higher nilpotency are
outside scope. This is an all-length obstruction in the declared formal
alphabet, not a search failure or an exclusion of arbitrary native networks.
No source preparation, physical movement, precision, stock, restoration or
complete supplier invoice is supplied. Those costs remain unknown.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker
and the selected scientific cold replay were not run.

The code has no recursion, subprocesses, dynamic evaluation or variable search
sizes. Its matrices have three rows. Each field scan has at most 1,330 nonzero
rows and eleven eigenvalues. Each dirty-input loop has exactly 4,096 vectors.
The ring has sixteen elements, and no large table of vectors persists. Every
function is below sixty physical lines. Explicit exceptions keep checks active
under optimized Python; warnings are errors. CPython's managed allocation is
a deviation from fixed steady-state allocation, bounded by these fixed domains.
No external static analyzer or proof kernel is claimed.

## Credit, provenance and coordination

Nick Petalas's #4776 supplies the exact two-generator classification and the
explicit three-generator open question. Nick Petalas's #4773 supplies the
first-zero common-row argument extended here. His #4745 supplies the earlier
two-role square-zero context, and #4243 the free-map normal form. Wentao Li's
#4099 following #2513 supplies the right-vector alphabet; ToikY's #4334
supplies the shared-chart context. These are cited predecessors, not audited
deliverables. No predecessor code or credit line is changed. No general
literature-priority claim is made for the underlying nilpotent matrix pair.
The contribution is its reachability obstruction answering the stated open
question and the common-row extension supporting that conclusion.

The `formal-interface-lemma` card is explicitly changed to this algebraic
side question. It identifies information a determinant-only interface loses;
it does not discharge a selected assumption or expand a physical construction.
The current source-bound baseline passed after its omitted sparse inputs were
materialized. Its marker is `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, which is
orientation rather than scientific replay.

[SOURCES.json](SOURCES.json) pins the original card, selected record and
conceptual predecessor READMEs as provenance at canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. There are
no external runtime inputs. Live open PRs, this account's earlier work,
recent handoff claims, active Discussions, local reservations, merged PR
searches and main README terms were inspected. The overlap helper had complete
remote pagination and incomplete sparse local-note coverage. That coverage
does not certify novelty.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213489).

## Open next questions

1. Is a full common invariant flag necessary for reachability of every
   square-zero target with an invertible coefficient? The first-zero argument
   yields only one eigenrow. Begin with a tuple having one common eigenrow
   but an irreducible quotient; the missing step is a quotient argument that
   preserves the paid alphabet and chronology.
2. Can a restored fourth role make this example reachable? Begin with
   diag(M,1). Its nonzero scalar endpoint prevents the first-zero argument
   used here, so a separate invariant or a literal attaining word is needed.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
These follow-ups are not investigated here.
