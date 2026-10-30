# Conditional kappa 0.00308326 from a shared dirty public relay

This construction raises the complete conditional kappa from **0.00308189** in
[PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) to
**0.00308326**, a claimed-endpoint gain of **0.00000137**. It replaces two owned
deliveries by a shared public relay, then exactly compensates the relay's
arbitrary initial inputs. The complete paid profile changes; this is not an
improvement obtained by reporting more root digits or fewer scalar additions.

For each of 18 local calls, the paid change is `H6 - H1 - H2 - H3`, where
`Hr(t) = r^t`. Strict subadditivity makes this negative for every `0 < t < 1`.
The complete bill has **66,816 paid jobs** and **12,814 productive targets**.
All public endpoints and productive targets are unchanged. There are still
735 arbitrary public inputs, eight owned lifetimes and owned peak one.
The 25,167-event local word adds 29 ADDs and removes two MOVEs relative to
the 25,140-event source; it remains below the inherited 26,000-event bound.

Read [PROOF.md](PROOF.md), the deterministic [construction](construct.py),
the [complete verifier](verify.py), and [RESULT.json](RESULT.json).
The exact raw crossing lies in **(0.00308326461942, 0.00308326461943)**;
the claimed endpoint is tested at 0.0030832605. The raw crossing gain over
the source lies in (0.00000136965075, 0.00000136965077).

## Mechanism and scope

Public helper 587 already acquires twice the useful signal together with an
arbitrary nuisance value. Moving this existing preparation earlier lets one
new contact replace the two owned reads into 203 and 148. Twelve initial
zero-frame ADDs cancel the nuisance at the lower-dimensional endpoints;
18 later full-frame ADDs restore the remaining outputs. Here zero-frame means
a zero-dimensional chart, **not a zero-valued input**. The input correction is
explicitly invertible. No clean helper, free erasure or extra storage is assumed.

Removing the 148 read also makes one intermediate public frame unused. Its two
adjacent transports contract to one. The relay and this contraction are both
included in the claimed profile and all verification below.

This changes public scalar dependencies and therefore lies outside the
fixed-contact shortest-path scope of
[PR #5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590), and outside
the fixed joint boundary studied in
[PR #5591](https://github.com/CrocSwap/integer-mult-bounds/pull/5591).
It is a small constructive P104 improvement, not a new controller or a claim
of optimality. The selected record is untouched.

The prepublication refresh found stronger concurrent claims:
[PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565) reports
0.00308520 from a commuting-contact cascade, and
[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) reports
0.00309839 from independent helper splits. This package therefore does **not**
claim to be the best current pending P104 endpoint. It isolates a different
paid-profile mechanism. Composition with those proposals requires an exact
combined word, target inventory and complete caller/price replay; their
headline gains must not simply be added.


## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-shared-residual-relay
```

The registered normal and optimized modes each print
`PASS_P104_SHARED_RESIDUAL_KAPPA_00308326`, followed by the launcher's
`PASS_REGISTERED_RESEARCH_PACKAGE`. The complete checks authenticate source
bytes and all 33 dependency payloads, regenerate every word field, replay all
743 final rows on all 735 arbitrary inputs, check the dense transpose and
2,918 distinct signed native maps, replay the physical caller, and check both
rational interval engines, the compiler and all 58 outer predicates. Five
negative controls reject missing initial/final corrections, a wrong relay
coefficient, missing transport and an unchanged claimed invoice.

Source bytes and provenance are recorded in [SOURCES.json](SOURCES.json).
The PR5580 word, pricing source and loader, and the PR5545 source closure are
retained unchanged. Regenerated gzip output is compared by its entire parsed
payload, not by a platform-dependent compressed-byte hash. The five pricing
declaration edits are shown in [LITERAL-CHANGES.diff](LITERAL-CHANGES.diff);
the inherited mathematical tests are unmodified.

## Limits and ceiling

The inherited framework assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision and fixed-tape costs, and
analytic recovery. Independent acceptance of the source's helper-endpoint
contract is still required. The uniform word and complete rounded multiplier
are not materialized. This is an exact finite certificate and conditional
bound calculation, not proof-kernel verification of the multiplication theorem.

The verifier proves that this fixed invoice has strictly decreasing signed
moment on [0, 0.0034]. Its funding ceiling is the raw crossing above. Remaining
headroom above the claimed endpoint is between 4.61942e-9 and 4.61943e-9.
That ceiling does not constrain other words, dependencies or suppliers.
Larger proposed numerical endpoints with unresolved additional compiler or
attachment premises are not asserted to be weaker than this result.

## Independent checks and credit

Three separately tasked Codex agents derived or checked the dirty-relay
identity, invertible initial correction, full-frame residual and final
unused-frame contraction. The shared-owned and literature agents independently built words matching
the submitted generator's complete payload. A third agent used a differently
ordered equivalent construction and directly replayed the submitted word. The root ran the full native/caller/pricing
verification. These are independent agent calculations, not independent human
review or independent implementations of every inherited framework check.

The base is canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`.
The source is Ali Romman's PR5580 at
`6efa248cf456d6101d757e9d09ba29711d18a13a`. His source preserves credit to:
Joel Pulikkan (@GamingPuzzled) for the PR5569 helper-706 handoff and PR5472
successor handoff; @DreamingOfClouds for the PR5561 free-endpoint word and
event-level toolkit; @thu-nmrc for PR5551 coupled contacts; Ali Romman for
PR5544/PR5545 caller and closure; Gareth Davidson, David Arias and Cinna Davis
for the P104 word, coalescing and private reuse; Cinna Davis for the controller;
Jacob Alan Sussman for productive recursion; and zxv and Cao Yifan for the
interval, compiler and native framework. Earlier geometry, BIT and analytic
notices remain in the unchanged source capsule.

New construction, proof and verification prepared for flyingviper with
substantial OpenAI Codex assistance and independent agents. Apache-2.0.

## Open next questions

Can coupled relays replace further owned reads while allowing their nuisance
terms to be cancelled at the common initial frame? First test the changed
word's exact endpoint map on every nonzero-frame input; a free correction of
helper-only nuisance cannot repair a remaining live-input obstruction. Only
then construct an invertible initial correction, restore full-frame outputs
and price every changed transport. Independent review of this construction
and the inherited framework obligations remains valuable. Structured next
questions and the refined task scope are in [TASK.json](TASK.json).
