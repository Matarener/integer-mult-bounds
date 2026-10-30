# Which construction component is ready to remove?

The best immediate opportunity is [PR #5644](https://github.com/CrocSwap/integer-mult-bounds/pull/5644)'s obsolete late helper cleanup, combined with [PR #5643](https://github.com/CrocSwap/integer-mult-bounds/pull/5643)'s A2 exchange. Its exact input-basis preparation and last-read cancellation remove contacts that force otherwise unused native stops. The resulting common word supports **conditional κ = 0.00310644468** in the fresh complete replay. This is an actual functional replacement with a recomputed invoice.

The original summarized list ran through PR5612; later PR5627 consumed its compatible improvements. Current exact sources are PR5643 `a3ff5c628bfc8825553d62d913f3e91f75d6825f`, PR5644 `c5871955d89bf73506fd68b0a5bf1cf2b3153c02` and their common PR5627 source `ed4dc88a09a7d201971f6603b8c2074e95dd9c32`. All screens below bind the emitted common word, compressed SHA256 `e94809cecf9e9cba56dd7a8a11ff1edeedc4c34013ff6caebdaf3b021351cf8c`.

| Rank | Component and lineage | Complete accounting and decision |
|---|---|---|
| 1 — positive | Late helper cleanup, [#5644](https://github.com/CrocSwap/integer-mult-bounds/pull/5644), plus A2, [#5643](https://github.com/CrocSwap/integer-mult-bounds/pull/5643) | The functional common word retains all targets. Against PR5643 it replaces 54 complete H1+H5 paths by H6; against PR5644 it retains 18 A2 rank exchanges. Extra ordinary work is charged. κ increases over both. |
| 2 — changed interface needed | Owned delivery replaced by a complementary public relay, [#5605](https://github.com/CrocSwap/integer-mult-bounds/pull/5605)/[#5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612) | Eight paid H7 deliveries remain. All eight fail free reconstruction from current public values at their first read's literal chart and time. A new preparation or source window could still replace one, but must charge storage, routing, cleanup and any native access. |
| 3 — changed graph needed | Vacating an intermediate frame, [#5561](https://github.com/CrocSwap/integer-mult-bounds/pull/5561)/[#5601](https://github.com/CrocSwap/integer-mult-bounds/pull/5601)/[#5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) | Their earlier compatible retimings are already consumed. A2 shows a changed noncommuting dependency graph can escape a fixed-contact screen. The next useful object is one specific last read that can be removed or moved by an exact identity. |
| 4 — fixed-word route exhausted in tested scope | Independent helper split, [#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)/[#5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602), with dyadic completion [#5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611)/[#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) | The complete rational prefix/suffix pairing vanishes at every tested common-chart cut for all 411 ZERO-to-FULL helpers. There is no hidden dyadic unit ideal in this scope. A changed word or charged mixed-boundary interface is required before another basis search can pay. |
| 5 — no recursive saving by deletion alone | Prepared zero-prefix storage, [#5606](https://github.com/CrocSwap/integer-mult-bounds/pull/5606), and inverse/main wrappers | Prepared role 751's three lifetimes have zero paid MOVEs, and inverse/main adapters already add zero recursive jobs. Removing them alone changes ordinary constants. Their usefulness would be enabling a different charged word, not deleting a recursive bill they do not contain. |

The older [#5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) coupled restoration adds 144 H8 paid calls and 144 H8 productive targets. Deleting both is rankwise neutral; retaining the productive credit while deleting its paid realization would need a new source-compatible correction. The larger [#5440](https://github.com/CrocSwap/integer-mult-bounds/pull/5440) headline remains outside this ready list because its priced native primitive and actual physical caller are not matched.

## Exact negative screens and their limits

[Owned-delivery evidence](analysis/owned-deliveries/COMPOSED-CENTRE-RECONSTRUCTION.json) comes from a separate rational interpreter that checks all 752 scalar endpoint rows and owned zero exits. The eight H7 source rows have rational rank eight. At their first public use, the available same-frame public spans have ranks 1, 2, 1, 1, 1, 1, 1, 1; each delivery value has a nonzero residual. This excludes an ADD-only substitution at those exact frames/times. It does not exclude changed windows, preconditioning, paid transport or joint native maps.

[Joint-cut evidence](analysis/helper-cuts/ALL-EVENT-CUT-SCREEN.json) covers 8,847 event/chart states at 7,253 distinct cuts, all actual cohorts of sizes 1–16 and all 411 ZERO-to-FULL helpers. Only 18 states have nonzero prefix and suffix spaces; every full rational boundary pairing matrix is zero. The [scope proof](analysis/helper-cuts/README.md) explains the exact kernels, unaffected-chart state compression and COPY handling. A separate backward-prefix/forward-suffix checker verifies all 18 witnesses; it does not independently recompute every empty kernel.

Reproduce the lightweight checks from the repository root:

```sh
python3.12 -I -O -B research/p104-a2-neutral-cleanup/analysis/owned-deliveries/check_composed_centres.py
python3.12 -I -O -B research/p104-a2-neutral-cleanup/analysis/helper-cuts/check_report.py research/p104-a2-neutral-cleanup/WORD.json.gz
```

The discovery scanner can explicitly regenerate its own receipt:

```sh
python3.12 -B research/p104-a2-neutral-cleanup/analysis/helper-cuts/scan_all_cuts.py research/p104-a2-neutral-cleanup/WORD.json.gz
```

## Why apparent accounting deletions are not automatically gains

The retained caller's 3,120 whole idle jobs supply part of its actual endpoint action. Its 15 isolated query shears supply 1,560 paid H1 jobs; literal deletion changes the exact formal caller endpoint. They are not disposable line items. The BIT side is currently slack above this complex ceiling, so a stronger BIT component alone does not raise the complete κ.

The useful distinction is whether a functional replacement removes paid jobs **after** surrendering any lost productive targets and charging new ownership/native access. PR5644's last-read identity and PR5643's changed A2 graph satisfy that test together. Merely dropping a wrapper, deleting both halves of an equal paid/target entry, or treating an independently prepared input as free does not.

Scientific credit remains with the linked contributors and the complete source notices. The coordinating agent and three subagents produced this triage with substantial OpenAI Codex assistance. The [skeptical composition review](analysis/owned-deliveries/COMPOSITION-SKEPTICAL-REVIEW.md) is scoped agent scrutiny, not independent human or proof-kernel acceptance.

## Open next questions

The strongest remaining bounded task is one changed complementary-public-value window for a named H7 delivery. First show the source survives to its consumer under the changed chronology; then emit its whole restoration and native bill. A changed scalar dependency that makes a fixed helper boundary pairing nonzero is another distinct route. The current screens do not supply either construction.
