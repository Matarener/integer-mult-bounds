# A joint moment floor for the complete eight-owned-block boundary

Source: PR5580 head `6efa248cf456d6101d757e9d09ba29711d18a13a`, compressed word
SHA256 `b2a98c4bd0dbe86c09e9d15ee060dcf1aab09dbef90aa1e2127676f4039f406b`.
No new kappa or construction is claimed.

## The deliberately enlarged boundary

The replacement interval is `[13378,13485)` in the source program, from the
first owned INIT to just after the last owned CLEAR. Its public boundary has
41 roles: eight distinct copied producers and 33 distinct recipients. No
other public role is read or modified within the literal interval.

Treat these 41 public entry values as independent coordinates. The verifier
checks that their actual prefix rows have rank41 on original arbitrary public
inputs. It also checks that the fixed suffix observes all41 public coordinates
with column rank41. Therefore an exact whole-word replacement using only these
roles must implement the same local public map: from `S(R-T)P=0`, right and left
inverses imply `R=T`. It may not rely on correlated values in outside registers.

Every producer enters and exits at dimension8. Every recipient keeps its own
arbitrary input and gains a nonzero multiple of exactly one producer. For each
producer, at least one recipient exits at dimension1. Projection of these eight
observations onto the eight independent producer coordinates has rank8.

An allowed replacement can change every internal scalar dependency, introduce
arbitrarily many zero-initialized owned fields, share private work across all
eight original lifetimes, and use arbitrary rational scalar operations. It
must preserve all public entry/exit values and frames, clear private outputs,
use common-frame scalar operations, ascending public transports and paid
descending owned transports. It introduces no public helper or new productive
credit. This is stronger than seven separate fixed-star theorems, but weaker
than a global lower bound allowing earlier preparation or outside information.

## Seven information cuts

Fix a dimension threshold `k` in `{2,3,4,5,6,7,8}`. Project every current scalar
value onto its eight producer coordinates. Let `V_k` be the span of every such
projected row ever observed in a register with frame dimension less than k.
The span retains past observations after storage is erased or moved away.

Initially `V_k=0`: the only boundary coordinates containing producer information
are the eight producer registers themselves, all at dimension8. Other input
coordinates are independent recipient values, whose producer projections vanish.

Scalar combinations at a common frame below k do not enlarge `V_k`. Operations
above k stay above k. INIT is zero, CLEAR cannot add information, and a public
ascent cannot carry information from above the threshold to below it. Only an
owned descent from dimension `a>=k` to `b<k` can enlarge the span. That event
transports one scalar row, so increases the span's rank by at most one.

The final eight dimension1 observations have producer-projection rank8.
Consequently every allowed replacement has at least eight owned descents
crossing each of these seven thresholds. This argument permits sequential
outputs, arbitrary private erasure, multiple private fields and shared work.

## Convert crossing counts to the recursive moment

Let `H_r(t)=r^t` for `0<t<=1`. An owned transport of rank `r=a-b` crosses
`c=#{k in {2,...,8}: b<k<=a}` of the seven thresholds, where
`c<=min(r,7)`. For every positive integer r,

```
H_r(t) >= c * 7^(t-1).
```

For `r<=7`, this follows from `r^(t-1)>=7^(t-1)` and `c<=r`. For `r>=7`,
it follows from `r^t>=7^t` and `c<=7`. Summing over all owned transports and
then summing the seven rank-eight cut requirements gives

```
total owned paid moment >= 56 * 7^(t-1) = 8 H7(t).
```

The source's public boundary has total ascending dimension change31, spread
over31 fields each changing by one dimension. Every physical public field must
retain its own endpoint. Its required rank-one ascent costs H1, independently
of the owned transports counted above. Thus every replacement pays at least

```
31 H1(t) + 8 H7(t).
```

The literal word instead pays

```
33 H1(t) + H2(t) + H3(t) + 7 H7(t).
```

Therefore the maximum possible raw recursive saving inside this full shared
boundary is at most

```
2 H1(t) + H2(t) + H3(t) - H7(t).
```

Both have the same rank mass87 at t=1. The cap is the exceptional role738's
fragmentation penalty. The argument does not prove this cap attainable; extra
middle-level delivery constraints may make the actual optimum higher.

## Crucial distinction from original-input dimensions

The original word's relevant inputs mostly enter on dimension0 or1 frames.
Those original variables do NOT justify dimension cuts requiring eight
high-dimensional sources. The theorem is valid here only because it uses the
later 41-role boundary, treats its coordinates independently (with verified
prefix and suffix ranks), and disallows reading outside public side information.
Moving the boundary earlier can invalidate the source-dimension hypothesis.

This is not a sum of the nonadditive original-support loss-space bounds. It is
a new joint information-flow argument under a stronger boundary contract.
It gives no unrestricted whole-word tariff optimum, new productive credit,
ordinary-pass improvement, native admission or new multiplication bound.

## Certificate

`joint_boundary.py` reconstructs all source scalar rows and frame/lifetime
legality; finds the interval and its41roles; proves both boundary ranks; checks
the exact recipient map, eight one-dimensional independent observations,
public31H1 tariff and each of the seven source crossing counts. A scope control
duplicates one observation and correctly lowers the observation rank to7.

Prepared with substantial OpenAI Codex assistance. Apache-2.0. Retain the PR5580,
PR5569, PR5561 and complete P104 predecessor attribution in the source package.
