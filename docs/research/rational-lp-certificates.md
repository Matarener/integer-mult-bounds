# Replay exact optimization certificates

Use this checker to validate a proposed result from a linear-program solver.
Keep the solver outside the trusted replay. The checker uses exact rational
arithmetic and has no optimization-library dependency.

```sh
python3 -B scripts/verify_rational_lp.py MODEL.json CERTIFICATE.json > replay.json
```

The model is **maximize `c*x` subject to `A*x <= b` and `x >= 0`**. Its schema is
`integer-mult-rational-lp/v1`. Supply a `contract` string, unique `variables`, an
`objective` coefficient list, and `constraints`. Each constraint has a unique
`id`, a `coefficients` list, and an `upper` bound. Entries are JSON integers or
strings such as `"-2/3"`. Floats, decimals, and scientific notation are rejected.
Convert other LP forms to this explicit form before requesting a certificate.

Each certificate has schema `integer-mult-lp-certificate/v1` and one `kind`:

- `bounds`: supply `primal` x and `dual` y. The checker requires primal
  feasibility, `y>=0`, and `A^T*y>=c`. It reports `c*x`, `b*y`, and their gap.
  Only a zero gap certifies optimality.
- `infeasible`: supply `dual` y with `y>=0`, `A^T*y>=0`, and `b*y<0`.
- `unbounded`: supply a feasible `primal` x and a `ray` d with `d>=0`, `A*d<=0`,
  and `c*d>0`.

The proof is short. For bounds, `c*x <= y*A*x <= y*b`; thus the two objectives
enclose the optimum. For infeasibility, any feasible x would give
`0 <= y*A*x <= y*b < 0`, a contradiction. For an improving ray, `x+lambda*d`
stays feasible for every nonnegative lambda and its objective grows without bound.
The report includes exact constraint slacks or ray changes for inspection.

For a fee tradeoff, maximize `3*x+5*y` with `x+y<=3`, `x+4*y<=6`, and nonnegative
x,y. Primal `[2,1]` and dual `["7/3","2/3"]` both have objective 11. This proves
the optimum of that declared relaxation. A supplied feasible point `[0,0]` still
gives valid bounds, but its gap is 11 and the checker does not call it optimal.

This is a continuous LP certificate. An LP upper bound can bound an integer
search that is contained in the relaxation, but the containment requires a
separate argument. The `primal_integral` field only reports whether the supplied
point has integer coordinates. Do not infer a physical lower bound or a barrier
for a larger family from a model that omits legal constructions.

Limits: 128 variables, 128 constraints, 4 MiB per input, integer magnitude at most
`10^60`, and fraction strings of at most 128 characters. Invalid models or false
certificates exit 2 with no success report. Exact bytes of both inputs are hashed.
There is no numerical feasibility tolerance or automatic witness rounding.

## Open next questions

Export exact constraints from a source-bound candidate search. Reconstruct
rational witnesses from the search solver, then replay them here. Prove that
every claimed source candidate is inside the model. A verified LP alone does
not establish source legality, fee completeness, or a new κ.

Credits: classical weak duality and Farkas' lemma; the repository's source-specific
primal/dual audits retain their own scope and attribution. Prepared for Ali
Romman with OpenAI Codex assistance. Apache-2.0.
