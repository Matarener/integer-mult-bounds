# Sharp denominator and precision for the central Gaussian bulk

This scoped mathematical proof makes the degree-R denominator upper bound in
David Ganz's [PR #5813](https://github.com/CrocSwap/integer-mult-bounds/pull/5813)
sharp. It also proves the matching worst-case numerator-precision requirement.
The result concerns the full ordinary bulk response, with unrestricted integral
inputs. It supplies no new κ, physical supplier or complete multiplication theorem.

This contribution was produced by Nick Petalas. Apache-2.0.

## Exact statement

Put π=1+i. For integers n>=1, 0<=R<=n and 0<=a<=n-R, let X_j flip bit j
of the 2^n coordinate labels, W=(nI-sum_j X_j)/2, and

```text
g(z) = i^a sum_(h=0)^R (i-1)^h binom(z-a,h),     B = g(W).
```

The source construction agrees with the normalized Gaussian tensor on Walsh
weights a through a+R. Its constructive numerator grid is π^R B. The new conclusions are:

1. In the unique convolution expansion B=sum_S c_S X_S, every |S|=R has
   exactly c_S=i^a/π^R, and c_S=0 for |S|>R. Hence the least nonnegative
   integer d with π^d B Gaussian-integral is exactly R.
2. B is the only permutation-symmetric convolution supported on displacements
   of Hamming weight at most R that has the prescribed central-band response.
   Therefore a different formula within that class cannot lower this grid debt.
3. For every p>=1, the integral numerator G=π^R B must in general be known
   modulo π^(p+R) to recover Bx modulo π^p. One fewer numerator digit fails
   for an explicit pair of integral inputs. Every individual output coordinate
   has such a witness. Likewise x modulo π^(p+R) suffices, and x modulo
   π^(p+R-1) does not suffice for arbitrary integral x.

Fractional-output congruence means equality in Q(i)/π^p Z[i]. The precision
claim concerns the quotient contract, not an instruction count or every possible
algorithm that may have other information about x.

## Proof

The 2^n matrices X_S are linearly independent: applying them to the coordinate
vector e_0 gives the distinct vectors e_S. Thus convolution coefficients are
literal matrix entries, not coefficients that could cancel under a relation.

For R>0 the leading coefficient of g is i^a(i-1)^R/R!. A product W^h has
no displacement of weight greater than h. To obtain displacement S of weight R
in W^R, all R factors must choose its distinct bit flips; there are R! orders.
Consequently

```text
c_S = [i^a(i-1)^R/R!] [R! (-1/2)^R]
    = i^a [(1-i)/2]^R
    = i^a/π^R.
```

The same formula at R=0 is B=i^a I. Since i^a is a Gaussian unit, π^(R-1)B
is not integral when R>0. Ganz's constructive upper bound shows π^R B is
integral. For completeness, it follows from

```text
B = sum_(j=0)^R b_j E_j,
E_j = sum_(|S|=j) product_(k in S)(I-X_k),
b_j = i^a 2^(-j) sum_(h=j)^R (i-1)^h binom(-a,h-j).
```

Each E_j is integral. Every term in b_j has π-valuation h-2j>=-R and has
only a power of 2 in its denominator. This proves the matching upper bound,
including n=R and negative integer offsets in the binomial expression.
The upper construction and Newton identity remain credited to Ganz.

For uniqueness, a permutation-symmetric convolution of radius at most R is
H=sum_(d=0)^R t_d sum_(|S|=d)X_S. On a Walsh character of weight k its
eigenvalue is the polynomial

```text
h(k) = sum_(d=0)^R t_d K_d(k;n),
K_d(k;n) = sum_(j=0)^d (-1)^j binom(k,j) binom(n-k,d-j).
```

Here binomial coefficients are polynomials in k. The leading coefficient of
K_d is (-2)^d/d!: multiply the leading coefficients in each summand and use
sum_j 1/(j!(d-j)!)=2^d/d!. Thus these polynomials have distinct degrees
0 through R. The central-band conditions fix h on R+1 distinct integers.
Polynomial uniqueness gives h=g, and the Walsh basis then gives H=B.
This also excludes degree below R when R>0.

For precision, G has Gaussian-integer entries, and its entry at displacement S
of weight R is i^a. Fix any output coordinate t, choose such an S and put
s=t xor S. For any p>=1 take

```text
x_0 = 0,     x_1 = π^(p+R-1) e_s.
```

The inputs are congruent modulo π^(p+R-1). Their numerator responses Gx_0
and Gx_1 are also congruent at that modulus. But their B responses differ at
coordinate t by i^a π^(p-1), which is not divisible by π^p. This proves
both insufficiency claims with actual reachable numerator vectors. Conversely,
knowing Gx modulo π^(p+R) permits division by π^R at the required output
modulus. An input change divisible by π^(p+R) changes Bx by π^p times an
integral vector because π^R B is integral. This proves input sufficiency.
All statements include R=0 with S empty.

## Evidence and reproduction

The written proof covers every finite n and every stated band and precision.
The verifier provides finite exact corroboration, not a proof-kernel certificate.
It uses independent exact Walsh inversion and falling-factorial evaluation in
the Boolean group ring. It checks the top coefficient and its minimal grid,
complete literal small Walsh spectra, and indistinguishable-input precision
witnesses. Mutations remove or negate the top coefficient, add an illegal
higher-degree term or odd denominator, and truncate the coefficient list.
The fixed census covers 285 bands, 114,686 coefficients and 11,263 top
coefficients through n=10; 1,022 independently evaluated group-ring
coefficients through n=5; 350 literal Walsh eigenvalues through n=4;
and 75,768 reachable precision witnesses through n=8 with p=1,...,4.
There are sixteen boundary and semantic controls.
Invalid bands and nonintegral valuation inputs are rejected. Checks use explicit
exceptions and remain enabled under optimization.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/gaussian-bulk-sharp-denominator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-bulk-sharp-denominator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-bulk-sharp-denominator --check-source-history
```

CPython 3.12 and the standard library suffice. The first command emits its own
counts and SHA256 bindings to all five package files. It writes no files.
The registered commands run normal and optimized warning-strict modes.
Run times and outputs are retained outside the checkout until publication is
settled. No predecessor verifier, native replay, Lean or Docker run is required
or claimed. Hosted CI status is recorded in the PR body.

## Scope, sources and relation to open work

The question is a narrowed side result of the decoder card, not a complete
signed-invoice improvement. The card's first working metadata control passed.
Canonical main was de5ec2e7a6074068452f45b1a191b5c72832df4a, priority revision 8.
The selected κ remains .00310045, with all five inherited assumptions.

David Ganz's PR #5813 at af37059809ae41283142c6aeb217cc456852aff1 supplies
the explicit central spectral interpolation and R-unit constructive grid.
Its denominator-accounting question is the source of this refinement. The new
step is sharpness, uniqueness within the stated radius class, and reachable
precision witnesses. The source is
[gaussian-spectral-bridge.md at that head](https://github.com/CrocSwap/integer-mult-bounds/blob/af37059809ae41283142c6aeb217cc456852aff1/research/eth-gaussian-spectral-transport/gaussian-spectral-bridge.md).
It is cited rather than imported or replayed; this package is self-contained.
Classical Walsh diagonalization, Newton interpolation and Krawtchouk polynomials
retain their standard mathematical attribution.

- [PR #5815](https://github.com/CrocSwap/integer-mult-bounds/pull/5815), David Ganz,
  at f0fcda576df410dc15cd5b8183d4f74d284eba2b gives exceptional correction and
  mixed-precision constructions; this proof prices neither implementation.
- [PR #5825](https://github.com/CrocSwap/integer-mult-bounds/pull/5825), Ali Romman,
  at baea91d8c0044a0036006bdd3b4d7bce3d6cf783 gives a work lower bound for a
  specified standalone Newton-W graph. Here the denominator obstruction is
  independent of the realization graph, within the stated response class.
- [PR #5880](https://github.com/CrocSwap/integer-mult-bounds/pull/5880), Nick Petalas,
  studies reversible clean storage for the raw tensor endpoint. That different
  endpoint is not an input lemma or the target of this contribution.

Restricted input lattices, restricted observables, nonsymmetric operators and
higher-degree spectral replacements are outside the uniqueness obstruction.
Native normalization, correction delivery, storage, restoration, movement and
whole-caller cost remain separate obligations. No favorable physical budget is
inferred from this local result.

## Verifier bounds and diagnostics

All finite checks fix n<=10 before allocation, hence at most 1024 coefficients;
the independent group-ring evaluation fixes n<=5 and literal spectra n<=4.
Precision witnesses fix n<=8 and p<=4. Every function is shorter than 60 lines;
there is no recursion or dynamic code generation. Valuation division has an
explicit bound from the norm's bit length. Invalid inputs and corruptions fail
with ValueError, including under -O.

Power-of-ten rule 3 has a managed-runtime deviation: Python allocates exact
integer/Fraction objects during these bounded checks. The fixed dimensions,
precision and coefficient formulas bound live storage and integer size; no
input files, network reads or external subprocesses enter the mathematics.
Rule 9 has a bounded test-harness deviation: the rejection helper invokes only
the explicitly listed control closures, synchronously and without retained
state. These deviations apply only to this finite verifier. A future verifier
that accepts external ranges must impose equivalent resource limits before
allocation. Warning-strict normal and optimized execution are the available
Python diagnostics; no external linter or type-checker dependency is added.

## Open next questions

1. Allow Boolean degree above R while fixing the same central band. Can its
   extra Krawtchouk coefficients lower the denominator? Solve a small exact
   integrality system with one additional degree first. A physical benefit
   still requires a complete paid correction and caller bill.
2. Which actual consumed observable removes every coefficient attaining the
   R-unit denominator debt? Pin one provider response and multiply its exact
   observable by B. No such physical consumer is supplied here.

The structured versions are in TASK.json. These questions change hypotheses
of the proved obstruction and are not claims of a funded continuation.
