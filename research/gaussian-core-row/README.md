# A core row clears the within-cell agreement radius

**Claim type:** a distance comparison for one core row.
**No new κ.** The ideal-gap gauge stays a hypothesis. The selected record
remains `23/10000`.

## Question

#4490 uses `||B - P|| < p^6 exp(-p^2)` on one core axis and asks whether a
core row meets the within-cell gauge of #4452. That gauge gives the same
error for a section whose ideal off-sums are at most `1 - 1/(8p^2)`, once
the row lies past the agreement radius.

## Lemma

Let `p ≥ 2` and `W` be integers with `0 ≤ W ≤ p - 1`. Write

```text
R = (2 p^{24} - 1) W,    A = ceil(p^{48}).
```

Then `R < p^{26} < p^{48} = A`. An output kept at distance `A` from every
face is strictly farther from the section boundary than this bandwidth.
Its section-polynomial row is the global polynomial row. If the section
meets the #4452 gauge, then

```text
||P - H_sec^{-1}||_2 < p^6 exp(-p^2),
```

and the core row is a row of that operator. The distance `p^{25}` does not
clear the loose radius `(2 p^{24} + 1) W` at `p = 2`.

## Proof

The bandwidth identity is

```text
p^{26} - (2 p^{24} - 1)(p - 1)
  = p^{24} ((p - 1)^2 + 1) + p - 1.
```

For every integer `p ≥ 2`, `(p - 1)^2 + 1 ≥ 1` and `p - 1 ≥ 1`, so the
right-hand side is positive. Since `W ≤ p - 1`,

```text
R ≤ (2 p^{24} - 1)(p - 1) < p^{26}.
```

For an integer `p`, `p^{48}` is an integer, so `A = p^{48}`. Also
`p^{48} = p^{26} p^{22}` and `p^{22} ≥ 2^{22} > 1`, hence `p^{48} > p^{26}`.
The core distance exceeds the agreement radius of #4452. HALO's sentence
that a row at distance `A` from a section boundary has its polynomial row
equal to the global row therefore applies to this output. The operator
bound itself is #4452's, under that package's ideal-gap hypotheses. This
package does not re-prove it.

At `p = 2` and `W = 1`, the loose radius is `2^{25} + 1`, which is larger
than `p^{25}`. Exponent 25 is not a uniform agreement distance. Exponent
26 is, and the core uses 48.

## Not covered

- A proof of the ideal off-sums `1 - 1/(8p^2)`.
- The global-inverse summand `||P - H^{-1}||` on the same row.
- The comparison of the Neumann ceiling `U` with `10 p^2`.
- Editing the #4100 notes. They still use `A = ceil(p^{48})` and
  `p^{10} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-core-row --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-core-row
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T01:31:47Z, 344 records;
discussions fetched 2026-10-22T01:32:37Z, 3368 records) names this draft, #4452
and its check #4460, the gauge packages #4438 and #4469, #4482, and the
locality audit. The audit and discussion comment 19078965 already say
`A = ceil(p^{48})` clears the written radius with `J = ceil(p^{42})`. #4482
uses agreement distance `p^{26}` as a core side, not as this row distance.
No other package compares `ceil(p^{48})` with the lowered radius `p^{26}`.
A search miss is not a novelty certificate. #4452 is the within-cell error.
HALO is the core distance.

## Open next questions

1. **Is the within-cell Neumann ceiling `U` at most `10 p^2`?** #4452 proves
   `8 p^2 < U < p^6` and `U < 16 p^2 - 1`. The tensor chain uses `10 p^2`.
   The first step is to clear `8(D - 4) ≤ 10(D - 32 p^2)`.

## Credit

- The core distance `A = ceil(p^{48})` and the exact-row sentence are #4100's.
- The radius `(2 p^{24} - 1) W < p^{26}` and the error `p^6 exp(-p^2)` are #4452's.
- The polynomial split that consumes this error is #4490.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
