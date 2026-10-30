# Exact universal axis cutoff for the CRT reservoir envelope

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
For every fixed ambient parameter p and allowed dyadic axis count d, the
largest batch over all accepted precisions and width patterns is exactly
floor(d/6400), and a finite all-wide layout attains it. Consequently the
inherited conservative factor-3 envelope fits the printed repair allowance
for every such layout exactly when

```text
c = ceil(log2(p+2)),
M = floor(p 2^(64c) / (19200 (p+2)^64)),
d <= 6400(M+1)-1.
```

Every larger allowed d has an explicit accepted failure witness. Thus no
cutoff in p alone covers the constructor's unbounded axis counts. This
settles a new uniform capacity question beyond the predecessor's individual
layouts. The proof is in [PROOF.md](PROOF.md), including the exact hypotheses
and an attaining precision. It does not reverify a predecessor theorem.

For example, at p=131070 and d=65536 every width pattern passes through
precision 36, while the all-wide layout fails at precision 37. The exact
ratios to the allowance are 3840/4369 and 4480/4369, respectively. At
p=2^24-2, the largest axis count covered uniformly in precision is 2^22;
2^23 fails at its explicit attaining precision.

These are statements about the conservative printed majorant. A failed
majorant is not a counterexample to actual repair, the smaller error bound
or the real E polynomial. No physical supplier, selected-frontier change,
new kappa or complete multiplication theorem is claimed.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/reservoir-universal-axis-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/reservoir-universal-axis-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reservoir-universal-axis-cutoff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reservoir-universal-axis-cutoff --check-source-history
```

Substitute another CPython 3.12 executable as needed. The direct marker is
PASS_RESERVOIR_UNIVERSAL_AXIS_CUTOFF. Default replay is read-only and compares
the entire generated [receipt](RESULT.json), including package/live-input
SHA256 hashes. `--write NEW_PATH` generates a new receipt and refuses an
existing file. Source pins and provenance are in [SOURCES.json](SOURCES.json).
The checker needs neither Git nor network at runtime. It imports no
predecessor verifier and does not run the descriptor census or repair engine.

The finite checks cover 74,880 precision rows, 1,152 attainment seams, all
393,222 width-count patterns in six boxes, 1,464 capacity-neighbor probes
at 732 ambient parameters, four actual source Layout fixtures and fourteen
domain/source/receipt controls. The
unbounded quantifiers come from the written floor argument, not from the
finite probes. [VERIFY.json](VERIFY.json) registers normal and optimized
warning-strict commands. Code constraints and bounded runtime deviations
are recorded in the proof.

## Open next questions

1. Optimize the exact published window factor instead of the conservative
   constant 3. Start with the batch staircase and decreasing correction as
   precision varies. Those competing terms are not optimized here.
2. Bind an enclosing physical caller's reached p,d,ell values to this
   criterion and the charged E envelope. The real evaluator, repair,
   routing, restoration, native and outer obligations remain open.

Structured first steps and blockers are in [TASK.json](TASK.json).
Independent human and formal proof-kernel review are unclaimed. No Lean,
Docker, selected cold replay or complete multiplier execution was run.

## Source context and credit

Base: canonical main 3f0152a32eeebac0df11946dbd50cabe5a7f7839, priority
revision 8. The selected conditional kappa remains .003125804. The
formal-interface-lemma card is changed to this original arithmetic theorem
rather than a formalization or audit. The known-working selected binding
command passed; it was orientation only.

Credit Hiroki KUMAZAKI for [PR4174's constructor](https://github.com/CrocSwap/integer-mult-bounds/pull/4174),
James Reed for [PR4923's factor 3](https://github.com/CrocSwap/integer-mult-bounds/pull/4923),
[PR4925's ratio](https://github.com/CrocSwap/integer-mult-bounds/pull/4925)
and [PR4926's edge comparison](https://github.com/CrocSwap/integer-mult-bounds/pull/4926).
The compact-switch density/room premises in PR4646 and PR4328, Cinna Davis's
PR4100 CRT framework and their retained predecessor lineage keep their credit.
Integer division and monotonicity are standard. The new step is the exact
unbounded precision optimization, sharp axis-capacity criterion and explicit
failure construction for this envelope. No literature-priority claim is made.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267742).
Overlap covered live open PRs, recent account work, active hub claims,
local reservations, distinctive main README formulas and merged PR bodies.
Unpublished work and historical diffs outside those searches remain limits.
Only this new package is changed; frozen inputs and contributor notices remain.
