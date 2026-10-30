# No inserted carrier correction legalizes a PR5718-shape leak class on the PR6030 P104 word

**Scoped exact result; no new κ.** Base: canonical main `a2b4b0395e293dded1cb17b4e78910b364af2343`; inputs rechecked unchanged at
`721c03822`. The selected record is unchanged by this package.

Nick Petalas's [PR #6040](https://github.com/CrocSwap/integer-mult-bounds/pull/6040) (`shapesplit.py`, pinned
here as `inputs/shapesplit.py` from head `1889253f`) finds no PR5718-shape helper split on the PR5907 word. Every
candidate class either *leaks*, meaning the new helper's direction `d = S e_p` reaches a role whose final chart is
not `V`, or fails the pairing. It released step (3) of its claim: output corrections at later meetings. This
package takes that step. It runs on the merged
[PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) word (DreamingOfClouds, κ .003125804), which
became the selected word at main `721c03822` while this package was being prepared (the input bytes are unchanged),
and repeats the run on PR5907.

## Result

| Word | Leak classes | Carrier sources | Legalized by an inserted carrier correction |
|---|---:|---:|---:|
| PR6030 | 4,033 (390 leak to one role) | **0** | **0** |
| PR5907 | 4,206 (425 leak to one role) | **0** | **0** |

On both words, no **single** inserted chart-local ADD or SCALE after the cut clears the defect outside `V`, in any
leak class. Neither does any correction program whose sources all lie along the defect direction. The PR6040
suggestion `r += q·new` (a correction from a pure multiple of the new helper `z`) cannot clear a leak, with any
number of corrections. The z-part alone is easy to satisfy. That is why PR6040's z-only criterion is not a useful
filter once corrections are allowed.

## Why (exact, from linearity)

Fix a class: cut after event `i`, helper `p` at chart `F`, `V = final[p]`, `O` = roles whose final chart is not
`V`. Let `ℓ = row_p(i)·X` be the value the split retires. In the split word, field `f` holds
`orig_f(t) + β_f(t)(z − ℓ)` after event `t`. Here `β_f(t)` is the coefficient with which `p`'s cut content reaches
`f`. So the split outputs are `orig + d ⊗ (z − ℓ)`, and a legal split needs the **O-defect** `d_O ⊗ (z − ℓ)` removed
(with `z` still reaching a `V`-final output). Insert ADDs `r'_k += q_k f_k` after events `t_k`. The telescoping
identity for products gives the exact change: `Σ_k q_k S_{t_k} e_{r'_k} ⊗ (corrected value of f_k at t_k)`, where
`S` is the suffix map of the original word. Hence:

1. **Pure-z sources never suffice.** They add only multiples of `z`, so the `−d_O ⊗ ℓ` part stays. `ℓ ≠ 0` in every
   leak class (checked). On PR6030's leak-one classes, the z-part screen finds 124 classes it would pass (all
   4,033 classes, local run: 2,071 pass, 703 by one correction). The direct simulator (`check.py`) confirms for
   three of them that the z-leak is cleared while the O output keeps a non-z defect.
2. **A single correction needs a carrier.** For `q v_O ⊗ value_f = −d_O ⊗ (z − ℓ)`, `v_O` must be proportional to
   `d_O` and `value_f` to `z − ℓ`. That means `orig_f(t) = 0` with `β_f(t) ≠ 0`. A SCALE is the case `f = r'`.
3. **Carrier programs need a first carrier.** Corrections from carriers add multiples of `z − ℓ` and leave every
   `orig_f` unchanged. So the first correction in time needs a carrier of the uncorrected word.

The census (`leakfix.py`) tracks `β` for every leak class in one forward pass. It finds **no field, at any event
after any cut, that is zero in the original word while carrying the cut content**. Items 2 and 3 then exclude all
4,033 + 4,206 classes. The span machinery (one backward pass of suffix columns) decides the general carrier-source
equation `d_O + Σ μ_k (v_k)_O = 0` exactly over Q. It rejects solutions that erase `z` from every `V`-final output,
and it applies PR6040's pairing test to the corrected `d'_p`.

**Positive control.** On the PR5713 word, a carrier and a leak are planted after PR5718's own cut (event 14330,
chart 602, helper 708): `INIT s; s += p | cut | s −= p; o += p` with `o = 128`. The class leaks to three roles. The
census finds the single correction `o += s` (μ = −1), and the independent simulator accepts it with no z-leak and no
non-z defect outside `V`. A doubled coefficient is rejected.

## Reproduce

Python 3.12, standard library, from the repository root (about 90 s):

```sh
python3.12 -B research/p104-pr5718-leak-correction/verify.py
python3.12 -B scripts/research_package.py --package research/p104-pr5718-leak-correction
```

Marker: `PASS_P104_PR5718_LEAK_CORRECTION`. `--write` regenerates `RESULT.json`. Normal replay is read-only and
compares it byte for byte. The full pure-z screen over all PR6030 classes (`leakfix.run(w, mode='purez')`) takes
about 7 minutes. It is local-only evidence and is not in the verifier.

A side check (local only, not in the verifier): Matarener's PR5994 `splitcensus.py` and PR6040's census on the
PR6030 word give 0 witnesses each (8,734 evaluations; group and boundary supports; both input rules).

## Scope and limits

- Scalar O-defect condition only, at the level of PR5994/PR6040: no `V` normalization legality beyond "z still
  reaches `V`", and no native maps, owned lifetimes, caller, compiler, precision or outer checks.
- Covered edits: inserted chart-local ADD/SCALE events after the cut; programs of such events whose sources are all
  carriers in the corrected word; any number of pure-z corrections. **Not covered:** several corrections with
  non-carrier sources whose rank-one terms combine to `d_O ⊗ (z − ℓ)`; this includes several ADDs into one
  target from fields whose combination is a carrier. Rewriting existing events, new MOVEs (paid), and injections
  other than PR5718's unit injection `b = e_p` are also not covered.
- The census accepts only the PR6040 class list, so it inherits PR6040's input rule ('empty') and class definition.

## Open next questions

- **Combination carriers.** Is some combination of the fields at a chart zero in the original word but nonzero in
  `β`, at some event after a cut? That would enable multi-ADD corrections. First step: for each event and touched
  chart, test whether appending the `β` column raises the rank of the field rows. Blocked by speed: a direct
  Fraction rank test did not finish a 1/50 class subsample in ten minutes. It needs incremental rank maintenance
  per chart.
- **Edits that rewrite events.** Changing one existing ADD coefficient after the cut changes the original map and
  falls outside the identity above. First step: allow one coefficient change and repeat the defect equation.

## Credit

Nick Petalas (PR6040 census and class definition, pinned unmodified), Matarener (PR5994 census and pure-subspace
decision), flyingviper (PR5718 split shape), Ali Romman (PR5599 split criterion) and DreamingOfClouds (PR5907 and
PR6030 words) retain credit; nothing of theirs is modified. Prepared for JosieElliston by Claude Opus 5.5
(Anthropic) via Claude Code, as one session of an unattended overnight run; no human review. Apache-2.0.
