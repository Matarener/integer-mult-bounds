# One axis splits through the section polynomial

**Claim type:** the triangle inequality on one axis.
**No new κ.** Each section error and the inverse ceiling stay hypotheses.
The selected record remains `23/10000`.

## Question

#4488 uses three bounds on one axis: `||B|| ≤ 10 p^2`,
`||C|| ≤ 10 p^2 + ε`, and `||B - C|| < 2 ε`, with
`ε = p^6 exp(-p^2)`. The named step is to split `B - C` through the section
polynomial.

## Lemma

Let `B`, `C` and `P` be vectors in a normed space, and let `ε > 0`. Then

```text
B - C = (B - P) + (P - C),
||B - C|| ≤ ||B - P|| + ||P - C||,
||P|| ≤ ||B|| + ||P - B||.
```

If `||B - P|| < ε` and `||C - P|| < ε`, then `||B - C|| < 2 ε`.
If `||B|| ≤ 10 p^2` and `||P - B|| < ε`, then `||P|| < 10 p^2 + ε`.

Thus the pair `(B, P)` meets the difference and approximant hypotheses of
#4488 once the inverse ceiling and one section error are known. The pair of
inverses `(B, C)` meets `||B - C|| < 2 ε` once both are within `ε` of the
same polynomial. The ceiling `||B|| ≤ 10 p^2` is not derived here. The factor
2 is this sum of two errors. HALO's `2g` rectangles remain a volume partition.

## Proof

The first display is the definition of `P`. The norm axioms give the two
inequalities. If `x < ε` and `y < ε`, then `x + y < 2 ε`. The integer shadow
replaces a strict cap `ε` by the previous integer: two copies of `m = 3` sum
to `6`, and `6 < 2 · 4`. The same addition is the factor `1 + 1 = 2`.

The polynomial norm is the second triangle. With ceiling `10` and error `2`,
`|6| ≤ 10 + 2`. Removing the error from the ceiling fails: `|13 - 10| = 3`
while `|13| > 10 + 1`.

The scalar check `(8 - 5) = (8 - 6) + (6 - 5)` is the one-dimensional case.

## Not covered

- A proof that `||B - P|| < p^6 exp(-p^2)`, or that `||C - P||` is that small.
- A proof that `||B|| ≤ 10 p^2`.
- The tensor sum and the gate below `2^{-C p}`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-bridge --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-bridge
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22 (open PRs fetched 2026-10-22T01:25:31Z, 343 records;
discussions fetched 2026-10-22T01:26:17Z, 3367 records) names this draft, #4488
(the telescope, which leaves the three bounds open), and the locality audit.
That audit already writes `||H_sec^{-1} - P_sec|| + ||P - H^{-1}|| <= 2 p^{10}
exp(-p^2)`. It does not separate the triangle at `ε = p^6 exp(-p^2)` or the
polynomial norm under the ceiling `10 p^2`. A search miss is not a novelty
certificate. #4488 is the telescope. HALO is the tensor sentence.

## Open next questions

1. **Is one section error below `p^6 exp(-p^2)` on a core axis?** The bridge
   consumes `||B - P|| < ε` as a hypothesis. The first step is to match one
   core row with the within-cell gauge of #4452.

## Credit

- The tensor sentence is #4100's.
- The locality audit already adds two `p^{10}` errors on a core axis.
- The ceiling `10 p^2` is Ryanson Jonathan's #4462, as carried through #4481.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The three axis hypotheses are #4488's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
