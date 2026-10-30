# Optimize a bounded parameter model exactly

Use this tool to maximize a rational linear objective over a declared finite
box and closed linear inequalities. Supply a feasible incumbent; the tool
checks it before search. This contract is useful when improving a known valid
parameter setting. An invalid incumbent is an input error, not an
infeasibility theorem about the whole model.

```json
{"schema":"rational-box-lp/v1","objective":[1,1,1],
 "lower":[0,0,0],"upper":[1,1,1],"feasible":[0,0,0],
 "constraints":[
   {"coefficients":[1,1,0],"bound":1},
   {"coefficients":[0,1,1],"bound":1},
   {"coefficients":[1,0,1],"bound":1}
 ]}
```

```sh
python3 -B scripts/optimize_rational_box.py problem.json > certificate.json
python3 -B scripts/optimize_rational_box.py problem.json --check certificate.json
```

The example returns (1/2,1/2,1/2) with objective 3/2. Dual weight 1/2 on each
of the three inequalities gives the same upper bound. In general, the report
contains x and nonnegative y with Ax<=b, A^T y=c and c^T x=b^T y. Weak duality
then proves the returned point is globally optimal. The separate checker
verifies these products and inequalities without enumerating vertices.

Dual rows follow the input constraints, then x_i<=upper_i and -x_i<=-lower_i
for each coordinate i. Keep this order when reading a certificate. The input
byte hash prevents accidental reuse against a changed constraint system.

The producer enumerates independent active row sets. A nonempty bounded
polytope has an optimal vertex. Its active normal cone contains the objective;
an independent subset with nonnegative multipliers can be extended to a full
active basis. Thus the finite enumeration contains a primal-dual certificate,
including degenerate or lower-dimensional boxes. A zero objective uses the
checked incumbent with zero dual weights.

Limits: six parameters, 24 rows including the two box rows per parameter, and
at most 50000 possible active bases. Input rational numerators and denominators
are at most 10^9. Excessive declared searches are rejected before enumeration.
The solver uses exact standard-library fractions; large intermediate values
can increase runtime. It does not need an external LP solver.

## Open next questions

Derive each row from a complete source bill or a proved sufficient constraint.
For strict margins, include a margin variable and maximize it; then require a
strictly positive certified optimum. Nonlinear constraints, integer choices
and rounded coefficient models need separate proofs. A rational optimum is
not automatically a legal physical parameter or a new kappa certificate.

This producer complements the general certificate checker in
[PR #5767](https://github.com/CrocSwap/integer-mult-bounds/pull/5767). It is
independent of that pending change. Credit classical vertex theory and LP
duality. Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. No selected-frontier change.
