# Exact routing, cost, and storage proofs

## 1. Scope and algebra

Work over a ring in which 2 is a unit. The ordinary maps `J_j` commute and square to `I`. The query `Q` commutes with all of them and has square `J_0`. For `a in F2^s`, set

`E_a = 2^(-s) sum_m (-1)^(a dot m) J^m`.

The `E_a` are pairwise orthogonal idempotents and sum to `I`. No positivity or numerical approximation is used. There are `r` independent blocks, each with `n=2^s` data fields. Define `F_a=I+Q E_a/2` and `G_a=I+(Q-I)E_a`.

## 2. Controlled swap from legal instructions

For bit `k`, put `P=(I-J_k)/2`. On two distinct fields `(a,b)`, execute:

```
a += P b
b -= P a
a += P b
b  = J_k b
```

Each of the first three lines is two separate ADDs, with coefficients `+/-1/2` and shifts `I,J_k`. Thus this macro has six ADDs and one pure SHIFT. Since `P^2=P`, the final fields are

`((I-P)a + P b, P a + (I-P)b)`.

It swaps the fields on the negative `J_k` sector and leaves them in place on the positive sector. This identity also follows by direct expansion in `Z[1/2][J_k]/(J_k^2-1)`. The verifier checks all input columns and every cut of the seven-instruction macro. Both the coefficient prefix norm and suffix norm have maximum 2.

For each bit `k`, apply the macro to all `n/2` role pairs that differ in bit `k`. Do this for all bits. Call the result `R`. On sector `sigma`, the role action is `a -> a xor sigma`. Hence `R^2=I`, and its output at role zero is `sum_a E_a x_a`. The bit stages commute as complete maps. Using the same stage order a second time is therefore a valid inverse; it is not necessary to reverse the individual shears.

## 3. The two middle operations

Route each block, act at role zero, then route again.

For `F`, use one extra field `z`. Clear it once at entry. In each block, copy the routed role zero to `z` with one ADD, query `z`, add half of `z` to role zero, then clear `z`. The next block can use the same field. On sector `sigma`, only original role `sigma` receives `Q/2` of itself. All other roles are unchanged. This is precisely `diag(F_a)`. The full map is independent of the initial value of `z`, and the final value of `z` is zero.

For `G`, query routed role zero in place. There is no extra field. Sector `sigma` applies `Q` only to original role `sigma`, which is precisely `diag(G_a)`.

The two routes use `ns` controlled swaps per block. This proves the in-place tariff table. To keep inputs, first clear `rn` separate output fields and copy each input to its output with one ADD. Apply the in-place circuit to these outputs. This gives `rn` further ADDs and CLEARs. The original input fields are unchanged. The input-preserving comparison is thus a comparison of the same retained-input contract as PR5626, not a storage saving obtained by dropping its inputs.

For one block, PR5626 has `2n^2+n` ADDs, `n+2` CLEARs and `n+1` owned fields including outputs. The new retained-input circuit has `6ns+n+2` ADDs, `ns` pure shifts and the same query, CLEAR and field counts. It uses fewer ADDs for `s>=4`. Its ordinary instruction count is `O(n log n)` for this entire family. A universal lower bound on ADD count is not claimed.

## 4. Query lower bound

On every nonempty sector, the coefficient of `Q` in `diag(F_a)` has rank `r`: there is one nonzero entry `1/2` per block. The same rank is `r` for `G`. The sector-rank lower bound of PR5626 therefore requires at least `r` single-field queries, even with linear feedback and extra fields. Our circuits attain this bound.

This lower bound requires `I` and `Q` to be linearly independent on every sector used. The native central Gaussian family has this property for `f>=3`, as specified in the source proof. The construction works for smaller `f`, but the same minimality claim is not made there. The construction needs no Smith factorization or odd division.

## 5. Sharp workspace and CLEAR counts in a declared alphabet

This section has a narrower instruction model than the query lower bound. Allow distinct-role ADDs with dyadic coefficients and ordinary `J` shifts; pure ordinary shifts; `Q` or `Q^-1` on one field; multiplication of a field by a dyadic unit `+/-2^k`; and CLEAR. Extra borrowed fields may start arbitrarily, but must be restored. Each owned workspace field also starts arbitrarily and must finish zero. Do not allow a nonunit scalar overwrite, an arbitrary destructive address map, or a free initial zero field.

Specialize `Q=1` and every `J_j=1`, then reduce the dyadic coefficients modulo 3. Each block of `F` has one factor `3/2`, which becomes zero, and all other factors are one. If there are `m` owned fields, the final map has nullity `r+m`: `r` data directions and `m` owned directions. All allowed instructions except CLEAR are invertible modulo 3. One CLEAR can reduce rank by at most one. Thus at least `r+m` CLEARs are required.

There must also be at least one owned field. If `m=0`, the desired map on all data and restored borrowed fields is invertible over the rationals at the same specialization. A CLEAR would make the full square map singular, so no CLEAR could occur. Every remaining instruction has determinant a dyadic unit. Their product cannot have determinant `(3/2)^r`. This is a contradiction. With `m=1`, our circuit attains both the minimum workspace and the lower bound `r+1` CLEARs. For the gauge map, zero workspace and zero CLEARs are attained, so those counts are minimal.

These statements do not concern the additional retained outputs of the input-preserving wrapper. They do not apply to a model that admits `SCALE 3/2`: that instruction is singular modulo 3 and defeats the key invertibility premise. The verifier checks this scope control. In particular, the argument is not a universal memory lower bound for arbitrary scalar algorithms.

## 6. Prefix and suffix bounds

Use the maximum absolute row-sum norm on all fields and addresses. At a complete bit stage, each role interacts with only one other role. Every partial prefix and suffix within that stage has norm at most 2, from the exact local seven-instruction check. A full route has `s` stages. Thus every route prefix and suffix has norm at most `2^s=n`.

Let `M>=1` bound the query, all its prefixes, and all its suffixes. Each middle prefix and suffix in the perturbation circuit has norm at most `2(1+M)`, including a cut with arbitrary residual `z`. This follows by the triangle inequality on the copy, query, half-ADD and CLEAR. The gauge middle uses at most `M`. Composition gives the common bound `2 n^2 (1+M)` for every prefix and suffix in either in-place block.

The full `F` block has norm at most `1+M/2`; the full `G` block has norm at most `2+M`. Different completed blocks act on disjoint data. A prefix starts with the workspace clear. In a suffix, arbitrary workspace at the cut can affect at most the first remaining middle operation; its next CLEAR removes it before later blocks. Thus the same common bound holds for any number of sequential blocks, with no factor exponential in `r`. The input-preserving wrapper adds a copy stage of norm at most 2, so twice the common bound suffices for its prefixes and suffixes.

At native instruction boundaries, `||Q_f||_infinity = 2^(f/2)`, and `M=2^f` is a rational upper bound. This substitution does not bound an unexamined arithmetic implementation inside QUERY. A caller must provide those internal bounds and pay for the actual shifts and shifted ADDs. No complete tape, precision, or multiplication budget follows from the field circuit alone.

## 7. Checks and proof boundaries

The symbolic interpreter uses the regular group algebra `Q[C4 x C2^(s-1)]`. The low two bits give the power of `Q`; the other bits give spectator involutions. Its final matrix is compared with a direct expansion of each `E_a`. It includes every initial data and workspace column. A separate reverse-order adjoint interpreter swaps ADD source and destination roles and checks the transposed final map. This is a role transpose over a commutative coefficient ring, not the native address adjoint.

The native interpreter instead uses exact pairs of rational numbers at each address. It applies the Gaussian two-point map on each central bit and literal XOR shifts on the spectator bits. Its expected result expands the projectors directly from the original inputs. The tests cover one orbit of the spectator translations; all such address orbits have the same action. Five deleted or changed instructions fail against the full-column target. These finite checks do not replace the all-parameter proof above or the missing complete caller.
