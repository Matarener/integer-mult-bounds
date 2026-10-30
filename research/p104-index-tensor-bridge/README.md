# Index-to-tensor bridge for the scalar P104 code

**Audit of one published convention. No new κ.** Selected κ stays
`0.001672660197076918`.

PR #3996 checks 763,392 literal events and, separately, the block algebra of
`U`. Its proof states the bridge between them and does not execute that
bridge. This package executes it.

## Scope and evidence

The index in that proof is

```text
index(bank, i, j) = (bank*104 + i)*104 + j
```

Axis 0 varies `i` at fixed `j`. Axis 1 varies `j` at fixed `i`. On every
coefficient of widths 2 and 8, and on one dense width-104 state:

- broadcasting a one-axis map `K` along axis 0 is `K tensor I` (left multiplication);
- broadcasting it along axis 1 is `I tensor K`, which right-multiplies by `K^t`.

The second identity fails if the column fiber is implemented as right
multiplication by `K`. The four sweeps `U`, `U^{-1}`, `U^t` and `U^{-t}` of
the canonical code are checked in that form. The four shears are the block
maps with factors `A` and `M`: lower/upper `A` use axis 0 and axis 1 of `A`,
and the coded Gram shears use `M = U U^t`.

On the canonical fixture
`research/p104-native-channel/inputs/P104-FIXTURE.json`
(SHA256 `516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4`),
an independent root enumeration rebuilds the 768 signed-half entries. Their
ASCII digest is
`88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535`,
the same digest PR #3996 binds. For this `U`:

- `A = U^t P U` satisfies `A^2 = 13 A`, and `(I-A)` has an exhibited rational inverse;
- `M = U U^t` is invertible, and `M` is not `U^t U`;
- the bank block `P tensor (M - U^t U)` has Frobenius square **18432**;
- `N - P = U^{-t}(I-A)U^{-1}` is invertible, so each omitted side
  `(N-P) tensor M` and `M tensor (N-P)` has rational rank **10816**.

The contraction identity
`||sum c_k A_k tensor B_k||_F^2 = sum c_k c_l <A_k, A_l> <B_k, B_l>`
was checked against the dense Kronecker matrix at widths 2 and 3, including
a nonzero sample. The width-104 gap uses that identity. Both factors of an
omitted side have exhibited inverses. The identity
`(A tensor B)(A^{-1} tensor B^{-1}) = I` was checked on a 2-by-2 pair. At
width 104 it is the same entrywise rule, not a stored 10816-square product.
That is the rank step.

This does **not** replay the 763,392 events, localize a fiber of PR #3979, or
supply a physical consumer. Algebraic rank is not a native-call price. No
supplier is admitted.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/p104-index-tensor-bridge/verify.py
python3.12 -B research/p104-index-tensor-bridge/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-index-tensor-bridge
```

Expected markers:

```text
PASS_P104_INDEX_TENSOR_BRIDGE
PASS_P104_INDEX_TENSOR_BRIDGE_TESTS
```

The tests reject a column convention that drops the transpose, and they reject
a one-entry change to `B2`.

## Open next questions

1. One frozen encoder fiber from PR #3996 should be compared with axis 0 of
   `U`, without calling that package's checker. The word bytes are on head
   `b8dd4e04bf8490aca121abc7ba0e503651db6c97`, not on this main checkout.
2. A repeated physical consumer still has to pay `(N-P) tensor M` or show a
   different interface. Rank 10816 says the Gram shear is not that payment.

## Credit

The code, the index sentence, and the rank claim under audit are Chris R /
Clear1nsight's PR #3979, audited by ToikY in PR #3996. The fixture and root
normalization come from the retained P104 native channel (Rohan Arun, Chafik
Boukhalfa, Adam Gall, and the native/E8 lineage named there). This package
does not import either checker's source.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review is claimed.
