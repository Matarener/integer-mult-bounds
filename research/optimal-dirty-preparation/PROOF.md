# Exact binary idempotent preparation distance

Let u,v be nonzero binary column vectors of finite length r with v^T u=1.
All vector weights and intersections below are ordinary integer counts.
A scalar row-XOR is E_ab=I+e_a e_b^T with a!=b, charged one unit. It acts
on the pair as u -> E_ab u and v^T -> v^T E_ab, since E_ab is an involution.
Thus it adds bit u_b into u_a and bit v_a into v_b. A preparation T must
send uv^T to some coordinate projector, equivalently Tu=e_p and
v^T T^-1=e_p^T. The coordinate p is not prescribed.

Put A=wt(u), B=wt(v), c=wt(u&v). The idempotence assumption makes c odd.
The exact minimum number of row-XORs is

    d(u,v) = A+B-(c+3)/2.                                      (1)

Extra arbitrary dirty roles with zero entries in u,v do not reduce this
minimum. Free role permutations, if granted, do not change it either.
No arbitrary free GL_r basis changes or clean initialization are granted.

## Lower bound

Define F(u,v)=A+B-(c+3)/2. Assign each coordinate its color (u_k,v_k).
Its contribution to 2F+3 is 0 for 00, 2 for 10 or 01, and 3 for 11.
Only the destination and source colors change in one row-XOR. In the next
table rows give the old destination color, columns the old source color;
entries give the change in 2F.

| destination / source | 00 | 01 | 10 | 11 |
| --- | ---: | ---: | ---: | ---: |
| 00 | 0 | 0 | 2 | 2 |
| 01 | 2 | -2 | 2 | 0 |
| 10 | 0 | 0 | -2 | -2 |
| 11 | 2 | -2 | 0 | -2 |

These sixteen entries follow directly from
(u_a,v_a,u_b,v_b) -> (u_a+u_b,v_a,u_b,v_b+v_a) over F2.
In particular every paid step lowers F by at most one. The endpoint has
A=B=c=1 and F=0, so every preparation uses at least F(u,v) steps.
Appending 00 coordinates leaves F unchanged, proving the dirty-workspace
statement. Permuting coordinates also leaves F unchanged.

## Attaining construction

Choose any shared coordinate p with u_p=v_p=1. Pair the other c-1 shared
coordinates. For each pair a,b, execute, chronologically,

    row_a ^= row_b
    row_b ^= row_p
    row_p ^= row_a.

Initially both a,b have color 11. After the first step they have colors
01 and 10. The second removes the remaining u_b without changing v_p;
the third removes v_a without changing u_p. Both end 00, and p remains 11.
Every other coordinate is unchanged. Hence each pair costs three steps.

Remove each original u-only coordinate k by row_k ^= row_p and each
original v-only coordinate k by row_p ^= row_k. Each costs one step and
preserves p. The total is

    3(c-1)/2 + (A-c)+(B-c) = A+B-(c+3)/2.

The resulting T has the requested pair endpoint and gives (1).
No statement here depends on a finite census or a field representation of Q8.

Since A+B=|supp(u) union supp(v)|+c <= r+c and c is odd, the worst-case
distance at r roles is floor(3(r-1)/2). It is attained by u=v=all ones
for odd r, and by all-one u and a v with exactly r-1 ones for even r.

## Finite-array consequence

Use Arham Tahir's PR3137 regular Q8 action P_g on eight contiguous payload
blocks per role. The required full dirty operator is I+uv^T(P_g-I).
Execute the preparation, P_g on role p, then the preparation in reverse.
The complete operator is T^-1 [I+E_pp(P_g-I)] T, which equals the target
on every input. This argument works for any linear address operator P_g.

For nonidentity Q8 labels let S_g=4 for the central label -1 and S_g=6
otherwise. These are the existing PR3137 block-transposition counts.
The new scalar preparation/restoration count and data XOR bill are

    C_new = 2d = 2A+2B-c-3,
    bit XORs = 8 payload C_new + 3 payload S_g.                 (2)

The unchanged two-star compiler uses C_old=2(A+B-2). Thus the exact
reduction is c-1 whole-array XORs, or 8 payload (c-1) bit XORs.
The middle Q8 algorithm, its swap invoice and array layout are unchanged.
Identity emits no work. At u=v=(1,1,1), C falls from eight to six. A
noncentral label therefore costs 66 payload bit XORs rather than 82 payload.

The scalar basis preparation is optimal in the stated row-XOR alphabet.
Equation (2) is the bill of this conjugate-once/inverse-restore compiler,
not a minimum over arbitrary bit circuits, interleaved address operations,
shared consecutive actions, or physically hosted supplier implementations.
Descriptor generation, address arithmetic, storage, routing and the actual
recursive caller require separate payment. No complete multiplication bound
or improved kappa follows from this local saving.

## Evidence and proof boundary

The written proof quantifies over every finite r. The executable compiler
enforces 1<=r<=256 and payload<=7 as resource limits. Independent multisource
BFS checks every binary idempotent through eight roles, allowing every
destination/source row-XOR and every coordinate endpoint. The BFS does not
use (1), the constructor or its pair update function. Its integer distance
table agrees with the emitted schedule lengths in every case.

An independent Hamilton integer-quaternion reference reconstructs every
dirty-array output, while the implementation uses the affine address action
and literal three-XOR swaps. Symbolic packets contain every input bit as an
independent basis symbol. Equality of all output packets proves each tested
linear operator on arbitrary dirty data, including spectators. The inverse
is checked too. These finite checks corroborate the written proof; no formal
proof-kernel review or complete selected replay is claimed.
