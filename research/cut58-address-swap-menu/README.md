# The cut58 ADDRESS swap does not cheapen the separable response menu

Open PR **#4086** already proves that the q2 event58 six-bank suffix costs at
least **22f** native mass for every `f>=2`, inside the separable class
`h T^e` with `h` in `<K,W>`, and that the existing word attains 22f. The
proposed 16f suffix is excluded there. That proof leaves outside-group
adapters open, and names one explicit phase-correct adapter as the next test.

This package prices the adapter already present in the cut58 source: the
rank-zero ADDRESS swap `P`. For every separable response `g` and every
placement `P^a g P^b`,

- the monomial has one inherited label `(K-parity, W-parity, T-parity)`,
  independent of which of the four writings produced it;
- its one-coordinate polar rank equals the polar rank of `g`;
- that rank still meets the separable tariff
  `2(q + (p xor q) + e)`.

The enlarged menu has **1008** monomials. **752** of them lie outside
`<K,W,T>`, including the transports `P T P`, `P K P` and `P W P`, and
**40** extra polar-rank-zero monomials. None of those outside responses is
cheaper than the separable parent it factors through. The minimum positive
polar rank in the outside part of the menu remains 2.

This does **not** extend the 22f word bound. A same-rank outside response, or
one of the 40 extra free monomials, might still shorten a full six-bank word.
No such word is constructed or excluded here. Selected κ is unchanged.

## Menu and proof

The vendored operators are the cut58 monomials `K`, `W`, `T` and the source
ADDRESS swap `P` from PR #4082. `verify.py` recomputes the group; it does not
import either predecessor tree. `P` has order 2 and polar rank 0, and it is
not in `G=<K,W,T>`. `G` has order 256. The old subgroup `H=<K,W>` has order
128, and `T` is outside it. `K^2=T^2` is the shared rank-zero square, and
both `K` and `W` commute with `T`.

K-parity `p` and W-parity `q` are the mod-2 word lengths in the left Cayley
graph of `H`. The tagging is consistent, and the 128 elements fall into the
same rank table as PR #4086:

| `(p,q)` | rank 0 | rank 2 | rank 4 |
| --- | ---: | ---: | ---: |
| `(0,0)` | 16 | 0 | 16 |
| `(1,0)` | 0 | 16 | 16 |
| `(0,1)` | 0 | 0 | 32 |
| `(1,1)` | 0 | 32 | 0 |

So `r(h) >= 2(q + (p xor q))` for every old response. T-parity `e` is 0 on
`H` and 1 on the other coset. The parent `h T^e` has polar rank
`r(h)+2e`, which is at least `2(q + (p xor q) + e)`.

There are 1024 writings `P^a (h T^e) P^b` and 1008 distinct monomials. Every
writing of one monomial carries the same `(p,q,e)` and the same parent rank,
and the monomial's own polar rank equals that parent rank. Rank equality is
not only conjugation invariance: the one-sided placements `P g` and `g P`
are included, and `P K P` has an old/fresh polar cross term while keeping
rank 2. The 40 outside rank-zero monomials all inherit `(0,0,0)`, so they
are extra free adapters rather than disguised positive-tariff responses.

The separable elements themselves have no polar cross term among the old
block `{0,1,2,3}`, the spectator block `{4..9}`, and the fresh block
`{10,11}`. That block split is the support reason the PR #4086 class is
separable. `P` moves the fresh pair onto bits `{0,1}`, which is why the
sandwiches leave the class.

PR #4086's counting argument (`n_W>=1`, `n_KW>=4`, `n_T>=6`, hence 22f)
uses characters of this separable class and the endpoint defects of the
displayed matrix. Those characters are not re-proved here, and they are not
claimed for sandwiches outside `G`. Equal parent rank does not by itself
bound a word that uses the new monomials.

## Relation to the task card

Catalogue card `joint-query-controller`, priority revision 6. The first
working command `python3 -B scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`. The card asks for a QQ16
producer and consumer. This scope is **refined**: Discussion #1166 comment
19039339 asked for the event58 local-16 suffix, and open PR #4086 already
answers that question inside the separable class. The remaining named test
is one outside adapter. The source ADDRESS swap is that adapter. The result
is a scoped menu obstruction, not a supplier and not a new κ.

Ordered eligible #1166 handoffs used for this session, after dropping items
already delivered or matched by an open PR, and after dropping the work
listed for the parallel sessions:

1. Typed actual-width physical H (19016699).
2. Single-hub two-bearing factorization of PR #3573 (19021149).
3. Integer-shear supplier/recurrence inequality left by #3947 (19031016).
4. One actual adjacent completed-call pair (19034066).
5. One changed chronological caller with a complete bill (19034741).
6. Fuse a physical source-normalization factor with the joint interface (19035513).
7. Independent inspection of the #3996 literal-index bridge (19035716).
8. One physical K/adjoint/frame boundary (19036235).
9. Fixed-tape producer at the encoded caller boundary (19037887).
10. Event58 local-16 suffix (19039339).

Item 10 is the handoff taken. Its separable 16f target is already excluded
by open PR #4086 (head `cd0f22abce2b74d7d080a2e640c0f495d3d2c3aa`), so this
package is the distinct remaining piece of that handoff: the outside ADDRESS
adapter #4086 names and does not price. A fresh 16-floor inside `G` would
have duplicated #4086 and would have been weaker than 22f.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/cut58-address-swap-menu --check-only
python3.12 scripts/research_package.py --package research/cut58-address-swap-menu
```

Directly:

```sh
python3.12 -I -B research/cut58-address-swap-menu/verify.py
```

The passing line is `PASS_CUT58_ADDRESS_SWAP_MENU`. The run rebuilds `H` and
`G`, checks the rank census and tariff, enumerates all 1024 writings, and
rejects a forced label conflict, a K rank tampered down to 0, and the claim
that the identity adapter transports `T` outside `G`.

Not run: the PR #4086 Gram and endpoint oracles, a search for a word below
22f that uses the 40 extra free monomials, Lean, Docker, and the selected
cold replay. The `f` multiplier in the physical tariff is the disjoint-support
factor proved in PR #4086; this checker certifies the one-coordinate ranks
that multiply it.

## Open next questions

1. Can a word whose unaries lie in this 1008-element menu realize the cut58
   matrix with native mass below 22f? The per-response tariff did not drop,
   but the 22f count uses characters of `G` only. A same-rank outside
   sandwich, or one of the 40 extra rank-zero monomials, might still reduce
   the number of positive responses. The first step is either to extend one
   of the three PR #4086 characters to the subgroup generated by the menu, or
   to exhibit one explicit cheaper word. Direct closure of `<K,W,T,P>` was
   still growing past 20,000 elements, so that enumeration is not a proof.

2. Is there a phase-correct monomial outside this P-double-coset whose polar
   rank is strictly below the separable tariff of the endpoint defect it
   replaces? That is the favorable outside bill requested by PR #4086, and
   this package only prices sandwiches by the source ADDRESS swap. No such
   monomial is supplied here.

## Credit

The cut58 matrix, the operators, and the 22-mass separable word come from
Ross Richardson, PR #4082, head
`ff277e8a958829954f371c85bdc447672266edbd`. The 22f separable-class floor and
the request for one outside adapter are PR #4086, head
`cd0f22abce2b74d7d080a2e640c0f495d3d2c3aa`. Preserve the predecessor lineage
named there: icekylinx/PR531, Rohan Arun/kernel92, Chris R/Clear1nsight, and
ToikY. The mod-2 K/W tagging and the rank table are the same separable census;
this package recomputes that census on the 12-bit monomials and adds the
P-sandwich menu.

Prepared by unpaidmoon with substantial Cursor Grok assistance in the group
computation, the menu argument, and the write-up. No independent human or
formal-kernel review is claimed. New work is Apache-2.0. Selected frontier
and κ are unchanged.
