# T74 cost in the actual selected width

I adapt the physical T74 root to reserve and recurse from its actual selected
width g. With PR3562's ordinary profile and a changed stopping rule, I prove

    O(V g^.99827101 log p) time and O(V)+F_q space,
    1<=g<=floor(p^.997).

I retain the source-native, hosting, physical refinement and complete-record
premises. I return normalized H0 on the selected bits, preserve the other
coordinates, and keep one final truncation. I claim no new multiplication
exponent or selected-frontier change.

The previous root chose d=floor(p^.997) even when g was smaller. I now choose
d=g, keep its complete field formulas and full-depth stock, and prove the
small-g fallback within the same bound. I also replace the ordinary profile
with c=1/577 and the stopping power 1000 with 10^6. I authenticate all 23 ordinary
backend files against the rate proof and retain one physical tape cohort.

I state the quantified domain, complete invoice and source qualifications in
[PROOF.md](PROOF.md). Actual complete coefficient records must satisfy
`r>=2^(b(log2 p)^2)` and `log2 r<=Bp`, for fixed b,B>0, with the retained
O(p) address/descriptor bound. I do not manufacture those records from a
fixed coarse label or an unvisited suffix. The constants may depend on b,B
and the finite source.

I give a separate single-bit exposure lemma. For a globally complete dyadic
tensor, I can map g selected bit positions to g spaced target positions with
support at most 2g. Conjugation then transfers the root endpoint to the original
selected bits. The fast global cost additionally requires the pinned paid
support-router contract and retains its polylog p factor: I obtain the
conditional global bound O(V g^.99827101 polylog p). I supply finite exposure
certificates and a physical root composition check; I do not implement that
arbitrary-support router.

## Implementation and reproduction

I provide ActiveWidthPlan, RetunedMachine and ActiveWidthRoot in isolated
modules. I compare each copied function against its frozen predecessor after
the declared deltas: one stopping site, one planning substitution and two root
constructor targets. I inherit the execution loop, private release, child
return, grid conversion, phases, padding and normalization.

Use active_sources.opened() to retain the authenticated source context for the
whole construction and invocation. production_layer() binds the retained
T74 source and the retuned native factory. The full production finite factory
has impractical size; the registered runtime tests use reduced bindings.
The root run signature and signed component format match PR3477. Consume the
output before reuse. I change no shared source or default.

With Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/t74-retuned-physical-layer
```

I record executed coverage in [EVIDENCE.md](EVIDENCE.md). The source exports
retain the complete runtime and mathematical premises, so a scientific replay
needs no foreign Git object or network. I do not rerun the unchanged large
native compilation and supplier admission suites; I preserve their evidence
and scope and check the new code and source binding.

## Source and scope

I start from canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. I retain PR3477 at `75343dd7e067c40d18c243ea97231b7006680eef` and
PR3562 at `abb93be8b9ceca07a2b17f3a97db7bb6b074271d` as author-checked
dependencies. I coordinate in [Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).

## Open next questions

Can we implement the paid arbitrary-support exposure and actual untouched-
record placement in the same physical cohort? Start with the retained
support-router matching, reservoir and sparse-repair contracts. The current
equally spaced compact control does not implement arbitrary supports, and
individual bit swaps do not establish its sublinear routing exponent. Nick
Petalas proves a Theta(Vg) obstruction for a hard isolated-support family
under completed, materialized B1 exchanges in
[PR3581](https://github.com/CrocSwap/integer-mult-bounds/pull/3581). That restricted
adapter cannot supply the conditional global bound. Start with the richer
router contract, including its controlled rotations and sparse repair.

Can we then bind this selected-width service to a complete outer caller?
Retain the global coarse ranges, raw-H conversion, error accumulation and
the g cap. Batching larger groups changes the main-transform bill. I do not
inherit PR2979's modern headline or PR2298's weaker caller rate by substitution.
Independent scientific review of the inherited all-size premises remains open.

## Attribution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in proof,
implementation, verification and source analysis. Apache-2.0.

I retain the PR3385/3477 physical controller and root, PR3562 ordinary-rate
proof, David Arias's PR2753 caller, Nick Petalas's PR2808 wrapper and PR3493
dimension/format bridge, Adam Gall's PR2087 uniform lifting, and the existing
native, numerical, parking and primitive lineage in the source notices.
Marius-Paul Dumitrean/Dugongue and Jeremy Kothe supplied the retained T74 word
and profile. Vlado Vojdanovski's PR1673 supplies the conditional support-router
and tensor-interface arguments. I claim the actual-width binding and the
stated single-bit exposure composition, not those predecessor methods.
I claim no independent human or formal-kernel review.

Hiroki Kumazaki concurrently binds the retuned ordinary cohort to the older
root and stopping power 1000 in [PR3576](https://github.com/CrocSwap/integer-mult-bounds/pull/3576),
head `1630afea0fc1083717b5b2799b8de7a819a6ea02`. I adapt his
[explicit binding-module namespace and lazy-import boundary](https://github.com/CrocSwap/integer-mult-bounds/blob/1630afea0fc1083717b5b2799b8de7a819a6ea02/research/t74-retuned-ordinary-layer/factory.py#L50-L111)
and whole-constructor/stale-alias checks. He contributes those shared factory
and rate steps; I add actual-width planning and the deeper-stop theorem.
I use Nick Petalas's PR3581, head
`282915e57cf71d7a6f0087fbb6ae03345a0b33d4`, to delimit the B1-only exposure
option. Both contributors retain their Apache-2.0 attribution.
