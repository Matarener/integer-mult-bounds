# Selected-word reject exhaustion for length-≤2 dest-in divergence

**Card `supplier-boundary-audit`, priority revision 6**, changed to answer
[#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696) open question 2
under the [#2977](https://github.com/CrocSwap/integer-mult-bounds/pull/2977) /
[#3004](https://github.com/CrocSwap/integer-mult-bounds/pull/3004) checker/exporter
cascade. No new kappa (`0.001672660197076918`).

#3696 showed dest-free gates always make Sym and Exp agree, named dest-in
witnesses that diverge, and four B[0] `bad operands` rejects. Its OQ2 asked
whether those four rejects are exhaustive for dest-in-sources divergence on the
pinned word. They are not.

This package proves a closed-form Sym/Exp agreement criterion for dest-in lists,
enumerates every source list of length at most 2 at B[0]'s destination `d=111`
over `n=661` registers, and obtains exactly **661** divergences
`{[d,d]} ∪ {[a,d] : a ≠ d}`. Only `self_even` and `dest_with_src` among the four
named rejects lie in that set; `dup_src` and `self_once` agree. Dest-free
agreement is used inside the closed form and is not republished as the claim.

```sh
python3.12 -I -B research/selected-word-reject-exhaustion/verify.py
```

Expected:

```text
PASS_SELECTED_WORD_REJECT_EXHAUSTION len2_divergences=661 named_diverge=2 four_exhaustive=false no_new_kappa
```

## Evidence

- Closed form matches linear Sym/Exp on all `(d,srcs)` with `n≤8`, `len(srcs)≤5`,
  and on the full length-≤2 census at `d=111`.
- Length-≤2 census: **661** divergences, **661** dest-in agreements, total
  `1+661+661²` lists.
- Named rejects: diverge `{self_even, dest_with_src}`; agree `{dup_src, self_once}`.
- Checker rejects all four named mutants and spot divergences
  `[d,d]`, `[0,d]`, `[660,d]`, `[3,d]` with `bad operands`.
- Every length-≤2 divergence fails operand distinctness.

Default verify is read-only against `CERTIFICATE.json`. Admission uses `need()`
and stays enforced under `python -O`. Explicit `--write` regenerates the
certificate only.

## Reproduce

```sh
python3.12 -I -B research/selected-word-reject-exhaustion/verify.py
python3.12 -I -O -Werror -B research/selected-word-reject-exhaustion/verify.py
python3.12 -I -B research/selected-word-reject-exhaustion/independent.py
python3.12 -I -B research/selected-word-reject-exhaustion/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-word-reject-exhaustion
```

## Open next questions

1. **Exact length-≤3 divergence count at the same destination?** First step:
   count closed-form failures over `n=661` lists of length 3. Blocked by: none;
   omitted to keep this package on the length-≤2 OQ2 scope.
2. **Should schema docs separate divergence classes from distinctness rejects?**
   First step: optional exporter warning keyed to the closed-form predicate.
   Blocked by: maintainer adoption.

## Credit

Closest prior: [#3696](https://github.com/CrocSwap/integer-mult-bounds/pull/3696)
`gate-operand-export-parity` (Wentao Li; dest-free lemma, four named rejects,
OQ2). Cascade priors: Nick Petalas / #2977; Kumagi / #3004; Dylan Crow exporter;
eumemic symbolic checker; tuned PR589 word. Scatter-parity contract audit is
credited as provenance only.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
No independent human or proof-assistant review is claimed.
