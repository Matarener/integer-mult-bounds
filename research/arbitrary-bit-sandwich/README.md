# A paid arbitrary-bit boundary for the CRT/Tensor Sandwich

This contribution was produced by Nick Petalas. It supplies a new physical
caller construction under a completed-child contract, with finite exact
corroboration. No new kappa or selected-frontier change is claimed.

[boundary.py](boundary.py) implements the released arbitrary-bit wrapper
handoff in [Discussion #3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664).
The retained [PR #5095](https://github.com/CrocSwap/integer-mult-bounds/pull/5095)
Sandwich accepts whole little-endian radix words. The new wrapper accepts two
complete n-bit MSB-first operands, including leading zeroes, and returns
exactly 2n MSB-first product bits. Both n and b stay on encoded Count tapes.

```text
validate both n-bit operands
q = ceil(n/b), d = qb-n, computed on Count tapes
reverse each n-bit operand and append d high zeroes
call Sandwich.run with its mandatory production recovery policy
check the first 2d returned bits are zero; copy exactly 2n bits
consume the child's return and erase both packed operands
return the protected 2n-bit result; consume() later erases it
```

[PROOF.md](PROOF.md) states the representation, ownership and cost contract.
The packing formula and high-prefix observation are credited to JoyboyBrian's
handoff. The new contribution is their implemented, paid, reusable boundary
on the retained physical runtime, including malformed-return cleanup.

For n=5, b=3, x=29 and y=23, the actual packed streams are `101110` and
`111010`. The completed-child fixture supplies twelve output bits;
the wrapper checks two high zeroes and returns `1010011011`, the ten-bit
representation of 667. Its full boundary lifetime uses exactly 1,738 reads,
468 writes and 1,746 unit moves in that fixture. These counts include both
child-return consumption and final wrapper-return consumption. Only
`child.run` and host oracle/inspection work are excluded. This is an exact
operation tally for that fixture, not a runtime comparison or a production
cost estimate.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/arbitrary-bit-sandwich/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/arbitrary-bit-sandwich/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/arbitrary-bit-sandwich
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/arbitrary-bit-sandwich --check-source-history --check-modes
```

Any CPython 3.12 executable can replace the local path. The direct marker is
`PASS_ARBITRARY_BIT_SANDWICH`. Each run emits a deterministic JSON receipt
bound to every package file's SHA256. No receipt is handwritten or retained
as a generated checkout file. Normal replay reads its declared inputs and
uses the inherited authenticated loader's temporary source export.

## Evidence

The verifier checks 1,845 positive physical boundary invocations. Of these,
1,700 exhaust every pair of n-bit operands for 1<=n<=4 and 1<=b<=5. Another
144 cover the stated six larger widths through n=33 and six radix widths,
and the explicit 29-by-23 fixture supplies the final case. Exactly 869
invocations have n not divisible by b. Every returned bit, borrowed port,
erased boundary bank and child-return lifetime is checked. The observed
metadata scratch peak is seven leases from the fixed capacity of 32.

Five completed-child failure controls cover a nonzero discarded prefix,
short return, extra return, invalid output symbol and child entry failure.
Eight input controls cover both ports' short/long/invalid bodies and zero
parameters. Fourteen ownership controls cover payload and metadata aliases,
four resident/child aliases, an occupied return with its head at the end,
and double consumption. Successful reuse follows the failure controls.

The actual unmodified Sandwich is instantiated with its retained physical
Tensor and CRT Converter owners. The wrapper reaches its production guard
with the reduced p48 catalogue and preserves its rejection. Both owners
and every boundary role clean up. No positive production numerical payload
is executed. Positive child fixtures are explicitly supplied exact oracles;
their host arithmetic is outside the charged wrapper.

[SOURCES.json](SOURCES.json) binds canonical main
`3f0152a32eeebac0df11946dbd50cabe5a7f7839`, the original task card and all 74
runtime/source inputs. The predecessor's scientific verifier is not run.
The selected baseline control reports `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
with selected kappa `781451/250000000`; that control authenticates metadata.

## Limits and implementation discipline

The result assumes canonical positive Count inputs and the retained completed
Tape/Count operations. The child must satisfy its exact recovered-product
contract, preserve borrowed ports, and close failed invocations. Source
catalogue, precision, locality, native, analytic recovery and all-size
parameter obligations remain with that child and its caller. The new wrapper
never selects the diagnostic `require_recovery=False` policy. Production
catalogue admission, a complete multiplier, a full physical numerical replay,
the selected cold replay, Lean and Docker are unrun. Independent human and
formal proof-kernel review are unclaimed.

The new runtime has no recursion or data-dependent host decoding. Payload
loops have encoded finite countdowns bounded by n, d, 2d or 2n. Inventory
loops have fixed bounds of 35 resident tapes and 32 leases, together with the
child's fixed inventory. Every function is below 60 physical lines. Failure
checks remain active under optimized Python. Warning-strict normal and
optimized registered replays supply recurring diagnostics.

Power of Ten rule 3 deviation: CPython allocates objects and extends tape
backing during execution. This verifier and reference runtime therefore do
not claim allocation-free host execution. The physical construction fixes
35 resident boundary tapes before entry, and sealed constructors reject a
new physical Tape or Arena during the run. The payload banks have finite
encoded extents, and the metadata pool fails explicitly on exhaustion.
Larger fixtures must retain these contracts and state their own host limits.
Rule 9 deviation: the completed-child call is a deliberate interface dispatch.
Its allowed target must establish the stated ABI. Tests use the exact fixture
child and the authenticated original Sandwich; they license no other target
without that proof. The inherited loader's bounded source extraction and
constructor specialization remain source dependencies, not new runtime code.

## Open next questions

- Bind an admitted production catalogue and an all-size parameter family to
  this wrapper. First choose n, b and a catalogue satisfying `Sandwich.admit`
  and charge the full coefficient/native construction. Production admission
  and the retained numerical assumptions are the blockers.
- Execute one complete recovery-admitted Sandwich invocation through this
  boundary. First supply a genuinely admitted catalogue; the retained reduced
  p48 fixture intentionally fails that policy. Positive boundary oracles do
  not resolve this numerical obligation.

## Credit

JoyboyBrian supplied PR5095's Sandwich and the released packing/lifetime
handoff in Discussion3664. Jose Manuel / jmbarrancoml supplied the physical
Tensor, expansion/chirp sources and Tape/Count runtime; Tekalign / tekuuu
supplied the CRT Converter. Mason Hale's recovery work, source07/source08,
Chafik Boukhalfa / RaD, hipotures and all retained Fourier/native/word-runtime
contributors retain their original credit and notices. No predecessor code
or credit line is changed. New material is Apache-2.0.
