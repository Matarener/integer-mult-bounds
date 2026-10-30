# Audit of #6097's five-call diagonal-pair refutation, and the same floor over F3

**Independent audit and a scoped extension. No new κ.** The selected record is
unchanged.

[#6097](https://github.com/CrocSwap/integer-mult-bounds/pull/6097) (JoyboyBrian,
head `0a24101a977a652a306dd252b009d54840e4fdc9`) proves a computer-assisted
floor in the rank-one-idempotent register model of #4089. Over `F2` at width
two, for every group `G` and label set `L`, no product of at most five calls
`D_N(g) = (I−N) + [g]N` equals `diag([a],[b])`. This needs `a ≠ b` and that
neither is a product of at most two labels. For `diag([xyx],[yxy])` the
direct six-call word shows the bound is exact.

## Results

1. **#6097's PROOF.md: no error found.** I checked each step against the model.
   This covers the free basis-change normalization, dropping identity-labelled
   calls, prefix/suffix cancellation, the forbidden equalities, the parity step,
   and the completeness of partner branching. There are three remarks, and none
   affects the result.
   * PROOF.md says "every common-prefix or common-suffix rule". #6097's
     `cancellation_rules` emits only the *maximal* common prefix and suffix of
     each pair. The two closures are equal. Say `U = p·r·u` and `V = p·r·v`, where
     `p·r` is the maximal prefix. The shorter-prefix law `U ~ V ⇔ r·u ~ r·v` then
     follows from the maximal laws `U ~ V ⇔ u ~ v` and `r·u ~ r·v ⇔ u ~ v`. My
     engine emits every prefix and suffix length and reaches the same verdicts.
   * Its node counts are exactly those of my engine (1,392 at length four and
     10,634 at length five). The codes are different, but both branch on the
     first class of a shortest residual equation. So the search order is not an
     independent check. The SAT encoding below is a different method.
   * The node cap (200,000) is shared by all tuples of one length. It fails
     closed, so it cannot produce a false rejection.
2. **An independent stdlib engine agrees** ([verify.py](verify.py)). It was
   written before I read #6097's verifier. It restates the relaxation over `F_p`
   and imports no repository code. Over `F2` it finds zero survivors at lengths
   0–5 (all 9,331 tuples), and it accepts #6097's controls. Without
   cancellation it gives exactly 20 survivors at length four and 938 at length
   five. These are the counts of #6048's support-only relaxation.
3. **A local SAT cross-check also agrees** ([sat_crosscheck.py](sat_crosscheck.py),
   python-sat 1.9.dev15 / CaDiCaL 1.5.3, Python 3.12.14, macOS arm64). This
   method is independent of the branching search. Over `F2` it finds zero
   survivors at lengths 1–5. Without cancellation it finds 20 and 938, matching
   the stdlib engine.
4. **New: the same six-call floor holds over F3 at width two.** Over `F3` there
   are 12 rank-one idempotents (`p(p+1)`). The stdlib engine refutes all tuples
   of length 0–4: 22,621 of them, registered. The local SAT run refutes all
   248,832 tuples of length five (783 s with 9 workers; an earlier prototype of the same encoding also found none). The direct six-call word
   works over every field. So under #6097's hypotheses the minimum over `F3` is
   also **exactly six**. This answers #6097 open question 2 for `F3` at width
   two. The length-five row is **local SAT evidence**, not a stdlib replay.
   The stdlib search is far too slow there: single tuples starting and ending
   with the projectors `[[2,1],[1,2]]` and `[[2,2],[2,2]]` need up to ~1.4·10⁵
   nodes. Without cancellation, both engines find exactly 84 survivors at `F3`
   length four. So the F3 refutation does depend on cancellation, as it does
   over `F2`.

## Soundness over F_p

The argument is #6097's, with parity replaced by class weights mod `p`. Drop
identity-labelled calls. Expand the product as `Σ_U [g_U] P_U`, with
`P_U = Π_i (N_i if i ∈ U else I − N_i)` in chronological order. Subtract
`[a]` in entry 00 and `[b]` in entry 11. Each of the four entry equations is
zero in `F_p[G]`. The elements `[g]` form a basis, so every actual group-value
class has total coefficient 0 mod `p` in every equation. This follows the
known partition argument:

* **Closure.** Common-prefix and common-suffix cancellation hold in every group.
  The forbidden equalities `g_i ≠ e`, `a ≠ b`, and `a, b ∉ {g_U : |U| ≤ 2}`
  are the hypotheses.
* **Forcing.** Merges only add the class totals of an equation. Suppose a
  current class has a nonzero total. Its final class must then contain another
  current class whose total is nonzero. With one such class there is a
  contradiction. With exactly two, they must merge, and their totals must sum
  to 0.
* **Branching.** Otherwise, take a class with a nonzero total in a shortest
  residual equation. Branch over every other class with a nonzero total in that
  equation. One branch keeps the actual realization.

The SAT encoding states the same relaxation directly. It has one variable per
node pair, transitivity clauses, and each cancellation rule as an equivalence.
Forbidden pairs are negative units. For every equation `E` and node `u ∈ E`, a
mod-`p` one-hot counter forces `Σ_{v∈E} w_v [v ~ u] ≡ 0`. A model is exactly
a surviving partition. Free scalar changes of basis reduce to conjugated
projectors over `GL₂(F_p)`, exactly as in #6097. `S D_N(g) S⁻¹ = D_{SNS⁻¹}(g)`,
and the augmentation `F_p[G] → F_p` forces the trailing scalar to be `I`.

## Reproduce

```sh
python3 -I -W error -B research/diagonal-pair-collision-audit/verify.py      # ~30 s
python3 -I -O -W error -B research/diagonal-pair-collision-audit/verify.py
# local only, needs python-sat:
python3 -I -B research/diagonal-pair-collision-audit/sat_crosscheck.py 2 5
python3 -I -B research/diagonal-pair-collision-audit/sat_crosscheck.py 3 5 --jobs 8   # ~13 min
python3 -I -B research/diagonal-pair-collision-audit/sat_crosscheck.py 3 4 --no-cancel   # 84
```

Expected marker: `PASS_DIAGONAL_PAIR_COLLISION_AUDIT`. The run must also show
zero survivors in every row: `F2` lengths 0–5 and `F3` lengths 0–4. The
controls check several things:

* both projector inventories, against an independent `u vᵀ` (`v·u = 1`)
  enumeration;
* #6097's bit encoding;
* every generated cancellation rule, as a single common-context law;
* the subset expansion, against a free-monoid expansion;
* the exact six-call endpoint over `F2` and `F3`;
* that the solver accepts the six-call word and #6038's four-call `xy/yx`
  word;
* that #6097's tuple `(1,5,1,10)` survives without cancellation and dies with
  it;
* the short-target reopening of `(E00,E11)`, and the rejection of #6097's
  written five-call example;
* the exact no-cancellation counts 20, 938 and 84, and the 30 `F2` length-five
  survivors left when only prefix cancellation is used.

## What this does not cover

* Width at least three, `F4` and other prime-power fields, and `F_p` for
  `p ≥ 5` at length five. I did not finish a local stdlib run of `F5` at length
  four, and I claim nothing from it.
* A stdlib or proof-checked replay of the `F3` length-five row. A DRAT proof
  per tuple, or a symmetry-reduced faster search, would close this.
* Native conversion, restoration, tariffs, suppliers and the selected
  frontier. No independent human or proof-kernel review is claimed.

## Open next questions

1. **A checkable F3 length-five certificate.** *Why:* it would remove the
   local-SAT label from result 4. *First step:* reduce by the target-preserving
   symmetries (conjugation by `diag(1,−1)` and by the swap, and the
   reversal–transpose map `G → G^op`), then emit DRAT proofs for the heavy
   tuples. *Blocker:* the symmetry reductions need their own soundness lines.
2. **F5 and F4 at length five.** *Why:* this is the rest of #6097's field
   question at width two. *First step:* run the SAT encoding on `F5`. It has 30
   projectors and 24.3M tuples, so it needs the symmetry reduction first. `F4`
   needs `GF(4)` arithmetic in place of the mod-`p` code. *Blocker:* compute.

## Credit

JoyboyBrian (#6097) supplied the theorem, the collision relaxation and the
controls audited here. Josie Elliston (#6048) supplied the question and the
support-only counts. Nick Petalas (#6038) supplied the four-call `xy/yx`
theorem. Wentao Li (#4089/#4093) supplied the register model, following Cinna
Davis's A5 target (#2246). Prepared for JosieElliston by Claude Opus 5.5 via
Claude Code, Apache-2.0. No frozen predecessor file is changed or copied.
