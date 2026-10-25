# Native quadratic-phase audit of the staged544 terminal promotion

This independently corroborates the signed native action at every promoted
terminal residual and every genuinely changed warp interface in the two
PR3945 providers. It also exhibits an actual binary inverse whose canonical
Clifford lift differs from the correct adjoint by a nonconstant sign character.
The result is a finite local operator certificate; it makes no new κ claim.

**Result:** 40 unique interfaces cover 144 source occurrences, checked on all
20,480 basis columns with every Gaussian coefficient and global phase retained.
Each provider contributes 26 cold terminal promotions, old and new residuals,
and 5 changed warp interfaces in both directions, old and new. The other 47
changed warp records only shift chronological indices. All equalities pass.

The mathematical pairing is framed arithmetic with finite symplectic geometry
and Z4 quadratic refinements. For the actual map
`G=[1,2,8,32,44,128,59,66,489]`, the canonical lift obeys
`K_(G inverse) K_G = Z_256`: a sign change on 256 of 512 basis coordinates.
Thus replacing a signed adjoint with the canonical lift of the binary inverse
would be wrong. The source uses the correct adjoint and passes. This is a
phase-discipline witness, not an author bug. The correction is a nonconstant
Pauli character; it is not merely a global scalar phase.

## Sources and independence

Scientific input: [Dugongue PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945),
head `91f81d131252db704f945891da1ea54e29d46b8b`. The four exact frozen words and
native source/receipt hashes are authenticated by SOURCES.json. Source words
are not edited. The nearest predecessor is the independent owner audit
[PR3969](https://github.com/CrocSwap/integer-mult-bounds/pull/3969), head
`6ff67539f1131a287eb9a9a98bf1e94a02eecba7`, which explicitly excluded phases.

`generate.py` optionally uses the byte-pinned predecessor compiler to generate
RECIPES.json. `verify.py` and `exact_phase.py` execute no predecessor code.
The new standard-library verifier independently inverts binary permutations,
constructs quadratic forms, propagates scalar Gaussian integers and decodes
the serialized recipe. It checks coverage directly against both old/new words.
The all-column checks prove local equality on arbitrary complex dirty state;
whole-word dirty restoration and physical admission remain inherited obligations.

Fresh frozen release crosslinks connect these exact words, the author native
recipe inventories, the final package manifest and the reported release receipt.
All crosslink files are included and checked. This does not replay the full
archive or complete native recipe payload. The retained complete recipe hashes
are recorded separately from our newly generated subset. The author evidence
explicitly discloses corrected frozen-spec bindings and reused successful
prefixes; this package does not describe that history as an uninterrupted run.

## Reproduce

Python 3.12, standard library only; no network or Git needed for the standalone
scientific verifier:

```sh
python3 -B research/staged544-native-quadratic-audit/verify.py
python3 -O -B research/staged544-native-quadratic-audit/verify.py
```

The registered repository check is:

```sh
python3 scripts/research_package.py --package research/staged544-native-quadratic-audit
```

The verifier is read-only. To obtain a new comparison receipt, pass `--emit`
with a path outside the package. Optional source-compiler recipe regeneration:

```sh
python3 -B research/staged544-native-quadratic-audit/generate.py /tmp/phase-recipes.json
```

Compare that JSON with RECIPES.json. Generation is not the independent check.
Fourteen semantic mutations reject, including phases invisible to binary-map
checks; all serialized monomials also pass exact inverse-column controls.
Both ordinary and optimized independent verifier runs are registered.

## Costs, scope and attribution

LEDGER.json lists proved, inherited and unknown obligations. Terminal recursive
ranks are 4 before and 5 after promotion; changed native warps have rank zero.
These statements assign no zero physical, precision, stock or tape tariff to
monomial wrappers or to the corrective sign. The complete owner bill is inherited
from PR3969. All changed scalar frame-transition classes, complete emitted
program, full release and uniform supplier conditions are outside this audit.

Credit: Dugongue's terminal promotion and native frame work (PR3945/3929),
dataisfire's literal providers (PR3734), Cinna Davis's PR2226 dirty-borrowing
operators, Tekalign's native replay, and the retained native compiler and phase
lineage including icekylinx, DreamingOfClouds and upstream contributors. The
source audit lineage includes Sagar Thakrar, roger-sato and Arham Tahir. Exact
retained notices are in SOURCE-CREDITS.md, NOTICE-PR3945.md and
frozen/NATIVE-LINEAGE-NOTICE. Chris R / Clear1nsight prepared this independent
audit with substantial OpenAI Codex assistance. Root-agent coordination supplied
an independently authenticated release crosslink inspection; this verifier
rechecks those links from the included raw bytes. Apache-2.0.

## Open next questions

Regenerate the complete source-bound canonical word and native recipe payload,
match the retained complete recipe hashes, and extend independent exact action
to every changed scalar frame-transition class and complete emitted program.
This would connect the local equality here to the remaining native admission
boundary. It requires explicit coverage of all emitted interfaces and the
retained uniform model obligations; a fresh subset hash or owner bill alone
cannot discharge it. TASK.json records the bounded first step and stop rule.
