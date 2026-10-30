# No PR5718-shape helper split remains on the PR5907 P104 word

**Scoped finite certificate; no new κ.** Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`.
The selected record is unchanged.

Matarener's open [PR #5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994)
(`research/p104-helper-split-exhaustion`) shows that no PR5599-type helper split remains on the latest conditional
P104 word, DreamingOfClouds's [PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907). It names
splits of the kind in flyingviper's merged [PR #5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718)
as the remaining route: different input and output bases, with an output correction. This package tests that
route on the PR5907 word.

## Result

The split shape of PR5718 (see its `PROOF.md`) is: a helper `p` of a boundary group with charts `(U, V)` is retired
at a strictly intermediate chart `F` after event `i`; a new independent helper with arbitrary input `z` takes over
`p`'s continuation (unit injection `b = e_p`); the input functional `c = aP` may use any role whose initial chart is
zero-dimensional, main inputs included; and the output defect is normalised on roles whose final chart is `V`.
The census in [shapesplit.py](shapesplit.py) decides exactly over Q, for every helper group, every strictly
intermediate chart, every cut after an event that touches that chart, and every group helper at the chart, whether

- some combination `a` of the prefix rows at `F` has `a_p ≠ 0` and `aP` in the allowed input support, and
- the z-direction `d = S e_p` vanishes on every role whose final chart is not `V` (no **leak**), and
- `a·b = c·d' ≠ 0` for some `d'` that agrees with `d` except on freely corrected `V`-final roles (the **pairing**).

| Word | Input rule | Evaluations | Leak | Pairing fails | Witnesses |
|---|---|---:|---:|---:|---:|
| PR5713 source (calibration) | group + U-initial | 8,579 | 3,817 | 2 | **7** |
| PR5713 source (calibration) | + empty-frame roles | 8,579 | 3,817 | 2 | **7** |
| PR5907 | group + U-initial | 8,913 | 4,202 | 4 | **0** |
| PR5907 | + empty-frame roles | 8,913 | 4,206 | 4 | **0** |

**Calibration.** On the PR5713 source word, the census recovers PR5718's own split: cut after event 14330,
chart 602, helper 708, ranks (2, 7). All 7 witnesses lie on chart 602 and helper 708 (earlier cuts of the same
meeting).

**PR5907.** No class passes. In 4,206 classes the new helper's z-direction leaks to a role whose final chart is
not `V`. In the other 4 (chart 549, helper 173, cuts 15974–15988) only the pairing `a_p = d_p c_p` fails. So on
PR5907, any further PR5718-type split must cancel that leak with a correction in the middle of the word. The
receipt lists how many leaked roles each class has. 425 classes leak to exactly one role; these are the nearest
candidates.

PR5718's split itself is a boundary-relaxation witness of the PR5994 census on its source word. So PR5994's
boundary-support exclusion already rules out PR5718-shape splits on PR5907 when the output defect stays on
`V`-final roles. This package gives that link an exact calibration and a separate decision procedure for unit
injection, and it records where the leak goes.

## Scope and limits

- Scalar necessary condition only, for the z-part of the split. The non-z part of the output normalisation, native
  maps, owned lifetimes, caller, compiler and outer checks are not involved. A witness would still need all of them.
- Unit injection on one group helper, as in PR5718. Injections along a combination of several fields are not
  covered.
- Mid-word corrections, such as `r += q·new` at a later meeting of the new helper with a leaked role, are not
  modelled. They are the open route, not an exclusion. A direct exact implementation of that relaxation was
  written but not run to completion, and it is not part of this package.

## Reproduce

Python 3.12, standard library, from the repository root (about 5–30 s):

```sh
python3.12 -B research/p104-pr5718-shape-split-census/verify.py
python3.12 -B scripts/research_package.py --package research/p104-pr5718-shape-split-census
```

Expected marker: `PASS_P104_PR5718_SHAPE_SPLIT_CENSUS`. The verifier authenticates both inputs: the PR5907 word
`research/p104-helper468-rung-removal/WORD.json.gz` and the PR5713 word read from
`research/p104-two-boundary-helper-split/inputs/pr5713-source.tar`. It also runs six synthetic controls of the pairing
decision and compares `RESULT.json` byte for byte.

## Open next questions

- **Leak-1 classes on PR5907.** Can a mid-word correction remove the z-leak of one of the 425 classes that leak to
  exactly one role outside `V`? Each one that closes adds one zero-paid split per LOCAL. First step: for one such
  class, list the later meetings of the pivot's chart with the leaked role. Then test whether a correction vector
  `S_τ e_r` reaches the leaked output coordinate, and check the non-z part of the correction. Blocked by a fast exact
  span update for the meeting corrections.
- **Chart 549, helper 173.** The four PR5907 classes without leak fail only the pairing. Does an input role outside
  the empty-frame rule make `a_p = d_p c_p` solvable? First step: print `A` and `d_p` at cut 15974.

## Credit

PR5994 (Matarener) supplies the census criterion, the pure-subspace construction and the question. PR5718
(flyingviper) supplies the split shape. PR5713 (Ali Romman) supplies the calibration word. PR5907 (DreamingOfClouds)
supplies the target word. PR5599 (Ali Romman) supplies the split criterion. The P104 lineage is retained in those
packages. Nothing of theirs is modified. This package was produced by Nick Petalas. Apache-2.0.
