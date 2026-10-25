# Validation and limits

Author checks on macOS, CPython3.12, standard library only. No heavy solver,
Lean, Docker, complete multiplication replay or predecessor suite was run.

- Registered normal and optimized independent replay passed. The final verifier
  includes 272,160 complete normalized nonzero GL2 local cases, 1,621 zero-case
  controls, all1,296 GL2 transport-pair ranks, 36 dirty obstructions over12
  sampled orders and3 exact nine-call positive controls.
- A separate sparse group-ring implementation applies the entire word before
  projecting modulo I^3. No predecessor executable or precomputed oracle is imported.
- Source metadata, committed-byte/source-history and explicit-input-ref export
  are checked at the final commit; a read-only Git-free extracted copy is replayed.
  Export success is a packaging check, not mathematical acceptance.
- The all-m, all-order and arbitrary PBQ statement rests on PROOF.md. Finite
  GL2 checks and m3 word fixtures are corroboration only.

Initial metadata used an invalid outcome label; the validator rejected it and
it was corrected to `completed` before the final registered replay. The label
means the scoped task is complete, not that the full register model is solved.

Remaining obligations: arbitrary other patterns, four-term syzygies, additional
mixing/registers, even denominators, and paid native implementation are unproved.
No selected result or recursive invoice is changed.
