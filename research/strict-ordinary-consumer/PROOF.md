# Strict padding in the complete ordinary consumer

Fix integers q>=2, k,w,n>=1 and 0<=ell<w. Put R=q^k, M=q^w,
A=M^n and J=q^ell. Let P,Z,T be positive complete spectator extents.
The original payload has order

```text
[P][H_hi:R][H_body:A][H_rem:J][Z][D_hi:R][D_body:A][D_rem:J][T].
V=P R^2 A^2 J^2 Z T.
```

Let S be positive compatible stock with S<2R. The executable routine uses
PR2808's canonical numerical/Count tapes and primitive contracts. Its strict
padding inputs, including the computed complete body extent, must fit
PR3503's 4096-bit Count capacity. Numerical arenas retain their own capacity
contracts. The mathematical endpoint argument below has no bit-capacity bound.

## Required completed callee

For Rprime=ceil(R/S)S, the callee takes a complete borrowed input with order

```text
[P][Rprime][H_body][H_rem][Z][D_hi:R][D_body][D_rem][T].
```

It preserves the borrowed input and its Counts, restores all heads, returns a
distinct owned output and closes its work before returning or raising. Its
endpoint fixes P, each fresh-row ordinal, H_rem,Z,D_hi,D_rem,T pointwise.
Within each row it applies F_I(H,D)=(C D,C H), where C reverses the n atom
coordinates. This is the unweighted endpoint. Involutivity alone does not
supply this contract. In particular, an arbitrary weighted reversed endpoint
cannot replace F_I.

These are semantic premises. Zero-added-output checks alone cannot prove
them. The routine does not accept arbitrary dirty in-place padding. All added
rows belong to fresh owned input/output fields.

## Each return is restricted before another ordinary operation

PR3503 proves R<=Rprime<2R exactly when S<2R. For R<S, its encoded adapter
returns Rprime=S and added=S-R. For R>=S it delegates to the unchanged
PR2786 planner. Both cases use the same retained complete row scans.

For each prefix, those scans append added zero rows after the R genuine rows.
The completed callee preserves each row ordinal and permutes coordinates
within it. Hence each added row remains zero. Restriction retains exactly
the R genuine rows in order and checks every added output bit is zero. It
returns an owned payload of volume V and erases the padded input/output.
Each call's volume is Vprime=V Rprime/R<2V.

The new body routine calls this complete adapter twice. It acquires the
restricted result before proceeding to the next body operation. The second
padding therefore starts from R genuine rows again. The two calls reuse
stock sequentially. No row multiplication across calls occurs.

Only the call's first fresh-row field grows. The other high field remains
the genuine R-valued D_hi spectator, so gap=J Z R throughout the body.
The prefix for body operations remains P R, and suffix=J T. Replacing
D_hi by Rprime would change the source rectangle and the primitive extents.

## Full chunk endpoint

First exchange H_rem,D_rem when ell>0, retaining their original positions in
the ordered layout. PR2808's body coordinate i then uses

```text
before_i=P R M^i,
middle_i=M^(n-1) J Z R,
suffix_i=M^(n-1-i) J T.
```

The same exact extents serve every ordinary body stage. The endpoint sequence
is the retained two-call identity

```text
D-=H; F_I; D+=H; F_I; D=-D; D+=H.
(H,D-H), (C(D-H),CH), (C(D-H),CD),
(D,D-H), (D,H-D), (D,H).
```

Additivity and C^2=I prove every displayed equality over the atom ring. The
padding/restriction argument makes each F_I the required genuine-row endpoint,
including the new R<S domain. The high-field swap finally uses before=P,
middle=A J Z and suffix=A J T. All fields of each original chunk, including
its residual and high fields, have exchanged. P,Z,T and every other complete
spectator retain their ordinals.

This proof inherits the retained primitive implementations and the stated
completed-callee contract. It extends PR2808's composition to PR3503's wider
row contract. The underlying ordinary identity and strict-volume theorem
belong to those predecessors.

## A newly admitted complete toy invocation

Take q=2, e=5, w=1, m=2, r=1, W=Q=1. The one-family GL2(F2) toy has
b=|GL2(F2)|=(4-1)(4-2)=6. Let D(n)=0 for n<2 and
D(n)=1+D(floor(n/2)) otherwise, with S_0=1 and S_d=6^d.
Legal borrowing has 2k<5 and body=5-k>=2, so k is 0,1 or 2.

```text
k    body    depth    R    S    covering R>=S    strict 2R>S
0       5        2    1   36    false             false
1       4        2    2   36    false             false
2       3        1    4    6    false             true
```

Thus this toy profile has no legal covering plan, but its least strict plan
has k=2, n=3, R=4 and S=6. The new consumer executes both retained source
Node/Driver calls on six padded rows and restricts each to four genuine rows.
The complete original binary interchange has 2^5 * 2^5=1024 input columns.
The source check verifies all of them and all 1536 columns of each padded
call. Each source call is checked separately, so two wrong calls cannot
cancel silently at the final endpoint. This is an executed toy consumer of
the changed contract, rather than just the selector's arithmetic feasibility.

The code also executes the retained n=2 toy on R=4,S=6. That endpoint is
valid but has e=4 and 2k=e, so it is not a fitted near-half borrowing example.
Neither q=2 toy is in the selected large odd-prime GL64 domain. The toy's
opaque coefficient-program token does not execute serialized coefficient
program syntax. The checker does not run the encoded selector; the small
table above supplies its exact independently visible arithmetic.

## Complete added invoice and ownership

All previous charges remain. Using complete primitive costs, the chronological
invoice is

```text
3n ADD(V,M) + n NEG(V,M) + (k+ell) DIGIT_q(V)
+ 2 F_I(Vprime) + 2 PAD_RESTRICT(V,Vprime)
+ encoded admission/setup and intermediate-output disposal.
```

Each PAD_RESTRICT retains PR2786's payload traffic of 4V+8Vprime+12 reads,
V+3Vprime writes and 4V+8Vprime+16 unit moves. Binary control is additional.
The new admission copies and doubles R, then compares S with 2R on encoded
tapes before payload access. It uses a constant number of Count roles and
O(log(R+S)) binary work. For R<S the retained strict planner's additional
setup is O(log S) with constant roles. The old-domain planner still has its
unchanged R-row scan cost. No unknown callee or physical cost is zeroed.

The same conservative outside-callee live-payload bound 8V follows from
PR2808's layout and Vprime<2V. During a callee the bound is
3V+L_F(Vprime), where L_F includes the padded input, returned output and
callee-owned state. Metadata and cleared backing capacity remain separately
charged. This is not a Python heap or total physical-reserve measurement.

Every wrapper pass preserves its borrowed input and returns fresh owned
output. Replacement clears only prior owned outputs. Each complete adapter
clears its padded input, returned output and Counts on success or completed
callee failure. Enclosing cleanup clears the current owned body/remainder
result and closes its shape Counts. The original source is never cleared.
The tests inject failure at both completed-callee entries, including after
the first restricted return. They do not prove arbitrary allocation failure
or interrupted cleanup inside inherited numerical primitives.

## Remaining admission boundary

An actual selected producer coefficient, selected GL64 payload, physical C0
refinement, encoded selector-to-consumer transfer, full-cover and root fresh
fields, completed leaves, every child, row/spectator restoration, routing,
precision/tape costs and outer transfer remain obligations. This local
composition and its newly admitted toy do not establish a supplier, cutoff,
kappa gain or complete multiplication theorem. Author-written proof is
distinct from independent human or formal-kernel acceptance.
