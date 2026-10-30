# Exact joint-restriction gate

## 1. Fixed source and quantified model

Let T be the decoded scalar map of the pinned PR5827 word. Its 770 public
coordinates are independent. Its 29 owned coordinates start arbitrary; INIT
must erase their input columns, and all owned outputs are zero. On public
coordinates, T is the identity plus the 104 prescribed X-to-Y shears.
The exact forward and transpose checks establish these statements for this
finite scalar word. Native realization is a retained source premise.

Partition the public coordinates into 666 groups: one pair `{r,r+112}` for
each live main port r, and one singleton for each of the 562 helpers. Choose
any set D of groups to remove. Retain at least one main pair. Set removed
inputs to zero and omit removed outputs. Paired main removal ensures that
T has no coupling between a removed pair and a retained pair.

At every original paid query e, compute the exact decoded prefix row and
suffix column on the original word. Let A_e and B_e be their group supports.
The discovery model permits removal of e if

```
A_e is contained in D, or B_e is contained in D.
```

The first condition makes the original argument zero. The second condition
makes a change in the original queried field invisible to retained outputs.
Grant both conditions independently, at every query. Their simultaneous
physical implementation is not assumed. This is a relaxation: a candidate
that uses only these original support discounts cannot receive a larger
discount. A candidate that changes the arguments or creates new cancellations
is outside this model.

The replay uses exact rational coefficients. No modular rank or sampled
column is used in the certificate. The source query count is 3455. The scalar
map and its transpose are checked on all 799 input labels; owned input columns
are erased. The current query ranks and helper target ranks are read from the
source frames. Their complete histograms equal the published source receipt.
No new native phase assertion follows from this scalar check.

## 2. Complete price and rational bounds

Put H_r = r^(1-kappa). For a helper group g, let w_g be H_r at its original
productive target rank r. For a main-port pair, define

```
w_main = [2 H_145 - 15 H_1
          + 2 sum_(l in {7,8}) sum_(j=1..l)
                (H_(1+8(j+1)) - H_(8(j+1)))] / 18.
```

There are 18 full calls, 15 thin shears and two main lanes per port on the
length-seven and length-eight paths. Thus the complete moment margin divided
by 18, for a candidate in the relaxation, is

```
Phi(D) = sum_(g not in D) w_g
         - sum_(e not granted removal) H_rank(e).
```

The implementation reconstructs the original full invoice from these terms.
It matches 66870 paid calls and 13444 productive fields, including every whole
idle and thin query. New nonnegative costs are omitted favorably.

The tests use the exact rational values `.003124767` and `.003156014468`.
The latter equals `101/100` times the declared source `.00312476680`.
No interval monotonicity statement is used.

For an integer r, write r = 2^m u with 1 <= u < 2. For
z = (u-1)/(u+1), use

```
log u = 2 sum_(j>=0) z^(2j+1)/(2j+1).
```

After 32 terms, the remaining positive tail is at most
`2 z^65 / [65(1-z^2)]`. Apply the same bound to log 2 with z=1/3.
This gives rational L <= log r <= U. Here `0 <= kappa U < 1`.
The alternating exponential series of degrees 13 and 14 gives

```
r sum_(j=0..13) (-kappa U)^j/j! <= H_r
H_r <= r sum_(j=0..14) (-kappa L)^j/j!.
```

All terms are rational. Use upper bounds for retained target terms and lower bounds for retained
paid terms. In w_main, use lower bounds on its subtracted idle terms.
At scale S=10^12, round target weights upward to integers c_g and query
weights downward to integers p_e. Then

```
S Phi(D) <= sum_(g not in D) c_g - sum_(e retained) p_e.
```

Rounding is done on retained terms. Thus removing a term removes the same
integer from the total; no inconsistent debit is introduced.

## 3. Branch coverage and flow dual

A branch fixes a set Y of removed groups and a disjoint set N of retained
groups. If A_e meets N, the input condition is impossible on this branch.
If B_e meets N, the output condition is impossible. If both are impossible,
the query is not granted a discount. If exactly one remains possible, use
its complete support as a necessary removed set. If both remain possible,
use A_e intersect B_e as a necessary removed set. Remove Y from this set.
Call the resulting free-group set K_e.

Merge equal K_e and add their integer query prices. This produces terms
(K_i, p_i). Set C = sum_g c_g - sum_e p_e. The branch margin is at most

```
C - sum_(g in Y) c_g
  + sum_i p_i v_i - sum_(free g) c_g z_g,
```

where z_g is the removal indicator and v_i <= z_g for every g in K_i.
This implication is only a necessary condition. Replacing the true query
predicate by it can only increase the upper bound.

The certificate supplies nonnegative integer allocations f_ig only on
edges g in K_i. It satisfies

```
sum_g f_ig <= p_i,       sum_i f_ig <= c_g.
```

Since v_i <= z_g, subtracting the allocated parts and using these two
capacity inequalities gives

```
sum_i p_i v_i - sum_g c_g z_g <= sum_i p_i - sum_ig f_ig.
```

The checker validates every edge and both capacities. It does not solve a
flow problem. Every priced leaf has the strict integer bound

```
C - sum_(g in Y) c_g + sum_i p_i - sum_ig f_ig < 0.
```

Every internal node splits one previously free group into its retained and
removed cases. The checker visits both children and rejects reuse, an absent
child or an unused node. A leaf may instead exclude a branch where all 104
main groups are removed. Induction on this finite tree covers every subset
with at least one retained main group. There are 233 nodes at the near gate
and 221 nodes at the one-percent gate.

The least negative certified local upper bounds are respectively
`-2481461/10^12` and `-46854465615/10^12`. Therefore every admissible subset
in this relaxed model has a negative complete moment margin at each tested
saving. The conclusion is pointwise and source-bound.

## 4. Controls and remaining obligations

The original source has a strictly positive rational lower margin at its
published `.00312476680` claim. It is a positive price control. The certificate
checker rejects a changed saving, repeated branch, false empty-main leaf,
nonnegative leaf bound, negative flow, excessive flow and a Boolean flow value.
All decisions use explicit checks and remain active under Python optimization.

The optional search uses a flow solver to find allocations and floating-point
scores only to choose branches. Neither the scores nor solver status is trusted
by replay. The exact integer allocation and complete tree are the proof data.

This proof does not create a new native word, confirm a compiler assumption,
prove a bound for changed input relations, or establish a universal exponent
ceiling. It does not count the absence of a search hit as proof. The two exact
certificates are the evidence for the stated finite restriction model.
