# Encoded twiddle diagonal on a full positioned cube

This package executes one complete fixed-round synthetic-twiddle diagonal
on an already-positioned full cube. An encoded odometer visits every physical
record address, the unchanged PR3593 controller produces its actual header,
and the unchanged PR3611 signed consumer processes the corresponding actual
packet. The same physical tapes are rearmed and reused throughout.

For $N=2^A$ records and $r=2^\ell$ coefficients per record, the endpoint is
$f_j\mapsto y^{E_j}f_j\pmod{y^r+1}$ at every original physical record
position. The source is preserved, the complete output is retained, all
heads return, and working tapes are erased. Signed components must admit
each negation actually requested. The proof assumes valid matching input
extents and separate backing storage; failure recovery is not claimed.

## Source boundary and implementation

The first physical named address slot is most significant. This follows
from `upstream/build/sections/02-streams.tex:17–23` and the actual layout
permutation in `06-transforms.tex:236–274`. There is no extra uncharged
record permutation. The mandatory source example has $\ell=6$, $K=2$,
one long and one short axis, $h=4$, $A=11$, and all 2048 records.

The full source format is `@` followed by consecutive `^bits$` packets,
then `!`. Each packet contains increasing polynomial coefficients, real
then imaginary components, in signed MSB-first width-$w$ words.
`DiagonalPass(producer_module, consumer_module, descriptor_text, width,
source_cells).run()` returns the owned full-output tape. Host shape fields
admit storage; descriptor scans, tape symbols and binary carry control
execution. There is no published per-record callback or materialized
address/header list.

The 38 distinct tape roles include both full streams. With $B=2rw$ and
the unchanged producer's capacity $C_{\rm producer}$, the exact capacity is

$$C_{\rm producer}+2N(B+2)+4B+2w+A+3\ell+32.$$

Excluding the retained full input/output, auxiliary storage is $O(rw+p)$.
Read/write/move counts and explicit control/data gates are recorded
separately; their combined invoice includes constructor counter setup,
same-tape rearming, packet copies, clearing and full-stream head returns.
It is a physical-action tariff, not a Python timing or byte-memory claim.

The written proof gives $O(N(rw+A+p^3))$ work. Under the retained source
bands $A=O(p)$, $w=O(p)$ and superpolynomial growth of $r$ in $p$, this is
eventually $O(Nrp)$, without an explicit cutoff. See [PROOF.md](PROOF.md)
for the exact premises, enumeration invariant and stock derivation.

## Verification

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-twiddle-diagonal-pass
```

Use the registered commands in [VERIFY.json](VERIFY.json) with the declared
environment and frozen source inputs. [RESULT.json](RESULT.json) records
the finite replay evidence. The executable inherits $2\leq\ell\leq32$
and at most 16 axes; practical full-cube fixtures do not exhaust these
bounds or prove the unbounded mathematical family.

The independent replay checks six complete cubes, totaling 2,140 packet
applications, including an actual forward/opposite stream round trip. The
requested 2,048-record mixed-axis case uses width four and diverse signed
data: 38 physical tapes, 2,108,012 cells in total and 2,664 auxiliary cells,
with an exact recorded tariff of 345,267,202. It checks every address,
actual header/packet pairing and complete signed output against a separate
coordinate-exponent and coefficient-destination oracle.

Six mutations reject a missing address flip, missing counter rearm,
unrearmed consumer, uncleared header, premature wrap and an uncharged move.
Instrumentation independently reconciles physical operations by tape
identity, including constructor actions; shared tapes are counted once.
All heads return, borrowed bytes are unchanged, private cells are blank,
and replacement tape allocation during execution is forbidden by the checker.

Validation on 2026-10-18 used CPython 3.12.15 on Linux. Normal full evidence
generation and the registered `-I -O -B -Werror` replay passed. The four
frozen source exports also match their pinned original Git bytes.
After an EOF-whitespace cleanup, the adapter's parsed syntax tree was
unchanged and the small cases/control outcomes matched again; only the
source-mutation hashes were refreshed.

The transform text supplies the exponent and signed-rotation identities;
the synthetic-twiddle circuit package supplies the named-slot interpretation.
Nick Petalas's [PR #3593](https://github.com/CrocSwap/integer-mult-bounds/pull/3593)
supplies encoded header production and
[PR #3611](https://github.com/CrocSwap/integer-mult-bounds/pull/3611) supplies
the physical signed packet consumer. The specified mixed-axis caller follows
the handoff in [PR #3590](https://github.com/CrocSwap/integer-mult-bounds/pull/3590).
This package contributes the complete
fixed-round stream join and reuse argument. Source manifests preserve the
predecessor attribution. It does not implement a complete transform,
truncated layer or multiplication theorem, and changes no selected frontier.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, including
separate implementation, proof and exact-verification agents. Their
same-session reviews are not independent human acceptance or formal proof.
The new code is Apache-2.0; unchanged source files retain their notices.

Canonical coordination: [Discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19015185).

## Open next questions

Join this pass to an actual butterfly round, including its paid packet
movement and formats. Extend that joined implementation to truncated
domains and spectators before claiming a complete layer or root invoice.
