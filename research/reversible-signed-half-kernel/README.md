# PR6066's signed halves have an explicit reversible tape kernel

One signed stochastic half from [PR6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066) now has an explicit binary gate word and two-tape program, with exact dirty-input restoration and residue cleanup. It works for every W>=2 signed bits, either sign and either resident coin, without a further arithmetic guard bit. The coin is never written.

The kernel uses one retained parity bit, W clean working cells and a read-only unary program of O(W^2) symbols. Its literal data-head walks and program-head return are charged. A direction takes 2L+2 interpreter steps for emitted word length L; exact gate counts and per-width program hashes are in RESULT.json. The retained bit is necessary for the isolated half; working scratch is not claimed minimal.

## Significance for researchers

This completes the specific single-macro lowering requested by PR6066. Its physical tariff is concrete and includes program storage and head motion. It does not make the complete stochastic prefix or supplier free: resident coin delivery, other scalar macros, caller widths and native transitions still need their own bills. [PR6091](https://github.com/CrocSwap/integer-mult-bounds/pull/6091)'s inferred residue sites have extra side information and need a compatible composition.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/reversible-signed-half-kernel
python3.12 -B scripts/check_research_commit.py --package research/reversible-signed-half-kernel
```

Normal and optimized standard-library checks exhaust 2,032 signed gate cases through eight bits, execute 324 literal tape round trips and check larger guards through 128 bits. They compare separate integer, gate and tape interpreters, including signed endpoints, exact scratch/coin/head restoration, invoices and rejection controls. PROOF.md establishes the all-width identities and tape model; finite tests do not replace them.

## Open next questions

Install the kernel at one actual reached half site with paid resident-coin delivery, clean-work allocation and the caller's exact finite guard. Then lower the rounded ADD and other SCALE macros and total their physical bill. An optimized tape layout or asymptotically faster increment program is a separate comparison against this explicit baseline.

## Scope and credit

Only one local signed half is implemented. The historical PR5599 prefix is authenticated to bind its two coefficient signs and 84 sites, not replayed as a complete physical program. No native/selected cold replay, complete sampler/caller, improved kappa or total resource optimum is claimed. Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance; credit [Nick Petalas](https://github.com/petalas), [Ali Romman](https://github.com/aliromman), PR6066 and their retained source lineage. The pending predecessor statement is retained verbatim with its exact hash. Apache-2.0; no independent human or proof-kernel review.
