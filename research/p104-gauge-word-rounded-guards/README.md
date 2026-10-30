# Rounded-error guards for the two PR5833 P104 words

**Finite certificate; no new κ.** Ali Romman's PR5833 emitted two complete
P104 words with sharp ideal field amplification 96 (original scalar budget)
and 2 (minimum). PR5838 proved a 20-bit completed-operation guard for the
earlier PR5830 word, with peak 65,537. It also asked for the bound to be
recomputed for a later gauge tradeoff word. This package does that for both
PR5833 words, under PR5838's contract and its causal bound, used unchanged.

| Word | Ideal peak | Causal guard | Final public error | Intermediate error | Field norm + error |
|---|---:|---:|---:|---:|---:|
| PR5830 (PR5838's result) | 65,537 | 20 | < 0.97754 B | < 26.903 B | < 65,563.91 B |
| PR5833 budget word | 96 | **20** | < 0.97746 B | **< 0.97746 B** | **< 96.978 B** |
| PR5833 minimum word | 2 | **20** | < 0.97746 B | **< 0.97746 B** | **< 2.978 B** |

B bounds every initial field's Hilbert norm and u = 2^-guard. All bounds are
exact rationals in `RESULT.json`; the table rounds them up.

What changes:

- **The final guard stays at 20 bits.** At guard 19 the causal bound on both
  new words is above 1.955 B, as on PR5830's word. Lowering amplification by
  factors of about 683 and 32,768 does not lower the accepted final guard.
- **The intermediate error envelope falls from 26.9 B to below 0.978 B.**
  On both new words the largest error bound at any instruction is the final
  bound on public field 205. No intermediate field ever carries a larger
  error bound than the outputs.
- **The field-magnitude envelope falls from below 2^17 B to below 97 B and
  3 B.** Read as fixed-point headroom (an inference, not a physical
  representation proof), the integer part above B needs 7 bits on the budget
  word and 2 bits on the minimum word, against 17 on PR5830's word, with the
  same 20 fractional guard bits.

The budget word keeps PR5833's original allowance (224,878 ≤ 224,880 scalar
primitives). Its precision envelope is therefore 10 integer bits narrower than
PR5830's word, at 24,332 more scalar primitives than PR5830's 200,546. That
is the tradeoff PR5833 asked to price; this package supplies only its error
side.

## Contract and method

Every physical `MOVE`, `ADD` and `SCALE` of the emitted word is a relative
defect site with PR5838's allowance: local ideal input norm plus actual prior
error feedback, times u. `COPY`, `INIT` and `CLEAR` are exact, as in PR5838.
The emitted PR5833 words already contain every entry, exit and lowered
`SCALE`, and neither word has an identity `SCALE`, so no site is virtual.
PR5838's `transfer.ideal` supplies the weights and checks every arbitrary-input
endpoint row. PR5838's `causal.bound` computes the forward bound with exact
signed coefficient rows and upward-rounded 96-bit dyadic defect bounds. Both
files are imported from `research/p104-gauge-error-covariance` without change.

**Adapter control.** PR5838 runs its bound on a timeline that also numbers
exact virtual identities. Applied to PR5830's emitted word with all physical
`MOVE`/`ADD`/`SCALE` as sites, this adapter reproduces PR5838's recorded
20-bit case exactly. That covers all public and owned final coefficients, the
peak value and its field, and the 26,271 sites; only the peak's instruction
index differs. This shows the site convention matches. It is not a re-check
of PR5838.

Four controls are rejected: a truncated budget word and a budget word with one
doubled `SCALE` coefficient both fail the endpoint check. Guard 19 is not
accepted. Omitting 1,000 sites changes the bound.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3.12 -I -W error -B research/p104-gauge-word-rounded-guards/verify.py
python3.12 -I -O -W error -B research/p104-gauge-word-rounded-guards/verify.py
python3.12 -B scripts/research_package.py --package research/p104-gauge-word-rounded-guards
```

Each prints `PASS_P104_GAUGE_WORD_ROUNDED_GUARDS` and takes about 17 seconds
locally. `--write` regenerates `RESULT.json`; the default mode requires the
committed receipt to equal the recomputation byte for byte. Sparse checkouts
need `research/p104-gauge-error-covariance` and
`research/p104-priced-amplification`. The six live inputs are pinned by Git
blob and SHA256 in `SOURCES.json`.

## Limits

- This is an upper bound under one worst-case contract. Sharpness at 20 bits
  is **not** claimed for the new words. PR5838 shows that a MOVE/ADD-only
  19-bit trace survives every field-constant signed scalar gauge of its base
  word. Whether PR5833's words lie in that gauge class was not checked here.
- Hardware rounding with stronger correlations may need fewer bits; PR5838's
  contract allows independently adverse completed defects.
- No rounded native child, COPY/reset machine, signed-record range, tape or
  descriptor cost is built or charged. The five framework assumptions remain.
  No κ, selected-frontier or admission change follows.

## Open next questions

1. **Is 20 sharp on the PR5833 words?** Transport PR5838's family adversary
   (`FAMILY-ADVERSARY.json`) to each word, or show the words are field-constant
   signed scalar gauges of PR5838's base word. The first step is to map each
   PR5833 instruction to its base-word event and gauge ratio.
2. **Does a narrower field envelope buy a cheaper physical word?** The budget
   word needs 7 integer bits instead of 17. Price a fixed-point record at
   27 total bits against 37 in the actual tape/descriptor tariff, including
   the extra 24,332 scalar primitives. Physical record widths are not yet bound.
3. **Can a gauge lower the final guard itself?** Both new words keep the final
   public bound near 0.9775 B. That points at the output-side native MOVE/ADD
   chain, not field amplification. The first step is the per-site share of
   field 205's final bound.

## Credit

This package was produced by Nick Petalas. The completed-operation contract,
causal bound, transfer method and 20-bit PR5830 result are Ali Romman's PR5838
(`research/p104-gauge-error-covariance`), which credits the PR5819/5826/5831
transfer method and the PR5830/5824/5822/5812 gauge lineage. The two emitted
words and their sharp ideal peaks are Ali Romman's PR5833
(`research/p104-priced-amplification`). All P104, native and compiler authors
retained in those packages' notices are credited through them. The new
contribution is the rounded-error guard and envelopes for the two PR5833
words. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
