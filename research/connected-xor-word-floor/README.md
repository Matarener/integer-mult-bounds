# Connected restored source-XOR words need 2(n-1) calls

Every restored word of source XORs `x_t += x_s` over F2 on `n` labels whose
interaction graph has `c` components has at least `2(n-c)` calls. In
particular, a connected restored word needs at least `2(n-1)` XORs, for every
`n`. Doubling any spanning tree's edges attains the bound.

Claim type: scoped written mathematical proof with finite exact corroboration.
This contribution was produced by Nick Petalas. Apache-2.0. Independent human
and formal proof-kernel review are unclaimed. No new κ is claimed.

[PROOF.md](PROOF.md) gives the complete argument in two steps:

1. **Rank lemma.** If a product of `L` rank-one updates `I + u_k v_k^T` is the
   identity over any field, then `L >= rank U + rank V`. For XOR words,
   `L >= |targets| + |sources|`. So a word in which every label is both a
   source and a target has at least `2n` calls.
2. **Induction.** Otherwise some label is only a target or only a source.
   Deleting its calls leaves a restored word on `n-1` labels. Each component
   of the remaining graph needs at least two calls to or from the deleted label,
   because one nonzero contribution cannot cancel.

The theorem covers overlapping interactions and odd-length identities. One
example is the five-call commutator word on three labels. Neither a graph edge
count nor a parity argument is used.

## Consequence for the mutable-source connector

PR #2455 shows that a restored common-B mutable-source word with `Q` queries
has `Q >= n + c`. Here `c` is the number of components of its source
interaction graph. PR #2455 proves this for five sources, and that result is
cited, not audited. Under that inequality, the theorem gives

    X >= 2(n - c) >= 2(2n - Q),   n + 1 <= Q <= 2n.

At five sources this recovers PR #2455's `X >= 8` at six queries and
PR #2643's sharp `X >= 6` at seven queries. It also gives `X >= 4` at eight
queries and `X >= 2` at nine. At the minimum query count `Q = n+1`, the
graph is connected and `X >= 2(n-1)`, which is PR #2455's Open next question 2.
The proof also works unchanged for calls `x_t += a x_s` with `a != 0` over any
field. That extension is written-proof only.

## Evidence and reproduction

The read-only standard-library verifier enumerates every word on one to five
labels by meet-in-the-middle. It keeps each frame matrix together with every
directed arc set that reaches it. Every generator is an involution, so a word
`u reverse(v)` is restored exactly when `M(u) = M(v)`. Joining equal matrices
therefore enumerates every restored arc set of each length. The verifier joins
full lengths through 2, 4, 6, 8 and 8 for one through five labels. On every
restored arc set it checks `L >= |T| + |S|` and `c >= n - floor(L/2)`. It
confirms that the first connected restored length is exactly `2(n-1)`, and
that the floor is attained at every even length up to `2(n-1)`. It also
checks the star and path words through twelve labels, the odd commutator
identity, and six semantic controls.

The local CPython 3.12.15 run passes. At five labels, the half-layers hold
1, 20, 280, 3,330 and 36,110 matrix/arc-set states. The joins give 7,705
connected restored arc sets at length eight and none shorter. The fewest
components at lengths 0 to 8 are 5, –, 4, –, 3, 3, 2, 2, 1. Each registered
command took about 0.1 seconds locally, far below its 120-second limit.

From the repository root, run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/connected-xor-word-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/connected-xor-word-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connected-xor-word-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connected-xor-word-floor --check-source-history
```

Any CPython 3.12 executable may replace this installation path. A direct run
prints `PASS_CONNECTED_XOR_WORD_FLOOR`, followed by a generated JSON receipt
with every census count and the SHA256 of all six package files. Save stdout
outside the checkout. No scientific receipt is handwritten. The verifier reads
no predecessor files at runtime.

## Sources, scope and stopping decision

The question is Open next question 2 of ywz65's
[PR #2455](https://github.com/CrocSwap/integer-mult-bounds/pull/2455),
`research/mutable-source-six-query-xor`. That package supplies the X-only
reduction, the component inequality and the five-label census through length
seven. Arham Tahir's PR #1898 and PR #1340 supply the connector, the paid
source-XOR alphabet and the eight-XOR construction. VictorLiwentao's PR #2643
supplies the seven-query floor. These results are cited, not re-verified.
Exact source blobs are pinned in SOURCES.json.

The base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`,
priority revision eight. The card's first-step control and the
selected-baseline metadata control both passed. The card scope is changed:
the alphabet is kept and the source-count restriction is removed, which the
card lists as a scope-change trigger. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19219151)
records this scope. The work stopped at the first verified theorem.

The selected frontier is unchanged. Tariff optimality at other query counts,
physical common-B source access, native/precision/hosting costs, supplier
admission and the complete multiplication theorem are outside scope. The
connector corollary for `n != 5` assumes PR #2455's component inequality at
that source count. No Lean, Docker or historical scientific replay is run.

## Open next questions

- What is the minimum odd length of a connected restored word? The theorem
  gives at least `2n-1`. The census attains it at three and four labels, with
  lengths five and seven. Five labels were joined only through length eight.
  First test whether `2n-1` is attained for every `n >= 3`. This matters
  because it decides which odd X counts occur at the minimum-query endpoint.
- Can the floor `X >= 2(2n-Q)` raise the eight- and nine-query tariff floors
  of PR #2677? That package records only `X >= 0` there for its path-lowered
  class. First bind the component inequality and those readout floors to one
  shared model. This package does not establish that they hold together.

Structured questions and blockers are in TASK.json.

## Verifier implementation limits

All loops have fixed finite domains: at most five labels in the census, at
most twelve in the attaining-word checks, and half-length at most four. The
largest live table has 36,110 states. Union-find has an explicit iteration
bound, and nothing is recursive. There is no subprocess, network access or
scientific output write. Python allocates bounded tuples, sets and dicts, so
static allocation is unavailable. Functions are under sixty lines. Explicit
`ValueError` checks still run under `-O`, and the registered commands treat
warnings as errors. Package hashing reads exactly six package files.
