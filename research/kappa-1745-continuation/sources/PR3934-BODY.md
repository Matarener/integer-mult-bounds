Conditional κ = `0.001734846264120199151475 − 10⁻⁴⁶ − 10⁻⁷⁰`, **+0.00176% over #3251** (0.001734815770385098563484). This takes the whole remaining window to the R438 bit endpoint. **Draft: full verification is running.**

| | complex root lower | bit | binds | κ |
|---|---|---|---|---|
| #3251 | 0.0017348157703850985634843 | R438 0.001734846264120199151475 | complex | 0.001734815770385098563484 − … |
| **this** | **0.0017348651784727109982331** | R438 0.001734846264120199151475 | **bit** | **0.001734846264120199151475 − …** |

## Change

After #3251, 149,514 rank-1 idle remainders remain:
- 107,356 fail #1252's translation rule, so no receiver can take them.
- 39,558 conflict with every unhosted child of their group, and the group's other children are all hosted.
- 2,600 conflict with every unhosted child.

Relaying through an unhosted child was tested and found nothing legal.

New in this PR is a fifth phase: an idle-remainder axis may move into the remainder of **another partially hosted bin** in the same (replica, port). The axis must commute with that bin's **full** recipe frame (hosted prefix plus remainder), with all stage X/Y translations and the terminal Y translation, and with both terminal translations. Receivers are capped at 51, and no child both donates and receives.

This adds 2,374 moves, 437,978 in total, mostly merging pairs of rank-1 remainders into rank-2 children. Rank mass is unchanged at `65088·740`.

## Verification

`research/rank7-idle-hosted-receivers-r438/verify.py` is #3251's independent verifier, extended for hosted receivers. It re-derives:
- every move's legality, including orthogonality to the receiver's hosted prefix;
- the profile and rank mass;
- the exact complex root bracket;
- the R438 endpoint;
- `κ = min(floor₂₄(complex), bit) − …`, with the bit side binding.

Nine mutation controls are rejected, including a prefix-conflicting hosted receiver. `scripts/research_package.py` passes locally under Python 3.12.

## Scope

This adds a new hypothesis: hosted remainders may *receive* axes, extending #3190's hosted-donor hypothesis. No hosted-controller argument is given.

Not rerun yet: the native admission, the overlay-aware controller audit, and the outer release.

The result is conditional on R438 (#1043 is still open) and on the full stack #3251 → #3200 → #3198 → #3190 → #3184 → #3148 → #3133.

Credits: Gonzalo-Mier (#1252), Guéorgui Maissouradze, Jeremy Diviney (#3148), dcharb78 (#3133), Marius-Paul Dumitrean (#2979), Ali Romman (#1043), Sagar Thakrar (#2423), DreamingOfClouds, eumemic, and OpenCode (Space bunny free) for ideas in the stacked predecessors. Prepared by Rohan Arun with Anthropic Claude assistance.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011S35E2acyQDaVRjPRw4TDy