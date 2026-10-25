# Commuting moved-ADD pairs do not retarget a staged544 line

**Negative result. No new kappa.** Selected kappa stays `0.001672660197076918`.

On both pinned PR3734 providers, every rank-1 ADD frame has a witness operand
whose line is created by an entrance, a warp map, or an earlier rank-1 ADD
that does not commute with it. Those witnesses are invariant under
`apply_move`. No finite sequence of commuting ADD moves can put that frame on
a disjoint line. The crossed-line pattern asked for by PR #3964 therefore does
not occur in this contract.

The same pattern, written as two scalar ADDs, keeps its opcodes and
coefficients. Each of the two helpers contributes two rank-1 climbs before and
after the retarget, so the child-histogram delta is zero. Either single-frame
intermediate is illegal. An unchanged histogram is not a paid-profile gain.

The argument and the twelve dependence pairs are in [PROOF.md](PROOF.md).

PR #4122 prices a different scalar identity for the same open question: a
swap of `y += x` with `y += z`, plus restoration, also at histogram delta 0.
That package does not search these providers. The obstruction above is the
provider half it leaves open. The two-ADD identity in section 3 of the proof
is the synthetic control already named by PR #3964, recomputed here only to
show that its bill is zero and that it is not an occurrence.

## Scope and evidence

Original card: `scalar-to-moment`, scope **refined**. The card asks for one
scalar simplification and its histogram. This package takes the released
moved-ADD question: a frame edit that does not change the scalar program.
Details, the stop rule, and the bottleneck link are in [TASK.json](TASK.json).

| Provider | SHA-256 | Rank-1 ADDs | Entrance | Map | Dependence |
|---|---|---:|---:|---:|---:|
| `BORROW-WORD-43base.json.gz` | `5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699` | 735 | 653 | 70 | 12 |
| `BORROW-WORD-43extra.json.gz` | `965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e` | 735 | 653 | 70 | 12 |

The gzip bytes and `vendor/retiming.py`
(`591d7278541ac4de9e9b6fc1e17aba23b205ac4b6c81824a28fc08294658ef0d`) are
unmodified copies of PR #3964 at `8a8bfb8d36cf5c9f7681b9e7f5d7876a4ba0f5a0`,
paths `research/staged544-stationary-pairs/inputs/` and
`vendor/retiming.py`. That commit is not an ancestor of this package's base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`, so [SOURCES.json](SOURCES.json) pins
only the catalogue and selected record. `verify.py` checks the three SHA-256
values directly.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/staged544-moved-add-pair/verify.py
python3.12 -B scripts/research_package.py --package research/staged544-moved-add-pair
```

Expected marker:

```text
PASS_MOVED_ADD_PAIR providers=2 rank1=735 entrance=653 map=70 dependence=12 disjoint_line_moves=0 toy_helper_bill=4xrank1 toy_delta=0 no_new_kappa
```

The direct command also passes under `-O`. No Lean, Docker, or selected cold
replay was run.

## Open next questions

1. Can one explicit noncommuting transposition, with a scalar correction, put
   a rank-1 ADD on a disjoint line and strictly lower the histogram for every
   real `0<a<1`? The twelve read-after-write pairs are the place to start.
   This obstruction stops at `crosses`, so that rewrite is a different
   identity. No such correction is specified here.
2. Does a commuting move whose new frame properly contains the old line improve
   the histogram? Containing frames are outside this theorem. PR #3970 already
   prices fixed-frame displacement two; a containing-frame census needs its
   own domain.

## Credit

The providers are dataisfire's PR #3734 words as vendored by Chris R /
Clear1nsight in PR #3964. The stationary legality theorem, the crossed-line
control, and `retiming.py` are from that PR and its credited PR #3886 /
PR #3942 lineage. Parallel PR #4122, discussion comment 19056694, invoices a
swap-and-restore identity and does not search these words. The witness
partition and the invariance argument are the part added here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review is claimed. Apache-2.0.
