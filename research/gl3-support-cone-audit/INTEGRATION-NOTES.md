# Source integration scope

`verify.py` is an integration adapter that intentionally reuses authenticated
PR4211 code. It is not the independent oracle. It compares actual predecessor
outputs against the independently frozen oracle revision 2, whose receipt-only
correction records example lengths as integers; no cone or prefix data changed.

The direct-CNF allocated state-variable keys bind all 117 interior row masks,
including all 5,247 allocated coefficient bits. At time zero and the endpoint,
the original encoder uses constants rather than state variables; comparison of
all 153 cone rows uses the actual packed implementation and the CNF generator's
reported all-cut support counts. This adapter does not separately recover and
audit the values of every internal endpoint constant or every transition
Tseitin clause. Both complete generated CNFs are nevertheless regenerated and
their bytes, variables and clause counts match the published certificate pins.

The source nine-call positive example passes its 504-basis checker, and all ten
prefix matrices agree literally with the frozen independent formal replay.
The legal two-call word provides concrete orientation, one-hole and wrong-target
controls. The fourth control replaces an involutory address label with an
order-three address; it does not mistake a non-idempotent scalar matrix for a
failure of involutivity. Indeed, q squared being zero suffices for the factor
square identity over F2 for every scalar N.

Normal isolated execution and optimized isolated execution with warnings as
errors both pass and produce byte-identical results. Each takes about half a
second on the current machine. Default execution writes only temporary CNFs;
it writes no package files. `--output` explicitly writes a requested receipt.

No SAT solver, RUP/DRAT checker, broad target search, complete Boolean compiler
equivalence audit, free-mixing normalization audit, human review or proof
assistant is claimed. The result does not independently certify minimum nine
or change kappa. Credit remains with Brian Ross and the predecessor authors;
the integration adapter was prepared with OpenAI Codex assistance.
