# Separate monotone UT3 price minima need not compose

For three central UT3(F2) targets with scalar rank cap three, set the complete
positive-rank prices to `a(d)=5+d^2` and `b(d)=10+d`. The exact full formal bill
is **54**, although the two independent partition minima sum to **53**.
Arbitrarily many restored dirty roles and non-idempotent scalar couplings
cannot attain that separate lower bill.

Claim type: **scoped algebraic proof with exact finite corroboration**.
This answers the nonproportional-price question in
[PR4846](https://github.com/CrocSwap/integer-mult-bounds/pull/4846) negatively.
The new step is a chronological cut obstruction. The predecessor's common-price
theorem remains applicable to its stated hypothesis. No physical supplier,
recursive moment gain, new kappa or complete multiplication theorem is supplied.

This package was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Model and theorem

Use Arham Tahir's [PR1919](https://github.com/CrocSwap/integer-mult-bounds/pull/1919)
rank-capped alphabet. Write `G=UT3(F2)` as

```text
(x,y,z)(u,v,w) = (x+u, y+v, z+w+xv),
a=(1,0,0), b=(0,1,0), c=abab=(0,0,1).
```

Group coordinates use binary arithmetic. For any finite `r>=3`, a paid call
in `Mat_r(F2[G])` is `D_N(g)=I+([g]+[1])N`, where `g` is `a` or `b` and
`1<=rank_F2(N)<=3`. Matrices `N` need not be idempotent. Every call is an
involution because `([g]+[1])^2=0`. Scalar invertible binary maps are free
in this formal model. Conjugation normalizes them into the paid matrices;
augmentation forces the remaining scalar map to be identity, as in PR1919.

Require the entire formal endpoint

```text
T = diag([c],[c],[c],[1],...,[1]).
```

Every input is arbitrary, including every spectator. There are no clean
ancillas, free address maps, central-letter calls, COPY, ERASE or uncharged
inverse calls. All restoration calls are charged.

Define the two nonnegative nondecreasing prices, with value zero at rank zero,
by `a(1..3)=(6,9,14)` and `b(1..3)=(11,12,13)`.

**Theorem.** The exact minimum bill for T is 54 for every finite r>=3.
The independent rank-partition lower bounds are 27 for a and 26 for b, but
no single legal word attains both. Four rank-three calls attain 54 without
extra roles.

## Proof

PR1919's coefficient-span lemma gives total rank at least six for each
letter, for every legal full endpoint and arbitrary restored dirty workspace.
Its rank argument builds on steph4n-gh #1573, Arham Tahir #1589 and Hanson Sun
#1607. The present proof uses that lemma. No predecessor executable is imported
or replayed.

For ranks d=1,2,3, the exact rational dual bounds are

```text
a(d) >= (9/2)d, with equality only at d=2;
b(d) >= (13/3)d, with equality only at d=3.
```

Consequently every word costs at least `27+26=53`. Equality requires total
rank exactly six for each letter, exactly three rank-two a calls and exactly
two rank-three b calls. These are the unique equality rank lists. They also
attain each independent partition minimum separately.

We now exclude their simultaneous occurrence. Use the inherited quotient

```text
Q = F2<X,Y> / (X^2,Y^2, all words of length at least three),
phi([x,y,z]) = 1+xX+yY+zXY+(z+xy)YX.
```

The group law makes phi an algebra homomorphism. It sends a calls to `I+NX`
and b calls to `I+NY`. Put `P=diag(1,1,1,0,...,0)`. The full endpoint has
zero X and Y coefficients and has both XY and YX coefficients equal to P.
This quotient supplies necessary conditions, not a sufficient endpoint test.

Consider any realizing word with exactly two b calls. Their scalar matrices
are equal, say N, because the Y coefficient is zero. Let L, M and R be the
sums of a-call matrices before the first b, between the two b calls and after
the second b. Vanishing of the X coefficient gives `L+M+R=0`. Expanding the
two mixed coefficients in their actual order gives

```text
XY: L N + (L+M)N = M N = P,
YX: N(M+R) + N R = N M = P.
```

Thus `rank M>=3`. Also `M=L+R`, so the a calls outside the interval have
rank sum at least three. The a calls inside the interval likewise have rank
sum at least three. If every a call has rank two, at least two must lie
inside and at least two outside. There cannot be only three a calls.
The argument permits arbitrary noncommuting matrices and every finite number
of restored dirty spectators.

This excludes bill 53. Every call price is an integer, so the bill is at
least 54. For attainment, execute `D_P(a),D_P(b),D_P(a),D_P(b)`. Each target
sees `abab=c`; every spectator sees identity. Its complete price is
`2*14+2*13=54`. This proves the theorem.

The result does not contradict the earlier asymmetric concave theorem in
[PR2129](https://github.com/CrocSwap/integer-mult-bounds/pull/2129). The a
price here is nonconcave. The common monotone theorem of #4846 also remains
unchanged. The failed implication is that arbitrary separate monotone
partition optima always compose into one legal word.

## Exact evidence

[verify.py](verify.py) is a new standard-library implementation.
[RESULT.json](RESULT.json) is generated by replay and binds all five source
and metadata files by SHA256. It records:

- The two exact price duals and their equality cases, all seven rank-count
  partitions of six with parts at most three, and all ten a/b order patterns
  with three a calls and two b calls.
- All 3,840 choices of nonzero two-by-two N and arbitrary L,M, with R=L+M,
  evaluated in the full formal group algebra. Their mixed coefficients equal
  MN and NM in every case. Sixteen choices give the full two-target endpoint.
  These are cut-identity fixtures, not a census of three-target words.
- Thirty-six complete endpoint fixtures on three through six roles. Eight
  are the two orientations of the optimal word. Twenty-eight are six-call
  rank-two comparison words under seven target-basis frames. A separate
  literal three-by-three address-matrix implementation checks all 1,296
  faithful regular-action basis columns, including every dirty spectator.
- Thirty-two deleted-call controls and three semantic controls reject:
  a changed dirty spectator, a nonzero formal perturbation invisible to the
  quotient, and an unrestored first-order coefficient. The quotient-kernel
  perturbation is a diagnostic operator, not an asserted paid word.

The all-workspace lower bound is the written proof. Finite tests corroborate
its equations and the attaining boundary; they do not replace it. No previous
contributor's reported count is rechecked as this package's deliverable.

## Reproduction

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut3-asymmetric-monotone-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ut3-asymmetric-monotone-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ut3-asymmetric-monotone-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ut3-asymmetric-monotone-gap --check-source-history
```

Elsewhere replace the interpreter path with CPython 3.12. The direct marker is
`PASS_UT3_ASYMMETRIC_MONOTONE_GAP separate=53 exact=54 no_new_kappa`.
Normal replay writes nothing. `verify.py --emit` prints a freshly computed
receipt to standard output. Both registered commands have 120-second limits.

## Scope, sources and credit

Scientific base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`,
priority revision 8, selected conditional kappa .00310045. The selected
source-binding orientation passes; it is not a scientific replay.
[SOURCES.json](SOURCES.json) pins the exact predecessor READMEs, selected
record and catalogue as historical provenance. There are no live external
inputs. [TASK.json](TASK.json) records the changed card scope and structured
next questions. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213517)
names this exact pricing question.

Credit Arham Tahir #1919 for the rank-capped alphabet, rank-volume lemma and
nonlinear-pricing question; Nick Petalas #2129 for asymmetric concave pricing
and #4846 for common monotone pricing and the explicit open question; and
steph4n-gh #1573, Arham Tahir #1589, Hanson Sun #1607 and Josie Elliston #1792
for the retained coefficient-span and model lineage. Retain juper997 #1478,
woklerx #1443, Gareth Davidson / bitplane #1333 and their credited predecessors.
Their files and credit lines are unchanged.

Entry overlap included 405 open PRs and 5,286 Discussion records with complete
remote pagination. Sparse local coverage was incomplete. Separate all-main
README searches, merged PR searches and the relevant UT3 pricing PR bodies
found the explicit unresolved question but no delivered asymmetric monotone
gap. Arbitrary nested files, unindexed literature and unpublished work are
outside that coverage; global literature priority is unclaimed.

Physical scalar mixing, native address implementation, recursive-child rank
identification, hosting, precision/tape costs, compiler admission and analytic
transfer are outside scope. No selected cold replay, Lean or Docker run was
performed. The selected frontier is unchanged.

## Open next questions

Can one characterize when separate monotone partition minima are compatible?
Start with exactly two b calls and classify a-rank partitions that can supply
rank three on both sides of the interval cut. This would improve interface
pricing, but the cut alone need not suffice for arbitrary noncommuting words.

Can a native complete UT3 interface realize useful asymmetric prices? First
specify one literal producer/consumer pair and charge scalar mixing, frames,
preparation, dirty restoration, hosting and precision. Physical realization
and the interpretation of scalar rank as recursive child rank are missing.

## Implementation bounds

The verifier has no recursion, subprocesses, network access or write path.
Formal matrices have at most six roles and eight group coefficients per cell;
words have at most sixteen factors. The cut sweep has exactly 3,840 cases,
the partition scan has 343 count vectors, and kernel scanning has 255 masks.
The literal check covers at most 48 basis inputs per fixture. Source and
receipt reads reject files exceeding 128 KiB. Every function is below sixty
physical lines. Exceptions keep all checks active under optimized Python.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates bounded
lists, tuples and integers during replay; allocator internals are not
instrumented and no allocation-free execution is claimed. Raw-pointer and
preprocessor restrictions have no direct Python equivalent. Calls are direct
apart from fixed standard-library iteration and JSON serialization. Warning-
strict normal and optimized replay plus AST/function-length inspection are
the available diagnostics; no separate static type checker is configured.
