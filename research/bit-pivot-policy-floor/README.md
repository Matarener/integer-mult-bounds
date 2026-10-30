# A pivot-policy swap floor for the paid pivoted BIT fallback

This contribution is a **scoped proof with a finite certificate**. It was
produced by Nick Petalas. No new kappa, supplier admission or complete
multiplication theorem is claimed. The selected frontier is unchanged.

It answers open question 2 of the pivoted fallback in
[#4235](https://github.com/CrocSwap/integer-mult-bounds/pull/4235): can another
pivot policy reduce the paid swaps? That package proves at most `s <= 2r`
swaps for its first-unit rule, so at most `1+12r` children (`1+4r` when
`f = 1`), which is 505 at the retained `m = 64, r <= 42` boundary.

## Result

Fix the compiler family of #4235. At stage `k = 0..r-1` a policy may choose
**any** unit pivot in residual rows `k..m-1` and columns `0..m-1-k` of
`M = P C`. A paid head swap is charged if its row is not `k`, and a paid
tail swap if its column is not `m-1-k`. Ordered clearing ADDs follow. Let
`D_r = diag(0^(m-r), 1^r)` be the diagonal suffix projector.

1. **Floor (proved).** Every pivot policy pays at least `2 min(r, m-r)`
   swaps on `D_r`.
2. **Attainment (proved).** An explicit policy pays exactly that many.
3. **Consequence at m = 64 (proved).** For `r <= 32` the first-unit bound
   `s <= 2r` is sharp for every policy. Over the retained ranks `r <= 42`,
   the best policy's worst-case packet still needs at least
   `1 + 6*64 = 385` children when `f >= 2` and `1 + 2*64 = 129` when
   `f = 1`, against #4235's 505 and 169. A changed pivot policy can save at
   most 120 (or 40) worst-case children at this boundary, and only in ranks
   33 to 42.
4. **Optimal policy on small censuses (finite certificate).** Over every
   idempotent in 13 complete `(q, m, r)` domains, the exhaustive
   optimal-policy worst case `s*(m, r)` equals the floor except at corank
   one, where `s*(m, m-1) = 3` for `m = 4, 5, 6` over F3 and `m = 4` over F5.
   The first-unit rule pays `2r` there (up to 10 at `m = 6`). So the floor
   is not sharp above `m/2`, and a better rule does gain in that range.

| q | m | r | idempotents | floor | optimal worst | first-unit worst |
|---|---|---|---:|---:|---:|---:|
| 3 | 2 | 1 | 12 | 2 | 2 | 2 |
| 3 | 3 | 1 | 117 | 2 | 2 | 2 |
| 3 | 3 | 2 | 117 | 2 | 2 | 4 |
| 3 | 4 | 1 | 1,080 | 2 | 2 | 2 |
| 3 | 4 | 2 | 10,530 | 4 | 4 | 4 |
| 3 | 4 | 3 | 1,080 | 2 | 3 | 6 |
| 3 | 5 | 1 | 9,801 | 2 | 2 | 2 |
| 3 | 5 | 4 | 9,801 | 2 | 3 | 8 |
| 3 | 6 | 5 | 88,452 | 2 | 3 | 10 |
| 5 | 2 | 1 | 30 | 2 | 2 | 2 |
| 5 | 3 | 1 | 775 | 2 | 2 | 2 |
| 5 | 3 | 2 | 775 | 2 | 2 | 4 |
| 5 | 4 | 3 | 19,500 | 2 | 3 | 6 |

The opt-in `--extended` run adds `m = 5`, ranks 2 and 3 over F3
(882,090 idempotents each); both have optimal worst case 4, equal to the floor.

## Proof of the floor

Write labels for the original rows and columns of `M = D_r C`. Its only
nonzero entries are `M[i][m-1-i] = 1` for `i >= m-r`. Rows `0..m-r-1` and
columns `r..m-1` are zero.

*Zero labels stay zero in the residual.* A clearing row ADD adds a multiple
of the pivot row chosen to cancel the pivot column. A residual row that is
zero has a zero coefficient. Column clearing and column swaps act inside
each row. So a label whose original row is zero has zero residual at every
stage. Any other ordered ADD from an earlier pivot row also leaves the
residual unchanged, because after column clearing a pivot row is zero on
every later residual column.

*Positions below `m-r` keep zero labels until their stage.* Claim: at the
start of stage `k`, every head position `p` with `k <= p < m-r` holds a zero
label. This holds at `k = 0`. Stage `k` swaps position `k` with the
position `i` of its pivot row. That row has a nonzero residual, so its label
is nonzero and `i` lies outside `[k, m-r)` by the claim. The swap moves the
zero label from `k` to `i >= m-r`, so the claim holds at `k+1`. ADDs do not
move labels.

Hence at each stage `k < min(r, m-r)` the row at position `k` has zero
residual. The pivot cannot lie in it, so a head swap is paid. The tail side
is the same argument for columns: the tail position `m-1-k` holds a zero
column label iff `m-1-k >= r`, that is, `k < m-r`. Column swaps exchange
position `m-1-k` with an earlier position, so zero labels again move only out
of the way. That gives `min(r, m-r)` paid tail swaps, and the floor follows.
Units over `Z/q^w` are the nonzero residues, and `D_r` has 0/1 entries, so
the argument is the same over every odd prime-power ring.

## Attaining policy

If `r <= m/2`, every stage pays at most two swaps, so `2r` is attained. If
`r > m/2`, at stage `k` take the home pivot `(k, m-1-k)` when it is a unit.
This happens exactly for `m-r <= k < r`. For `k < m-r`, take row label
`r+k` with its column label `m-1-r-k`. Those labels lie outside every later
home position, `[m-r, r)` on both sides, and the zero labels they displace
move to positions `>= r` and `<= m-1-r`. So later home pivots stay in place
and the policy pays exactly `2(m-r)`. The verifier executes this policy
(written as label `max(r, m-r)+k`, which agrees when `r > m/2`) on all 63
literal `m = 64` suffix fixtures and checks that it pays exactly the floor.
On the same fixtures it checks that the first-unit rule pays `2r`.

## Boundary bill

#4235 charges `2s` children of width `f` and `4s` half-width children
(`2s` width-one children when `f = 1`), plus one rank-`r` child. With
`s >= 2 min(r, 64-r)` on `D_r`, the worst packet over `r <= 42` under any
policy needs at least `max_r 1 + 12 min(r, 64-r) = 385` children (at
`r = 32`) for `f >= 2`, and 129 for `f = 1`. The upper bounds 505 and 169
come from #4235. Whether the best policy reaches 385 depends on
`s*(64, r) <= 64` for `33 <= r <= 42`, which is open; corank one shows the
floor `2(64-r)` itself can be exceeded.

## Evidence and reproduction

`verify.py` is standalone. It enumerates every rank-`r` idempotent once, with
the image in reduced row echelon form and the kernel as a graph over a
coordinate complement, and checks each count against
`q^(r(m-r)) [m choose r]_q`. For each idempotent it computes the exact
optimal-policy swap count by memoized search over every unit pivot at every
stage, and the first-unit count. It checks `optimum <= first-unit <= 2r`,
that the suffix optimum equals the floor, and that each domain's worst
optimum lies between the floor and `2r`. A control rejects a zero home pivot.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-pivot-policy-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-pivot-policy-floor --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-pivot-policy-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/bit-pivot-policy-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-pivot-policy-floor/verify.py --extended
```

Any CPython 3.12 works. Each registered command prints JSON with
`"status": "PASS_BIT_PIVOT_POLICY_FLOOR"` and the SHA256 of every package
file, and takes about 20 to 35 seconds. The opt-in `--extended` run takes
several minutes. `--receipt /absolute/new/path.json` writes the generated
report.

## Scope and limitations

The floor holds for the declared compiler family: stage-ordered pivots at
head `k` and tail `m-1-k`, paid swaps, ordered ADDs. A compiler with a
different normal form, pivot positions or swap pricing is outside it. The
floor is proved only for the projector `D_r`. The table's optimal worst
cases are finite facts about the listed fields and sizes, not a formula.
No caller is built, and preparation, routing and stock costs remain caller
obligations, as in #4235. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

1. Determine `s*(m, r)` for `m/2 < r < m`. Is `s*(m, m-1) = 3` for every
   `m >= 4`? A bound `s* <= 2(m-r)+2` would make the best-policy boundary
   maximum exactly 385. Every residual block keeps corank `m-r`, which is a
   natural first handle.
2. Find a polynomial-time rule that attains `s*`. The home-first greedy rule
   is not optimal (it pays up to 10 at `m = 6, r = 5`, against an optimum
   of 3).

Structured questions are in [TASK.json](TASK.json).

## Sources and credit

Base: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the selected record and task
catalogue as provenance. The compiler family, its swap pricing and the
residue-itinerary argument come from #4235 (head `27f1ce441`), which builds on
Cinna Davis's #4100 normal-form identity and its credited source527 and
commdata2338 normalizer lineage. That code is not merged, so this verifier
reimplements the stage process instead of importing it. The floor, the
attaining policy, the boundary consequence and the optimal-policy censuses
were produced by Nick Petalas. Independent human and formal proof-kernel
review are unclaimed. Apache-2.0.
