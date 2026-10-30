# Two-helper zero-frame shears: no feedback gain at any target count

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped proof (every target count T) with finite corroboration.
No new supplier, κ or selected-frontier change.**

## Result

Use the model of [bit-zero-frame-feedback](../bit-zero-frame-feedback/README.md)
(PR #1306) and [bit-zero-frame-feedback-to-8-registers](../bit-zero-frame-feedback-to-8-registers/README.md)
(PR #2567). Registers are two helpers `h0, h1` and `T` targets `y_1..y_T`. All
inputs are arbitrary (dirty). A gate `(d, s)` is `x_d ^= x_s` at unit cost; there
are no extra registers. A restricted word has no gate with a helper destination
and a target source. The required map is the shear `(h, y) -> (h, y + K h)`
over F2, where `K` is `T × 2`.

Write `a`, `b` and `c` for the number of rows of `K` equal to `(1,0)`, `(0,1)`
and `(1,1)`, and `r = a + b + c` for the number of nonzero rows.

**Theorem.** For every `T ≥ 1` and every `K`, the restricted and unrestricted
minimum word lengths are equal:

```text
d_P(K) = d_full(K) = a + b + c + min(c, 2) = r + min(c, 2).
```

So target-to-helper feedback never lowers the cost of a two-helper shear. This
settles the 2×7 shape of Open next question 1 in PR #2567, and every other
2×T shape. By that package's duality `cost_{H×T}(K) = cost_{T×H}(K^T)`, it also
settles every T×2 shape, including 7×2. The 3×6 and 4×5 shapes stay open.

## Proof

**Upper bound (restricted).** Apply `y_i ^= h0` or `y_i ^= h1` for each pure
row. If `c ≤ 1`, apply `y_i ^= h0; y_i ^= h1` for the `(1,1)` row. If `c ≥ 2`,
apply `h0 ^= h1`, then `y_i ^= h0` for each `(1,1)` row, then `h0 ^= h1`. The
pure reads come first, so they see the original `h0`. The length is
`a + b + 2c` or `a + b + c + 2`, which is `r + min(c, 2)` in both cases. No gate
reads a target into a helper.

**Lower bound (feedback allowed).** Let `w` be any word, in the unrestricted
alphabet, whose product is the shear. Track each register's content as a
linear form in the initial values. The contents of all registers form an
invertible matrix after every prefix, so no register ever holds zero.

1. *Each nonzero row needs its target as a destination.* A register that is
   never a destination ends with its initial content. A target with a nonzero
   row of `K` must change, so at least `r` gates have a target destination.
2. *A once-modified target gets a pure row if no helper is a destination.*
   Suppose no gate has a helper destination. Then `h0` and `h1` hold their
   initial values throughout. Every prefix product then has block form
   `[[I, 0], [X, Y]]` with `Y` invertible, so each target register's content has
   a nonzero target part. If target `y_i` is the destination of exactly one gate,
   its final content is `y_i + v`, where `v` is the source content at that gate.
   The final target part must be `y_i` alone, so `v` has zero target part. Hence
   `v` is `h0` or `h1`, and the row of `y_i` is `(1,0)` or `(0,1)`. So every
   `(1,1)` target is a destination at least twice.
3. *A once-modified helper cannot end unchanged.* If helper `h_x` is the
   destination of exactly one gate, it ends with `h_x + v` with `v ≠ 0`. The
   shear requires it to end as `h_x`.

Now suppose `c ≥ 1` and `|w| ≤ r + min(c, 2) - 1`. Step 1 gives `|w| ≥ r`. If `|w| = r`, all gates have target destinations. If
`c ≥ 2` and `|w| = r + 1`, at most one gate is not target-destined, and step 3
forbids a lone helper destination. In both cases no gate has a helper
destination. Step 2 then needs at least `r + c` target-destined gates. That
exceeds `|w|`, because `c ≥ 1` when `|w| = r` and `c ≥ 2` when `|w| = r + 1`.
When `c = 0`, step 1 alone gives `|w| ≥ r`. Therefore
`d_full(K) ≥ r + min(c, 2)`. Since `d_full ≤ d_P`, both minima equal the formula. ∎

With `T = 1` we have `c ≤ 1`, and the formula reduces to `wt(K)`, as in the
`T = 1` lemma of PR #2567.

## Evidence

`verify.py` uses only the standard library and imports no predecessor code. It
checks four things:

- **Witnesses:** for every `K` with `T = 1..8` (87,380 matrices), the explicit
  restricted word above has length `r + min(c, 2)` and computes the shear
  exactly. The gates are linear, so this covers all dirty inputs.
- **Exact BFS:** for `T = 1, 2, 3` (84 matrices), it runs independent
  breadth-first searches in the unrestricted and restricted alphabets. Both
  minima equal the formula.
- **Consistency with PR #2567:** the formula matches the pinned certified
  minima for every `K` in 2×4, 2×5 and 2×6 (5,376 matrices). The certificate is
  authenticated by SHA256. This is a calibration of the formula, not a replay
  of PR #2567's search.
- **Controls:** the verifier rejects a truncated witness and a wrong shared
  gate, detects an inserted feedback gate, and rejects the weight formula
  `wt(K)` on a 2×3 matrix with three `(1,1)` rows (BFS minimum 5, weight 6).

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-helper-zero-frame-feedback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/two-helper-zero-frame-feedback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-helper-zero-frame-feedback
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-helper-zero-frame-feedback --check-source-history
```

Any CPython 3.12 path works. Each direct run takes under one second and prints

```text
PASS_TWO_HELPER_ZERO_FRAME_FEEDBACK witnesses=87380 bfs=84 pr2567=5376 controls=4 feedback_gains=0 no_new_kappa
```

The checks use explicit exceptions, so they stay active under `-O`.

## Scope and limits

The theorem covers `H = 2` (and `T = 2` by duality), F2, PR #1306's two
unit-cost single-source alphabets, zero frames and no extra registers. Larger
helper counts, nonzero frames, multi-source gates, other costs and other fields
are outside scope. Physical precision, hosting and supplier pricing are not
built or checked. The finite checks corroborate the written proof. They do not
replace it for `T > 8`. Independent human and formal proof-kernel review are
unclaimed.

Power of Ten rule 3 deviation: CPython allocates dynamically. Data sizes are
bounded by the fixed limits `T ≤ 8` for witnesses and `T ≤ 3` for BFS. The
largest BFS ball has fewer than 10^5 states.

## Open next questions

1. **Does feedback help for three helpers at nine registers (3×6)?** Step 2
   of the proof needs a replacement: with three helpers, a shared helper sum
   can serve several row types, and two-step gains can combine. A first step is
   a closed form for `d_P` on 3×T using the row-type counts, checked against
   PR #2567's 3×5 certificate.
2. **Is there a row-type formula for every H?** For `H = 2` the cost depends
   only on the row-type counts. For larger `H` the restricted cost becomes a
   shared-sum covering problem. A closed form for `d_P` would give the target for
   an unrestricted lower bound.
3. **Does the destination-counting argument extend to twisted exits?** The
   contamination lemma of PR #4071 handles twisted exits at fixed small shapes.
   Step 2 assumes the helper block stays fixed, so it would need the twisted
   helper block's own cost.

## Credits

The model, the restricted/unrestricted question and the 2×4–2×6 certificates
are from rtyu193-rgb's PR #2567, which builds on commdata2338's PR #1306,
bbMisk's PR #1557 and rtyu193-rgb's PR #1706. The twisted-exit question cites
thakrarsagar's PR #4071. The new contribution here is the all-T two-helper
theorem and its proof.
