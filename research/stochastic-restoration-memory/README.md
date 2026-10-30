# PR6066 stochastic restoration needs exactly 76 retained residue bits

The historical [PR6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066) integer-grid protocol's retained log falls from **84 to 76 bits**, with the same stochastic forward map, unchanged random tape and exact arbitrary-dirty restoration. A matching 2^76-point collision proves 76 is optimal for retained information at this logical boundary. This saves eight bits (about 9.52%); physical working scratch and tape costs remain open. No new kappa is claimed.

One residue in each of eight independent tail blocks can be inferred from current data when the inverse reaches it. For the first three blocks its input parity is one current role's parity; for the last five it is the sum of two roles' parities. A symbolic source-bound invariant proves these rules for every integer input and coin tape, including the fractional ADDs. No rounding event or coin changes. The other 76 residues follow the predecessor's original save/reconstruct/clear lifecycle.

The lower bound uses 60 early halvings before any doubling, followed by eight disjoint four-preimage tail collisions. Their product gives exactly the retained-state requirement. [PROOF.md](PROOF.md) supplies both proofs and the exact source scope; [COLLISIONS.json](COLLISIONS.json) contains the small witnesses. The matching inverse is in compressed.py.

## Significance for researchers

This resolves PR6066's question about chronological reduction of the 84 parity bits at its logical boundary. The 32 later doublings do not make a 52-bit log possible; exact collisions force 76. The constructive upper bound also shows that keeping all 84 local residues was unnecessary. Next work can price the actual 76-bit interface instead of searching further for a smaller retained log under the same map.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/stochastic-restoration-memory
python3.12 -B scripts/check_research_commit.py --package research/stochastic-restoration-memory
```

The standard-library checks authenticate the historical word and retained predecessor, verify all 32 small collision inputs and complete nominated fibers, derive both symbolic parity invariants, execute 86 whole-prefix collision lifts, and compare 64 full restored protocols against the unmodified predecessor interpreter. Signed-half and wrong-holder controls remain active under optimization. The written product proof supplies the 2^76 quantifier; that many inputs are not enumerated. RESULT.json is compared with the recomputation.

## Open next questions

Can the 76-bit protocol be lowered to a reversible integer/tape implementation with a favorable total cost? Start with the eight inferred-parity sites, thirteen existing-value parity reads and the complete scratch/cleanup ledger. Retained-log optimality does not price working memory or tape movement.

Can one actual native MOVE accept the resulting copied-output error and guard contract? Pin its source operands and completed error bound before composing the caller. The predecessor's stochastic error estimate and the complete native/caller costs remain separate obligations.

## Scope and credit

This uses the historical PR5599 prefix used by PR6066, not the different selected PR6030 word. Optimality concerns worst-case retained information for exact pathwise restoration with arbitrary integer data and unchanged tape. It does not assert an average-code-length lower bound or a total physical resource optimum. A conservative 4,571-bit signed/guard width suffices for the entire collision family; executed representative collision fixtures use ten magnitude bits. No selected/native cold replay, independent human review, proof-kernel acceptance or new kappa is claimed.

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance. Credit [Nick Petalas](https://github.com/petalas)'s [PR6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026), [Ali Romman](https://github.com/aliromman)'s [PR5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), PR6066's restoration ABI and the retained P104 lineage. The pending predecessor statement and interpreter are retained verbatim with exact head/hash. Apache-2.0.
