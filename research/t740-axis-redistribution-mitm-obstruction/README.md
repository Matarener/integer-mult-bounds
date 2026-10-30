# Repeated-axis redistributions do not preserve the fixed T740 operator

**Scoped negative result; no new κ or supplier admission.** For the fixed
T740 owner-zero schedule, changing only where copies of an existing residual
axis are hosted cannot preserve the exact physical operator when the total
number of copies of that axis is conserved. The check covers every port recipe,
all 20 residual-child slots and all 72 distinct residual axes per port.

## What this closes

Open PR [#3296](https://github.com/CrocSwap/integer-mult-bounds/pull/3296)
showed that one of the source-bound singleton transfer claims needed an exact
physical counterexample. The follow-up
[PR #3328](https://github.com/CrocSwap/integer-mult-bounds/pull/3328)'s
[basis-isolation package](../pr3190-distinct-axis-basis-isolation/README.md)
and [PR #3311](https://github.com/CrocSwap/integer-mult-bounds/pull/3311)
cover singleton moves and bundles whose moved axes are distinct and
orthogonal. Their isolation step does not separate several moves carrying
copies of the *same* vector, which is the gap addressed here.

This package exhausts that case without an optimizer. For each axis it assigns
a binary keep/move bit to every eligible child occurrence, requires the total
copy count to stay fixed, and tests every balanced assignment against the exact
eight-stream operator. Additions must fit under the residual rank cap 51 and
remain orthogonal to the destination's hosted basis. Translations, hosted rows,
the axis dictionary, chronology, bridges and native events stay fixed.

The key reduction is that the 72 distinct residual vectors form an orthonormal
dictionary over `F₂`: each vector has self-pairing one and pairs to zero with
all other vectors. Evaluating at the character equal to an axis therefore
isolates every change to copies of that axis. If a simultaneous collection of
different-axis changes preserved the full operator, each individual axis
assignment would have to preserve its isolated-character operator too.

For one axis, a chronological word with `n` eligible toggles has
`sum_t C(removals,t) C(additions,t)` count-balanced patterns. The verifier
factorizes its exact schedule matrix into fixed segments and diagonal `i`/`-i`
toggle factors. It meets exact prefix and pulled-back suffix actions on six
input columns, including the copy-count balance key. If a signature leaves
more than 16 patterns, it widens the signature; every remaining pattern is
replayed against the full literal eight-stream matrix. A full operator
equality therefore cannot be skipped by the screen. Fixed-segment inverse
candidates are accepted only after exact two-sided Gaussian-integer
multiplication checks; the fallback uses exact Gaussian rationals. No equality
hit occurs.

The verifier reuses the source-authenticated PR3187/PR3148 operator semantics
from the pinned predecessor. The new contribution is the all-child repeated-
copy domain and its exact meet-in-the-middle search; this is not an independent
implementation of the physical interpreter.

## Evidence and reproduction

The two deterministic receipts record all 112 ports. They include each port's
axis count, eligible toggle count, total balanced-pattern count, exact meet
states and nontrivial equality count. Every count is source-bound; the package
does not treat a finite search as an all-size proof.

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/t740-axis-redistribution-mitm-obstruction
python3.12 -B scripts/research_package.py --package research/t740-axis-redistribution-mitm-obstruction --check-only
```

The first half directly checks all 16 toggle masks for one axis against literal
replay and confirms the predecessor journal rejects a mutated preimage. Both
halves compare the literal event product with the generated operation sequence
and with the fixed-segment factorization for every port-axis pair. Each
registered half is bounded by 600 seconds and uses only the Python standard
library. No OR-Tools model is useful for this exact finite equality search.

## Open next questions

The result says nothing about changing axis vectors, translations, hosts,
bridges, owner replica, native words or the supplier and outer constructions.
It does not improve κ.

- **Can changing the residual axis vectors together with one actual bridge
  permit an exactly cancelling rank transfer at a lower complete cost?** This
  matters because every support-only redistribution of the fixed dictionary
  has now failed. Start with one small orthogonal-frame move next to one
  bridge, derive the resulting `Z/4` phase-polynomial difference, solve the
  exact Gaussian-integer intertwining equation, and price changed ranks,
  frame work, bridge work and restoration before widening the search. The
  blocker is that no source-supported cheap bridge rewrite or complete
  replacement invoice is known.
- **Can a same-axis occupancy move become feasible with jointly changed
  translations or hosting?** These variables can alter the phase at the
  isolating character and the legal destination set. Start by adding one
  bounded translation variable and its exact `Z/4` signature to the meet key;
  only then consider a host-schedule change. Such a variant still needs a
  physical source, full invoice and replay, none of which this package
  supplies.

[TASK.json](TASK.json) retains the structured questions and blockers.

## Sources and credit

The base commit, task card and exact live source pins are in
[SOURCES.json](SOURCES.json). The PR3187 operator loader and PR3148 T740 fill
are reused with their source-specific attribution and notices unchanged. New
analysis and verifier by OpenAI Codex with substantial AI assistance; no
independent human or proof-kernel review is claimed. New package material is
Apache-2.0.
