# Assign distinct resources at minimum cost

Use this tool when each required consumer needs one distinct resource and all
allowed pairs have known charges. For example, a source audit can list legal
helper deliveries as rows and available physical fields as columns. Use `null`
for a forbidden pair. Never encode an unknown delivery as a zero-cost edge.

```json
{"schema":"compatible-assignment/v1","costs":[[4,1,null],[2,null,8]]}
```

```sh
python3 -B scripts/assign_compatible_resources.py problem.json > certificate.json
python3 -B scripts/assign_compatible_resources.py problem.json --check certificate.json
```

The complete assignment has minimum total charge among all injective choices
in this matrix. The report includes integer row potentials u and column
potentials v. They satisfy v<=0 and u[i]+v[j]<=cost[i,j] on every allowed pair.
Thus sum(u)+sum(v) is a lower bound on every complete assignment. Equality with
the returned assignment cost proves optimality. Unused columns do not create
credits: their nonpositive dual values remain in the lower bound.

If no complete assignment exists, the report gives a row set S whose full
neighbor set has fewer than |S| columns. Hall's theorem rules out every complete
injective assignment in this declared graph. The checker recomputes that full
neighbor set. It does not trust a partial list of allowed resources.

The producer uses the classical rectangular Hungarian algorithm. The separate
checker only checks arithmetic, edge constraints, injection and coverage.
Limits: 128 rows, 256 columns and nonnegative integer charges at most 10^12.
Zero columns are allowed and produce a shortage certificate. Input hashes bind
the exact problem bytes. The CLI rejects floats, duplicate JSON keys and bool
costs. It uses the Python standard library.

## Open next questions

Build an authenticated adapter from one source's compatibility data. Check
that assignments do not share hidden state and that charges include delivery,
restoration and routes. This model excludes coupled choices and capacity reuse
over time. A minimum cost here is not a new native word or a kappa certificate.

Credit: Hall's theorem and the Hungarian primal-dual method; existing R420
target-pair research supplies project context. Prepared for Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0. Selected frontier unchanged.
