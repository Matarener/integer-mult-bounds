# Halve the complex sparse-feedback update coefficient

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. The new
all-complex inequality is

```text
h(z) = -z log_2|z|, h(0)=0,
|h(p)+h(q)-h(p+q)| <= |p|+|q|.
```

The constant one is sharp. Apart from the zero pair, equality holds exactly
when `p=q != 0`. The proof covers cancellation, arbitrary complex phases
and every magnitude. It is self-contained in [PROOF.md](PROOF.md).

Applied to Chris R / Clear1nsight's [PR #4036](https://github.com/CrocSwap/integer-mult-bounds/pull/4036)
sparse-feedback contract, the lemma strengthens its necessary conditions to

```text
4 sum_t K_t + Re(Delta_Q) >= lambda f V,
4 K S       + Re(Delta_Q) >= lambda f V.
```

At `lambda=1/2`, the source's child-first zero-jump class therefore needs
`S >= fV/(8K)`, twice its stated `fV/(16K)` bound. The predecessor's
preconditioner, endpoint value, auxiliary reduction and native-cut accounting
are cited premises. No predecessor verifier or fixture is imported or replayed.
This package proves the new scalar step and derives its stronger consequence.
Optimality of the circuit coefficient four is not claimed.

`S` charges every updated scalar coordinate. `K` bounds every full formal
machine prefix condition number, including masked-operation internal cuts.
`Delta_Q` is the actual jump across the sole native call. Its zero value
requires the cited child-first, payload-preserving monomial premise.
The source allows arbitrary restored dirty auxiliaries and returned clean
auxiliaries. All its remaining boundary and linear-operation hypotheses apply.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-complex-entropy-defect/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sharp-complex-entropy-defect/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-complex-entropy-defect
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-complex-entropy-defect --check-source-history
```

Another CPython 3.12 executable may replace the absolute interpreter path.
The direct verifier is read-only and Git-free. It prints
`PASS_SHARP_COMPLEX_ENTROPY_DEFECT scalar_constant=1 update_coefficient=4`
and a generated receipt containing all six package-file SHA256 hashes.
The receipt records checked bytes; it is not a proof-kernel certificate.

The complete finite grid has 2,401 ordered pairs of Gaussian integers with
real and imaginary parts in `[-3,3]`. It checks all 48 nonzero equality
cases and strictness of every other nonzero-input pair. Logarithms use exact
rational enclosures from 48 terms of the atanh series with its explicit
geometric tail. Square roots use 192-bit rational enclosures. A separate
branch checks 161 dyadic-norm pairs with exact logarithm identities and
squared rational comparisons. The checker also covers 100 scaled rational
complex pairs, 192 columns from 64 new complex mixing fixtures, six semantic
controls and six rejected input-domain cases. These fixtures belong to this
new lemma; they are not a replay of #4036's endpoint evidence.

The universal result rests on the written proof. Finite enumeration alone
does not prove it. `SOURCES.json` pins the predecessor proof/README and the
original revision-8 card as historical provenance. The standalone checker
has no live external input, network dependency or third-party dependency.

## Scope, credit and verification limits

Credit Chris R / Clear1nsight #4036 for its coupling potential and boundary
argument; #4009/#3989, Gonzalo Mier #3975 and their retained Pauli/native
lineage for the coupled boundary; and Nir Ailon and Gal Yehuda for the
classical preconditioned quasi-entropy method. Elementary calculus and binary
entropy are classical. No literature-wide priority is claimed. The new step
is the sharp complex defect, its equality classification and this stronger
source-relative bound.

This package does not supply a native word, supplier admission or a new
kappa. General interleaving retains `Delta_Q`; unbounded conditioning remains
outside the zero-jump obstruction. Complete physical routing, precision,
stock, compiler and outer multiplication obligations remain unrun.
Independent human and formal proof-kernel review are unclaimed. The selected
frontier remains unchanged.

The checker has no recursion or unbounded loop. It fixes all enumeration domains,
caps logarithm input numerators/denominators at 256 bits and the cache at
4,096 entries, and caps each of six receipt files at 128 KiB. Functions fit
within 29 physical lines. Python and Fraction allocate dynamically, so fixed
post-initialization storage is a documented managed-runtime deviation. The
domain bounds limit live data; no allocation instrumentation is claimed.
The six invalid-input control calls use a fixed tuple of known functions.
Warning-strict normal/optimized runs and AST inspection are the local
diagnostics. No repository-wide static analysis or historical suite is claimed.

## Open next questions

1. Can the matrix update coefficient four be reduced by using joint constraints
   on the old/new pair products? Its scalar constituent is sharp, but the
   two triangle bounds and four row-norm bounds need not be jointly tight.
   Start with a single invertible two-row matrix and its inverse-dual image.
   A universal matrix bound or attaining family is missing.
2. Can a named interleaved native caller exploit the sharper accounting?
   First compute its actual pre/post-native potential and complete paid
   arithmetic volume. Its jump, conditioning, precision and physical bill
   must be supplied before any supplier conclusion.

Structured first steps and blockers are in [TASK.json](TASK.json).
