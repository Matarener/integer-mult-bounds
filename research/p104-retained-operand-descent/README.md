# Retained operand: conditional κ = 0.003128645

This package raises the conditional claim of
[PR6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144)
from **0.003128386 to 0.003128645**. The new gain is **0.000000259**
(about 0.00828%). This is a small gain from a changed paid profile.
The source is fixed at `5ec9b6dafc1ec54e2c0ca0771e8ed032f7888417`.
The branch starts at canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`.

The new operation order removes one stop from root register 772. Save helper
228 at frame 737 in register 770. Reader 451 can then receive the root at frame
595 before it adds that saved operand at frame 737. Clear the saved operand
before the existing use of register 770. All public outputs and productive
targets stay the same. The declared register count stays 29 and peak use stays
13. The extra lifetime and 12 scalar operations are charged.

For `H_r = r^(1-κ)`, the local paid change is
`H_1 - H_2 - H_4 + H_5`. It is negative for `0 < κ < 1`.
The complete caller uses this change 18 times. It still has 66,762 paid calls,
13,444 productive fields and rank surplus 760.

The raw crossing is strictly between **0.00312865201590** and
**0.00312865201591**. The claim leaves more than `7.01590e-9` of raw headroom.
The old PR6144 profile fails at the new claimed κ. This excludes an improvement
that comes only from a smaller rounding gap.

## Evidence and scope

[construct.py](construct.py) applies five guarded replacements to the pinned
source word. [PROOF.md](PROOF.md) proves the changed schedule and price.
[RESULT.json](RESULT.json) records the complete check. [VERIFY.json](VERIFY.json)
registers the replay. [VALIDATION.md](VALIDATION.md) records the environment and
the publication checks.

The verifier checks the full regenerated payload, all 799 input columns,
638,401 endpoint coefficients, a separate transpose calculation, native maps
and exact phases, main adapters, helper normalization and the physical caller.
Two rational interval engines check the price. The completion, compiler and
all 54 strict plus four functional outer inequalities are checked. Controls
remove or change the cache, the later addition, restoration and cleanup.

The five inherited assumptions remain: native operators at all column widths,
owned erasure, uniform compiler closure, precision and tape movement, and
analytic integer recovery. The uniform word at the stated threshold and the
rounded multiplier are not materialized. These are author checks. Independent
scientific acceptance remains open. The selected record stays at 0.003125804.

## Reproduce

Python 3.12 and its standard library are sufficient. From the repository root:

```sh
python3.12 -I -B research/p104-retained-operand-descent/verify.py
python3.12 -I -O -B research/p104-retained-operand-descent/verify.py
python3.12 scripts/research_package.py --package research/p104-retained-operand-descent
```

Use `--build-only` on `verify.py` for the exact endpoint and inventory checks.
That option does not check the full native and compiler chain. The full command
does not need Git or network access. It authenticates every file in the retained
PR5827 source archive before use. Its local checker is unmodified. The price
equals PR6144's price with the three declared edits in
[PRICING-EDITS.json](PRICING-EDITS.json).

Immutable input hashes stay exact. Regenerated gzip output is compared by every
decompressed payload byte, so different container headers are accepted.

## Coordination and credit

The canonical investigation is
[Discussion 5645](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19205459).
PR6144 explicitly left the reader 451/497 root-2 stop question open. This work
completes its reader 451 branch. The changed premise is a retained historical
operand and a changed addition order. The protected R22 and 102-contact event
sequences stay byte-exact. The overlap coverage and its limits are in
[TASK.json](TASK.json).

New construction, proof and checks: Ali Romman, with substantial OpenAI Codex
assistance. PR6144 and PR6143 are by DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. PR6030 and PR5907 retain that author's credit.
PR5827, PR5811, PR5802, PR5786 and their source authors retain all earlier credit.
The source reader follows DreamingOfClouds and Ali Romman. The portability
controls retain Douglas Colkitt and Maxime Fleury credit. [NOTICE](NOTICE)
retains the full source notices, including native, caller, compiler and BIT work.
All new work is Apache-2.0.

## Open next questions

- Can an independent reviewer confirm the changed chronology, full invoice and
  complete replay? Start with the five replacements and the cache controls.
  Author checks and hosted CI do not establish this acceptance.
- Can reader 497 avoid the remaining stop at frame 520? Its earlier operand at
  frame 519 is an extra constraint: frame 595 is not a subspace of frame 519.
  Start with an explicit paid schedule for both operands. A rank estimate or
  an available historical span alone does not satisfy this task.

The structured questions and their blockers are in [TASK.json](TASK.json).
