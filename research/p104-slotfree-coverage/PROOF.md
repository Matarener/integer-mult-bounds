# Slot-free `(w, q, v_N)` boundary and the paired-chain screen

## 1. Object

This note prices the consumer requested by discussion comment 19030045 and
left open by `research/p104-role-exchange-caller-audit`: a caller that accepts
the PR3882 encoding `(w, q, v_N)` **without** moving those values back onto
the original source slots.

The encoding tail is the one in `research/p104-role-exchange-residue`. Its
executable convention is the object. `A` is the Gram matrix of the 104
retained roots divided by 8. The channel exit is `X = x` in FULL and
`Y = y + A x` in the target hyperplanes. The tail then returns

```
X_J = q = x_J + B x_N          FULL
Y_J = w_J                      hyperplane
X_N = w_N                      hyperplane
Y_N = v_N = y_N + B^t q        FULL
```

with `J` the eight orthogonal pivots, `N` the other 96 ports, `w = x + y`,
and every nonzero entry of `B` a signed half. All 72 dirty helpers stay
FULL and are not read. No later restoration adapter is appended. That is
the slot-free boundary.

The retained two-stage caller in `notes/copied-centers-complex.tex` asks for
data `(-y, w)`. The fixed-location adapter in the caller audit asks for
`(x, w)` on the original slots and proves a 192-rank net frame change for
**that** placement. Both targets are used below only as comparison payloads.
This note does not construct either schedule again.

## 2. The frame-dimension multiset does not move

At the channel exit the 208 data registers are 104 FULL banks and 104
hyperplane banks. The tail lifts all 104 `Y` banks and later drops exactly
the 96 `X_N` banks and the 8 `Y_J` banks. Lifts and drops are the only
frame operations. There are 104 of each, hence 208 rank-one conversions,
and every arithmetic step requires a FULL target and a FULL source.

The exit dimensions are therefore

| registers | dimension |
| --- | ---: |
| `X_J` (8) and `Y_N` (96) | 9 |
| `X_N` (96) and `Y_J` (8) | 8 |

That is again 104 nines and 104 eights. A coverage law that scores only the
multiset of data-frame dimensions awards this tail **no new endpoint
progress**. The 208 conversions relocate which banks are full. They do not
add a full bank.

Omitting a later slot-restoration adapter does not remove these 208
conversions. They are inside the encoding tail. The fixed-location adapter
is an additional word, not a subset of this one.

## 3. The payload is not a renaming of either caller target

The hyperplane banks are exactly the corrected sums: `X_i = w_i` for
`i in N` and `Y_j = w_j` for `j in J`. The FULL banks are `q` and `v_N`.

`B B^t = 12 I_8`, every row and every column of `B` is nonzero, and `B` has
384 nonzeros. Each coordinate of `q` is therefore `x_j` plus at least one
nonpivot source, so it is not a single `x` coordinate and it has no `y`
term. Each coordinate of `v_N` has `y_n` with coefficient 1 plus a nonzero
image of `q`, so it is not `-y_n` and not an `x` coordinate.

Hence no bijection of the 208 data banks preserves both frames and values
and carries this boundary onto either

- `X = x` in FULL and `Y = w` in hyperplanes, or
- `X = -y` in FULL and `Y = w` in hyperplanes.

The hyperplane half already matches `w`. The FULL half matches neither
candidate. Free renaming of banks does not turn the slot-free boundary into
the retained caller output.

One separating input is `x = 0`, `y = e_0`. Port 0 is a pivot, so
`(q, v_N) = (0, 0)` while `w = e_0` and `-y = -e_0`.

## 4. The screen that a replacement law still has to beat

The paired-chain constants are the ones in
`docs/research/p104-side-correction-scope-map.md`: width 73, 832 families,
nine local calls, 2312 progress units already credited per call, idle
coverage `72*832 - 9*2312 = 39096`, and capacity `73*832 = 60736`. The
channel mass is 2368. The tail adds `k = 208` rank units and, by section 2,
zero dimension-scored progress.

If a replacement law instead credits `c` rank units of payload progress per
call, the zero-saving moment is

```
M(0) = (9*(2368 + 208) + 39096 - 9 c) / 60736
     = (62280 - 9 c) / 60736.
```

This equals `7785/7592 > 1` at `c = 0`. It equals 1 exactly at
`c = 1544/9`, and it is strictly less than 1 exactly when `c > 1544/9`.
Every integer credit `c <= 171` fails the comparison; `c >= 172` passes it.

The usual child comparison still applies to this profile: for `0 <= a < 1`
and rank `r <= 9`, `(r/9)^(1-a) >= r/9`. At `c = 0` the moment is therefore
at least `M(0) > 1` for every such `a`, and unknown nonnegative costs do
not help. Equality at `c = 1544/9` is not a positive saving. A strict
screen pass needs `c > 1544/9` **and** a law that actually awards that
credit. This note does not supply that law. `M(0) < 1` is not admission:
native wrappers, owners, precision, tapes and later calls stay unpriced,
and they are not set to zero.

`B B^t = 12 I_8` is the block identity already used to rank the residual
error in the caller audit. It is checked here, not claimed as a new matrix
theorem. The 192-rank fixed-location tariff is likewise a predecessor
result and is not re-proved.

## 5. What this does not decide

No physical owner map, signed-floor word, or all-size transfer is given.
The dimension-only law is one explicit replacement screen, not every
coverage law. A consumer that changes the demanded output, deletes part of
the tail, or earns more than `1544/9` rank units of real endpoint progress
is outside this rejection.
