# Bounded integer multiplication with counted Word RAM execution

This package applies four reviewed Lean-library interfaces to one working bounded integer-multiplication construction: tcslib's literal Word RAM semantics, FastPoly's fixed-syntax/shared-value discipline, CatCrypt's exact NTT identities, and mpfx's sufficient recovery endpoint.

For every pair of unsigned inputs of at most 256 hexadecimal digits (1,024 bits each), the exact backend supplies a fixed input-independent 64-bit Word RAM instruction program producing the base-16 product. It preserves the input cells and arbitrary exterior memory and clears every owned intermediate word. The included informal proof covers all admissible inputs; executable controls independently check the implementation. The complete machine theorem is **not Lean-formalized**.

## Concrete result

The 512-point template has 6,912 shared butterflies, 507,701 static instructions and 17,920 owned temporary words. Every instruction runs through an interpreter of the retained tcslib ISA: `one`, `add`, `sub`, `mul`, `bltz` and final `accept`. No division, shift, FFT, modulus reduction or arbitrary-precision multiplication is smuggled in as a RAM instruction. Runtime constant construction, carry normalization and clearing are charged.

For the all-15 input pair (two maximal 1,024-bit unsigned integers), the program takes **391,079 instructions**, versus **636,835** for a same-ABI control that independently recomputes each butterfly product: **245,756 fewer instructions (38.59%)**. This is a comparison with that explicit control, not with the selected project algorithm or every FFT implementation.

For every admitted input pair, the same-output sharing transformation saves between `33 B` and `49 B` executed instructions, where `B = 3 N log2(N)/2`. The fused template has a uniform upper bound of `60 B + 193 N + 1,144` instructions, including setup and clearing. This is a bounded-template result, **not a new asymptotic kappa**.

A separate exact-rationally certified complex fixed-point FFT backend recovers every coefficient at 31 fractional bits under its stated complete error bound; 40 bits give a bound below 0.001. Its multiword intermediates are **not** priced as single 64-bit RAM operations. Four local algebra/recovery lemmas passed a fresh Lean 4.33.0 kernel/transitive-axiom audit; only the standard propext, Classical.choice and Quot.sound axioms occur.

## Apply the four sources

| Source interface | Application here | Exact boundary |
|---|---|---|
| tcslib base Word RAM and instruction steps | Literal, fully interpreted multiply/reduce/butterfly/whole-product programs with explicit word, memory and halt contracts | We do not instantiate `compileProgram_correct`; the assembler targets the base ISA directly. No unfinished extended-RAM simulation is used. |
| FastPoly fixed program / circuit sharing | One shared butterfly product, fixed before input values, with a same-ABI recomputation control | This applies the proof pattern. Our executed scalar products are not FastPoly nonscalar rank or the project's paid rank moment. |
| CatCrypt convolution / general inverse / radix split | Prime-field NTT, zero padding, least-residue coefficient lifting and exact carry normalization | The Python implementation is original; upstream Lean theorems are cited and their mathematical interfaces adapted, not imported or rebuilt here. |
| mpfx strict lattice recovery | Sufficient coefficient recovery after complete dyadic FFT error propagation, with exact twiddle certificates | The strict local endpoint and three butterfly identities passed a separate fresh Lean audit; the entire FFT and RAM implementation do not thereby become Lean-verified. |

## Reproduce

From this directory, on Python 3.10 or later with no third-party dependencies:

```sh
python3 -B verify.py
```

The checker validates the package hashes, runs independent transform and integer-product oracles, replays the actual RAM instructions with dirty owned memory, compares the recomputation control, and regenerates both exact-rational precision checks in memory. It does not need Git, Lean, network access, Windows, a GPU or upstream library installations. It fails under Python `-O`, because executable certificates use assertions.

`PROOF.txt` gives the complete informal assembly and cost proof. `ram/PROOFS.txt`, `ntt/NTT-APPLICATION.txt` and `recovery/REPORT.txt` provide the component arguments. `INTEGRATION-RESULTS.json` and component receipts are finite evidence, not replacements for their universal arguments. `SOURCES.json` retains exact upstream revisions/hashes; `STANDALONE-VERIFY.json` specifies this standalone replay. No global repository checker or selected record is changed.

## Frontier and overlap

The inspected base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`. Its authoritative selected record is the conditional PR 5413 construction, with PR 5407 provider, PR 5414 companion audit and the retained predecessor lineage. This package neither discharges all five framework assumptions nor replaces that selected result.

Pending PR 5443 addresses owned-bank lifetime/splitting, PR 5438 exact grids, PR 5451 physical operator error and PR 5442 all-width identities. This package supplies a different bounded, directly executable arithmetic kernel; it does not claim to supersede those statements. Updated open-PR titles/bodies were screened for overlap, not exhaustively mathematically audited. Standard Cooley-Tukey NTT/FFT, product sharing, base conversion and strict-half recovery are classical; no broad mathematical novelty is claimed.

## Open next questions

1. **Formalize the exact literal-program refinement.** Encode the assembler and prove its all-input output/frame/cost theorem against tcslib at one compatible toolchain. First bridge one butterfly and greedy reduction. Blocker: full instruction semantics are currently paper-proved and independently interpreted, rather than checked by Lean.
2. **Lower storage without repaying the saved work.** Replace fresh per-stage cells by a proved liveness schedule. Start with one in-place stage and count load/store/clearing changes. Blocker: no same-cost lifetime refinement has yet been established; the present 17,920-word figure is explicit.
3. **Connect an actual selected consumer.** Identify one real multiplication/recombination call whose complete bill this kernel improves, including conversions and precision. Blocker: the project's paid-rank/outer invoice differs from this fixed RAM instruction model. Only a proved complete-budget improvement would justify a kappa claim.
4. **Extend beyond the fixed field/size.** Construct a uniform modulus/CRT or recursive blocking route, charge prime selection/table generation and word widths, and retain exact integer recovery. Blocker: the current fixed-size family alone is not an asymptotic algorithm.

## Credit and license

Original integration and implementations prepared for Dugongue with substantial OpenAI Codex assistance from four workers. Credit for the reusable formal interfaces belongs to Shilun-Allan-Li/tcslib, Thomas Ahle/fast-polynomials, Bas Spitters and CatCrypt-core contributors, and Brett Saiki/mpfx-lean and their credited predecessors (including Flocq/Pierre Roux for cited rounding developments). Exact pins and source hashes are in `SOURCES.json`; existing project contributor attribution remains unchanged. Original package code and prose are Apache-2.0; the retained CatCrypt MIT notice applies to that upstream source material. No whole upstream library is vendored.

The base Word RAM semantics retain Anthropic, PBC / anthropics/formal-math [AFM26], `3sum-apsp/EndStatement.lean` at `e1a4e6508154ea59f030480661590a9fe3018011`, as attributed in tcslibâ€™s source header.

Local helper proof receipt: `lean/STATUS.json` binds the exact source hash and transitive axioms. The source can be checked in an existing Mathlib v4.33.0 environment with `lake env lean <path-to-this-package>/lean/IntegerKernelRecovery20261024.lean`. The supplied portable numerical replay does not install or invoke Lean.
