# Selected rank-two intertwiner and budget audit

**A constructive finite fusion, an exact lifting-cost obstruction, and two rejected donor-retiming budgets; no new κ.**

This follows Gonzalo Mier's [PR3975](https://github.com/CrocSwap/integer-mult-bounds/pull/3975)
first sequential candidate: forward phase-B register195, events12806 and13402,
frames0→2→252, with `L195 += L521/2` between them. The task pairs Clifford
and native circuit algebra with linear-systems transfer operators and
operator-space dimension arguments.

The direct rank-two recipe **does equal the composition of the two rank-one
maps**, including global phase. The ADD still transports a nontrivial donor
operator B. Omitting it gives an explicit e0 counterexample, and its residual
has ordinary matrix rank256. Retiming the donor either after or before the
fused child yields exact identities, but restoring the arbitrary dirty donor
immediately increases normalized recursive charge by `2^(1-a)`. Deferring
restoration to the donor's next actual child forces Fourier width3 and
increases charge by `3^(1-a)-1`. Both are positive for0<a<1, before charging
changed finite wrappers or hosting.

There is also a **positive finite construction**: the transport is
`B=((1+i)I+(1-i)P)/2`, with the explicit signed-XOR Pauli
`P e_x=(-1)^parity(96&x)e_(x xor224)`. One rank2 target child, four rational
array ADDs and six monomial source maps implement the exact boundary and
restore the arbitrary donor with no new register. This is a new physical macro
identity; its internal ADDs do not claim the inherited scalar-word common-frame
checker accepts the sequence. A macro compiler/admission remains open. For tensor multiplicity f,
its read-only-donor accumulation lift needs exactly **2^f monomial channels**.
At volume V its literal accumulation bill is at least V·2^f, so it cannot
silently acquire a constant native-adapter invoice. This scoped lower bound
allows different coupled programs; the selected κ is not improved.

A separate joint-macro result goes further than the unary retiming check:
**one arbitrary operator invocation plus coordinate-uniform scalar register
mixing cannot realize this boundary**. The boundary operator blocks I,B,C
span dimension3, certified by a three-entry minor with determinant(1+i)/4;
a one-call scalar-mixing circuit has operator span at most2. Arbitrary
additional coordinate-dependent adapters are outside this explicit class.
All algebraic statements extend to every positive tensor multiplicity f and
identity spectators; [PROOF.md](PROOF.md) gives the proof and scope limits.

The exact checker authenticates the entire597-event source interval and its
594 disjoint interior events, all512 basis columns of each map, all1024
basis inputs of the two-register boundary, two independent-order correction
recipes, the explicit finite native Pauli schedule, and five failure controls. It uses Gaussian rational arithmetic
and imports no predecessor executable. `RESULT.json` is recomputed read-only.
The numerical matrix rank256 is never substituted for a native cost.

## Reproduction

```sh
python3 scripts/research_package.py --package research/selected-rank2-intertwiner --check-only
python3 scripts/research_package.py --package research/selected-rank2-intertwiner
```

## Scope, overlap and expansion decision

Base canonical main20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision6.
This is a changed, bounded implication/cost audit of `complex-rank-shape-decoder`,
not its five-percent construction acceptance gate. The parent session checked
679 open PR bodies and rendered active/handoff Discussions before assignment;
Discussion/closed/diff/private coverage is partial. PR3975 was read at head
118967102329e19e2202ae38dcf37e85997a08dc; its later credit-only head
93157ab23657fb5f33751c5f858e81568caaec4b retains the same tested sources.

Cinna Davis's PR1836 and Adam Gall's `complex-heterogeneous-child-interface`
study simultaneous unequal-rank child packing and reciprocal encodings. This
package studies the different literal sequential transfer channel and its
next actual donor transition; it does not repeat their census or classification.
Both unary donor-retiming recursive charge expressions worsen even under free
finite wrappers; the positive finite Pauli route has the stated uniform channel
bill. Stop those implementations as uniform improvements; preserve the positive exact identities
and require a changed contract before another construction round.

## Open next questions

Can coordinate-dependent joint adapters implement this **same** two-register
boundary with a complete native invoice below the original? Start by specifying
which operator call touches which volume, and the exact input/output charts,
then test the three-block minor and complete donor restoration. Such adapters
must escape the scalar-mixing hypothesis; their geometry alone gives no tariff.
Hosting, finite correction costs and a complete selected replay are unresolved.
No general impossibility, supplier admission or κ improvement is claimed.

## Credit and license

Gonzalo Mier's PR3975 supplies the sequential candidate and its prior screen.
Credit Cinna Davis/PR1836, Adam Gall's heterogeneous interface audit and its
credited PR1920/PR679 predecessors for the related contract and volume-billing
lessons. Retain the selected PR1094 provider lineage and source audit.
The correction recipes were generated using the inherited `clifford_exact.py`
compiler preserved under `complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/`;
replay independently decodes their entries and requires exact equality.
Prepared by Clear1nsight with substantial OpenAI Codex assistance and a
separate Codex mathematical review. Apache-2.0. No independent human or
formal-kernel proof acceptance is claimed.
