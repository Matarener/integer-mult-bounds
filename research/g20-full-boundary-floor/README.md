# The full fixed G20 boundary needs exactly 38 ADDs

**Scoped source-bound proof; no new kappa.** Each exact 32-wire boundary of
Ali Romman's PR5840 needs exactly 38 unit binary ADDs, even when intermediate
ADDs connect different endpoint components or the two untouched wires.
This closes the fixed-endpoint question explicitly left by PR6081
`2f258ab31a018b069d77449a148fe80727a6b9a1`,
`research/g20-joint-exchange-floor/README.md`, Open next questions.

## Contract and proof

The live input is PR5840's controller, retained by Charan ./PR5851 in
`research/g20-isolated-exchange-floor/inputs/CONTROLLER.json` and pinned in
SOURCES.json. Work over F2 with 32 independent input wires, unit gates
`x_d <- x_d + x_s`, d != s, fixed physical labels and the literal source
endpoint. Gates may connect any two of the 32 wires. No extra scratch, resets,
free basis changes or relabelling are allowed.

We use the connectivity/diagonal bound of Alan Bu, Evan Fan and Robert Joo,
*Minimum Synthesis Cost of CNOT Circuits*, arXiv:2408.07898v1, Lemma 3.6 and
Theorem 5.2, also used by PR6081. Here is its counting proof. Build the
undirected interaction graph of all gates seen so far. Each current row is
supported inside its interaction component. A gate joining separate components
therefore adds a source row with zero coefficient on the destination's own
original input: such a join cannot change any diagonal entry. Every other gate
changes at most one diagonal entry. If the endpoint has z zero diagonals,
at least z non-join gates are necessary. If the endpoint's undirected support
graph has v components, the interaction graph has at most v components, so
at least n-v joins are necessary. These are disjoint gate classes, hence
L >= n-v+z. This reasoning permits arbitrary intermediate cross-component gates.

For **both** source endpoints, the exact support components are:

- `(0,2,4,6,8,10,12,14,31)` and `(1,3,5,7,9,11,13,15,30)`;
- `(16,28)`, `(17,29)`, `(18,26)`, `(19,27)`, `(20,24)`, `(21,25)`;
- `(22)` and `(23)`.

Thus n=32 and v=10. The zero diagonal indices are 14 through 21 and 24
through 31, so z=16. The bound is **32-10+16=38**. The source contains eight
SWAPs and fourteen ADDs. Expanding each SWAP into three ADDs gives a literal
38-gate witness for each side. The two endpoints are inverse maps. This proves
exact minimality for each fixed boundary; it does not add separate
component-local lower bounds.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/g20-full-boundary-floor
```

The registered normal and optimized checks authenticate source hashes, replay
both literal programs and compare their serialized endpoint rows, compute the
support partition by two algorithms, check every input column separately,
verify the inverse composition, and reject all 76 single-gate omissions.
Identity, ADD, swap and unused-wire controls check the bound's conventions.
The universal lower bound follows from the proof, not finite testing.

## Open next questions

This closes fixed physical endpoints, including gates through wires 22 and 23.
It does not cover basis changes that alter the chain endpoint, additional
scratch, nonlinear gates, nonunit tariffs, joint supplier/caller optimization,
or physical/compiler admission. No recursive paid ranks or selected result
change. General GL2 choices affecting the chain still require a newly stated
endpoint family and its complete invoice. A useful first step is to identify
which such choices are actually legal for the source consumer before trying to
minimize their graph bound. An arbitrary matrix-family census is not admission.
No predecessor exhaustive circuit search or selected scientific replay was run.

## Provenance and credit

Canonical base 721c03822c421b7f7fcbb2598993b947c4d88419, priority revision 8.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5804#discussioncomment-19234839).
This changes the generic BIT card to the actual full G20 boundary obligation.
Credit Ali Romman/PR5840 (`6a043d0fc0199ee5b24c61f883f1943eaf6424be`) and retained
G20/native/controller lineage; Charan ./PR5851; Nick Petalas/PR5942 for the
18-wire component result; JoyboyBrian/PR6081 for the twelve-wire joint result
and explicit full-boundary question; Bu, Fan and Joo for the general bound.
PR6081 is context, not an executable or theorem dependency: the argument is
included above. Original source bytes remain unchanged. Prepared by
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0. No independent
human review, formal-kernel acceptance or complete multiplication theorem is
claimed.
