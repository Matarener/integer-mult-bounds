# Eigenvalues of this section's Q lie strictly inside (0, 1 - p^{-40})

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the normalized Schur
section `H` on `0,1,2,7,8,9` satisfies `||H||_2 < 1226/625` and
`||H^{-1}||_2 < 319/100`. For `Q = I - p^{-20} H* H`,

- `p^{-20} (1226/625)^2 < 1`, so every eigenvalue is strictly greater than 0;
- `p^{-20} (100/319)^2 > p^{-40}`, so every eigenvalue is strictly less than
  `1 - p^{-40}`.

Those eigenvalues therefore lie in `[0, 1 - p^{-40}]`. No new kappa is
claimed. The selected record is unchanged. This is one normalized section,
not the note's all-size eigenvalue statement. The matrix `Q` is not formed.

## The two comparisons

`FINE-PRIME.md` puts the eigenvalues of `Q = I - p^{-20} H* H` in
`[0, 1-p^{-40}]` when both 2-norms are at most `p^10`. The preceding audit
bounds every absolute row sum and column sum of this section by
`1226/625`, and the inverse 2-norm by `319/100`. Squared singular values
then lie strictly between `(100/319)^2` and `(1226/625)^2`. Dividing by
`19^{20}` puts `1 - p^{-20} sigma^2` strictly between 0 and
`1 - 19^{-40}`. The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-q-eigenvalues/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-q-eigenvalues
```

The verifier authenticates the pinned notes and checks the two power
comparisons.

## Open next questions

The next sentence of the fine-prime note bounds the tail of
`p^{-20} sum_{j<J} Q^j H*` by `p^{10} exp(-p^2)` at `J=ceil(p^{42})`.
Nothing here estimates that series.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
comparison of the matrix 2-norm with `1226/625` and `19^{10}` is the
preceding audit. These eigenvalue comparisons are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
