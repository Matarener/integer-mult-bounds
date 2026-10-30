# One encoder fiber is axis 0 of U

## Statement

Let `B` be the `8×96` integer matrix rebuilt from the canonical P104 fixture
`research/p104-native-channel/inputs/P104-FIXTURE.json` (SHA256
`516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4`), with the
pivot order `(0,1,3,6,22,31,93,103)` and the same root removal as PR #3979.
Its ASCII JSON digest is
`88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535`, and it has
384 entries in `{-1,0,1}`.

Let `U` be the `104×104` matrix

```text
U = [[I_8, B/2], [0, I_96]]
```

over `Q`. Axis 0 varies the row index `i` at a fixed column `j`. On one bank,
that is left multiplication by `U` on each column, the factor `U ⊗ I` in the
row-major layout `index = (bank*104 + i)*104 + j`.

Let `W` be the encoder word `code_word(B)` emitted by the frozen builder at
`frozen/word_builder.py`, SHA256
`27bae82fe247fe49b8fc3b5efbd429e2c8c0ee8f56cc4ace748cbb681a5abacc`. Those are
the bytes PR #3996 vendors from PR #3979. This note does not call PR #3996's
checker.

## Program

The axis-0 program on bank `0`, column `0`, is:

1. Halve rows `8..103`.
2. For each nonzero `B[r][c]`, add that unit into row `r` from row `8+c`.
3. Double rows `8..103`.

After step 1 the tail is `x_tail/2`. Step 2 adds `B x_tail/2` into the pivot
block. Step 3 restores the tail. The net map is `pivot ↦ pivot + (B/2) tail`
and `tail ↦ tail`, which is multiplication by `U`.

## Word bytes

`W` contains this 576-event program exactly once, as the contiguous slice
starting at event `41600`. The slice's own indices all lie on bank `0` and
column `0`. Interpreting those events on the 104 row coordinates reproduces
`U` exactly, and the same map is not `U^{-1}`, `U^t`, or `U^{-t}`.

The offset is the end of the encoder's first sweep. It is found by searching
the emitted events, not by skipping a hardcoded prefix and trusting it.

## What this does not say

The encoder's full map is `L = U_r U_c^{-t}`, not this single factor. The
other 415 encoder fibers, both decoders, and both Gram words are not
replayed. No physical consumer, identity-side shear, native tariff, or new κ
is claimed. Selected κ stays `0.001672660197076918`.
