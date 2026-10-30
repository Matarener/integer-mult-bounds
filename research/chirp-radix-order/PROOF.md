# Largest-radix-first cached chirp table movement

This is a scoped written proof. It concerns the sequential table tape of
Ryanson Jonathan's PR #4325 suffix-product chirp enumerator, with a changed
axis layout. It does not audit that package or Cinna Davis's PR #4100.

## Contract

There are d >= 1 axes of dyadic lengths t_0,...,t_(d-1), each at least two,
and T is their product. The tape contains the tables in that order. Each
entry occupies P >= 1 consecutive cells. Table k starts at
O_k = P sum_(i<k) t_i. The table head starts at zero.

The mixed-radix counter enumerates axis zero fastest. At the first record,
read entry zero of tables d-1,...,0 to fill the suffix-product cache. At a
later record, if the carry stops at axis j, read the new entries of tables
j,j-1,...,0 and recompute those suffix products. To read an entry, move to
its first cell and sweep forward P cells. After the final record, return
the table head to cell zero. All table contents are read-only.

Cache arithmetic, cache-tape actions, the counter and payload are separate
from this table-head metric. Products of exact phases commute, so the
cache returns the same phase at each named coordinate after an axis
permutation. Finite-precision multiplication need not commute or associate
exactly; a rounded service must use its stated error contract.

## Exact movement identity

Write L_k = product_(i<k) t_i, so L_0=1 and L_d=T.
For the full enumeration including setup and final return, table movement is

```
Q/P = 2 t_0
      + 2 sum_(k=0)^(d-2) (t_k+1) T/L_(k+1)
      +   sum_(j=1)^(d-1) (t_j-1) T/L_j.                 (1)
```

Empty sums are zero. This identity in fact requires only integer t_i >= 2.

To prove it, first omit the final return. The last table read is the final
entry of table zero, so the final head is t_0 P. If B is the total backward
distance in units of P, the total distance before return is t_0 P+2BP.
Returning adds another t_0 P.

For each k < d-1, the reverse table traversal crosses from table k+1 to
entry zero of table k exactly T/L_(k+1) times, including initialization.
Its baseline backward distance is t_k+1. If the carry stops at j=k+1,
the newly read entry of table j has index b in 1,...,t_j-1, so this one
crossing has an additional backward distance b. Each such b occurs
T/L_(j+1) times. Thus

```
B = sum_(k=0)^(d-2) (t_k+1) T/L_(k+1)
    + sum_(j=1)^(d-1) [t_j(t_j-1)/2] T/L_(j+1).
```

Substitution proves (1). Every forward sweep, initial seek and final
return is included; counting only the distance between entry starts would
give a different identity.

## Sharp uniform bound after choosing a fastest axis

Choose any largest radix M as t_0. The remaining axes can stay in their
relative order. Then

```
Q <= 7 T P.                                            (2)
```

No bound on max(t_i)/min(t_i) is needed. For d=1, Q=2TP.
For d>=2 put b=2^(-(d-1)). Since t_i>=2 and t_i<=M,

```
2M/T <= 2b,
2 sum_(k=0)^(d-2) (t_k+1)/L_(k+1)
  = 2 sum_(k=0)^(d-2) (1+1/t_k)/L_k
 <= 2 + 2/M + (6/M)(1-2b),
sum_(j=1)^(d-1) (t_j-1)/L_j
 <= (2-2/M)(1-b).
```

The middle sum over k>=1 is empty when d=2, and the displayed bound then
has 1-2b=0. Adding gives the explicit stronger estimate

```
Q/(TP) <= 4 + 6/M - 10b/M <= 7,
```

because M>=2 and b>0. This proves (2).

The constant seven cannot be decreased uniformly in d. With every t_i=2,
(1) gives the exact formula

```
Q/P = 7*2^d - 10,
Q/(TP) = 7 - 10/2^d.
```

It approaches seven from below. This is sharpness of one specified table
schedule, not an optimality theorem over every possible tape algorithm.

## First application and boundary

On the skew two-axis layout (2,512), (1) gives Q=264708P. Choosing the
512-axis fastest gives (512,2) and Q=3078P, with T=1024. The latter is
1539/512 emitted word volumes. Both counts include the table-head return.
PR #4325's displayed 258.5 ratio omits that final return and rounds the
ratio; the metrics should not be silently mixed.

The exact phase at an original named coordinate x is the product of the
same one-axis factors in either order. The new enumeration emits those
coordinates in the new order. A consumer must already accept that order,
or separately pay for layout conversion. This proof supplies no free
transpose, physical encoded controller, table construction, cache cleanup,
multiplier implementation, supplier admission or new kappa.

## Executable scope

The independent literal counter executes every table read and carry. The
closed-form implementation never calls that counter. Complete small
dyadic domains compare both, and a separate exact quadratic-exponent cache
checks the association of emitted phases with original axis names. The
binary family is checked through 64 axes by exact arithmetic. The written
argument, rather than that finite range, proves the all-size assertion.

Executable inputs have at most 64 axes, radices at most 65536, word width
at most 64 and product bit length at most 1025. Literal enumerations are
capped at 131072 records; phase checks at 4096. These are verifier resource
bounds. All loops have finite bounds, and all contracts remain enabled
under optimized Python. Functions are below 60 lines. There is no recursion,
dynamic loading, network, or write path. Python's managed integer, JSON and
dictionary allocations are a Power-of-Ten rule-3 deviation, bounded by the
input and fixture limits. Standard-library iterator and key callbacks have
fixed targets and no shared mutable state. Warning-strict execution is the
available interpreted diagnostic; no global analyzer configuration changes.
