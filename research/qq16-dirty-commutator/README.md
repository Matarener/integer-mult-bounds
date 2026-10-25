# A priced dirty-ancilla replacement of the rectangular QQ16 correction

An explicit reversible repair replaces PR3985's112 additional owned full-cover
temporaries with **nine mutable borrowed banks**, supplied in F16 with arbitrary
content and returned exactly. All224 current X/Y input fields remain frozen;
all224 original recovery outputs still finish in F17. No borrowed bank is cleared.

It fails the intended cost screen. Keeping all104 query-source W fields in F17
throughout the rectangular block costs **976 H1**, not224. The before/after
response cancels arbitrary query and scratch dirt, but computing and uncomputing
the query pays832 lines; responses pay32, and the unchanged decoder pays112.
Against PR3976's explicitly conditional553-H1 native-only allowance, this exact
strategy exceeds the cap by423. No universal dirty-ancilla lower bound follows.

One bounded pivot temporarily aligns the104 owned query outputs until the query
has been uncomputed. It costs352 H1 and restores all borrowed state, but the
original PR2707 decoder already costs336 H1 with no additional D temporaries.
The pivot is therefore not presented as a new improved decoder. The result is a
source-pinned stopping decision for this attempted ownership repair.

| Complete word | H1 | Wrappers | Cover maps | Unit ADD | Quarter ADD | CLEAR | Scalar allowance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Canonical PR2707 |336|672|464|1808|896|312|25840|
| PR3985 owned rectangular copy |224|448|352|1920|896|536|27184|
| Fixed-query-frame dirty repair |976|1952|1104|3488|992|296|40400|
| Aligned-query dirty pivot |352|704|480|2240|992|296|30416|

The dirty words have zero extra owned D arrays and nine extra borrowed full-cover
banks; the unchanged owner-private peak is16. Those banks are a required local
interface, not storage proven available in the actual caller. Maps/wrappers are
not free physical operations. Precision, dirty ranges, hosting, access, movement,
actual outer consumption and productive-family coverage remain open.

[PROOF.md](PROOF.md) states the ordered commutator identities and complete scope.
RESULT records both invoices, a concrete dirty-baseline witness, failure controls
and source pins. WORDS freezes both complete programs. No new kappa, second centre
credit, or globally admitted consumer is claimed. The actual global provider
still names gauge44.

## Reproduce

Python3.12 standard library:

```
python3 -I -Werror -B research/qq16-dirty-commutator/verify.py
python3 -I -O -Werror -B research/qq16-dirty-commutator/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-dirty-commutator
```

Default replay authenticates source bytes before inherited execution and compares
both complete words and the typed receipt. It checks arbitrary original and
current routed inputs, independent dirt in all nine borrowed banks, full73-coordinate
phase frames and every borrowed return. Six semantic controls reject broken
dirt cancellation, return, map payload, sign or ownership. Signed kernel basis
checks cover112 ports with both signs (114688 columns); each976/352 occurrence
is bound to one such recipe, not described as a new independent kernel proof.
Boundary tests cover source/manifest/data/word/receipt mutation, generation
refusal, and normal/optimized Git-free read-only exports.

## Open next questions

Reopen only if an actual typed replacement deletes some of the paid native
compute/uncompute paths or supplies genuinely dead owned workspace with a
restoration proof. First name those events and compare against both PR2707 and
PR3985; a reduction relative to the expensive dirty construction alone is not
an improved known decoder. Physical availability and a full caller bill must
precede another parameter or precision round. A separate parallel output-aliasing
construction is outside this package and is not a dependency.

## Workflow and credit

Explicit user-assigned reversible-computation lane, original
`joint-query-controller` card, priority6, canonical base20ecf2891d80b5acf18d980b2164fb44ea7faa90.
Main remained unchanged at round entry and the pre-pivot checkpoint.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/pull/3985#issuecomment-6263114494).
Targeted live dirty/commutator overlap and shared Discussion review have partial
coverage. Adjacent3374 prices widths;3422 records a dirty fault magnitude;
3985 supplies the rectangular cut. They do not price this restored borrowed-bank
substitution. No exhaustive novelty claim is made.

Credit ywz65 PR2707, Arham Tahir PR2681, Ali Romman and the retained QQ16/native/
geometry/supplier lineage, PR3985's owned-copy construction and PR3976's conditional
cap. Reversible compute/uncompute and dirty-baseline compensation are standard
linear-algebra techniques; the new result is this literal source-bound realization
and bounded failure decision. New work Chris R / Clear1nsight with substantial
OpenAI Codex assistance, Apache-2.0. Independent AI review is not human or formal
verification. Exact reuse is recorded in PREDECESSORS and SOURCES.
