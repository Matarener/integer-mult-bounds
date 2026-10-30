# A sharp minimum block exponent

## Statement and inherited premises

Fix the complete PR5756 paid and target histograms `P_r,T_r`, with
`C = 622627591/200000000000`, `t=1-C`,
`T = sum_r T_r r^t`, and `N = sum_r T_r = 13390`. Define

```text
g(c,u) = sum_r P_r r^(t+u) / (c^u T),
d(c,b) = N b / (c^C T).
```

The declared gate family has integers `L>=3`, `c>=1`, `b>=1`, real `u>0`,
and rational `0<rho<1`. Its complete set of inequalities is

```text
g(c,u) < rho,
d(c,b) < rho,
rho^L < 1/16,
c^L < b^(L-2).
```

For `L=128`, the last condition is equivalent to `c^64<b^63`, so this is
exactly PR5775's two-tail/capacity subsystem. Allowing other `L` defines a
new algebraic family. No compiler implementing it is assumed to exist.

**Theorem.** Subject to the cited scalar premises below, this family is
feasible exactly for integer `L>=112`. At `L=112`, its unique integer
cutoff/floor pair is `(16,17)`. An explicit witness is

```text
L=112, c=16, b=17, u=1/7, rho=1951/2000.
```

The theorem remains true if `L` must be even or if `u` must be rational.

Ali Romman's [PR5775](https://github.com/CrocSwap/integer-mult-bounds/pull/5775),
head `56dc0a9ec02020f5e035c7d83f078fb2b27ac76a`, supplies these premises:

| Quantity | Cited rational lower bound |
| --- | --- |
| `inf_{u>0} g(15,u)` | `983563652257169/1000000000000000` |
| `inf_{u>0} g(16,u)` | `a = 487740894096357/500000000000000` |
| `d(17,18)` | `999697814388247/1000000000000000` |
| `d(16,18)` | `999886507972867/1000000000000000` |

Each cited lower bound is strict and exceeds `a`, except the row defining
`a` itself. The retained [result](premises/RESULT.json) and
[proof](premises/PROOF.md) specify their scope. PR5775 also retains PR5756's
[source invoice](premises/INVOICE.json), whose `strictification` records
upper bounds for `g(16,1/7)` and `d(16,17)`. Exact comparison gives

```text
g(16,1/7) < 975485/1000000 < 1951/2000,
d(16,17) < 945/1000 < 1951/2000.
```

These are cited mathematical premises, not independently rederived results
of this package. `ORIGINS.json` binds the verbatim source bytes to their
repository, head, paths, Git blobs and SHA256 hashes. Authentication does not
prove the predecessor's mathematics. This contribution proves the new
block-exponent consequence of those premises.

## Exclusion of every smaller block

The capacity inequality implies `b>=c+1`. Indeed, `b<=c` would give
`b^(L-2)<=c^(L-2)<=c^L`, a contradiction.

For fixed `u>0`, `g(c,u)` decreases with `c`. Thus every `c<=15` has
`g(c,u)>983563652257169/1000000000000000>a`.

The function `d(c,b)` increases with `b`. On real `c>=1`, the derivative of
`(c+1)/c^C` has the sign of `(1-C)c-C`, which is positive since `0<C<1/2`.
Consequently every `c>=17` and every capacity-compatible `b` has
`d(c,b)>=d(17,18)>a`.

For `c=16`, every `b>=18` has `d(c,b)>=d(16,18)>a`. The only remaining
integer pair is `(16,17)`, and its paid tail is at least the cited infimum,
which exceeds `a`. Therefore every capacity-compatible pair and every
positive offset satisfy `max(g(c,u),d(c,b))>a`.

The new exact integer comparison is

```text
16 * 487740894096357^111 > 500000000000000^111.
```

It says `a^111>1/16`. Since `0<a<1`, every integer `3<=L<=111` has
`a^L>=a^111>1/16`. Any passing tail choice requires `rho>a`, hence
`rho^L>1/16`. This contradicts the reserve gate. This argument covers all
cutoffs, floors, offsets and decays in the declared model.

## A passing block and all larger blocks

The cited upper bounds give both tail inequalities for the displayed
rational witness. The remaining new checks are integer comparisons:

```text
16 * 1951^112 < 2000^112,
16^112 < 17^110.
```

These prove the strict reserve and capacity gates at length 112. For larger
`L`, the same witness still works. Its reserve `rho^L` decreases, and its
capacity ratio is `17^2*(16/17)^L`, which also decreases. The two tails are
independent of `L` in the declared family. This proves the exact feasibility
set, without an upper cutoff on `L`.

At `L=112`, each of the other three cited lower bounds has its 112th power
strictly greater than `1/16`. The same case split therefore excludes every
integer cutoff/floor pair except `(16,17)` at the minimum.

## Meaning and limits

The new minimum is 16 below the predecessor's fixed length 128, a fractional
shortening of `1/8` within this gate family. This is a parameter-existence
result and a sharp obstruction below 112. It does not show that a complete
compiler can use 112, reduce carrier height, preserve another gate, or earn
a new exponent saving. Changing a block can change normalization, exit,
rounding and nonrecursive charges. Those changes require a separate complete
construction and bill. No source operator replay or predecessor audit is
part of this proof, and no physical supplier or complete multiplication theorem
follows.
