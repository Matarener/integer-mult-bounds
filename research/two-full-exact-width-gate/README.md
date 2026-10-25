# Exact numerator width at two-FULL source cuts

Exact arithmetic does not make the declared two-FULL border affordable under
one uniform width policy. The actual source has 4,524 paid cuts with two
independent integer bands. At each such cut, a literal exact numerator needs
leading width 2k rather than the budgeted k. Charging only the 3,163 original
rank-one cuts gives paid mass 13,817 versus target mass 10,750. Every power
moment with exponent in [0,1] then fails. **The complete kappa calculation
does not improve.**

Read [the proof](PROOF.md), [exact result](RESULT.json),
[all occurrence witnesses](WITNESSES.json.gz), and [source pins](SOURCES.json).
The publication base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`.

## Exact scope

The source operations are ideal and exact. The two integer amplitudes are
independent inputs; there are no independent operator faults. Each paid
occurrence has a width fixed for all its permitted inputs. The raw bill funds
`k+o(k)` bits and charges linearly in width, at fixed native rank and fixed
fiber/column multiplicity. Tensor-frame denominator offsets can grow with that
multiplicity; no limit with growing multiplicity is claimed.

This is a source-specific gate for literal numerators, including a shared
exponent. It is not a lower bound for adaptive per-input width charges, joint
symbolic storage, different words, or a baseline that already funds a larger
leading width. Separate worst-case site witnesses do not prove one input
incurs their sum under an adaptive policy.

The new census uses the retained moving-frame audit as a pinned live input.
That audit checks all 42,898 events and the zero-address phase of all 72 warp
matrices. The new code checks the 520-column restricted caller input space,
all independent helper returns, all 4,524 recorded cuts, and the full declared
helper and main target debit. It does not rerun physical Gaussian compilation.
The rank-split wide profile is informational; the rejection uses original H1
cuts only.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3 -B research/two-full-exact-width-gate/verify.py
python3 -O -B research/two-full-exact-width-gate/verify.py
python3 -B research/two-full-exact-width-gate/test_mutations.py
python3 -B scripts/research_package.py --package research/two-full-exact-width-gate
```

Expected direct output:

```text
PASS_TWO_FULL_EXACT_WIDTH_GATE wide_sites=4524 extra_H1=3163 ratio_upper=10750/13817 new_kappa=false
PASS_TWO_FULL_WIDTH_MUTATIONS checks=4 normal_and_optimized=true
```

Default replay is read-only. `verify.py --write` rebuilds the certificate and
receipt. Regeneration compares decompressed canonical JSON, not gzip headers.
The source archive and inherited frame checker have exact byte pins. The two
live input paths in VERIFY.json must be present in a standalone export. No
Git or network access is needed by either direct scientific check.

The controls reject an understated valuation loss, a zero band coefficient,
a missing final C0 clear, a float in an exact receipt, changed source bytes,
and a changed witness coefficient. The last two use isolated normal and
optimized subprocesses. The finite checks support the written proof; they
do not replace its all-k argument.

## Related work and credit

Cao Yifan supplied the retained round-three source and its full profile in the
[PR #4610 lineage](https://github.com/CrocSwap/integer-mult-bounds/pull/4610).
The [pinned source proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/kappa-round3-warp-20261022/PROOF.md)
retains the native, helper and compiler lineage.

Yiyang (@Lyy-iiis) supplied the actual caller, source boundary calculation and
moving-frame audit in [PR #4966](https://github.com/CrocSwap/integer-mult-bounds/pull/4966).
The [pinned caller proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/two-full-border-paid-precision/paid-sensitivity/PROOF.md)
rejects a different, independent-error policy. Its
[pinned invariant audit](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/two-full-border-paid-precision/independent-review/invariance/REVIEW.md)
supplies the exact logical-frame semantics reused here. Dillon's earlier
[PR #4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623) retains
credit for the border and recovery question.

Cinna Davis's [PR #4983](https://github.com/CrocSwap/integer-mult-bounds/pull/4983)
concerns additive scalar compatibility. JoyboyBrian's
[PR #5106](https://github.com/CrocSwap/integer-mult-bounds/pull/5106) concerns a
coherent rank gauge. Neither argument is used as an exact width lower bound.
The rounded inverse and history frontier in
[PR #5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444) concerns
output-grid fibers and repeated recoding, not this source-cut numerator bill.
[OVERLAP.json](OVERLAP.json) records these distinctions and coverage limits.

The new source census, width proof, checker and package were prepared by
Ali Romman (@aliromman), with substantial OpenAI Codex assistance. Parallel
agents are part of the author process, not independent human review.
Classical valuation, injective counting and rank separation are not claimed
as new general mathematics. New files are Apache-2.0. The source notices and
retained contributors remain unchanged.

## Open next questions

A changed exact representation needs a literal caller and a complete cost
comparison. Start with one paid cut and state where both independent bands
are stored, how its Gaussian action is computed, and what the input and return
costs are. Joint symbolic state, adaptive widths and larger funded baselines
are outside this theorem and need their own proofs. Recursive child
compatibility remains a separate obligation. [TASK.json](TASK.json) gives the
scoped follow-up and stop rule.
