# Encoded shared atom powers for recursive child spectators

The actual BIT caller builds three spectator cardinalities through repeated
`radix_power` traversals. This package moves that traversal outside the runtime
atom loop and shares it across all three powers. The exponents stay encoded;
one reusable blank counter role replaces repeated validator work.

This fills the **child-geometry component** explicitly left open by
[PR4025](https://github.com/CrocSwap/integer-mult-bounds/pull/4025) and
[PR4062](https://github.com/CrocSwap/integer-mult-bounds/pull/4062).
It supplies an opt-in kernel, an adapter to the **actual frozen
`Layout.child_extents` method**, and a complete source-action comparison.
It does not supply the complete recursive caller or a new κ.

| Same complete geometry/cleanup input | Original actions | Shared actions | Reduction |
| --- | ---: | ---: | ---: |
| Internal-child width 70, n=321, q=3, w=2 | 7,046,111 | 5,038,964 | 28.49% |
| q=5, even columns, w=2 | 2,334,453 | 1,042,650 | 55.34% |
| No remainder, rank 42, w=1 | 84,977 | 34,668 | 59.20% |

Across the fifteen declared pairs the reduction is about 28.49%–59.20%.
These totals sum retained **record, residue-Word and index-Word** reads,
writes and unit moves. Added probes, counters, copies, marginal conversions
and disposal are charged. They are not physical-machine step counts or a
measured production-runtime speedup. The tested additional per-bank numerical
peaks remain index 21/residue 6. No complete physical reserve follows.

## Component API and exact budget

`Powers(env, workspace=None).multiply(items, ring, q)` accepts one to three
fixed pairs `(owned_count, borrowed_exponent_word)`. It maps each Count v to
`v*(q^w)^e`, preserves the Ring/exponent inputs at their canonical heads,
and returns its distinct **owned blank** counter role erased at head 1.
A caller can provide an existing blank role; arbitrary dirty acquisition is
not implemented. `runtime.adapt(env,powers)` returns the source-method adapter
without changing the original method or frozen files. The reference loader
uses a private interpreter/module context; this is a research component,
not shared-caller installation.

For E=sum(e), k positive exponents and complete radix invoice rho, the exact
old-minus-new residue invoice is `(E-1)*rho` when k>0. The extra index bill
is `w*k*(3I+3,0,2I+4)`; the complete counter delta has a closed form in
[PROOF.md](PROOF.md). It is checked against individual trailing-zero cases
and actual source Counters. Counter costs are not treated as free.

A **same-output exponent-one losing control** demonstrates why this is not
a universally faster primitive. Future callers must prove the complete
budget at their site, including any dispatch rule, instead of replacing
all powers indiscriminately.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-child-spectators
```

Expected markers: `PASS_ENCODED_CHILD_SPECTATORS`,
`PASS_INDEPENDENT_CHILD_SPECTATORS`, `PASS_CHILD_SPECTATOR_CONTROLS`, then
`PASS_REGISTERED_RESEARCH_PACKAGE`. Normal replay is read-only; receipt
creation with `verify.py --write` refuses an existing destination.

[CERTIFICATE.json](CERTIFICATE.json) records all paired bytes, complete
lane invoices, ownership/head restoration, erased backing and geometry.
[TIMINGS.json](TIMINGS.json) records single same-input Python observations;
timing values are not mathematical acceptance fields.

Coverage includes all six source child-geometry branches at w=1/w3, remainder
and gap placements, width 70 (above the recursive cutoff), q=5 and rank 42.
These are valid geometry instances, not complete production packets or a
proof of every chosen source's top-level reachability. The independent
checker imports no runtime/primary code. It rederives geometry and counter
accounting, taking rho as the measured validator invoice rather than
reimplementing the source's full Ring arithmetic. Controls include real source
geometry guards, 26 Counter tariff calibrations, omitted output work,
alias/reentrancy, invalid radix detection, source/inventory corruption,
typed receipts and overwrite refusal. Word.inspect is disabled during the
measured interval. Error detection is retained; full malformed-input or
interruption rollback is not claimed.

Exact base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
[SOURCES.json](SOURCES.json) seals eight canonical live files; all are checked
before source execution. [CONTEXT.json](CONTEXT.json) pins predecessor heads
and the claim. OS seed 4 selects the BIT track and nonunit spectator cases.
Frozen predecessors and the selected frontier remain unchanged.

## Open next questions

Compose this adapter with #4062's actual Context/directory/admission interval,
using one existing blank counter role, then pay fixed capsule and payload
copies and all lifetime backing. That is the next concrete join; a tiny
controlled payload does not establish the full production caller.

Prove a useful source-coupled parameter region from the exact action formula,
including any encoded original/shared dispatch. The existing finite savings
do not establish a global speedup. Physical control/allocator tariffs,
original-width stock, whole payload/source admission and supplier transfer
remain separate. Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

David Arias/PR2753 supplied ordered child geometry and the logical caller;
Jose Manuel/jmbarrancoml supplied the fixed-role caller and retained runtime.
ToikY/PR4025 supplied the fixed-d² shared-radix precedent, following ywz65/PR2590;
Chris R/Clear1nsight/PR4062 supplied the preparation composition and released
geometry handoff. All retained source/record/codec/caller attribution remains
with the unchanged originals. This extends the mechanism to **runtime encoded
atom exponents and the actual three-spectator method**; it does not re-claim
the fixed-d² result.

Tekalign (`tekuuu`), substantial OpenAI Codex assistance in design, tariff
proof, implementation, controls and packaging. Apache-2.0. Exact finite
checks are not independent human review or formal multiplication verification.
