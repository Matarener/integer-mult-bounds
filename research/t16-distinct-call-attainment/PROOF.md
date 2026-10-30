# Distinct-call attainment of the T16 integer envelope

## The finite problem

Take the exact selected1094 PLAN/SPEC bytes pinned in SOURCES.json. A helper
is an actual pair `(call time, helper index)`, with its listed width. A bin
is `(owner replica, child, port)`. Its capacity and allowed times are the
PLAN window for that owner and child, replicated over all 112 ports.

A feasible assignment places every helper in one allowed bin at a nonnegative
integer offset. Reservations in each bin are disjoint and their union is a
prefix. Within each call, different helpers use different physical families.
No helper uses that call's active data pair. The physical family number is

```text
896*owner + 112*(2*pairs[child] + sides[child]) + port.
```

The objective is the sum of `r^(1-a)` over nonzero bin residuals r. This
problem takes the supplied windows as hypotheses. It does not derive them
from the source program or charge phase charts, native adapters, controller
storage or other physical admission costs.

## The new certificate and sufficiency lemma

Group windows by their exact pair `(capacity, allowed-time set)`. There are
144 groups, each with two windows and therefore 224 physical bins. Retain the
PR3395 pattern allocation. An allocation row a assigns n bins of one pattern
p to one group. Write `c[p,k]` for the number of width-k slots in that pattern.

The new integer certificate gives `y[a,t,k]`, the number of width-k helpers
from call t assigned to allocation row a. The checker verifies:

1. Each group has exactly 224 bins, with matching capacity.
2. `sum_a y[a,t,k]` is the literal width-k helper count of call t.
3. `sum_t y[a,t,k] = n*c[p,k]` for every allocation row and width.
4. y is nonnegative, integral and zero outside that group's allowed times.
5. `sum_k y[a,t,k] <= n` for each allocation row and call.

Condition 5 is the new constraint. The older temporal certificate did not
impose it. In particular, its old/new flows put as many as 331/296 helpers
of a call in one 224-bin group. That observation rejects those particular
flows as physical assignments, not their pattern inventories.

Fix one allocation row with nonempty pattern and multiplicity n. Make a
bipartite multigraph whose left vertices are its active call times and whose
right vertices are the individual pattern slots. Split the width-k demands
among the `c[p,k]` corresponding right vertices until each has degree n.
This is possible by condition 3. Every left degree is at most n by condition
5. Splitting cannot increase a left degree.

There are at least as many active times as slots: total degree is n times
the number of slots, and each active time contributes at most n. Add dummy
slot vertices until the two sides have equal size. Fill their edges to make
every vertex n-regular. Total left and right degree deficits agree, so a
successive deficit-filling construction suffices.

Every nonempty n-regular bipartite multigraph has a perfect matching. For a
set S of left vertices, its n*|S| incident edges end in N(S), whose total
degree is at most n*|N(S)|. Thus |S|<=|N(S)|, and Hall's theorem applies.
Remove a perfect matching and repeat. Equivalently, remove the minimum
multiplicity on a chosen matching in one step and repeat that colour that
many times. The graph decomposes into n matchings. Each matching is one bin.
After discarding dummy edges, each bin has exactly the prescribed width
slots and at most one occurrence of any call time. Empty patterns give n
empty bins directly.

Map these colours to the group's physical bins. For each call and width,
assign its literal helper indices bijectively to the matching's slots.
Place the slots in increasing time order at consecutive offsets. Conditions
1 through 4 prove complete helper coverage, capacity, time eligibility and
prefix disjointness. The matching construction proves distinct times in
each bin.

The source-geometry check proves that at any one time at most one eligible
child belongs to any physical family, and that every eligible child lies
outside the active data pair. Therefore distinct bins within a call imply
distinct physical families, even across groups. Both properties are also
checked directly on every expanded helper row.

## Result and inherited lower bound

The two resulting assignments have residual profiles

```text
old: {1:2431,17:1,48:4887}
new: {1:2429,5:1,14:1,48:4887}.
```

Each uses all 69,120 literal helpers in 144 calls and all 32,256 bins. Both
have residual rank mass 237,024. RESULT.json records hashes of the complete
expanded row sequences. The source-bound inherited `audit_roles` function
also accepted both exported original-schema owner maps, with 480 different
families in every call.

For every real `0<=a<=1/2`, put `p=1-a`. Forgetting times and family identities
maps every feasible assignment to the pooled integer problem. The separately
replayed PR3378 theorem at exact commit
`08da381d84bfc5eda02dad5008ddb00edb9bf9f2` gives the pooled lower bound

```text
min(2431+17^p,2429+5^p+14^p) + 4887*48^p.
```

The two new assignments attain its two branches, so this is also the exact
optimum of the finite hosting problem stated above. At a=0 both costs equal
the fixed residual rank mass. For other parameters, choose the cheaper of
the two separately feasible assignments.

The lower-bound theorem and its 56,987 continuum obligations remain credited
to PR3378 and its predecessor chain. DEPENDENCIES.json pins its proof and
checker; README.md gives its separate replay. The normal replay here proves
the new attainability statement without importing that proof or any solver.
No complete physical admission, supplier or multiplication exponent follows
until the remaining physical costs and inherited interface obligations pass.
