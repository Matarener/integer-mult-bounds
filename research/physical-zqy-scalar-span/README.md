# An explicit full-frame native-history kernel

## Stronger complete-channel kernel

[KERNEL-PROOF.md](KERNEL-PROOF.md) gives a short all-width information barrier for the exact full-frame-only channels. Every raw-backward history is invariant under logical `(X,Y,H) -> (X+v,Y+v,H)`; the forward histories are invariant under `Y -> Y+v`. The small [kernel certificate](KERNEL.json) and [fresh direct replay](KERNEL-RESULT.json) therefore exclude arbitrary postprocessing of these retained values, including unrestricted left operators. Helpers remain fixed. The statement does not include partial-frame values, original X, new paid observations or changed input relations.

This stronger proof needs no independence of monomial matrices. The earlier scalar-span and finite-image results below remain separately replayable evidence, with their original restricted statements. No new kappa is claimed.

## Earlier scalar-span certificate

The earlier certificate resolves the physical scalar-span question left open by
[Mark/Matarener's #5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427).
At **every positive tensor width**, no nonzero pure-Y observation is a scalar
combination of all retained full-frame versions of the frozen #5402 backward
word or either orientation of the final #4610 word. All original inputs remain
independent. The complete history is granted, including versions after an exit.

That certificate tests the actual operator algebra. The 215 signed operators have
one genuine four-term linear relation at width one. After including that
relation the observation still does not exist. A full-rank tensor-square Gram
certificate and the shared zero-state anchor cover every larger width. Exact
rational projection ranks and nonzero modular minors play separate roles;
modular nonmembership alone is not used as a rational exclusion.

**The scalar certificate alone is a restricted negative theorem.** The new input kernel above closes arbitrary postprocessing of the same full-frame channel. Changed native schedules, partial-frame histories and new paid observations supply different data and remain outside the channel. The independent inputs, observation version and these limits
are part of the claim. See [PROOF.md](PROOF.md).

## Reproduce

Python 3.12, standard library only, read-only default:

```sh
python3 -B scripts/research_package.py --package research/physical-zqy-scalar-span
```

The registered checks verify the direct all-width input kernel, repeat it over formal free words, independently regenerate the provider kernel with a separate native/group/frame implementation, and compare exact physical phases against the retained Clifford implementation. All run in normal and optimized modes. The ordinary command compares frozen receipts without writing; `--write` explicitly authors outputs.

The initial scalar-rank/Gram and fixed-image certificates are retained unchanged from publication head `6d81d47e6d107e3c52b4583526d31e102b219bdc`. They are no longer dependencies of the stronger kernel proof or default registered replay. They remain optional direct checks:

```sh
python3 -B research/physical-zqy-scalar-span/verify.py
python3 -B research/physical-zqy-scalar-span/abi_closure.py
```

Mathematical/runtime checks are recorded in VALIDATION.md; exact publication byte/export results are recorded in the PR. [INTERNAL-REVIEW.md](INTERNAL-REVIEW.md) distinguishes AI corroboration from external acceptance. No selected cold replay, fresh complete native admission, compiler/outer, precision/tape, Lean or Docker run is claimed.

## Earlier concrete Z-ABI certificate

The earlier bounded continuation grants each backward-provider version one
left image from `{I, Kp_i, Km_a, Km_a^-1 Kp_i}`. The 1,012 distinct physical
maps and 59 actual history operators give 59,708 pairwise nonproportional
products, with exact F9 commutation and phase checks. The resulting span has
no nonzero pure-Y observation for **every f>=59,707**. Thus this fixed bank
cannot implement an all-width observer. This does not assert small-width
nonmembership or closure under arbitrary further products on its own. The new kernel separately excludes this whole channel at every positive width. The proof and
[ABI-CLOSURE.json](ABI-CLOSURE.json) state this as a separate theorem.

## Open next questions

1. Modify the native word to retain pure Ry before Dx is mixed in. Price every
   new observer job, storage slot and eventual termination. A supplied-observer
   invoice is not its construction.
2. Supply a genuinely new, versioned nonfree observation from another paid
   caller event, keeping disjoint mode ownership and every original input.
   Reconstruct one actual current-Y exit before extending the caller.
3. Test a different producer or partial-frame interface with its own exact
   arbitrary-input operator and complete bill. These theorems provide no
   price lower bound for that changed construction.

## Provenance and credit

Prepared by THU New Media Research Center (@thu-nmrc) with substantial OpenAI
Codex assistance from a lead and separate algebra/phase reviewers. These agents
are not independent human reviewers or a proof kernel. Apache-2.0.

- [Mark/Matarener, #5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427),
  head `389578f2d3ef075495ce76f08100ac50e18f7d40`: formal-word question,
  input/ownership/event/version semantics and the explicit physical follow-up.
  `native.py` adapts those semantics with actual signed operator composition.
- [Dillon Amburgey/dillona, #5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402):
  unrestricted coupled provider and all original mode inputs.
- [Cao Yifan/intqwq, #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610):
  final native word and phase evidence. Cinna Davis/1337isnot1337, zxv,
  Dugongue, Jacob Alan Sussman and retained source authors supply its native,
  query, frame, tensor, compiler and analytic lineage.
- [zxv, #5415](https://github.com/CrocSwap/integer-mult-bounds/pull/5415) and
  [#5419](https://github.com/CrocSwap/integer-mult-bounds/pull/5419): current-Y
  observation contract, physical normalizers and consumer/cost obligations.
- [Ali Romman, #5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377):
  retained native row conventions. Chris R/Clear1nsight's provider and caller
  reviews remain separate from this scoped result.

Frozen upstream packages, scientific receipts and selected-frontier files are
unchanged. Exact canonical input blobs and hashes are in SOURCES.json.
