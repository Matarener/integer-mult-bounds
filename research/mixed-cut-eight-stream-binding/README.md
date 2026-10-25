# The half-cut heads pass the source-bound eight-stream seam

This answers the bounded replay request in Jacob Sussman's PR #4268,
Open question 2, on Marius-Paul Dumitrean's **unchanged PR #2979 T74 fill**.
It adds a source-bound chronology check, four complete matrix fixtures,
a rejecting wrong-location control, and the precise first-touch lemma.
It supplies no new rate, supplier admission or kappa.

## Established result

The new loader authenticates the actual 271,728 fill rows, 666 call positions,
74 replicas, provider widths, dispatch and 112 port recipes. The retained
`PLAN.T = 37` is historical metadata; it is not used as the replica count.
The unrelated PR3148/T740 loader is never called. Every hosted occurrence
affecting each projected owner/port is retained, including foreign callers.

On all owner/port keys, a structural first-touch check counts:

| Child | Replicas 0–36 | Replicas 37–73 | Total heads |
|---|---:|---:|---:|
| 8, physical X3 | 4,032 | 4,032 | 8,064 |
| 10, physical Y3 | 4,011 | 4,011 | 8,022 |

The other 12,104 rank-48 blocks, in children 12 and 13, are non-heads.
The classification is freshly regenerated, with its complete ordered-list
digest in `EXPECTED-ENGINE.json`. This is an actual eight-stream chronology
classification; the predecessor's own lowering/network is not imported.

For the four named fixtures `(owner, port, child)` = `(0,0,8)`, `(37,0,8)`,
`(0,0,10)`, `(37,0,10)`, delete the first 24 actual unhosted axes, preserving
every remaining axis, translation, helper phase and later event. All four
pass on 79 specified characters and **all eight arbitrary input columns**.
Each fixture retains all 29 hosted occurrences, including 26 foreign callers.

The target relation is

```text
M_cut(chi) = M_original(chi) C(chi)^(-1),
C(chi) = phase on the cut INPUT stream by i^(sum_{v in removed} dot(chi,v)).
```

The exponent is an integer sum modulo four, not an XOR parity. The baseline
full-job operator is checked first. [PROOF.md](PROOF.md) proves the relation
for every character when the literal first-touch guard is established in
this completed-invocation, identity-cover model. The structural check covers
all named keys; the four numerical fixtures are regression evidence, not
an assertion of exact symmetry or enumeration of all `2^73` characters.

A wrong half-cut on `(owner=0, port=0, child=12)` is rejected at
`chi = 2^25 = 33554432`; complete actual and required matrices are retained.
This shows that equal rank deletion at an arbitrary location is insufficient.
Because the baseline is scalar at this cover, left versus right correction
alone cannot be distinguished by these literal baseline samples. The side
follows from the written lemma; a separate embedded shear example rejects
the wrong side and a write-only first-touch guard.

## Independent checks and reproduction

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-cut-eight-stream-binding
```

The registered normal and optimized commands both use `-I -W error -B`.
They authenticate all 19 declared inputs, freshly classify and replay, and
compare every typed field against the committed complete generated data.
Three controls reject an altered dirty-input entry, a missing cut axis and
an integer substituted for Boolean acceptance.

The primary engine reuses Nick Petalas's unmodified Gaussian-integer row
operations. `oracle.py` separately constructs and multiplies explicit dense
operation matrices: all 344 complete matrices, 22,016 entries and 113 active
phase cases agree, including the non-head mismatch. **Source event extraction
is shared** and separately reviewed; this is not two independent allocation
reconstructions. The stored data include exact axes, chronology, hosted rows,
primitive events and all tested actual/required columns.

`SOURCES.json` binds immutable inputs; `source/` retains the original PR4268
question, proof, classifier, instance and notice unchanged. Original Git
commit/tree authentication and clean-export/hosted receipts accompany the
public handoff. Merely running this direct script does not check Git ancestry.

## Limits

The conclusion is at **identity cover**, under the retained completed-local-
invocation contract. Bank padding and the zero all-family correction are
outside the projected matrix. Native helper internals, all other covers,
finite precision, routing, storage, restoration, stock, mixed recursion and
the multiplication outer theorem are not admitted. The source axis geometry
and completed-call interpretation remain inherited premises for interpreting
the phase deletion as a smaller 49-axis job. Gram orthonormality is not
independently recertified here; the phase identity itself does not require it.
Independent human and proof-kernel acceptance are unclaimed.

## Open next questions

1. Bind a specific nonidentity cover or actual native invocation to the same
   cut. This can decide the next physical seam; first specify its literal
   producer/consumer and full invoice. The current model does not provide it.
2. State the integer-multiplication outer theorem's exact mixed-job supplier
   hypotheses and complete precision/stock/restoration budget. This is needed
   before any kappa implication; no root-digit or packing search closes it.

Stop further construction without that named boundary or budget. The later
PR4268 comments report external A-fc Lean work; this package does not repeat
the stale Lean question or independently validate that external receipt.

## Credit

Jacob Sussman/PR4268 proposed the lever, mixed-target recursion and replay
request. Marius-Paul Dumitrean/PR2979 supplied the unchanged allocation and
words. Nick Petalas/PR3187 supplied the exact eight-stream algebra, following
Gareth Davidson/PR1387 and Rohan Arun's physical-stream objection. Gonzalo-Mier,
Guéorgui Maissouradze, Jeremy Kothe, Jeremy Diviney, Mason Hale, Yiyang Lu,
Cinna Davis/1337isnot1337, Tekalign, icekylinx and the full retained E8/native/
owner lineage retain their credit; see the unchanged source notice and
PR2979 `NOTICE`/`CREDITS.md`. New source binding, structural application,
dense arithmetic, checks and integration are by ToikY with substantial
OpenAI Codex assistance and separate AI contexts. Apache-2.0.
