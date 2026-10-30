# Twelve physical slots for the P104 caller

The complete PR5812 word now uses **12 actual owned storage slots**, down
from 28 declared labels. Exact private liveness trimming also lowers its peak
from 13 to 12. The emitted word has 25,975 instructions and 29 lifetimes.
Its positive local scalar allowance falls from 225,026 to 224,976, a saving
of 50 per call or 900 over the retained 18 full calls.

This is a physical local word, not only an interval table. All public indices
remain fixed. Each private operand names one of the 12 reusable slots.
Every slot is initialized before use and cleared after its last use. Its
initial content can be arbitrary. No source cache is assumed to start at zero.

## Construction and exact scope

The constructor keeps every public operation. A reverse pass keeps each
private operation only if its result has a later retained read. COPY kills
the previous private value; INIT and CLEAR delimit independent lifetimes.
The remaining private events therefore have the same effect on every public
observation. Each retained INIT moves to the first retained use; CLEAR moves
to the last. Their chart is the chart at that exact event.

Apply the PR5763 allocator to those source-derived half-open lifetimes. It
assigns all 29 episodes to 12 slots. A separate occupancy sweep rejects
collisions. The retained simultaneous set at source time 27822 has width
12, so fewer slots cannot implement this fixed trimmed chronology. This
is not a minimum over changed public words or alternate native schedules.

The verifier then executes the actual renamed word on all 782 arbitrary
input axes, including its 12 dirty private axes. The independent reverse
column engine checks all 611,524 endpoint coefficients. It also compares all
21,663 chronological public source observations and every native query's
exact RAW payload and frame pair against the unmodified source. This is
stronger than final endpoint equality. All paid ranks, targets, productive
helper interfaces and public boundaries stay fixed.

The full source native phases, physical caller and recursive price are
retained dependencies. The equality of every native payload/frame makes
the same local native action available under those hypotheses; this replay
does not rerun the predecessor's native Clifford or full outer compiler.
The old positive finite allowance remains a conservative bound. Smaller
physical pool addresses and the exact scalar saving are reported separately;
no new tape tariff or new kappa is inferred. The source conditional kappa
.00312360607355 and all five framework assumptions remain unchanged.

## Reproduction

```sh
python3.12 -B scripts/research_package.py --package research/p104-compact-owned-pool
```

Normal and optimized registered checks authenticate the source word, source
local checker and exact allocator. RESULT.json records the minimum pool
certificate, source indices removed, complete local costs and observation
hashes. WORD.json.gz is the full emitted word. The checker also rejects a
collision in the certified simultaneous set and a missing dirty-slot INIT.
The direct verifier needs no Git, network or external Python dependencies.

## Open next questions

Can a different legal public/native schedule reduce the simultaneous set
below 12 while improving the complete recursive invoice? Start with the
12 listed episode IDs at the certified peak. Their actual source reads and
native continuations are fixed by this result. A changed schedule must prove
those reads and include its route, cache and target costs. TASK.json states
the boundary; this package does not claim that 12 is a universal floor.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. The source
is PR5812 at049714cf00952f58d2f48ef596445f5f08590ff8. Retain David Arias,
Cinna Davis, Gareth Davidson, Dugongue and all predecessor credits in
inputs/NOTICE. PR5763 supplies the exact interval allocator and its separate
occupancy certificate. Frozen source bytes are unchanged. The source local
checker is used only for its complete forward and reverse endpoint engines;
its native imports are not invoked. New work is the source-derived lifetime
proof, actual renamed word and query-by-query simulation. Apache-2.0.
Coordination: https://github.com/CrocSwap/integer-mult-bounds/discussions/5804.
