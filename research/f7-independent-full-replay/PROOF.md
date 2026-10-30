# Finite scope and completeness argument

This package concerns the abstract PR943 singleton prefix-walk model only.
Fix `n=7`, an even word length `L`, and a label word
`w=(w_1,...,w_L)` over `{0,...,6}`. Define `q_0=0` and
`q_i=q_(i-1) XOR 2^w_i`. A restored word uses each label a positive even
number of times; consequently `q_L=0`. Its prefix set is
`P={q_0,...,q_(L-1)}`. Universality means `P+P=F_2^7`.

## The necessary collision budgets

The parity of the Hamming weight of `q_i` is `i mod 2`, since every step
flips one coordinate. Let `E` and `O` be the distinct prefix states of even
and odd weight, with sizes `s` and `t`. At `L=20`, each has size at most 10.

For each nonzero even mask `x`, let `A_x` and `B_x` count its unordered
representations by distinct pairs from `E` and `O`. Put

```
a = C(s,2) - |supp A|,       b = C(t,2) - |supp B|.
```

Universality requires all 63 nonzero even masks in `supp A union supp B`, so

```
a+b <= C(s,2)+C(t,2)-63.                       (1)
```

For each odd mask `y`, let `r_y` count its representations by `E x O`. There
are 64 odd masks and `s*t` cross pairs, hence the cross-excess at a universal
leaf is `s*t-64`.

The collision identity is

```
sum_y C(r_y,2) = 2 sum_x A_x B_x.
```

It follows by counting an unordered `E` pair and `O` pair with the same sum:
their four cross pairs form exactly two unordered colliding pairs. Since every
odd mask is represented, `C(r_y,2) >= r_y-1`, giving

```
sum_x A_x B_x >= ceil((s*t-64)/2).               (2)
```

On the common support of `A` and `B`, write
`A_x B_x=1+(A_x-1)+(B_x-1)+(A_x-1)(B_x-1)`. Summing and using (1)'s exact
support count bounds the left side of (2) above by

```
B0 + a*b,  where B0=C(s,2)+C(t,2)-63,
```
subject to `a,b>=0` and `a+b<=B0`. Thus a split can be discarded if no
integer pair `(a,b)` satisfies both inequalities.

For `s>=t`, the elementary pair-capacity necessities
`C(s,2)+C(t,2)>=63` and `s*t>=64`, with `s,t<=10`, leave
`(10,10),(10,9),(10,8),(10,7),(9,9),(9,8)`. The last split has `B0=1` and
right side of (2) equal to 4, but `B0+a*b<=1` for all nonnegative integers
with `a+b<=1`; it is impossible. Therefore only the five searched splits
remain.

There is no loss from sorting the split. Cyclically rotating a restored word
by one label translates its prefix set by the odd-weight vector `q_1`.
Translation preserves pairwise-XOR coverage and swaps `E` with `O`.
Coordinate relabeling then restores first-occurrence canonical form while
preserving Hamming-weight parity. Every reversed split therefore has a
representative in the five searched cases.

## Search completeness and prune soundness

`replay.c` visits restricted-growth label words. Relabeling each coordinate
by order of first appearance maps every word to exactly one such form; this
coordinate permutation preserves closure and universality. Label counts are
checked so every label occurs positively and evenly at a closed leaf.

The engine stores the *distinct* prefix states in two lists, separated by
Hamming-weight parity. For every newly seen point, it inserts all new same-side
pair differences into an exact byte frequency table and increments the even
collision excess once for each difference already supported. It similarly
tracks cross differences and odd excess. A repeated prefix state contributes
no new pair. Thus both excess counters are nondecreasing along a branch.
Each class has at most 10 points, so a same-side difference frequency is at
most `C(10,2)+C(10,2)=90` and a cross-difference frequency is at most
`10*10=100`; both fit exactly in `uint8_t`. There are fewer than `8^20`
restricted-growth prefixes, so the `uint64_t` node counters also cannot
overflow.
Pruning when either exceeds its final bound (1) or `s*t-64` cannot remove a
universal completion. The class-size and remaining-position checks only remove
branches that cannot reach the requested final split; the remaining-multiplicity
checks only remove branches that cannot use every label a positive even number
of times. The final step is required to close and is not inserted as a new
prefix point.

At each completed leaf, the program recomputes all pairwise XORs directly from
the distinct prefix states and records a hit only if all 128 masks occur.
No floating-point arithmetic, randomized search, node cap or predecessor
census implementation is used in the five full runs. The cap control is a
separate negative control and is accepted only when it returns incomplete.

The small raw-word oracle in `verify.py` independently checks the `n=4,L=8`
regression without calling either census engine. The pinned predecessor is
loaded only to confirm that its `q & 1` grouping and fixed target-split budget
reject the named word; that old code is the audit subject, not part of the new
full n=7 replay.

## Consequence and limit

If all five `n=7,L=20` representative searches complete with zero universal
words, no shorter restored universal word exists: append copies of an already
used label in pairs until its length is 20. The old prefix set remains inside
the padded prefix set, so universality is preserved. The pinned length-24
reflected-Gray word is checked directly as an upper witness. Together these
finite facts leave `f(7)` in `{22,24}` **in this word model**. They do not decide
whether a length-22 word exists, nor imply any multiplier theorem or selected
supplier improvement.
