# Encoded physical sparse XOR batch

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## Contract and inherited premises

I implement one batch after reservoir placement. I use the fixed field order
`(u,t,y,b)`, with widths `(H,H,N,H)`, positive H,N, and complete binary ranges.
Each address carries an opaque R-bit record; R and the outer-row count C are
positive. For Gaussian records, I preserve the complete signed component
encodings and their order within each record. Payload correlations are arbitrary.

I receive canonical Count tapes for the numerical parameters, plus one borrowed
pair tape. For k pairs, I require

    w=max(1,ceil(log2 N)), D=2kw,
    0<=s_i<N, 0<=j_i, j_i+K<=N,
    j_(i+1)>=j_i+K, K>=1, G>=1, kG<=H.

The pair tape contains exactly k fixed-width `(s_i,j_i)` records, with w bits
per position in the retained least-significant-bit-first format. I require
distinct sources and `s_i` outside the entire target set. Sources may lie
inside any guard. The high H-kG control bits may have arbitrary values.
I admit k=0 with an empty pair tape.

I return the exact address operation

    T(u,t,y,b)=(u,t,y XOR sum_i y[s_i] 2^j_i,b).

I preserve the borrowed payload, pair tape and numerical descriptors, including
their origin heads. I return a distinct protected output at its origin and
erase owned work on successful admitted execution. The caller consumes that
output before reuse. I retain the predecessor's successful-execution contract;
I make no interrupted-macro rollback or general malformed-input time claim.

I retain PR1673's sparse-control algebra and conditional router argument,
PR3055's physical rotations/repair/B1 boundary, and PR3562's ordinary-rate proof.
I authenticate their retained bytes and compare all 23 active ordinary-backend
files with the rate proof's cohort, including nested archives. I require a
fresh native with that cohort's `Profile(1,577)` before engine ownership.

For the time theorem, I assume the completed binary ordinary bound

    T_B1(v,h) <= K_q v(1+h^tau), tau=332353/332929,

with the retained source-admissible fixed q, C0 endpoint, chronology, stock,
fixed-tape refinement and cost premises. Small q=2 fixtures establish their
declared functional coverage. I do not infer the inherited universal premises
from those fixtures or from source authentication.

## The raw word and prefix reads

Put B=2^G and define

    E(y)=sum_i y[j_i] B^i,
    P(y)=sum_i y[s_i] B^i,
    z_i=(u >> iG) mod 2.

I retain the four-update gadget F:

    y += sum_i 2 z_i t_i 2^j_i;
    t += E(y);
    y += sum_i z_i(1-2t_i)2^j_i;
    t -= E(y XOR sum_i z_i 2^j_i).

I use whole-field moduli 2^N and 2^H throughout, including exceptional
addresses and inactive high control digits. I execute

    F; L; F; L^-1,  where L: u += P(y).

For each t update I swap t with b, rotate b using the preceding y field,
then swap back. I use the same shuttle for the u load and unload. During a
y rotation I read only preceding u,t. During a b rotation I can read all of
the current y field. I therefore execute twelve full-width-H swaps and ten
rotations per complete row. I pay the swaps at H, including inactive digits.

Each rotation's offset is independent of its target and reads only preceding
fields. I implement it with the retained split/merge scans, recomputing the
same offset on both traversals. I retain the swap's complete `Binary.run`,
suspended caller allocation scope, protected-return copy and callee cleanup.
Thus the raw word S is a permutation on all addresses, even with modular
wraparound. The dirty back field returns after each shuttle.

A direct same-y early-source substitution would violate this condition.
For G=2, K=N=6, H=2, source bit 1, target bit 0 and t=1, its first purported rotation
would send both y=18 and y=20 to 20 via `y -> y+2*y[1] mod64`. Both satisfy
the guard below. I use the late-source word; I do not treat a target-dependent
offset as an available rotation.

## Guarded identity and complete repair

I call an address good when, for each listed pair,

    u_i,t_i < B-1,
    2B <= (y >> (j_i+1)) mod 2^(K-1) < 2^(K-1)-2B.

An empty guard interval makes a nonempty batch wholly exceptional. For k=0,
I return false from the bad predicate before exponentiating unused K or G.
Their encoded input lengths still enter the resource bill.

On a good address, a completed F toggles target j_i by z_i and restores t.
The two y updates have total displacement `1-2e` when z_i=1, where e was the
initial target bit, and zero when z_i=0. The margins contain both intermediate
displacements inside the guard. Disjoint guards prevent cross-block carries.
I use no equality of successive target gaps.

Completed F fixes every non-target bit. A source inside a guard may change
during F, but returns before the load or unload reads it. The load changes
u_i to `u_i+y[s_i]` without interdigit carry. The loaded digit may equal B-1;
the second F only reads its parity and does not increment it. The second F
restores t again and fixes the source bits. Unloading therefore restores u,
including inactive high digits. I obtain S=T on the good set.

The ideal T is an involution because sources avoid the whole target set.
It preserves controls and guard bits, so it preserves the good set. Since S
is a bijection and agrees there with T, it preserves the exceptional set too.

I retain complete-row repair. At current raw-output address q, I compute
the destination `T(S^-1(q))` for an exceptional record. I reverse the literal
22-operation word and evaluate each inverse offset on the current inverse
state. I retain all H control bits in the state and key. I do not freeze the
forward controls or partition repair by a dirty-control value.

I preserve the retained good stream, exceptional keyed stream and hole flags.
Stable radix passes order the exceptional destinations; reinsertion checks
that the next key equals the current hole. Since T composed with S^-1 is a
permutation of the exceptional set, I fill each hole once and preserve each
opaque record. Good records already have their ideal destinations. This
proves the full endpoint for arbitrary payloads.

I end the batch after repair. The old regular Compact operation appended a
highest selected bit outside its guarded digit list. Here each listed target
already has its complete guard, so that extra operation would change the
specified endpoint.

## Encoded pair-list refinement

I store the variable list on one borrowed tape. `pair(i)` rewinds it, skips
2iw cells using an encoded counter, reads two fixed-width Counts, and closes
them and rewinds in `finally`. Nested validation reads the same tape again;
it retains at most two decoded pairs. I construct no k-dependent field tuple
or physical tape inventory.

Validation checks the canonical position width, complete descriptor extent,
ordered disjoint guards, source bounds, source uniqueness and source/target
exclusion. Repeated scans give these tests without an indexed list. On
admitted nonempty inputs I obtain K<=N and G<=H. I derive offsets by scanning
the pairs and distinguishing source position s_i, target position j_i and
packed control position iG. These three positions cannot share a uniform
stride counter.

I use the retained Count bit windows, shifts, XOR, modular sums and fixed-width
read/write operations. Negative terms use a positive magnitude and modular
negation. I inherit the current-control inverse evaluator. Each helper preserves
borrowed Counts and closes its owned numerical work. Prefix decoding sets
inaccessible fields to zero; the validated operation controls make those zeros
irrelevant to the offset.

## Complete time bill

Write

    a=N+3H, M0=2^a, v0=M0 R, M=C M0, V=MR,
    D=2kw,
    A=2+a+D+ceil(log2(R+1))+I,

where I includes canonical scalar-parameter input lengths other than the
separately charged outer-row count C. In particular I includes the encoded
lengths of unused K,G for an empty list.

One pair read costs `O((i+1)w+log^2(D+2))`, including skip, decode, erase and
rewind, and hence O(A^2). A selected-bit pack, mask, offset or guard evaluation
costs O(kA^2), at most O(A^3). The nested admission scans cost O(k^2 A^2),
at most O(A^4), once before the row loop. Counts used in modular geometry have
O(A) bits: packed weights fit H+1 bits and shifted target terms fit O(N+H).
The retained elementary arithmetic has quadratic bit bounds. The fixed raw
inverse and ideal destination computation therefore cost O(A^3) per record.

I retain the conservative full invoice

    12 sum_(row=1)^C T_B1(v0,H)
      + O(V + M A^6 + delta M A(R+A))
    <= 12 K_q V(1+H^tau)
      + O(V + M A^6 + delta M A(R+A)),

with

    delta=min(1,k(2/B+8B/2^K)).

I charge both split and merge offset computations in the ten rotations.
The M A^6 allowance covers the new descriptor scans, validation, retained
setup and disposal. I retain the separate exceptional radix/record bill;
I do not replace a full computed-key sort by a fast primitive.

For a fast-domain statement, take p>=2, fixed positive constants b,A0,
`a,I,log2(R+1)<=A0 p`, and actual records

    R >= 2^(b(log2 p)^2),
    G=4ceil(log2 p)+6,
    K>=G+4ceil(log2 p)+10.

Since kG<=H and w=O(log p), I obtain D=O(p) and A=O(p). The union bound gives
`delta<=5k/(128p^4)=O(p^-3)`, since k<=N=O(p). For any fixed j>=0,

    p^j/R <= 2^(jx-bx^2) <= 2^(j^2/(4b)), x=log2 p.

This pays A^6/R and the remaining `delta A(1+A/R)` uniformly. I obtain

    time O_(q,b,A0)(V(1+H^tau)).

If H=kG, I may write the nonempty-batch bound as
`O_(q,b,A0)(V(1+(k log p)^tau))`. For a caller that supplies H>kG, I retain H
in the bill. I require actual complete record bits; a declared length or fixed
coarse label does not supply them.

## Fixed inventory and occupied space

I retain the 288-role sparse pool, the binary/native pools and the protected
output. I suspend the sparse allocation scope while B1 owns its execution.
For a source-level upper bound, I budget 16 simultaneous leases for Layout,
the outer-row counter and current row; 24 for retained rotation, repair,
decode and radix frames; and 32 for sparse control and arithmetic. These sum
to 72, below a conservative 96-lease bound and the allocated 288.

In the control category I count at most 11 local Counts, two pair contexts
with three retained Counts each, and at most eight additional leases in the
deepest arithmetic-helper chain. I include `Count.literal`'s temporary copy,
product/division intermediates and a returned value before predecessor disposal.
Rotation and repair run sequentially; radix sorting starts after the repair
address state closes. I charge the separate binary/native inventory through
the inherited bound. I do not infer a fixed inventory merely from measured peaks.

For one row, the temporary payload, hole and keyed streams give the envelope

    O(V + D + delta M0 a + A + log(C+1)),

plus retained ordinary workspace and fixed compilation. The protected output
can grow to V. Repeated descriptor scans revisit D cells; they do not multiply
its storage. Under the fast domain I retain O_(q,b,A0)(V)+F_q space.

For simulator backing extent, I multiply the maximum temporary-role extent
by the fixed pool capacity. I state the bound for a fresh engine, or against
the maximum preceding invocation extent during reuse. Clearing cells does not
shrink historical backing arrays.

## Scope of the new step

I supply the encoded variable-position control and physical repaired return.
PR1673 already supplies the unequal-gap algebra; I retain that credit.
PR3581's B1-only materialized-exposure lower bound restricts a different
operation alphabet. Here I execute controlled rotations and sparse correction
between B1 calls and retain their complete charges.

I have not supplied reservoir placement, matching/color scheduling, the full
arbitrary-support router, a T74/root integration, or the enclosing multiplication
and error ledger. I leave scientific review of the inherited universal premises
open and leave the selected frontier unchanged.
