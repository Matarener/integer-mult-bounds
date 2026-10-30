# Disposition receipt: the #4436 direct-flow chain

**Claim type:** a source-bound overlap and disposition receipt (the overlap-receipt card). **No new κ.**
It makes no closures and no merge recommendations. It covers zxv's #4436 and the five follow-ups around
it, all open on base `2a13eb18`. `RECEIPT.json` records heads and package blobs.

## Disposition

Nothing is retained on main. Only #4436 edits files outside its package:
`docs/ci-verification.md` and `docs/research/current-status.md`. These conflict textually with the p17
chain's edits of the same files (see my #4474).

| PR | Head | What it establishes |
| --- | --- | --- |
| #4436 (zxv) | `56003680` | Direct overlapping flow (§2) and nested-width size bounds (§3). The exponent gate is open. |
| #4456 | `bbef80cd` | Independent check of §2: 9 recorded flows, the potential identity, exact `L(1000)`. |
| #4459 | `488a75a9` | Mirror identity (exact), and the rigorous boundary-share bound `β ≤ 0.321`. **It corrects its own first version.** |
| #4465 | `36d9c475` | The refined-induction ceiling `s*·g/(g + 1 + ln m)`. The growth of `g` comes from leaf exits alone. |
| #4467 | `30ff97c3` | Leaf walk: exact `√G` regime to depth 60; saturation observed (overshoot tends to `1/λ* = 133.3`); single-step cap about 0.00257 < `s*`; depth-variant diagnostics. |
| #4476 | `4e7022aa` | Independent check of §3: width factor, the exact slot identity `S + X + 2·matched = U(W+P)`, and `N log N` growth. |

## Withdrawn claim

The first version of #4459 (head `04da76eb`) claimed that the direct exponent gate reduces to a uniform
boundary-exit share. That claim is **withdrawn**. Leaf exits reach about `0.397N` and carry 85–92% of
the `t`-potential. The correction is at `488a75a9`.

## Where the chain stands

Under #4405's single-step refined induction, #4436's direct flow certifies about 0.0008 by
`N ≈ 3·10⁵`. By the leaf-walk saturation heuristic, it reaches at most about 0.00257 asymptotically,
and 0.0023 only near `N ≈ 10^{940}`.

Open:
- a proof of the saturation and of the stability of the shares;
- a multi-step exit test;
- the admissibility of a shallower lockstep depth, given its tiny low-source mass;
- a tighter constructive width.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-chain-receipt --check-only
python3.12 -B scripts/research_package.py --package research/direct-flow-chain-receipt
```

The verifier prints `PASS_DIRECT_FLOW_CHAIN_RECEIPT`.

## Open next questions

1. **A multi-step exit test for #4436's flow.**
   - *Why it matters:* the single-step test is capped below `s*`.
   - *First step:* substitute each exit's own flow once, and remeasure `κ` against `η`.

## Credit

- zxv's #4436.
- 1337isnot1337's #4405.
- Jacob Alan Sussman's Theorem 1G.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
