# Selected coupled Pauli feedback: linear adapters with a uniform cost limit

**Scoped positive construction and lower bound; no new κ.** A reversible
feedback network implements the selected boundary `(x,y)→(C_f x+B_f y/2,y)`
with one rank2f native call and one arbitrary dirty helper, restored exactly.
It replaces #3989's exponential read-only transfer expansion with O(f)
adapter passes. A matching Ω(f) support/uncertainty argument rules out a
uniform saving under the stated full-array arithmetic charge model.

The explicit rational schedule uses **26f+1 array ADDs,12f signed-P maps and
24f unit-phase maps**, one V-sized child operand, and3V live payload including
the borrowed V-sized helper. Every coefficient has denominator at most2.
No additional recursive call is hidden in the network. Routing, precision,
helper hosting and common-frame compiler admission remain unproved, not free.

[PROOF.md](PROOF.md) gives the source boundary, all-f elementary-matrix
factorization, complete pass ledger, uncertainty proof and uniform budget
screen. [RESULT.json](RESULT.json) records exact replay results. The primary
field is Clifford/Pauli circuit algebra; the contrasting tools are elementary
matrices/reversible linear networks and discrete uncertainty.

## Reproduce

```sh
python3 scripts/research_package.py --package research/selected-coupled-pauli-feedback --check-only
python3 scripts/research_package.py --package research/selected-coupled-pauli-feedback
```

Only Python standard library is needed. The bounded command checks1536 literal
three-register basis inputs,128 source orbit charts,252 reduced tensor basis
inputs, a formal ring identity, operation counts and four negative controls.
All-f conclusions follow from the written proof; finite checks are controls.
Declared source bytes, Git blobs and provenance are in [SOURCES.json](SOURCES.json).
The pending predecessor PR is not a runtime dependency. This package changes
no inherited/frozen inputs, selected result, moment engine or supplier.

## Boundary and research decision

The literal candidate is forward phase-B register195, events12806 and13402,
frames0→2→252, with event12807 adding half of donor521. This network is a
physical coupled operator identity, not a new inherited common-frame event
word. It keeps every source and restores both donor and arbitrary helper.
For lane volume V=512^f times spectators, the lower bound k≥f counts full-V
shears. Its arithmetic bill eventually exceeds the available recursive saving
A V [2−2^(1−α)] f^(1−α) for every fixed A>0 and selected0<α<1. No κ improvement,
global profile, cold replay or complete admitted supplier is claimed.

## Open next questions

Stop this full-array one-child construction family here. The next admissible
question is a changed sparse/variable-volume operation model with a proved
sum of processed volumes and all restoration/hosting charges, screened before
synthesis. [TASK.json](TASK.json) records that obligation and the scope change.

## Overlap and predecessor credit

Canonical main was20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision6.
The coordinating agent checked702 open PR bodies at08:35 UTC on2026-10-19;
this worker searched2492 local research records at08:41 and inspected nearby
scopes. This coverage is not all closed diffs, Discussions or private work.
No exact feedback-factorization/uncertainty result was identified in that
checked coverage. PR1974 (merged head a4992da8e4e81a74cf1fd2b2d3af948662476d6e)
uses a finite F2[GL3] shear alphabet; PR2017 (merged head
5950e7896b8825a2c167ee63836251b3096060f8) studies binary Eisenstein rectangles.
Neither is asserted to exclude this Q(i) selected coupled-boundary model.

The nearest broader precedent is Arham Tahir’s [Discussion1901](https://github.com/CrocSwap/integer-mult-bounds/discussions/1901) / [PR1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920): reciprocal basis changes for independent Clifford lanes, with arbitrary dirty padding. ToikY’s [PR1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924) treats clean invariant-subspace injection. Our independently chosen pre/post feedback networks implement the triangular donor-coupled boundary; they are not a reciprocal conjugacy, and the helper is arbitrary dirty rather than a zero complement. The constructive network and its full-array pass invoice are the scoped addition here. Both precedents inform the unchanged boundary-volume discipline.

Credit GonzaloMier's [#3975](https://github.com/CrocSwap/integer-mult-bounds/pull/3975)
for the literal candidate and endpoint warning (scientific source head
118967102329e19e2202ae38dcf37e85997a08dc; credit update
93157ab23657fb5f33751c5f858e81568caaec4b). Credit Clear1nsight/Codex
[#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989), head
7b6dda7ab6ed10d608ecba357ac2f6924166d38b, for the Pauli boundary, direct-channel
contract and primitive exact decoder adapted in exact.py. This package adds
the feedback factorization and broad one-child full-array bound; it does not
relabel the prior narrow no-go as a new result.

Retain CinnaDavis's [#1836](https://github.com/CrocSwap/integer-mult-bounds/pull/1836),
AdamGall's `complex-heterogeneous-child-interface`, the selected #1094 lineage
and its #1920/#679 provenance for the complex child/scalar interface, selected
native source and accounting context. Source archive credit and licenses
remain intact. Prepared by Clear1nsight with substantial OpenAI Codex assistance,
including an independent algebra reviewer. New package text and code Apache-2.0.
