# Three negative Q8 targets need at least seven positive calls

Work in the full formal group algebra F2[Q8], with
`Q8={1,i,j,k,z,zi,zj,zk}`, `i^2=j^2=z`, `z^2=1`, `ji=z ij`.
The symbols z and 1 are distinct. A paid factor is

```text
D_l = I + ([g_l]+1) u_l v_l^T,   g_l in {i,j},   v_l^T u_l=1,
```

with binary vectors. Binary scalar GL mixing is free. Every role starts
with arbitrary independent dirty input; identity-target roles must restore it.
The target has exactly three entries in `{zi,zj}` and identity elsewhere.

**Claim (written reduction plus complete finite computation).** No such
endpoint has fewer than seven paid calls, for any finite number of roles.
The direct nine-call construction supplies an upper bound. Thus its minimum
is either seven or nine. This does not decide seven calls or improve kappa.

## From arbitrary dirty workspace to a finite call-indexed test

The scalar-core and call-Gram argument is from Nick Petalas's PR3517,
exact head `2c0cd78964ef363b15e2f4b2675bbd6982ae3ed8`. Its proof is retained
unchanged in `inputs/pr3517-PROOF.md`, with exact origin identities in
`inputs/RETENTION.json`. The needed argument is restated here.

Normalize scalar mixing by conjugating each paid projector. Augmentation
sends every paid gate and the diagonal group endpoint to identity, so the
remaining final scalar factor is identity. Put the image vectors into X's
columns, the covectors into Y's rows, and set A=YX. Its diagonal is one.
Every paid projector preserves `U=im X` and kills `K=ker Y`. The quotient

```text
C = U / (U intersect K)
```

has dimension rank A and retains each ordered rank-one idempotent. Its image
vector cannot vanish because `v_l^T u_l=1`. The map induced by Y identifies
C with `im A`, and projector l there is `A e_l e_l^T`.

Let E be the three active target coordinates and D the restored coordinates.
Each coefficient of the endpoint minus identity has image in U; its zi and
zj coefficients are the corresponding coordinate projections. Thus E lies
in U. Each factor fixes K, so the same coefficients kill K, giving K subset D.
Consequently C is E plus a quotient of restored dirty directions. It keeps
the three targets and restores all remaining arbitrary input. No clean
ancilla assumption, specialization of dirty data, or transpose over the
noncommutative algebra occurs.

The two first-order characters of Q8's abelianization give `X E_i Y=P_i`
and `X E_j Y=P_j`, where E_i/E_j select calls by label and P_i/P_j are the
zi/zj coordinate projections. Their sum gives `XY=P`, with rank P=3.
It follows that

```text
A^3=A^2,          rank(A^2)=3.
```

For the rank equality, PX maps onto E, since E lies in im X. Y is injective
on E because `XY e=e`. Hence `YPX=A^2` has rank three. Taking traces and
ranks in `XY=P` gives `n=3 (mod 2)` and `n>=3`. Separately, the numbers of
i and j calls dominate the respective target counts and have their parities.
Therefore lengths below seven reduce exactly to n=3 and n=5.

On the ambient call-index space define

```text
L_i=A E_i,  L_j=A E_j,  Z_i=L_i A,  Z_j=L_j A.
```

Every realizing word necessarily satisfies

```text
rank Z_i=s_i, rank Z_j=s_j,
L_i Z_i=Z_i, L_j Z_j=Z_j, L_i Z_j=0, L_j Z_i=0,
T A = A + ([zi]+1) Z_i + ([zj]+1) Z_j,
```

where T is the chronological product of the ambient gates
`I+([g_l]+1) A e_l e_l^T`. The last equality compares all eight formal
coefficients. Gate zero acts first. These are also sufficient: on im A the
first four equations define orthogonal target projections, and the final
equation gives the desired action on their images and identity on their
common kernel. A binary basis diagonalizes those projections. Only necessity
is used to exclude a word; sufficiency supports the positive controls.

Interchanging i and j is a group automorphism and target permutation is
free scalar mixing. The two shapes `(s_i,s_j)=(3,0),(2,1)` therefore cover
all eight ordered three-negative target lists and any placement of dirt.

## Complete finite evidence

`algebra.grams(n)` takes a Cartesian product of the `2^(n-1)` possible
diagonal-one rows at each of n positions. Every binary diagonal-one matrix
appears exactly once; there is no similarity, word-order or reversal pruning.
The registered dimensions are exactly three and five, so their totals are
64 and 1,048,576. Every matrix passes through the spectral/rank filters above.

For every survivor, the primary code enumerates every ordered i/j label list
obeying the proved separate rank/parity conditions. There are respectively
1/3 such lists at n=3 and 11/15 at n=5 for the two shapes. It tests the four
projector equations and then every coefficient of the formal endpoint.

The complete results are:

| Calls | All diagonal-one A | Spectral rank-three A | First-order candidates (3,0) | First-order candidates (2,1) | Accepted |
|---|---:|---:|---:|---:|---:|
| 3 | 64 | 1 | 1 | 3 | 0 |
| 5 | 1,048,576 | 4,280 | 4,920 | 11,420 | 0 |

`oracle.py` independently enumerates the off-diagonal integer counter, uses
binary dot products and explicit row spans, tries every label list without
the primary rank/parity pruning, and applies fixed faithful Hamilton left
permutations to eight-bit group packets. It imports none of the primary
algebra. Both complete censuses agree on counts and SHA256 streams containing
every first-order candidate, its labels, full endpoint and acceptance flag.
Stream order and canonical compact JSON encoding are specified by the code.
Hashes bind the computed data; their equality is not a substitute for the
coverage argument or the integer comparisons in the replay.

The small independent check covers every diagonal-one Gram matrix and label
list through three calls, with every nonnegative target-rank pair. Eight
direct nine-call endpoints are accepted; deleting any one of their nine
calls is rejected. Faithful regular-action checks retain two independent
dirty spectators. These fixtures test the predicate and restoration contract;
they do not replace the complete n=5 enumeration.

## Limits and credit

This is a computer-assisted exclusion of two exact lengths, transported to
all finite workspace by the written reduction. It is not a formal-kernel
certificate. Seven calls remain unsearched here, and the exact minimum remains
undecided. No physical caller, scalar-XOR preparation invoice, supplier,
multiplication theorem, new kappa or selected-frontier change is supplied.
Independent human and formal proof-kernel review are unclaimed.

PR3517 retains the scalar core and exact Gram criterion. Tuafo/PR2900 retains
image restriction, ywz65/PR2587 coefficient support/Sylvester, and PR3487 the
common-kernel quotient/two-sided bound. PR3471 retains its three-role negative
triple census, and PR3499 its scoped weighted tariffs. Aaron Wang/PR2318,
Cinna Davis, steph4n-gh and the register-model lineage keep their predecessor
credit. Arham Tahir/PR3137 and PR3461 address separate physical/scalar costs.
The retained predecessor proof preserves its full original credit and notices.
