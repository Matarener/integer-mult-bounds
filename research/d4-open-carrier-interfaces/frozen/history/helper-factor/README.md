# Four-helper OPEN bus factorization

After its explicit raw field swaps restore the physical IDs, the invariant-
gauge four-helper OPEN bus is exactly the zero-helper OPEN carrier on the24
public fields, direct-summed with four independent native rank3 channels.
All28 entering fields may contain arbitrary values. No helper value occurs
in the target response.

The exact child profiles differ by precisely four rank3 children:

    four-helper bus: {1:8,2:40,3:20}, mass148
    zero-helper carrier: {1:8,2:40,3:16}, mass136.

`verify_factor.py` uses the pinned actual Gaussian operators, including the
invariant full gauge `F=X33 F7`, all12 public block entries, and the four
helper operators `H_j=F C_(q_j)^-1 E_A^-1`. Their native lowerings retain
global phases. The scalar all-column identity and explicit native factors
extend by tensor products to every chunk size; no small-chunk translation
sum is extrapolated. Ordinary and optimized replay pass.

This isolates what a new shared-helper proposal must change. Leaving these
four channels separate cannot fix the public caller's endpoint deficit.
Using them for public completion while retaining their helper-progress
credit would count the same progress twice. A coupled global owner exchange
or other changed word remains open and needs its own actual all-input proof.

This is a local operator factorization, not a no-go theorem for all helper
sharing, a complete caller, rounded/tape admission, or a new kappa. Raw swaps,
monomial wrappers and every scalar scan remain paid operations.

Reproduce: `python3 verify_factor.py` and `python3 -O verify_factor.py`.
Scientific pin20ecf2891d80b5acf18d980b2164fb44ea7faa90. Geometry and exact
compiler hashes are recorded in FACTOR.json. This builds on the preceding
local D4 bus, source-carrier and width3-helper constructions; their source
files remain unchanged. Substantial OpenAI Codex assistance; Apache-2.0.
