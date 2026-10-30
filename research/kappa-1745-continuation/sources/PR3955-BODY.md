**Author-checked conditional candidate, stacked on #3939 (→ #3934 → #3251 → … → #3148 → #3133).** Draft. The full verification run is still going.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| #3939 | 0.0017348651784727109982331 | pooled R438 0.001734900431583947157341 | complex | 0.001734865178472710998233 − … |
| **this** | **0.0017411725885452521674224** | pooled R438 0.001734900431583947157341 | **bit** | **0.001734900431583947157341 − 10⁻⁴⁶ − 10⁻⁷⁰** |

**+0.00203% over #3939.** That is the whole remaining window up to the pooled bit endpoint. The complex root itself rises by **+0.36%**, so κ is now capped by the bit supplier with about 6.3e-6 of complex headroom.

### Idea: hosted frame selection (new hypothesis)
Since #3190, a bin hosting `used` helper cells kept them on the recipe prefix `[0, used)`, and its idle remainder was the recipe suffix `[used, cap)`. After #3934:
- 94,656 rank-1 hosted remainders keep only an axis that fails PR1252's translation rule;
- yet every one of the 134,320 unmodified rank-1 hosted bins has a translation-commuting axis somewhere in its frame.

This package lets the hosted cells take **any** `used`-subset of the frame. The remainder is chosen per bin as the axes most able to move. #3934's pipeline then runs unchanged: exact phase 1, star phase, greedy phase, hosted receivers. All moves keep PR1252's commuting rule, role exclusivity and the rank-51 cap.

The result is 521,798 axis moves. Rank-1 remainders fall from 147,220 to 79,440, and rank-51 children rise from 129,006 to 160,932. Rank mass is unchanged.

### Verification
- `verify.py` is independent of `build.py`. It checks:
  - donated axes come from the donor's own frame, within the `cap − used` idle budget;
  - each hosted receiver is orthogonal to its whole frame;
  - role exclusivity, orthogonality at receipt, the commuting rule and the rank-51 cap;
  - the profile, the rank mass and the exact root bracket;
  - the pooled R438 endpoint, by rerunning #3939's role audit;
  - κ with the bit side binding.
- **9/9 mutation controls rejected:** over-budget donation, hosted-frame conflict, a non-commuting axis, a foreign axis, an axis moved twice, a receiver that also donates, a dropped move, the next root grid point, and κ above the bit cap.
- **Determinism:** two builds give byte-identical BINS and MOVES.
- **Registered replay:** `python3.12 scripts/research_package.py --package research/rank7-idle-frame-select` → `PASS_REGISTERED_RESEARCH_PACKAGE`.

### Scope
**New hypothesis: the hosted cell-to-axis map is free.** This is stronger than #3190's prefix convention. It also inherits #3934's hosted receivers, #3190's hosted donors and #3939's cross-replica bit owners.

**Not rerun:** native admission, the overlay-aware T74 controller audit, and the outer release. All inherited obligations remain.

Done with help from OpenCode (Space bunny free) for ideas in the stacked predecessors. Prepared by Rohan Arun with Anthropic Claude assistance.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011S35E2acyQDaVRjPRw4TDy
