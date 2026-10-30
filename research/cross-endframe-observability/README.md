# Cross-endframe observability in the PR2979 word

**Claim: no κ improvement.** This package finds exact eligible linear forms only by pooling outputs from incomparable rank-seven terminal subspaces. It does not identify a consumer, realize a new helper, provide a complete invoice, or change the selected result.

## Result

The pinned `WORD-base` and `WORD-extra` providers from [the joint-endframes package](../rank7-joint-endframes/README.md) each have 49 observed rank-seven endpoint classes (104 registers) and 126 rank-eight classes (336 registers). An independent exact reverse-adjoint checker examines every endpoint class individually, all 1,176 pairs, and all 18,424 triples of rank-seven endpoint classes, grouped by the dimension of their join.

- No individual rank-seven or rank-eight endpoint exposes an eligible input form.
- Of 413 rank-eight pair joins, one exposes a form. The other 763 pair joins have rank nine and expose none.
- Of 2,571 rank-eight triple joins, one exposes the same form as that pair.
- Of 15,853 rank-nine triple joins, 52 expose eligible forms: 50 classes have eligible rank one and two have eligible rank two. Deduplication gives 11 scalar forms, ten of them additional. The ten additional forms span a five-dimensional space; five have six input terms and five have eight.

The rank-eight witness is

```text
-out[7] - out[232] + out[236] + out[238]
 = 1/2 * (-h224 + h227 - h229 - h231 - h232 + h233
         -h234 + h235 + h236 - h237 + h238 - h239 - h276 - h292).
```

The five independent six-term forms in the rank-nine block have these exact readouts:

| Eligible form | Terminal readout |
| --- | --- |
| `h224 + h229 - h235 + h237 - h238 + h239` | `2 out[7] - 2 out[87] - 2 out[238]` |
| `h227 - h231 + h233 + h236 - h237 - h239` | `-2 out[7] + 2 out[236] + 2 out[239]` |
| `h229 + h231 + h236 - h237 + h238 - h239` | `-2 out[7] - out[76] + out[231]` |
| `h232 + h234 - h237 - h239 + h276 + h292` | `-2 out[7] + 2 out[87] + 2 out[232] + 2 out[239]` |
| `h232 + h234 + h237 + h239 + h276 + h292` | `2 out[7] + out[76] + 2 out[232] - out[233]` |

Each equation cancels all 497 protected initial columns and every nonempty formal warp word. The five forms are independent. The ten new forms, including five additional eight-term forms, span the same five-dimensional space. Their readouts use three or four terminal registers, but the contributing rank-seven endpoints have a rank-nine join. Both provider orientations produce the same counts and coefficients.

## Four-endpoint pooling exposes a sparse basis

I extended the census to all `49 choose 4 = 211,876` four-class supports. A complete GF(3) screen uses the nine-dimensional global protected-readout kernel; its rational coordinates have denominators coprime to 3, so every rational rank defect appears in the screen. Each of the 1,353 surviving supports was then recomputed over `Q`. All have rank-nine joins and expose eligible forms: 1,258 have eligible rank one, 94 rank two, and one rank three. The screen and exact results agree in both pinned word orientations.

The four-class census adds six normalized scalar forms beyond the triple census. Four use only five input coordinates, one uses eight and one uses ten. Together the six span the full five-dimensional space; the four five-term forms alone span dimension three. Their exact identities are:

| Input form | Terminal readout |
| --- | --- |
| `h224 + 2h229 + h231 - h235 + h236` | `-out76 - 2out87 + out231 - 2out238` |
| `h224 - h231 - h235 - h236 - 2h238` | `-out231 + out233 - 2out238 + 2out239` |
| `h227 - h229 - 2h231 + h233 - h238` | `out76 - out231 + 2out236 + 2out239` |
| `h227 + h229 + h233 + 2h236 + h238` | `-2out87 + out231 - out233 + 2out236` |
| `h224 - h227 - h233 - h235 - 2h236 + h237 - 2h238 + h239` | `2out7 - out231 + out233 - 2out236 - 2out238` |
| `h224 - h227 + 2h229 + 2h231 + h232 - h233 + h234 - h235 + h276 + h292` | `-out76 + out231 + 2out232 - 2out236 - 2out238` |

These six readouts use only nine distinct terminal registers across seven rank-seven endpoint classes, whose joint frame has rank nine. This is a compact *observable interface* in the linear-algebra sense: it extracts a five-dimensional block without first constructing one common rank-nine register. The source forms are exact information identities, not five product outputs, and these endpoint observations still need a physical producer and a real caller. Treating the rank-nine join as free would erase the main cost.

The test follows the open boundary identified by [PR #3172](https://github.com/CrocSwap/integer-mult-bounds/pull/3172): its fixed-word obstruction covers each common endpoint separately and explicitly leaves pooling incomparable endpoints outside scope. This package tests that escape on the changed PR2979 word. It does not claim that the pooling idea itself is new or that the result generalizes beyond these two words.

## Reproduce

The checker uses only the Python standard library. From the repository root:

```sh
python3 -B research/cross-endframe-observability/verify.py
python3 scripts/research_package.py --package research/cross-endframe-observability --check-only
python3.12 scripts/research_package.py --package research/cross-endframe-observability
```

The two compressed word inputs are hash-pinned in `SOURCES.json`. `verify.py` independently reconstructs the endpoint frames and the non-target formal-polynomial maps; it does not import the predecessor producer or verifier. Its checks include the complete pair, triple and four-class censuses, exact rational rechecks after the GF(3) screen, canonical forms, orientation agreement, and controls that delete each register from the rank-eight witness in turn.

## What remains before κ can change

These are information identities, not a supplier. The ten triple forms and six sparse quartet forms expose the same five-dimensional opportunity through different readout bases. A caller must accept this block; the circuit must deliver it through a real multi-register contract; and the full synthesis, observation, storage, restoration, physical and recursive costs must be charged. In particular, the sparse quartet witnesses use a rank-nine join, so treating their rank-seven sources as a free common endpoint would be incorrect.

The current selected κ is still 0.001672660197076918. The conditional 0.0017290339826465… claim in the predecessor package is not selected, and this result does not exceed it.

## Open next questions

Can a downstream caller consume the five-dimensional sparse readout block directly without materializing a new rank-nine register? First trace the six forms to a named current call and compare the caller's needed subspace with their span; the four five-term forms alone give dimension three, and both bridge forms are needed for the full five-space. Then derive the input basis change and dirty-state restoration and price the shared observation and full recursive profile. Stop if no real caller consumes the block or if the complete transfer cost misses the required budget. The current evidence has no such caller or invoice.

## Credit

This scoped follow-up uses the two PR2979 word providers and preserves their attribution in the predecessor package. Ross Richardson's PR #3172 explicitly identifies incomparable-endpoint pooling as outside its theorem. New analysis and checker prepared by OpenAI Codex with substantial AI assistance; no independent human or formal-kernel review is claimed. Apache-2.0.
