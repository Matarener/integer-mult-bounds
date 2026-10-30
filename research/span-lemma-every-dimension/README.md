# Frame span m+1 cannot save a call in any address dimension

In the abelian scalar-idempotent register model with `m x m` rational
frames and `W` registers, a paid-frame span of dimension at most `m + 1`
forces at least **`mW` calls** for invertible lower-triangular targets.
This holds for every `m`. PR #468 proves it only at `m = 3` (its span-four
lemma, nine calls for three registers). The direct word attains `mW`.

After normalizing the span to `diag + t·uv^T`, set
`K = supp(u) ∩ supp(v)`. The lower-triangular hypothesis is needed only
when `|K| = 2`:

| Case | Argument | Targets |
| --- | --- | --- |
| span `<= m` | PR #468 low-span lemma | any invertible |
| `|K| >= 3` | new: rank-one frames lie on `m + 1` lines | any invertible |
| `|K| <= 1` | new reduction: span is triangular after a permutation | any invertible |
| `|K| = 2` | PR #468 block flag argument, cited | lower triangular |

The key step is a 2×2 minor identity. For distinct `i, k, l`, the minor of
`D + tB` on rows `{i,k}` and columns `{i,l}` is `D_ii t u_k v_l`. With
`|K| >= 3`, each `i` has such `k, l` in `K`, so every rank-one element of
the span lies on a basis line. PR #468 needs full support of `u, v` for
this step. In dimension four or more, that misses frames with zero
coordinates whose diagonal blocks have size above two.

**Claim type:** a scoped written proof with an exact finite check of its
combinatorial step. No construction, native conversion, supplier change
or new κ. The selected frontier is unchanged.

[PROOF.md](PROOF.md) has the model, theorem, proof and scope.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3.12 -I -W error -B research/span-lemma-every-dimension/verify.py
python3.12 -I -O -W error -B research/span-lemma-every-dimension/verify.py
```

Both print `PASS_SPAN_LEMMA_EVERY_DIMENSION` in under a second. The
verifier checks the support classification for all nonempty support pairs
with `m <= 7`. It checks the minor identity as a polynomial identity. It
runs an exact rank-one grid at `m = 3, 4, 5` (434,845 matrices, zero
off-line rank-one elements). It also runs two controls, including an
explicit off-line rank-one element at `|K| = 2`.

## Limitations

- The `|K| = 2` case cites PR #468's block flag argument and its
  lower-triangular target hypothesis. That argument is not rechecked here.
- Span `m + 2` or more, extra clean or dirty registers, free address maps
  between paid calls and nonabelian models are not covered.
- The finite grid is a control. The theorem rests on the written proof.

## Open next questions

1. Does `|K| = 2` still force `mW` calls for non-triangular invertible
   targets? Start at `m = 2` with full-support `u, v`, where off-line
   rank-one frames exist.
2. Does span `m + 2` force `mW` calls for `m >= 4`? Normalize to
   `diag + span{B, B'}` and classify the joint support graph of the two
   extra frames.
3. Do clean or dirty extra registers change the span-`(m+1)` bound? Check
   whether the line projection of Lemma A survives identity helper targets.

## Sources and credit

The proof and verifier were produced by Nick Petalas. Apache-2.0.
The model is eumemic's PR #288, section 1.2. The low-span lemma,
span-four lemma at `m = 3`, projection tools and block flag argument are
Ali Romman's [PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468)
(`research/bit-three-register-lower-bound`). The common triangular-flag
obstruction is huxint's [PR #203](https://github.com/CrocSwap/integer-mult-bounds/pull/203).
The new parts are the `|K| >= 3` line lemma in general dimension, the
`|K| <= 1` triangular reduction after normalization, and their assembly
into the all-dimension statement.

[SOURCES.json](SOURCES.json) pins the input bytes at canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226223)
records the scope. Main-tree, merged-PR and open-PR searches found no
general-dimension span-`(m+1)` lemma. This is search coverage, not a
guarantee about unpublished work.
