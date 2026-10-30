# Sharp adaptive choice among higher-rank minors with shared columns

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped proof with exact finite corroboration. For a uniform
G in GL_m(F_q), let U be its first k rows, where 1<=k<m, and write U=[C B]
with k-1 shared columns C and t=m-k+1 remaining columns B. A candidate
v in F_q^t tests whether det[C,Bv]=0. Candidates are fixed before G is seen;
a selector may inspect all of G. Projectively equal candidates count once.

The sharp maximum failure probability with at most M>=1 candidates is

```text
1 - A max(q+1-M, 0),
A = q^(kt-2) (q-1) product_{j=0}^{k-2}(q^k-q^j)
    / product_{j=0}^{k-1}(q^m-q^j).
```

A projective pencil attains it over every finite field. At q=2,m=3,k=2,
the rates for one, two and three choices are 3/7, 5/7 and 1. This resolves
a concrete family in the higher-rank-intersection direction of ywz65's
[PR #2601](https://github.com/CrocSwap/integer-mult-bounds/pull/2601),
Open next question 2. Its linear-minor theorem is cited, not re-audited.
The new step is the exact common-column deficiency term and its combination
with the quotient test. [PROOF.md](PROOF.md) gives the all-field argument.

These determinant tests correspond to fixed input charts that share their
first k-1 columns. They need not be coordinate minors in one common chart.
The result does not identify the selected caller's actual bad varieties,
construct a physical selector, improve kappa or change the selected frontier.

## Exact evidence

The verifier enumerates every full-row-rank matrix and every nonempty
projective candidate family in five domains. Gaussian elimination selects
the full-row-rank frames; the permutation determinant expansion evaluates
every candidate. It computes each family's literal union count and maximizes
over all families within each budget, rather than assuming pencil optimality.

```text
q  m  k    full-row-rank frames   candidate families   deficient prefixes
2  3  2             42                    7                     6
3  3  2            624                   15                    48
4  3  2           3780                   31                   180
2  4  2            210                  127                    42
2  4  3           2520                    7                   504
```

That is 7,176 frames and 187 families across the five domains. F_4 uses
F_2[x]/(x^2+x+1), not arithmetic modulo four. Separate literal GL_3 censuses
cover all 168 binary and 11,232 ternary invertible matrices and compare
complete candidate-failure-mask frequencies with their top-frame fibers.
There are seven rejected formula-domain calls and seven semantic comparisons.
All acceptance checks use explicit exceptions and stay active under -O.

## Reproduce

From the repository root, with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/common-prefix-minor-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/common-prefix-minor-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/common-prefix-minor-frontier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/common-prefix-minor-frontier --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter path. The
verifier writes nothing and emits JSON with `PASS_COMMON_PREFIX_MINOR_FRONTIER`,
the enumerated results and SHA256 hashes of all six package files. Redirect
stdout outside the checkout to retain a generated receipt. Both registered
commands have 60-second limits. Local warning-strict ordinary and optimized
checks, metadata and publication-byte/source-history checks are required.
Hosted CI status is recorded separately in the PR body.

The direct verifier also runs from a Git-free copy of this package. Exact
source pins are historical provenance only. No predecessor executable is
imported, and there are no external live inputs.

## Limits and attribution

The all-finite-field quantifier follows from the written proof. The exhaustive
checks cover only the five stated domains. Arbitrary higher-rank minor families,
nonuniform matrices, current-dependent candidate preparation and a fully charged
selected caller remain outside scope. Physical reads, routes, restoration,
transcript emission, eligible-prime arguments and all five selected framework
assumptions remain open. No native, Lean, Docker or selected scientific cold
replay was run. Independent human and formal proof-kernel review are unclaimed.

Credit ywz65's #2601 for the question, bounded-choice interface and sharp
linear-minor pencil bound. Credit Adam Gall's #2097 for the fresh-row versus
adaptive-selection boundary, with the retained three-stage-cover, eumemic
source527, Rohan Arun, Jeremy Kothe and PR589 lineage. Finite-field matrix
completion counts and projective pencils are classical; no general literature
priority is claimed for those methods. No predecessor text or code is copied.

Canonical base is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The task picker suggested `replay-runtime`. [TASK.json](TASK.json) explicitly
changes it to this algebraic counting side result because the assignment
requires an original result rather than an audit. The selected orientation
passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is metadata orientation,
not scientific evidence for this theorem.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221368)
reserves this exact shared-column question. Live account PRs, current open
PRs and Discussions, merged-PR searches and tracked-main README searches
were checked. The overlap snapshot had 341 open PRs and 5,519 Discussion
records with complete remote pagination. Its local sparse coverage was
incomplete, so direct Git searches supplemented it. Unpublished work and
arbitrary code diffs are outside those checks.

## Open next questions

1. Does an actual stopped-cover caller expose a fixed candidate family of
   this shared-column form? First export its exact input charts and field
   distribution. Such an adapter, eligible-prime coverage, a complete current-
   field transcript and the physical selector bill are missing.
2. What is the sharp bound when only k-2 columns are shared? The quotient
   then has dimension two, and failure is a two-column determinant rather
   than a hyperplane. Start with one specified two-plane candidate family
   over F_2 and its literal GL distribution. Its intersection geometry is
   not covered by the one-dimensional reduction here.

## Verifier bounds

The verifier has no recursion, subprocesses, network use or write path.
Every matrix enumeration has at most 19,683 candidates; matrices have at
most four columns and three rows. Permutation determinants have at most
six terms. Candidate sets have at most seven projective points and 127
nonempty families. Functions are below 60 physical lines. Package reads
are bounded to 256 KiB each. Warning-strict normal and optimized execution
and in-memory syntax inspection supply diagnostics.

Python exact integers, lists and runtime calls allocate during this bounded
offline check. These are managed-runtime deviations from Power of Ten static
allocation and indirect-call restrictions. All call targets are fixed,
collections have the stated bounds, and there is no persistent shared state.
Larger executable domains require new capacity bounds before use.
