# Outside-domain root witnesses for the power-variation certificate

**Scoped proof and exact checker; no new κ.** The general-rank invoice
certificate from Ali Romman's PR5788
([`recursive-power-variation.md`](../../docs/research/recursive-power-variation.md))
bounds all real roots of `F(t) = Σ c_r r^t` by the number `V` of sign changes
in the rank-ordered coefficients. It spends that budget only on `t = 0`, `t = 1`
and brackets inside `(0,1)`. Roots at `t < 0` or `t > 1` leave the budget
unspent, so the report is `inconclusive`. That document's Open next question
asks for a proof that a root lies outside the domain.

This package proves such roots from exact data and subtracts them before the
interior count. On a factored oracle census of 4,455 invoices, the predecessor
certifies 391. With this change, 2,987 are certified (2,596 newly settled).
There are no false certificates and no changed predecessor verdicts.

For example, `4 - 8·2^t - 3^t + 2·6^t = 2(2^t - 1/2)(3^t - 4)` has `V = 2` and
equal endpoint values `-3`. The predecessor reports `inconclusive`. Here an
exact zero at `t = -1` and a sign change on `(1,2)` use both roots, so the
difference is **uniformly lower on all of `0 < t < 1`**. The fixture
`15 - 20·2^t - 3·3^t + 4·6^t` has an irrational root in `(-1,0)` and is settled
in the same way.

## Statement

Let `F(t) = Σ_i c_i r_i^t` with distinct positive integer ranks
`r_0 < … < r_n` and nonzero integer coefficients. Let `V` be the number of
sign changes in `c_0, …, c_n`, and let `e_0, e_1` be the exact endpoint
multiplicity lower bounds from PR5788. On the left, list
`-∞, -K, …, -1`, followed by `0` when `F(0) ≠ 0`. On the right, list `1`
when `F(1) ≠ 0`, followed by `2, …, K, +∞`. Give `-∞` the sign of `c_0`
and `+∞` the sign of `c_n`. Each finite point gets the sign of the exact
rational `F(k)`. Let `W` count the exact zeros at listed integers plus the
strict sign changes between adjacent strictly signed points, with an exact zero
breaking adjacency. Then `F` has at least `W` distinct real roots in
`(-∞,0) ∪ (1,∞)`, and

`(roots in (0,1), with multiplicity) ≤ V - e_0 - e_1 - W`.

If the interior brackets and exact interior zeros number exactly this
remainder, every interior root is simple and witnessed. With remainder zero
and one strict interior sample, the sign is uniform on `(0,1)`. These are
the same closure rules as PR5788, applied to a smaller budget.

## Proof

*Asymptotic signs.* `F(t) = r_0^t (c_0 + Σ_{i>0} c_i (r_i/r_0)^t)`. Every
ratio exceeds one, so the bracket tends to `c_0` as `t → -∞`. Hence `F` has
the sign of `c_0` on some ray `(-∞, T)`. Symmetrically, `F(t) = r_n^t (c_n + …)`
has the sign of `c_n` on some ray `(T', ∞)`.

*Witnesses.* A strict sign change between adjacent finite listed points gives
a root in that open interval by continuity. Between `-∞` and the first finite
point `-K`, choose `T < -K` inside the asymptotic ray; the opposite signs at
`T` and `-K` give a root in `(T,-K)`. The `+∞` case is symmetric. An exact zero
at a listed integer is a root. The open intervals are pairwise disjoint. They
avoid every listed integer and neither contains `0` or `1`: the point `0` or
`1` is listed when `F` is nonzero there. When `F(0) = 0`, the last left point is
`-1` and no interval reaches `0`. So the `W` roots are distinct, lie outside
`[0,1]`, and are disjoint from the endpoint roots counted by `e_0, e_1`.

*Budget.* PR5788 proves (generalized Descartes rule, Rolle induction) that `F`
has at most `V` real roots counted with multiplicity. Each outside witness has
multiplicity at least one. Subtracting `W` and the endpoint lower bounds leaves
the stated interior bound. The closure step is unchanged. Interior witnesses
lie in disjoint subintervals, so if they exhaust the remainder, each has
multiplicity exactly one and no other interior root exists. ∎

Outside witnesses only reduce an upper bound, so they cannot turn a valid
predecessor certificate into a different verdict. The census also checks this
on every fixture.

## Evidence

[`outside_roots.py`](outside_roots.py) imports the unchanged
`scripts/compare_power_variation.py` helpers (endpoint multiplicities,
directed interior enclosures). It adds `outside_witnesses` and the reduced
budget. Values at integer exponents are exact `Fraction`s. Reach `K` defaults
to 8 (at most 64). It accepts the same invoice pair as the shared tool:

```sh
python3 -B research/power-variation-outside-roots/outside_roots.py OLD.json NEW.json
```

[`verify.py`](verify.py) checks the following (about 13 s on CPython 3.12):

- The two fixtures above are `inconclusive` under PR5788 and become
  `uniformly_lower` with the stated witnesses.
- **Factored oracle census.** Every product of one, two or three factors
  `q·a^t − p` is checked. Bases are `a ∈ {2,3,5}`, three-factor products use
  three distinct bases, and `p/q` ranges over 15 thresholds from `1/3` to `25`.
  This gives 4,455 expanded invoices. Roots are `log(p/q)/log a` in closed form.
  Interior membership (`1 < p/q < a`), integer roots and the sign at `t = 1/2`
  are exact integer tests. Floats only order distinct non-integer roots, and a
  near-coincidence would be excluded and counted (0 occurred). Every predecessor
  and extended certificate is compared with the oracle: uniform sign, number of
  interior roots, simplicity and bracket location. Result: predecessor 391
  certified, extension 2,987, newly settled 2,596. False certificates,
  budget overruns and changed predecessor verdicts are all 0. 3,544 reports use
  an outside witness. Both tools use a 32-cell interior grid in the census.
- **Failure controls.** Two deliberately wrong witness rules are rejected by the
  same oracle. Swapping the two asymptotic signs gives 887 false certificates,
  2,026 budget overruns and 94 changed verdicts. Listing `0`/`1` as a witness
  point even when `F` vanishes there double-counts endpoint roots: 463 false,
  491 overruns and 104 changed.

Reproduce from the repository root (local run: CPython 3.12.14 at
`~/git/integer-mult-bounds/.venv/bin/python3.12`):

```sh
python3.12 -B research/power-variation-outside-roots/verify.py
python3.12 -B scripts/research_package.py --package research/power-variation-outside-roots
python3.12 -B scripts/check_research_commit.py --package research/power-variation-outside-roots --check-source-history
```

Expected final line: `PASS_POWER_VARIATION_OUTSIDE_ROOTS`. The verifier
fails closed without `assert`, so an isolated optimized run
(`python3.12 -I -O -B research/power-variation-outside-roots/verify.py`)
checks the same conditions.

## Scope and limits

This is invoice arithmetic only. It is not a construction, source extraction,
native operator, compiler endpoint, supplier admission or new κ. The selected
result is unchanged. The census is a finite exact check of the implementation,
not a proof of completeness. Two roots in the same unit interval outside
`[0,1]` with equal signs at its ends are not witnessed; the report then stays
`inconclusive`, which remains sound. Touching interior roots (even
multiplicity) are still unresolved, as in PR5788. The shared
`scripts/compare_power_variation.py` is not modified. Merging this check into it
is a separate maintainer decision.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

- **Finer outside brackets.** Can rational points beyond the unit grid
  (directed enclosures at `t < 0` and `t > 1`) separate two outside roots in one
  unit interval? Start with `(2^t − 5/2)(3^t − 4)`, whose two roots
  (about 1.32 and 1.26) both lie in `(1,2)`. The existing power engine accepts
  only `0 < t < 1`, so this needs an exact `r^(k+s)` reduction.
- **Pinned source invoices.** Does any committed paid-minus-target invoice
  that PR5788 leaves `inconclusive` become certified here? Run `outside_roots.py`
  on the pinned P104 ledger exported by the selected-invoice tool (#5735) and
  its declared edits.
- **Touching interior roots.** Even-multiplicity interior roots still block
  closure. A Sturm-type argument for exponential sums with commensurable
  exponents, or an exact derivative-sign witness, is needed.

## Credit

The root budget, endpoint multiplicities, interior brackets, invoice schema and
directed power engine are Ali Romman's PR5788/PR5746 work and their credited
predecessors (zxv's signed-invoice interface, woklerx's T16 unique-crossing
proof, mightyOil's moment-order audit). The generalized Descartes rule is
classical. New here: the outside-domain witness rule, its proof, the factored
oracle census and controls, produced by Nick Petalas. Apache-2.0.
