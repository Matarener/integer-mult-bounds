# staged544-clock-ceiling

**The staged544 packing ceiling is a certified cap, and PR3734's own T360 clock reaches it
with one rule. No new κ: the value equals PR3802's, which was published first.**

Answers the first open next question of
[PR3734](https://github.com/CrocSwap/integer-mult-bounds/pull/3734)
(`research/staged544-producer-return`): *"Can a changed source clock attain more of the
ideal544 packing gain?"* Stacked on PR3734's head
`fa041037a3374eaa08feeca0b26a5d6893194147`; no file of that package changes.

## What this adds next to PR3802

[PR3802](https://github.com/CrocSwap/integer-mult-bounds/pull/3802) (hexapode, head
`de2cd5c58009205210e3bf328b0ef5cadf3903af`) reached the same conditional
κ = `0.001730578437266246818740 − 10^-46 − 10^-70` with a T385 combined clock while this
work was in progress; its idle histogram is exactly 385/360 times the one here, rank by
rank. This package does not claim priority on that value. It adds:

1. **A certificate that this κ cannot be beaten by any owner fill of this inventory**,
   under any clock and any replica count (`ceiling_certificate.py`, exact rationals,
   standard library). PR3734 and PR3802 make no packing-optimality claim. Further gains
   for the staged544 supplier therefore need a changed inventory, template or word, not
   another allocation.
2. **The cause of PR3734's loss**: its own clock, at the start, measured by an exact
   per-tick LP (`construction/hall_lp.py`) that rates any clock in about 20 s.
3. **The ceiling on PR3734's own clock and stock**: one deterministic rule (`clock.py`,
   727 of 3240 calls moved), T360, 323,069 physical families (PR3802: T385, 345,469; both
   need 19 stock bits, so no margin changes).
4. **PR3734's complete admission run end to end** through its `full_replay.py` wrapper on
   the changed inputs (PR3734 and PR3802 each report that their wrapper was not).

## Result

| | PR3734 | this package |
|---|---|---|
| source clock | `inputs/ORDER.json` | one rule applied to it, 727 of 3240 calls moved |
| idle histogram | `{1:84732, 3:23211, 5:4679, 32:1, 48:137911}` | `{1:84240, 3:23328, 5:4320, 48:137952}` |
| paid profile root, lower end | `0.001730448360207635461740` | `0.001730578437266246818740` |
| conditional κ (complete admission) | `0.00173044836020763546173999…99` | `0.00173057843726624681873999…99` |

The new idle histogram is the fixed-inventory optimum, and its root is the "ideal
fixed-inventory packing root" quoted in PR3734's PROOF.md as infeasible on the fixed clock.

## The ceiling certificate

Per owner replica the inventory is fixed by PR3734's supplier and template, whatever the
clock or replica count: nine calls of 408 helpers `{4:26, 5:2, 6:18, 7:53, 8:96, 9:213}`,
idle bins 672 × rank 8, 448 × rank 16, 448 × rank 32, 448 × rank 48, the local profile
`{1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}` per call and 896 live families of rank 73. Each
helper takes its width in one idle bin and each remainder l > 0 is paid as one rank-l child,
as in `owner_audit.py`.

- The root is unique. `F(a) = Σ n_r r^(1−a) − 896 T 73^(1−a)` has the sign of
  `G(a) = Σ n_r r (73/r)^a − 65408 T`, strictly increasing since every paid rank is below
  73. So "root < a" is "F(a) > 0", and every term scales with T.
- F(a) is linear in the counts of bin patterns. Any dual `(π_w, μ_c)` with
  `π·p + μ_c ≤ h(l_p)` for every pattern p of every rank c bounds, by weak duality, the
  idle part of F for every packing: integer or fractional, with or without time windows
  and the one-helper-per-call-per-bin rule.
- The dual is solved exactly on the ten patterns of the ideal, with outward rational
  enclosures of `r^(1−a)` from PR3734's `rational_price.py` at `a = root_upper =
  0.001730578437266246818741`. All 2551 patterns of ranks 8, 16, 32 and 48 are dual
  feasible (minimum reduced cost exactly 0) and the bound on min F is positive
  (≈ 5.3e-20 per replica).

Hence every owner fill of this inventory has root below `0.001730578437266246818741`,
while this package's fill has root above `0.001730578437266246818740`. Controls: at
`root_lower` the same certificate gives a non-positive bound, and shifting the width-9
dual by 10^-30 makes it infeasible.

## Why PR3734's clock lost 8.65 bill units

A clock fixes for each owner replica nine stage times τ0 < … < τ8. The nine idle child
pairs (224 bins each) are open on fixed stage windows:

| children | rank | window |
|---|---|---|
| 0, 2 | 16 | (−1, τ1] |
| 1, 3 | 8 | (τ1, τ2] |
| 4, 6 | 32 | (−1, τ3] |
| 5, 7 | 8 | (τ3, τ4] |
| 8, 10 | 48 | (−1, τ5] |
| 9, 11 | 8 | (τ5, τ6] |
| 12, 13 | 48 | (τ2, τ8] |
| 14, 15 | 32 | (τ4, τ8] |
| 16, 17 | 16 | (τ6, τ8] |

Both providers have the same native widths in the same helper order, so every call
supplies the same 408 helpers and the clock only shapes the windows. For one width,
assigning helpers to interval windows is feasible exactly when every tick interval [A, B]
supplies at least the demand of the windows it contains (Hall). `construction/hall_lp.py`
solves the resulting LP at single-tick resolution, generating these rows and the patterns
on demand. It relaxes integrality and the per-call rule, so it bounds a given clock from
above; it accepts PR3734's own fill (every Hall row holds) and returns the ideal when the
Hall rows are dropped.

On PR3734's clock it stops at `0.0017304575193851`, only 9.2e-9 above the actual fill:
the clock, not the solver, cost 8.0 of the 8.65 units. The binding rows were a start cut
for width 7 (b = 359) and end cuts for widths 4, 5, 8 (b = 2655). Each stage-1 call closes
its owner's rank-16 pair (−1, τ1], whose ideal content is 224 × (7, 9), while every call
supplies 53 width-7 helpers, and 8 replicas reach τ1 between ticks 40 and 47. Once the
start is throttled the LP reaches the ideal and the end cuts stop binding, with the tail
of the clock unchanged.

## The rule

`clock.py`: greedy merge of PR3734's call list. At tick t the next call is the first
listed call whose replica has placed every earlier stage, except that a stage-1 call
waits while it would raise the number of placed stage-1 calls above `53/224 · (t + 1)`
(integer test `224 (placed + 1) > 53 (t + 1)`). Stage-1 calls move later by at most 114
ticks and other calls earlier by at most 36. Coverage and per-replica stage order are
kept, which is all `owner_audit.py`, `admit544.py` and the block-norm context require of a
clock; the block-norm helper/data alias premise holds because τs never lies in a window of
its own replica's pair `stage_pair[s]`, and `verify.py` checks it on every role.

Tighter ratios (0.9 and 0.8 × 53/224) create one-tick windows and lose again. Moving every
stage-8 call into a final block on top of the throttle also reaches the ideal (2591 calls
moved, late windows of at least 376 ticks); the smaller change is kept.

## Construction (provenance, not rerun by the verifier)

1. `construction/hall_lp.py` on the changed clock, with the per-call rows of step 2: the
   LP optimum is integral (3061 classes with one pattern, 179 with two or three), an
   alternative vertex of the ideal with the same idle histogram.
2. `construction/build_fill.py` places helpers tick by tick **in reverse time**, serving
   first the open class that opens latest, so that the residual flood falls at the start
   of the clock, where the 1080 classes (−1, τ] are all open; there bins are filled
   emptiest first. Forward deadline order fails: the classes that close last are then
   filled by the last few calls, one helper per bin. For the last 40 ticks the LP also
   carries the per-call matching condition (for each set S of widths, at least
   Σ_{w∈S} s_w open bins with a slot in S); 12 ticks were not enough on this clock because
   its tail stays compressed.
3. `owner_audit.py` replayed unchanged on the result.

Environment: CPython 3.12.14, numpy 2.5.4, scipy 1.18.1, highspy 1.15.1 (macOS arm64).
The solver comments are in French.

## Reproduce

```sh
python3 scripts/research_package.py --package research/staged544-clock-ceiling --check-only
python3.12 scripts/research_package.py --package research/staged544-clock-ceiling
```

`verify.py` (standard library, about 15 s) regenerates the clock from its rule, runs
PR3734's byte-pinned `owner_audit.py` on the changed `ORDER.json`, `FILL.json.gz` and
`PROFILE.json` beside PR3734's unchanged DISPATCH, NATIVE, PLAN and TEMPLATE inputs,
checks the helper/data alias premise, encloses the root with PR3734's `rational_price.py`,
checks the ceiling certificate, binds the recorded complete admission to these inputs, and
rejects six semantic controls: PR3734's clock with the new fill, a same-replica stage swap,
a bracket shifted by 10^-24, one idle rank-48 child split into 47 + 1, the certificate at
`root_lower`, and a dual perturbed by 10^-30.

## Complete admission

PR3734's own `full_replay.py --reuse-current-native` ran end to end from a copy of
`research/staged544-producer-return` whose `inputs/ORDER.json`, `inputs/FILL.json.gz`,
`inputs/PROFILE.json` and `PRICE.json` were replaced by this package's files (nothing else
changed; the pinned replay archive was reused as is). Recorded in
[evidence/RELEASE.json](evidence/RELEASE.json):

- `PASS_STAGED544_COMPLETE_CONDITIONAL_RELEASE`, admission
  `PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE`;
- conditional κ = `0.0017305784372662468187399999999999999999999998999999999999999999999999`
  (root lower end − 10^-46 − 10^-70, as for PR3734);
- stages owners 17 s, parent-lift 39 s, rebind 3 s, discovery 352 s, both outer ledgers,
  release 553 s (CPython 3.12.14, numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, mpmath 1.3.0,
  macOS arm64).

`verify.py` does not rerun it; it binds the record to this package (input hashes, profile,
headline = root lower end − 10^-46 − 10^-70, strict gain over PR3734 and PR3682). Native
chains and retained ancestry were reused under their pinned receipts; no fresh native replay
or third-party review is claimed.

## Scope and remaining obligations

Conditional finite construction in exactly PR3734's sense: every inherited all-size
compiler, realization, hosting, precision/recovery, analytic and BIT assumption of PR3734
and its chain remains. The ceiling certificate is scoped to this supplier, idle-child
template and paid-remainder rule; it says nothing about changed words or templates. No
unconditional theorem, formal verification or selected-frontier change is claimed. If
PR3734 changes head, this package must be rebased and rerun.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- **Raise the ceiling.** The packing of this supplier is now provably at its cap, so a
  gain needs a changed T360 inventory (child ranks or counts) or word. First step: price
  candidate inventories with the fixed-inventory LP (`construction/hall_lp.py` without
  Hall rows, or the dual of `ceiling_certificate.py`), then with a throttled clock.
  Blocker: physical stock, coverage law and template checks of the complete admission.
- **Other chains.** Do other chronological owner fills of this model (for example
  PR3682's T360 incumbent) fall short of their own fixed-inventory ceiling because of the
  clock? First step: run `construction/hall_lp.py` on the chain's ORDER.json and act only
  if its exact per-tick LP is below the ideal. Blocker: the 53/224 ratio belongs to this
  template's rank-16 (7, 9) closures; PR3694 reports that PR3633's T488 allocation already
  attains its ceiling.

## Credit

Prepared by Erwan Secousses (ChaloupeMusic), at human direction, with substantial
assistance from Claude (Anthropic, Claude Code). Builds directly on dataisfire's PR3734
(staged544 producer return, owner audit, rational price, fixed-inventory ideal and the
open question answered here) and, through it, PR3682 (zxv, retiming and T360 framework),
PR3638 (chronological allocation and integral network construction), PR3605 (staged
entry), PR3687/3693 (retained independent interpreter) and the authors credited in
PR3734's SOURCE-CREDITS.md. PR3802 and PR3795 (hexapode) are concurrent work; PR3802
reached the same κ first. Apache-2.0.
