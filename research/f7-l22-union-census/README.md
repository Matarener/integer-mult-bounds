# A union-support budget in the length-22 seven-label word census

This package adds one proved necessary condition to the corrected seven-label
word census of [#2973](../f7-weight-parity-census-correction/README.md) and
uses it to extend the length-22 split domain of PR
[#3731](https://github.com/CrocSwap/integer-mult-bounds/pull/3731).

The new condition is not a new search heuristic. It is the completion bound
already proved and mutant-tested in the merged independent census
[#3005](../f7-union-support-audit/README.md), ported into the fast corrected
engine as a strictly stronger replacement for the even-side excess budget:

```
|U| + C(S,2) + C(T,2) - C(e,2) - C(o,2) >= 2^(n-1) - 1,
U = {x XOR y : x,y in E, x != y} union {x XOR y : x,y in O, x != y}.
```

`E` and `O` are the current distinct even- and odd-Hamming-weight prefix
states, `e=|E|`, `o=|O|`, and `(S,T)` is the target split. The predecessor's
even budget is `a+b <= B0` with `a = C(e,2)-|supp A|`, `b = C(o,2)-|supp B|`
and `B0 = C(S,2)+C(T,2)-(2^(n-1)-1)`. Since

```
|U| = |supp A union supp B| <= |supp A| + |supp B|,
```

the union condition dominates it: every state the old even budget rejects is
also rejected by the union budget, and some states it admits are rejected.
The odd-side bound is unchanged (the two forms are algebraically identical
there).

## What is established

1. **The port is a strict strengthening, with unchanged coverage.** The union
   budget is enabled by default; `--no-union-budget` restores the
   predecessor's even-side test. The engine differs from the pinned
   `corrected_census.c` (`sha256 265ead91...`) by exactly the committed
   [`engine/DELTA.diff`](engine/DELTA.diff): the length gate `L<=20` to
   `L<=22` (the same gate change recorded in PR #3731) and the union budget
   and its flag/counter. The pinned predecessor bytes are unchanged.

2. **Soundness evidence.** The predecessor's raw-product brute-force
   cross-check (`validation/check_corrected_c.py`, unchanged) passes with the
   union engine on all small splits and all four budget modes: 164
   comparisons, including positive universal counts, with cap and fail-closed
   controls. A union-only run (both older budgets disabled) also matches the
   brute-force universal counts. The proof of the bound itself is the
   argument quoted above and in #3005; the tests exercise it, they do not
   replace it.

3. **The six recorded L20/L18 zero-hit receipts replay complete and zero-hit**
   under the union engine. Node counts are deliberately not compared: the
   union budget removes nodes by design. The pinned predecessor receipts are
   untouched.

4. **Length-22 results.** Every split is run as the fifteen disjoint
   restricted-growth length-four prefix shards. The reported sharded node
   total is the raw sum over those shards; shared prefix nodes are counted
   once per descendant shard, so it exceeds an unsharded run by a
   split-dependent constant (51 where every shard survives to depth four).
   Sharded totals are compared only with sharded totals. A split is a finite
   exclusion only when all fifteen shards exit 0 with `complete=true`, zero
   hits, and no cap.

| Split | Nodes | Outcome |
|---|---:|---|
| `(11,7)` | 8,620,043 | complete, zero hits (control for #3731's exclusion) |
| `(10,8)` | 239,946,434 | complete, zero hits (control; #3731: 597,933,297) |
| `(11,8)` | 1,017,687,439 | complete, zero hits (control; #3731: 1,349,702,650) |
| `(9,9)` | 388,563,293 | complete, zero hits → **new finite split exclusion** |
| `(10,9)` | ≥ 6.7976e9 | one shard capped at 3e9; lower bound only |
| `(10,10)` | ≥ 1.43517e10 | six shards capped at 1.5e9; lower bound only |
| `(11,9)` | ≥ 8.1284e9 | one shard capped at 1.5e9; lower bound only |
| `(11,10)` | ≥ 7.5000e9 | five shards capped at 1.5e9; lower bound only |
| `(11,11)` | ≥ 6.0000e9 | four shards capped at 1.5e9; lower bound only |

The `(11,7)`, `(10,8)` and `(11,8)` node counts are single unsharded runs;
`(9,9)` is also a single unsharded run, with sharded total 388,563,344 in
`RESULT.json`. The lower bounds are sharded-node floors (capped shards
counted at their caps); they exceed the corresponding unsharded tree by at
most the small shard-duplication constant. The three control splits reproduce
#3731's zero-hit exclusions with the same engine shape; their node counts
differ only because of the stronger budget. The `(10,8)` tree is 2.49 times
smaller and the `(11,8)` tree 1.33 times smaller.

**Domain after this package.** #3731 left the six splits
`{(9,9),(10,9),(10,10),(11,9),(11,10),(11,11)}`. The `(9,9)` exclusion removes
one, leaving five splits that any restored universal length-22 word must use.
This is a narrowing of the finite domain, not a length-22 decision.

**Scope, stated exactly.** This is a finite word-census result inside
PR943's singleton prefix-walk model, not a formal-kernel proof and not a
statement about every multiplication algorithm. `RESULT.json` records all
fifteen shards of `(9,9)` complete with zero hits, so `(9,9)` is a finite
split exclusion under the engine's stated scope. Splits with any capped or
failed shard are tree-size lower bounds only and are not exclusions. No
kappa, supplier, tariff, certificate, frozen input or selected-frontier value
changes. `f(7)` remains `22 <= f(7) <= 24`; this package does not decide
length 22.

## Why the pair identity is not the third prune

PR #3731's open question asked whether `sum_x A_x B_x >= need` from #2973's
`MATH.md` section 3 can prune. It cannot in that direction. At every partial
state the identity

```
2 * sum_x A_x B_x = sum_y r_y^2 - s*t
```

holds exactly, and `sum_x A_x B_x` is monotone nondecreasing as points are
added (each `A_x` and `B_x` only increases). A universal leaf requires the
quantity to be at least `need`, but a partial state is always at or below its
own completion, so a lower bound at the leaf never rejects a partial state.
A usable prune needs a leaf upper bound; the union-support bound supplies
one. This is a negative answer to #3731's question, not a new identity.

## Verification

```sh
# Registered checks (each under the repository's 600 s per-command margin):
python3.12 -I -B research/f7-l22-union-census/verify.py --skip-probe
python3.12 -I -B research/f7-l22-union-census/verify.py --probe-split 9,9
# one --probe-split command per additional completed split in RESULT.json

# Full local replay of every probe (not run by CI):
python3.12 -I -B research/f7-l22-union-census/verify.py --probe-all
```

The sharded replay is deterministic: for a completed split the fresh shard
sum must equal the committed `RESULT.json` node count exactly. Timing fields
are excluded from every equality check.

## Credit

Predecessor and mathematical source for the corrected engine, budgets and
split theory: **Nicholas Stone** (#2973), building on the word model of
**Aaron Wang** (PR2542/PR2634) and **Ross Richardson** (PR943). The union
completion bound is from the merged independent census #3005 by **Nick
Petalas**. The length-22 split domain and the measured L22 budget are from PR
#3731 by **Nick Petalas**. This package was produced by Nick Petalas with AI
assistance. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.

## Open next questions

1. Does a restored universal length-22 word exist (`f(7)=22` versus `24`)?
   Any split left capped in `RESULT.json` needs a larger shard cap or a
   further proved completion bound.
2. Can the exact pair identity be turned into a *leaf upper* bound other than
   the shared-support one used here? That is the only direction that can
   prune.
3. Independently replay the `(9,9)` exclusion with a separately implemented
   engine (the #3005 C++ census is a natural candidate at `L=22`).
