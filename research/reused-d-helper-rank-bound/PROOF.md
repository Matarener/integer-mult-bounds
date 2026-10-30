# A shared-D rank obstruction with productive helper reuse

## Exact alphabet and endpoint

Work over a field of characteristic two and in the ring
`F[q,d]/(q^2,d^2)`. Both symbols commute with all scalar matrices. Put
`Q=I+q` and `D=I+d`. The required endpoint on n main fields is
`I_n+q I_n+d I_n+qd I_n`. The theorem requires equality of all four
coefficients. It also applies to an operator representation in which those
four coefficients are independent. It does not assume that an arbitrary
representation has that property.

There are f FULL calls. A source FULL has v main pairs. FULL i also reuses
s_i autonomous full-rank helper fields, and has normalized coefficients

```text
I + d E_i + q N_i + qd N_i.
```

The exact hypotheses are:

```text
E_i^2=E_i,           rank(E_i)=2v+s_i,
E_i N_i=N_i E_i=N_i, rank(E_i+N_i)=2v.
```

They hold for a main block made of v nilpotent two-by-two query blocks and
s_i independent QD helper directions, after any constant scalar conjugation.
The full proof below only needs the displayed support and rank conditions.
It permits mixing across ports, rather than requiring separate port matrices.

Each thin letter is `I+q T_j`. Let h be the total paid H1 count of these letters,
with `sum_j rank(T_j)<=h`. A usual v-port thin packet has rank at most v and
costs v H1 calls. General thin matrices with that funded rank condition are
allowed. They give no additional productive targets.

Ordinary scalar changes of basis independent of q and d can occur between
calls. At q=d=0 their total product must be identity. Moving those constants
to the boundary conjugates the displayed matrices and preserves every rank
hypothesis. Operator-valued free changes of basis are outside the alphabet.

## Rank theorem

Write `s=sum_i s_i` and `M=2vf+s`. Comparing the d and q coefficients gives

```text
sum_i E_i = I_n,
sum_i N_i + sum_j T_j = I_n.
```

Thus `M>=n`. Factor each projector as `E_i=U_i V_i`, where U_i has
`2v+s_i` columns and `V_i U_i=I_(2v+s_i)`. Put
`B_i=V_i(E_i+N_i)U_i`. The support identity gives
`E_i+N_i=U_i B_i V_i`, and `rank(B_i)=2v`.

Stack all U_i horizontally into U, all V_i vertically into V, and all B_i
as diagonal blocks in B. Then

```text
UV=I_n,   rank(U)=rank(V)=n,   rank(B)=2vf.
```

The rank inequality for a product through the M-dimensional middle space gives

```text
rank(U B V) >= rank(U)+rank(B)+rank(V)-2M
            = 2n-2vf-2s.
```

In characteristic two, the coefficient equations also give

```text
U B V = sum_i(E_i+N_i) = sum_j T_j.
```

The last sum has rank at most h. Therefore every word in the stated alphabet
satisfies both necessary inequalities

```text
M=2vf+s >= n,                 h >= 2n-2vf-2s.          (1)
```

This proof is independent of word order, a simplex construction, a search size
or the mixed qd equation. It does not say that (1) is sufficient for a word.
It is an application of the classical rank inequality, not a new rank theorem
for arbitrary matrix products.

When no helper is reused and n=v n0, divide (1) by v to get
`2f>=n0` and `h/v>=2n0-2f`. The proposed family
`n0=2p`, `f=p+2`, `h/v=p-1` can therefore exist only for `p<=3`.
Its favorable unrestrained rank surplus is `48p-3123`, positive only for
`p>=66`. The two necessary conditions have no common value. A positive price
for that unrestrained family does not supply a controller.

## Complete rank-mass consequence

Assume each FULL source has paid rank mass equal to its autonomous helper
rank mass plus `2va+delta`, where `a>=1` and `delta>0`. A main target has
rank a+1. The integer a is distinct from the formal nilpotent d.
Each reused helper was a productive target of rank a+1, so it must
be debited once. Thin letters cost h rank-one jobs. All other source helper
credits remain. The complete target-minus-paid rank surplus is

```text
Delta_1 = (a+1)n - (2va+delta)f - (a+1)s - h
        <= (a-1)(n-M) - delta f
        <= -delta f < 0.                               (2)
```

The last strict inequality holds for a nonempty target, which forces f>0.
The loss holds for unequal s_i, partial-port helper reuse, and arbitrary
constant scalar coupling. It does not require s_i to be a multiple of v.
Added ordinary work cannot remove this raw invoice loss.

For the retained compact BIT profile, the authenticated source receipt gives

```text
v=111, a=7,
paid={1:1319,2:1342,3:78,4:39,5:102,6:10,7:18}, mass=5089,
helpers={4:4,8:432}, mass=3472,
5089-3472=1617=2*111*7+63.
```

Thus delta=63. Reuse is limited to the 432 autonomous H8 fields of each source
call. The four H4 helpers stay productive. The theorem remains a favorable
relaxation of any more restrictive physical matching or chart rules.
The source's actual controller uses distinct fresh D blocks and has positive
rank surplus 753. It is outside this theorem. The verifier checks that source
invoice as a control against applying the conclusion to the retained caller.

## Every retained power moment loses

Let `0<=t<=1` and let `Delta_t=T_t-P_t`, where an H_r job costs r^t.
Every paid job has rank at most eight. All targets have rank eight except
exactly four H4 helper targets per FULL. Therefore

```text
P_t >= 8^(t-1) P_1,
T_t = 8^(t-1) T_1 + 4f(4^t-4*8^(t-1)).
```

Combining this with (2) gives

```text
Delta_t <= -f*8^(t-1)*(79-32*2^(-t))
        <= -47f*8^(t-1) < 0.                            (3)
```

This uses the exact inequality `2^(-t)<=1`, not numerical root samples.
It handles the four partial helper targets rather than treating them as H8.
It rules out a favorable raw power moment for this source and alphabet even
before ordinary, storage, precision, compiler or outer costs are added.
It gives no new multiplication exponent and no claim about all BIT callers.

## Attaining examples and checks

For one port and one FULL, take a block of size r+2. Let E be identity.
Let N be `J2(0)` on the first pair and identity on the other r directions.
Use two thin nilpotents, `[[0,0],[1,0]]` and `[[1,1],[1,1]]`, on that pair.
The first pair of N is `[[0,1],[0,0]]`. The three query coefficients sum to E.
The chronological word FULL, first thin, second thin has all four endpoint
coefficients equal to identity. It has `M=n=r+2` and two thin calls, so both
rank inequalities are equalities. Direct sums give unequal r values and any
number of FULL blocks. Taking v parallel copies gives the native port count;
the target and debit scale together. These are exact alphabet examples, not
new physical native suppliers.

The standard-library checker tests 13 such words, including direct sums up to
256 streams per port and r=1,2,3 productive-helper examples. It checks projector,
support, defect and thin ranks before multiplying all four coefficients.
Removing any one call from the r=1 word fails its endpoint; dropping the FULL
qd coefficient also fails. Omitting 111 recycled-H8 debits would turn the
true surplus -63 into a false +825, so the productive debit is material.
Integer relaxations also check non-multiple-of-111 helper counts against (2).
The source's local paid/helper profile is joined to its complete retained
18-FULL invoice. The shared signed-invoice checker confirms that the attaining
examples cost more than direct evaluation under every increasing concave tariff.
The written proof establishes (1)-(3); finite examples do not replace it.

Changed native calls, productive thin jobs, uncharged helper losses, several
fresh D variables, operator-valued free codes and different coefficient
algebras require new arguments. Neither a universal circuit obstruction nor
formal verification of the multiplication theorem is claimed.
