# Scoped skeptical review of the common word

Local-only separate agent review; substantial OpenAI Codex assistance. This is not independent human review, formal verification or a full inherited theorem audit.

Candidate: `/private/tmp/integer-mult-p104-a2-submit/research/p104-a2-neutral-cleanup/WORD.json.gz`, compressed SHA256 `e94809cecf9e9cba56dd7a8a11ff1edeedc4c34013ff6caebdaf3b021351cf8c`.

Sources read: COMPOSITION-PROOF.md, audit_composition.py, verify.py, pricing.py, COMPOSITION.json, and the retained [Ali Romman](https://github.com/aliromman) [PR #5644](https://github.com/CrocSwap/integer-mult-bounds/pull/5644) constructor, WITNESS.json and PROOF.md. The A2 source is [zxv](https://github.com/zxv)'s [PR #5643](https://github.com/CrocSwap/integer-mult-bounds/pull/5643). Exact heads remain c5871955d89bf73506fd68b0a5bf1cf2b3153c02 and a3ff5c628bfc8825553d62d913f3e91f75d6825f, respectively.

No concrete objection was found to the changed local functional argument:

1. For a cleanup helper h, the checked prefix relation is a full rational row equality. Preconditioning changes only the initial coordinate h; substitution turns the canceled prefix row into s*x_h. All involved input operations share the initial chart, and cut operations share the final chart. Division by the dyadic unit s is an ordinary SCALE already emitted and charged.
2. The original complete scalar endpoint has helper h only in its own output. Therefore preparing h cannot change the other final rows. No later operation reads h as a source, so replacing its cut value and deleting only its own scalar suffix cannot feed a changed value into another output.
3. The A2 identity holds for every prefix triple, without a zero-input assumption. The lightweight audit confirms that applying A2 after cleanup produces the exact common scalar skeleton and independently reconstructs the identical entire typed MOVE/scalar program. This is stronger than assuming disjoint histogram deltas.
4. Public/owned inventories and boundary charts remain fixed. The complete owned-event subsequence is retained. The extra ordinary scalar charge is explicit: 220,220 total, +54 above the A2 word and +12 above cleanup alone. Every productive target is retained; the changed local paid deltas are exactly the declared A2 and three cleanup deltas.
5. The frame-invariant proof uses full chart maps with phase and exact chronological native transports. It does not commute noncommuting operators or distribute tensor powers over sums. Actual phase/native/caller verification remains necessary and belongs to the parent's separate full replay.

Executed only cheap checks:

- `python3.12 -B research/p104-a2-neutral-cleanup/audit_composition.py`: PASS_INDEPENDENT_COMPOSITION_ORDER_AND_FRAME_AUDIT; 25,449 chronological events and 22,015 scalar events.
- A separately implemented scalar interpreter in `check_composed_centres.py` checks every one of the 752 complete endpoint rows and all final owned zero states. This interpreter does not import the construction or local checker.
- The same interpreter repeats the current-frame public-span screen on the actual composed word. All eight H7 centre sources remain independent and none is already reconstructible from available public values at its first delivery chart/time. Prepared751 first reads are reconstructible but carry no paid MOVE. See COMPOSED-CENTRE-RECONSTRUCTION.json.

Suggested wording clarification: the original helper's endpoint is its independent input **as a scalar row in normalized reference coordinates**; physically it is still the credited map Φ_final Φ_initial^-1. This is a clarity point, not a mathematical objection.

Not rerun here: native phases, physical caller, rational price engines, compiler/outer suite, source archive import or hosted CI. No new ownership, erasure, native alphabet or all-width realization premise was identified in this local review; the inherited five framework assumptions and helper-endpoint contract remain.
