# Native tensor composition followed by strict rank cutoff

This note constructs a new finite mixed supplier from the source-bound native
inventory in [NATIVE.md](NATIVE.md). It then restores the strict rank separation
required by PR4359's compiler. The native program and interfaces come from
PR4359 at `da637c87c89482bc4c86be36bd0071b3d400dbed`; its integer lockstep
compiler builds on Jacob Alan Sussman's Theorem 1G. Apache-2.0; substantial
OpenAI/Codex assistance.

The result is conditional on the source arbitrary-input native words,
whole-job adapters, complete spectators, scalar and movement primitives, and
finite-program closure. It does not infer native correctness from a moment
histogram. The large new word is defined by finite algorithms and is not
materialized here.

## 1. A native product of two mixed units

Let a unit U have productive roles indexed by i, with canonical target ranks
`k_i`, and a chronological list of paid ranks `r_l`. Let a second unit V have
roles indexed by j, target ranks `h_j`, and chronological paid ranks `s_a`.
Every role is a distinct arbitrary complete array. Owned work fields have
separate identities and are not counted as productive inputs.
As in the source unit and its products, assume each native ambient rank is
its maximum productive rank and every paid rank fits that ambient space.

For each productive V role j, instantiate one U word at column multiplicity
`h_j`. Its productive arrays are the grid `(i,j)`. Use one common ambient
space of rank `max_i(k_i)*max_j(h_j)`, with the source whole-job embeddings
and complete spectators. Each U copy receives its own owned work fields.

Execute these U copies in lockstep through their common chronological paid
list. The all-column word has the same list of operations at every positive
column count. At paid position l, pause every U copy. Copy j requests one
complete canonical job of rank `r_l*h_j` on its designated physical owner.
These owners are distinct across j, since they belong to distinct U copies.
They may be productive fields or U-owned centers holding correlated data.

Use them as the productive roles of one V invocation at column multiplicity
`r_l`. Its j-th target is exactly the required rank `h_j*r_l`. Apply the
permitted complete-job coordinate matchers before the V call and undo them
after its completed endpoint. These matchers align arbitrary equal-rank axis
subsets; they do not relabel intermediate scalar contacts. The V call is
correct on all its distinct arbitrary input arrays, including correlated
values. Its own owned fields are fresh and distinct from every U field.

Complete V, restore all its whole-job adapters, and only then resume the
paused U copies. Never mix early and late requests of the same U copy in one
V invocation. This establishes chronology and excludes cyclic dependencies.

At the end, each `(i,j)` field has received the canonical rank `k_i*h_j`
job. The remaining paid calls, in the actual nested order, have ranks
`r_l*s_a`. Consequently, for any exponent tau,

```
target_moment(U product V) = target_moment(U)*target_moment(V),
paid_moment(U product V)   = paid_moment(U)*paid_moment(V).
```

This is explicit substitution of complete array programs. Scalar gates
remain scalar gates on roles. No claim that tensor power distributes over
matrix addition is used.

All intermediate U and V work fields persist until their actual owners clear
them. A safe allocation is one full bank per instantiated unit; every bank
is supplied, initialized, parked, and erased, with no productive credit.
There are only finitely many banks and operations in a fixed product word.
The source finite closure theorem must be applied with these new constants.

Iterating this construction n times gives exactly `B^n` productive roles,
target moments `T_tau^n`, and paid moments `P_tau^n`. The minimum and maximum
target ranks become `k_min^n` and `m^n`. Each finite word accepts all further
positive tensor multiplicities: lift every coordinate and every whole-job
matcher, while retaining the same chronological scalar word.

## 2. Restore strict separation by splitting only paid jobs

Write `tau=1-C`, where `0<C<1`, and choose an integer cutoff `J` strictly
below the new minimum productive target rank. For each paid job of rank
`R>J`, write `R=q*J+r`, with `0<=r<J`. Replace its canonical transform by
q complete rank-J transforms and, if nonzero, one rank-r transform on the
remaining disjoint axes. These calls occur consecutively in place of the
original paid job. The original whole-job phase/address adapters remain
outside the complete replacement.

The source splitting identity proves the same endpoint on arbitrary data
and spectators, at every column count. No new productive input is created.
The paid rank-one total is preserved. Concavity is needed only for the bill:

```
q*J^tau + r^tau <= R*J^(-C) + J^tau <= 2*R*J^(-C).
```

The last inequality uses `R>J`. The zero-remainder case omits the last call.
Unsplit lower-rank calls retain their original charge. If `P_1` is the base
unit's paid rank-one moment, the n-fold word therefore has complete paid
tau-moment at most

```
P_tau^n + 2*P_1^n/J^C.
```

This deliberately overcounts the original cost of the replaced large jobs.
It includes all paid calls, including those made on owned centers.

Choose `J=b^n` for an integer `1<b<k_min`, and define

```
alpha = P_tau/T_tau,
gamma = P_1/(b^C*T_tau).
```

If both alpha and gamma are strictly less than one, the normalized new
moment is at most `alpha^n+2*gamma^n`, which is below one for an effective
finite n. Every new paid rank is at most `b^n<k_min^n`, so PR4359's strict
separation hypothesis now holds. This is an additional rank-one tail premise,
not a consequence of the ordinary mixed moment inequality alone.

One general effective choice uses rational upper bounds `alpha<=a<1` and
`gamma<=g<1`: take an integer `n>max(1/(1-a),3/(1-g))`. The elementary bound
`x^n<=1/(1+n*(1-x))` gives `a^n<1/2` and `g^n<1/4`. The present certificate
is much smaller because it retains the exact rational power of g instead.

## 3. Exact source-bound application

The audited native construction gives each local helper its own arbitrary
productive field and pays each retained main idle window in full, as proved
in NATIVE.md. Its complete invoice is

```
targets = {5:196, 6:126, 7:392, 8:651, 9:1491, 25:448, 57:224},
paid    = {1:17409, 2:4991, 3:1568, 4:714, 5:140, 8:504, 16:448}.
```

There are 3,528 productive fields. The exact rank-one moments are
`T_1=47075`, `P_1=46851`, leaving the original surplus 224. The raw unit has
paid rank 16 and productive rank 5, so it cannot directly use the source
compiler's strict separation condition.

At tested saving `C=0.00247756=61939/25000000`, exact rational elementary
function enclosures prove

```
alpha < 999999999/1000000000,
gamma = P_1/(4^C*T_tau) < 999/1000.
```

Use `n=15000`, `J=4^15000`. A directly verified rational inequality is

```
1/(1+15000/10^9) + 2*(999/1000)^15000 < 1.
```

The certified surplus is greater than `0.00001439`. Thus this finite word
has a strict mixed moment at the tested saving, with

```
minimum productive rank = 5^15000,
maximum productive rank = 57^15000,
maximum paid rank       <= 4^15000.
```

The compiler's exit exponent satisfies
`theta<=log(4)/log(5)<7/8`, by the exact integer inequality `4^8<5^7`.
Unlike a cutoff only one below `5^15000`, this construction retains a fixed
gap `h=1/8` for the subsequent compiler bound.

Run the source-bound arithmetic certificate from the repository root:

```sh
python3 -I -B research/pr4359-tensor-strictification/strictification.py
```

The program first rechecks the native invoice. It then verifies both ratio
bounds and the complete power inequality, rejects a failed smaller trial
power under these particular conservative bounds, rejects gamma equal to
one, and rejects the unsupported raw saving 0.003. These are scoped checks
of the construction's sufficient inequalities; no minimal power is claimed.

## 4. Applying the existing uniform compiler

The new finite unit satisfies the same arbitrary-input, whole-job adapter,
spectator, chronological, and owned-storage contracts, together with strict
separation and a strict tested superpotential. Its positive rank-one surplus
is `47075^15000-46851^15000`; paid splitting preserves that total. The source
uniform compiler therefore applies at every strictly smaller positive saving.

For an effective explicit bound, let `t=1-C`, choose a desired uniform
exponent `z>t`, and put `z0=(t+z)/2`, `delta=z0-t`, and `h=1/8`. The source
exit estimate with the new m and r_max gives, for `x>=m`,

```
m*E(x)/x <= 4^n*57^(n/8)*x^(-1/8)
          < 2^((11/4)*n)*x^(-1/8),
-log2(z0*m^(z0-1)) < 1+6*n*(1-z0),
```

where the second inequality uses `z0>1/2`. It follows that

```
H0 = ceil(((11/4)*n*delta+1+6*n*(1-z0))/(h*delta)),
H1 = floor(H0*(1-z0)/(z-z0))+1,
N  = 2^H1
```

is sufficient, provided `H0>=6*n` covers the finite base range. The endpoint
certificate checks this condition and both strict inequalities at its chosen
uniform saving. The proof is the same complement induction with the actual
complement coefficient; it does not reuse the old exit constant 16.

After choosing N, recalculate the finite unit count, productive width, paid
leaf count, scalar word, owned storage, and precision/row constants from this
new exact word. Every such quantity is fixed before the eventual input grows.
The inherited analytic decomposition, permitted physical primitives,
fixed-tape model, and outer transfer remain conditional premises.

In particular, count raw native instances through both the tensor
substitution and the final uniform compiler, rather than counting each
large tensor macro as one unit. If this expanded count is `U_raw`, allocate
`O=U_raw` complete owned center banks. Let `W` and `P` be the final uniform
productive width and rank-one paid count. Count every non-scalar native
record and complete normalization in the new expanded word as `R`; this
includes the additional whole idle-window calls and every compiler/product
adapter. The unchanged scalar words have allowance `1147304*U_raw`.
Whole-job coordinate permutations and unit phases add no coefficient
height, but the source's conservative eight-per-record allowance gives
the safe new charge `G=1147304*U_raw+8*R`. All actual route work is charged
separately. This uses the new count R instead of reusing the old 460 paid
completion normalizers or old numerical G envelope. Substitute

```
Z = W+O,
E = 64*(Z+N+P+G+1)^3,
B = P+E,
C0 = 32*N*B^2.
```

The source completed-child semantic recurrence is then
`A(e)<=A(floor(e/N))+P*floor(e/N)+E`, giving `A(e)<=2*B*e` and the
same form of linear outer guard. No single center per tensor macro is
assumed. Allocated bank count, finite movement cost, and borrowed row stock
all use the fully expanded word. Reusing the source small-word numerical
constants without this substitution would not establish the precision or
storage interface.

Open next questions are to optimize the cutoff base and finite tensor power,
reduce the effective uniform rank, and certify stronger native mergers. A
favorable histogram alone would not justify any such native change.
