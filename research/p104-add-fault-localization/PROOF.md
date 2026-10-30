# Exact localization of a single ADD coefficient

This is a scoped proof about linear scalar programs over the rationals. The
algorithm and its P104 application are produced by Nick Petalas. Prefix/suffix
rank-one fault propagation is standard mathematics, already used in the R439
omission atlas. It is not claimed as new here.

## Contract

There are R scalar roles. The first N hold arbitrary independent inputs,
including arbitrary dirty public helpers. The remaining roles start at zero.
The allowed fixed chronological operations are

```
ADD d,s,c:    x_d <- x_d + c*x_s, d != s
COPY d,s,c:   x_d <- c*x_s,       d != s
SCALE d,c:    x_d <- c*x_d
INIT d:      x_d <- 0
CLEAR d:     x_d <- 0
MOVE:        the scalar state is unchanged
```

All coefficients are rational. Every output role is observed as a linear
function of all N input coordinates. A supplied matrix T specifies the desired
complete scalar endpoint. The question is which single ADD coefficient can be
changed by a nonzero rational delta to make that endpoint exactly T. Every
other operation, operand, coefficient and order stays fixed.

Zeroing is the declared scalar interpretation. It does not prove that erasing
a particular physical owned field is legal. MOVE ignores scalar frame action
in this logical model; the model does not claim that arbitrary cross-frame
physical operations preserve scalar semantics.

## Necessary and sufficient repair identity

Fix an ADD at event i. Let P_i map the N inputs to the state immediately before
that event, and let S_i map the state immediately after it to all R outputs.
Both may be singular. In particular, COPY and zeroing are permitted before or
after the chosen event. Write

```
p_i = e_s^T P_i,     q_i = S_i e_d.
F   = S_i (I + c e_d e_s^T) P_i.
```

Replacing c by c+delta changes the complete endpoint by exactly

```
F_new - F = delta * q_i p_i.
```

There is no approximation or higher order term. Thus a nonzero residual
E=T-F admits a single ADD repair exactly when E=delta*q_i*p_i for some event
i and nonzero delta. In particular, a residual of rank greater than one
cannot be repaired in this model. If p_i or q_i is zero, that event is
invisible to the complete endpoint under every coefficient change.

Choose any nonzero residual entry E[a,b]=h. If E has rank one, let its a-th
row be u and its b-th column be v. Then E=v*u/h. A repairing event necessarily
has p_i[b] != 0 and q_i[a] != 0, and it satisfies precisely

```
p_i = (p_i[b]/h) * u,
q_i = (q_i[a]/h) * v,
delta = h / (q_i[a]*p_i[b]).
```

Necessity follows by taking row a and column b of the repair identity.
Conversely, substituting the two proportionalities and delta gives
delta*q_i*p_i=v*u/h=E. This proves sufficiency as well. The algorithm checks
these equalities over exact fractions, so it returns every semantic repair
and no others, provided it completes within its declared resource bounds.

Several events can have proportional signatures. They must all be reported;
the observed endpoint cannot decide which event was historically corrupted.
If E is zero, the program reports `already_matches`. That status makes no
assertion that the program has no endpoint-invisible faults. If E has rank
one but no event passes both tests, it reports `no_single_add_repair`.

## Computation without a matrix per event

A first forward pass computes F and factors the residual. A second forward
pass maintains every current role's input row and checks each ADD's source
row against u. Only the event index and p_i[b] of surviving events are kept.
A reverse pass starts from the identity map on the R outputs. At an ADD
`d += c*s`, its suffix column q_i is the current column for d, before the
reverse update `column_s += c*column_d`. COPY additionally zeros column_d;
SCALE multiplies it; INIT and CLEAR zero it. These updates right-multiply the
suffix map by each elementary operation, including singular operations.

The reverse pass tests surviving events against v and emits the unique delta
for each passing event. Both passes use the same original program. No
candidate mutation is replayed by the diagnostic, and no random projection
or fixed-input fingerprint replaces equality of the full linear maps.

## P104 specialization and limits

The P104 adapter uses N public inputs and eight initially zero owned roles,
as in PR5568's scalar legality oracle. Its target preserves every public
input and adds input x_s to output x_(s+112) for each listed live port s.
All eight owned outputs must be zero. This binds the diagnostic to that
declared endpoint, rather than treating one sampled input as a certificate.

Each proposed coefficient is also marked according to the toolkit's scalar
coefficient rule: nonzero, dyadic, and abs(c)+1 < 2^16. That mark checks only
this coefficient rule. It does not certify ownership, frames, zero-before-COPY,
legal CLEAR, arbitrary native action, precision, tape work, the caller,
compiler assumptions, supplier admission or a multiplication exponent.

The executable accepts at most 1,024 roles, 26,000 events, 256-bit input
coefficients, 4,096-bit stored linear-map numerators and denominators,
and 16 MiB input/decompressed files. Exceeding a bound fails explicitly; it
does not produce a partial candidate list. The written identity has no such
finite size restriction. Independent human and formal proof-kernel review
are unclaimed.
