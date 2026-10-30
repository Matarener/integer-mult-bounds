# Direct-stage search in the minimal-cut path family

The selected candidate has 17 data pairs, cut 8, idle mask
`280378328416255`, and native-stage mask `28633115307`. Stages
`2,4,...,32` are direct rank-one Q shears. The remaining 19 stages use the
audited retimed native supplier from PR #4441 at commit
`ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9`. Its helper profile is
`{4:26,5:2,7:29,8:42,9:309}` and its complete local paid profile is
`{1:2253,2:515,3:445,4:102,5:40,8:8}`. This supplier already includes
the fifteen previously shortened helper lifetimes.

Its raw moment root is approximately `0.003001054183175`. This number is a
discovery estimate. The independent integration package supplies the exact
interval inequality, physical bindings, and inherited transfer obligations.

## Dynamic program

For a controller with p pairs, there are `2p+1` local stages. Fix a cut c
between 0 and p−1. The minimal-cut idle mask retains all middle singleton
windows, the c initial windows, and the p−1−c terminal windows. Before
specialization, the main output monomials are two copies of each of:

* prefixes `[0,...,2j]`, for `1<=j<=c`;
* suffixes `[2p−2j,...,2p]`, for `1<=j<=p−1−c`;
* the full stage interval `[0,...,2p]`.

Each copy corresponds to 112 physical fields. For a binary choice of native
stages, an output interval containing n selected stages has productive
width `1+8n`. A retained idle interval containing n selected stages costs
224 children of width `8n`, and disappears when n is zero. Each native
stage contributes the same local paid and helper histograms. Each direct
stage contributes 112 rank-one children and no native helper outputs.

At a test exponent tau, write `f(r)=r^tau`, with `f(0)=0`. A left branch
of length c is processed from the outer endpoint toward the central stage.
Before its j-th even stage, let t be the number of native stages already
selected. Selecting that even stage with bit e contributes

`224 [ f(1+8(t+e)) − f(8t) − e f(8) ]`.

The first two terms are the paired productive prefix and idle prefix. The
last term prices the middle singleton. The following odd bit changes only
the native count used by subsequent terms. Thus the sufficient branch state
is its current native count; the program stores the best score and one
realizing mask for each count. The right branch is the reflected recurrence.

The two outermost positions of a nonempty branch have identical membership
in every relevant output and idle interval. Their individual bit order has
no effect on the invoice: only their total count 0, 1, or 2 matters. The
implementation therefore keeps `01` as a representative of the one-selected
case and omits the equivalent `10`. This is an equivalence of these profiles,
not an assertion that the two physical native placements are identical.

For branch counts nL and nR and central-stage bit m, let n=nL+nR+m. Their
remaining shared score is

`n [112 + helper_moment − local_paid_moment] − 112(2p+1) + 224 f(1+8n)`.

The first terms charge native versus direct local stages; the last term
is the full-interval productive output. Enumerating the two branch counts,
the central bit, and all cuts therefore covers every direct/native stage
mask in this minimal-cut path family, up to the stated outer-bit equivalence.

## Search scope and numerical limitations

The floating-point dynamic program was run for every p from 1 through 120,
every cut, and every native-count state at test kappa `0.00300106`. Its best
candidate is the p17 profile above. The same controller had previously been
selected using the fifteen-tail-pruned supplier. The new run replaces the
complete local helper and paid histograms before scoring every candidate.

This is not a proof of global optimality. It does not cover arbitrary idle
masks outside the minimal-cut family, other controller topologies, new
native suppliers, or every p beyond 120. Floating comparison of dynamic
programming scores is a discovery procedure. The positive p17 result is
certified separately using exact rational Laurent identities and exact
integer histograms, followed by the integration package's interval tests.

## Reproduction

Run from this directory:

```sh
python direct_stage_dp.py --max-p 120 --kappa 0.00300106 --summary --out SUMMARY-120.json
python ../controller/make_direct_case.py --source-root /path/to/integer-mult-bounds
```

The controller builder authenticates the attributed controller and rational
algebra source files. It reconstructs and factors the full complex controller
over the rational Laurent ring, substitutes the direct-stage variables by
one, and checks every specialized coefficient with the same exact scalar
boundary factors. A wrong backward sign fails this check. It independently
reconstructs the binary monomial factor only to cross-check the integer
width histogram; the complex acceptance check retains both Q and Q inverse.

The exact specialized receipt is `../controller/P17-DIRECT-CASE.json`. The
unspecialized receipt is `../controller/P17-FULL-LAURENT-CASE.json`. Sparse matrix
multiplication in the builder omits zero summands but retains exact rational
arithmetic throughout.
