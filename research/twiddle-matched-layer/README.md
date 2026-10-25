# Matched twiddle layout for the actual-width normalised layer

**A source-relative interface repair and conditional complete-round theorem.**
This package joins the actual outer layout to the newer root's selected width,
proves its record-size and signed-packet admission, and states the remaining
paid layer lifecycle. A separate addendum incorporates the subsequently
published PR3617 full diagonal pass. The physical root, all-round reuse,
complete caller invoice, and a faster multiplier remain unestablished.

The investigation is complementary to
[Sagar Thakrar's completed fixed-h diagonal-pass handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19015185).
It reuses his unchanged implementation. Its sources include the actual
[PR3493 outer wrapper](https://github.com/CrocSwap/integer-mult-bounds/pull/3493),
[PR3599 actual-width root](https://github.com/CrocSwap/integer-mult-bounds/pull/3599),
[PR3593 header producer](https://github.com/CrocSwap/integer-mult-bounds/pull/3593),
and [PR3611 packet consumer](https://github.com/CrocSwap/integer-mult-bounds/pull/3611).
All four are pinned at exact heads, with original bytes and credit retained.

## Exact mismatch and repair

In the retained outer construction, d=floor(p^(1/40)) and common rounds select
g=d-1 axes. The original layout chooses K=floor(d^(1/500)), while PR3599's
actual-width plan chooses K=floor(g^(1/500)). The integers disagree exactly
when d=k^500 for an integer k>=2. This changes both the root's complete array
extent and its selected physical bits. Increasing a left extent to conceal
the cardinality mismatch does not fix the wrong tensor action.

[PROOF.md](PROOF.md) supplies a matched layout using
K=floor((d-1)^(1/500)), with the corresponding inverse layout and complete
descriptors. Common rounds already act on consecutive K-bit chunks at one
common offset, so these calls do not require a separate general-support
router. That distinct support-router work has also advanced in PR3619; it is
not part of this join. The existing layout movement and component-order conversion remain
charged. A new active-root wrapper must still bind them to the same complete
Gaussian array. The old wrapper's dimension-exponent constructor check cannot
simply be reused for the new plan.

The floor issue survives the caller's final rounding. At a production boundary
d=k^500, g=d-1, take one real coefficient at address zero with p-grid numerator
2^g. Its value 2^(g-p) lies in the unit disk since p>=d^40>=g. In a common
chunk at residue zero, hiding the extent mismatch leaves actual selected
positions spaced k-1 bits apart. Its normalised tensor has numerator one at
address 2^(k-1), where the intended spacing-k tensor has zero. Both are already
on the p-grid, so truncation cannot hide the difference. Here the address is
within the final common chunk group, with right offset zero; a nonzero right
offset shifts both selected-position formulas. A subsequent signed
packet rotation preserves nonzeroness. This is a quantified counterexample to
the naive substitution, not an execution of an enormous production instance.

For unrestricted integer precision, the old K>=k threshold is p>=k^20000;
the matched one is p>=(k^500+1)^40. The actual caller uses precisions divisible
by six. Exact tests cover the first legal precisions at both boundaries for
k=2 and k=3. The distinction persists on that restricted domain.

## Completed rounds, precision, and cost

The proof covers all-short, mixed, all-long, and singleton axes, common chunks,
top and bottom prefix rounds, and both transform directions. It retains the
frequency bit reversal and layout endpoint maps. The inverse direction applies
the inverse diagonal before the butterfly and reverses the round order.

The actual outer bands imply the root's required long-record condition
r>=2^((log2 p)^2), with r=2^ell, and its dimension condition. Completed
normalised butterflies contract the unit disk, and truncation towards zero
preserves it. Signed coefficient permutations are exact isometries and commute
with this truncation. The packet width is therefore w=p+2 throughout the
complete-round induction, and the source's forbidden signed minimum is
unreachable. PR3611 already supplies the one-packet width observation; the new
scope is the actual layer's admission and repeated-round implication.

After R<=ell rounds, the source-relative error is less than
sqrt(2) R 2^-p. Intermediate butterfly factors are not separately truncated.
With the retained ordinary movement exponent tau=99830289/10^8 and the newer
root exponent alpha=99827101/10^8, the complete conditional bound remains

    O(T p [d K + p K^(tau-1) + ell g^alpha log p]).

Here M is the number of records, r the coefficients per record, and T=Mr.
No newer internal ordinary profile is silently substituted for the retained
outer movement theorem. The exact-K movement saving 169711/2000000000000
still controls the narrower bottleneck. This package does not improve the
selected integer exponent.

Let Q include all added address enumeration, packet framing, extraction and
assembly, descriptor updates, output consumption and clearing, tape reuse,
and head returns. A sufficient missing implementation contract is

    Q <= C M R (r w + A + p^3) + poly(p)

for a fixed constant C and A=log2(M), together with complete same-order output,
preserved borrowed data, returned heads, private cleanup, and a fixed number
of complete array buffers across rounds. The long-record band pays this term.
The proof also retains and sums the producer and consumer's written tariffs.
PR3617 now supplies the fixed-h enumeration and packet lifecycle part, under
its own matching framed-input and successful-return premises. Q is still
unknown for the whole proposed composition, including the physical root,
initial framing and layout, descriptor changes, whole-output consumption,
and reuse between rounds. The exact simultaneous tape count and production
width lifecycle remain unestablished.

## Published diagonal joined to complete arithmetic rounds

The original seventeen-file proof/check component stays frozen. At the
pre-submission checkpoint, Sagar published
[PR3617](https://github.com/CrocSwap/integer-mult-bounds/pull/3617), exact head
`4bf091f415d6470b60a5062a08b0a47e5b12dbd7`, and explicitly handed its fixed-h
pass to this complementary caller audit. [diagonal/ADDENDUM.md](diagonal/ADDENDUM.md)
records the source-bound contract and what remains open.

The addendum's checker retains all twelve predecessor package files unchanged
and executes the actual full diagonal on two small complete-cube geometries.
There are **12 positive completed forward/opposite rounds, 384 actual packet
applications, and 4,096 Gaussian coefficient comparisons**. The arithmetic
butterfly, truncation, layout, and host fixture serialization are explicitly
unpriced oracles. Each direction starts from the same initial cube; this is
not a forward/opposite full-transform round-trip claim.

Every diagonal stage preserves borrowed bytes, returns all 38 heads, blanks
private roles, and rejects runtime tape replacement. The positive fixed-pass
tariffs total **19,566,850 actions**. A separate 64-packet wrong-K pass differs
at four coefficient positions. Off-grid encoding and second-use controls
reject for their intended reasons.

The 38 roles include both complete streams. Packet buffers are reused within
each pass, but the full pass object itself is one-shot. Fresh stage instances
in the checker supply no physical all-round allocation or reuse theorem.
Thus PR3617 closes the fixed-diagonal portion of the former Q condition while
leaving the enclosing layer obligations explicit. The source's full historical
six-cube suite and a production physical root are not replayed here.

## Bounded evidence and reproduction

[check_join.py](check_join.py) reconstructs the layout independently and checks
ten complete small Gaussian cubes, giving **50 forward/opposite completed-round
comparisons**. Seven structural controls distinguish wrong extent, concealed
wrong tensor, old inverse layout, wrong offset, inverse order, floor rounding,
and insufficient signed width.

Two additional calls execute the unchanged PR3593 and PR3611 modules on a
nonzero packet returned by the repaired layout's arithmetic butterfly oracle.
At physical address 36, matched K=1 emits residues 12 and 4; interpreting the
same bits under old K=2 emits zero. The opposite packet returns exactly.
Both consumer costs independently reconcile to 9,863 counted actions, with
producer tariffs 37,867 and 36,549. Source caps and one-shot reuse rejection
remain active. These are actual single-packet interfaces, not a full-array
diagonal implementation or physical T74 execution.

The source executables cap ell at 32. The nontrivial outer bands instead imply
ell>=45,812,984,491. Thus the finite fixtures do not execute a legal nontrivial
outer instance. They corroborate interfaces; the unbounded results are written
proofs under named source premises. No cap was removed to imply otherwise.

With Python 3.12 and the standard library, run from this directory

```sh
python3.12 -I -Werror -B verify.py
python3.12 -I -O -Werror -B verify.py
python3.12 -I -Werror -B diagonal/verify.py
python3.12 -I -O -Werror -B diagonal/verify.py
```

The wrapper authenticates the exact inventory and all retained source bytes,
runs the bounded checker, and strictly compares [RECEIPT.json](RECEIPT.json).
Boolean/integer substitutions and changed source bytes fail. Default replay
is read-only and also works in a Git-free export. The addendum wrapper separately
authenticates its inventory, the frozen arithmetic module, and its typed
[receipt](diagonal/RECEIPT.json). Running either component checker alone prints
newly computed data; it does not compare the stored receipt.

From a complete repository checkout, run

```sh
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/research_package.py --package research/twiddle-matched-layer --check-only
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/research_package.py --package research/twiddle-matched-layer
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/check_research_commit.py --package research/twiddle-matched-layer --check-source-history
```

[SOURCES.json](SOURCES.json) preserves the main20ecf289 baseline and original
catalogue card. Pending source bytes are retained in this PR's own ancestor
history; [SOURCE_INVENTORY.json](SOURCE_INVENTORY.json) records their original
paths, commits, Git blobs, SHA256s, and attribution. Frozen source modules are
not edited. [VERIFY.json](VERIFY.json) declares the bounded replay explicitly.

## Open next questions

[TASK.json](TASK.json) gives the structured next steps. The most useful next
implementation is the correctly typed active-width outer wrapper, connected
to PR3617 with the complete framing and inter-round lifecycle bill.
It must bind identical record order and extent, both component bit orders,
unit-disk output, borrowed storage, consumed previous outputs, private cleanup,
and returned heads across every round. A producer/consumer endpoint for one
record is insufficient for that obligation.

Reopen a faster-bound claim only with a paid change to the remaining outer
movement bottleneck and all retained transfer implications. Finite admission
fixtures and local header savings cannot supply that change.

## Credit

New work by Clear1nsight with substantial OpenAI assistance from a root agent
and three concurrent specialists, including independent same-session source,
proof, and executable review. No independent human or formal-kernel acceptance
is claimed. New work is Apache-2.0. Original LICENSE and NOTICE bytes are kept.

Credit Nick Petalas for PR3493's complete-format outer wrapper and PR3593's
encoded controller; Jose Manuel for the PR2298 outer construction and PR3599
actual-width root, retaining Hiroki Kumazaki's factory/rate lineage; Sagar
Thakrar for PR3611's signed packet consumer and PR3617's completed diagonal
pass; and Philipp, Douglas Colkitt, David Arias, and the retained source authors
for the earlier positional schedule, monomial, and transform work. Detailed
attribution remains in the unchanged source proofs and source inventory.
