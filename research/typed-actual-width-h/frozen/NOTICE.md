# Frozen predecessor sources

These two Python files are unmodified copies. `verify.py` hashes them and reads
two source lines. It does not import them.

| File | Vendored path in PR #3623 | Git blob | SHA-256 |
|---|---|---|---|
| `pr3493-outer_layer.py` | `research/twiddle-matched-layer/pr3493-outer_layer.py` | `2fc3370ea7e1b32be27faa4ec726ad7732af6769` | `3e6bae42f4e6239d0a467fb0498da3906fc139672fae96211c835be3b5fef307` |
| `pr3599-active_plan.py` | `research/twiddle-matched-layer/pr3599-active_plan.py` | `c3a01cd8c4f52cab478aefacad60f64f60f1453a` | `e1092fdbb70df43f1d4fdb50f39a07a543d71c4ea9f9e8a50b790b81fd50223e` |

Both blobs are identical at PR #3623 heads
`328c40966b650f60b1d62cfb0b1d67b2b755eb62` and
`c5ab698bba8b35323e40ae3b132e78f26179d393`.

`pr3493-outer_layer.py` is Nick Petalas's outer join from PR #3493.
`pr3599-active_plan.py` is Jose Manuel's actual-width planner from PR #3599.
Clear1nsight vendored both into PR #3623. Apache-2.0, with the notices already
in those files. They are not a new derivation.
