# Entrance, terminal, and caller price of one transported frame

The object is the single warp edit in the PR #3929 recipe: zero-based warp 0
on lender 243. The entrance basis changes from `(261, 133, 85, 45)` to
`(258, 130, 82, 42, 7)`, and the exit basis changes from `(320, 192, 45, 30)`
to `(320, 192, 42, 25, 7)`. The native map is the original column list. The
36 scalar edits are all in section B. No section A or restore opcode is
edited by the recipe.

## What the walker charges

The compiler transcribed in `verify.py` is the PR #3929 `compile_frames`
algorithm: guarded scalar and warp edits, one identity scale on the lender
when the pre-warp frame is a proper subspace of the new entrance, then
cleanup recomputed from the forward word. The histogram is
`audit_core.frame_bill`, the vendored PR #3929 bill.

On the vendored base word the bill moves only in section B:

| Piece | Histogram change |
|---|---|
| Entrance identity scale on register 243 | `+1 H1` |
| Positive-climb changes at the 36 edited B indices | `+11 H1 − 4 H3 + 4 H4` |
| Later B climbs whose frames were not themselves edited | `+16 H1 − 16 H2` |
| Section A, centre descents, restore, and final end-climbs | `0` |

The total is `+28 H1 − 16 H2 − 4 H3 + 4 H4`. Rank mass stays 5134. The width
inventory stays `{4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}`.

## Caller and terminal

These fields are identical before and after the compile: `ports`,
`start_extra`, `helper_final`, `target_levels`, `cut`, `precondition`,
`compensation`, `centers`, `center_frames`, `initial_corrections`, `A`,
`restore`, `removed`, and `prelude_events`. The caller therefore adds no
child and rewrites no interface.

Final end-climb counts stay `H1: 289`, `H2: 77`, `H3: 54`. `helper_final`
and every restore opcode and frame stay put. Cleanup gains exactly one
operation, the inverse scale `(scale, 243, 1, 1)` of the entrance identity,
and every other cleanup opcode and frame matches. That inverse is not a
forward frame-bill child.

## Power tariff

Let `f(q) = 28 − 16·2^q − 4·3^q + 4·4^q` for real `q`. This is the change in
`Σ n_r r^q` under the histogram delta above. Then `f(0) = 12` and `f(1) = 0`.

Set `x = 2^q` and `L = log₂ 3`, so `3^q = x^L` and `4^q = x^2`. For
`q ∈ [0, 1]` one has `x ∈ [1, 2]`, and

`f(q) = 4 g(x)`, `g(x) = 7 − 4x + x^2 − x^L`.

`g(2) = 3 − 2^L = 0`. Also `2^8 = 256 > 243 = 3^5`, so `L < 8/5`, and
`2^3 = 8 < 9 = 3^2`, so `L > 3/2`. Hence

`L(L − 1) < (8/5)(3/5) = 24/25 < 2`.

On `[1, 2]` the exponent `L − 2` is negative, so `x^{L−2} ≤ 1`, with equality
at `x = 1`. Differentiate `h(x) = 2x − L x^{L−1}`:

`h'(x) = 2 − L(L − 1) x^{L−2} > 2 − 2 = 0`.

So `h` is strictly increasing and `h(x) ≤ h(2)`. The identity
`2^{L−1} = 3/2` gives `h(2) = 4 − (3/2)L`. The lower bound on `L` gives

`h(2) < 4 − (3/2)·(3/2) = 7/4 < 4`.

Therefore `g'(x) = h(x) − 4 < 0` on `[1, 2]`. Since `g(2) = 0`, `g(x) > 0`
on `[1, 2)`, so `f(q) > 0` for every `q ∈ [0, 1)` and `f(1) = 0`.

Every power tariff `r^q` with `0 ≤ q < 1` therefore prices this frame
strictly above the original word. The zero caller delta and the zero
terminal end-climb delta cannot reverse that sign. Equality holds only for
the rank-mass tariff `q = 1`.

PR #3933 already shows that the least legal completion of this same entrance
also loses, and that the published non-minimal frames cost less than that
least completion while still losing. This note does not repeat that census.
It prices the published frame's entrance, terminal, and caller separately.
