# Losing-first two-edit search at displacement exactly two

This continues PR3941 and PR3942 on both literal PR3734 staged544 providers.
The question is whether a legal, initially more expensive ADD retiming across
exactly two scalar neighbours can unlock a second ADD retiming whose combined
raw recursive moment is lower than the original word.

The scientific inputs remain the exact PR3734 snapshots pinned through PR3886.
All entrances, target/centre/native cuts, native maps, helper identities and
exits, wrappers and caller contracts are fixed. The second move has no distance
bound inside its allowed scalar corridor. No instruction, helper or dirty buffer
is added. Neutral first starts are excluded from this package's losing-only
census; PR3941 covers its separate neutral domain. PR3942's radius-one class
is a predecessor rather than a set of extra disjoint cases.

**Result:** no lower raw recursive moment in this declared class, for every real
`0<a<1`, on either frozen provider. Per provider: **797 legal losing first
subspace states**, **9,149,777 interacting second cut/dimension prices**, and
**48 combined signed-profile types**, all with exact non-improvement
certificates. Across both providers this is **18,299,554 explicit second prices**.
All first records pass the real boundary audit; none is discarded there.
The first domain considers 8,431 cut/dimension price cells and explicitly
excludes 8,078 neutral price cells before expanding losing subspaces. Its
1,565 distinct interval/dimension triples have maximum quotient dimension three.

All **1,594 first dirty blocks** pass exact rational equality. Complete-word
checks additionally cover both baselines, **18 first states and 18 resulting
second-edit words**, in both orientations with reverse/cleanup checks. First
intermediates use 3,519–3,521 recursive children, with rank mass fixed at 5,134.
The helper inventory remains 408 roles and 91 dirty buffers. A conservative
finite bound for every final retimed scalar coefficient is 11 numerator bits
and 11 denominator bits; this is not a uniform precision or tape tariff.

Exact counts, sign rows, local cost and execution coverage are in RESULT-base.json,
RESULT-extra.json, CENSUS.json, LEDGER.json and VALIDATION.json. The verifier fails on an
unresolved sufficient sign test; a failed sign certificate is never described
as a profitable circuit. Counts are insertion-cut/frame-dimension prices in a
relaxation, not distinct whole circuits or supplier admissions. PROOF.md gives
the exact domain, completeness, register-interaction reduction and sign proof.

## Reproduce

Python 3.12, standard library only, no network, solver or Git required for the
scientific replay:

```sh
python3 -B research/staged544-losing-first-d2/verify.py --provider base
python3 -B research/staged544-losing-first-d2/verify.py --provider extra
python3 -B research/staged544-losing-first-d2/check_controls.py
python3 -O -B research/staged544-losing-first-d2/check_controls.py
```

The full replay authenticates the frozen bytes before executing retained
modules, regenerates all 1,776,295 original single-move premise cases, enumerates
every first-frame subspace and every interacting second cut/dimension, charges
the first loss, reconstructs invoices, checks exact sign prefixes and compares
the complete committed receipt. The optional `--emit /external/path.json`
regenerates a receipt outside the package; ordinary execution is read-only.

From a complete repository checkout, the opt-in registered hook is:

```sh
python3 -B scripts/research_package.py --package research/staged544-losing-first-d2
python3 -B scripts/check_research_commit.py --package research/staged544-losing-first-d2 --check-source-history
```

Registry metadata, source-history/committed-byte transport, hosted CI and the
mathematical replay are separate checks. VALIDATION.json states which actually
ran and their exact environments/runtimes. Source snapshots make the scientific
replay independent of pending predecessor Git ancestry.

## Exact dirt and complete costs

Every admitted first move receives an exact rational equality check of its
complete three-instruction block on independent symbols for all participating
registers. This covers arbitrary dirty state by composition with unchanged
surrounding operators. Legal frame/boundary audits accompany every first word.
The retained full interpreter additionally checks the complete baseline and
first/middle/last samples per phase, plus actual final second-move samples:
632 live inputs and 91 dirty buffers, both orientations, reverse pull-back and
cleanup boundaries. This is exact compositional verification for the entire
first class, supplemented by explicitly sampled full-word replay. It does not
claim every first word was individually passed through the full interpreter.

The controls independently enumerate quotient-frame bases and first cut/price
records, reconstruct integer sign certificates, check literal undo, reject
wrong scalars after fresh cleanup, bad frames, omitted dirty cleanup, source
drift and scalar barriers, and test exact three-gate SCALE conjugations. The
already-retained Jeremy Kothe PR2957 rollback/recovery remains the credited
positive control, `2+3 -> 1+4`; it is not a new improvement on the pinned word.

LEDGER.json records the baseline recursive profile, children and rank mass,
all changed intermediate profiles, combined histograms, helper widths,
primitive/native inventory, entrance/exit fingerprints and coefficient bit
bounds. First-move losses are charged before concluding anything about the
second move. Unknown fresh native/phase, physical allocation/hosting,
precision/stock/tape, all-size/compiler, outer/supplier, analytic and BIT costs
remain unknown or explicitly inherited; they are not priced at zero. There is
no new kappa, selected-frontier change or unconditional multiplication theorem.

## Scope, overlap and credit

Explicit user-assigned `scalar-to-moment` continuation, canonical main
20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision 6 at entry.
TASK.json retains the actual scope, expansion decision, overlap coverage,
claim, checkpoints and stopping rule. PR3945 changes terminal/native interfaces
and therefore lies outside this fixed-input search; no claim about its new
supplier follows from these frozen-baseline results.

Credit dataisfire/PR3734, PR3886, PR3941, PR3942, Jeremy Kothe/PR2957, PR2979 and
the staged-entry/retiming chain, Dugongue/PR3863 and the ranked-pair/MathProof
predecessors. PR3942 supplies the exact all-subspace enumeration and the
same-gate/disjoint second-move reduction; search.py is an explicitly adapted
derivative. PR3941 supplies the dirty-block checking method. Their original
source/proof is retained for comparison where applicable.

Sagar Thakrar's auditor and roger-sato's semantic adapter are reused unchanged,
including Arham Tahir's frame-contract attribution. They are not newly
independent interpreters. New displacement-two census, dirty checks, controls
and packaging by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0 and retained source notices apply. No independent human review or
formal-kernel acceptance is claimed.

## Open next questions

* Neutral frame-preserving first moves across exactly two neighbours remain a
  nearby gap. This package excludes every neutral first move; PR3941 covers
  neutral changed-frame starts through two and adjacent frame-preserving ADD
  swaps, and PR3942 stops at displacement one. Their union is not the complete
  radius-two two-edit class. Enumerate those fixed-frame starts and derive the
  new insertion-gap prices before a separate census; the frozen-baseline
  adjacent certificate cannot simply be iterated.

* A first move of displacement three or farther remains outside this bounded
  domain. Before expanding, pin one concrete candidate and explain which
  projected-frame interaction is newly available, then derive its second-move
  and physical invoice. This requires a separate expansion decision, rather
  than automatically adding another radius or seed.
* A simultaneous two-frame rewrite without a legal intermediate has a different
  contract. Supply one exact before/after word and arbitrary-dirty restoration
  identity before attempting the proposed rank exchange or an aggregate price.
* The changed-terminal supplier in PR3945 needs its own source-bound review.
  These fixed-interface exclusions do not certify or refute that construction.
