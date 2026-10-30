# Find the smallest binary parameter precision

A rational feasible point can require a denominator that the chosen physical
format does not support. This tool searches a bounded linear region for a
point z/2^p, with integer coordinates z and one common nonnegative precision p.
It certifies the smallest p within the requested limit, or reports the exact
bounds that remain when the search budget ends.

```sh
python3 -B scripts/find_dyadic_parameters.py \
  tests/fixtures/dyadic-parameters/selected-saving-interval.json > certificate.json
python3 -B scripts/find_dyadic_parameters.py \
  tests/fixtures/dyadic-parameters/selected-saving-interval.json --check certificate.json
```

The fixture asks only for a dyadic number in [0.0031,0.00310045]. The upper
endpoint is the selected saving at main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`; it is copied as the exact fraction
62009/20000000. The minimum precision is 20, with point 3251/1048576. At precision
19 the integer box is empty. This is a representation example, not a new saving
or a replay of the selected theorem.

Input fields are `schema: dyadic-feasibility/v1`, rational `lower` and `upper`
vectors, `constraints`, `max_bits` and `node_budget`. Each row has `coefficients`,
`bound` and a Boolean `strict`: its inequality is a*x<b when true, a*x<=b when
false. Use integers or rational strings. Strict boundaries are checked exactly.

## Certificate and search

At precision p, the exact integer box is ceil(2^p lower) through floor(2^p upper).
A rejected box is either empty or has one row whose exact minimum violates the
required inequality. A branch splits one integer coordinate into two adjacent,
disjoint intervals covering the whole parent. The checker walks that complete
exclusion tree and recomputes every bound. It does not rerun the search.

The grids are nested. Excluding precision p excludes every smaller precision.
A feasible point at p and an exclusion tree at p-1 therefore prove minimality.
The producer first tests the maximum precision, then uses binary search on
precision. Within one grid it uses interval pruning and tests box midpoints.
The report retains only the strongest exclusion tree and the best feasible
point, with a lower and upper bound on the possible minimum precision.

`minimal` means both bounds agree. `infeasible_through_limit` excludes all grids
through the requested limit; a real feasible point or a finer dyadic point can
still exist. `unresolved` means the node budget ended. Its surviving feasible
point and exclusion tree remain valid; it makes no minimum claim. The saved
receipt is compact JSON to avoid indentation growth in large proof trees.

Limits: eight parameters, 64 rows, precision through 30, 50000 search nodes,
input rational numerator/denominator magnitudes through 10^9 and 8 MiB JSON.
The checker enforces the declared work bound on the retained exclusion tree.
Both source bytes and saved feasible coordinates are checked exactly.

## Open next questions

Bind the feasible region to a complete parameter proof, including strict error
and stock margins. Price storage, arithmetic and rounding in the chosen format.
This tool does not prove the source inequalities, nonlinear constraints or a
physical compiler. A coarse feasible point can be useful without maximizing
the source objective; optimize that objective in a separate stated model.

Credit classical interval branch-and-bound and binary search on nested grids.
Prepared for Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
No new kappa or selected-frontier change.
