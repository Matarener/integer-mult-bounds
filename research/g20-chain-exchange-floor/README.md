# G20 chain/exchange component: exact 20-ADD minimum

**Scoped negative result; no new kappa.** The remaining 18-register component
of the PR5840 G20 boundary (wires 0-15, 30, 31: fourteen chain ADDs plus the
bank 7/15 exchange) needs exactly **20 unit ADDs per side**, even when gates
may mix chain and exchange operations anywhere on those 18 wires. The source
attains 20. The component splits into two closed 9-wire parts, and each needs
exactly 10.

This answers, inside the component, the question that
[#5850](https://github.com/CrocSwap/integer-mult-bounds/pull/5850) leaves open
("the remaining 18-register component ... may permit a cheaper complete
boundary") and the joint chain/exchange question of
[#5851](https://github.com/CrocSwap/integer-mult-bounds/pull/5851). With their
component-local six-ADD exchange floor, 20 + 3 x 6 = 38 per side and 76 per
port stay optimal for synthesis that keeps gates inside each component.

Claim type: finite exhaustive certificate (a computer proof), with a written
model and a hand proof of the even 9-wire bound in [PROOF.md](PROOF.md). It is
not a 32-wire global minimum, a search failure, a new kappa or a complete
multiplication theorem.

## Result

| Target (scratch-free, unit ADDs) | Wires | Source cost | Exact minimum |
|---|---:|---:|---:|
| even part: chain on 0,2,...,12 with exchange 14/31 | 9 | 10 | 10 |
| odd part: prefix chain on 1,3,...,13 with exchange 15/30 | 9 | 10 | 10 |
| whole component, cross-part gates allowed | 18 | 20 | 20 |

The search excludes every word of at most 19 ADDs on the 18 wires. It visits
2,016,480 nodes at budget 19 and finds a 20-ADD witness at budget 20.

## Reproduce

From the repository root, with CPython 3.12 and only the standard library:

```sh
python3 -I -W error -B research/g20-chain-exchange-floor/verify.py
python3 -B scripts/research_package.py --package research/g20-chain-exchange-floor
```

Expected last line of the direct run:
`PASS_G20_CHAIN_EXCHANGE_FLOOR component18=20 even9=10 odd9=10 controls=4`.
Locally a run takes about 35 seconds and 400 MB of memory.

The only live input is the PR5840 controller already vendored by #5851 at
`research/g20-isolated-exchange-floor/inputs/CONTROLLER.json` (SHA256 pinned in
[SOURCES.json](SOURCES.json) and checked by the verifier). The verifier replays
both source programs against the stored rows, checks that the 18 wires are
closed and that the right boundary is the exact inverse, then runs the search.

## Method

Exhaustive depth-first search for each budget, trying every ADD on the wire
set at every node. Pruning uses two admissible bounds: rows that still differ
from the target, and non-unit columns of the remaining map (valid because the
reversed transposed word has the same length). Failed states are memoized with
their largest failed budget. A node limit turns an overlong search into a
failure, never into a bound. Witnesses are replayed on all Boolean inputs.
Controls: the chain alone needs exactly 14, a weakened even target fits in
nine, and a two-wire exchange needs exactly three.

## Limits

Not covered: gates linking the component to the other 14 boundary wires,
general GL2 bases in the equal-target pairs `(2k, 2k+1)` (they mix the two
parts and change the target), scratch or helpers, a changed controller,
nonunit tariffs, and every recursive, physical, compiler, precision or analytic
obligation. The paid recursive profile is unchanged. The selected conditional
kappa 0.00310045 and its five framework assumptions are unchanged.

## Open next questions

1. Does any scratch-free word on all 32 boundary wires implement one side in
   fewer than 38 ADDs? This matters because every current floor is
   component-local. First step: run the same search on the chain component
   plus one four-wire exchange (22 wires, budget 25). Blocker: search cost
   grows quickly with wires and slack, so a stronger bound or a written
   argument is likely needed.
2. Do GL2 bases inside the equal-target pairs lower the 20-ADD component cost?
   This matters because pair bases are the freedom PR5840 released. First
   step: enumerate the pair-basis orbit of the 18-wire target up to
   cost-preserving symmetries and search the cheapest representatives.
   Blocker: each basis must also be priced at the caller and checked against
   the target diagonal.

Structured versions are in [TASK.json](TASK.json).

## Credit

Ali Romman supplied the PR5840 G20 target-pair boundary and its controller.
Charan . (#5850, #5851) posed the 18-register and joint chain/exchange
questions and proved the isolated four-wire exchange floor cited above; the
controller copy vendored by #5851 is the input. Their retained lineage
(PR5834, PR5807/5828, PR5708/5671, ai-nanachi PR5512, Dugongue, ToikY) is
recorded in those packages. Budgeted depth-first search and the transpose
argument are standard; the new work is the component decomposition, the exact
20-ADD minimum and its verifier, produced by Nick Petalas. Apache-2.0.
