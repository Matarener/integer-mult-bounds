# A birth-lowered market needs a paid deletion

This is a scoped accounting obstruction, with new finite continuation fixtures.
It does not re-prove or audit the source construction.

## Contract

Fix the PR6030 word stored by DreamingOfClouds's PR6170 toolkit. Write
`t = 1-C`, with `0<t<1`. Use the source recursive ledger

    F(t) = 18 sum_helpers span(h)^t - 18 sum_MOVEs rank(MOVE)^t
           + unchanged outer terms.

A public MOVE ascends strictly through nested binary subspaces. Its rank is
the difference of their dimensions. A helper's productive span is its final
dimension minus its initial dimension. These are inherited pricing rules,
not a claim that all physical work is priced by this equation.

For each of the fourteen market birth frames G in the pinned rebuild manifest,
let O=G^perp under the literal binary dot product. Select one or more public
helpers initially at G and finally at the full nine-dimensional frame.
Replace each selected birth G by B contained in O intersect G. Preserve:

- every original MOVE, with its register, source and destination frames;
- the final frame of every selected helper;
- all other productive initial/final frames and their credits.

Arbitrary scalar resynthesis, including hub/market coupling, is allowed.
Additional paid work is allowed and charged. No additional productive credit
is granted. The selected registers must still reach G to execute their first
original MOVE. Multiple changed registers are charged separately.

The theorem is conditional on a candidate satisfying this contract. It does
not assert that an arbitrary scalar resynthesis is realizable or correct.

## General lower bound

Suppose a helper's original productive span is s>0 and lowering its birth
adds dimension d>0. Before its first original MOVE it must ascend from the
new birth to the old birth. Let the positive ranks of those new MOVEs be
`d_1,...,d_k`. Nesting gives `sum_i d_i=d`.

For `0<t<1`, strict subadditivity gives

    sum_i d_i^t >= d^t,
    (s+d)^t < s^t+d^t.

Its target-credit increase is `18((s+d)^t-s^t)`. Every original paid MOVE
remains, and the extra ascents cost at least `18d^t`. Hence

    Delta F(t) <= -18 [s^t+d^t-(s+d)^t] < 0.                 (1)

Summing (1) over selected helpers proves the same strict loss for any
nonempty simultaneous choice. Extra paid work can only decrease F further.
This argument does not inspect scalar coefficients, row contents, event
order between different registers, or independence of the proposed targets.
It already rejects the optimistic invoice. Correctness and native delivery
cannot make that invoice better without changing the stated contract.

For completeness, strict subadditivity follows by fixing s>0 and observing
that `g(d)=(s+d)^t-d^t` has negative derivative for d>0, with limiting value
`s^t` at zero. Iterating the non-strict form proves the path inequality.

## Exact P104 specialization and sharpness

The checker enumerates the fourteen manifest markets. Each G has dimension
five; its orthogonal O has dimension four; and I=O intersect G has dimension
two. The helpers born at these G and ending at the full frame form a disjoint
set of 62 roles. These extracted source facts select the new candidate family;
they are not a replay of the original arithmetic or invoice.

A binary plane has exactly five subspaces: zero, its three lines, and itself.
Thus there are 310 single-helper choices (h,B). Their added dimensions are
five, four and three respectively, and every old helper span is four.
For fixed s and t, the deficit

    D(s,d,t)=s^t+d^t-(s+d)^t

strictly increases with d, since its d derivative is
`t[d^(t-1)-(s+d)^(t-1)]>0`. Consequently every changed helper loses at least

    18 [4^t+3^t-7^t],                                   (2)

and a nonempty m-helper change loses at least m times (2).
The bound holds throughout the open power interval, including the selected
complex supplier's power, without a numerical root search.

The optimistic lower bound is attained as an invoice difference: take
B=I, change only h's initial frame, and prepend the single MOVE B->G.
This MOVE changes no logical row. At the old entry boundary, every register
again has precisely its old frame and arbitrary unit row. Keeping the entire
old program therefore preserves its arbitrary-input continuation identity,
conditional on the source's identity. No arithmetic replay of that source is
needed or claimed. The new recursive bill is exactly (2) worse. Scalar or
physical overhead can add cost; attainment here concerns this recursive bill.

The checker constructs all 310 such continuation splices, checks their
new prefix and literal unchanged suffix, and derives their changed target and
paid entries. It does not claim to enumerate every possible scalar coupling.

## What this excludes and what remains

The result excludes obtaining a gain solely by lowering market births and
resynthesizing scalars while preserving the original paid transitions and
other target endpoints. A prospective coupled word must remove an original
paid transition or obtain another justified target/boundary gain worth more
than its strict preparation deficit. Replacing, splitting or deleting old
MOVEs, changing helper final frames, adding productive targets, owned/native
interfaces and actual consumer costs require a new comparison.

No universal helper-split barrier, supplier admission, complete multiplication
theorem, selected-frontier change or new kappa is proved. No source result was
independently audited. The source's arbitrary-input identity and recursive
pricing convention are cited premises. Independent human and formal
proof-kernel review are unclaimed.

The argument uses classical concavity and monotone dimension accounting.
The contribution is this quantified changed-boundary obstruction, its sharp
P104 preparation bill and the explicit new continuation family. Credit
DreamingOfClouds for PR6170's geometry, Lemma 11 opening, word and ledger, Ali
Romman and the retained P104/native/helper/caller/compiler/BIT contributors.
This contribution was produced by Nick Petalas.
