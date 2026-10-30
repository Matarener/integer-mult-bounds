# Direct bounded carry rotation

This is a source-level argument for `rotation.py` and the opt-in adapter, not a
formal proof of the complete multiplication theorem. Jose Manuel's PR2915
supplies the reached high-field route, its complete affine compiler, and its
inherited primitive/caller contracts. We change one bounded carry operation.
The exact base and executable/archive pins are in SOURCES.json.

## Contract and exact coordinates

Let B,Q,S be positive canonical encoded counts, with Q>1 for the actual Ring
interface, and V=BQS. A complete input contains the Boolean cells
`source[(b Q+x) S+s]`, in that order, for 0<=b<B, 0<=x<Q, 0<=s<S.
The source and cardinalities enter at their origins. The output must satisfy

    output[(b Q+((x+a) mod Q)) S+s] = source[(b Q+x) S+s],

where the compiled integer a is in {-4,-3,-2,-1,1,2,3,4}. Neither the source,
counts nor numerical Ring are disposable. The factory supplies distinct blank
owned scratch leases. Capacity and successful underlying operations are
premises. Existing occupied leases are excluded from allocation and preserved.
No general interrupted-operation rollback guarantee is asserted.

`split_lengths` keeps a canonical countdown initially equal to Q and a count
initially zero. After j bounded iterations they represent Q-r and r, where
r=j mod Q, including the representation Q,0 when r=0. Decrement/increment
preserves this invariant until the countdown reaches zero, when both are reset.
This proves the returned pair Q-r,r for r=abs(a) mod Q. There are at most four
iterations. The runtime modulus is never decoded to a host integer; only the
already compiled carry chooses a bounded finite-control loop.

For a>0, split each Q-field row into intervals L=[0,Q-r), R=[Q-r,Q). Store all
L blocks in one sequential bucket and all R blocks in another, retaining the
complete S-bit suffix and the order of the B prefixes. Emit R then L for each
prefix. An old x<Q-r is emitted at r+x, and an old x>=Q-r at x-(Q-r), exactly
x+a mod Q. For a<0 split at r instead: L=[0,r), R=[r,Q); emit R then L. These
coordinates are x-r mod Q. The bucket cursors advance by their exact per-prefix
lengths, so no suffix or neighboring prefix is interchanged.

When r=0, the result is the identity but is still copied to a distinct owned
output. This covers, for example, carries ±3 at Q=3. The helper split itself
also has a valid Q=1 identity, but Ring rejects Q=1 and the enclosing PR2915
executor skips all high operations there. The complete-route zero-high fixture
checks that unchanged boundary; no Q=1 Ring execution is claimed.

The code checks input exhaustion at the actual end of the first pass, and both
bucket ends at the end of the second. It rewinds the source, clears both private
buckets and every count, and returns only the output lease at its origin. The
numerical bank is only read to obtain the modulus. Thus the column identity
holds on arbitrary Boolean input, without zero-filled-source assumptions.

## Complete local cost and storage

Count every Tape read, write and unit movement, including encoded setup,
countdown allocation/normalization, payload copies, rewinds, erasure and pool
acquisitions. Let I be the fixed encoded width scanned when copying the Ring
modulus. The direct kernel costs

    T_rotate(B,Q,S,I,a) = O(BQS + I),   0<|a|<=4.

Here is the complete decomposition, with all constants independent of B,Q,S.
The initial modulus copy and normalization cost O(I). The bounded split uses
O(log Q) copying, at most four decrements and bounded zero-counter resets. Its
final copy and all split-count disposal cost O(log Q). A canonical countdown
from m through zero costs O(m+log(m+1)) including construction and disposal:
bit toggles and head travel have a geometric sum, and the final erasure costs
its encoded length. This is the actual retained Counter algorithm, not an
assumption of constant-time arbitrary integer subtraction.

Each nonidentity route has two phases. Each phase has one B-countdown and at
most two Q-row subloops per prefix. There are exactly BQ suffix copies per
phase; each suffix copy costs O(S), including its S-countdown when S>1. The
one-bit branch is constant. Since log(m+1)<=m for positive integer m, all row,
prefix and suffix initialization costs are absorbed into O(BQS). There are two
full payload copy passes (2V copied bits), O(V) total bucket rewind/clear work,
O(V) source/output rewinds, and a fixed number of end checks and acquisitions.
The identity path uses one complete copy pass. Returned-output disposal is an
additional O(V) charge at the caller. No recursive child, source access, sign,
frame change, or restoration is hidden in this expression.

For the reached canonical high bank I=O(log Q), this becomes O(V). Arbitrarily
padded encodings retain the separate I term. This is a constant-factor execution
change; it does not improve the recursive exponent or provide a total stock,
backing-capacity, uniform primitive coefficient or machine-admission theorem.

At the nonidentity streaming peak there are three payload leases (left, right,
output), two split counts, and at most three nested counters (prefix, field,
suffix): **eight additional scratch roles**. The temporary modulus has already
been erased. Split construction uses at most four roles, including the temporary
literal constructor. For S=1 the deepest suffix counter is absent. An occupied
entry lease is not one of these eight. A literal fixture attains eight, and a
one-role-short allocator rejects. The kernel allocates **zero numerical words**.
Payload storage is at most V in the two buckets plus V in the output; including
the borrowed source gives 3V occupied payload cells. Count tapes, markers,
retained blank extents and enclosing caller payloads remain separate categories.
This is not a bound on the entire recursive machine's backing capacity.

## Adapter and whole-route accounting

`CarryAdapter` retains PR2915's complete execute lifecycle: source copy,
modulus setup, affine-operation order, intermediate disposal, final bank erasure
and source return. Only translations with a!=1 use the new kernel. All other
operations, including +1, use the original dispatcher. +1 already uses a single
translation pass; retaining it avoids the small setup regression observed at
B=S=1. This is a static opcode selection, not a benchmark-dependent guard.

For compiled operations o_1,...,o_k the whole charge is

    T_new = T_setup_and_return
            + sum_{unchanged o_j} T_original(o_j)
            + sum_{replaced carries a_j} T_rotate(B_j,Q,S_j,I,a_j).

The inherited setup term includes every original input copy, intermediate clear
and high-bank lifecycle. Every swap and reversed-ADD native interval is identical
and fully charged. There is no additional native child or new recursive profile.
We prove the replacement's completed contract and linear cost. We do not infer
an all-domain numerical speed ratio from this big-O statement or finite timings.

Before replacement a positive carry a uses a calls to `translate_one`, whereas
a negative carry uses |a| repetitions of sign/translate/sign, or 3|a| full-field
primitive calls. The new path uses one direct kernel (including both buckets),
with +1 unchanged. The catalogue receipt counts these calls in one precisely
named source specialization. These different primitives have different costs;
that count is neither a runtime ratio nor a κ calculation.

## Verification boundary

The independent oracle maps each input column using host modular arithmetic,
separately from the encoded implementation. Random Boolean values are only an
additional check: the provenance observer propagates a distinct formal column
for every input cell, and a wrong-direction control also fails on all-zero data.
All input bits, old prefixes and suffixes are included. A raw Tape observer
meters setup through complete kernel/route return. Native route intervals are
additionally reported but are not subtracted from totals.

The package checks 96 complete before/after kernel pairs, seven complete route
pairs, 2,056 independently decoded split identities, source pins, cardinality and
ownership restoration, occupied dirty leases, erased buckets, invalid carries,
trailing input and endpoint-preserving extra-traffic controls. Complete selected
GL64 payload execution, supplier admission, whole caller stock and inherited
native/analytic assumptions remain outside this result. No new κ is claimed.

Tekalign (tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
