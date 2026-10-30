# Conditional kappa 0.00310299 from delayed shared preparation

This construction raises complete conditional kappa from **0.00310184** in
[PR #5608](https://github.com/CrocSwap/integer-mult-bounds/pull/5608) to
**0.00310299**, a gain of **0.00000115**. Its new mechanism delays the
preparation of public helper696 by reusing a complementary component already
present in helper700. Coupled corrections remove the remaining owned738
delivery into159. Every retained independent helper input is preserved exactly.

The new mechanism has paid delta `H4+H7-H5-H6`, strictly negative for
`Hr=r^t`, `0<t<1`. It is composed with the existing 13 independent helper
splits, Ali Romman's coupled-frame step from
[PR #5601](https://github.com/CrocSwap/integer-mult-bounds/pull/5601), and
Scratch-net's prepared split-helper retirement from
[PR #5606](https://github.com/CrocSwap/integer-mult-bounds/pull/5606).
Those contributions and their costs are explicit, not attributed to this work.

The exact raw crossing is **(0.00310299359333,0.00310299359334)**; the claim
is tested at 0.0031029905. The full bill has **66,636 paid calls, 13,030
independent productive targets and rank surplus760**. The final word has
**747 independent inputs, 539 helpers, nine owned roles, 11 owned lifetimes,
peak owned occupancy two and 25,529 events**. Every added ordinary operation,
owned lifetime, route and target debit enters the complete accounting.

Read [MECHANISM.md](MECHANISM.md) for the new delayed preparation,
[COMPOSITION.md](COMPOSITION.md) for the full construction, and
[RESULT.json](RESULT.json) for the exact native/caller/price receipt.
The selected frontier is unchanged. These are finite exact checks and a
conditional bound calculation, not independent human or proof-kernel acceptance.

## Reproduce

Python3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/p104-delayed-shared-relay
```

Normal and optimized modes print `PASS_P104_DELAYED_SHARED_RELAY_KAPPA_00310299`;
the launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Verification authenticates
the official 24-file PR5608 export and its nested unchanged33-file framework
closure before importing code. It reconstructs every stage, checks all13 fresh
prefix/suffix witnesses and every intermediate independent-input identity,
checks all756 final rows and transpose columns, all signed native maps, the
physical caller, complete paid/target bill, two interval engines at the tested
endpoint, the compiler and58 outer predicates. Five controls reject missing
owned initialization/return, missing new cleanup, a falsely retained target
and an uncharged transport. Gzip equality uses complete decompressed payloads.

The checker adaptation from PR5606 changes the explicit interface constants
750/758/749 to748/756/747, inlines the same exception helper and selects MOVE
direction by validated ownership. The verifier compares the remaining checker
body exactly to its pinned source. The retired573 role has no MOVE in the
submitted word. The [pricing diff](PRICING-CHANGES.diff) retains the source's
mathematical tests; only endpoint/comparison/count declarations change.

## Limits and ceiling

The five inherited framework assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision and fixed-tape costs, and
analytic recovery. The inherited helper-endpoint contract remains. The enormous
uniform word and complete rounded multiplier are not materialized.
The prepared-helper step uses the existing owned-erasure contract explicitly;
it does not count the retired prefix as an independent productive target.

The fixed invoice has a strictly decreasing signed moment on[0,0.0034].
Its raw funding ceiling is the interval above, leaving between3.59333e-9 and
3.59334e-9 above the claimed endpoint. This is not an optimum over other words,
inventories or suppliers. The uniform compiler retains logarithm power1024,
tail decay39/40 and the full reserve/outer conditions.

## Sources, independent checks and credit

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision7.
The final upstream refresh reached `d7633ce230196a1d5d061347de7a0fd8be512ed6`;
the guidance, priority catalogue and selected record were unchanged. That update
archived predecessor research; archival intake does not change scientific acceptance.
The assigned scalar-to-moment task is refined to changed public dependencies
and composition with independently introduced target and ownership changes.
Source pins and retention history are in[SOURCES.json](SOURCES.json).

PR5608 is pinned at `5ec3b5b3ee4738f896e823c1dfc04e7ff1789ffb`; PR5601 at
`8f7e870b22885a367b347dc12791da98fd53f83d`; PR5606 at
`cd7d89345c6c5d2114625e5ce912a52ecd5e1d27`. The PR5608 export retains exact
PR5580, PR5565, PR5599 and PR5605 source files and their original notices.
No foreign branch-object cache is required for replay.

Credit Ali Romman for the independent split identity, frame step, source word
and native/caller/price machinery; Pierre-Loic Doulcet/hexapode for the commuting
cascade; Scratch-net for prepared573; Joel Pulikkan/GamingPuzzled for successor
handoffs; DreamingOfClouds for free endpoints and event-level tools; thu-nmrc
for coupled contacts; Gareth Davidson, David Arias, Cinna Davis, Jacob Alan
Sussman, zxv, Cao Yifan and all retained geometry, BIT and analytic predecessors.
The new delayed696 P104 construction, composition and verification were prepared
for flyingviper with substantial OpenAI Codex assistance. Independent agents
derived and checked the current-value identities, ordered cleanup, split
compatibility, prepared ownership and complete invoice. These are separate
agent calculations, not independent human review. Apache-2.0.

## Open next questions

For another owned delivery, identify complementary early public expressions
that persist until its signal is available. First derive an exact current-value
identity and the live-input endpoint effect; only then construct invertible
nuisance corrections and charge its full itinerary.

A separate opportunity is another prepared split prefix: at each of its paid
MOVEs, test whether its current row can be reconstructed from already coframed
public rows modulo that prefix's own independent input. Every reconstruction,
owned lifetime and retired target must be charged. No further prefix candidate
is claimed here. Structured next questions are in[TASK.json](TASK.json).
