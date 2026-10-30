# Choose a cheapest basis for a binary query span

A search can produce many dependent binary queries with different acquisition
costs. This tool selects a minimum-cost basis for their entire span and gives
an XOR expression for every original query in that basis.

```json
{"schema":"binary-query-basis/v1","width":2,"vectors":[
  {"bits":"1","cost":5},{"bits":"2","cost":2},{"bits":"3","cost":1}
]}
```

```sh
python3 -B scripts/select_binary_query_basis.py problem.json > certificate.json
python3 -B scripts/select_binary_query_basis.py problem.json --check certificate.json
```

The example chooses vectors 3 and 2 at total cost 3; vector 1 is their XOR.
Vectors use canonical lowercase hexadecimal, without `0x`. Bit i denotes
coordinate i. A representation mask uses bit j for selected basis entry j.
The report includes dual coordinate forms: the binary dot product of form i
with basis vector j is one exactly when i=j. These forms prove independence.

The checker reconstructs every input query. For every selected basis vector
in its expression, the query's cost must be at least that basis vector's cost.
Otherwise a cheaper one-element exchange exists. This condition proves global
optimality: for every price threshold, all queries below that threshold lie
in the span of the selected basis vectors below it. The rank of each cheap
prefix is therefore attained. No basis can buy more independent coordinates
at that lower price. Summing the prefix rank bounds gives the returned cost.

The producer uses weighted matroid greedy selection. The separate checker
uses only XOR, binary dot products, coverage and cost comparisons. It does not
sort candidates or run elimination. Ties can have several valid optima; the
producer breaks ties by input order. Zero vectors need no basis entry.

Limits: 4096 queries, 256 coordinates and integer acquisition costs in
0..10^12. The CLI binds exact input bytes and checks saved certificates without
search. All arithmetic uses the Python standard library.

## Open next questions

Bind binary queries and costs to one actual source model. Price the required
XOR reconstruction, delivery and restoration separately. The optimum covers
basis acquisition for the whole span; it does not minimize reconstruction
cost, a subset sufficient for only some targets, or physical native operators.
Binary coordinates do not establish scalar phases or legal helper endpoints.

Credit classical linear matroids, weighted greedy selection and the
fundamental-circuit exchange criterion. Prepared for Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0. No new kappa or frontier change.
