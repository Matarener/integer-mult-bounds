# Finite q-Toeplitz factorization

## Question

For `0 < q <= 1/4`, does the lower-triangular Toeplitz factorization reproduce the Gaussian matrix `G_ij = q^{(i-j)^2}` and its inverse?

## Result

Set `f_0 = 1` and `f_j = prod_{k=1}^j (1-q^{2k})`. The sequences `g_j = q^{j^2}/f_j` and `h_j = (-q)^j/f_j` satisfy `T(g) T(h) = I`, where `T` is the lower-triangular Toeplitz matrix. With `D_f = diag(f)`,

```
G = L D_f L^T,    L = D_f T(g) D_f^{-1},
G^{-1} = D_f^{-1} T(h)^T D_f T(h) D_f^{-1}.
```

This holds for all 30 matrices with `q` in `{1/4, 1/5, 1/6, 1/8, 1/10}` and order 1 through 6. At `q = 1/4` the geometric tail is `1/15`, so the elementary product bound is `14/15`, and `(15/14)/(1-q) = 10/7`. Every checked `f_j` lies in `[14/15, 1]`, and every checked row sum of `T(h)` is at most `10/7`. The selected κ is unchanged.

## Boundary

This checks the finite factorization and these two rational bounds. It does not run the Gaussian core or the chirp consumer. The stop rule is to record this factorization.

## Reproduce

```bash
python3.12 -B research/q-toeplitz-factorization/verify.py
python3.12 -B research/q-toeplitz-factorization/test_verify.py
```

## Open next questions

None. The finite factorization and the two rational bounds are settled on this range. The Gaussian core would leave this package.

## Credit

Chafik Boukhalfa recorded the factorization in PR #489, citing Alexey Kuznetsov. Jose Manuel (`jmbarrancoml`) retained it in PR #3851. The checker recomputes the matrices. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
