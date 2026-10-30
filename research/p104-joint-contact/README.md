# Conditional kappa .00304153 from coupled P104 contacts

This contribution increases complete conditional kappa from **.00304117 in
[PR5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545)** to
**.00304153**, a gain of **.00000036**. Six ADD contacts change frame while
every scalar coefficient and its order remain identical. The selected record
remains .003027288235 and is not edited.

The first three contacts involve registers 297, 303 and 152; the other three
involve 198, 319 and 205. The exact source events and replacement frames are
listed in [construct.py](construct.py). Their joint local paid delta is

```text
2 H1 - 3 H2 + H3 - H4 + H5.
```

Each of the 18 local calls uses this change. The complete bill still has
**69,912 paid calls and 12,814 productive fields**, with rank-mass surplus
760 and maximum child/target ranks 72/145. Its distribution changes enough
to reduce the concave moment. All 735 independent public inputs, 743 endpoint
rows, productive targets and eight owned lifetimes are retained; peak owned
occupancy remains one.

These are **author-checked conditional results**. The claim is tested at
.0030415305, with raw crossing in
(.00304153116714, .00304153116715). The five inherited premises remain:
native all-column implementation, owned erasure, the uniform compiler,
precision and tape costs, and analytic recovery. The enormous uniform word
and complete rounded multiplier are not materialized. No independent human
or proof-kernel acceptance, merge or selected-frontier update is claimed.

Read [PROOF.md](PROOF.md), [the full receipt](RESULT.json),
[the emitted word](WORD.json.gz), [the complete pricing code](pricing.py)
and [the source pins](SOURCES.json). No global optimum is claimed.

## Replay and source closure

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-joint-contact --check-only
python3.12 -B scripts/research_package.py --package research/p104-joint-contact
```

[VERIFY.json](VERIFY.json) registers normal and optimized execution of the
same complete verifier, with a 540-second bound per command, plus two
30-second independent funding checks and two 30-second dense native checks.
The verifier
authenticates the retained predecessor, reconstructs the literal replacement,
checks the complete scalar and signed native endpoints, checks the physical
caller and full invoices, and evaluates both rational moment engines,
compiler/stock conditions and all outer predicates. The receipt and
[VALIDATION.md](VALIDATION.md) distinguish the checks actually executed from
the inherited premises. Metadata validation alone is not scientific replay.

The separately written [funding audit](funding-peer/README.md) implements
a third rational log/exp interval engine, without importing either source
moment engine. It independently recounts the complete invoice and ordinary
allowances and proves the signs at the claimed/tested savings and both raw
crossing endpoints. [funding_review.py](funding_review.py) binds that audit
to this publication's exact receipt, source capsule, pricing code and word.

The [four-map dense audit](native-peer/README.md) reuses Chris R/Clear1nsight's
credited PR5548 arithmetic interpreter to compare every complex entry in
all 512 columns of each newly introduced MOVE map. It checks absolute phase,
norm and support rank, totaling 1,048,576 entries per mode.
[native_review.py](native_review.py) binds it to the actual published word
and authenticated native sources and rejects two actual corrupted source
files before import. This covers the four new interfaces, preserving the
inherited old-map and framework premises. The conditional endpoint is unchanged.

The source is Ali Romman's PR5545 at
`18968423711fd902aaee1099979497d55603e1dc`. Its **unchanged official source
export** is retained as
[inputs/pr5545-source-closure.tar.gz](inputs/pr5545-source-closure.tar.gz).
The custom verifier checks the compressed capsule, embedded export manifest
and all 33 payload files before importing source modules. This capsule is a
dependency: its proof and embedded attribution remain unchanged, and all
source-specific notices continue to apply. Those 33 files are not newly
authored contributions. No foreign-history Git pin is used. The generic
package metadata pins canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04` and its revision-7 task card as
historical provenance. The package-local capsule participates in ordinary
package-change invalidation.

## Open next questions

Independent review should check the six source sites, their complete frame
paths and source-read intervals, then replay the arbitrary-input native
identity and both complete moment engines. This matters because the result
still depends on the inherited framework premises. No technical source
dependency is missing; independent scientific acceptance remains pending.
The structured handoff is in [TASK.json](TASK.json).

A later improvement must change a paid path or a productive target contract
and fund the entire caller. Refining the digits of this fixed crossing does
not supply a further structural gain.

## Credit

Ali Romman's [PR5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545)
supplies the starting contact word; his
[PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) supplies
the productive caller, scalar interpreters and complete pricing engine.
Gareth Davidson (@bitplane) supplied
[PR2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305), joining
David Arias's (@DavidAriasC)
[PR2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152) coalesced
word and Cinna Davis's (@1337isnot1337)
[PR2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219) private
reuse. The general common-chart two-operand transport identity is inherited;
the contribution here is this coupled source-pinned itinerary and its
complete conditional cost gain.

Retain Jacob Alan Sussman's productive recursion, Cinna Davis's controller,
zxv's compiler and outer machinery, Cao Yifan's pricing lineage, and every
geometry, scalar, native, COPY, precision and analytic author named in the
retained source proofs and notices. Prepared for thu-nmrc with substantial
OpenAI Codex assistance, including parallel subagents. These are author-side
checks. New work is Apache-2.0.
