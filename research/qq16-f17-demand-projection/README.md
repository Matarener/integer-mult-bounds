# A real F17 demand: 112-child projection and a conditional budget obstruction

PR2512's published consumer demands 96 ordinary `y1_U` arrays in `F_U1=F17`.
Projecting PR2707's zero-retention inverse onto this demand removes real work:
**336 -> 112 rank-one children**, **464 -> 208 cover maps**, **672 -> 224 native
wrappers**, and **25,840 -> 9,376 scalar primitive allowance**. The complete
1,410-event word reads all 112 current Y fields, no X fields or early records;
it returns 96 owned outputs, clears sixteen full-cover temporaries and eight
owner-private scratch fields, and leaves all borrowed fields untouched.

This changed demand **escapes PR3908's rank-eight-waived obstruction**. It does
not yield an admitted supplier. Retaining the reported eight H8 profile charges
still gives a favorable moment in **[1.000023149708, 1.000023150305]**, above one
at the selected saving even with physical overhead free. The waived profile
instead lies in **[0.999995759681, 0.999995760274]**, leaving only about
0.00000424 normalized allowance. The fixed-eight profile requires at least
51 fewer decoder H1 calls per pair just to pass the optimistic integer screen.

[PROOF.md](PROOF.md) gives the operator identity, exact input/frame/ownership
contract, complete counts, rational bounds and limits. This is one source-bound
local endpoint and a conditional fixed-profile exclusion, not a shortest word,
whole-controller result, physical six-tape admission, net storage saving or new
kappa. The full 224-output decoder and its obstruction remain valid for their
original contract. PR2512's input contract differs: its eight retained T arrays
are replaced by sixteen additional selected current Y reads here.

## Reproduce

Standard library, CPython 3.12; from repository root:

```sh
python3 -I -Werror -B research/qq16-f17-demand-projection/verify.py
python3 -I -O -Werror -B research/qq16-f17-demand-projection/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-f17-demand-projection
```

`verify.py` checks the complete committed word and receipt without writing.
Expected marker: `PASS_QQ16_F17_DEMAND_PROJECTION no_new_kappa`. Its replay uses
explicitly adapted, source-authenticated predecessor operator primitives;
it is not a code-disjoint reimplementation of all inherited algebra.
Evidence includes independent x1/y1 B1 symbols, 4,992 demanded routed terms,
full 73-coordinate phases, 57,344 native basis columns, nine semantic mutants,
the complete local invoice and both sides of the budget thresholds. Seven
boundary test groups include a read-only Git-free export, pre-execution source
failure and complete word/typed receipt rejection. See VERIFICATION.json for
actual commands and publication checks. No huge payload, selected cold replay,
Lean/formal-kernel check or independent human review is claimed.

## Scope and workflow

Explicit assigned continuation of #3946/#3908; no task reroll. Canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6; exact inputs and
original task card in SOURCES.json/TASK.json. Only this scoped package is added.
Frozen sources and selected frontier are unchanged. The [advance claim and
canonical update](https://github.com/CrocSwap/integer-mult-bounds/pull/3946#issuecomment-6260950964)
records the stop rule. Live targeted PR searches and the overlap helper found
the named adjacent packages; the helper lacks gh, so remote coverage is partial,
not a novelty guarantee. PREDECESSORS.json retains exact heads and code reuse.

## Open next questions

The next useful audit is **the eight reported rank-eight centre copies under
this actual reduced demand**. Bind their literal source/destination/frame and
last uses to one real continuation; decide whether they can legally retire (at least fourteen of sixteen pair H8 charges must disappear with this 112-H1 word under unchanged centre 64),
and recompute coverage and physical costs. If they remain, this word is
excluded in the fixed model and needs at least 51 genuinely removed H1 pair
charges before further implementation is warranted. A hypothetical free centre
or arbitrary waiver is not that audit. Structured questions, first steps and
blockers are in TASK.json; the full stopping rule is in PROOF.md section 6.

## Credit

Chris R / Clear1nsight, with substantial OpenAI assistance in source inspection,
derivation, implementation, verification and writing. Apache-2.0.

Credit ywz65's #2512/#2492/#2468 for the actual demand, L2 native maps and read
machinery; thakrarsagar/#2470 for L2; Arham Tahir/#2681 for the complete logical
inverse and routed/phase primitives; ywz65/#2707 for the line-normalized physical
word; 1337isnot1337/#3908 for the budget obstruction; dcharb78/#3181 for its
profile premise; Clear1nsight/#3946 for the independent budget arithmetic;
Ali Romman/#1969, starship-s, Ross Richardson and retained QQ16/native lineage;
Douglas Colkitt, Sagar Thakrar and coverage-ceiling contributors. Source notices
remain intact. The new result is the demanded projection, its complete local
invoice and the changed budget conclusion, not those predecessor identities.
