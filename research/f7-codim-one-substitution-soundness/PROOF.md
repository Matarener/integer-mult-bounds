# Codimension-one soundness of the fixed `L/2` substitution

The model is the PR943 singleton prefix walk, as corrected by #2973 and
classified on small domains by #3699. For a word `w` of length `L` over
`[0, n)`,

```
q_0 = 0,    q_{i+1} = q_i XOR e_{w_i}.
```

The prefix set `S` is `{q_0, ..., q_{L-1}}`. The word is **simple** when these
`L` states are distinct, **restored** when every label occurs a positive even
number of times, and **universal** when `S + S = F_2^n`. A nonzero linear
functional `f` has kernel `K` of size `Q = 2^{n-1}`. Write `E = S ∩ K`,
`O = S \ E`, `s = |E|`, `t = |O|`, and

```
a = C(s, 2) - |{x + y : x ≠ y in E}|,
b = C(t, 2) - |{x + y : x ≠ y in O}|.
```

Pair sums of either class land in `K`. Universality forces `a + b ≤ base + d²`,
where `d = (s - t) / 2` and

```
base(n, L) = 2 C(L/2, 2) - (Q - 1).
```

The fixed substitution uses budget `base`. It **falsely prunes** a universal
word when `base < a + b ≤ base + d²`.

#3699 measured that, on its firing domains, no functional of Hamming weight at
least `n - 1` falsely prunes, and said that regularity was not a theorem.
#3733 then showed the regularity is not a weight law: at `(4, 12)` three
weight-3 masks do fire. This note proves the measured statement in the one
range where every label occurs twice.

## 1. Two preserving steps

**Lemma.** Let `L` be even and let exactly two steps of the walk preserve a
linear functional `f` with `f(q_0) = 0`. Among `q_0, ..., q_{L-1}`, the two
level sets of `f` differ in size by at most 2.

*Proof.* A preserving step is a stay and every other step flips `f`. Let the
stays be at indices `i < j`. Then `f(q_k)` equals `k mod 2` for `k ≤ i` and for
`k > j`, and equals `(k - 1) mod 2` for `i < k ≤ j`. The comparison pattern
`k mod 2` has exactly `L/2` zeros. The two patterns differ exactly on the
integer interval `(i, j]`. On any integer interval the numbers of even and odd
points differ by at most 1, so replacing one count by the other changes the
zero count by at most 1. Therefore `|s - L/2| ≤ 1` and `|s - t| ≤ 2`.

The hypothesis is sharp: four stays can produce a difference of 4. The
verifier checks every stay pair for `L ∈ {6, 8, 10, 12, 14}` against this
interval formula, and checks one four-stay pattern that leaves the bound.

## 2. Pair sums in small spaces

**Lemma.** Any three distinct vectors have three distinct pairwise sums, none
of them zero.

*Proof.* If `a + b = a + c` then `b = c`. The other two identifications are the
same argument.

**Lemma.** Every 5-subset `E` of `F_2^3` has `{x + y : x ≠ y in E}` equal to
all seven nonzero vectors.

*Proof.* A nonzero `v` that is missed meets `E` in at most one point of each
coset of `{0, v}`. There are four such cosets, so `|E| ≤ 4`. The verifier
enumerates all `C(8, 5) = 56` subsets and one 4-subset that misses a direction.

An affine coset `v + K` has the same pair-sum set as its translate inside `K`,
because `(v + a) + (v + b) = a + b`.

## 3. Double transversals, `n ≤ 4`

**Theorem.** Let `n ∈ {3, 4}` and `L = 2n`. On every simple restored universal
word, every functional of weight at least `n - 1` is sound for the substituted
budget: it does not falsely prune.

*Proof.* Length `2n` and positive even label counts force every label to occur
exactly twice.

The all-ones functional has weight `n`. Every step flips it, so its level sets
are the two time-parity classes and `s = t = n`. Then `d = 0`, the correct
budget equals `base`, and `a + b ≤ base`. The substitution does not reject a
word the correct budget admits.

A weight-`(n - 1)` functional misses exactly one label. That label occurs
twice, so exactly two steps preserve the functional. The first lemma gives
`|s - t| ≤ 2`. If `s = t`, then again `d = 0` and there is no false prune.
If `|s - t| = 2`, the class sizes are `n + 1` and `n - 1`.

For `n = 4` those sizes are 5 and 3, and the kernel is a 3-dimensional space.
The size-5 class lies in one coset of the kernel. By the five-point lemma its
pair sums are all seven nonzero kernel vectors. The size-3 class contributes
three further pair sums. Pair slots number `C(5, 2) + C(3, 2) = 13`, so

```
a + b = 13 - (7 + 3) = 3.
```

Here `base(4, 8) = 5`, and `3 ≤ 5`, so the strict false-prune inequality fails.

For `n = 3` the sizes are 4 and 2, and the kernel is `F_2^2`. The size-4 class
is a whole coset, whose pair sums are all three nonzero kernel vectors. The
size-2 class contributes one pair sum. Pair slots number `C(4, 2) + C(2, 2) = 7`,
so `a + b = 7 - 4 = 3`. Here `base(3, 6) = 3`. Equality does not satisfy
`base < a + b`, so the word is not falsely pruned.

The verifier recomputes every restricted-growth simple universal word in both
domains (4 words at `(3, 6)`, 22 at `(4, 8)`) and checks the size and excess
claims for every mask of weight at least `n - 1`. Restricted growth is a
label-introduction normal form: it does not drop a geometric word, and the
masks are the functionals in that normal form. The predicate is not vacuous.
The word `01021323` is universal and the coordinate-bit-0 functional falsely
prunes it, with split `(6, 2)` and excess 8 against base 5.

## 4. The weight pattern is not a law

At `(4, 12)` the positive even compositions of 12 into four parts are
`4, 4, 2, 2` and `6, 2, 2, 2`. A weight-3 functional that omits a label of
count 4 or 6 therefore preserves four or six steps, and the two-stay lemma
no longer caps `d`. An independent enumeration of the 314 restricted-growth
simple universal words finds:

| mask | omitted label | false prunes |
|---:|---:|---:|
| `0111` | 3 | 0 |
| `1011` | 2 | 4 |
| `1101` | 1 | 4 |
| `1110` | 0 | 4 |

Weight at least `n - 1` is not a soundness law once a label may occur four
times. #3733 measured this domain first, including the further fact that only
`0111` and `1111` stay sound among the high-weight masks. The count above is
recomputed here and is not imported from that package. The four firing words
for each of the three masks are the explicit reason not to generalise the
`(4, 8)` and `(5, 12)` tables.

## 5. The two weight-`(n - 2)` exceptions are finite

#3699's other open description is that mask `1010` does not fire at `(4, 8)`
and mask `11010` does not fire at `(5, 12)`, although every other mask of the
same weight does. Both masks have weight `n - 2`, so Section 3 does not apply.

On all 22 universal words at `(4, 8)`, mask `1010` has excess at most 3, and
`3 ≤ base = 5`. On all 828 universal words at `(5, 12)`, mask `11010` has
excess at most 14, and `14 ≤ base = 15`. Both statements are enumerations.
The second is tight by one unit. Neither enumeration is a structural proof,
and neither is the `(7, 18)` census.

## 6. What is not claimed

This does not run `survey(7, 18)` or `survey(7, 20)`, does not decide `f(7)`,
and does not repair a retained engine. Rows with no universal word support no
prune conclusion. Nothing here changes a supplier, a tariff, or the selected
conditional `κ`.
