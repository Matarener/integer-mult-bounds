# Draft tweet thread: conditional κ = 0.0023

Draft only; not posted. Credit details and scopes are in the
[contributor map](community-productive4359-contributors.md). Each numbered paragraph
is a suggested post; links can be attached to the relevant post.

1. New checkpoint in our community integer-multiplication project: κ = 0.0023, clearing 2⁻⁹. That gives O(n(log n)^0.9977), conditional on the retained OpenAI #109 framework. The construction and review are now on main. Huge community effort. https://github.com/CrocSwap/integer-mult-bounds/pull/4359

2. Lead credit to zxv for the breakthrough. Helper arrays can do useful work of their own. The hard part was compiling those unequal jobs into one valid recursive construction—with ownership, restoration and every cost accounted for. https://github.com/CrocSwap/integer-mult-bounds/pull/4359

3. Jacob Alan Sussman's mixed-target recursion supplied the key enabling idea. His Theorem 1G lets different arrays carry different-sized jobs. zxv built the explicit compiler and multiplication integration around it. https://github.com/CrocSwap/integer-mult-bounds/pull/4268

4. @RohanArun deserves major credit for the long incremental climb: native constructions, staged helper entries, owner schedules and packing. His #4181 checkpoint reached ~0.001731. The new saving is 32.9% larger—exponent saving, not measured speed. https://github.com/CrocSwap/integer-mult-bounds/pull/4181

5. Cinna Davis (@devslashurandom), David Ganz and Jeremy Kothe built essential parts of the complex-network lineage: staged helper entries, terminal-width-five words, native constructions and the outer framework. Their work carries directly into this result.

6. Marius-Paul Dumitrean's exact frame and joint-endframe work, and Erwan Secousses' staged-entry machinery and Hall-based allocation, helped supply the concrete networks behind the new recursion. This is a new mechanism built on a lot of prior construction work.

7. Credit also to Vlado-V for capped phase-cell fusion, @cfky_ for fine source-prime padding, and Zhihao Chen for semantic precision. These are parts of the surrounding machinery that lets a finite-network saving reach the multiplication bound.

8. On the binary side, eumemic and DreamingOfClouds supplied the punctured word and transport improvements. The new result retains that work while changing the recursive compilation and how the binary cover is applied.

9. Verification credit matters too: @ryansonjonathan contributed a separate exact flow/rank audit. Earlier interpreters and owner/pricing checks by Sagar Thakrar, roger-sato and Josie Elliston remain valuable parts of the project's verification history.

10. Ross Richardson's ceilings, Nick Petalas' reuse/pooling work, dataisfire's producer-return construction, and many others helped map what the old construction could do. Full credits, including the broader community, are linked here: https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-productive4359-contributors.md

11. Scope matters: the fresh replay passed 23 stages and checked 59 regenerated artifacts. We also reviewed the changed proof interfaces. This remains conditional mathematics—not a complete Lean proof or a practical multiplication benchmark. Independent review is welcome.

## Optional comparison wording

Against the last selected main-branch checkpoint (κ = 0.001672660197076918),
the gain in exponent saving is about **37.5%**. Against Rohan's later #4181
conditional checkpoint (κ ≈ 0.001730980256), it is **32.9%**. Do not mix the
baselines or present either percentage as a measured runtime improvement.

## Posting notes

No X handles are inferred from GitHub usernames. The three profile-confirmed
handles and Rohan's user-supplied announcement account are documented in the
contributor map. The lead contributor has no publicly linked X handle in the
checked GitHub profile. The full-thread credit list is intentionally broader
than the new PR's authorship: retained construction, comparison and verification
roles are distinguished in the map. No claim of independent human verification
or formal verification of the entire multiplication theorem is made.
