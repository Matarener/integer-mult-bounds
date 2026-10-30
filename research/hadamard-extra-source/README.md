# A 208-primitive signed Hadamard connector

This contribution was produced by Nick Petalas. Apache-2.0.

An explicit exact construction reduces the signed four-source/four-output
Hadamard batch from the cited 222 primitive calls in Cinna Davis's
[PR #1158](https://github.com/CrocSwap/integer-mult-bounds/pull/1158) to
**208**, a saving of **14**. The new word has 22 complete top-level queries,
62 internal echo nodes and four dirty scratch rows. The cited comparator
has 24 queries, 66 echo nodes and the same four dirty rows. Its result is
used as a predecessor, not audited or replayed here.

The change is two additional restoring queries on the cheapest source.
They permit four fewer readouts on the first output. This leaves the
predecessor's exactly-eight-source-call class, so it does not contradict
that class's optimum. The claim is an exact finite construction with a
scoped algebraic proof. Neither unrestricted optimality nor a new kappa
is claimed.

## Contract

There are four read-only sources x_j, four distinct accumulating outputs y_i,
and an arbitrary dirty connector z. For exact additive linear maps A_i,B_j,
the permitted queries are

```text
source j, sign s:  z   += s B_j x_j
output i, sign s:  y_i += s A_i z             s in {-1,+1}.
```

Maps need not commute. Each query restores its private workspace and every
source it reads. Outputs cannot be borrowed as workspace. The target is

```text
y_i += sum_j H_ij A_i B_j x_j,
H = [ 1  1  1  1 ]
    [ 1 -1  1 -1 ]
    [ 1  1 -1 -1 ]
    [ 1 -1 -1  1 ].
```

All row numbers below are zero-based. All rows have a common compatible
module or vector-space dimension. The identities use only addition,
subtraction and composition, so the proof works over any commutative base
ring with exact linear maps. Rounded or nonlinear children require a
separate contract.

## The word and proof

Execute the following ten source events in order. A symbol +j or -j means
a signed source query, not a scalar operation assumed free.

```text
-0, -1, +0, +3, -2, -3, +1, +0, -0, +2.
```

Let q_t be the source-coefficient vector in z after t source events.
Initially q_0=0, and z=z_initial+sum_j (q_t)_j B_j x_j. The complete path is

```text
t:      0    1    2    3    4    5    6    7    8    9   10
q_t[0]: 0   -1   -1    0    0    0    0    0    1    0    0
q_t[1]: 0    0   -1   -1   -1   -1   -1    0    0    0    0
q_t[2]: 0    0    0    0    0   -1   -1   -1   -1   -1    0
q_t[3]: 0    0    0    0    1    1    0    0    0    0    0
```

Insert these readouts at their indicated source-prefix visits:

```text
output 0:  +A_0 z at t=10 and t=4; -A_0 z at t=2 and t=6
output 1:  +A_1 z twice at t=3;    -A_1 z at t=1 and t=5
output 2:  +A_2 z at t=8;          -A_2 z at t=4
output 3:  +A_3 z at t=5;          -A_3 z at t=1.
```

Readouts at a common visit can be executed in either order because they
write distinct outputs, or repeatedly add the same source value. The two
positive output-1 calls are both paid. No doubling instruction is free.

For each output the signed coefficients of z_initial sum to zero. The
remaining source coefficients are exactly

```text
q_10 - q_2 + q_4 - q_6 = (1, 1, 1, 1)
2 q_3 - q_1 - q_5      = (1,-1, 1,-1)
q_8 - q_4              = (1, 1,-1,-1)
q_5 - q_1              = (1,-1,-1, 1).
```

Linearity therefore proves the desired map without exchanging the order
of A_i and B_j. Also q_10=0, so z restores exactly. Source queries never
write x, and readouts only accumulate into y. Initial output values are
preserved additively. This proves the complete arbitrary-input endpoint.

## Every child and inverse is charged

Use the predecessor's fixed product lengths

```text
A lengths = (2,3,4,5),    B lengths = (1,2,3,4).
```

Factors are listed in application order. For a product with n factors,
split the first b=floor(n/2) from the last a=ceil(n/2), so the operator is
A B. A positive product query is the literal dirty echo

```text
u += B source;  target += A u;
u -= B source;  target -= A u.
```

Its negative is the complete reversed word with all signs negated.
This restores arbitrary u and implements the product in its original
order. Descendant scratch excludes both active rows and all ancestors.
The written induction proves the lowering at every finite dimension.

The primitive and internal-node recurrences are

```text
C(1)=1, C(n)=2 C(b)+2 C(a),     C(1..5)=(1,4,10,16,28)
I(1)=0, I(n)=1+2 I(b)+2 I(a),   I(1..5)=(0,1,3,5,9).
```

The new source profile is (4,2,2,2), costing
`4*1+2*4+2*10+2*16=64` primitives and 18 echo nodes. The output profile is
(4,4,2,2), costing `4*4+4*10+2*16+2*28=144` primitives and 44 echo nodes.
Thus the literal program has **208 primitives and 62 echo nodes**. There
are ten source queries and twelve readouts. The largest child has length
five and uses three private dirty rows; including z gives four dirty rows.
The verifier expands every call and checks these counts directly.

Under the predecessor's complete-cost notation, price a primitive by E,
an echo node's extra control by D, a complete query dispatch by Q, and
all remaining preparation/placement costs by P+R. The new complete bill is

```text
208 E + 62 D + 22 Q + P_new + R_new.
```

Against the cited comparator, the benefit survives precisely when its
additional P+R expense is less than `14 E + 4 D + 2 Q`. This charges extra
source calls and every child/inverse. It does not assert that physical
layout or precision makes P and R equal. The same 24 distinct factor maps
are used; no new coefficient oracle is supplied.

## Evidence and reproduction

From the worktree root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/hadamard-extra-source/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/hadamard-extra-source/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/hadamard-extra-source
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/hadamard-extra-source --check-source-history
```

Another CPython 3.12 installation may replace that interpreter path.
Expected markers are `PASS_HADAMARD_EXTRA_SOURCE`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The source-history check requires committed package bytes and full history.

The verifier checks the formal query endpoint with independent A/B symbols,
then expands all 208 leaves and checks the endpoint with independent
noncommuting primitive symbols. Both include every input role and all
four arbitrary dirty rows. Separate dense matrix execution checks all 24
basis inputs and two dense inputs for each of four factor assignments,
104 input cases in total. Every case also runs the complete literal inverse.
There are 25 rejection controls: deleting each of 22 top-level calls,
deleting the final primitive restoration, changing one target sign and
aliasing the active registers. Checks use explicit exceptions and remain
active under optimized Python. Generated stdout receipts bind all five
package files by SHA256. No receipt is handwritten.

A bounded proposal search with deterministic seed 1158 found this word on
its tenth path and stopped immediately. Only the witness, its proof and
standalone verifier are part of the result; no census or optimality claim
is made. No predecessor scientific executable is imported or replayed.

## Scope, provenance and credit

Scientific base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8. The selected
baseline passed its source-binding check only. This is a historical
recursive-interface side result, explicitly changed from the
`bit-new-register-model` card. It does not supply a native larger-register
BIT program, current caller or selected-supplier improvement.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19220061)
names the additional-source boundary. Live PRs, this account's recent PRs,
handoffs, active Discussions, local reservations, all-main README terms,
targeted merged PRs and the overlap helper were checked. Sparse local notes,
arbitrary historical diffs and unpublished work are not fully covered.
[SOURCES.json](SOURCES.json) binds predecessor proof text as historical
provenance. There are no external runtime inputs.

Credit Cinna Davis / 1337isnot1337 #1158 for the exact eight-source-call
census, weighted envelope, 222-primitive comparator and explicit excluded
boundary, and #997 for the signed Hadamard batch. Retain Martin #1088,
Jerry Chen / CubeJerry #889, Ross Richardson #934/#943/#944 and Chafik
Boukhalfa #628 for the weighted-repair, connector and dirty-echo lineage.
Their results are cited, not claimed as new. All predecessor files and
credit lines are unchanged. The new material is the ten-source word,
its 208-primitive lowering and exact verification.

Native realization, physical routing, precision/error propagation, stock,
complete supplier admission and the multiplication theorem remain unproved.
No Lean, Docker or selected scientific cold replay was run. Independent
human and formal proof-kernel review are unclaimed. Selected kappa is
unchanged.

## Open next questions

1. What is the least weighted query price with arbitrary restoring source
   multiplicities for this fixed Hadamard target? Begin with this word as
   an upper bound and derive a lower bound that charges each source
   separately. Unbounded integer paths need a completeness argument;
   bounded sampling does not provide one.
2. Can one actual physical caller retain the saving after all layout and
   precision costs? Bind that caller and compare its additional P+R cost
   with `14E+4D+2Q`. No such caller is supplied here.

The structured questions, relevance and blockers are in TASK.json.

## Verifier bounds

The verifier has no recursion, subprocesses, network access or write path.
Functions are at most 37 physical lines. The formal pass has at most 208
calls, 12 registers and 2,048 retained monomials per destination. Lowering
has a 512-iteration guard and depth three. Dense execution has exactly
104 fixed inputs of 24 scalar coordinates and at most 208 steps per pass.
Receipt reads are limited to 128 KiB plus one guard byte per fixed file.
Normal/optimized warning-strict runs and in-memory source compilation
provide the available Python diagnostics. No external analyzer was run.

Power of Ten rule 3 needs a managed-runtime deviation: CPython allocates
objects dynamically. The fixed call, dimension, polynomial and read limits
bound this terminating verifier's live collections. Internal integers have
no fixed machine width; the input fixtures and finite operation count bound
their growth. No allocator-internals or fixed-memory runtime claim is made.
The literal inverse is the reverse of a finite 208-step list. The direct
call graph is acyclic and all failure checks propagate as exceptions.
