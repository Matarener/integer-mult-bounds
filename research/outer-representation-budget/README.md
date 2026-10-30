# Quadratic prescribed guards cannot fit the current outer assembly

**Scoped proof and exact arithmetic evidence. No new supplier or κ.**

The current nine outer rows do not turn a favorable supplier moment into a multiplication theorem. A proposed representation must also fit its precision, total simultaneous stock and small-width fallback into the actual caller.

For the explicitly declared contract in [PROOF.md](PROOF.md), let U and B be the completed above-cutoff complex and BIT saving budgets, and put

$$M=\min(U,B,1/32),\qquad s=\frac{\zeta}{1-\nu}.$$

The prescribed precision guard grows as `d^ρ polylog(d)`, and the complete logarithmic stock reserve at active width h is bounded by `h^ν p^ζ polylog(p)`, where ρ≥1 and 0≤ν<1. The outer schedule retains its complete-field, restoration, native, compiler, tape and analytic premises. A cutoff `p^t` with t>s is processed individually, with its cost charged.

**The exact strict exponent region is**

$$\boxed{\rho(1+s)<2,\qquad
\mathrm{OLD}<\kappa<\min\left(M/\rho,\ 1/\rho-s\right).}$$

OLD is the inherited ledger's bookkeeping threshold, not a general lower limit. The proof supplies rational parameters for every interior point and positive-weight obstruction identities for the two stock/fallback boundaries. The one changed outer saving is `group_scans: 1−ε+β → 1−ε+β−t`; the strengthened row also pays the full-width residual.

For some κ>.01, this policy needs `M>.01ρ`, `s<1/ρ−.01`, and `ρ(1+s)<2`. In particular, quadratic or larger **prescribed** guards cannot satisfy the retained membership geometry even with ideal suppliers. A loose O(d²) upper bound is not a precision lower bound; a tighter actual envelope or another representation can escape this obstruction.

## Significance for researchers

This gives a representation-level admission target before another supplier search. Linear precision with ζ=0 recovers [Nick Petalas](https://github.com/petalas)'s [PR5984](https://github.com/CrocSwap/integer-mult-bounds/pull/5984) region `OLD<κ<M`, which is credited rather than claimed again. Precision-dependent stock introduces a paid fallback term that a largest-call fit test misses. The selected PR6030 remains complex-limited at κ=.003125804 with admitted BIT .0034; the hypothetical examples do not raise either budget.

A concrete falsification sets U=B=.02, ρ=1, ν=1/2 and ζ=.4975. At κ=.011 the original 58 predicates, the two added precision checks, total-stock fit and both cutoff checks all pass. Only the charged fallback row fails: its saving is `16993/7000000 ≈ .00242757`. The exact supremum of this policy is .005. This falsifies a free-fallback screen, and alleges no fault in the retained ζ=0 construction.

## Evidence and scope

[RESULT.json](RESULT.json) records 4,056 rational witnesses, all 63 predicates at every witness, 300 arbitrary-parameter checks of the obstruction identities, independently restated nine-row formulas, strict-boundary exclusions and the false-positive control. Examples include points 10^-24 below their supremum and hypothetical κ=.011 contracts with linear and 3/2-power precision guards. The written proof supplies universal claims; finite samples corroborate them.

All live sources are SHA256-authenticated before evaluation. The actual source ledger is executed unchanged from its authenticated text. Normal and optimized registered CPython 3.12 replays are read-only. [SOURCES.json](SOURCES.json) pins canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`; the selected record and task catalogue are historical provenance. [TASK.json](TASK.json) records the explicit backward-interface assignment and changed scope. Coordination: [Discussion6056](https://github.com/CrocSwap/integer-mult-bounds/discussions/6056).

No finite helper word, changed supplier, native map, fast fallback, complete rounded multiplier, selected replay, independent human review or proof-assistant check is supplied. Inherited assumptions remain. The theorem characterizes the declared strict accounting policy, not all representations or multiplication algorithms. A tighter guard, smaller stock, faster fallback or changed membership schedule requires reassessment.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/outer-representation-budget
python3.12 -I -B research/outer-representation-budget/verify.py
python3.12 -I -O -W error -B research/outer-representation-budget/verify.py
```

Expected final marker: `PASS_OUTER_REPRESENTATION_BUDGET witnesses=4056 predicates=63 dual_checks=300 RECEIPT_MATCH no_new_kappa`. `--emit` prints a fresh receipt without modifying files.

## Open next questions

1. **Bind an actual changed supplier to the growth contract.** First extract a complete chronological precision/error envelope and the product of simultaneous reserves at its real outer calls. This determines whether κ>.01 needs a different representation. Actual suppliers and their error/runtime guarantees remain missing; a raw moment or local grid statement is insufficient.
2. **Replace the expensive individual-axis fallback.** First give one completed routine below `p^(ζ/(1−ν))` with a paid better exponent, arbitrary dirty inputs, storage and returned grid. That could improve the `1/ρ−s` cap. No such routine is implemented here.
3. **Change the membership/record interface.** First derive a complete alternative to the source cost `β+2(1−ε)<1`, including headers, source-prime arithmetic and tape scans. This is the precise route by which a quadratic prescribed guard could reopen. Faster membership arithmetic is not assumed.

The structured versions and blockers are in [TASK.json](TASK.json).

## Credit

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance in proof, code, verification and writing. Apache-2.0. [Nick Petalas](https://github.com/petalas) supplied PR5984's unchanged-ledger theorem. The source outer formulas retain [Vlado Vojdanovski](https://github.com/Vlado-V)'s PR1673 and [Jeremy Kothe](https://github.com/jeremykothe2)'s PR1758 and [Chafik Boukhalfa](https://github.com/chafreaky)'s PR1786 attribution, the radix-union/Strassen/fine-prime lineage and its notices. The PR4359 ledger, finite-template semantic-precision and complete-stock arguments, [DreamingOfClouds](https://github.com/DreamingOfClouds)'s PR6030 caller, and retained Harvey–van der Hoeven/OpenAI manuscript framework remain predecessor work. No frozen source is changed.
