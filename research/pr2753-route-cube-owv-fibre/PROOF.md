# Exact fibre work of PR2753 `routes.route_cube`

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.

This prices the reached owner-route primitive `routes.route_cube` from David
Arias's PR2753 head `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, as retained
byte-exactly under `research/selected-bit-recursive-caller/predecessor/vendor/`
on pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Jose Manuel's PR2697 supplies
the vendor lineage. The routine and its dependencies are unchanged. No new
κ, supplier admission or H2 replacement is claimed. The selected decimal
remains `0.001672660197076918`.

## Domain and metric

Fix an odd prime label `q >= 3`, atom exponent `w >= 1`, dimension `d >= 1` and
fibre length `F >= 1`. The caller's Ring uses modulus `M = q^w` with
`L = bit_length(M) + 1` arena bits (one high-zero margin). Context sets
`cap = M/q` and `H = cap^(d^2)`. Put `V = H F` for the Boolean cube volume.

The metric counts only successful `bitstream.copy_bits` **writes of fibre
payload bits** inside one `route_cube` call: decoration, every `partition`
fill/drain, and final key stripping. Key `append_word` traffic, numerical
`high_key` work, Counter drains, blank tests and head returns are excluded.
This is a logical tape fibre-copy invoice for the pinned implementation, not
Python wall-clock time and not a fixed-physical-tape compiler bound.

## Cursor-pass lemma

In `route_cube`, when `cap > 1`, each of the `d^2` coordinates runs

```text
cursor <- copy(one)
loop:
  partition(..., cursor, ...)
  cursor.msb(); if MSB == ONE: break
  cursor <- shift_add_bit(cursor, ZERO)
```

The Word `one` is the one-hot LSB. Each `shift_add_bit(..., ZERO)` advances
that single `ONE` one position toward the high margin. The loop breaks when
the `ONE` occupies the reserved high-margin bit. Hence there are exactly `L`
partition calls per coordinate, and `d^2 L` partition calls in total.
Independent Word fixtures with `L in {3,5,6,8}` confirm the pass count.

When `cap = 1` (equivalently `w = 1`), the source skips the partition block.

## Partition fibre traffic

Each `partition` call, for every one of the `H` decorated records, executes
`copy_bits(..., fibre)` once into a bucket and once out to the merged output.
Keys are copied by `copy_key`/`append_tape`, not by fibre `copy_bits`. Thus
each partition contributes **exactly** `2V` fibre writes.

Decoration copies the borrowed cube once (`V` writes). Key stripping copies
the routed cube once (`V` writes). No other fibre `copy_bits` sites exist in
`route_cube`.

## Exact invoice

Therefore the pinned implementation has exact fibre `copy_bits` write count

```text
T_fibre = (2 d^2 L + 2) V    if cap > 1,
T_fibre = 2 V                if cap = 1.
```

Partition count is `d^2 L` or `0` respectively. Both identities are checked on
six fixtures, including a non-identity scaled chart, `d = 2`, `q = 5`, and the
`w = 1` (`cap = 1`) control.

## Matching the stated `O(wV)` charge

PR2753 states that owner routes still use `O_q(wV)` implementations. For every
fixture with `w >= 2` one has `cap > 1` and

```text
T_fibre = (2 d^2 L + 2) V >= 2 L V >= 2 (floor(w log2 q) + 1) V >= 2 w V
```

since `L = bit_length(q^w) + 1 >= floor(w log2 q) + 1` and `q >= 3` implies
`L >= w + 1`. Thus the exact invoice is an explicit numerical lower bound of
the stated form on this reached primitive. It does **not** prove that every
correct routing algorithm requires `Ω(wV)`; selected-bit-fast-primitives
replaces this routine. It does not price atom swaps, admit H2, or change κ.

## Relation to predecessors

- `binary-digit-cost-audit` exact-bills `bitstream` digit swaps/atom swaps; the
  `bitstream.py` bytes agree with this vendor, but that package does not invoice
  `route_cube`.
- `selected-route-live-volume` bounds live storage peaks of the same decorated
  cube, not fibre time.
- `high-route-prefix-cost` prices the later old-prefix wrapper around the
  replaced high-route path.
- `linear-sign-total-traffic` closes the linear sign; its open question 1 is
  the present route/leaf binding.
- `selected-bit-fast-primitives` constructs a faster replacement; it does not
  certify this retained implementation's exact fibre lower bound.

## Finite evidence

Registered replay meters the six fixtures against the closed form, checks the
cursor-pass lemma, authenticates source pins (including `routes.py` digest
`ed7dc3679451696ab1dd841146b215c9515a3eec5e4ff3763f33c315f1696ada`), rejects
corrupted certificates and duplicate JSON keys, and runs an independent
closed-form checker that does not import `verify.py` or `model.py`.
