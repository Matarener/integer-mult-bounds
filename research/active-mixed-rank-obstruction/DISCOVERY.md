# Bounded discovery and final certificate

The exact backward response census was the first test. Support-cover LPs
were used only to find candidate rational witnesses. They gave no exclusion
at maximum rank four: an integral cost-62 cover exists. Its response span
misses five target directions.

Quotient-rank cuts then replaced the coordinate-only test. Greedy spans of
actual response spaces supplied candidate cuts. SciPy/HiGHS solved finite
relaxations during discovery. Each retained nonnegative dual weight was
rounded down to a multiple of 1/100000000. The final checker recalculates
every cut and proves every capacity inequality with exact fractions.
Floating-point success is not used as mathematical evidence.

The search used twenty refinement rounds at maximum rank four and thirty
at maximum rank five. The stronger rank-five certificate also covers ranks
one through four. Its retained nonzero cuts seed the rank-six certificate;
those seed rank seven. Both extensions have a strict bound above 64.
This reaches the largest contiguous rank range below the known rank-eight
attainment. The earlier rank-four checkpoint is not a separate result.

The same method was also tried on all ranks with at least nine channels.
The bounded relaxation remained below the needed price and was stopped.
There is no all-rank exclusion and no positive construction from that run.
The final package retains only checked exact certificates and the useful
cost-62 failure witness. No claim of an optimized true minimum is made.
