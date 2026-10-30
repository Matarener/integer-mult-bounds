# Cross-port information capacity for the thin-query pool

This is a scoped proof. The general ingredient is classical linear information
dimension. The repository's outside-input rank probe already states the fixed-
observation quotient formula; its centre-nonlinear-fresh-floor package applies
dimension arguments to a different centre history. The new claim here is the
conditional cross-port thin-pool capacity constraint and its 528-request
consequences below. It proposes no physical primitive.

## Observation contract

Let K be any field. The input x ranges over the whole finite-dimensional space
X. A row of X* is a scalar linear observable. Initially the consumer knows all
observations in a subspace F of X*. It must return all observations in T.

A request returns at most c scalar linear observations of x. Its rows may depend
on previously observed values, including the initial free observations. Each
request's rows are fixed once that previous transcript is fixed. Free computation,
mixing across ports, feedback, and final decoding may be arbitrary deterministic
functions of the known transcript. They reveal no additional information about x.
There is no hidden input-dependent control channel. Every execution is finite.

The capacity c counts scalar output coordinates. It is neither a native frame
rank nor the number of ports with a nonzero coefficient. A field response with
several independently readable coordinates is a vector response and must be
charged for those coordinates. Correlated or restricted inputs are outside X.

## Theorem 1: capacity on every successful transcript

Put D = dim(F + T) - dim F. Every protocol correct for every x has, on every
execution, total returned scalar capacity at least D. A sharper statement uses
the rank of the actual returned rows modulo F, which must be at least D.

Proof. Fix an execution on x, and collect its actual query rows in Q. Suppose
there is h in ker F intersect ker Q with T h nonzero. The execution on x+h has
the same initial transcript. Inductively, each request chooses the same rows
and returns the same values, so it also makes the same control decisions and
stops with the same decoder output. Its required answer differs by T h. This
contradicts correctness. Thus ker(F + Q) is contained in ker T. By finite-
dimensional duality, T is contained in F + Q. Therefore

    D <= dim(F + Q) - dim F <= number of returned scalar coordinates
      <= sum_j c_j.

This argument permits nonlinear decoding and data-dependent query selection.
Randomness with a correctness guarantee for every fixed random tape can be
fixed first. No claim is made about bounded-error randomized protocols.

The bound is sharp in this abstract oracle contract. Choose D target rows
complementing F inside F+T, request them, and reconstruct every target using F.
Group the D rows into packets of the declared capacities when their total is
at least D. This is an information-theoretic upper bound. It does not show
chronological availability or physical implementation of these queries.

## Theorem 2: independent ports and extra free information

For P independent port inputs X_p, suppose free and target rows are port-local
and F = direct_sum F_p, T = direct_sum T_p. Then

    D = sum_p [dim(F_p + T_p) - dim F_p].

This follows by taking dimensions of direct sums. Theorem 1 permits every query
row to mix all ports, so it is stronger than summing bounds for protocols
restricted to port-local requests. An invertible linear change of all input
coordinates preserves the dimensions. Relabeling or mixing ports cannot
replace P independent inputs with one correlated input.

If an additional free observation space S is supplied, the exact oracle
minimum becomes D_S = dim(F + S + T) - dim(F + S). The dimension formula gives

    D_S >= D - [dim(F + S) - dim F].

Consequently, reducing the necessary scalar capacity by k needs at least k
new independent free observations modulo F. This lower bound is sharp by
choosing S inside a complement of F in F+T. Where those observations come from,
and what they cost, are separate physical questions.

## Conditional application to the reported thin-query deficit

Matarener's [PR #5996](https://github.com/CrocSwap/integer-mult-bounds/pull/5996),
head `47242572d3b22ce49371245edc561dd75bf263e8`, reports a one-port quotient
dimension of fifteen for the retained p16 controllers. Its README at that
head defines the scalar specialization and credits the controller lineage.
That reported quotient dimension is an explicit premise here. Its computation
is not rerun, and no scientific acceptance of that predecessor is claimed.

If P independent copies of that observation contract are required, Theorem 2
gives D = 15P. Thus 104 ports require total scalar capacity 1560 and 112 ports
require 1680, even with dense cross-port encoding, arbitrary joint decoding and
adaptive feedback as defined above. The atlas's 528-request target therefore
requires the following output capacities.

- At 104 ports, capacity at most two per request is insufficient. If every
  request has capacity at most three, at least 504 of the 528 requests must
  have capacity three. The remaining 24 can have capacity two. These capacities
  sum to 1560. With fewer than 528 requests the necessary count of capacity-three
  requests can only increase, until it is infeasible.
- At 112 ports, capacity at most three per request is insufficient. If every
  request has capacity at most four, at least 96 of the 528 requests must have
  capacity four. The remaining 432 can have capacity three. Their total is 1680.
- If all requests remain scalar, meeting 528 needs at least 1032 new free
  dimensions at 104 ports, or 1152 at 112 ports, beyond the cited free span.

For the first two statements, if n requests have maximum capacity r, their
total capacity is at most (r-1)*528+n. Solve this necessary inequality for n.
The displayed distributions attain equality only as abstract output budgets.
They are not causal controllers or invoices. In particular a rank-r native
job has not been proved to deliver r scalar observations at the desired price.

## Scope of the obstruction

The new exclusion is for scalar or capacity-limited observations on independent
port inputs. A channel supported on all ports can still return only one scalar.
A channel exposing an entire port vector can have large capacity and is not
excluded. Restricted input families, new paid full outputs, changed target
relations, input-dependent side channels and approximate recovery require
different hypotheses. The proof does not identify native frame rank with
information capacity. No physical execution, complete paid moment, compiler,
stock, precision, tape tariff, all-size admission or new kappa is supplied.
