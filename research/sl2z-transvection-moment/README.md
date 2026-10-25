# Arbitrary integer transvections pass for B and fail for every higher power

**Scoped moment calculation. No new κ, no supplier admission, no selected-frontier change.**
The selected conditional exponent remains `0.001672660197076918`.

PR #4126 proves that the unit alphabet `{X, X^{-1}, Y, Y^{-1}}` makes every faithful word for `B^k = X^2 Y^2` fail the strict supplier test. Its open question asks whether one explicitly larger alphabet, still implementing the integer matrix rather than the three-bit quotient, can pass for some `a > 0`. This package names that alphabet and prices it. The three-bit quotient is not used as a substitute bill.

## Alphabet and charge

Let

```text
X^t = [[1, t], [0, 1]],    Y^t = [[1, 0], [t, 1]],    t in Z, t != 0.
```

`X^t - I` and `Y^t - I` each have rank 1. The moment parameters are the ones fixed by PR #4126: address width `m = 2`, and a two-role diagonal word whose spectator role is never written. Each allowed transvection is one rank-1 child. There is no cleanup child. The strict test is

```text
M(a) = (λ / W) * (1/2)^{1-a} < 1,    a in [0, 1],
```

where `λ` is the number of transvections and `W` is the role count. Equivalently, for a rational `a = p/q`,

```text
λ^q * 2^p < W^q * 2^q.
```

Two readings are reported. `W = 2` counts the idle spectator, as PR #4126 does. `W = 1` charges only the active role. Coefficient size is not a child in this alphabet: `X^2` is one letter, not two unit shears. That omission is stated below and is not treated as a zero cost in any other model.

## Length

Write `B = X^2 Y^2 = [[5, 2], [2, 1]]`. Then `B^2 = 6B - I`, so the entries

```text
u_0 = 1,  u_1 = 5,  u_k = 6 u_{k-1} - u_{k-2},
v_0 = 0,  v_1 = 2,  v_k = 2 u_{k-1} + v_{k-1}
```

satisfy `B^k = [[u_k, v_k], [v_k, u_{k-1}]]` and `u_k u_{k-1} - v_k^2 = 1`. The same square relation gives `u_k = 2 v_k + u_{k-1}` and `u_k >= 5 u_{k-1}` for `k >= 1`.

Consecutive letters from the same family multiply: `X^a X^b = X^{a+b}`. A shortest word therefore alternates, and a word of length 3 that does not alternate reduces to length at most 2.

- Length 1 is impossible: `v_k != 0`.
- Length 2 is `X^a Y^b = [[1+ab, a], [b, 1]]` or `Y^a X^b = [[1, b], [a, 1+ab]]`. One diagonal entry equals 1. This happens at `k = 1`, by the word `X^2 Y^2`. For `k >= 2` both diagonal entries are at least 5.
- Length 3 is `X^a Y^b X^c` or `Y^a X^b Y^c`. Expanding gives

```text
X^a Y^b X^c = [[1+ab, a+c(1+ab)], [b, 1+bc]].
```

Matching `B^k` forces `b = v_k`, `1+bc = u_{k-1}` and `1+ab = u_k`. Thus `v_k` must divide both `u_k - 1` and `u_{k-1} - 1`. Those two divisibility statements are equivalent: if `u_k = 1 + a v_k`, the determinant rearranges to `u_{k-1} - 1 = v_k (v_k - a u_{k-1})`, and the converse is the same calculation with the two diagonal entries exchanged. When the divisor exists, the remaining off-diagonal equation holds automatically, because its numerator is `u_k u_{k-1} - 1 = v_k^2`.

For `k >= 2` the divisor does not exist. Indeed

```text
v_k - (u_{k-1} - 1) = u_{k-1} + v_{k-1} + 1 > 0
```

and `u_{k-1} - 1 > 0`, so the positive remainder of `u_{k-1} - 1` modulo `v_k` is `u_{k-1} - 1` itself. The `YXY` expansion imposes the same divisibility condition. Therefore `λ(B^k) >= 4` for every `k >= 2`, even if every nonzero integer coefficient is allowed. The explicit word `(X^2 Y^2)^k` shows the matching upper bound `λ(B^k) <= 2k`.

At `k = 1` the same length-3 equations produce a zero exponent, so they degenerate into the length-2 word. Hence `λ(B) = 2`.

## Moment

With `W = 2`:

- `λ(B) = 2` gives `M(a) = 2^{a-1}`. This is strictly less than 1 for every `a in [0, 1)`, and equals 1 at `a = 1`. The strict test therefore passes for the single matrix `B` at every positive exponent below 1.
- `λ(B^k) >= 4` gives `M(a) >= 2^a >= 1` for every `k >= 2` and every `a in [0, 1]`. The strict test fails for every higher power.

With `W = 1`, `λ >= 2` gives `M(a) >= 2^a >= 1` for every `a in [0, 1]`. The strict test already fails for `B`. The pass above uses the idle spectator in the denominator.

The unit sub-alphabet `{X^{±1}, Y^{±1}}` still needs four letters for `B`. A breadth-first search confirms that no shorter unit word exists, which is the `k = 1` case of PR #4126, recomputed here rather than imported. If every coefficient `t` must be expanded into `|t|` unit shears, `X^2 Y^2` costs four children again and the `W = 2` pass disappears. That expansion cost is unknown in the rank-only alphabet; it is not entered as zero.

## What this does not establish

This is not a register identity that escapes the three-register obstruction, not a native XOR bill, and not a multiplication theorem. The three-bit quotient of PR #3947 still has an unpriced conversion into these integer matrices. No selected cold replay, Lean proof, or supplier admission was run. An optimistic pass for one matrix, at one role count, is not acceptance under the catalogue gate.

**Expansion decision: stop.** The unit alphabet fails, the coefficient-free alphabet fails for every power that a recurrence would call, and the single-matrix pass depends on counting an idle role. Another formal-word search is not justified.

## Evidence

The length classification and both moment readings are proved above. `verify.py` checks the matrix identities those proofs use through `B^{24}`, the two closed-form expansions on a sample of exponents, the unit-shear breadth-first control, and the strict comparison on every rational exponent with denominator at most 8. It also rejects the boundary `M = 1` and a damaged coefficient. These checks do not replace the divisibility argument.

```sh
python3.12 -B scripts/research_package.py --package research/sl2z-transvection-moment
```

Python 3.12, standard library only. A direct run of `verify.py` is the same check.

## Open next questions

1. What child count should the coefficient `t` have if a double is one shift rather than either one child or `|t|` children? The `W = 2` pass and the unit-alphabet failure are the two extremes. A one-shift price for `t = 2` decides which side this alphabet lands on. The blocker is a native operation that is actually legal for that shift; the rank-only model does not provide one.

## Credit

- **1337isnot1337 / OpenAI Codex**, PR #3905: the shear generators, the target `B`, and the four-call unit word.
- **ToikY with OpenAI Codex**, PR #3937 and PR #3947: the commutative obstruction, the three-bit quotient, and the request for a supplier inequality. The quotient is not reused as a bill.
- **unpaidmoon**, PR #4126: the unit-alphabet inequality `λ >= 2k+1` in the rank-1 model, and open question 1, which asks for a larger integer alphabet. This package answers that question and does not reopen the unit-letter proof.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
