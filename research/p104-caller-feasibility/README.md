# P104 caller feasibility after PR3609

**Two source-bound results, with no new supplier or selected bound claimed.**
This package answers the changed-consumer and physical-format routes from the
[PR3609 handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3609).
The companion normalised-layer investigation is a different interface and
does not supply a P104 cost credit.

The first result is a sharp **425 rejected / 426 abstractly passing** threshold
for rank-unit deletions from the actual new full dual, across every integer
pair count in the named inherited coverage model. The second is a sharp
**six / seven / six** fractional-bit contract for its entrance, full execution,
and final outputs. A physical producer, legal owners, and an affordable full
caller are still missing. Neither theorem makes unpriced costs zero.

## Changed complete consumer

[consumer/PROOF.md](consumer/PROOF.md) derives an exact whole-bill criterion for
an arbitrary replacement dual profile, genuine unpaid coverage relief, and
additional rank-normalised cost. It distinguishes a realised replacement from
an optimistic relaxation.

The retained forward has 1,646 children and rank mass 3,070. PR3609's new full
dual has 1,742 children and rank mass 3,542. In the named all-pair consumer,
there are p+1 forward calls and p dual calls, m=16p+9, W=208p, and the stated
3,014 endpoint credit per call. Here p denotes the pair count, not precision.

Deleting rank-one children is the most favourable integer rank-unit deletion
at a fixed allowance. Strict convexity of the relaxed excess in p, together
with exact outward rational evaluations at p=6,7,8, proves that deleting at
most 425 units per dual fails for **every p>=1 and every finite number of
fully paid auxiliary banks**. At 425, the global integer minimum is p=7 and
is positive, approximately 1.6006864105095964.

An abstract deletion of 426 rank-one children per dual passes at p=7 and
a=1/596, whose outer ratio 1/597 exceeds the frozen selected benchmark. Its
entire seven-pair bill has only about **4.557071360876949 rank-normalised cost
units** of remaining slack. Adding four units passes; adding five fails.
At fixed p=4, the corresponding boundary is 427/428. No such deletion network
is constructed. Endpoint credits and coverage cannot be silently retained
after a replacement that changes their premises.

The independent calculator also reproduces two different providers' arithmetic.
[PR3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605), at exact
head `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`, has 23,953,011 children,
rank mass 48,165,120, and the strict root bracket
0.001730006549538841847005 < beta < 0.001730006549538841847006 in its own
T740 model. The [PR3574](https://github.com/CrocSwap/integer-mult-bounds/pull/3574)
1126/1127 hosting separator also agrees under its own native-channel law.
These are comparisons, not substitute P104 bills. This package does not replay
either historical physical release or establish its recursive assumptions.

## Exact physical format

[physical/FORMAT_PROOF.md](physical/FORMAT_PROOF.md) combines Gaussian-ideal
valuation with the actual program's rational rows and a literal dependency
cone. For arbitrary initial physical components on the 2^-f grid, one common
fixed-point format needs the following added fractional bits.

| Boundary | Sharp uniform guard | Scope |
| --- | ---: | --- |
| Standalone entrance | 6 | All 1,238 new operations |
| Entrance plus retained projection | 7 | All 5,265 operations |
| Required final outputs | 6 | All 358 physical fields |

Refining the mantissa and its unit preserves the numerical input. The theorem
computes the ideal Gaussian word exactly on the refined grid; it does not
identify that result with a separately rounded coarse-grid execution outside
the source's exactness domain. The six-bit entrance proof does not assert the
false inclusion 64 Z[i]^512 in the stronger sufficient domain 4 B9.

The checker traces every scalar row, scalar product, and final frame. A
36-event dependency cone gives the actual seven-bit obstruction at original
event 2142, combined event 3000. A required X0 endpoint proves the six-bit lower
bound. Full seven-bit sufficiency uses the credited Newton module and native
covariance theorems. Those historical theorems are inherited, not re-certified
by the bounded witness.

If each original real and imaginary component has magnitude at most H, a
sufficient stored-field bound is **3296H**, and the declared literal scalar
schedule's scratch bound is **6592H**. With b magnitude bits in the original
mantissa, sufficient full-word signed widths are b+20 for fields and b+21 for
scratch. These include integer headroom as well as the seven fractional bits.
No minimal magnitude-width or arbitrary recursive-depth claim is made.

[physical/CALLER_AUDIT.md](physical/CALLER_AUDIT.md) records the named source
interfaces inspected and the exact producer, borrowing, conversion, routing,
and cost obligations. Source preparation and output-format conversion remain
paid operations or explicit producer/consumer contracts.

## Evidence and reproduction

Use Python 3.12 and the standard library. From this directory, including a
Git-free source export, run

```sh
python3.12 -I -Werror -B verify.py
python3.12 -I -O -Werror -B verify.py
```

Each component authenticates its retained source bytes, recomputes its receipt,
and compares it with strict JSON types. Default replay is read-only. Arithmetic
signs use outward rational intervals, not floating-point approximations.
See [consumer/RESULT.json](consumer/RESULT.json) and
[physical/FORMAT_RESULT.json](physical/FORMAT_RESULT.json) for the deterministic
receipts. [VERIFY.json](VERIFY.json) registers both Python modes. These commands
do not launch a historical native census, full selected replay, physical owner
implementation, or formal proof kernel.

From a complete repository checkout, run

```sh
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/research_package.py --package research/p104-caller-feasibility --check-only
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/research_package.py --package research/p104-caller-feasibility
GIT_NO_REPLACE_OBJECTS=1 python3.12 -B scripts/check_research_commit.py --package research/p104-caller-feasibility --check-source-history
```

[SOURCES.json](SOURCES.json) binds the unchanged task catalogue and selected
record at main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Exact pending-source
bytes are retained in this PR's own ancestor history. The component manifests
record original public paths, commits, blobs, and SHA256s. This preserves
provenance without requiring unrelated unmerged branches in a clean checkout.
The selected frontier is unchanged.

## Open next questions

[TASK.json](TASK.json) gives structured questions, first steps, and blockers.
Useful P104 reopening evidence is a realised replacement profile or changed
coverage law that passes its own full bill, with legal field access and actual
source/return contracts. The 426 sensitivity witness is a rejection screen for
proposals, not a reason to expand an unpriced construction.

A concrete caller must supply writable/restored Y access, owned private-zero
lifetimes, the stated frames and width, and paid conversion, routing,
controller, and recursion. Those costs must enter the same complete inequality.
For work aimed at the stronger existing T740 candidate, the distinct next step
is an independent audit of PR3605's complete release and retained implications,
not transplanting its profile into P104.

## Credit

Prepared by Clear1nsight with substantial OpenAI assistance from a root agent
and three concurrent specialists, including cross-review. This is same-session
independent implementation and review, not independent human acceptance.
New work is Apache-2.0; original notices are retained with the source inputs.

Credit PR3609 for the actual entrance and full profile; Jose Manuel's p=4
consumer and Nick Petalas's all-pair budget for the inherited model; Vasek and
PR2458/2744 for the forward; ywz65 and Arham Tahir for the original physical
word and native data; the PR3382/3406/3416 lineage and Ross Richardson's
Clifford-grid work for module and precision premises; and Dumas and Grenet
for the earlier dirty-accumulation method. PR3605's T740 construction is Ross
Richardson's work. PR3574 is jwr's work, retaining Nick Petalas's budget,
Rohan Arun's native channel, and its lineage. Detailed attribution remains in
the component proofs and manifests.
