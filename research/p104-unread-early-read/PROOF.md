# Early read on the PR #5827 role-695 interval

This note checks one published replacement. It does not recompute conditional
kappa, native phases, or the caller bill.

## Pinned words

The source word is the PR #5811 word vendored by PR #5827 at
`05cd36e5af06d7a3790e30ce3f449fa89b853768`
(`inputs/pr5811-WORD.json.gz`, canonical SHA256
`a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c`).
The edited word is that pull request's published program
(`inputs/pr5827-WORD.json.gz`, canonical SHA256
`d1e5ee3b9811ce7be0ad80aecf19b41cd9277e838b3a9fe52d25baa610d58782`).
Those canonical digests are the `source_word_sha256` and `word_sha256`
fields of that pull request's `WITNESS.json`. The programs differ at
indices 13815 through 13821 and nowhere else. Boundaries, frames, ports
and the live set are identical.

## The interval

Write a, b, c, d for roles 695, 733, 773, 709. Write A, C, B for frames
3, 597, 1031. Replaying every transport before index 13815 on the source
word, with the same strict nesting rule as a public move into a larger
frame and a private move into a smaller frame, puts a and b in A, d in C
and c in B.

The unique source block at that index is

```text
MOVE c: B -> C   (private)
ADD  d += c in C
MOVE b: A -> C
ADD  b += c in C
MOVE a: A -> C
ADD  a += b in C
MOVE a: C -> B
```

The replacement is

```text
ADD  a += b in A
MOVE a: A -> B
ADD  a += c in B
MOVE c: B -> C   (private)
ADD  d += c in C
MOVE b: A -> C
ADD  b += c in C
```

Both schedules are legal on these entry frames. Both finish with a in B,
b in C, c in C and d in C, and with images

```text
a' = a + b + c
b' = b + c
c' = c
d' = d + c
```

taken over the interval-entry values. The first replacement event reads b
while b still carries its entry value: b is not the destination of any
earlier event in the block. Omitting that event stays frame-legal and
yields `a' = a + c`. Replacing its coefficient 1 by 2 yields a term `2b`.
Moving that same event to the end of the block is not a legal common-chart
addition: a then sits in B and b sits in C, while the event still names
frame A.

Reading the post-update value `b + c` and also adding c, which is the
arithmetic content of a late read followed by the direct `a += c`, produces
`a + b + 2c`. That counterfactual is not itself a legal schedule of this
interval. The legal early read is what keeps the coefficient of c equal to 1.

## Frame ranks

The frame bases have lengths 0, 1 and 5, and their XOR-spans have sizes
1, 2 and 32, so those lengths are the F_2-dimensions. The spans are strictly
nested: span(A) proper subset span(C) proper subset span(B). A transport
rank is the absolute difference of basis lengths, which is the rank used by
PR #5827's own native boundary check.

The two role-695 transports in the source block therefore have ranks

```text
A -> C : |1 - 0| = 1
C -> B : |5 - 1| = 4
```

and the replacement transport has rank

```text
A -> B : |5 - 0| = 5.
```

The other two moves, private c from B to C (rank 4) and public b from A to C
(rank 1), occur in both schedules. The MOVE-rank multiset therefore changes
by exactly `-H_1 - H_4 + H_5`.

PR #5827's proof says these frames have dimensions 0, 4 and 5, and that the
public queries A to C and C to B have ranks 4 and 1. The nesting claim is
right. The dimensions and the assignment of the two leg ranks are not.
The histogram change written next to that sentence, `-H_1 - H_4 + H_5`,
still matches the word.

## Local power sign

For `H_r(t) = r^t` and `0 < t < 1`,

```text
1^t + 4^t - 5^t > 0.
```

Indeed `1^t = 1`, and dividing by `5^t` gives the equivalent inequality
`(1/5)^t + (4/5)^t > 1`. For `v` in `(0, 1)` and `t` in `(0, 1)`,
`v^(t-1) > 1`, hence `v^t > v`. Both `1/5` and `4/5` lie in `(0, 1)` and
sum to 1, so the two strict comparisons add. At `t = 1` the difference is 0.
At `t = 2` it is `1 + 16 - 25 < 0`.

One extra coefficient-+1 ADD is present. Under the scalar rule
`2 * (3 + bit_length(n) - 1 + bit_count(n) + bit_length(d) - 1)` with
`n = d = 1`, that ADD costs 8 real scalar primitives. This is a local
charge, not a caller moment.

## What this does not show

It does not show that the native phase of either actual map matches the
published receipt, that the full ordinary and outer bill crosses at
0.00312476680, or that any of the five framework assumptions holds. The
selected frontier is unchanged.
