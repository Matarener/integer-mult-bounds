# One temporal helper split: scalar implication and source boundary

This is an independent audit of **step 1 only** of Ali Romman's PR #5786 at
`6b936acd68a7e0f9062037900f0fe9bc4b6fdd25`, using its pinned PLAN and the
PR #5774 word at `7d6ec0cdef31d0c37b7d2563e709979caa0d5eae`.
The algebra below is quantified over arbitrary inputs. Its source instantiation
checks temporal scalar data and frames; it does not admit the complete caller.

## Quantified temporal lemma

Work over the rational scalars with the source's permitted dyadic operations.
Let a finite linear word have public input vector x and arbitrary dirty owned
input vector a. Under its charged INIT/CLEAR semantics its complete endpoint is
`(T x, 0_owned)`, independent of a. Let G be a set of independent public helper
coordinates with common zero entrance frame and common full exit frame V.
Require both rows and columns of T on G to be those of the identity: equivalently,
`T = I_G direct-sum T_rest` in this coordinate decomposition. In particular, an
admissible change of basis on G commutes with T.

Fix h in G, an intermediate frame F, and a cut where the physical field h is
live at F. Suppose the following data are supplied and checked against the
actual word, including all public and dirty owned columns:

1. Collection contacts, all at F and no later than the cut, have complete
   prefix row c. Its support is in G; its dirty owned coefficients vanish.
2. Injection contacts, all at F and no earlier than the cut, have complete
   suffix column d into all old outputs. Its support is in G, including zero
   components on old owned outputs. Thus injecting a common scalar u adds d u.
3. `c d = 1`, and there is an admissible invertible dyadic basis Q on G with
   `Q e_h = d` and `c Q = e_h^T`. Both boundary basis changes are legal at the
   common entrance and exit frames.
4. A separately charged owned buffer can remain live at F from the first
   collection through the last injection. Every interior contact is available
   through a paid, admissible query subdivision; all required primitive costs
   and owned storage are retained. These are hypotheses about implementation,
   not consequences of the scalar pairing.

Then one can replace helper h's old zero-to-V target by two independent public
targets, zero-to-F and F-to-V, while retaining every other prescribed public
output and zeroing every owned output under the same INIT/CLEAR semantics.
The target ranks become `dim(F)` and `dim(V)-dim(F)`.

For completeness, when `d_h` is a unit in the dyadic ring, a concrete Q is
`B D A`, where

```
A = I - e_h sum_(j != h) c_j e_j^T,
D scales coordinate h by d_h,
B = I + sum_(j != h) (d_j/d_h) e_j e_h^T.
```

All factors are invertible and admissible under that unit hypothesis.
Immediately `B D A e_h = d`. The unit pairing gives
`c B D = e_h^T + sum_(j != h) c_j e_j^T`, so `c B D A = e_h^T`.
The present instance has `d_h = 1`.

## Proof, with the buffer value retained

Apply Q to the public helper inputs at their common entrance. Initialize the
new owned buffer b at the first collection. Its incoming value is arbitrary;
the inherited, charged INIT primitive removes its dependence on that value.
Accumulate the collection contacts without changing their source fields.
Their sum is `c Q x = x_h`, independently of every dirty owned input.
No inverse of a possibly singular prefix is used.

At the cut write y for the old value of physical field h. Introduce a fresh,
independent public input z at F. Initially `(h,b,fresh) = (y,x_h,z)`. Perform

```
swap(h,b); swap(fresh,b); b <- b - h.
```

Each scalar swap is three ADDs and one SCALE by -1: on coordinates (p,q), use
`p<-p+q; q<-q-p; p<-p+q; q<--q`. Thus the displayed sequence leaves
`(h,b,fresh) = (x_h,z-x_h,y)`. Retire physical h at F. Rename **every** remaining
reference in its old trajectory to fresh, including its final boundary-basis
reference. The source continuation therefore begins with its original y;
there is no assumption that y equals x_h.

Keep b at F and inject its unchanged value at the stated later contacts.
Linearity of the complete suffix histories makes the resulting correction
exactly `d(z-x_h)`, including zero correction on every old owned output.
The continuing old-coordinate output before the final basis inverse is

```
T Q x + d(z-x_h).
```

Since T commutes with Q and `Q^-1 d = e_h`, applying the legal terminal Q^-1
gives `T x + e_h(z-x_h)`. Its h coordinate is z, every other old public output
is unchanged, and all old owned outputs remain zero. The retired physical
field holds x_h at F. These are the two independent targets asserted above.

After its last injection **the buffer still contains `z-x_h` in general**.
Its final zero is supplied by the inherited, charged CLEAR primitive. This
argument does not derive reversible erasure of an arbitrary scalar, supply
free clean storage, or discharge the framework assumption behind INIT/CLEAR.

## Exact first-step binding and limits

For the pinned step, h is 696, F is frame 1031, and the cut time2 is 27044.
An even time2 denotes the boundary before event `time2/2`; an odd value is an
interior contact in the indexed MOVE. The collection is field 696 at 27026.
The injection contacts are fields 696 and 697 at 27044, owned field 770 at
27501, and field 699 at 27516. The complete row and column to check are

```
c = e_696^T,
d = e_696 + e_697 + e_699 + e_709 + e_733 + 2 e_133.
```

All six coordinates in d enter at frame 3 (the zero space) and exit at frame
127 (dimension nine). They belong to the identity block of the prescribed
source endpoint `I + sum_(r live) e_(r+112) e_r^T`. Thus `c d = 1`, `d_696 = 1`,
and the boundary-basis conditions hold. These support facts alone do not
establish the temporal rows: the verifier separately checks complete
prefix/suffix histories and the actual source contact frames and lifetime.

The odd injection contact is inside source event 13750,
`MOVE 770 591 597 owned=true`. The actual frame dimensions are 8, 5, 1, and
the required descending inclusions are `591 > 1031 > 597`. Its paid ranks
are consequently `7 -> (3,4)`, with access-query cost change
`H3 + H4 - H7`, where `Hr = r^t`. This is a frame/rank audit of this single
subdivision, not the full step invoice. In particular, `2H1-H2` is not the
cost change for this first-step query. The split helper targets have ranks
5 and 4 instead of 9.

The verifier also emits and replays this first split in an independent formal
namespace: old public labels 0 through 766 and owned labels 767 through 788
are retained, fresh public input z is label 789, and the new owned buffer is
790. It emits the initial basis, collection, all nine cut operations, all four
injections, the two real-frame query segments with their intervening injection,
the charged buffer CLEAR, and the terminal basis inverse. All source references
to 696 at or after the cut are renamed to 789; the terminal inverse uses 789
as well. This is not a byte-identity claim for the author's emitted word.

The literal witness has 25,909 events, 25 owned lifetimes and peak 12 live
owned fields. Exact replay checks all `791^2 = 625,681` endpoint coefficient
positions, including every arbitrary dirty owned input axis. It restores all
old public values and zero owned outputs, retires 696 at frame 1031 and ends
789 at frame 127. Immediately before CLEAR the buffer row is exactly
`e_789^T - e_696^T`. Omitting that CLEAR and omitting the first swap's SCALE
are separately rejected by endpoint discrepancies. Thus the finite decoded
scalar/frame restoration and emitted owned-lifetime closure are checked;
their complete native implementation and price remain separate obligations.

This audit does not check native maps or absolute phases, price all boundary
and lifetime operations, replay steps 2 or 3, verify the physical caller,
establish an ordinary compiler, or admit a full conditional kappa bound.
Static unit pairing without the checked temporal frames, complete histories,
legal bases, and funded owned lifetime cannot justify the target split.

Credit: Ali Romman with OpenAI Codex assistance for the source temporal
construction, PLAN, PR #5774 word and retained predecessor lineage in NOTICE.
This scoped proof/audit was prepared by ToikY with substantial OpenAI Codex
assistance, using separate implementation and review contexts. Apache-2.0.
