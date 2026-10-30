# Coalescing the last-read owned copy

This contribution was produced by Nick Petalas. Apache-2.0.

## Claim and source

The claim is a finite exact circuit certificate and a scoped substitution
proof. It does not assert a new exponent saving, a smaller peak-space bound,
or a complete multiplication theorem.

The input is DreamingOfClouds' PR6144 word at
`4f3b67e7c37ae270da9584033132866d0cf63e42`. `PREDECESSOR.json` records the
original path, Git blob, SHA256 and credit. The byte-identical exported word
is retained in this branch's history. Ali Romman's PR5827 `local.py` is already
on canonical main and is used unchanged. The source word's conditional
supplier and framework claims are cited, not independently audited here.

All event indices below are zero-based indices in the retained input.

## General substitution

Suppose an owned field S contains x, and an initialized owned field D receives
COPY D,S followed by SCALE D,q. Suppose that after this COPY the old S has no
use except a later CLEAR. Replace the COPY and D's initialization by SCALE S,q;
execute D's continuation on S; clear S where D was cleared; delete the old
S CLEAR. Require that S is available before the continuation starts, and that
the continuation does not read the old S separately.

Immediately after the scaling, the substituted S and old D have equal values
and frames. Every subsequent continuation operation has the same coefficient,
frame and value operands after renaming. Induction over the continuation proves
equality of every other field and the substituted D value. The unread old S
does not influence another field. Both constructions return all owned fields
to the erased state. This is an exact linear argument over any coefficient
field containing q. Its use here is over the dyadic rationals.

The substituted lifetime starts at the old S initialization and ends at the
old D erasure. While the two lifetimes previously overlapped, the new one
occupies one field. Elsewhere it occupies at most their former union. Thus
this substitution cannot increase live owned occupancy. This statement alone
does not imply that the global peak falls strictly.

## Literal application

Old S is role 791, initialized at event 13473 in frame 549 and assigned the
value x of role 173 by event 13474. Its only subsequent reads are

```text
13475  ADD 121,791,1/2,549
13659  COPY 770,791,1,549
```

Its only remaining use is CLEAR at event 15591 in frame 549. There are no
hidden reads or writes. `construct.py` checks this complete use list.

Old D is role 770. The adjacent events at 13658 through 13661 initialize it,
copy x, scale by 1/2 and start its descent from frame 549 to 553. Its
continuation ends with CLEAR in frame 593 at event 15424. It has exactly one
initialization and no use outside that lifetime. The continuation never reads
old 791. Therefore the substitution lemma applies with q = 1/2. The new
scaling occurs just before the old descent, after the retained read at 13475.

The constructor removes old role 770 from the owned inventory. For every
remaining old role r, the new label is r when r < 770 and r-1 when r > 770.
Uses of old 770 first become old 791, then become new role 790. Only opcode
role positions are renamed; frame IDs and coefficients are unchanged.

All public initial and final frames, ports, productive outputs and arbitrary
public input coordinates are identical. Initial arbitrary owned contents
cannot affect the result because every reached owned lifetime initializes
before use. The new source-owned lifetime is initialized once and cleared at
the continuation's old endpoint. Both exact row replay and reverse-column
replay check the resulting word in full.

## Exact account

The removed INIT costs 2 scalar units, COPY with coefficient 1 costs 8, and
CLEAR costs 2. The same single SCALE by 1/2 remains and costs 2 in either
program. Net savings are 12 scalar units and three events. The original
source-owned CLEAR disappears, and the continuation CLEAR now clears the
substituted field.

Literal enumeration gives

```text
events                22818 -> 22815
local scalar units   189658 -> 189646
declared owned fields    29 -> 28
owned lifetimes          31 -> 30
peak live owned fields   13 -> 13
```

Every MOVE keeps its entry frame, exit frame and ownership flag. Its complete
native operator is therefore the same prescribed operator after role
renaming, including its scalar phase. No new native frame pair is introduced.
Every public endpoint is retained, so every productive rank is retained.
The complete local paid histogram is unchanged and equals
`{1:2215, 2:457, 3:496, 4:99, 5:164, 6:8, 7:9, 8:1}`.
Consequently this edit supplies no new signed-moment or kappa gain.

## Verification boundary

The finite checker verifies all 798 columns and 636804 matrix coefficients
of the edited word using the retained sparse forward and dense reverse
implementations. Nine mutation controls cover missing initialization, scaling,
clear, descent and read; wrong scaling sign; hidden source use; a changed COPY;
and incorrect source inventory. Normal and optimized runs retain the checks.

The semantic native operator list is unchanged; no native operator replay,
complete caller, compiler, outer ledger, rounded error analysis, Lean or Docker
run is part of this result. In particular the retained caller's reserve is
not changed to 28 by this package. All five framework assumptions remain.
The rounded numerical equivalence of copying and subsequently scaling an
existing field is a separate implementation obligation.
