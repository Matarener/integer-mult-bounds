# A standard product entrance repays the encoded-exit saving

## 1. Entrance kept by the encoded exit

Work over the Gaussian dyadic ring `D = Z[i, 1/2]`. Ports, the Gram matrix `A`, the pivot set `J = [0,1,3,6,22,31,93,103]`, its complement `N`, and the block `B = A[J, N]` are the PR #3943 geometry: `A = [[I, B], [B^t, B^t B]]` in that order, `B` has 384 entries in `{0, ±1/2}`, and `B^t B` has rank 8. Write `w = x + y`, `v = y + A x`, and `q = x_J + B x_N`.

The encoded exit of that package places `w_J` on `Y_J` in the target hyperplane `H_j`, `w_N` on `X_N` in `H_n`, `q` on `X_J` in FULL, and `v_N` on `Y_N` in FULL. Helpers are already restored. Its explicit inverse is the one recorded there,

```
x_N = w_N - v_N + B^t q,
x_J = q - B x_N,
y = w - x.
```

Every encoded `(w, q, v_N)` is therefore a realizable source state. In particular, for each `n in N` the bank state with `X_n = u` and every other data bank zero is realizable. On that state the value `u` is not present on `Y_n`.

The same inverse gives the product defect on the N side. Cancelling `y`,

```
v_N - w_N = B^t x_J + (B^t B - I) x_N.
```

The coefficient matrix of `(x_J, x_N)` in this formula has rank 96. Every one of the 96 coordinates is a nonzero form, so no N port already stores the product on `Y_n`.

## 2. Alphabet

The consumer may use only the formal operations of the PR #3943 adapter:

- `up` takes a bank from its hyperplane to FULL and costs one rank-one transport;
- `down` takes a bank from FULL to a named hyperplane and costs one rank-one transport;
- `scale` by `1/2` or `2`, and a unit `add`, require every bank they read or write to be FULL;
- an add cannot use a bank as both source and target.

There is no allocation, disposal, bank renaming, self-subtraction, or zero scale. Helper banks may begin with arbitrary dirt and must be returned unchanged. This is the fixed-occupancy model of that adapter, not a claim about every native instruction set.

## 3. Lower bound

Consider a program that, on every realizable encoded exit, ends with `Y_i = w_i` in `H_i` for every port `i`, and restores every helper.

Fix `n in N` and the witness of section 1, and set every helper to zero. The only nonzero bank is `X_n`, whose frame is `H_n`. No scale or add among the zero banks creates `u`. An `up` does not move a value to another bank. The first operation that can copy `u` is therefore an add that reads `X_n`, and that add is legal only after an `up` of `X_n`. At least one lift of `X_n` occurs.

`Y_n` starts in FULL and must end in `H_n`. Frames change only by `up` and `down`, so the transcript of `Y_n` contains at least one `down`.

These two transports name different banks. The 96 witnesses name 96 different lifts and 96 different descents. Any single program that meets the contract on every witness therefore contains at least 192 rank-one transports.

## 4. Attainment, and what it does to the encoded banks

The following program meets the contract. It is the PR #3943 return adapter with the final `X_J` repair deleted:

1. Lift every `X_n` from `H_n` to FULL.
2. Subtract `B^t q` from `Y_N`, using the eight FULL pivot banks and restoring each by the paired double.
3. For each `n`, subtract `Y_n` from `X_n` and add the new `X_n` into `Y_n`.
4. Descend every `Y_n` into `H_n`.

On the symbolic encoded exit this ends at `Y_i = w_i` in `H_i`. Helpers are untouched. `X_J` is still `q`. `X_N` has become `x_N` in FULL, so the encoded copy of `w_N` is destroyed. The invoice is 96 lifts, 96 descents, 576 unit additions and 16 scales.

The deleted repair is 384 further unit additions and 192 scales. Restoring it makes `X_i = x_i` in FULL as well, which is the legacy source return, still with exactly 192 transports and now 960 unit additions. Skipping that repair saves scalar work only. It does not save a transport, and it is not a consumer that keeps the encoded endpoint: `X_N` no longer holds `w_N`.

## 5. Rank bill

Both exits have the same frame-dimension total. The encoded exit contributes `8·9 + 96·8` from X and `8·8 + 96·9` from Y. The standard exit contributes `104·9` from X and `104·8` from Y. Helpers contribute `72·9` either way. Both totals are 2416. The PR #3943 optimistic credit subtracts the same initial 104 and leaves `P = 2312` for either exit.

The encoded native rank mass is 2576. Section 4 adds 192, so the standard-Y consumer has mass `C = 2768`, the legacy return mass. The rank excess `C - P` is 456, which is 192 more than the encoded excess 264. In the odd-stage paired-chain template of that package, `s = 2p + 1`, `m = 8s + 1` and `W = 104(s - 1)`, the necessary gap is

```
s C + max(0, (m - 1) W - s P) - m W
  >= s (C - P) - W
   = 352 s + 104.
```

The right-hand side is exactly the legacy-return screen. At nine stages the actual gap equals that bound and is 3272, against capacity 60736. The encoded exit, with no extra transports, has the smaller positive screen `160 s + 104` (1544 at nine stages). Moving the N products onto the standard Y banks spends the entire difference.

The 768 unit additions removed by the residual cleanup are not in this rank mass. They do not pay the 192 transports. A downstream consumer that presents the standard product entrance therefore repays the encoded-exit rank saving. The split read that leaves every bank in place has transport cost zero, and section 1 shows that it is not this entrance.

No selected-frontier change, supplier admission, or new κ follows. Selected κ stays `0.001672660197076918`.
