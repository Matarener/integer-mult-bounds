# Defer the P112 five-plane decoder's dirty-endpoint corrections

**Exact algebraic opportunity; no new supplier or κ.** The selected P112 labels split into 22 orthogonal five-frames and one orthogonal pair. The existing five-plane package prices one rank-one-equivalent cleanup for each of the resulting 23 block translations. This package checks a different schedule: apply every block lift to one shared nine-bit address register and defer all 23 cleanups until the end.

Let `q_i ∈ F₂⁹` be the pinned selected labels, and let `E_g` be one block. The predecessor verifies, by exact Gaussian-dyadic replay, that

`C_{E_g}² = X_{δ_g}`, where `δ_g = ⊕_{i∈E_g} q_i`.

The 23 blocks partition all 112 labels, whose xor is zero. Therefore

`∏_g C_{E_g}² = X_{⊕_g δ_g} = X_{⊕_i q_i} = I`.

The verifier checks each local identity on all 512 address basis states, and checks that the 23 shifts xor to zero. It also confirms that their span has rank 9: the cancellation is a global relation, not pairwise cancellation.

## Cost consequence and limit

The existing exact local `u=5` screen has an `a` ceiling of `0.017542237243537` before charging these translations. Charging 23 rank-one-equivalent cleanup units lowers that screen to `0.016435974402421`; the optimistic allowance for all additional route, hosting, restoration and precision work drops from 157 units to 134. Deferring cleanup would recover those 23 units in this local ledger.

This is **not a new κ**. The cancellation saves cost only if all block lifts act on the same nine-bit address register and the translations can be deferred across the block schedule. If the physical implementation materializes a separate output stream or address register for each cover class, the translations act on distinct state and do not cancel across classes. The current five-plane package has no native owner map or physical schedule that settles this condition. The result changes neither the selected record nor the multiplication bound.

The local ledger is a planning relaxation, and one unit per translation is the predecessor's provisional price. Unknown physical costs remain unknown; they are not zero.

## Reproduce

From the repository root:

```sh
python3 -B research/complex-global-delta-cancellation/verify.py
python3 scripts/research_package.py --package research/complex-global-delta-cancellation --check-only
python3.12 scripts/research_package.py --package research/complex-global-delta-cancellation
```

The scoped replay binds the selected source archive, five-plane candidate, predecessor source manifest and matching certificate. It checks the 23 exact local endpoint maps, their global xor, the local budget screens, and controls for a missing block and a duplicated port. It does not synthesize the shared-register physical schedule.

## Open next questions

Can the native source/consumer route schedule all 23 `C_E` lifts on one shared nine-bit address register, with a single deferred endpoint correction and all output streams restored? This matters because it decides whether the 23-unit margin is real. First map one five-frame block through its actual producer and consumer, then determine whether the next block continues on that same address register. The blocker is the missing owner and restoration schedule; stop if blocks require distinct live output registers.

## Provenance and credit

This is a changed-scope follow-up to `coverage-law-change`, using the existing selected P112 five-plane algebraic decoder. It retains the predecessor's selected-label attribution and exact pins in [SOURCES.json](SOURCES.json). The predecessor remains the source for its 16-term, charge-118 factorization and local `u=5` budget. No selected frontier update or PR claim of improved κ is made.

Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. Apache-2.0.
