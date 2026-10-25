# Explicit constant for the uniform CRT evaluator

This is a counting proof for one proposition in Cinna Davis's PR #4100,
`CRT.md` §2 and the amortization display in §4. It is not an acceptance of
that construction, and it does not change κ.

## Proposition

For every integer `p >= 2` and `ell >= 1`, there is a sequential evaluator
that, from a CRT group of total bit length `W <= p` and a batch of at most
`A <= 8(p+2)` target axes, returns the forward and inverse rotation-switch
tables used by `CRT.md` and restores its work tapes, in at most

```text
E(p, ell) = 2^{4 ell} (p+2)^{16}
```

bit-steps. Thus the constant in the displayed bound

```text
E(p, ell) <= C 2^{4 ell} (p+2)^{16}
```

may be taken to be `C = 1` on this domain. The same bound implies the §4
comparison

```text
2^{-G} E(p, ell) <= 2^{-60 ell} (p+2)^{-48}
```

with `G = 64 (ell + ceil(log2(p+2)))`, again with constant 1.

The caller sizes in `research/unconditional-batched-crt/PROOF.md` meet
`W <= p`. For `n < 4` that file uses elementary multiplication and does not
call this evaluator. For `n >= 4`, `b = ceil(log2 n) >= 2` and the nominal
parameter is `p = 6b`. The dyadic length `T` is a power of two in
`[4n/b, 8n/b)`, so

```text
log2 T < log2(8n/b) = 3 + log2 n - log2 b <= b + 3 - log2 b.
```

For `b >= 2`, `log2 b >= 1`, hence `log2 T <= b + 1 <= p`. The split of
`log2 T` is the sum of the axis widths, and every CRT group is a subset, so
`W <= p`. The batch cap `A <= 8(p+2)` is the explicit reading of `CRT.md`'s
"at most O(p) axis controls" used here. It is not a claim that every hidden
factor inside an `O(p)` in that file has been extracted.

## Bit-step model

A bit-step is one head move, one bit read, one bit write, or one binary
Boolean operation. Three tapes are used: input, work, and output. An indexed
read of a table is a full sequential scan of that table and a return to its
marker. No tape is allocated per recursion depth, axis, or input length.

Schoolbook multiplication of an `a`-bit integer by a `b`-bit integer, for
`a, b >= 1`, costs at most `8ab` bit-steps: each of the `a` rows ANDs `b`
bits and adds them into a window of `b + 1` bits at 2 steps per bit, then
the `a + b` product bits are written. That is `3ab + 3a + b`. For `a = 1`
this is at most `5b`; for `b = 1` it is at most `5a`; for `a, b >= 2`,
`3a + b <= 4ab`. In every case the total is at most `8ab`.

Restoring division with quotient length `a` and divisor length `b` costs at
most `8ab` bit-steps. Each of the `a` quotient bits subtracts and shifts a
window of `b + 1` bits, at `3(b + 1)` steps, and the quotient is written:
`3ab + 4a <= 8ab` because `4a <= 5ab` for `b >= 1`.

A positive Euclidean algorithm halves the remainder at least every two
steps: `r_i = q r_{i+1} + r_{i+2}` with `q >= 1` and `r_{i+1} > r_{i+2}`,
so `r_i > 2 r_{i+2}`. A `b`-bit modulus therefore produces at most `2b`
divisions. Each division and the two coefficient products cost at most
`32 b^2` bit-steps, because `8b^2 + 16b^2 + 4b <= 32b^2` for `b >= 1`.
The modular inverse therefore costs at most `64 b^3` bit-steps.

## What one axis evaluates

Fix a left group of `m <= 8(p+2)` moduli whose bit lengths sum to
`W <= 8(p+2)`, and one target modulus of bit length at most `ell`. The
offset is the one computed by the retained `balanced` step: reconstruct the
left integer with `decode_group`, then multiply by the inverse of the
growing right-child prefix modulo the target. One axis is charged for the
whole reconstruction, whether or not several targets share it.

That procedure uses at most `8m` multiplications of `W`-bit words, `4m`
divisions of a `2W`-bit dividend by a `W`-bit divisor, `2m` inverses of
`ell`-bit moduli, and `4m` additions of `W`-bit words at `4W` steps each.
The resulting per-axis CRT bill is at most

```text
64 m W^2 + 64 m W^2 + 128 m ell^3 + 16 m W
  = 128 m W^2 + 128 m ell^3 + 16 m W.
```

Substitute `m <= 8q` and `W <= 8q` with `q = p + 2`:

```text
65536 q^3 + 1024 q ell^3 + 1024 q^2.
```

Across `A <= 8q` axes this is `524288 q^4 + 8192 q^2 ell^3 + 8192 q^3`.

Four networks are built from that offset and its negative: the forward
rotation, the inverse rotation, and the same pair for the inverse macro.
`CRT.md` describes a fixed number of forward and inverse gadget operations;
four is the number priced here.

For a network on `N = 2^h` wires, `1 <= h <= ell`:

- Writing the rotation table costs at most `9(ell + 2)^2` bit-steps per
  wire, hence at most `9(ell + 2)^2 2^ell` altogether. Each wire is one
  addition and one restoring division of integers of at most `ell + 2` bits.
- The Beneš tables are produced by the scan recurrence below, at most
  `64 ell 2^{2 ell}` bit-steps.
- The output is at most `2 ell` layers of `N` bits. Scanning it once and
  returning the head costs at most `8 ell 2^ell` bit-steps.

Per network this is at most `25(ell + 2)^2 2^ell + 64 ell 2^{2 ell}`.
Four networks and `A <= 8q` axes contribute

```text
800 q (ell + 2)^2 2^ell + 2048 q ell 2^{2 ell}.
```

The input descriptor has at most `A W <= 64 q^2` bits and is scanned once,
at `256 q^2` bit-steps. Adding the CRT bill for every axis gives the six
quantities in `cost_terms` inside `verify.py`: setup `256 q^2`, CRT
`524288 q^4` and `8192 q^3`, the inverse piece `8192 q^2 ell^3`, and the
two network pieces.

## Beneš scans

At a dyadic node of size `n = 2^k`, `k >= 2`, the sequential procedure
performs `7n + 1` full scans of `n` records of `k` bits: `n` scans to build
the inverse, `4n` scans for the two neighbor lookups at every node, `2n`
scans for the stack push and pop, and one scan to emit the child
permutations. A scan of `n` records of `k` bits costs `4nk` bit-steps, so
the local bill is `(7n + 1) 4 n k <= 32 k n^2`. The two children satisfy
the inductive claim `T(n/2, k-1) <= 64 (k-1) (n/2)^2`, and

```text
2 T(n/2, k-1) + 32 k n^2 = 64 k n^2 - 32 n^2 <= 64 k n^2.
```

The `n = 2` node performs 13 scans and costs `104` bit-steps, at most
`64 * 1 * 4 = 256`. Therefore `T(2^h, h) <= 64 h 2^{2h} <= 64 ell 2^{2 ell}`.
The child permutations are the standard even-cycle coloring of the retained
`benes` routine; the scans change the access mechanism, not the Boolean
tables. `verify.py` checks those tables against
`research/unconditional-batched-crt/check_batched_crt.py` on 90 rotation
networks and checks that flipping one control bit changes the image.

## Closing the inequality

Let `B = 2^{4 ell} q^{16}` and let `q = p + 2 >= 4`. Every term has the
shape `C(ell) q^a` with `a <= 4`. For an integer `q >= 5`,

```text
q^a / q^{16} < 4^a / 4^{16},
```

because `q^{12} > 4^{12}` and `x |-> x^{12}` is strictly increasing on the
positive integers. The ratio of each term to `B` is therefore largest at
`q = 4`.

At `p = 2`, `ell = 1`, each of the six terms is at most `B/7`. Raising
`ell` by one multiplies `B` by 16. It multiplies the quartic and cubic CRT
terms by 1, the `ell^3` term by at most 8, the table term by at most
`32/9`, and the network term by at most 8. Each of those factors is at most
16, so `7 * term <= B` is preserved for every `ell >= 1`. The sum of six
terms each at most `B/7` is at most `B`.

## The guard amortization

The bound just proved says `E <= 2^{4 ell} (p+2)^{16}`. With
`G = 64 (ell + ceil(log2(p+2)))`,

```text
G - 60 ell = 4 ell + 64 ceil(log2(p+2)).
```

So `E (p+2)^{48} <= 2^{G - 60 ell}` follows from
`(p+2)^{64} <= 2^{64 ceil(log2(p+2))}`, which is
`p + 2 <= 2^{ceil(log2(p+2))}`. This is exactly the displayed comparison
`2^{-G} E <= 2^{-60 ell} (p+2)^{-48}`. It prices only that comparison. It
does not prove reservoir placement, the ordinary interchange callee, or the
sparse repair program.

## What was executed

`verify.py` checks the integer comparisons in this argument, the scan
recurrence, the schoolbook and division tariffs through bit lengths 16 and
12, the Euclidean halving identity on the Fibonacci worst cases, 90
agreements with the retained compiler, 44 CRT offset or direct-endpoint
fixtures, rejection of a non-invertible prefix and of a non-permutation,
and a direct grid `p = 2..30`, `ell = 1..12`. The executed compiler uses
ordinary arrays. The bit-step count is the counting argument above, not a
trace of a finite-state tape simulator.
