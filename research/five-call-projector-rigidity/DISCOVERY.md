# Discovery record and limits

All searches in this record are author-side work. No entry gives a new
kappa. Only the exact proofs and registered replay support the exclusions
in PROOF.md. A small residual, a timeout or a finite-prime failure is not
a characteristic-zero endpoint proof.

## Exact all-full discovery

`discovery.py` and `search.cpp` enumerate the complete compatible interior
rank-two projectors for the canonical four-field query tuple. There are
p^4 projectors at each of three interior sites. Over F3 the complete domain
has 531441 triples; over F5 it has 244140625. Both searches return zero
query survivors. The compact receipts are in `discovery-results/finite-*`.
These finite results motivated the symbolic proof; they do not establish
it by reduction modulo a prime.

```sh
python3 discovery.py --prime 3 --output /tmp/projectors-f3.txt
c++ -std=c++17 -O3 -Wall -Wextra -Werror search.cpp -o /tmp/projector-search
/tmp/projector-search < /tmp/projectors-f3.txt
```

Replace 3 by 5 for the second domain. The finite search is not required
by the registered proof replay.

`symbolic_discovery.py` uses SymPy 1.14.0. It builds the full query polynomial,
solves its first coefficient, and finds the unit ideal. The short identity
in PROOF.md replaces reliance on an opaque Groebner calculation. The saved
four-field chart records its original parameter convention.

`general_tangent.py` and `second_order_reduce.py` use tail-conjugated
projectors. The first coefficient leaves 16 parameters for n=6 and 36 for
n=8. Repeated exact quadratic row reduction gives a contradiction in each
case. Compact step transcripts are retained. The registered replay rebuilds
the system with direct chronological multiplication and a different
elimination order; it does not load these transcripts.

Typical discovery commands are:

```sh
python3 general_tangent.py --n 8 --output /tmp/chart-n8.json
python3 second_order_reduce.py --chart /tmp/chart-n8.json --output /tmp/quadratic-n8.json
```

Run these from this package directory in an environment with SymPy1.14.0.
They are discovery tools, not registered replay dependencies.

## Alternating thin queries and saved histories

The first feasible interior thin sites are {2}, {2,4} and {2,4,6} for
n=4,6,8. The registered replay derives the rational projectors and checks
every coefficient of the query identity. With the natural end projectors,
the stage word has a nonzero nilpotent defect at z=2. Thus its stage powers
cannot be read as independent Gaussian targets.

`history_discovery.py` then grants an ordinary saved copy of every field
after every completed call, including the original input. It uses exact
rational row reduction to test whether a constant combination gives a
pure S z^e row. On the six-field natural endpoint, degree two has dimension
two. The other degrees from zero through five have dimension zero. The
two returned input rows are (1,1,0,0,0,0) and (0,0,0,0,0,1). This does not
complete six independent Gaussian targets. The test includes arbitrary
ordinary combinations of the original inputs and covers only this fixed
prefix history and endpoint choice.

Correction after the first publication: the earlier discovery script used
coefficients of w=z-1 but tested a single coefficient as if it were z^e.
It therefore tested S (z-1)^e, and its all-zero result did not exclude
S z^e. The corrected script uses coefficients of z throughout and has a
control that a full stage on the entire space is exactly z I. This error
was in the unregistered history screen. It did not affect PROOF.md,
PERIOD.md or the registered exact replay.

The six-field history receipt and rational projectors are saved. The same
elimination used in `verify.alternating` rebuilds those projectors.
No target credit is given to saved copies, since they are correlated work.

```sh
python3 history_discovery.py --projectors discovery-results/alternating-n6.json \
  --output /tmp/six-field-history.json
```

## Numerical tests that did not give a construction

The first-coefficient chart was also searched with SciPy1.18.1 and
NumPy2.5.4, using analytic derivatives checked by finite differences.
Twenty-four complex six-field trials gave no endpoint. The exact algebraic
proof supersedes this negative numerical evidence.

The finite-order test uses n=8, U^7=I and a cyclic scalar query frame.
If C sends u_i to u_(i+1), its last column is u_n and C^(n+1)=-I.
The search imposes P_i=C^i P_0 C^(-i), with the complete rank-two chart
for P_0. This is a restricted family; the complete finite-order question
allows unrelated projectors at the different sites.

```sh
OPENBLAS_NUM_THREADS=1 python3 cyclic_discovery.py \
  --n 8 --period 7 --trials 12 --steps 300 \
  --seed 6201 --output /tmp/cyclic-nine-seven.json
```

The twelve trials did not reach an endpoint. The best residual norm was
about19.3352 and its largest entry was about2.7982. The complete compact
receipt is saved. This is not a finite-domain exclusion. A candidate would
still need exact coefficient arithmetic modulo z^7-1, target normalizers,
native phases and all-column source routing before its price could be used.

The later theorem in PERIOD.md excludes this period-seven scope without a
numerical search. The short-interval coefficient test alone was unresolved;
the two-corner Gram determinant proves the missing implication.

Period six remains outside that theorem. The same cyclic frame was searched
for 24 trials with 500 steps. A larger test then solved every short-interval
first-coefficient constraint and searched its 41 complex parameters, without
the cyclic-frame restriction. Its 24 trials used at most 800 evaluations
each. The best norm was about6.79944, with maximum entry about0.797768.
These tests did not find an endpoint. Neither is an exact exclusion.

The complete larger input chart and both receipts are saved. To repeat the
larger discovery run from this directory:

```sh
OPENBLAS_NUM_THREADS=1 python3 tangent_search.py \
  --chart discovery-results/interval-chart-n8-p6.json \
  --trials 24 --steps 800 --output /tmp/general-n8-p6.json
```

Changing both boundary projectors of the six-field alternating construction
also did not produce a numerical monomial endpoint in 24 trials. That test
uses z W'(z)=W'(1) W(z), rather than a presumed eigenvalue count. Its receipt
and `boundary_discovery.py` are retained. A separate signed-stage second-order
test is unresolved; it is not counted among the proved exclusions.

## Changed ordinary-output and dirty-return contracts

`mixed_target_discovery.py` tests q full calls on q fields, with q-1
central-query targets and one independent ordinary target. Every proposed
stage power is two. Its query tuple extends the canonical (q-1)-field tuple
by either a zero or a common nonzero input column. This is a tested family,
not a classification of all mixed-target query tuples.

The complete optimistic PR5599 tariff is favorable at .0034 for q=7 and
q=9. However, both q=7 extension charts fail the exact first coefficient.
The q=9 nonzero-extension chart fails there too. These are local exact
algebraic screens with saved receipts. They are not part of the registered
84-domain theorem and have not received a separate implementation check.

`dirty_target_discovery.py` instead returns that last arbitrary input through
the identity and permits two degree-three central targets, with the other
central targets of degree two. On q=7 the nonzero-extension chart fails
the first coefficient. The zero-extension chart fails the second coefficient
together with the rank-two target projector equation. These records do not
exclude initialized work whose output may be discarded, more work fields,
other target powers or other query tuples.

```sh
python3 mixed_target_discovery.py --q 7 --coupling 0 --output /tmp/mixed-q7.json
python3 dirty_target_discovery.py --q 7 --coupling 0 --output /tmp/dirty-q7.json
```

Every ordinary target here is an independent input. A returned identity
field earns no Gaussian credit. No screen establishes a source-bound caller,
native implementation or kappa gain.

## Border comparison

The natural alternating endpoint has the desired diagonal eigenvalues but
nonzero coupling terms. A singular scalar conjugation is therefore a
possible border question. This is not a new conversion argument: Dillon's
`controller-border-interface` already separates the formal constant term,
losing direct interpolation, and the missing chronological product theorem.
Yiyang's `bounded-lane-border-core` gives a fixed-grade inverse-pair core
and root-only Walsh extraction under an explicit coherent native boundary.

An ordinary tensor power of a polynomial matrix does not establish the
degree or grade bounds for the repository's chronological supplier product.
This package supplies no missing recursive coherence, precision or native
boundary proof. It does not count border eigenvalues as productive targets.
