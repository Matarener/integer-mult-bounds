# Exact spatial cut ranks for repeated Walsh transforms

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.**
For a fixed linear program on one sequential tape, repeated Walsh transforms
have different unavoidable head-travel bills under two common data layouts.
For N Walsh addresses, m independent columns and one carried field register,
the proved lower bounds, in unit cell moves, are

```text
address-major:  (Nm)^2 / 2
column-major:   m N^2 / 2 + 2(m-1).
```

These are lower bounds, not attained minima. For N=8 and m=4 they are 512
and 134. The underlying sums of directional communication ranks are 512
and 128; the extra six column-major moves account for crossing the three
boundaries between whole columns and returning. A zero communication rank
at such a boundary does not make physical travel free.

The new result is the exact pair of layout profiles and their complete
one-head travel conversion, including arbitrary positive register capacity.
The communication-rank argument is classical. This is a side result for the
`precision_tape` obligation, not a new supplier, κ or complete multiplication
theorem. The selected construction permits multiple tapes and is not excluded.

## Machine and endpoint

Let F be any field of characteristic other than two, N=2^h with h>=1,
m>=1, and s>=1. Let

```text
H_N[a,b] = (-1)^(popcount(a & b)),      0 <= a,b < N.
```

The Nm independent input scalars occupy consecutive cells 0,...,Nm-1.
The endpoint replaces each column x[:,c] by H_N x[:,c] in those same cells.
Two physical encodings are compared:

```text
address-major position(a,c) = a m + c,     matrix H_N tensor I_m;
column-major  position(a,c) = c N + a,     matrix I_m tensor H_N.
```

There is one movable head and s carried field registers. At its current
cell it may apply any fixed F-linear operation to that cell and the
registers. It may move one cell at a time. Control, coefficients and the
entire address schedule are independent of input values. No other head,
remote-cell operation or source-dependent channel is available. Scratch
cells outside the data interval and the carried registers may start with
arbitrary independent dirt; any used scratch must be restored. The head
starts and finishes at cell zero. There is no requirement to preserve the
original data separately.

This permits destructive local linear updates and arbitrary coefficients,
not merely a chosen butterfly gate list. It excludes nonlinear encodings
of several field values into one register, input-dependent control or head
positions, changed output placement and additional data tapes. The lower
bound does not charge local arithmetic, which can only add work.

## General directional cut bound

For any prescribed linear endpoint matrix M, cut the tape between q-1 and q.
Let L and R denote the data indices on its two sides. Write

```text
r_left(q)  = rank M[L,R],
r_right(q) = rank M[R,L].
```

If the head crosses right to left c_left times and left to right c_right
times, then

```text
s c_left >= r_left(q),        s c_right >= r_right(q).
```

To prove the first inequality, keep only dependence on the initial right
input variables. All initial left cells and independent scratch then have
zero dependence. Every right-to-left crossing imports at most s linear
forms. Between such crossings, every left-side operation only takes linear
combinations of forms already available there. Outgoing messages cannot
enlarge this space. Consequently all final left outputs lie in the span of
at most s c_left imported forms. Their coefficient matrix is M[L,R]. The
other direction is identical after exchanging the roles of left and right.
Interaction, reuse, destructive updates and dirty scratch do not change
this span argument. The starting registers contain independent dirt, not
input-dependent information.

Every cell must receive a nonidentity output for this Walsh endpoint. In
particular the head must reach the last cell. Since it returns to zero,
each internal data boundary is crossed at least once in each direction.
Thus the total number of unit moves obeys

```text
moves >= sum(q=1..Nm-1) [max(1,ceil(r_left(q)/s))
                         + max(1,ceil(r_right(q)/s))].
```

A unit move crosses exactly one boundary. Extra visits outside the data
interval only increase the move count. The proof does not assume that all
cut demands are simultaneously attainable.

## Exact Walsh cut profiles

First consider a single H_N, cut after k coordinates. Both directional
ranks are min(k,N-k). For k<=N/2, the first k rows and the last N/2 columns
form the first k rows of H_(N/2), by the block recursion

```text
H_N = [ H_(N/2)   H_(N/2) ; H_(N/2)  -H_(N/2) ].
```

Those rows are independent because H_(N/2) is invertible. For k>=N/2,
take the first N/2 rows and the last N-k columns instead; these columns
of H_(N/2) are independent. The opposite block is the transpose, so it has
the same rank. The endpoint cases k=0,N have rank zero. Invertibility uses
H_N H_N^T = N I and the characteristic hypothesis.

For address-major storage write q=km+r with 0<=r<m. Exactly r columns
have k+1 coordinates on the left; the other m-r have k. Independence of
the columns gives the rank in either direction as

```text
r min(k+1,N-k-1) + (m-r) min(k,N-k) = min(q,Nm-q).
```

Indeed for k<N/2 the expression is km+r; for k>=N/2 it is Nm-km-r.
For column-major storage only the partly cut column can communicate across
the boundary. Whole columns have no endpoint dependence on other columns.
The rank in either direction is therefore

```text
min(q mod N, N-(q mod N)).
```

These equalities give exact cut ranks for every h,m and every cut, not just
the finite fixtures below.

## Register-dependent closed form

For an even positive L define

```text
F(a,s) = sum(j=1..a) ceil(j/s)
       = s u(u+1)/2 + (u+1)v,          a=us+v, 0<=v<s;
B(L,s) = 4 F(L/2-1,s) + 2 ceil(L/(2s)).
```

The formula for F groups s successive equal ceiling values. The ranks in a
single even block are 1,2,...,L/2,...,2,1, which proves the formula for B.
Substituting the exact profiles into the general cut bound gives

```text
address-major moves >= B(Nm,s);
column-major  moves >= m B(N,s) + 2(m-1).
```

For s=1, B(L,1)=L^2/2, giving the displayed bounds. Even without the
ceiling corrections, address-major storage forces at least (Nm)^2/(2s)
moves. With fixed N and s this excludes a travel bill linear in m for that
one-head layout. The column-major cut bound grows linearly in m. This does
not by itself construct a linear-in-m program or compare optimal runtimes.

## Reproduce and finite evidence

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/walsh-tape-cut-area/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/walsh-tape-cut-area/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/walsh-tape-cut-area
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/walsh-tape-cut-area --check-source-history
```

Substitute another CPython 3.12 executable on another machine. Both registered
commands print `PASS_WALSH_TAPE_CUT_AREA`, counts and a generated SHA256-bound
receipt on stdout. Redirect logs outside the checkout; replay writes no files.

The verifier constructs 32 literal integer endpoint matrices for N in
{2,4,8,16}, m in {1,2,3,4} and both layouts. Fraction elimination computes
both directional ranks at all 568 internal cuts. It independently sums those
ranks and the ceiling demands for seven register capacities, checking 224
closed-form travel bounds.

A separate local-gate interpreter executes 18 programs for N in {2,4,8},
m in {1,2,3} and both layouts. Each butterfly borrows one arbitrary dirty
register: swap it with the first data cell, apply a two-variable Hadamard
at the second cell, then swap it back at the first. Independent initial
symbols verify every endpoint column and register restoration. The inverse
uses the reversed gate list and a half-Hadamard, and its full product is
checked. The programs execute 612 local gates and 2,358 enumerated unit
moves; 150 spatial cuts satisfy both directional demands. These programs
are feasibility controls, not optimal upper bounds.

Eleven controls cover invalid dimensions, a wrong layout, a zero-rank
inter-column boundary, omitted inter-column travel, omitted dirty restoration,
a changed gate, register-capacity sensitivity and an unpaid remote shortcut.
The last control checks that a nonzero communication demand cannot have a
zero-move local realization; it does not execute a remote-operation machine.
Explicit exceptions keep the checks active under optimized Python.

## Limits and engineering choices

The all-size theorem is the written argument. Finite replay is corroboration,
not a formal proof. No production tape layout, complete native caller,
precision ledger, bit encoding or selected supplier is instantiated. Several
heads, extra data tapes, reordering or source-dependent side information can
change the obstruction. Field-operation and bit-operation models are distinct.
Independent human and formal proof-kernel review are unclaimed.

The checker accepts no external data and caps matrices at 64 cells, its
local word at 4,096 gates, and the main census at fixed finite ranges. There
is no recursion or subprocess. Functions are below 60 lines. Python/Fraction
allocation is a managed-runtime deviation from fixed memory allocation, bounded
by these finite matrices and words. Warning-strict normal and optimized
execution provide the interpreter diagnostics. No global linter or repository
build setting is changed.

## Sources, overlap and credit

Base main is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The scope changes the `uniform-transfer-audit` card to an original restricted
backend obstruction; it does not purport to discharge the selected
`precision_tape` assumption. The selected source-binding positive control
passed before the investigation. No predecessor executable is imported or
replayed as the deliverable. [The advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226107)
states this question.

Credit zxv's [PR #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441)
for the distinction between fixed transfer representations and unpriced
physical movement, and ToikY's [PR #4192](https://github.com/CrocSwap/integer-mult-bounds/pull/4192)
for the distinct explicit sequential scan compiler. Their results are context,
not mathematical premises. Nick Petalas's #5148 studies stable lane passes;
its indivisible-record/tape-lane model and reversal question differ from the
one-head local linear machine and independent-column transforms here. This
is not a continuation of that result.

Communication-based one-tape lower bounds are classical; see, for example,
[Dietzfelbinger's 1996 linear-array paper](https://eccc.weizmann.ac.il/eccc-reports/1996/TR96-063/index.html).
The linear-span proof above is self-contained. The Walsh matrix, Kronecker
products and rank subadditivity are background, not new general methods.
No global literature-priority claim is made.

Entry overlap checking covered all 361 open PRs and 5,562 Discussion records
in the helper's reported complete remote pagination. The sparse local note
scan covered 205 of 8,136 tracked note paths; separate all-main README
searches covered the named layouts, Walsh/tape and cut-rank/head-travel terms,
and live merged searches were inspected. Recent account PRs and the local
claims were checked. This bounded, non-atomic search is not a novelty proof
and does not cover unpublished work or arbitrary diffs.

## Open next questions

1. Construct matching-order head-travel upper bounds in these exact layouts,
   with scratch restoration and a literal schedule. This would determine
   whether the layout-specific lower bounds describe the true order of
   growth. Start by processing complete column programs consecutively;
   finite butterfly feasibility alone does not establish the best schedule.
2. Bind one actual native caller's data layout and moving register budget to
   this model, or identify the extra tape/head channel that escapes it.
   This would decide applicability to production. Its data placement,
   head motion and side information are not supplied here.
