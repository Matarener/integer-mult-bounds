# #4334's sharp right-vector threshold over extension fields

**Claim type: an independent finite check over six non-prime fields. No new
κ.** It adds the extension-field software coverage that #4334 explicitly does
not claim.

## Object

[PR #4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334) (ToikY)
works in the right-vector model:

- paid factors `I + u·yᵀ`, with `u ∈ R²` and `y ∈ K²`;
- `R = K^k`, where `u` may vary by component but `y` and the free `GL_2(K)`
  maps are common to all components.

It proves a sharp component threshold for every finite field `K = F_q`. For
`k ≤ q`, every invertible target has `cost = δ ≤ 2`. For `k ≥ q+1`, there is a
target with `cost = 3` and `δ = 2`.

The sharp example comes from a quadratic extension `L = K[X]/(h)`: the
components are multiplication by one representative of each of the `q+1`
`K`-lines of `L`. #4334 writes the proof for every finite field, but its
software witnesses cover only prime fields. Its README says it does not
"claim an extension-field software census".

## Results

For `F_4`, `F_8`, `F_9`, `F_16`, `F_25` and `F_27`, built from irreducible
polynomials found by search, this package builds #4334's target with `q+1`
components and checks:

| Check | Result, every field |
| --- | --- |
| Each input line `t` is sent onto every line of `P¹(K)` exactly once | holds |
| No common pivot: every `(φ, t)` pair is killed by some component, over all `(q+1)²` pairs | holds, so `cost > 2` by #4334's criterion |
| #4334's Section 3 word `[[1,0],[r,1]]·[[1,b],[0,D]]·[[e,0],[f,1]]` reproduces each component | holds, so `cost ≤ 3` |
| `δ = min_T dim((MT − I)K²)` over every free `T ∈ GL_2(K)` | `δ = 2` |
| `k = q` side: 300 random invertible targets with `q` components have a common pivot | holds |

**F4 without the criterion.** An exhaustive search over every free `S`, every
pair of right-vector lines and every left vector finds **no word with two
paid factors** for the five-component target. It does not use #4334's pivot
criterion.

**Control.** The same search finds a two-factor word once one component is
dropped, which is the `k = q` case.

## Method and independence

- Field arithmetic is built here: `F_(p^k)` as `F_p[x]/(f)`, with `f` found
  by search and field tables checked.
- The irreducible quadratic `h` over `K` is also found by search.
- Nothing is imported from #4334. Its prime-field oracle and BFS are not used.

## Not covered

- The written proof for every finite field, which this corroborates on six
  fields and does not replace.
- Singular targets and general commutative algebras.
- Any native caller or invoice.

## Reproduce

```sh
python3.12 -B research/right-vector-extension-fields/verify.py
```

It prints `PASS_RIGHT_VECTOR_EXTENSION_FIELDS` in about 90 seconds, using only
the standard library. Most of the time goes to the `δ` check over `GL_2(F_27)`,
which has 511,056 elements.

## Open next questions

None from this check.

## Credit

The theorem, the construction and the three-factor word are ToikY's (#4334),
answering Nick Petalas's #4276 and building on Wentao Li's #4099 and #2513.
Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
