# Exact full-Pauli paid-history minimum for arbitrary targets

This contribution was produced by Nick Petalas. Apache-2.0.

JoyboyBrian's [PR #5482](https://github.com/CrocSwap/integer-mult-bounds/pull/5482)
proves that, in its phase-complete Pauli history model, q owners with
targets `(aI+bX)^tensor f` need q paid returns at every width f>=2. It
states that it "does not classify arbitrary Pauli-nonordinary matrices."
This package answers that question for the model's history count.

**Theorem 1 (scoped proof).** For arbitrary targets H_j on distinct owners,
the least number of returned rows is exactly

* even f: the largest number of owners whose target is nonordinary in one
  common character of the commutative algebra `R=span{I,P,C,PC}`;
* odd f: `ceil(sum_j s_j / 2)`, where `R` is isomorphic to `M_2(K)` and
  `s_j = (dim(R+R H_j)-4)/2` is in {0,1,2}.

The lower bound holds for every program in the #5482 model. Explicit
returned rows attain it.

So the per-owner count q is not a floor for general nonordinary targets:

* **Every tensor square (f=2).** The profile of `M tensor M` is the set of
  forms B in {I,X,Z} with `M^T B M` not proportional to B. For M not a
  scalar multiple of a Pauli, it has two or three members. The minimum is
  at least `ceil(2q/3)`, and this is sharp. Owners with targets
  `(2I+X)^tensor 2`, `(2I+Y)^tensor 2` and `(2I+Z)^tensor 2` need **two**
  returns, not three.
* **Every rank-one tensor power (f>=3).** For `M=u w^T`, the odd-width excess
  is 1 if u is an eigenvector of X, Z or XZ, and 2 otherwise. Two such
  owners, for example `E11^tensor 3` twice, share **one** return. At even
  widths the profile has four characters, or two for Pauli eigenvectors;
  [PROOF.md](PROOF.md) tabulates them by f mod 4. These profiles force q
  when f = 0 mod 4 and allow `ceil(2q/3)` when f = 2 mod 4.

At even width the count q is forced exactly when one character is shared
by every owner. At odd width it is forced exactly when at most one owner
has excess 1 and none has excess 0. The #5482 family satisfies both
conditions, consistent with that result.

No κ, physical paid-call count or selected-frontier change is claimed.

## Reproduce

From the repository root, with CPython 3.12 (standard library only):

```sh
python3.12 -B scripts/research_package.py --package research/pauli-history-arbitrary-targets
python3.12 -W error -B research/pauli-history-arbitrary-targets/verify.py
python3.12 -O -W error -B research/pauli-history-arbitrary-targets/verify.py
```

Each verifier run takes about two seconds and prints a JSON receipt with
`PASS_PAULI_HISTORY_ARBITRARY_TARGETS` and SHA-256 hashes of the package
files. It checks the cited proof's hash and uses exact Q(i) arithmetic:

* The algebra identities at widths 1 to 5.
* Eleven target instances at widths 2 to 5. For each, the formula value,
  explicit attaining returns, exact membership of every target in the
  history module, and failure after dropping one return.
* All 625 width-two matrices with entries in {0,±1,±i}. The character
  profile equals the form profile (1), the singlet never occurs, and
  non-Pauli profiles have two or three characters. Size counts are
  17, 192 and 416 for sizes 0, 2 and 3.
* 48 vectors u at widths 3 to 9: dim RU is 2 exactly for the 30 Pauli
  eigenvectors.
* The even-width rank-one profile table at widths 4, 6 and 8.
* Five rejection controls.

The finite checks corroborate the written all-width proof. They do not
replace it.

## Limitations

The minimum counts returned rows in the #5482 history model. Its lower bound
applies to every program in that model. The attaining rows are explicit, but
this package does not show that a native operator applied to one current
field produces them. Invertible non-Pauli tensor powers at widths at least
three are not classified. The verifier observes full invariants there only
for finitely many tested matrices.

## Open next questions

1. **Invertible targets at f>=3.** Does every invertible `M` outside
   `K{I,X,Z,XZ}` have excess 2 at odd f>=3 and all four characters at even
   f>=4? If so, the q-call count of #5482 extends to all invertible
   nonordinary tensor powers. First step: the condition `r M^tensor f in R`
   is a linear relation among the eight tensor powers of `σM` and `σ`;
   handle the low widths 3 to 6, where the tensor-power lemma alone is too
   weak.
2. **Operator realizability of sharing.** Can two paid calls, each a fixed
   linear operator applied to one current field, deliver the three width-two
   X/Y/Z-type targets? A positive answer turns the history sharing into a
   program. A negative answer gives a stronger operator-call floor than
   Theorem 1.
3. **Physical caller.** A cached physical boundary must still bind its actual
   observation module and complete paid bill before either count is charged.

## Credit

JoyboyBrian (PR #5482) supplies the model, the history-module inclusion and
the q-call theorem for `(aI+bX)^tensor f`. That package's credits carry
over: Chris R / Clear1nsight, the PR5425/PR5446 history authors and Ali
Romman's PR5450. Theorem 1, the two classifications and the sharing
constructions are new here. The algebra is classical.
