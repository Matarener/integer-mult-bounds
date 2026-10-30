# Proof: shortest unsigned depth-three chain connector

## Setting

Let R be a nonzero unital ring of exact characteristic m >= 2. Registers
x = z_0 (immutable), z_1, z_2 and y = z_3 hold arbitrary initial (dirty)
values z_j^0 in R-modules M_0, ..., M_3. The R-linear maps B_l: M_{l-1} -> M_l
are arbitrary. The only operations are the complete calls

```text
l = 1, 2, 3:   z_l += B_l z_{l-1}
```

with no sign or inverse calls. A word w over {1, 2, 3} is *correct for c*
when, for every choice of modules, maps and dirty data, it ends with z_1, z_2
restored and y = y^0 + c B_3 B_2 B_1 x. For an interval 1 <= i <= j <= 3 let
N_w[i..j] be the number of increasing position tuples p_i < ... < p_j with
letter l at position p_l (scattered occurrences of the subword i(i+1)...j).

**Lemma 1 (action).** After w,
z_j = z_j^0 + sum_{i <= j} N_w[i..j] B_j ... B_i z_{i-1}^0.

*Proof.* Induction on appending letter l. Only z_l changes, by
B_l z_{l-1} = B_l z_{l-1}^0 + sum_{i < l} N[i..l-1] B_l ... B_i z_{i-1}^0.
That is N[l..l] += 1 and N[i..l] += N[i..l-1], the recurrence for subword
occurrences ending at the new letter. ∎

**Corollary.** w is correct for c iff N_w[i..j] ≡ 0 (mod m) for every
interval except N_w[1..3] ≡ c (mod m).

Sufficiency is Lemma 1. For necessity take M_l = R and every B_l = 1. Put
z_{i-1}^0 = 1 and every other initial value 0. Then z_j changes by N_w[i..j]·1,
which is zero iff m divides N_w[i..j], because the characteristic is m. The
same instance with x = 1 gives y - y^0 = N_w[1..3]·1 = c·1. ∎

Equivalently, the product of the elementary unipotents I + e_{l,l+1} in
UT_4(Z/m) must equal I + c e_{1,4}. This group form is also how the verifier
runs its exact search.

## Theorem

For every m >= 2 and c ≢ 0 (mod m), the shortest correct word has length 3m,
except (m, c) = (2, 1), (3, 2) and (4, 3), where it has length 4m. With no
finite characteristic no unsigned word is correct for any nonzero c.

**Lemma 2 (floor).** Each letter count n_l = N[l..l] is a positive multiple of
m. Hence every correct word has length a multiple of m and at least 3m.

*Proof.* n_l ≡ 0 by the Corollary. If some n_l = 0 then N[1..3] = 0 ≢ c. In
characteristic zero n_l = 0 is forced, which is the last claim. ∎

**Lemma 3 (construction).** Let m >= 5 with (m, c) ≠ (6, 5). Choose

- a = 1, t = c if 1 <= c <= m - 2;
- for c = m - 1, a unit a of Z/m in [2, floor(m/2)] and t = -a^{-1} mod m.

Such a exists: a = 2 for odd m >= 5; a = m/2 - 1 when 4 | m and m >= 8 (odd,
and gcd(a, m) divides m - 2a = 2); a = m/2 - 2 when m ≡ 2 (mod 4) and m >= 10
(odd, and gcd(a, m) divides m - 2a = 4). Then t ≠ 0, and t ≠ m - 1 because
a ≢ 1. So 1 <= t <= m - 2 and 1 <= a <= m/2 in both cases. The word

```text
W = 1^a 2 3^t 1^(m-2a) 2 1^a 2^(m-t-2) 3 2^t 3^(m-t-1)
```

has m copies of each letter and is correct for c ≡ ta.

*Proof.* Track (N[1..2], N[2..3], N[1..3]) through the blocks. The first 2
sees a ones: N12 = a. The block 3^t sees one 2 and N12 = a, adding t to N23 and
ta to N123. The second 2 sees m - a ones: N12 = m. The block 2^(m-t-2) sees m
ones: N12 = m(m - t - 1). The lone 3 sees m - t twos, so N23 = m, and adds
N12, which is ≡ 0. The block 2^t adds mt, so N12 = m(m - 1). The final
3^(m-t-1) sees m twos and N12 ≡ 0. The totals are N12 = m(m - 1) ≡ 0,
N23 = m(m - t) ≡ 0 and N123 ≡ ta ≡ c. The letter counts are
a + (m - 2a) + a, 1 + 1 + (m - t - 2) + t and t + 1 + (m - t - 1). ∎

The remaining case (m, c) = (6, 5) uses the explicit 18-call word
`111122133232123233`, checked by the verifier.

**Lemma 4 (small characteristic).** For m in {2, 3, 4}, a 3m-letter correct
word has n_1 = n_2 = n_3 = m by Lemma 2. The verifier enumerates all
90, 1,680 and 34,650 such words. The attained N[1..3] residues among words
whose other intervals vanish are {0}, {0, 1} and {0, 1, 2}. So 3m is attained
for every c except c ≡ -1, and the next admissible length is 4m by Lemma 2.
These explicit words attain it:

```text
m = 2, c = 1:  12321232
m = 3, c = 2:  112113211323
m = 4, c = 3:  1112111321213233
```

Lemmas 2 to 4 prove the Theorem. An exact breadth-first search over the
whole of UT_4(Z/m), m = 2, ..., 8, confirms every minimum independently. ∎

## Depth four (finite certificate only)

The same Corollary holds for any chain depth k. Lemma 2 gives the floor km and
lengths that are multiples of m. Exact breadth-first search over UT_5(Z/m)
gives these minima, equal for every nonzero c:

| m | 2 | 3 | 4 | 5 (opt-in run) |
|---|---|---|---|---|
| minimum | 12 = 6m | 18 = 6m | 20 = 5m | 25 = 5m |

So the per-letter floor 4m fails at depth four for m <= 5. No all-m depth-four
statement is claimed.
