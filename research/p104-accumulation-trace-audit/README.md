# All three P104 destination sums: trace and invoice audit

This package independently checks all three new destination sums in [PR5802](https://github.com/CrocSwap/integer-mult-bounds/pull/5802) against [PR5786](https://github.com/CrocSwap/integer-mult-bounds/pull/5786). It uses the retained words and receipts, with no source constructor or source checker imports. This is a finite audit under a stated native frame premise. It does not admit a supplier or claim a new kappa.

## Evidence

The verifier matches all 22,516 original scalar events. It checks 22,462 source observations and all 23 COPY values at their actual times. The three new sums use destinations 146, 173 and 151. Sources may change between reads. Each sum has one owned query, a unit delivery and a final CLEAR. No pending destination is read or changed before delivery.

It checks the exact formal endpoint on all 795 old and 798 new columns, with arbitrary public and dirty inputs. It also recounts frames, native query ranks, helper targets, scalar charges and owned lifetimes. The fixed p16/a7 caller contract gives 66,906 versus 66,870 paid calls, 13,444 targets in both words, and rank surplus 760 in both. Helper target changes are included. The local scalar allowance rises from 224,990 to 225,026 and the route allowance rises from 5,313,000 to 5,323,000.

[PROOF.md](PROOF.md) gives the trace invariant and the conditional frame lift. It proves a strict improvement of the signed recursive invoice for every exponent between zero and one. [RESULT.json](RESULT.json) records the exact counts. Tests include 200 separate dense matrix oracle pairs and 13 semantic rejection controls. An early read followed by a cancellation preserves the final matrix but fails the trace check.

## Reproduce

```sh
python3.12 -I -B -W error research/p104-accumulation-trace-audit/verify.py
python3.12 scripts/research_package.py --package research/p104-accumulation-trace-audit
```

The direct verifier also runs from a read-only source export, with no Git or PATH tools, under `-O`. It checks input hashes before and after the audit. Its checks do not use Python assertions. `--record` is an explicit receipt-generation command; normal replay cannot replace the receipt.

[SOURCES.json](SOURCES.json) pins the exact source commits, blobs and bytes. The retained source notices give the construction credits. The selected record and task card are historical provenance. Full ancestry was not checked in the shallow checkout. Exact source blobs, committed package bytes and a sealed source export were checked.

## Limits

MOVE is decoded as identity under the premise that its native map is `U_b U_a^-1`. The audit checks frame incidence, proper nesting, direction and rank. It does not check native phase/kernel implementation, physical caller action, compiler, precision tape or outer analytic recovery. The caller receipt is identical across the two pinned sources; the recursive invoice is recounted from that fixed controller contract. The five framework assumptions remain. The two source endpoint hashes are checked against PLAN; intermediate PLAN products are not reconstructed. This package does not certify the source kappa decimals or establish human review.

## Open next questions

Audit the changed native maps and their all-size law against the frame premise. Then test compatibility with the disjoint block changes in PR5795 after coordination with their authors. The exact scope and blockers are in [TASK.json](TASK.json).

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance. The source construction and prior work are credited in the retained `before-NOTICE` and `after-NOTICE` files. New audit code and prose are Apache-2.0. No source construction credit is claimed.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
