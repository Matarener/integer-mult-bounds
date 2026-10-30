# Minimum root row prefix

**An exact root-interface improvement; no new kappa.** The original QQ16
physical backend reserves q0=ceil(log2 F)D0(d) selected axes, although each
axis supplies K row bits. This package uses those bits and the depth of the
actual remaining core. It proves the minimum prefix under the same strict
factor-two padding budget and gives an exact reference compiler.

At p=2^8500, the full selected width needs **293 reserved axes instead of
36985358**. The reached depth is13993. At every p>=2^14000, **one axis**
suffices for every nonterminal remaining core; a terminal core needs zero.
These are source-relative row/geometry results. The complete paid supplier
profile and selected multiplication exponent do not change.

For remaining width M, the exact condition is

```text
floor(log2(F^D(M-q0))) <= K q0.
```

It is equivalent to the actual padded volume being strictly below twice the
input volume. Binary search returns its least feasible q0. [PROOF.md](PROOF.md)
proves the result and binds every retained source consumer of depth, q0 and
stock. [RESULT.json](RESULT.json) gives exact evidence;
[SOURCES.json](SOURCES.json) pins all sources.

## Reproduce

Python3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/minimum-root-row-prefix
python3.12 -I -O -B research/minimum-root-row-prefix/verify.py
```

Expect `PASS_MINIMUM_ROOT_ROW_PREFIX` and the registered package pass. The
checks include20000 direct padded-volume minima,10245 full-child depth
entries,21 complete finite dirty-data endpoints, production geometry at
p=2^8500, a separate inverse-depth oracle, and the one-axis tail certificate.
All32 Python files in the source controller are covered by the consumer
inventory. The code authenticates40 source inputs before checks.

The integer compiler is a reference implementation. The proof gives a paid
encoded algorithm and preserves the source row/guard/padding contracts; it
does not claim installed physical Count execution. The finite layout tests
use exact tensor endpoints on reduced address controls. Native correctness,
physical primitive admission, production payloads and the matched QQ16
comparison remain separate. [VALIDATION.md](VALIDATION.md) records replay
and publication checks.

## Open next questions

Implement the specified encoded planner at the RootPlan injection boundary,
retain all output fields, and execute reduced complete roots with source
Count/record primitives. Meter setup and every added operation. Production
geometry remains too large for a payload fixture. If the QQ16 intervention
is then reused, bind its changed core and all later calls again; the old
lambda45/72 internal band does not survive this replanning automatically.

## Credit

commdata2338's [PR5515](https://github.com/CrocSwap/integer-mult-bounds/pull/5515)
supplies exact reached depth, its inverse thresholds and the root-stock
handoff. Nick Petalas's PR4865 supplies the parking recurrence lineage.
Jose Manuel's PR3385 supplies the RootPlan and full source controller.
Sagar Thakrar's complex-root-address-refinement supplies the general address
and zero-padding argument, already present in the source proof. Their byte
copies and notices remain in vendor/. This work supplies the exact optimal
prefix, the eventual one-axis theorem, source-consumer binding and new checks.
Prepared by Ali Romman with substantial OpenAI Codex assistance. No subagents.
Apache-2.0. No human or formal-kernel review is claimed. Base main
 df0137efd35e11b4445734bf612bdd4c7ebc330c, priority7.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19188925).
