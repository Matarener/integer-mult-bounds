# First-variation gate for parameterised centre sharing

Clear1nsight, substantial OpenAI assistance. Apache-2.0.

## Exact contract

Retain the selected 144 local calls, complete scalar words, paired bridges,
all ordinary outputs and signed terminal exchanges. As in PR2622/2763,
project climbs, adapters, idle factors and address translations to identity.
Replace each of the 1,152 centre actions on its private scalar by multiplication
by z. Also test the version with z at forward calls and z^(-1) at backward
calls. The parameter varies near 1. A replacement must agree as a rational
function family, not just at z=1 or a root of unity.

This changed scalar oracle contract is NOT the fixed native Fourier operator.
The theorem below cannot be used as a native recursive-call lower bound.

## Time-expanded sheaf and derivative theorem

A finite causal linear circuit has states x_t and constraints
x_(t+1)=M_t(z)x_t, input injection J and final projection P. It can include
fixed linear recoding, extra finite workspace, copies and singular clears.
Its boundary transfer is

    F(z)=P M_(s-1)(z) ... M_0(z) J.

Assign state-space stalks to the chronological vertices and coordinate
compatibility restrictions to edges. Global sections are exactly legal linear
traces. Causality gives a unique trace for each input. This time-expanded
sheaf language describes compatibility, not a free implementation of elimination.

The product rule at z=1 gives

    F'(1)=sum_t P M_(s-1)(1)...M_(t+1)(1)
                    M'_t(1) M_(t-1)(1)...M_0(1) J.

If charged gates have derivative ranks r_t and every free operation is
independent of z, rank subadditivity gives

    rank F'(1) <= sum_t r_t.

Each scalar-register multiplication by z or z^(-1) has derivative rank one.
Thus q such oracle calls imply rank F'(1)<=q. This holds for arbitrary fixed
linear causal recoding and finite workspace, including arbitrary dirty values
held fixed when varying payload inputs. Invertibility of every intermediate
operation is unnecessary. A parameter-independent coordinate change cannot
alter the required boundary derivative. A gate on d independent coordinates
may have derivative rank d and must not be counted as a single scalar query.
Nonlinear/adaptive branching and parameter-dependent free maps are not covered.

## Application to the selected projected schedule

At z=1, let C contain the actual chronological centre-input covectors and B
the final response columns to additive centre-output perturbations. C has
shape 1152-by-14336, and B has shape 14336-by-1152. The baseline complete
ordinary endpoint is identity. With Sigma diagonal, all +1 or signed by call
orientation, the product rule is equivalently

    F'(1)=B Sigma C.

PR2622/2763 already establish full source-history rank, and PR2622 establishes
full final-error-response rank. Those are credited predecessor results.
The new verifier reconstructs both from the pinned selected archive without
importing predecessor executable code. Full modular ranks at two primes,
with opposite pivot conventions, certify their rational ranks as 1,152.
C is therefore surjective, B injective and Sigma invertible. Hence

    rank F'(1)=1152.

Combining this with the derivative theorem proves that any replacement in
the declared parameterised linear oracle class needs at least 1,152 scalar
oracle gates. Halving to 576 is impossible in this class. This is a gate on
generic temporal sharing, NOT a complete supplier rejection or native tariff.

The source-bound implementation independently derives all local endpoints,
chronological source rows, final response columns and the complete ordinary
baseline identity. A separately coded full dual-number interpreter over
Q[epsilon]/epsilon^2 checks both derivative sign conventions on dense signed
rational initial data. Each literal run retains 2,835,792 scalar instructions
and all 1,152 centre occurrences; every final ordinary field and private clear
must agree. This interpreter shares the input parser but calls none of the
primary local, bridge or endpoint routines. The dense checks support code
correctness; the rank/product-rule argument establishes the all-input result.

## Fixed-operator escape and essential limitations

The derivative concerns nearby parameters. A fixed native operator may obey
special algebraic identities that no generic z obeys. For example, n independent
coordinates transformed four times give F(z)=z^4 I_n and rank F'(1)=n. Under
the discrete condition z^4=1, the same fixed output is identity and uses zero
oracle calls. Consequently the generic lower bound cannot be transferred to
a finite-order native transform. The tests execute this counterexample.

A claimed free operation z I_n is another counterexample to dropping a premise:
it supplies derivative rank n with no charged query. Fixed source/readout
changes, weaker required endpoints, nonlinear algorithms, different native
primitives and actual higher-dimensional oracle gates also require a new model.
The all-output condition matters, including helper restoration. The theorem
does not silently replace the native endpoint by a source-only observation.

Eight generic test groups exercise product-rule ranks for noncommuting words,
a tight full-rank example, singular clears, coordinate changes, lost outputs,
fixed-operator and parameter-dependent-free-work counterexamples, and actual
missing/corrupt source loader rejection. Both normal and optimised modes are
registered. No independent human or formal proof-kernel acceptance is claimed.

## Decision and next question

NARROW to this exact generic scalar contract. A time-expanded sheaf alone
cannot remove work required by its boundary derivative. The useful constructive
escape is now explicit: bind one native fixed-operator identity that fails the
generic z model but preserves the complete required dirty-input endpoint.
Then charge source access, frames, chronological lifetimes, restoration,
precision, hosting and the complete recursive invoice. Those costs remain
unknown here, not zero. No paid profile, supplier or selected kappa changes.

## Credit and overlap

Sagar Thakrar/PR2199, after Adam Gall/PR1918, ywz65/PR2622 and the separate
bridge-source audit PR2763 supply the projected source/response lineage.
Tekalign/PR2814, after Arham Tahir/PR2799, already uses causal feedback and
operator derivatives for terminal-Y error kernels; this package instead bounds
the complete input/output derivative against fixed linear causal recoding.
PR3151 and PR3194 retain their distinct circle/history obstructions.
David Charbonneau/PR3147 supplies the research direction. Matarener/PR3656 and
Ross Richardson/PR3797 retain the block and independently established full-kernel
result; our PR3828 is not repeated. Retain Rohan Arun, Jeremy Kothe, Hao Yan,
Aaron Wang/navinor and all selected native/compiler source attribution.

The sheaf viewpoint uses established local-to-global linear algebra, including
Hansen and Ghrist, Toward a spectral theory of cellular sheaves (2019),
DOI10.1007/s41468-019-00038-7. The product rule and rank inequality are elementary.
No priority claim for temporal sheaves or generic oracle lower bounds is made.
Separate implementations share the author and source. No agent-spawning tool
was available in this session, and no multi-agent execution is claimed.
