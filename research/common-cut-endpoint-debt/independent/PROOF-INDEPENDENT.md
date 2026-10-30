# Heterogeneous path support and an exact sharp expansion

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.

This is an all-parameter written support argument and an independently checked
finite Gaussian operator example. The example uses a stated formal path alphabet;
it is not a normalized OPEN caller, a dirty-helper circuit, or a new multiplication
bound. The checker uses only Python's exact rational arithmetic and does not import
the historical Clifford compiler or either companion checker.

## The heterogeneous necessary condition

Let a target matrix on `N` address bits have all `2^N` entries nonzero in each row.
Suppose it is expressed as a finite sum `U = sum_j a_j U_j`, where each scalar
`a_j` is nonzero and every row of `U_j` has at most `2^{r_j}` nonzero entries.
For every row, the support of the sum is contained in the union of the summands'
supports. Consequently

`2^N <= sum_j 2^{r_j}`, or equivalently `sum_j 2^{-D_j} >= 1`,

where `D_j = N-r_j`. Cancellation cannot enlarge this union. No Clifford,
unitarity, tensor-product or phase hypothesis is needed for this argument.
The sharper row-specific statement uses each summand's actual row support in
place of its maximum. If `N=mf` and `D_j=d_j f`, this gives the requested
`sum_j 2^{-d_j f} >= 1`. The raw-deficit version also applies to paths whose
deficits do not divide by `f` to an integer.

For the historical common-two/disjoint-fresh-five unary current-cut model, the
companion endpoint theorem supplies `D_j >= 4f` for a C port or `D_j >= 2f` for
an A/B port. That theorem is an upper bound on each individual path's support.
The present argument converts *individually established*, possibly different,
support bounds into a necessary condition on their sum. It does not establish a
deficit for a changed caller or a forward full-native lineage.

## A strictly stronger test and the equality case

Write `d_min = min_j d_j`. The uniform bound retains only
`K >= 2^{d_min f}`. It can pass when the heterogeneous bound fails. For example,
at `f=1`, two paths with deficits `1,2` satisfy `K=2`, but their support mass is
`1/2+1/4=3/4`. They cannot sum to a full-support target. Similarly, fifteen
deficit-four paths and one deficit-five path meet the coarse sixteen-path count
but have mass `31/32`.

More generally, if `K=2^{d_min f}` exactly, even one path with strictly larger
deficit makes the mass less than one. If the heterogeneous mass equals one and
the target has full support, every path must attain its support upper bound in
every row and those supports must be pairwise disjoint in every row. Indeed,
both inequalities in

`2^N <= |union_j support(row_i U_j)| <= sum_j |support(row_i U_j)| <= 2^N`

must be equalities. This gives a useful rejection criterion for overlap even at
the sharp mass threshold. Disjoint full coverage still does not establish the
required coefficients or phases; exact operator comparison remains necessary.

## A sharp example in a declared formal alphabet

The allowed factors here are positive Gaussian native gates
`C_x = a I + b X_x`, translations `X_x`, and nonzero Gaussian dyadic scalars
outside each path, where `a=(1+i)/2` and `b=(1-i)/2`. Distinct address bits `x,y`
give the exact identity

`C_x C_y = a C_x + (1/2) X_y - (i/2) X_x X_y`.

It follows by expanding the left side and using `ab=1/2`, `b^2=-i/2`.
The three path operators have row supports `{0,x}`, `{y}`, and `{x+y}`, respectively.
These are a disjoint partition of the four translations. Their native ranks
are `1,0,0`, hence their raw support deficits on two bits are `1,2,2` and their
support mass is exactly one. All factors retain their actual Gaussian phases.
Each factor is invertible; the scalar coefficients are outside the path operators.

Tensor this identity on `f` disjoint pairs `(x_t,y_t)`. A word in `{A,B,C}^f`
selects `C_{x_t}`, `X_{y_t}`, or `X_{x_t}X_{y_t}` on each pair. If the word has
`k,u,v` occurrences, its scalar is

`a^k (1/2)^u (-i/2)^v = (1+i)^k (-i)^v / 2^f`.

Its row support has size `2^k`, its positive-native rank is `k`, and its raw
support deficit is `2f-k`. The product supports form a disjoint partition of
all `4^f` translations. Tensor distributivity proves the exact identity for
every integer `f>=1`. Thus this is an all-`f` equality example for the raw-deficit
condition; the normalized deficits are `d_j=2-k/f`.

## The precisely limited path invoice

In the displayed *unshared formal expansion*, the number of rank-`k` paths is

`H_k = binom(f,k) 2^{f-k}` for `0<=k<=f`.

There are `3^f` paths, of which `2^f` are monomial and `3^f-2^f` have positive
native rank. The rank mass is `sum_k k H_k = f 3^{f-1}`. The support mass is

`sum_k H_k 2^{k-2f} = 4^{-f}(2+2)^f = 1`.

These counts price native ranks of the stated unshared path products. They are
not a lower bound on circuits that share partial products. They also omit the
costs and contracts for path coefficients, accumulation, source access, physical
scans, dirty workspace, copying, and restoration. The example does not discharge
any of those obligations and is not asserted to be an admitted OPEN supplier.

## Exact finite verification and adverse controls

`check.py` independently constructs each path kernel from its three local letters.
It constructs the target directly from the coefficients of all `2f` positive
native gates, without using that decomposition. For `f=1,2,3`, it compares every
ordinary input/output entry: `16+256+4096=4368` exact Gaussian rational entries.
It also checks complete per-row support partitions, all path coefficients, and
the full rank histogram. The receipt retains every kernel and full output matrix.
There are no private registers in this formal example; the complete basis has
exactly `2^{2f}` columns, and no dirty-workspace claim is inferred from it.

Six adverse cases execute the same predicates used by positive acceptance:

- Omitting the last one-pair path passes the coarse two-path bound but fails
  the heterogeneous mass guard at `3/4`.
- Repeating a monomial path has mass one but fails the support-partition guard.
- Conjugating the last scalar phase preserves support and fails the full operator.
- Replacing a positive native factor by its adjoint preserves support and fails
  the full operator.
- Reusing only three uniform tensor words at `f=2` fails support mass at `3/8`.
- Adding a cancelling positive/negative pair of rank-one paths preserves the
  complete endpoint but fails the displayed unshared path invoice.

Each case must reject at its exact named guard, and the same production predicate
accepts when only that guard is disabled. These deletion checks isolate predicate
sensitivity; they do not claim that deleting that predicate would bypass every
other independent obligation. Term permutations and opposite scalar/operator
phase gauges are accepted as positive controls. Normal and optimized executions
must produce identical full receipts.

## Limits of the historical endpoint claims

The exact telescoping/support theorem quantifies over every length for which the
displayed ordered relay expression is supplied. The retained free noncommutative
caller certificate is the B1, `L=3` case; it is not a construction of every such
caller. Likewise the all-odd-length terminal-invoice contradiction is conditional
on its stipulated stock, call and direct unary completion profile. A generic
`L=1` endpoint operator is not a physical B1 caller.

For arbitrary monomial insertions, the endpoint need not be Clifford. A separate
unary completion lower bound uses row-support submultiplicativity: a rank-`r`
native child contributes at most `2^{rf}` to support. No binary Clifford rank is
assigned to a non-Clifford endpoint. Paid bank exchange, coupled-field decoders,
changed callers, and full-native forward lineages require separate analysis.
