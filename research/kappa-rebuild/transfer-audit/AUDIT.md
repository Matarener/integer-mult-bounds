# Adversarial audit of finite precompilation

Prepared with substantial OpenAI assistance, Apache-2.0. The mixed lockstep
tree and its potential argument are Jacob Alan Sussman's Theorem 1G. The
restored primary proof is
[`theorem-1g.md`](../architecture/sources/Sussman-563b4e6/research/record-track/proofs/theorem-1g.md),
from commit `563b4e6e913625637f36ba7869bf5fcd0dd4975a` of
[`wht-power-saving-lean`](https://github.com/jacobalansussman/wht-power-saving-lean).
The proposal independently scrutinized here is
[`FINITE-PRECOMPILATION.md`](../architecture/FINITE-PRECOMPILATION.md).

## Verdict and scope

The proposed finite precompilation bridge is valid under the native closure
hypotheses stated below. It does not follow from a mixed moment inequality
alone. The essential extra ingredients are independent arbitrary-input jobs,
canonical whole-job adapters, an ordered integer flow, and completion of each
source's complementary axes.

For the current complex candidate, the available finite certificates supply
the relevant ideal operator and alphabet closure. Two independent programs
in this directory check the concrete p2 boundary and a finite version of the
precompiler. They do not materialize the enormous near-threshold winning
supplier, prove a rounded multiplication implementation, or claim a new
kappa. The BIT weighted interface has separate compatibility obligations and
is outside this positive conclusion.

A correction was necessary: one owned center per recursion depth is not a
safe general allocation. Several units of a class can suspend with live
private centers. One center bank per compiled unit instance is a valid finite
upper bound. No such bank contributes productive output credit.

There is also a useful strengthening of the proposed argument: the exponent
existence step needs only an asymptotic bound on the **number of paid leaves**.
That bound follows directly from exact integer source/exit potentials. No
RAM running-time theorem, fluid row rounding, or unit-cost arbitrary
permutation assumption is needed to choose the fixed template size.

## 1. Precise conditional theorem

Let `C` be the fixed native complex kernel, and let a rank-s job mean
`C^(tensor s)` on specified complete coordinate axes, identity on all other
coordinates of the same array. All arrays have the same full ambient address
set. In the eventual column lift, every named axis becomes `f` axes and the
job rank becomes `s*f`.

Suppose a fixed mixed unit has target-role multiplicities `W_k`, a
chronologically ordered list of paid child calls of ranks `r_j`, and these
properties:

1. Its input roles are independent arbitrary arrays. Its completed endpoint
   is exactly one canonical rank-k job on each declared target role, without
   cross-role contamination. Every paid call has an explicit physical owner.
2. The unit, its paid-call normal forms, and its endpoint adapters are valid
   at every positive integer column multiplicity, on complete arbitrary
   spectators. The word consists of the retained scalar operations, permitted
   fixed binary-affine coordinate maps, unit Z4 quadratic phases, and the
   declared paid children.
3. Each completed job can be embedded on any prescribed subset of the fixed
   ambient axes by permitted fixed coordinate maps. A rank-a+b job is the
   product of its jobs on disjoint a and b axes. Adapters are actual whole-word
   operations; they are not permission to relabel an intermediate scalar
   contact.
4. Every owned workspace is explicitly supplied, initialized, preserved as
   long as needed, and cleared. Finite straight-line composition permits a
   finite fixed number of such work arrays and charges their actual scalar,
   movement, precision, and parking costs without counting them as outputs.

Put `m=max{k:W_k>0}`, `k0=min{k:W_k>0}`, and `r0=max_j r_j`. Assume
`1<=r0<k0`, and suppose `tau` in `(0,1)` satisfies

\[
\sum_j r_j^\tau=\sum_k W_k k^\tau.
\]

Then, for every real `z` with `tau<z<1`, there are fixed integers `N>=2`,
`B_N>=1`, and a finite native uniform supplier with exactly `B_N` independent
productive inputs and outputs. Its completed output on every productive
array is the full rank-N job. Its only paid children have rank one and their
number `P_N` satisfies

\[
P_N<B_N N^z.
\]

Its scalar word, coordinate matrices, productive width, owned storage, and
precision constants may be extremely large, but all are finite and fixed
before the eventual input size or tensor multiplicity is chosen.

The inherited ordinary supplier theorem can therefore be applied **after**
substituting these new constants and establishing its physical and precision
premises. The theorem above is a finite native circuit compilation statement,
not an unrestricted RAM-to-fixed-tape simulation.

## 2. Why a scalar balance is enough only after constructing the job flow

The integer tree uses a multi-index `a` on target ranks. Define

\[
c(a)=\prod_k k^{a_k},\qquad
u(a)=\frac{|a|!}{\prod_k a_k!}\prod_k W_k^{a_k}.
\]

The exact identity `u(b)=sum_k W_k*u(b-e_k)` matches **individual target
slots** to jobs issued by one specific parent round. Class labels include
the complete ordered round path, not just the resulting rank. This prevents
combining jobs from an early and a late round of the same suspended parent.

At top rank n, retain units with `m*rho*c(a)<=n`, where `rho` is the product
of the paid ranks on the class path and the degree decreases by one at every
class transition. Missing demands become independent sources; unmatched
paid jobs are forbidden. Strict separation `r0<k0` makes the Pascal matching
consume every parent output. The remaining source ranks s satisfy

\[
n/m<s\le n.
\]

Only the last class generation has exits. Every exit rank is smaller than n.
With `theta=log(r0)/log(k0)<1`, its largest rank is at most

\[
E(n)=r_0(n/m)^\theta.
\]

The exact tau-potential is conserved because each unit's input and paid
output potentials agree, and every matched internal job occurs once with
each sign. After dividing source counts by their total S, write source
weights `w_s=S_s/S` and normalized exit counts `x_e`. Then

\[
\sum_s w_s=1,\qquad
\sum_e x_e e^\tau=\sum_s w_s s^\tau.
\]

This is an identity for a vector-valued interface whose actual slots and
causal edges have already been matched. A bare histogram without that graph
would not supply the conclusion.

## 3. Exact finite batching and full-field completion

Induct on n. For every smaller rank t, assume a uniform program on `B_t`
arbitrary arrays is already available, with `P_t` rank-one paid children.
Use individual kernels for `n<m`; set `B_0=1,P_0=0`.

The integer tree at n has source counts `S_s` and an ordered sequence of exit
batches. Choose an integer a divisible by every smaller program width used
in an exit or source complement. More economically, a need only satisfy
`B_e | a*t` for each ordered exit batch of t rank-e jobs and
`B_(n-s) | a*S_s` for each complement group. A finite least common multiple
constructs such an a.

Take `B_n=a*S` distinct arbitrary source arrays. Assign each array to exactly
one source slot. First apply the complementary `(n-s)`-axis transform on
that array; this can be batched because its batch width is integral. Next run
a copies of the integer tree in lockstep. At each last-generation exit batch,
substitute the already compiled smaller uniform program and restore all of
its coordinate/role maps before resuming the suspended parent.

Each input array receives its s-axis job and its disjoint complementary job,
and hence receives the **full n-axis transform**. This statement remains
valid even if a unit temporarily acts on its spectators: its certified
completed endpoint fixes those spectator coordinates. An arbitrary input
may already have undergone its complementary transform.

New source arrays are globally distinct. Within a class, each parent issues
only one job per unit at that round, so incoming job arrays are distinct;
they are supplemented by fresh distinct source arrays. Consequently no
unit receives two aliases in roles that require independent arbitrary inputs.
A paid job on a parent's owned C0 may become an input role of a child unit;
that does not turn C0 into a productive outer input.

The exact normalized leaf recurrence is

\[
L(n)=P_n/B_n
=\sum_s w_s L(n-s)+\sum_e x_e L(e).
\]

Replication multiplies inputs, paid children, scalar passes, and workspace
instances together. It does not change L(n). The need for a huge a is thus a
constant-size issue after n is fixed, not hidden output credit or fractional
pieces of an array.

## 4. A direct leaf-count proof, without RAM timing assumptions

Choose `tau<z0<z<1` and put `delta=z0-tau`. Since sources have rank at least
`n/m` and exits have rank at most `E(n)`, potential conservation gives

\[
\sum_e x_e e^{z_0}
\le \left(\frac{mE(n)}n\right)^\delta
       \sum_s w_s s^{z_0}.
\]

The coefficient on the right tends to zero as n grows. Define
`eta=z0*m^(z0-1)>0`. For `t=s/n` in `[1/m,1]`, concavity gives
`1-(1-t)^z0>=z0*t>=eta*t^z0`. Therefore

\[
n^{z_0}-\sum_s w_s(n-s)^{z_0}
\ge\eta\sum_s w_s s^{z_0}.
\]

For all sufficiently large n the exit coefficient is at most `eta/2`.
Every exit and complement is strictly smaller than n, so strong induction
on the exact leaf recurrence proves `L(n)<=A*n^z0`; choose A to cover the
finite smaller range. It follows that `L(n)<n^z` for some fixed n=N.

This proof does not price a growing-rank arbitrary permutation as a unit
RAM operation. It only counts the native paid leaves of a finite circuit.
All remaining operations will be fixed operations after N has been chosen.
Their real implementation costs are addressed by the inherited native
supplier interface in the next section.

For rational z, the strict test is effective: for `z=a/b`, compare exact
integers `P_N^b < B_N^b*N^a`. Enumerating finite N and constructing the exact
integer programs eventually finds a success by the preceding bound. No
numerical estimate of a hidden asymptotic constant is necessary for this
effective existence statement. The present artifact has not run this
potentially astronomical search for the near-threshold p2 instance.

## 5. Native column lift and fixed-tape closure

The local complex replay proves an identity over rational coefficients and
free noncommuting operator words. Warps are formal generators; only genuine
inverse cancellation is used in those words. A column lift sends a frame or
warp operator G to its f-column copy. This substitution preserves products
and inverses and extends linearly on the free group algebra. Scalar ADD and
SCALE coefficients are unchanged. Thus the logical role-word identity holds
at every f.

This argument does **not** assert that tensor power is additive on arbitrary
matrix sums. It uses the stronger free-word identity that was actually
checked. Separate isolated exact physical identities, such as a child
factorization or a helper normal form, are tensor-powered as identities of
operators. Their base absolute phases must be included before lifting.

A rank-zero native monomial has the form

\[
|x\rangle\longmapsto i^{a+q(x)}|Mx+b\rangle,
\]

where M is invertible binary, b is binary, and q is a Z4 quadratic phase.
On f columns it acts columnwise, with phase
`a*f + sum_column q(x_column)` modulo four. Its binary map is a direct sum of
f copies of M, up to the fixed interchange between column-major and
slot-major notation. Translation b is repeated in each column. A rank-r
child becomes exactly `C^(tensor rf)`; spectators remain complete ranges.

Every new coordinate route in the finite precompiler is a fixed coordinate
permutation on N named axes. It is a permitted special case of the fixed
binary changes of basis. After tensor lifting it permutes the corresponding
f-axis blocks. A fixed invertible binary matrix decomposes into a fixed
number of row additions and exchanges. The retained packed selected-bit
implementation provides these operations on fixed tapes, at its established
compact-movement cost; they are not assumed to be arbitrary linear-time
address shuffles.

Primary local interfaces are documented in
[`general-clifford-frames.tex`](../../../notes/general-clifford-frames.tex),
[`endpoint-gauge-complex.tex`](../../../notes/endpoint-gauge-complex.tex),
[`05-layers.tex`](../../../upstream/build/sections/05-layers.tex), and
[`compact-control-movement.tex`](../../../notes/compact-control-movement.tex).
The first two explicitly supply exact monomial lifts and columnwise phase
normalization. The latter two provide the fixed binary basis operations,
complete fields, compact control, and row reservations.

All slots and role indices of the precompiled word are fixed constants. Its
actual scalar and movement operations, including pre/post adapters, add
fixed multiples of the existing per-node scalar/compact overhead. They can
be placed in a finite program and executed with a fixed number of role and
work tapes. The parking construction in
[`04-swap.tex`](../../../upstream/build/sections/04-swap.tex) and the complex
layer's depth-first schedule then apply to the resulting ordinary supplier.
No data-dependent scheduler or new random-access operation is introduced.

## 6. Storage, precision, and the ordinary recursion

Let the fixed compiled supplier have B productive arrays, P rank-one calls,
O owned work arrays, and a finite scalar/movement word. At one ordinary
recursive node, each productive role stream and each owned stream has the
same logical shape, of volume `V/B`. Owned arrays therefore contribute
fixed overhead and storage proportional to `O*V/B`, but the paid recursive
coefficient is still `P/B`. A paid call on an owned field is counted in P.
Splitting its complete rows into B child roles is legitimate because its
payload is arbitrary and the child contract is the same arbitrary-input
contract.

Reserve a bank per finite compiled unit instance, or supply a verified
smaller liveness allocation. Retain it through nested child calls and erase
it at its actual endpoint. Extra work arrays are excluded from B. Park them
along with inactive productive arrays. Both O and the number of node calls
are fixed, so this adds a fixed coefficient to the existing linear parking
cost.

The row stock is based on B, not B+O. Its reserved-axis coefficient may be
very large, but is fixed: the retained bound is proportional to
`ceil(log2 B)*log_N(d)=O(log d)`. The new child ratio is `1/N`, with a strict
hierarchy and `N^2>2` for the old halving guard.

The scalar alphabet remains Gaussian dyadic. Every fixed scalar coefficient,
its preparation, every unit phase, and every precompiled intermediate prefix
must be included in a new finite coefficient-depth constant. The old scalar
cap cannot be reused. A conservative semantic recurrence can charge all P
completed rank-f children and the actual finite local scalar charge E:

\[
A(e)\le A(f)+Pf+E,\qquad f=\lfloor e/N\rfloor.
\]

Completed child entries have dyadic denominator and absolute-row-sum bounds
exponential in their rank; the retained semantic guard uses exactly such
completed-child bounds. Choosing a sufficiently large fixed coefficient
gives `A(e)=O(e)`. Monomial unit phases and address maps add no magnitude or
denominator growth; their evaluation time is still charged. Finite remainder
axes are included in E. This is the appropriate route to re-establish the
precision premise; the finite audit does not reuse a previous numerical
invoice or claim to have written every outer threshold constant.

## 7. Independent finite evidence

Run from the repository root:

```sh
python3 -B research/kappa-rebuild/transfer-audit/finite_dag_audit.py
python3 -B research/kappa-rebuild/transfer-audit/native_boundary_audit.py
```

The first program does not import the source tree or scheduling checker. It
constructs explicit unit instances, target slots, physical field identities,
owned fields, chronological paid calls, and start/issue/finish dependencies.
It checks every ordered batch's divisibility and the full-axis completion of
every independent source. Six synthetic sizes exercise both complementary
recursion and up to two lockstep generations. A deliberately added dependency
on a future parent round is rejected as a cycle; an aliased input role and an
uncleared batch denominator are rejected. At rank 40, the complete synthetic
uniform circuit has 91,854 productive fields and 2,242,264 paid rank-one calls;
the exact integer inequality `P^10 < B^10*40^9` verifies an exponent below
9/10 including every complement. This synthetic rule is a scheduling test,
not a newly certified native circuit.

For the actual p2 rule, paid calls and their owners are extracted in order
from the authenticated THREE-base native words and global helper assignment.
At rank 41, one exact finite compilation has:

| Quantity | Checked value |
|---|---:|
| Independent productive arrays | 1,397 |
| Mixed source ranks | 146 of rank 6; 803 of rank 9; 448 of rank 41 |
| Native paid calls before rank-one expansion | 18,082 |
| Paid rank-one calls after all source complements | 57,149 |
| Full identity baseline `41*1397` | 57,277 |
| Complete rank-unit saving | 128 |
| Owned center arrays, uncredited | 1 |
| Event-DAG vertices | 36,166 |

This small rank-41 supplier is not the near-threshold winning supplier.
In particular, crediting its rank-6 or rank-9 sources as full rank 41 without
their complements would be an accounting error; those complements are
explicitly included in 57,149.

The second program independently checks all 2,240 forward/backward main
contacts and all inverse contacts, using direct Fourier symbols on the 862
addresses that determine their degree-two Z4 phases. It verifies all 2,040
helper bindings and 259 serialized helper coordinate maps. Changing one
affine shift is detected. It also verifies that THREE-base and THREE-extra
have identical original ports and all 632 external start/end references;
their only differences are an internal frame and its warps. Constant
THREE-base selection is thus legal for this local external contract.

The helper pre/post maps act around whole native invocations. Their use is
justified by the certified autonomous helper block: independent helper input
normalization cannot change a main output, and helper output normalization
acts on an independent completed helper job. Internal scalar gates retain
their original shared frames. Common outside-nine-axis spectators commute
with the local word and do not enlarge its paid rank.

## 8. What remains before a kappa admission

The positive conclusion is an ideal native uniformization theorem under
retained primitive contracts. A final integer-multiplication claim must still
choose a strict exponent, pair it with the actual admitted BIT supplier,
write the resulting ordinary scalar/precision/row constants, and replay the
outer analytic inequalities. The large template can be specified by an
effective finite generator and existence proof; if a concrete materialized
template is required by an admission policy, that is a separate gate.

The checked p2 source and the two audit receipts are immutable inputs to this
audit. A later controller with a different target histogram needs its own
native endpoint and owner certificate. The general theorem is reusable,
but the existing p2 receipt must not be relabeled as that new certificate.
