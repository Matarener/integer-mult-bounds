# Arbitrary-source compact switches at the batched CRT caller

This is an independent, scoped address-algebra audit of Cinna Davis's
[PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100), retained at
`337d04939571a637aeab54a0f58f54fde811663a`. The audited call is
[`CRT.md`, Section 4](../unconditional-batched-crt/CRT.md), used by the three
padded CRT conversions in [`PROOF.md`, “Address isomorphism”](../unconditional-batched-crt/PROOF.md).
The package source manifest fixes the actual bytes.

The result below confirms the arbitrary-function substitution at that caller
and supplies a literal inverse on the entire dirty address rectangle. It then
applies the existing exceptional-stream repair theorem. It does not establish
reservoir availability, ordinary interchange implementation, tape costs,
control-generation bounds, or the complete multiplication theorem.

## 1. Statement and complete domain

Let `r,G,H,K,N` be integers with

```
r >= 1, G >= 1, B = 2^G, H >= rG, K >= G+4.
```

Choose distinct target positions `j_0,...,j_(r-1)` such that the intervals
`[j_i,j_i+K)` are pairwise disjoint and lie in `[0,N)`. Their order need not
coincide with the order of compact digits. The caller uses positions of one
color modulo `K`; the proof only needs the stated disjointness. Its `K=64G`
satisfies the displayed bound. The bound ensures a nonempty guard interval;
empty-good-set variants of the repair argument are not needed here.

The complete address domain is

```
D = (Z/2^H Z)_u × (Z/2^H Z)_t × (Z/2^N Z)_y × W,
```

where `W` denotes the complete, arbitrary dirty back field and any additional
spectator fields. All word values are represented by their canonical
nonnegative integers. In particular, the inactive high digits of `u,t` are
included when `H>rG`; they are not fixed to zero or discarded on exceptional
addresses. The maps in this proof act identically on `W`.

Let `J={j_i}`. For each `i`, let `f_i` be a Boolean function on the complete
`N`-bit `y` field satisfying

```
f_i(y XOR 2^j) = f_i(y)  for every y and every j in J.       (1)
```

Thus each function omits **every active target**, not merely its own target.
It may depend on all other `y` bits, including target guards and unused high
bits. It is independent of `u,t,W`. Repeated application of (1) makes it
invariant under any subset of the target flips.

For a state define

```
u_i = floor(u/B^i) mod B,     t_i = floor(t/B^i) mod B,
z_i = u_i mod 2,             b_i = bit_(j_i)(y),
g_i = floor(y/2^(j_i+1)) mod 2^(K-1).
```

The good set `Q` consists of states satisfying, for every active digit,

```
u_i <= B-2,  t_i <= B-2,
2B <= g_i < 2^(K-1)-2B.                                    (2)
```

This is the predicate of `check_batched_crt.py:good`: the guard comparison
uses the `K-1` bits **above** the target parity. A predicate comparing the
whole `K`-bit segment without separating that parity would require a
different invariance argument.

Define the ideal switch by

```
T(u,t,y,w) = (u,t, y XOR sum_i f_i(y) 2^j_i, w).             (3)
```

Define the raw macro `S` by the literal operations in the next section.
The proposition is:

1. `S` and `T` are permutations of the entire domain `D`.
2. The explicit reverse word below computes `S^-1` on every state, including
   states outside `Q`.
3. `S=T` on `Q`, and `S(Q)=T(Q)=Q`.
4. On the complement `E=D\Q`, the existing correction key `T(S^-1(q))`
   permutes exactly the marked holes and restores each payload to its ideal
   destination.

The statement is for arbitrary admissible parameters and functions. The
finite checks supplied with this package are separate evidence about the
implementations and selected caller fixtures.

## 2. Literal word and inverse without a guard

Write

```
A(u,t) = sum_i 2 z_i t_i 2^j_i,
P(y)   = sum_i bit_(j_i)(y) B^i,
C(u,t) = sum_i z_i (1-2t_i) 2^j_i,
D(u,y) = sum_i (bit_(j_i)(y) XOR z_i) B^i,
L(y)   = sum_i f_i(y) B^i.
```

Here `D(u,y)` is a packed offset, distinct from the address domain `D`.
Every assignment to `u` or `t` is reduced modulo `2^H`, and every assignment
to `y` modulo `2^N`, immediately after that assignment. Offsets use the
**current** fields at that point in the word.

The four-step operation `F` is

```
y += A(u,t)
t += P(y)
y += C(u,t)
t -= D(u,y)
```

The complete raw word `S` is

```
F
u += L(y)
F
u -= L(y).                                                 (4)
```

Each assignment is a translation in one complete cyclic field, with its
offset independent of that field. It is therefore a permutation, even when
digits saturate, target carries escape the selected intervals, or the
modular field wraps. In particular, the two updates of `u` remain
permutations for arbitrary `f_i`; assumption (1) is not needed for raw
bijectivity.

Reverse the four assignments in order, using current controls:

```
F^-1:
    t += D(u,y)
    y -= C(u,t)
    t -= P(y)
    y -= A(u,t).                                           (5)
```

Each line exactly undoes the corresponding forward translation because its
controlling fields have already been restored to their values at that
forward step. Thus (5) is a two-sided inverse on the whole domain. Reversing
(4) gives

```
S^-1:
    u += L(y)
    F^-1
    u -= L(y)
    F^-1.                                                 (6)
```

The first and second evaluations of `L` in (6) use their respective current
`y` values. They need not be equal on bad addresses. Neither (5) nor (6)
assumes the guarded XOR identity, uses a forward permutation lookup table,
or assumes that `F` is an involution on bad states.

The source realizes the `t` and `u` translations by exchanging their entire
field with a back field, performing the ordered translation, and exchanging
back. Conjugating a translation by those swaps produces precisely the
translation above while restoring the arbitrary back field. This is an
address identity; the availability and cost of these swaps remain separate
caller obligations.

## 3. Guarded four-step identity for simultaneous targets

This section applies the compact four-step cancellation already used in
Douglas Colkitt's construction and proved in
[PR763, Section 1](../compact-carry-repair-audit/PROOF.md).
The relevant distinction is that the controls loaded between the two
completed operations will be functions of the same `y` field.

Fix an active segment, and write its initial value as `v_i=2g_i+b_i`,
where `0<=v_i<2^K`. For this one execution of `F`, assume only the
`t_i` and `g_i` conditions in (2). No nonsaturation condition on `u_i` is
needed: `F` reads only `z_i=u_i mod 2`.

The first addition increases this segment by `2z_i t_i`. Its parity stays
`b_i`. The guard keeps the intermediate segment in `[0,2^K)`:
the increase is at most `2B-4`, whereas the initial segment has at least
`4B` lower margin and more than `4B` upper margin. No carry reaches the
next selected segment or an outside bit.

The `t` update adds the original `b_i` to each active digit.
Since `t_i<=B-2`, all updated digits `t_i+b_i` are at most `B-1`.
There is no carry between compact digits, including from the highest active
digit into the unused part of the `H`-bit field.

The combined target updates have the exact integer identity

```
(2g_i+b_i) + 2z_i t_i + z_i(1-2(t_i+b_i))
    = 2g_i + b_i + z_i(1-2b_i)
    = 2g_i + (b_i XOR z_i).                                (7)
```

Both the first intermediate segment and this final segment are within
`[0,2^K)`. Consequently the signed second update has no borrow or carry
outside its segment. Because all selected intervals are disjoint, these
per-segment calculations hold simultaneously for the packed sums, with
every intervening and outside bit unchanged.

The final `t` subtraction reads

```
(b_i XOR z_i) XOR z_i = b_i.
```

It restores each digit, without borrowing into a predecessor or from an
inactive high digit. Thus, on this guarded domain, a completed `F`:

- flips target bit `i` by `z_i`;
- restores the entire `t` field;
- preserves `u`, every guard `g_i`, every non-target `y` bit, and `W`.

It therefore leaves the hypotheses needed for a second execution of `F`
intact, regardless of changes to the `u` parities between executions.

## 4. Arbitrary source functions at the two completed endpoints

Start in `Q`. The first `F` changes only bits in `J`, so (1) implies that
every `f_i` at its endpoint equals its value at the original state. This
remains true when a function reads a guard bit: guards can change during a
partial `F`, but they restore before `L(y)` is evaluated.

The load adds `f_i(y)` to each `u_i`. By (2),

```
0 <= u_i+f_i(y) <= B-1.
```

There are no inter-digit carries and no change to the inactive high part
of `u`. The loaded parity is

```
z'_i = z_i XOR f_i(y),                                     (8)
```

because `B` is even and the digit has not wrapped. A loaded digit may
equal `B-1`; this is permitted for the second `F`, whose proof in
Section 3 requires only the `t` and target guards.

That second `F` changes only targets, preserves all guards, and again
restores `t`. Equations (7) and (8) show that the two target changes
combine to `z_i XOR z'_i=f_i(y)`. Condition (1) also makes every `f_i`
at the second endpoint equal to its value at load. The final subtraction
of `L(y)` therefore restores the complete `u` field. This proves (3)
for every state of `Q`.

Moreover, (1) makes `T` an involution: its first application changes
only target bits and therefore leaves all its controlling function
values unchanged for the second application. It preserves `u,t,W` and
all `g_i`, hence preserves `Q`. Thus `T` is a permutation of `D`,
`T(Q)=Q`, and agreement gives `S(Q)=Q` as well.

## 5. Existing repair theorem with a literal reverse evaluator

We use the theorem proved in John-Michael Smith / @jp3isme's
[PR763, Section 4](../compact-carry-repair-audit/PROOF.md),
building on Douglas Colkitt's exceptional-stream construction. That
generic theorem and its distinction between hole coverage and payload
identity are predecessor results, not new claims here.

Since `S,T` are bijections and both preserve `Q`, both also preserve
`E=D\Q`. Therefore

```
R(q) = T(S^-1(q))
```

is a permutation of `E`. It is the identity on `Q`: if `q=S(x)` with
`x` good, then `S(x)=T(x)=q`.

After executing `S`, the payload at current address `q` originated
at `S^-1(q)`. Assigning its key by (6) followed by (3) gives its required
destination under `T`. Extract all current bad-address records, sort the
complete address keys together with their opaque payloads, and reinsert
them into the increasing sequence of marked holes. The keys are distinct
and their set is exactly `E`, so every hole is filled once. The payload
at key `a` originates at `T^-1(a)`, proving the complete desired
permutation for arbitrary payloads.

This is the missing executable distinction from using a table constructed
by exhaustive inversion of the forward word: (6) defines the address
inverse for every width and function, including exceptional inputs.
It does not itself prove a uniform tape tariff for evaluating the functions,
sorting keys, scanning guards, or moving records.

All coordinates that can change on bad executions belong to the complete
address key. In particular, inactive upper `u,t` digits and non-target
`y` bits must not be treated as invariant fibers merely because they
restore on good inputs. The back field and additional `W` spectators
are identities for every elementary word; their actual coordinate values
are retained unchanged in the full destination.

## 6. Binding to the stated CRT call

At a fixed balanced CRT tree level, an active axis lies in the right child
of one tree node. Its Beneš switch control uses its own non-target axis bits
and the left-child coordinates of that node
(`CRT.md:78–92`). Distinct nodes at that level have disjoint axes. All
active axes are right-child axes, so none is a left-child control axis.
Consequently each switch function omits every active target bit at the
level, and in particular every target in a selected color and batch.

The reservoir selection in `CRT.md:135–149` asserts that the borrowed
control fields lie outside those function dependencies. After the
specified placement swaps, its coordinate descriptors are recomputed.
Conditional on that advertised placement property, the functions are
exactly of the `f_i(y)` type in Section 1. This audit does not independently
prove that the claimed reservoirs are available at every recursive call.

Coloring by current position modulo `K` gives disjoint intervals for the
nonexceptional target positions. The source's separate treatment of the
last `K` positions (`CRT.md:201–213`) lies outside this compact lemma.
No omitted-highest-target completion is inferred from the present proof.

Thus the repaired compact operation implements the ideal simultaneous
switch for every address, not only globally valid CRT addresses.
Sequential composition of these exact switch permutations gives the
advertised switch program whenever its other caller premises hold. The
balanced CRT algebra, padding treatment, reservoir construction, boundary
operations, Beneš compiler, and their cost estimates are separate
obligations. The three-conversion call in `PROOF.md:68–78` is the concrete
downstream use; no claim about its final exponent follows from this
address-algebra audit alone.

## 7. A necessary all-target hypothesis

Requiring each `f_i` to omit only its own target is insufficient. Consider

```
G=2, B=4, K=6, r=2, H=4, N=12,
j=(0,6), (u,t,y)=(4,0,1040),
f_0(y)=bit_6(y), f_1(y)=0.
```

Both guards have `g_i=8`, in `[8,24)`, and the active `u,t` digits satisfy
(2). Each function omits its own target, but `f_0` reads the other active
target. The literal trace of (4) is

```
initial:          (4,0,1040)
after first F:    (4,0,1104)
after load:       (5,0,1104)
after second F:   (5,0,1041)
after unload:     (5,0,1041).
```

At the initial state both function values vanish, so the intended switch
would return `(4,0,1040)`. The raw word both flips the wrong target and
fails to restore `u`. This is a counterexample to a weakened hypothesis,
not to PR4100: its tree-level caller has the stronger all-target
independence verified in Section 6.

## 8. Evidence, limits, and attribution

The proof above is an integer derivation for the stated quantified
domain. Finite verification can check the literal forward and inverse
evaluators, compare source implementations, exercise the counterexample,
and verify complete keyed payload permutations in the declared finite
fixtures. Such tests do not establish the universal statement by sampling,
nor do their running times certify the asymptotic machine budget.

No selected frontier, predecessor predicate, or predecessor artifact is
changed. The audit does not discharge PR4100's remaining all-size,
compiler, precision, ordinary-callee, or fixed-tape obligations.

Credit Cinna Davis for the audited batched CRT construction and its
arbitrary-function claim; Douglas Colkitt for compact controls and the
repair construction; John-Michael Smith / @jp3isme for PR763's explicit
carry and exceptional-repair proof; and OpenAI and the attributed upstream
contributors for the surrounding framework. This contribution is by
Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance,
under Apache-2.0. It is not independent human peer review or a
proof-assistant formalization.
