# Native rank mass alone has no universal zero-helper floor

There is an exact admissible linear counterexample if the number of
rank-zero field-array scans may grow with the internal address length.
It does not meet the desired local cost and gives no kappa gain.

Let X_j flip internal address bit j. This is an explicit ADDRESS
permutation. Put

```
alpha=(1+i)/2,       beta=(1-i)/2,
C_j=alpha I+beta X_j,
C_j^-1=beta I+alpha X_j.
```

These are exact Gaussian dyadics. C_j is the usual native chirp, with
`C_j^2=X_j`. On two arbitrary independent public field arrays a,b, perform

```
a += C_j b;
b -= C_j^-1 a;
a += C_j b;
swap(a,b);
a = -a.
```

Before the swap, the fields are `(C_j b_old,-C_j^-1 a_old)`.
The final fields are exactly `(C_j^-1 a_old,C_j b_old)`. No input is zero,
no dirty input is discarded, and reversing every operation is the literal
inverse. Each displayed operator shear is two ordinary scalar/ADDRESS
ADDs: the source is unchanged while the two terms are added. Thus the
actual list contains six field-array ADD scans, one field-array swap and
one sign scan; it contains no native Fourier query.

Repeat this loop for every one of the mf internal bits. The bit factors
commute, so the two output operators are the inverse/full tensor chirps
`C^(tensor mf)` and `C^(-tensor mf)`, each of full native arity m. Their
native rank mass is2m, while the word uses zero native queries and no
helper or initialized field. The exact primitive count is

```
6mf field-array ADD scans,
mf field-array swaps,
mf sign scans.
```

If both output orientations must agree, one further ADDRESS flip of all
mf bits on the first field converts its inverse chirp to the forward
chirp: `C_total^2=X_all`, so `X_all C_total^-1=C_total`. The producer
checks this extra scan and its inverse; both final fields then have the
same full native forward operator.

This is O(mf) complete array traversals, not a constant independent of f.
In an ideal random-access array model its arithmetic work is
`O(mf*2^(mf))`; a physical tape controller/address implementation may add
further cost. The loop and its cost cannot be omitted from a supplier
invoice. In particular, the construction supplies no improved exponent.

`zero_helper_scan.py` independently checks every arbitrary dirty-input
coefficient, the full dense tensor target, the literal inverse and a
missing-ADD defect for `(m,f)=(1,1),(1,2),(1,3),(2,2)`. The displayed
per-bit identity proves the all-m,f statement. All scalar coefficients
remain exact rational pairs; no floating point or hidden dense operator
ADD is used by the checked word.

Consequently a claim that zero-helper arbitrary dirty linear algebra
forces total native rank at least the full-output rank is false without
additional quantitative premises. A possible constant-scan, bounded
conditioning, address-access or uniform-controller lower bound would
need its own precise statement and proof. This counterexample does not
settle any such stronger, cost-aware question.
