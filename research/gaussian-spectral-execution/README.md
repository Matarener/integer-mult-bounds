# Executable pruned Gaussian correction and its standalone cost boundary

This package executes the full valuation-pruned residual from PR5815,
including negative Newton offsets, exact coefficient valuations, both Walsh
passes, true normalization, arbitrary inputs and every output. An independent
polynomial/tensor oracle agrees on all336 tested parameter choices and98
basis columns. No residual rank is treated as a free query.

A shared immutable bank reduces gather ADD precision mass from84867 to31862
for four distinct responses. Including all coefficient and synthesis ADDs,
the total is169623 to116618, a31.25% component reduction. Every other positive
operation count remains in the receipt; this is not a runtime or kappa gain.

The all-width degree-zero theorem shows that every proper Walsh prefix still
needs full precision. Together with an explicit uniform-precision Newton-W
bulk contract, it gives an all-interval standalone cost of at least(n/2)Np.
At p proportional to n this route retains the input-size times log-input-size
scale. The theorem does not cover changed bulk graphs, shared responses or
other Gaussian algorithms. See [PROOF.md](PROOF.md) for the exact hypotheses.

[compiler.py](compiler.py) exports `prepare(n,a,R,p)`, `gather(source,plans)`,
`deliver(bank,plan,source)` and `close(bank)`. Source coordinates are integer
pairs. Delivered values are the integral correction numerator modulo pi^(p+n),
with denominator header n. The implementation preserves the original source;
owned initialization, cleanup and bank retirement are explicit charges.

```sh
python3.12 -I -B research/gaussian-spectral-execution/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-spectral-execution
```

The standard-library verifier authenticates source bytes before import. It
writes nothing. [RESULT.json](RESULT.json) records every cost comparison and
[VALIDATION.md](VALIDATION.md) records publication checks. There are six semantic
control families and seven source-corruption checks. No Lean or solver is used.

Base canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a, priority8. The
P104 side-correction card changes to this ordinary response component and
cost audit. The selected binding control passes. PR5815 retains construction
credit; only Gaussian arithmetic is reused from PR5821. Exact pins and unchanged
notices are in [ORIGINS.json](ORIGINS.json) and source/.

## Open next questions

1. Bind a shared bank to actual unchanged source versions in a current caller.
   Charge every update, delivery, target debit, frame and physical route. The
   positive fixture here has no P104 source-site or whole-caller funding claim.
2. Compare a shared full transform plus polynomial outputs with this shared
   residual tree. The component saving is not global algorithm optimality.
3. Change the Newton-W graph, representation or precision schedule before
   expanding standalone search. More interval choices do not escape the stated
   bound. The heterogeneous-bulk case needs a new proof and invoice.
4. Supply physical coefficient preparation, tape movement, exact/reset rules
   and a complete bit-time tariff. The current counts do not establish them.

Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
All five framework assumptions remain. No new kappa or selected-frontier change.
