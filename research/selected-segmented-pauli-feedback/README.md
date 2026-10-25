# Selected segmented Pauli feedback without a vector helper

**Exact construction and complete coordinate ledger; no new κ.** Fixed signed
coordinate-pair shears implement the actual195/521 coupled boundary with one
rank2f native child, an exactly restored arbitrary donor and no additional
vector helper. The rational ADD volume falls from #4009's(26f+1)V to
**(4f+1)V**; the signed-pair network uses **3fV unit-phase coordinate maps**.
Live vector payload falls3V→2V, plus bounded scalar primitive workspace.

The excess ADD volume over the original one-ADD boundary improves by exactly
6.5× (26fV→4fV). Total ADD work has ratio(26f+1)/(4f+1). Addressing is explicitly
charged O(fV) word operations, and the source-pair signs are compiled into the
rational coefficients. No whole-array signed-P permutation or exponential
address table is assumed free. This is a concrete change from full-array
register mixing to coordinate-pair shears, not an asymptotic FFT improvement.

[PROOF.md](PROOF.md) gives the exact seven-operation pair schedule, all-f
identity, addressing algorithm, arithmetic/memory/stock ledger, standalone
exact-grid bound, uniform outer-prefix condition bound729/4, and failed uniform
budget screen. [RESULT.json](RESULT.json)
records exact finite replay. Clifford/Pauli algebra is paired with segmented
in-place linear networks and block scheduling. The latter improves locality
options, but rescheduling this network does not reduce its Θ(fV) arithmetic.

## Reproduce

```sh
python3 scripts/research_package.py --package research/selected-segmented-pauli-feedback --check-only
python3 scripts/research_package.py --package research/selected-segmented-pauli-feedback
```

Python standard library only. The checker verifies both signed pair matrices,
1024 literal boundary inputs,128 source orbit charts,168 complete reduced tensor
basis inputs, fixed schedule counts, dyadic-grid fixtures and four corruptions.
All-f conclusions have a written proof; finite tests are not extrapolated.
[SOURCES.json](SOURCES.json) pins canonical source bytes and history. Pending
predecessor PRs are credited but are not runtime dependencies.

## Scope and decision

This physical macro permits within-register coordinate shears. It has not been
admitted by the inherited scalar-word common-frame checker. It restores donor521
exactly and returns target195's original physical output/frame, with no borrowed
vector helper. Scalar primitive workspace, tape/physical routing and approximate
native-child precision remain implementation obligations. The exact standalone
adapter uses grid2^(−p0−f−1)Z on dyadic donor inputs; including an exact rank2f
child needs at most2f extra grid bits. This is not an approximate supplier proof.

The explicit schedule still adds4fV rational ADD work over baseline. For fixed
A>0 and selected0<α<1, this eventually exceeds the available recursive saving
A V[2−2^(1−α)]f^(1−α), even if its phases/routing/precision are granted free.
No sub-fV algorithm, universal sparse lower bound, selected profile, improvedκ,
new cold replay, changed frontier or complete supplier is claimed. The result
removes a stock obligation and lowers constants without passing that uniform
budget gate. Stop further expansion of this particular schedule.

## Open next questions

A different algorithm would need a proved sub-fV processed-volume invoice,
with exact restoration, source access, routing and precision, before another
construction round. A blocked or cache-aware reorder of these same fV pair
kernels leaves its arithmetic count unchanged. The parallel sparse-lower-bound
and variable-volume-native investigations have different owners; this package
does not claim their open conclusions.

## Sources, overlap and credit

Scientific base20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision6;
canonical main was refetched unchanged during this round. Entry coverage was
733 open PR bodies at10:46 UTC on2026-10-19, current handoff/active Discussions
and relevant local package notes. Closed diffs, all Discussions and private
work were not exhaustively checked. No exact same boundary/signed-pair schedule
was identified in that coverage; this is not a novelty certificate.

Credit GonzaloMier's [#3975](https://github.com/CrocSwap/integer-mult-bounds/pull/3975)
for the literal sequential candidate, [#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989)
for its Pauli boundary and [#4009](https://github.com/CrocSwap/integer-mult-bounds/pull/4009),
head89a358aac11d11e0539eb95c27600e7677be7ce4, for the dirty-helper feedback
construction, full-array contract and exact primitive decoder adapted here.
The new contribution is its selected no-vector-helper segmented realization
and complete processed-volume/precision ledger, not the elementary shear or
butterfly method itself. Retain CinnaDavis/#1836, AdamGall's heterogeneous-child
interface and selected#1094/#679 lineage credit for the inherited setting.

Adjacent Ross Richardson [#4023](https://github.com/CrocSwap/integer-mult-bounds/pull/4023)
(head9124007ea9029a9a3b88898bb4c350ddb27ffa58) treats fixed-carrier unary query
bounds with restored dirty banks and a paid-scan counterexample. His
[#4027](https://github.com/CrocSwap/integer-mult-bounds/pull/4027)
(head1bcc4f8261d2dc322c98fa9e44c4ced43cd1cd95) treats an H6 asymmetric U9
compensation splice. These different scopes reinforce charging source visits,
wrappers and restoration; neither is asserted to prohibit this macro.
The adjacent [P104 handoff on#3954](https://github.com/CrocSwap/integer-mult-bounds/pull/3954#issuecomment-6265484095), updated11:02 UTC, adapts#4009 to5408 source-owner pairs with full-array scans and explicitly leaves sparse/variable-volume routes open. Its different physical boundary and70304f full-array ADD bill are not reused here; the present result has one selected195/521 boundary.

Arham Tahir/#1920 and ToikY/#1924 retain credit for reciprocal/clean-subspace
boundary and volume discipline, outside the present segmented implementation.

Prepared by Clear1nsight with substantial OpenAI Codex assistance for design,
proof, implementation, source investigation and independent agent review.
New text/code Apache-2.0; inherited notices retained. No independent human or
formal-kernel verification is claimed.
