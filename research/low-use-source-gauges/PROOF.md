# Restored gauges have a sharp source-use threshold

This is a scoped scalar-cost theorem. It answers the low-use part of the
coupled source/target question in Dugongue's PR #4518. Its native word and
its target-only interval theorem are predecessor work, not replay targets.

## Model

Let X be a finite collection of sources and Y a disjoint collection of
targets. Every field starts with arbitrary data. Fix a list of nonzero
dyadic contributions, indexed by e,

    Y_t(e) <- Y_t(e) + q_e X_s(e),    q_e = o_e 2^v_e,

where o_e is a signed odd integer and v_e is an integer. Parallel list
entries count separately. Each listed contribution executes exactly once,
in any order. No other ADDs, role mixing, scratch, or factorizations are
allowed. Sources never receive contributions. Targets never supply them.

Each role may undergo any finite sequence of positive power-of-two SCALEs.
Its integer gauge starts and ends at zero. With current source and target
gauges a_s and b_t, the physical ADD coefficient must be

    q_e 2^(b_t-a_s).

SCALE by 2^h costs 2|h|. The retained #4518 tariff for a nonzero ADD is

    c(o) + 2|v|,    c(o) = 2(2 + bit_length(|o|) + popcount(|o|)).

Thus the charged cost of a schedule is

    C + 2 sum_roles TV(g_role)
      + 2 sum_e |v_e + b_t(e) - a_s(e)|,                 (1)

where C=sum_e c(o_e). Gauge paths have zero endpoints, and TV includes both
entry and return. Nothing is assumed zero initially. The representation
invariant is X_stored=2^a X_initial and
Y_stored=2^b(Y_initial + sum of completed logical contributions).
It proves exactness of every schedule in this model and full dirty return.

## Theorem 1: remove every source used at most twice

For any schedule, erase all SCALEs of a source s used d_s<=2 times, leave
every other gauge path and the ADD order unchanged, and adjust its ADD
coefficients to the displayed representation invariant. The new schedule
has the same exact endpoint and costs no more.

Proof. Let M=max|a_s| over that source's complete path. Its zero endpoints
imply TV(a_s)>=2M. Erasing its SCALEs saves at least 4M. For each use,

    |v+b| - |v+b-a_s| <= |a_s| <= M.

Consequently its ADD cost grows by at most 2 d_s M <= 4M. Odd parts are
unchanged. The representation invariant proves the endpoint, including the
restored arbitrary source. This argument does not modify any target gauge
or rely on the timing of another source. Apply it to each such source. QED.

The same argument removes a target used at most twice. Interchanging the
two gauge variables only changes a sign inside the absolute value. This
observation is used below for the sharpness family.

## Corollary: an exact optimum with no coupled-source search

If every source has at most two list entries, the minimum over all coupled
source/target paths equals the target-only minimum

    C + sum_t min_(L<=0<=H)
        [4(H-L) + 2 sum_(e:t(e)=t) dist(-v_e,[L,H])].    (2)

Each endpoint can be chosen among zero and the -v_e incident to that target.
The new implication is Theorem 1. The target-only interval formula and its
attaining walk 0 -> L -> H -> 0 are #4518 Theorem 2, used as a cited premise.
Targets are independent when sources are fixed. Serve them consecutively to
attain the sum, with no extra fields and every entry/return SCALE charged.
Formula (2) covers arbitrary finite graph size, odd parts, valuation sizes,
ADD orders and finite integer gauge paths under the model above.

## Theorem 2: three uses are the first possible strict gain

Consider one source and d distinct targets, with every coefficient o 2^v.
For d>=1, the exact coupled optimum is

    d c(o) + 2 min(d,2)|v|.                             (3)

The target-only optimum is d c(o)+2d|v|. Hence for d>=3 and v!=0 the exact
gain is 2(d-2)|v|, and the source-use threshold in Theorem 1 is sharp.

Proof. Remove all target gauges by the symmetric low-use argument. Let M
be the largest absolute source gauge visited. Return costs at least 4M,
and the d ADDs cost at least d c(o)+2d max(|v|-M,0). For M<=|v| the variable
part is 2d|v|+(4-2d)M; for M>=|v| it is at least 4|v|. Minimizing these two
pieces gives (3). With d<=2, use no SCALEs. With d>=2, scale the source to
gauge v, execute all ADDs with coefficient o, and restore it to zero.
These constructions attain the bound. Without source gauges each target
has one contribution, and its return costs cannot improve that direct ADD.

At d=3, o=1, v=-1, the direct/target-only optimum is 30. Scaling the dirty
source by 1/2, executing three coefficient-one ADDs and scaling it by 2
costs 2+3*8+2=28. Every source and target retains its required arbitrary-input
endpoint. This is a scalar allowance gain for this star, not an invoice gain
for a complete supplier. QED.

## Both dual interfaces

Elementwise inverse-transpose dualization in the same execution order sends
ADD(t,s,q) to ADD(s,t,-q) and SCALE(r,2^h) to SCALE(r,2^-h). It gives the
inverse transpose of the full product and preserves every tariff. This is
the classical Levi homomorphism, used in #4518 Theorem 3. The star's dual
is one target receiving -o 2^v from d distinct sources. Both interfaces
restore every gauge and have the same optimum and dirty-state contract.
The finite checker independently multiplies both physical words.

## Scope

This supplies a new source-elimination theorem and an attaining sharpness
family for the declared ADD-once bipartite class. It is not optimality over
general scalar circuits. Repeated use count, source writes, target reads,
borrowing, non-diagonal changes, unreturned gauges, and alternative tariffs
can change the conclusion. The minimum includes a fixed list of ADDs;
coalescing or deleting that list is a separate optimization.

Ali Romman's PR #5824/#5830 already provide optimal signed representations
on different fixed P104 gauge graphs, using exact cuts and flow certificates.
No global gauge-optimization invention is claimed here. No existing native
word, recursive paid/target histogram, physical precision/tape bill or selected
frontier is changed. All five selected framework assumptions remain.
