# Mathematical cross-review of the companion C01 design

PASS within the stated finite, exact scalar compensation model. Reviewed
`c01-design/PROOF.md` (SHA256 `3cbacd11a7d7414e8889a6f559e759e9166d367fb7ec14c8896d381c7365ccf4`) and the constructor
`c01-design/design.py` (SHA256 `7d64232bced5cb621ff1a4ee65155b8d48b95620323564721042b4cfcb11bb00`). The independent whole-word
checker in this directory does not import that constructor.

The target preparation order is correct: deepest-first updates read each
original parent before that parent changes. Its residual is exactly `T C`.
For each helper preparation `h_a += s h_b`, right multiplication by `H^-1`
changes column b to `D_b - s D_a`. Pairwise disjointness prevents cross terms
and makes the claimed selected-pair savings additive. Restoring H and then T
therefore returns every arbitrary helper and target dirt term correctly. This
is freshly checked on all 632 logical input columns in both providers, with
forward, inverse-transpose and both literal reverse inverses. In particular,
the dual panel changes helpers by `-C^T y`; the proof correctly avoids claiming
they remain fixed at that local dual boundary.

The source-availability premise is sufficient for this changed choice. The
207 used helpers are live and absent from both source override dictionaries;
the authenticated transport gives precisely those helpers zero entrance and
FULL exit frames. The emitted prefix binds each raw register to its compact
identity and executes all helper preparation/restoration before entry adapters.
The entire suffix and every nonscalar event are unchanged. This is a checked
local availability and scalar-emission statement, not a fresh physical phase
proof or a new native supplier contract.

The target-forest optimum is correctly restricted to one signed unit parent
per nonroot, with the stated independent coefficient tariff. The superroot
bijection and sign symmetry make its total bill exactly a spanning-tree bill;
the complete all-edge cycle certificate is the appropriate minimum criterion.
The Prim calculation is correctly described as sharing the edge prices. The
88-pair selection is explicitly greedy and not claimed globally optimal. My
arithmetic replay independently confirms the final panel price 10633 per
component and the historical same-matrix rank-basis price 17334; it does not
supply an independent second enumeration of all forest or helper candidates.

The finite primitive reduction is useful, but its numerical tradeoff must
accompany the integrated claim: the exact scalar dual prefix row bound rises
from 169 to 181 and its positive-envelope strict power-of-two allowance rises
from 95 to 97 bits. Forward positive envelope also grows, while its 89-bit
allowance and exact range bound 302 remain unchanged. Exact scalar projection
grid depths stay four and five in the two orientations. CLEAR remains a
charged assignment in this model. No rounded physical cleanup, formal-kernel
proof, all-size implementation or new kappa follows.
