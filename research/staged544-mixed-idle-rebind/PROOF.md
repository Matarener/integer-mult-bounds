# Idle cost that the two-provider rebind does not charge

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Sources

Canonical base `bb4bccbf42844d2801487450727c2f63e10d1d0f`. The fill, order, dispatch, template, plan, helper origins and four words are the bytes of PR #4088 at `72d7efc181edb21806a878f174847c96dd410ab0`, checked by SHA-256 in `verify.py`. `vendor/rebind.py` is the unmodified file from the PR #3815 replay archive, SHA-256 `faf283eb4edd2e6a1ccb40b3cb3ba30ae54338eaf5ea0a10d84d11d7939502af`.

The predecessor global profile is PR #4085's published histogram. Its idle is that histogram minus `3240` copies of the three-entry local profile.

## Scanned invoice

Helper frames are ranked over `F_2^9`. On both orientations the three-entry and four-entry width vectors differ only at origin index 367, register 601, where the width falls from 8 to 7. The declared local profiles agree with that one-unit mass drop:

`L3 = {1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}`, mass 5157,

`L4 = {1:2489, 2:713, 3:227, 4:99, 5:20, 8:8}`, mass 5156.

The published dispatch is exactly the rule `(109 t mod 324) < 109` on the retained 3,240-call order: 1,090 fourth-entry calls and 2,150 three-entry calls. Walking every hosted row against the template windows gives idle

`I = {3:22783, 5:1625, 48:138492}`

and complete profile `2150 L3 + 1090 L4 + I`, which is the #4088 histogram. Total paid rank mass is `65088 * 360`.

The #4085 idle is `{3:22842, 5:1890, 48:138438}`. The difference is `-59 H3 - 265 H5 + 54 H48`, rank mass `+1090`, matching the local saving `1090 * 1`.

## Why the inherited rebind rejects this invoice

`rebind.py` sets `locs = {gauge44, extra}` and, when a provider's widths change, assigns that one vector to every `per_call_widths` entry of the provider. Inside `gauge44` the scanned calls use width 8 on 1,040 calls and width 7 on 528 calls. Inside `extra` the split is 1,110 and 562. One vector per id cannot match both.

The same function adds `n_pid * local_profile[pid]` for a single integer profile. The fourth-entry calls contribute `2 * 528 = 1056` extra rank-1 cells on `gauge44` and `2 * 562 = 1124` on `extra`. Neither count is divisible by the orientation's call count (1,568 and 1,672). No integer local profile per orientation reproduces the mixed local histogram.

Idle is read from the shipped construction and described in the file as the unchanged idle remainder. Substituting the mixed local sum and the #4085 idle produces a different histogram, lighter by exactly 1,090 rank units:

`{1:8060060, 2:2310120, 3:751872, 4:327210, 5:66690, 8:25920, 48:138438}`.

## Moment consequence

Let `M(k) = Σ n_r r^(1-k) - (896 * 360) 73^(1-k)`. Logarithms use the odd artanh series with an explicit geometric tail; `exp(-x)` uses the alternating Taylor theorem. Both are reimplemented in `verify.py`.

For the scanned profile, `M` is negative at `0.001730979115670792472760` and positive at `0.001730979115670792472761`. The same enclosure accepts the #4085 bracket and rejects that profile at the new bracket. After the retained outer padding `10^-46 + 10^-70`, the scanned endpoint still exceeds the #4085 upper endpoint by more than `8.69 × 10^-9`.

For the frozen-idle profile, a 24-step bisection isolates a sign change in

`(7328391261/4194304000000, 5862713009/3355443200000)`,

about `0.00174722463155`. The lower end exceeds the scanned upper endpoint by `259928254034166138949/16000000000000000000000000 > 1.62 × 10^-5`. Charging the scanned idle, in particular the 54 rank-48 cells, is what pulls the root back down. An ordinary release that kept the shipped idle would be certifying a different, lighter invoice.

## What this does not prove

The scan uses the words' declared local histograms and checks them against the frame-rank mass. It does not replay scalar semantics or the five native stages. It does not execute `admit544.py`, the outer ledger, or #4100's unconditional writeup. Passing this verifier does not admit a selected κ.
