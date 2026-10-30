# The all-pair handoff caller, with its full reader and terminal bill

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a local mathematical construction and a complete negative budget result
for its displayed cleanup. It does not establish a new multiplication exponent.

## Domain and conventions

Fix integers `q>=2` and `f>=1`. There are `n=2q+2` independent, arbitrary
field inputs, in banks

```
(a,t,b1,c1,b2,c2,...,bq,cq).
```

Write the original inputs as `a,t0,b1,k0,b2,C2,...,bq,Cq` and put `C1=0`.
The two distinguished dirty input directions are `t0,k0`; neither is initialized.
Every final bank, including these two directions, is eventually transformed.
All operators below act on the LEFT. Products are applied rightmost first.

In the free-operator calculation `N^2=-I`, and `P_j` are arbitrary independent,
invertible, noncommuting operators. The physical instance has common plane 0,
fresh planes `1,...,k`, `k=2q+1`, each of arity `2f`. Operators `N_i` satisfy
`N_i^2=-I`, commute on distinct planes, and are conjugated by actual ADDRESS
plane permutations. Set `N=N_0`, `P_j=S_(0,j)`, and

```
F_s=N_s ... N_1,       E=N_0 F_k.
```

All native phases are the exact global normalizations inherited from the
minimal-carrier interface. They are retained by the signed plane algebra.
`E` commutes with every native plane and every whole-plane ADDRESS permutation.
The physical public target is `diag(E,...,E)`, of arity `m=2(k+1)=4q+4`.
The displayed formula with formal `P_j` does not, by itself, admit a different
physical chart or postcode.

A raw stage pays `N_0` on its source and `N_j` on every other bank. It applies
the ADDRESS swap `S_(0,j)` on the source. The fresh-progress count is therefore
`n` calls of arity 2 per stage, including the source call; no inactive bank
is free. A before/after bank SWAP changes which arbitrary value receives the
source ADDRESS operation. Every such SWAP is in the event list.

## Base on the original independent inputs

Put

```
S = a + sum_(l=1..q) b_l,
A_r = a + sum_(l=r..q) b_l,
Q1 = N^-1 P1 N,
J = [[P2+Q1-I, I-P2], [Q1-I, I]].
```

The first three source stages, followed by scalar entrances, give the following
exact original-input rows:

```
u = P3 [N k0 + (P1-I)(N t0+S) - A2],
v = (P2+Q1-I)t0 + (I-P2)k0 + (2N-N P1-P2 N)S.
```

At the entrance to pair `r=2`, in the common retarded frame `F_3`, the rows are

```
bank a       = a,
bank t       = u + C2,
bank b1      = N b1 - v,
bank c1      = N u,
bank b_r     = b_r                    (r>=2),
bank c2      = -v-N A2,
bank c_l     = (C_l-C2)-v-N A2         (l>2).
```

This is a matrix identity on all `2q+2` original columns. In particular, `u,v`
are not clean states or promised copies of one another.

Here is an algebraic specification of the base word, sufficient to obtain the
rows by direct substitution. At raw ZERO apply `c_r+=c1` for `r>=2`, then the
shared encoder `b1+=N t`. This encoder uses one actual `N` exposure and its
literal inverse. For `r=q,...,1`, apply `c_r-=t; a+=b_r`. The three queries have
source/target pairs `(a,t),(t,b1),(b1,c1)`. Their normalized source-retraction
columns are respectively

```
u1=e_a+e_b1,
u2=e_t+sum_(r=1..q)e_c_r,
u3=e_b1-N sum_(r=2..q)e_c_r.
```

For a source `s`, the retraction is the invertible shear
`G=I+(u_i-e_s)e_s^T`; `G^-1` is obtained by negating the off-source entries.
Use `G^-1`, then the raw query with source diagonal `P_i` and target cross `N`,
then `G`. At the third source retain the actual `N` continuation, so its source
diagonal is `N P3`. Its `N`-valued entry fanouts use the existing source query;
its `N`-valued exit fanouts precede the continuation using `N(N P3)=-P3`.
The intervening bridges are

```
a-=b1; t+=c1;        [between stages 1 and 2]
t-=c1;               [between stages 2 and 3]
b1+=a; c1+=t; t-=c1; SWAP(b1,c1);
a-=b2; t+=c2; c_r-=t for r>=2.
```

Finally restore `a-=sum_(r=3..q)b_r`, and apply
`c1-=a+sum_(r=2..q)b_r`. The raw-a restoration is necessary: without it the
deeper response entrance leaves those independent future `b_r` inputs on `a`.
The saved defect control omitting it changes completed public columns.
This base pays `3n+3` arity-2 calls: three complete raw stages, the shared input
exposure and inverse, and the third-source continuation. All other operations
are explicitly paid finite scalar/ADDRESS scans.

## One pair: the scalar invariant and its proof

Suppose pair `r`, `2<=r<=q`, has the entrance

```
t=u+delta C_r,             c1=N u,
b1=N b1raw-v,              c_r=-v-N A_r,
c_l=(C_l-C_r)+c_r (l>r),   b_l=b_lraw (l>=r),
a=a_raw,
```

where `delta C_r=C_r-C_(r-1)` and every displayed future raw input remains
independent. Earlier completed public outputs may be retained unchanged.
There are two raw stages `e=2r`, `o=2r+1`.

At the even stage:

1. Query `N(t)` and perform `t-=c1`. This gives `N delta C_r` on `t`.
2. SWAP `t,c1` before the source ADDRESS operation. The source now holds `N u`.
3. Apply its literal `S_(0,e)` and fresh `N_e` to all non-source banks.
4. SWAP `c1,c_r`.

After removing the common fresh prefix, the source row is `U=P_e u`, the
completed `c_r` row is `N delta C_r`, and `c1` is the old dirty row `-v-N A_r`.
The elementary identity used here is `N_e^-1 S_(0,e)=S_(0,e) N^-1`.
It explains the retarded source postfactor `P_e N^-1`; this factor is not an
additional unpaid native query.

At the odd stage:

1. Query `N(b_r)`. Add that exposed source to every future `c_l`.
2. Perform `c1+=b_r`, and SWAP `b_r,c1` before the source ADDRESS operation.
   The new source is
   `-v-N A_(r+1)=N(Nv-A_(r+1))`.
3. Subtract that source from `b1` and every future `c_l`.
4. Apply source ADDRESS `S_(0,o)` and fresh `N_o` to every non-source bank.

The resulting rows are exactly

```
U=P_e u,                    V=P_o(Nv-A_(r+1)),
b_r=N b_rraw,               c_r=N delta C_r,
b1=N(b1raw+A_(r+1)),        c_l=C_l-C_r (l>r).
```

The future-c calculation retains all cross terms:

```
(C_l-C_r)-v-N A_r + N b_r -[-v-N A_(r+1)] = C_l-C_r.
```

If `r=q`, stop this loop and SWAP the finished `b_r` into its public slot.
If another pair remains, perform the following scalar re-encoding BEFORE the
one retained odd-source continuation:

```
b1+=U;
c_l-=c_(r+1); c_l+=U for l>r+1;
SWAP(t,c_(r+1));
t+=V;
N(V);                       [one actual arity-2 continuation]
SWAP(source b_r,c1).
```

Define

```
u_next=V,
v_next=-U-N A_(r+1).
```

Then `b1=N b1raw-v_next`, the next dirty `c_(r+1)` row is
`U=-v_next-N A_(r+1)`, the next `t` row is
`u_next+delta C_(r+1)`, and the held row is `N u_next`.
The future-c rows become `(C_l-C_(r+1))+U`, exactly the next invariant.
This proves the induction for every `q`; no fitted finite pattern is used.
The one-source continuation and all scalar re-encoding reads occur at their
actual shared fresh cut. Moving them elsewhere requires a new intertwiner.

At the end, query `N(a)` once and subtract it from `b1`. Decode completed c
outputs triangularly by `c_r+=c_(r-1)` for `r=3,...,q`. These operations finish
`a,b1,...,bq,C2,...,Cq` as full independent native outputs. The two carrier rows
remain

```
U=P_(2q) u_(q-1),
V=P_(2q+1)(N v_(q-1)-a).
```

## Both the homogeneous defect and every public reader

The base homogeneous dependence on the two original dirty inputs is

```
u1 = P3 N * (second row of J) + P3[(P1-2I)S+b1],
v1 =       (first row of J)  + (2N-NP1-P2N)S.
```

For each nonfinal pair the full affine recurrence is

```
u_next = P_o(N v-A),
v_next = -P_e u-N A,             A=A_(r+1).
```

Consequently the homogeneous update is the invertible anti-diagonal matrix
`[[0,P_o N],[-P_e,0]]`. A terminal bank permutation aligns its two monomial
factors with the two rows of `J`. This is an explicit bank-rank-two defect;
it does not prove constant native cleanup.

To include all readers, put `h=Nv`. The exact same recurrence becomes

```
u_next=P_o(h-A),
h_next=-N P_e u+A.
```

This form gives a literal inverse at the completed full-native cut:

```
h_next-=A;
N(h_next);
P_e^-1(h_next);                 [this register is now u]
P_o^-1(u_next); u_next+=A;      [this register is now h]
SWAP the two carrier roles.
```

There is one native `N` call, two ADDRESS scans, the displayed completed-public
reader ADDs and one bank SWAP. No independent public-native query is hidden.
`A` is available at this cut because every public output is already complete.

For clarity, the final physical prefix is `F_k` times the retarded carrier
rows, while its public rows are `E` times their inputs. Two leading common
queries on the carrier banks convert those rows to the completed `E` chart;
`E` commutes with every actual plane permutation. Invert the final factory
ADDRESS operations, restore its public `+a`, and run the inverse recurrence
above for pairs `q-1,...,2`. Then `P3^-1 u=y1` and `h=Nv1`.
The remaining original-input core has a shared two-carrier cleanup. In carrier
coordinates `(p,q)=(h,y1)`, its complete word is

```
p-=q; p+=b1;
Q2^-1(p);                       Q2^-1=N^-1 P2^-1 N
p-=S;
q+=p; q+=2S-b1;
P1^-1(q);
q-=S; q-=p; p+=q;
N^-1(p); N^-1(q).
```

The postponed `-P2 N S` and `-P1 S` reader contributions cancel immediately
after their corresponding shared operator exposure. This word therefore
retains all original public columns; it is not merely an inversion of `H`.
`Q2^-1` has actual native arity 4, with phase-complete monomial adapters.

## Complete cost and precise scope

The prefix has `k=2q+1` raw stages, `q-1` retained continuations, the two shared
input calls and the final common call. Thus

```
H2_prefix = n k + q+2,
m=4q+4=2n,     public stock=m n=2n^2,
D_prefix=2q.
```

The complete reader tail has two leading native calls, `q-2` recurrence calls,
two final native exits and one arity-4 query:

```
H2_tail=q+2,     H4_tail=1,     tail mass=2q+8.
H2_total=n^2+2,  H4_total=1,    total mass=2n^2+8,
D_total=-8.
```

This is a complete constructive invoice. Legal wide batching may change
positive-exponent pressure but leaves this rank mass unchanged. No public
output, helper, idling field, source postcode, factory reader or native phase
is discarded. There are no initialized fields, extra private fields or
unrestored helpers in the complete word. The inverse is obtained by reversing
every elementary event with its literal inverse, including all bank swaps.

For ordinary swaps, the two aligned homogeneous factory supports are exactly
`{5,9,13,...<=2q+1}` and `{3,7,11,...<=2q+1}`, of sizes `floor(q/2)` and
`ceil(q/2)`. This follows by substituting the homogeneous anti-diagonal update:
the new odd native plane enters the alternating factory and is distinct from
all earlier planes. In particular the support weight is `q`, not bounded.
The two direct `D_i^-1 N` arities sum to `2q+4`; the shared core adds 4.
This explains the displayed tariff, not a lower bound on all possible callers.

The proven negative scope is the ordinary source-handoff family and this
explicit complete tail. It does not exclude changed held-coordinate encoders,
operator-valued bridges, source-hole relocation, changed delivery kernels,
nonmonomial factory charts, or a different joint terminal word. A retarded
operator `F^-1 M F` cannot be replaced by the physical monomial `M` in such a
proposal. Every changed input chart and right ADDRESS code must be retained.

## Evidence and independent checks

- `handoff_family.py` / `HANDOFF-FAMILY.json`: free noncommutative and actual
  signed-plane all-column witnesses for q=2,3,4; both literal inverse orders.
  Normal and Python `-O` replay both pass. The written invariant above is the
  all-parameter proof, separate from these finite checks.
- `../q4-pauli-fusion/handoff_family_independent.py` /
  `INDEPENDENT-HANDOFF-FAMILY.json`: independently reconstructed first-three
  word and pair loop, opposite right-normal algebra, complete public-column
  and literal reversed-event checks for q=2,3,4,5,6,8,12,16. Its paid-progress
  intervals respect source/target reads, unary noncommutation and bank SWAPs.
  The omitted raw-a repair is a rejected defect control.
- `../native-frames/handoff_family_tail.py` / `HANDOFF-FAMILY-TAIL.json`:
  independently serialized full affine-reader tail, physical prefix replay,
  complete endpoint and both inverse orders for q=2,3,4; all-q inverse recurrence
  and exact ordinary factory-support proof. Omitting the final `a` reader fails.

These are exact finite computations plus written all-parameter proofs with
actual all-f operator bindings. They are not formal-kernel proofs, joint BIT
admission, numerical-error theorems, stock-owner allocations, fixed-tape
realizations or verified multiplication-exponent claims.
