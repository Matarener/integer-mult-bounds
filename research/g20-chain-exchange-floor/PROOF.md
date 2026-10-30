# Exact minimum of the G20 chain/exchange component

## Model

Work over F2 on the 32 boundary wires of PR5840. A state is a list of rows:
row `w` is the set of input coordinates currently held on wire `w`. An ADD is
`x_d <- x_d + x_s` with `d != s`, cost one. No scratch, reset, copy or free
relabelling of wires is allowed. A word implements a target when it maps the
identity rows to the target rows exactly.

## The component

Replaying the authenticated PR5840 `left_program` gives `left_rows`. Wires
`0..15, 30, 31` form a closed set: their rows read only those coordinates and
no other wire reads them. The source word spends fourteen chain ADDs and two
three-ADD exchanges (`SWAP 15 30`, `SWAP 14 31`) there: **20 ADDs**. The other
fourteen wires carry the three isolated four-wire bank exchanges covered by
#5850/#5851 and two untouched wires.

The 18-register component splits again into two closed 9-wire parts:

```
even  wires 0,2,...,12 : x_{2i}  = e_{2i} + e_{2i+2}      (i = 0..6)
      wire 14          : e_31
      wire 31          : e_14
odd   wire 1           : e_1
      wires 3,...,13   : x_{2i+1} = e_1 + e_3 + ... + e_{2i+1}
      wire 15          : e_30
      wire 30          : e_1 + e_3 + ... + e_13 + e_15
```

The source spends ten ADDs on each part.

## Statement

1. Every word on the nine even wires implementing the even part has at least
   10 ADDs. The same holds for the odd part.
2. Every word on all eighteen component wires implementing the component,
   including words whose ADDs cross between the even and odd parts, has at
   least 20 ADDs.
3. The right boundary is the reverse of the left word and the exact inverse
   map, so it has the same minimum. Each component side is exactly 20.

## Hand proof of the even bound

All nine even rows differ from the identity, so each even wire is a
destination at least once. A nine-ADD word therefore updates each wire exactly
once, and that update must produce its final row. A chain wire `2i` holds
`e_{2i}` before its update and its final row after it, so it never holds a
coordinate `e_31`. Suppose wire 14 is updated first among 14 and 31. Its
source must hold `e_14 + e_31`; wire 31 still holds `e_31`, and no chain wire
holds `e_31`. If wire 31 is updated first, its source must also hold
`e_14 + e_31`; wire 14 still holds `e_14`. Either case is impossible.

## Computer proof of all three bounds

`verify.py` runs an exhaustive depth-first search for each budget from zero up
to the source cost. It prunes a state only by two admissible bounds:

- each row of the state that differs from the target needs one more ADD;
- the remaining map `R = target * state^-1` needs at least as many ADDs as it
  has non-unit columns. The reversed word of transposed ADDs implements `R^T`
  with the same length, and the row bound applies to `R^T`.

The search tracks `R^T` incrementally: the state step `x_a += x_c` changes
`R^T` row `c` to `R^T[c] + R^T[a]`. A memo records the largest failed budget
for each state, which is sound because failure at budget `b` implies failure
at every smaller budget. Every ADD of the restricted wire set is tried at each
node, so no ordering or normal form is assumed. A search that exceeds its node
limit fails the check instead of reporting a bound.

The first feasible budget is the minimum. Its witness word is replayed as rows
and on every Boolean input of the wires. Four controls must behave as known:
the chain alone needs exactly 14, a weakened even target fits in nine, and a
two-wire exchange needs exactly three.

## Consequence for the source boundary

Within the stated model, a side of the PR5840 boundary cannot gain by
resynthesising the chain together with the bank 7/15 exchange, or by mixing
even and odd chain wires, as long as the gates stay on these 18 wires.
Adding the component-local six-ADD floor of the other three exchanges
(#5850/#5851) gives 20 + 18 = 38 per side and 76 per port. This is still a
component-local statement: gates linking the 18 wires to the exchange wires or
to the two untouched wires are not covered, so no global 32-wire minimum is
proved.

## Not covered

General GL2 bases inside equal-target pairs (pairs `(2k, 2k+1)` mix the even
and odd parts and change the target), scratch or helper wires, gates leaving
the component, changed controllers, nonunit tariffs, and any recursive,
physical, compiler or precision cost. The paid recursive profile is unchanged
and kappa is unchanged.
