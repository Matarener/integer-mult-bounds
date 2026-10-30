## Summary

This follow-up to merged PR #799 resynthesizes the fourteen dimension-four A-prefix blocks of the frozen X4 word with exact dyadic elementary operations. The scalar map, every stored frame, B segment, cleanup, local paid profile, owner map, and conditional exponent are unchanged.

- A prefix: 4,283 → 3,528 gates (−755).
- Global real-component invoice: 13,909,392 → 13,536,960 (−372,432; 2.6776%).
- Local adapters: 380,784 → 368,704.
- κ remains `0.001661634653669567`.

## Verification

`verify.py` replays the package global verifier against the current main checkout. The frozen word and receipts have passed 728 arbitrary columns in both orientations, 25 local negative controls, 2,949 phase edges, 224 endpoint adapters, the complete owner/invoice audit, both exact moment engines, all 47 outer inequalities, and the PR589 bit controls.

This is a finite circuit-cost contribution and does not claim a new exponent or an unconditional multiplication theorem.
