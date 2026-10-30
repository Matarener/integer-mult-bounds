# Controller income is capped at thick calls minus one

**Scoped negative result; no new κ.** In the Laurent caller alphabet of the retained p16 controllers
([`research/p104-productive-controller/caller.py`](../p104-productive-controller/caller.py)), the outputs earn
their rank mass because the central axis `Q` enters each target for free (target `1 + 8|S|` against lifts `8|S|`),
and the caller pays one rank-one request per port for each thin shear. This package proves that **no caller word
in that alphabet can twist more outputs than it has paid odd shears, minus one**, so the controller's rank-mass
income per port is at most the number of full calls minus one. The three retained controllers reach exactly that
bound (17 = 18 − 1).

**Prior work.** Theorem B of Cinna Davis's
[`research/productive-controller-basis-search/GLOBAL-PROOF.md`](../productive-controller-basis-search/GLOBAL-PROOF.md)
already proves that a successful controller with `2p` independent monomial outputs needs at least `2p + 1`
query-bearing calls, over `F₂[Q]/(Q² − 1)` with constant binary boundaries and no idle work, and its
[`PROOF.md`](../productive-controller-basis-search/PROOF.md) uses "a query changes the even part by one row" as a
search pruning rule; that package states explicitly that the binary theorem is not asserted for complex words. This
package is the complex-side counterpart: the same even-part count in the literal rational Laurent alphabet of the
retained callers (`Q² ≠ 1`, idle stage markers, any number of outputs twisted), stated as a bound on the income of
the complete invoice rather than on the call count, and checked on the literal controllers. It also answers, for
the rank mass, the first open question of that package: additional queries beyond `2p + 1` cannot raise the
controller's income, because every paid shear, thick or thin, buys at most one twisted output.

Base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`. Inputs pinned in [SOURCES.json](SOURCES.json).

## The argument

Split every bank's content into its even and odd parts in `Q`. Free operations (scalar `ADD`, swaps, `Q^{±2}`,
stage markers) are invertible row operations over the even subring and keep the rank of the even-part matrix; a paid
odd shear (`LOCAL` or `QUERY_SHEAR`) changes one row of it, so the rank drops by at most one, and the very first paid
shear cannot change it because no odd part exists yet. Every declared output is an odd monomial, so its row of the
constant left boundary lies in the left kernel of the final even-part matrix; these rows are independent, so the
final even rank is at most `n − twisted` (no invertibility of the left boundary is needed). Hence
`twisted outputs ≤ paid shears − 1`. Full statement and the invoice consequence in [PROOF.md](PROOF.md); the
left-kernel step and the stage-by-stage determinant proof of the lift cancellation are the repairs given by the
independent audit [PR #6120](https://github.com/CrocSwap/integer-mult-bounds/pull/6120) (A1, A2).

| Controller | Events | Paid shears (thick + thin) | Even-rank trace | Twisted outputs | Income per port |
|---|---:|---:|---|---:|---:|
| PR5398 direct (`kappa-backward-controller-20261023`) | 162 | 33 (18 + 15) | 32, 32, 31, …, 0 | 32 | 17 |
| Joint-helper lattice source (`joint-helper-lattice`) | 154 | 33 (18 + 15) | 32, 32, 31, …, 0 | 32 | 17 |
| p104 productive, all-forward (`p104-productive-controller`) | 218 | 33 (18 + 15) | 32, 32, 31, …, 0 | 32 | 17 |

Income per port is computed from the literal word: sum of target ranks `1 + 8|S_i|` over the 32 declared outputs
(1,584) minus every paid lift (8 per bank per full call and per idle stage, 1,552) minus the 15 thin requests.

Consequence for the complete rank-mass surplus with `v` ports and a local word losing `c` units per full call in its
owned centre: `M = v·income − calls·c ≤ calls·(v − c) − v`, which is `18·48 − 104 = 760` on the
[PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907) word. Changing the caller graph (path or
not, any idle law, any pairing of the thin shears) cannot raise it with 18 full calls; the open complex-side levers
are the centre, the fragmentation of the local word ([`research/fragmentation-ceiling`](../fragmentation-ceiling/README.md))
and the moment cost of longer callers ([PR #5554](https://github.com/CrocSwap/integer-mult-bounds/pull/5554)).
Outside the alphabet the bound can fail: a paid job that writes several rows, a paid odd one-bank translation
`Q^{±1}`, or a boundary that already carries odd `Q` content. A paid job that writes one row with a nonzero even
self-coefficient obeys it for any number of source banks (per-job bound `(n − rank A_e) + rank A_o`, audit PR #6120
A4; see [PROOF.md](PROOF.md), Scope).

## Verification

```sh
python3.12 -B research/p104-controller-income-bound/verify.py
```

Under a second, standard library only ([incomebound.py](incomebound.py)). It authenticates the pinned inputs;
replays one port of each controller from its right boundary to its left boundary with the literal rational
coefficients, tracking the exact rank over ℚ of the even part after `D_s → 1`, `Q² → 7/3` and `11/5`, and checks
that free events keep it, every paid shear changes it by at most one, the first leaves it unchanged, the trace is
32, 32, 31, …, 0 and all 32 declared outputs are odd monomials; computes the per-port income from the literal
word and checks the lift cancellation stage by stage (outputs containing `D_s` = row-lifts at `s`, 194 in all) and
records the rank of the left boundary; runs the controls (the two-bank Whitehead word with three odd shears reaches `diag(Q, Q⁻¹)` with trace
2, 2, 1, 0 and its two-shear prefix does not; dropping the last thin shear of the p104 controller leaves a positive
even rank and the declared diagonal is rejected; a free `Q^{±1}` is rejected by the alphabet); and compares
[RESULT.json](RESULT.json) in full. Final marker: `PASS_P104_CONTROLLER_INCOME_BOUND`.

## Credits and scope

Controllers by Cinna Davis (p16/a7 lattice), Ali Romman (PR5398 wrapper, PR5544 all-forward caller) and the
P104 lineage; Cinna Davis's `productive-controller-basis-search` for the binary `2p + 1` theorem and the even-part
pruning idea this package lifts to the rational Laurent alphabet; JosieElliston's independent audit
(PR #6120) for the left-kernel and determinant repairs and the corrected escape list; PR5405/PR5554 (zxv) for the path-family ceilings this bound complements; `fragmentation-ceiling`
for the moment side. The bound is on rank mass inside the literal alphabet; it makes no claim about the moment at
`t < 1`, about other primitives, or about any selected result. Prepared for Matarener with Claude (Anthropic),
via Claude Code. Apache-2.0.

## Open next questions

1. Does the bound extend to callers whose paid primitives are not odd central shears of one pair, for example a
   paid rank-r Gaussian touching several banks or several ports at once? Such a primitive could twist more than
   one output per paid job; with a paid odd one-bank translation and an odd boundary it is one of the ways to
   raise the controller income above thick calls minus one (PR #6120 A4 gives the per-job bound). First step:
   state the primitive as a physical job in `research/p104-productive-controller/caller.py` terms and extend the
   even-part tracker with its action; the bound becomes twisted ≤ Σ over paid jobs of their even-rank change.
2. Is the bound attained with more thick calls, and does the resulting invoice ever beat p = 16? Income grows by
   (ports − centre) per thick call, but the target ranks 1 + 8(p+2) and the idle chunks grow too; PR5554 covers
   path controllers, and the local invoice of PR5907 peaks at p = 16 (p = 20: 0.003117). First step: price
   M = calls × (v − c) − v against the log-moment growth for a non-path caller once one is constructed.
