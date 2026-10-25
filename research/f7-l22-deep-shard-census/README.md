# The length-22 seven-label split census, completed

**Finite census result inside PR943's singleton prefix-walk model. No kappa,
supplier, tariff, certificate or selected-frontier value changes.**

[#3818](../f7-l22-union-census/README.md) ran the length-22 seven-label word
census with the corrected union-budget engine and left five splits capped:
`(10,9)`, `(10,10)`, `(11,9)`, `(11,10)` and `(11,11)`. This package runs
those five splits to completion with **the same engine, unchanged**, and finds
**zero restored universal words** in every one. It also runs the two 17-point
splits `(11,6)` and `(10,7)` directly, so the length-22 result no longer needs
the imported 17-point exclusion.

| Split | Cover shards | Nodes (cover sum) | Hits | #3818 capped floor |
|---|---:|---:|---:|---:|
| `(11,11)` | 251 | 55,385,607,437 | 0 | ≥ 6.0000e9 |
| `(11,10)` | 251 | 52,957,641,635 | 0 | ≥ 7.5000e9 |
| `(11,9)` | 251 | 14,058,107,415 | 0 | ≥ 8.1284e9 |
| `(10,10)` | 251 | 44,378,511,529 | 0 | ≥ 1.43517e10 |
| `(10,9)` | 251 | 7,027,617,655 | 0 | ≥ 6.7976e9 |
| `(10,7)` | 251 | 700,909 | 0 | not run (imported) |
| `(11,6)` | 251 | 2,247 | 0 | not run (imported) |

## What is established

1. **Seven finite split exclusions.** Each of the seven splits ran on all 251
   shards of the prefix cover below. Every shard's engine exited 0 with
   `complete=true`, zero hits and an empty hit file. No node cap was set.

2. **The length-22 domain is closed.** The merged split-domain package
   [#3708](../f7-l22-split-domain/README.md) proves four necessary
   conditions that leave eleven splits (`s >= t` by the rotation symmetry
   proved there): `(11,11)`, `(11,10)`, `(11,9)`, `(10,10)`, `(11,8)`,
   `(10,9)`, `(11,7)`, `(10,8)`, `(9,9)`, `(11,6)`, `(10,7)`. It then imports
   the 17-point exclusions of #2773/#2870 to drop the last two. #3731 and
   #3818 excluded `(11,7)`, `(10,8)`, `(11,8)` and `(9,9)`. This package
   excludes the other seven, including the two 17-point splits, without the
   import. `verify.py --check-receipt` checks that the union is all eleven.

3. **Consequence for f(7).** #2973 established `22 <= f(7) <= 24` in the same
   model, with a length-24 witness. Restored words have even length, so with
   length 22 excluded, **`f(7) = 24` inside PR943's prefix-walk model**. This
   is conditional on the stated dependencies below.

### The prefix cover

#3818 split each run into fifteen depth-four restricted-growth prefixes, and
the heavy shards hit its cap. Here the cover is the 203 restricted-growth
prefixes of length six, with the single prefix of six distinct labels,
`012345`, replaced by its 49 restricted-growth extensions of length eight:
251 shards. Every canonical length-22 word has exactly one prefix in the
cover, so the shards partition the unsharded tree. The verifier checks this
directly: every restricted-growth word of length eight over seven labels has
exactly one prefix in the cover.

Node counts are raw per-shard sums. Nodes above a shard's prefix are counted
once per descendant shard, so a cover sum is compared only with the same
cover's sum. As a consistency check, the `(10,9)` depth-four shards #3818
completed (3.7976e9 nodes) plus the 3,230,011,225 nodes of its capped shard
`0123`, measured here on depth-six sub-shards, give 7.0276e9. That matches
this cover's total of 7.0276e9 up to the duplicated prefix nodes.

## Dependencies, stated exactly

- **The engine.** `research/f7-l22-union-census/engine/union_census.c` is
  used byte-for-byte (SHA256 pinned in `SOURCES.json`). Its pruning rules are
  the corrected weight-parity budgets of #2973 and the union-support budget of
  #3005/#3818. Their proofs are in those packages; brute-force small-domain
  cross-checks are in #3818 and the independent tiny-domain audit #3899 (open).
  This package adds no pruning rule.
- **The eleven-split domain.** #3708's four conditions and its rotation
  symmetry are proved there; `verify.py` takes the eleven rows from its table
  and does not re-derive them. The 17-point import of #2773/#2870 is not
  used: `(11,6)` and `(10,7)` are enumerated here.
- **One engine implementation.** The five large exclusions rest on this one C
  engine. #3005's separately implemented C++ census has not been run at
  length 22.

This is an exhaustive finite enumeration with a written pruning proof. It is
not a formal-kernel proof, and it is not a statement about every
multiplication algorithm or any supplier.

## Verification

```sh
# Registered checks (each well under the 600 s per-command margin):
python3.12 -I -B research/f7-l22-deep-shard-census/verify.py --check-receipt
python3.12 -I -B research/f7-l22-deep-shard-census/verify.py --control
python3.12 -I -B research/f7-l22-deep-shard-census/verify.py --replay S,T:A:B
# (the registered replay slices are listed in VERIFY.json)

# Full local replay of one split (all 251 shards; opt-in, not run by CI):
python3.12 -I -B research/f7-l22-deep-shard-census/verify.py --replay 11,11 --workers 14   # whole cover by default

# Regenerate RESULT.json (opt-in; about five CPU-hours):
python3.12 -B research/f7-l22-deep-shard-census/deep_census.py --workers 14 \
  --split 11,11 --split 11,10 --split 11,9 --split 10,10 --split 10,9 \
  --split 10,7 --split 11,6 \
  --work OUT_DIR --output RESULT.json
```

- `--check-receipt` checks the engine pin, the cover partition, every split's
  251 shard rows, zero hits, completeness, node totals, and that the closed
  splits are exactly #3818's capped ones plus the two 17-point splits, and
  that together with #3731/#3818 they close the eleven-split domain.
- `--control` compiles the same engine at `(N,L) = (4,8), (4,10), (5,12)`,
  where universal words exist, and builds the same kind of mixed-depth cover.
  On every accepted split the sharded hit set equals the unsharded hit set
  (77 splits, 2,452 universal words). Dropping a hit-bearing shard is detected.
  The receipt check also rejects a cover with one entry removed or one
  overlapping entry added.
- `--replay` recomputes a slice of cover entries for one split and requires
  each shard's node count to equal `RESULT.json` exactly, with zero hits.

CI replays only the registered slices (about 1.2e9 nodes). Every split was run in full locally;
the exhaustive replay is opt-in because the seven splits total about 1.74e11
nodes.

## Credit

Predecessors: **Ross Richardson** (PR943, the prefix-walk model), **Aaron
Wang** (PR2542/PR2634 word model), **Nicholas Stone** (#2973, the corrected
engine and `22 <= f(7) <= 24`), **navinor** (#2773, #2870, the 17-point
exclusions), and #3005, #3708, #3731 and #3818 (union budget, split domain and
earlier length-22 probes). This package was produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

1. **A second implementation at length 22.** The five exclusions rest on one C
   engine. Running #3005's separately implemented C++ census on the same
   cover would remove that single point of failure. Blocked by: that engine
   is gated at `L <= 20` and its throughput at length 22 is unmeasured.
2. **Recompute the domain inside the verifier.** `verify.py` takes #3708's
   eleven rows as given. Re-deriving them from the four conditions here would
   make the receipt check self-contained. Blocked by: nothing structural.
