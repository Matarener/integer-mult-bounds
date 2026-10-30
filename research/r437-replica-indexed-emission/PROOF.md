# Replica-indexed emission boundary

This is a finite IR compilation result and a conditional transport lemma. It is
not a physical CALL/RETURN implementation or an all-size multiplication theorem.
All sources are bound in PREDECESSORS.json. New analysis by Chris R / Clear1nsight
with substantial OpenAI Codex assistance, Apache-2.0.

## The first literal obstruction

PR #3959's first move changes stage 6, caller replica 1, helper 421 (local role
643) from absolute family 1097, child 6, offset 0, width 8 to absolute family
209, child 6, offset 16, width 8. The source call is calls[193]. The unchanged
replica-0 helper 421 owner is family 209, child 6, offset 0, width 8.

The selected-bit-node Catalogue._bind guard demands identical routes and
family = replica0_family + 888*replica. Therefore the new family 209 fails the
expected 1097 and its offset 16 fails offset 0. This does not depend on runtime
values, q, precision, or helper initialization. The verifier executes the
retained AST guard, adapting only 661 to 659 exactly as PR #3967 does, and obtains
`replica owner symmetry`. It also checks the unmodified R437 positive control.

Deleting that assertion would be unsound. The same catalogue builds only the
replica-0 requests and multiplies their rank histogram by 32; its semantic key
has no replica component. The pooled profile has 400877 rank 2 residuals and 1 rank 14
residual, which cannot be represented by such a 32-fold histogram. Topology's
idle_family also adds888*replica to one representative request. Thus both the
local-owner domain and physical idle request domain must become replica aware.
This is a limitation of that compressed interface, not a refutation of pooling.

## A completed absolute-owner IR adapter

The new compiler applies each move to exactly one(stage,replica,helper) key and
checks its full old owner record before replacement. No input word, schedule or
move is regenerated. It validates 125856 final helper roles: stage membership in
the destination window; destination family in the inactive pair; width 8 and
coordinate extent; and disjoint occupancy keyed by(child,absolute family).
The source's schedule touches all replicas of each active pair in phase order,
so a window of an inactive pair remains valid for a different caller replica.

Idle records are constructed for each(child,replica,copy), subtracting the
actual occupied prefix from its capacity. These are an explicit replica-indexed
IR invoice; they are not objects accepted by the old physical Catalogue.
The exact delta is the credited PR #3959 delta
{2:+13,6:-1,14:+1,26:-32,42:+19}. The number of paid requests 903456, rank mass
1808352 and maximum child 42 are retained. The halving test2*42^2<64^2 still
holds. All fallback and inherited preparation/native costs remain additional.

The final stream block of retained R437 emit_k.py already reads absolute owners.
We execute that block unchanged on the overlaid calls. It serializes every local
instruction with its literal absolute target/source owner, or the inherited
private centre when the source is the private output. The independently retained
audit_hosted_k.digest function agrees on the complete ordered stream digest and
7814016 event count. Both are predecessor algorithms, not an independent compiler
written for this package. RESULT.json records the number of changed events and
the new digest. The old source stream's digest cannot authenticate the new stream.

## Conditional uniform transport lemma

Let A be any set of coordinate values and I a finite logical register set. Let
j:I→J be an injection into a physical coordinate set, and let E_j identify the
logical values with the coordinates j(I), leaving the complement fixed. For any
local map P:A^I→A^I define its transported map by

    P^j(x)|j(I) = j_* P(j^*x),    P^j(x)|J\j(I) = x|J\j(I).

Then(PQ)^j=P^j Q^j, the identity transports to the identity, and if P is a
permutation then(P^-1)^j=(P^j)^-1. These follow by substituting the restriction
and extension formulas; no value distribution or zero helper hypothesis occurs.
If a local word restores a subset D of dirty logical registers for every input,
its transport restores j(D) for every physical input. Composition preserves this
statement while each call's owner injection is valid and the promised frames
and untouched windows are respected.

For the verified owner IR, active data roles lie in the active pair; hosted roles
lie in inactive pairs and occupy disjoint width 8 cells; the private stream uses
the inherited separate centre. Thus the role-to-slot map is injective at every
local invocation. The lemma proves uniform *abstract slot transport*, conditional
on the inherited local word and the charts identifying those slots. It does not
prove that source access, chart preparation or address routing is free. PR #3980's
unpooled chart-unit and key-separation result does not by itself cover this new
request domain. A chart matrix may change when a move changes the physical port
or pending axes; the new native catalogue must bind that actual chart.

The transport lemma is the categorical composition law for products of register
sets. The occupancy certificate is a network allocation with demands at logical
helpers and capacities at absolute host cells. The pair is useful because it
separates validity of an allocation from functorial compilation and from the
remaining physical realization, without assigning a zero cost to either join.

## Complete scoped obligation ledger

| Obligation | Status | Evidence or remaining work |
|---|---|---|
| Pinned63-move ownership and untouched windows | proved finite | All 125856 roles and destination capacities checked |
| Absolute-address local IR emission | proved finite | Two retained encoders;7814016 events; exact digest |
| Replica-indexed idle IR invoice | proved finite | Every absolute child/family prefix; exact profile |
| Uniform arbitrary-value/dirty-state slot transport | proved conditional lemma | Product-set injection and composition proof above |
| Old compressed physical catalogue compatibility | rejected | First actual move and non32-divisible histogram |
| Replica-aware native source identifiers and chart keys | unknown | Must include actual caller/owner information |
| Whole native forward/backward residual execution | unknown | No production constructors or residual body executed |
| Physical CALL/RETURN, source reads and consumers | unknown | No pooled physical gate or returned payload executed |
| Address routing, stock, parking, restoration, visited cells | unknown | No free renaming/SWAP assumption and no new upper bound |
| All-size, SOURCE, correlated hosting, field/cover and precision joins | inherited unknown | Not discharged by this finite package |
| Full dual-supplier κ improvement/admission | unknown | No new numeric claim; selected record unchanged |

The bounded next decision is one actual cross-replica source code and physical
CALL/RETURN with its complete accounting. Repeating a controlled unpooled payload
or re-pooling the same63 moves would not discharge it.
