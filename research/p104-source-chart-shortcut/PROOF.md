# Screened source chart after one Gram undo

## Question

Discussion #1166 comment 19035513 asks for one caller that fuses the physical
source-normalization factor with a full-output interface and a favorable bill.
The same handoff says a screened one-row Gram-undo shortcut still returns
`F81 T^{-1} x` on the physical source, and that the missing rank-one factor
costs 10816. This note proves that screening statement and the debt-free gate
arithmetic. It does not construct the fused caller.

## Local FULL is not F81

Let `F81 = F_2^9 ⊗ F_2^9`, dimension 81. For a nonzero row vector `r` and a
nonzero column vector `c`,

- `E_row(r) = r ⊗ F_2^9` has dimension 9,
- `E_col(c) = F_2^9 ⊗ c` has dimension 9,
- `E_row(r) ∩ E_col(c) = span{r ⊗ c}` has dimension 1,
- `E_row(r) + E_col(c)` has dimension 17,
- the codimension of that span in `F81` is 64.

The verifier checks all `511 × 511` nonzero pairs. Distinct nonzero `r` give
distinct row charts. A zero vector is not a 9-dimensional chart. Completing
one local row chart and one local column chart therefore leaves 64 dimensions
of the common chart unpaid. Local FULL is not global `F81`.

## The prepared entrance keeps `T^{-1}`

Use the prepared cut from PR #3978. Write `A_r` and `A_c` for the two Gram
factors, `K = T^{-1}`, and `F` for the common chart. The raw product and the
physical source read are

```text
M = [[I - A_c A_r, -A_c], [A_r, I]],
source = F * (M (K x, y))_1.
```

Polynomials are noncommutative. No relation `F K = K F` is used. Direct
expansion gives the source monomials

```text
+ F K x - F A_c A_r K x.
```

Every source monomial contains `K`. Setting `A_r = 0` (row Gram undo) or
`A_c = 0` (column Gram undo) leaves exactly `F K x`. Replacing the entrance
`(K x, y)` by `(x, y)` leaves `F x` instead. The Gram undo does not create
the chart defect, and it does not remove it. The physical source after either
one-axis undo is `F K x = F81 T^{-1} x`, not `F81 x`.

## Debt-free gate

The published conditional inventory in that same cut is `m = 81`,
`W = 36608`, `N = 104^2 = 10816`, 208 calls, bare channel mass 2368 and
persistent progress cap 2312. Those integers retie as

```text
81 W = 2965248,
81 W - N - 208*2312 = 2473536,
208*2368 + 2473536 = 2966080,
excess = 832.
```

For a changed local profile with debt `d = mass - progress`, the necessary
gate stated there is `C < N - 208 d`. At `d = 0` the strict allowance is
`C < 10816`. The predecessor tariff charges one rank-one child for the chart
`K` on each of the `N` data positions, cost `10816`. That cost equals the
allowance, so the strict gate fails. The screened excess moves from `-N` to
`0`, and the bill equals capacity `81 W` before helper, phase, owner, routing,
tape or precision charges. Any further positive charge makes the excess
positive.

The inherited positive-debt route already fails by 832 before this factor.
The debt-free calculation is the most favorable specialization of the same
gate for this particular shortcut. It is not a universal P104 barrier, and it
does not price the three-layer joint word (cost 32448 in PR #3978).

## What would escape the obstruction

An entrance that is already `(x, y)` rather than `(K x, y)` has source `F x`
after the row undo, so this chart charge is not forced by the Gram undo alone.
A fused caller can still change the entrance, the chart family, the debt, or
the progress binding. Those changes need their own bill. Equality at `81 W`
is already a failed strict gate for the screened shortcut.
