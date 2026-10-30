# Encoded twiddle header to a complete signed packet

Copyright 2026 Sagar Thakrar. Apache-2.0. Prepared with substantial OpenAI
Codex assistance, including separate implementation, proof and verification
agents. These are same-session reviews, not independent human acceptance.

This package connects the **actual output tape** of Nick Petalas's
[PR3593 encoded producer](https://github.com/CrocSwap/integer-mult-bounds/pull/3593),
at `46c04613a19a5b7bd50d98e50bbc8ea8dc6275b0`, to a new sequential signed
Gaussian polynomial packet consumer. It closes the single-header signed
rotation boundary; it does not implement a complete synthetic round or layer.

## Endpoint and execution

Write `r=2^ell` and the emitted residue as `E=epsilon*r+s`, with `0<=s<r`.
The output is multiplication by `y^E` modulo `y^r+1`: emit the final `s`
input coefficients with sign `(-1)^(epsilon+1)`, followed by the first
`r-s` with sign `(-1)^epsilon`. Both real and imaginary signed components
receive the same sign. The proof retains the producer's exponent contract;
the new consumer implements this exact integer endpoint.

`Consumer(ell, width)` admits and allocates blank simulator storage.
`run(header, descriptor, width_descriptor, source)` then borrows:

* the producer's raw MSB-first header tape, at head zero;
* that same producer's descriptor, whose first field is unary `ell`;
* a unary width tape `^ 1^width $`;
* a complete framed packet `^ bits $`, with `r` Gaussian coefficients,
  real then imaginary, each component MSB-first in signed two's complement.

Execution reads no host-decoded exponent, allocation size or tape index.
Initialization itself follows the borrowed source and unary descriptors.
Two little-endian counters split the packet. A marked highest set bit lets
decrement stop at the carry boundary and detect zero locally. Their total
decrement work is linear in the number of coefficients, rather than paying
the full counter width each time. Word scans use the encoded width; signed
negation scans the actual word backwards.

The one-shot consumer preserves borrowed contents, restores their heads,
and erases all private work except its returned output. A signed minimum
is admitted when copied unchanged and rejected when it would be negated;
that rejection also restores borrows and erases output/work. Matching
allocation dimensions, complete valid framing and separate backing storage
are admission premises. Arbitrary malformed-input recovery, dirty private
entry, interrupted execution and reusable-object semantics are not claimed.

## Paid boundary

[PROOF.md](PROOF.md) derives the implemented control and signed endpoint.
With `L=2*r*width`, the consumer's read/write/unit-move and finite-gate tariff
is at most

```text
256 * (L + ell + width + 1).
```

This includes encoded initialization, header control, split, signed output,
rewinds and cleanup. The six owned tapes allocate
`3L + width + 2ell + 20` finite-alphabet cells. The joined producer and
consumer use **34 fixed tape roles**. Shared header and descriptor storage
are counted once, and producer operations are snapshotted before adding
consumer increments, so shared-tape work is not double-counted.

The inherited producer has its separate `O(p^3)` source-band bound. The join
therefore costs `O(r*width+p^3)`, and fits the retained eventual `O(rp)`
allowance under `width=O(p)` and the stated superpolynomial lower bound on
`r`. This supplies neither an explicit cutoff nor a full caller invoice.

## Evidence

The first joined example uses `ell=8, K=4, h=5`, twelve alternating long/short
axes, `r=256`, and ten-bit signed components. Setting axis zero's branch
and five lower bits produces forward residue 264 and opposite residue 248.
The source's canonical address example produces 424 and 88. These integers
belong to the independent verification oracle; they do not control the
consumer. Each opposite producer consumes the preceding actual output
packet in the round-trip check.

The retained receipt checks 56 complete all-residue packet cases, eight
signed-word cases, 83 actual marked-countdown cases including wide padding,
and four direct producer joins with opposite round trips. It checks each
invoice role against actual tape operation counters, borrowed data/heads,
private erasure, shared storage and the tariff bound. Eight controls cover
signs, segment order, uncharged physical movement, frozen-source drift,
invalid header symbols and owned-role aliasing. Invalid-symbol controls
claim detection only, not arbitrary malformed-input cleanup.

The four joined examples allocate 21,537 cells each. Their measured tariffs
are 1,520,455; 1,510,337; 1,511,184; and 1,501,066 actions/gates, respectively.
These are simulator counts in the declared mathematical cost model, not
CPU timings or an end-to-end speedup.

Review corrected two prepublication issues: host-sized initialization loops
were replaced by encoded scans, and borrowed/private role aliases are now
rejected before tape mutation. Neither issue is hidden in the retained invoice.

## Reproduction and sources

From the repository root with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-twiddle-packet-consumer
```

[VERIFY.json](VERIFY.json) registers ordinary and isolated, optimized,
warnings-as-errors runs. [RESULT.json](RESULT.json) contains exact outputs,
operation counts, source hashes and controls. [SOURCES.json](SOURCES.json)
pins three unchanged producer files and comparison provenance. Only the
frozen producer and the new consumer are executed; no external package or
network request is needed for replay.

Both registered commands passed on CPython 3.12.15/Linux. Metadata checks
passed, and the three frozen producer files separately matched their
original Git bytes.

The producer's executable admission limits `ell` to 2..32 and axes to 1..16;
its unbounded valid-shape statement is a retained written proof. The new
consumer's executable allocation also limits `ell` to 2..32, while its
written encoded-control argument is uniform in the finite shape. Neither
finite replay proves an unbounded theorem or invokes a proof kernel.

## Attribution

Nick Petalas supplied PR3593 and its preceding header/packet lineage. His
`synthetic-monomial-packets` already implements the split/sign identity and
physical signed words with host-controlled headers. This package adds the
encoded consumer and paid direct tape join; it claims no first signed
negation or new polynomial identity. Retained notices credit Philipp's
positional engine, Jose Manuel's signed packing and PR2298, Douglas Colkitt,
and the underlying synthetic-transform sources. PR3590's owned address sweep
has a distinct scheduling contract and is not used here.

## Open next questions

* Connect this boundary to one actual normalized physical layer and complete
  synthetic round. Charge reservations, spectators, copying, precision,
  truncation and returns; none is discharged by this single-header result.
* Reconcile an owned physical address sweep with the encoded producer and
  consumer while retaining its complete scheduling and amortized invoice.
  The present producer borrows one independent address.

Structured first steps and blockers are in [TASK.json](TASK.json).
No supplier admission, new multiplication exponent or selected-frontier
change is claimed.
