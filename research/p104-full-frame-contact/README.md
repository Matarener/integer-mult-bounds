# Conditional kappa .00304117 from one P104 contact

This contribution increases complete conditional kappa from **.00304057 in
[PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544)** to
**.00304117**, a gain of **.00000060**. It changes the recursive paid profile.
The selected record remains .003027288235 and is not edited.

The change moves the subtraction on registers 341 and 345, and its sign,
from a four-dimensional frame to the full nine-dimensional frame. It replaces
H1 + H5 by H6 in each of 18 local calls. All scalar coefficients, public
boundaries, independent outputs and owned lifetimes remain unchanged.
The full bill has **69,912 paid calls and 12,814 productive fields**.

Read [the proof](PROOF.md), [the five-site constructor](construct.py),
[the full receipt](RESULT.json), [the emitted word](WORD.json.gz), and
[the exact source pins](SOURCES.json). The raw crossing and remaining headroom
are recorded in the receipt. No global optimum is claimed.

This is a focused successor to the released PR5544 at
`e2a6cce2f9db5a2c5f9714f4b9e5292dd3a10581`. Its original commit remains the
parent. The predecessor package is unchanged and is required for replay.
The research started at canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.

## Replay and evidence

Python 3.12 and the standard library suffice:

```sh
python3 -B scripts/research_package.py --package research/p104-full-frame-contact
```

The scientific marker is `PASS_P104_CONTACT_COMPLETE_KAPPA_00304117`.
The normal and optimized commands reconstruct the source, apply the literal
change, check all 552,049 public/owned coefficients by two interpreters, check
all native maps and target phases, replay the complete physical caller and
compute both full histograms. Two rational moment engines, all compiler and
stock bounds, and all 54 strict plus four functional outer predicates run.
Controls reject a one-sided move, wrong sign, undeclared source read and
omitted cost. Saved compressed words are compared by decompressed JSON.

[VALIDATION.md](VALIDATION.md) records the checks actually run and their limits.
The standard signed-invoice preflight is also recorded there. The first
search was a bounded common-contact descent on the exact source; the final
constructor contains only the one verified replacement, not that search.

The five native all-column, owned-erasure, compiler, precision/tape and
analytic-recovery assumptions of PR5544 remain. The enormous uniform word and
complete rounded multiplier are not materialized. No independent human or
proof-kernel acceptance is claimed. The source libraries are inherited,
although their candidate checks run again.

## Open next questions

Independent review should check the five edited sites, source-read intervals,
all-width chart identity and complete cost join. Start with the literal
constructor and the before/after invoices. Human or proof-kernel acceptance
is still absent. A later cost improvement must change a paid path or target
contract and pass the same full checks; more digits of this crossing are not
another structural gain. See [TASK.json](TASK.json) for the structured handoff.

## Credit

Ali Romman's [PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544)
supplies the productive caller, two scalar interpreters and full price engine.
Gareth Davidson (@bitplane) supplied
[PR2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305), which joins
David Arias's (@DavidAriasC)
[PR2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152) coalesced word
and Cinna Davis's (@1337isnot1337)
[PR2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219) private reuse.
The retained [shared-chart retiming](../p104-shared-chart-retiming/README.md)
and [dual-ADD retiming](../p104-dual-add-retiming/README.md) already give the
two-operand transport method. This package claims the new source contact and
its complete conditional endpoint, not that general identity.

Retain Jacob Alan Sussman, Cinna Davis, zxv, Cao Yifan and all geometry,
scalar, native, COPY, compiler, precision and analytic authors in the
[predecessor proof](../p104-productive-controller/PROOF.md) and
[native notices](../p104-native-channel/notices).
Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
New work is Apache-2.0.
