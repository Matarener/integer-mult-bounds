# Dirty-buffer XOR endpoint corrections

This package supplies an explicit space–time tradeoff for the residual XOR
corrections in Gonzalo Mier's PR3480, following Cinna Davis's PR2297. It
extends Dugongue's PR3879 with a faster **in-place** route that borrows a
larger dirty buffer and restores every borrowed bit.

For N = 2^h equal B-bit records and scratch capacity R = 2^r records,
the literal two-tape machine has the exact time

\[
 N(B+2)\sum_{k:\,δ_k=1}(5+2^{\max(k-r,0)}).
\]

With at most N/2 dirty scratch records this becomes
6N wt(δ)(B+2) ≤ 6Nh(B+2). No zero-initialized buffer, random access,
arithmetic register or uncharged online permutation is used. Both heads,
scratch, framing and arbitrary exterior contents are restored. The data
itself is permuted in place. The control is compiled for (h,δ,r), works for
every B ≥ 0 and has an explicitly charged finite state/table size.

For the 23 literal PR3480 masks at N = 512, sums of isolated costs are:

| Dirty scratch capacity, records | New exact sum of unit transitions |
|---:|---:|
| 1 | 3,267,584 B + 6,535,168 |
| 2 | 1,763,328 B + 3,526,656 |
| 4 | 1,014,784 B + 2,029,568 |
| 16 | 459,776 B + 919,552 |
| 64 | 330,752 B + 661,504 |
| 256 | 307,200 B + 614,400 |

PR3879's different one-dirty-record in-place schedule costs
2,033,554 B + 4,049,444 on those masks. Thus the new 256-record alternative
reduces that invoice by a factor greater than six for every B ≥ 0,
while borrowing more dirty space. The new one-record schedule is slower
than that predecessor; this is a useful tradeoff, not equal-space dominance.
PR3879's separate copy variant remains faster and needs a full owned
destination; the present theorem instead restores its borrowed buffer.

The universal proof in PROOF.md derives the complete table semantics, the
three-exchange dirty restoration, the stage travel telescope, exact control
size and all-size endpoint/frame properties. Finite evidence in RESULT.json
covers 986 parameter cases, 436 complete joint data/dirt states, all 23
literal production masks at B = 9 with 512 distinct payload labels, and
5,259,144 executed transitions.
test_machine.py includes actual missing-exchange, malformed-width, endpoint,
head, footprint, halt, export/source and frozen-invoice controls; these run
normally and with Python assertions disabled.

Reproduce with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/dirty-buffer-xor
```

For an extracted package outside Git, run `verify.py`, `test_machine.py`,
and `python3.12 -O -B test_machine.py` in this directory. Vendored inputs
are unmodified, authenticated public source files; no foreign Git history,
network fetch or private MathProof installation is needed for replay.

This is a complete informal machine result, with finite author checks.
It is not a fresh Lean/kernel certificate or independent human review.
Native owner/layout/encoding, scratch acquisition/lifetime, production
caller composition and the complete recursive invoice remain open.
There is no new κ, selected-frontier change, or claim of a universal
runtime improvement for the multiplication algorithm.

## Open next questions

1. Which native P112 endpoint exposes the contiguous record bank and a
   returnable dirty prefix? Freeze the actual owner and address map, then
   compare every record with this ABI. This would make the sufficient
   standalone construction callable; the map is currently missing.
2. Which point on the space–time tradeoff wins in a complete caller?
   Charge buffer acquisition, lifetime, representation and all movement,
   alongside PR3879's copy and low-space variants. The standalone numbers
   do not determine native rank tariffs or available storage.
3. Can a single fixed-control interpreter handle unbounded online h at an
   affordable cost? Preserve the present explicit table-size charge and
   supply actual counter/stack traversal if attempting that extension.
   A uniform compiler is not such an online interpreter.

Prepared by Dugongue with substantial OpenAI Codex assistance. NOTICE.md
and LIBRARY-BRIDGES.md retain the relevant predecessor and shared-library
credit. Classical chunk swapping and XOR bit decomposition are established
techniques; no first-ever use or exhaustive novelty claim is made.
