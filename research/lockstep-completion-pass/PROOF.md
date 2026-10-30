# The completion/splitting pass as a lockstep rule, and nested owned-bank lifetimes

Two written lemmas with event-level corroboration. Both live inside the retained
contract of `FINITE-PRECOMPILATION.md` (Jacob Alan Sussman's Theorem 1G flow, the
integer batch clearing, source complements and exit substitution) and of
`p7-TENSOR.md` / `higher-moment-strictification` (zxv: chronological product, paid
completion of small targets on their own owners, disjoint splitting at a cutoff).
Nothing here changes a raw native word, a paid invoice, a moment inequality or κ.

Notation. A *rule* is a finite native unit: roles `(name_i, k_i)` on pairwise
distinct arbitrary fields, an ordered list of paid rounds `(r_j, owner_j)` where
`owner_j` is a role name or an owned bank name, and a fixed list of owned banks.
Its compiled rank-`N` program is the lockstep flow executed by `executor.py`
(derived from our `lockstep-live-role-audit/live_roles.py`, #4691), which keeps for
every physical field the stack of live roles and checks I1–I6 at every event.

## Lemma A. The pass produces a lockstep rule with an exact invoice

Let `U` be a rule whose paid ranks may overlap its target ranks, let `m` be its
ambient rank and choose integers `0 < J < L <= m`. Define `U' = pass(U, J, L)`:

1. every role of rank `k_i < L` gets rank `L`;
2. every original round `(r_j, owner_j)` is replaced by the consecutive rounds
   `(J, owner_j) x q, (r, owner_j)` with `r_j = qJ + r`, `0 <= r < J` (the
   remainder round is omitted when `r = 0`); the first of them is tagged `orig`,
   the others `piece`;
3. after all of these, for every role with `k_i < L`, the rounds
   `(J, name_i) x q', (r', name_i)` with `L - k_i = q'J + r'`, tagged `completion`.

**Claim.** (a) `U'` satisfies the hierarchy `r_max(U') <= J < L <= k_min(U')`, so the
finite compiler and the executor apply to it. (b) Every compiled program of `U'`
satisfies I1–I6; in particular every added job is a whole job on a field whose
current owner is the issuing unit, so no completion or piece ever touches a parked
ancestor, a sibling's field or an array outside the unit. (c) Rank-one mass:
`T'_1 - P'_1 = T_1 - P_1`, and the added target mass equals the added paid mass
`sum_{k_i<L} (L - k_i)`. For every `t` in `(0,1)`, the net-tax identity (1) of
`net-tax-rank-compiler/PROOF.md` holds:
`T'_t - P'_t = T_t - P_t - sum_j tau(r_j) - sum_{k_i<L} E(k_i)`. (d) Per unit
instance the pass adds exactly `sum_j (ceil(r_j/J) - 1)` piece rounds,
`sum_{k_i<L} ceil((L-k_i)/J)` completion rounds, `2 |{i : k_i < L}|` whole-job
normalizer records (inverse map at the input, map at the output of a completed
role) and one block-address relocation per piece or completion round. A compiled
rank-`N` program contains `U_total(N)` unit instances (one lockstep copy has
`sum_classes |C|` units; the program has `a` copies plus its nested complement and
exit programs), so every count of the program is `U_total(N)` times the per-unit
count plus the counts of the nested programs.

*Proof.* (a) After step 2 every paid rank is at most `J`; after step 1 every target
rank is at least `L > J`. (b) The compiler never looks at the owner of a round
except to decide on which field the unit issues the job; the executor checks at
every round that the field's top entry is the issuing unit (I3) and that the
previous child class has returned (lockstep). A `piece` round has the same owner
as its original job: between two pieces the child class of the first piece has
returned, the unit is resumed and owns the field again, so the second piece is a
legal round. A `completion` round of role `i` is issued on the role's own array
after all original rounds; by I4 all children have returned, the unit is the top
of that array's stack, and the job of rank `L - k_i` is served by a child class
exactly like any other round (the Pascal matching only uses ranks). The disjoint
axes `k_i .. L-1` exist on that array because its role now has rank `L` in `U'`:
in the flow a role of rank `L` at column `col` is an `L col`-axis job on its
array, of which the native word uses `k_i col` axes and the completion the rest
(`p7-TENSOR.md` §2). The general induction of #4691 (fresh sources, one job per
round on an owned field, distinct fields within a class, LIFO undoing) is
unchanged, since the pass only changes ranks and adds rounds of the same shape.
(c) Splitting preserves rank mass; completion adds `L - k_i` to the target and to
the paid mass of the same unit. Identity (1) is the regrouping of the four sums by
original job and by completed role; `verify.py` evaluates both sides exactly at
`t = 1` and with 60 significant digits at `t = 1 - C`. (d) is the definition of
the pass; the executor counts the records while it runs and the histogram-level
counter multiplies the per-unit counts by `U_total`; both agree on every case.

**Scope.** Lemma A is about the rule and the compiled flow. The native content of
a completion job (a positive transform on `L - k_i` disjoint axes) and of the
whole-job normalizers is the inherited all-column hypothesis; the identity
`(A tensor B) = (A tensor I)(I tensor B)` behind splitting is hypothesis 2 of
`FINITE-PRECOMPILATION.md` §1. The strict moment inequality that makes the
completed unit profitable is zxv's theorem; it is not re-proved here.

## Lemma B. Owned-bank lifetimes are nested; the stack allocation is sufficient

`FINITE-PRECOMPILATION.md` §6 allocates one owned-centre bank per compiled unit
instance ("the safe finite allocation"), notes that one bank per recursion depth is
insufficient, and says that a smaller reuse allocation "requires its own lifetime
proof". This is that proof for the lockstep schedule.

**Claim.** In the executed rank-`N` program, at every event the set of unit
instances holding live owned banks is exactly the union of the classes on the
current class path `C_0, C_1, ..., C_d` of the current program together with the
same sets of every program on the current nesting chain (an exit or complement
program running inside a round). Consequently bank lifetimes are properly nested
and a single LIFO stack of bank slots suffices; its peak occupancy is

```
peak(N) = max( max_s peak(N-s) ,
               max_path ( a * nb * sum_{j=0..G} |C_j(path)| + max_{r paid} peak(r * dil(path)) ) ),
```

with `nb` banks per unit, `a` the replication factor, `|C_j|` the class sizes of
one lockstep copy and `dil(path)` the product of the paid ranks along the path, so
that the exit programs of a path have ranks `r * dil(path)` (`counts.py`,
`Counts.banks`; `FlowCounts.exit_paths` keeps, for each deepest dilation, the
largest live inventory of a path reaching it). The maximum is over compatible
(path, exit) pairs: the path inventory and the exit rank are tied by the same paid
ranks, and adding the two separate maxima can overestimate (review of #5443: a
two-generation rule at N = 45 executes with peak 2048, the decoupled sum gives 2050;
it is a regression case in `verify.py` and a control in `test_verify.py`). The total number of instances is
`total(N) = a nb sum_classes |C| + sum_s (a S_s / B_{N-s}) total(N-s) + sum_e (a t_e / B_e) total(e)`.

*Proof.* A class allocates the banks of all its units when it starts and frees them
when it ends. A child class starts inside one round of its parent class and ends
before the parent advances to the next round (lockstep: the executor rejects an
eager parent). An exit program starts inside the last round of the deepest class
and returns before the next exit group; a complement program runs before the flow
and returns before any class starts. Every program restores all stacks on return
(I4). Hence the live set at any event is as claimed, allocation and release are
LIFO, and the peak over the execution is the maximum over the finitely many
(path, nested chain) combinations of the live counts, where a nested exit
program belongs to the path whose deepest class runs it; this is the displayed
recursion. The executor implements the stack allocator (`owned_policy="stack"`),
requires at every class end that the class's banks are exactly the top of the
stack (I7) and that a bank is free when allocated (its live-role stack is empty,
which is the erasure contract: a bank is cleared by its unit before release), and
records the peak; `verify.py` requires the measured peak and total to equal the
recursion on every executed case, in full-width and in partial (two-copy) mode.

**What it buys.** The owned-field inventory `O` in the retained storage count
`Z = W + O` can be the peak instead of the number of instances, with no change to
`G`, `E` or any moment. For the selected #5413 profile after the pass at `v = 1`
(`J = 20`, `L = 21`, 77,204 rounds per unit) and top rank `N = 3045` (one
generation), one lockstep copy has 84,996 unit instances but at most 7,793 live
at once; including replication and nested programs the ratio total/peak is 346
(RESULT.json). For `v = 1024` the recursion is defined but not evaluated.

**Rejected alternatives.** One bank per depth aliases simultaneously live units
(rejected, as in #4691). Releasing a class's banks before its rounds lets a child
class reuse a bank the parent still uses for a paid job (rejected by I3).
