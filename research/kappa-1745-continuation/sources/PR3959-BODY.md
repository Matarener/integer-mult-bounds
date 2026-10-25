**Author-checked conditional candidate, stacked on #3958.** #3958 composes #3955's complex side with #3647's R437 bit supplier. This applies #3939's cross-replica owner map to R437. Draft.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| #3958 | 0.0017411725885452521674224 | R437 0.001736646042038446578551 | bit | 0.001736646042038446578551 − … |
| **this** | 0.0017411725885452521674224 | **pooled R437 0.001736738651088946052684** | **bit** | **0.001736738651088946052684 − 10⁻⁴⁶ − 10⁻⁷⁰** |

**+0.00533% over #3958.** About 4.4e-6 of complex headroom remains.

### Idea
Per replica, R437 keeps one two-residual window-6 family (idle 26) and 12 empty 42-families. Pooled over 32 replicas, the window-6 slack is 32·63 = 403·5 + 1 places. Residue t = 1 in mightyOil's `bit-partial-width7-optimum` table gives the pooled32 slot optimum: 403 empty 42-families plus one empty capacity-14 copy.

This package builds that optimum explicitly with **63 moves**: the 62 two-family residuals of replicas 1–31, plus replica 0's window-8 residual (stage 8, inside window 6). They fill replica 0's two-residual family and its 12 empty families. The idle bill changes by {2:+13, 6:−1, 14:+1, 26:−32, 42:+19}. Rank mass and maxchild are unchanged.

### Verification
- **Inputs:** #3647's `GLOBAL-TEMPLATE.json.gz` is vendored; its content SHA-256 equals `template_content_sha256` in #3647's `EXPECTED.json`.
- **Role audit:** `verify.py` is independent of `build.py`. It rebuilds all **125,856** R437 hosted roles and checks window, inactive host pair, width-8 extent, disjoint cells, compact prefixes and hosted-exactly-once.
- **Baseline:** it reproduces #3647's `EXPECTED` profile and endpoint exactly.
- **Pooled endpoint:** accepted at c and rejected at c + 10⁻²⁴, with the fallback envelope.
- **Composition:** #3955's complex root is rechecked; κ has the bit side binding.
- **6/6 mutation controls rejected.**
- **Registered replay:** `PASS_REGISTERED_RESEARCH_PACKAGE`.

### Scope
This carries the same cross-replica owner hypothesis as #3939; #3647's native hosted emission was not run with these owners. It inherits #3647's R437 interfaces (admission pending) and #3955's complex-side hypotheses.

Credit @ai-nanachi (#3647), Ali Romman (#1043), Sagar Thakrar (#3700/#2423/#1023), mightyOil (#1281) and the #3955 stack. Complex-side ideas in the stacked predecessors were done with help from OpenCode (Space bunny free). Prepared by Rohan Arun with Anthropic Claude assistance.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011S35E2acyQDaVRjPRw4TDy
