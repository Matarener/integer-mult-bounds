# Two-pass dyadic affine streams

This is a written local algorithm/cost argument, supported by exact finite
replay. It is not a formal proof of the complete multiplication theorem.
Jose Manuel's PR2915 supplies the reached affine compiler and caller; PR3343
supplies the direct-carry incumbent. Neither predecessor is changed.

## Contract

Let B,S be positive canonical encoded cardinalities and Q>=3 odd. The borrowed
source consists of exactly V=BQS Boolean cells, in order

    source[(b*Q+x)*S+s],  0<=b<B, 0<=x<Q, 0<=s<S.

The output is a distinct owned stream at its origin, with

    output[(b*Q+f(x))*S+s] = source[(b*Q+x)*S+s].

For multiplier A in {2,4} and compiled c in {-4,...,4}, the forward map is
f(x)=Ax+c mod Q. Inverse mode implements f(x)=A^(-1)(x-c) mod Q. The source,
borrowed B/S counts and numerical Ring are preserved. A factory supplies
distinct blank fixed-role leases; successful underlying operations and enough
free roles are premises. Occupied entry leases are excluded from allocation.
No general rollback theorem for an interrupted primitive is asserted.

Q is not decoded to a host integer. Division of its encoded copy by the fixed
A returns only Q mod A to finite control. A bounded countdown loop computes
r=abs(c) mod Q in five states: decrement, increment its bounded state, and
reset on reaching zero. At every iteration its countdown and state represent
Q-j mod Q and j mod Q, using Q,0 at a reset. There are at most four iterations.
All other unbounded extents remain Count/Counter tapes.

## Residue streams

First ignore c. Partition the input x into A consecutive intervals

    ceil(kQ/A) <= x < ceil((k+1)Q/A),  0<=k<A.

In interval k, the output y=Ax-kQ increases by A and has residue
j=-kQ mod A. Since gcd(A,Q)=1, k->j permutes the A residue streams. Conversely
the output y in [0,Q) with residue j has exactly

    n_j = floor(Q/A) + [j < Q mod A]

members. Thus the partition sizes can be built from one encoded quotient,
bounded increments and the finite residue. This remains valid for Q<A: zero
size intervals are allowed. No inversion or special assumption Q>=A is used.

For c>=0, split off the last r output coordinates [Q-r,Q). Their residues start
at (Q mod A-r) mod A. For c<0, split off [0,r), whose residues start at zero.
The small fragment size s_j is the number of those at most four coordinates
having residue j. The remaining size n_j-s_j is constructed by at most four
encoded decrements. Nonnegativity follows because the fragment is an actual
subset of the residue stream. The remaining full output length is Q-r.

Input order inside every interval agrees with output order inside its residue
stream. Therefore the small fragment is a tail for c>=0 and a head for c<0.
The first physical pass copies those two parts into separate buckets for each
residue, preserving each complete S-bit row. It repeats this for each prefix
b and checks actual source exhaustion after the final row.

For c>=0, the second pass emits the small tail in its original output order,
then the remaining output beginning at residue zero. This rotates the base
output right by r and hence implements Ax+c mod Q. For c<0 it emits the
remaining output beginning at residue r mod A, then the small head beginning
at residue zero. This rotates left by r and implements Ax+c mod Q. A canonical
Q-r countdown governs the long part; a bounded r loop governs the small part.
Every consumed bucket advances by exactly its per-prefix size, so neighboring
prefixes and spectators cannot mix. All bucket ends are checked.

In inverse mode, split the input into buckets in that rotated order, then
concatenate the buckets in the original interval order. These are the inverse
split and merge of the same permutation, which gives A^(-1)(x-c). The implementation
exchanges the directions of the two passes, rather than running a forward map
and testing whether its numerical values happen to agree.

Each of the V cells is copied once into buckets and once out of buckets.
The implementation rewinds the borrowed source, clears every bucket and count,
and returns only the distinct output lease. The numerical bank is only read to
obtain its encoded modulus. The argument is a column identity and applies to
arbitrary Boolean data, including all-zero data and dirty occupied spectators.

## Cost, storage and enclosing recurrence

Count every Tape read, write and unit head move, including Count construction,
normalization, division, bounded decrement, countdowns, bucket copying,
rewinds, erasure and the actual pool's marker-read acquisitions. Let I be the
encoded modulus width. The complete successful local charge is

    T_affine(B,Q,S,I,A,c) = O(BQS + I),  A in {2,4}, |c|<=4.

The initial modulus/quotient construction costs O(I). Fixed division and the
constant number of Count copies/decrements/disposals cost O(I+log Q). A
canonical countdown from m costs O(m+log(m+1)) including construction and
disposal, by the retained amortized ripple argument. The A interval loops
cost O(B(Q+A log Q)); the long-part loop costs O(B(Q+log Q)); and the bounded
short-part loops cost O(B). There are exactly 2BQ suffix copies, each costing
O(S+log(S+1)), including its actual suffix countdown. All payload rewinds and
erasure cost O(V); fixed empty buckets cost O(A). Since A<=4 and log(t+1)<=t
for positive integers, these charges are O(V+I). Returned-output disposal is
an additional O(V) at the caller. For the canonical reached modulus I=O(log Q),
the whole kernel charge is O(V). Padded encodings retain I explicitly.

At the streaming peak there are A remaining-count tapes, one Q-r tape,
2A payload buckets, one output, and at most three nested counters (prefix,
row and suffix): 3A+5 free roles, at most **17**. Setup uses at most A+4 roles
and is below this bound. There are zero new numerical words. The 17-role case
is attained; a one-role-short fixture rejects. This is the extra free inventory
at this kernel boundary, not the total inventory of a recursively active caller.
Bucket payloads total V, the output V and the borrowed source V, so occupied
payload storage is at most 3V. Encoded counts, retained blank extents, markers
and enclosing callers are separately charged. No whole-machine backing-capacity
bound follows from the occupied payload count.

The opt-in fuser consumes only contiguous identical-field fragments:

    double^k ; translate(c)  -> affine(2^k,c,forward)
    translate(c) ; half^k    -> affine(2^k,-c,inverse),  k=1 or 2.

The second rule gives (x+c)/2^k exactly. It moves no factor across another field,
ADD, swap, negation or native call. Standalone scales, including a pair of scales
without a carry, remain unchanged: their raw fused setup can lose on tiny inputs.
The raw kernel still verifies c=0 to cover its full stated interface. A finite
before/after census is not an all-domain speed inequality.

For a completed route R, let P(R) be its disjoint replaced fragments. The charge
is explicitly

    T_new(R) = T_setup/return(R)
             + sum_{o outside P(R)} T_incumbent(o)
             + sum_{p in P(R)} T_affine(B_p,Q,S_p,I, A_p,c_p).

The retained lifecycle includes the initial source copy, modulus setup, each
intermediate clear and final bank cleanup. Every ordinary B1 call is unchanged
and included. If J is an enclosing C1 invocation, its stopped recurrence has
the same recursive children C(J) and differs only in these local charges:

    T_C1,new(J) <= sum_{h in C(J)} T_child(h)
                + T_other(J) + sum_{reached R} T_new(R).

No source access, frame conversion, recursive child, restoration or final
output disposal is free in this expression. The predecessor all-size/native
refinement, numerical capacity, stock, physical backing and outer-transfer
premises remain dependencies. This is a constant-factor component change,
with a larger fixed scratch reserve, not a new recursive profile or exponent.

## Verification boundary

The independent oracle computes each input column's modular destination, with
separate host arithmetic used only by the checker. It compares complete maps,
borrowed/count/dirty state, ownership, cleanup and every physical I/O operation.
The full kernel domain is 504 pairs: Q in {3,5,7,9,17,25,81}, (B,S) in
{(1,1),(2,3)}, A in {2,4}, c in {-4,...,4}, and both directions. The raw c=0
regressions are preserved as evidence; the adapter retains standalone scales.
Complete route fixtures additionally exercise noncommuting words, low carries,
native intervals, old prefixes, suffixes, and zero-high width. The catalogue
census covers the actual 1,123 selected chart types at the explicitly labelled
q=3 identity-low specialization; it is not selected GL64 payload execution or
a count over all low classes. The source proof supplies the arbitrary legal
low-class local identity.

Wrong-offset controls reject even all-zero contents by their column masks.
An endpoint-preserving extra read changes the exact tariff and is detected.
Malformed extent, invalid compiled arguments, source corruption and inventory
controls serve different purposes; finite replays do not prove the universal
statement by enumeration. Full selected cold replay, fitted GL64 execution,
independent human review and proof-assistant verification are not claimed.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0. The Count,
Counter, ScratchPool, caller, scaling, direct-carry and native source lineage
retain the credits in README.md and their unchanged notices.
