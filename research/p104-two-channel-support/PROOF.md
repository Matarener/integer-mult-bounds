# Exact second support weight of the P104 root code

This contribution was produced by Nick Petalas. New material is Apache-2.0.

## 1. Object and inherited input

Use the ordered 104 odd-weight binary ports in `PORTS.json`, copied byte for
byte from Matarener's [PR6166 coordinate fixture](https://github.com/CrocSwap/integer-mult-bounds/blob/096938513138868f0ed27639061f1a5054900f96/research/p104-carrier-code-uniqueness/e8/ports.json).
Coordinates of a binary port are indexed 0 through 8. Its rational root is

- `r(q) = e_i - e_j` for a weight-seven port with zeros `i < j`;
- `r(q) = sum_{i in supp(q)} e_i - (1/3) sum_{i=0}^8 e_i` for a weight-three port.

Let `M[a,b] = r(q_a) . r(q_b) / 2`. Although the roots use thirds, every
entry of M is an integer or a half-integer. Reduce these entries modulo 3,
using `1/2 = 2`. The clique indices

```text
T = (1, 5, 18, 20, 80, 85, 100, 103)
```

give `M[T,T] = I_8`, over both Q and F3. Write `G = M[T,:]` and let `C_Q`
and `C_3` be its row spaces over Q and F3 respectively. These definitions
specify the two codes independently of any word replay.

The identification of `C_3`, up to coordinate signs, with every
8-dimensional ternary P104 decoding code is Matarener's PR6166 theorem.
Its code uniqueness, single-channel weight 49, and binary hyperplane port
capacity 60 are cited dependencies, not newly checked results here. The
predecessor's local-word lineage is Ali Romman PR5827 and DreamingOfClouds
PR5907/6030, with their retained E8/native/controller contributors.

## 2. Statement

For a linear code C define its second generalized support weight by

```text
d_2(C) = min |supp(u) union supp(v)|,
         over linearly independent u,v in C.
```

The finite certificate proves

```text
d_2(C_3) = d_2(C_Q) = 72.
```

There are exactly 704 minimizing two-dimensional subcodes of `C_3`.
This count is a finite enumeration, not a classification up to symmetry.
The value 72 and these minimizers are the new result. The mathematical
notion of a generalized Hamming weight is standard.

## 3. Exhaustive lower bound over F3

Since G restricts to the identity on T, the map `c -> cG` is injective on
`F3^8`. Every projective coefficient line has exactly one representative
whose first nonzero entry is 1. Enumerating the eight trits gives

```text
(3^8 - 1)/2 = 3280 representatives.
```

Two distinct representatives are linearly independent. Every independent
pair of codewords has the same support union as one of the unordered
pairs of representatives. Thus all cases are covered by

```text
binomial(3280,2) = 5377560 pairs.
```

`verify.py` evaluates each representative at all 104 coordinates and stores
its exact support as an integer bitset. For each distinct pair it computes
`(support_a | support_b).bit_count()`. The complete histogram, recomputed
on every replay and compared to `RESULT.json`, has minimum 72.

An F3 plane has four projective lines and six unordered pairs. Every pair
in that plane spans it and has the same support union. The replay forms
the four canonical representatives of every minimizing plane as
`a, b, a+b, a+2b`, then groups their sorted tuples. It obtains 4224 pairs
in 704 groups and checks that every group occurs exactly six times.
The total number of planes covered by the pair census is 5377560/6 = 896260.
No support test is sampled or inferred from the minimum-weight distribution.

The 832 Gram entries used to construct G are checked by two expressions:
the intersection-size formula and explicit nine-coordinate rational roots.
This is a construction check for this certificate, not a replay of the
predecessor's uniqueness proof or its word counts.

## 4. Rational lower bound and sharp witness

Suppose a two-dimensional subspace of `C_Q` is supported on a set S of
fewer than 72 coordinates. Its coefficient plane is in the kernel of
`G[:, outside(S)]^T`, so that rational matrix has rank at most six.
All its denominators are powers of two. Reduction modulo 3 cannot raise
its rank, since a nonzero reduced minor has a nonzero rational determinant.
Its F3 kernel therefore has dimension at least two. Injectivity of the
ternary coefficient map gives a two-dimensional subcode of `C_3` supported
inside S, contradicting section 3. Hence `d_2(C_Q) >= 72`.

In the ordered eight-row basis G, take

```text
a = (0,0,0,1,0,0,0,0)
b = (0,0,0,0,1,1,1,0).
```

Their coefficient minor on positions 3 and 4 is the identity. Their rational
codewords have individual weights 49 and 71, and their union has weight 72.
Over F3 their individual weights are 49 and 69 and their union is the same
72-coordinate set. The checker calculates every rational and ternary entry;
`RESULT.json` records the union as binary port values. This proves sharpness
in both fields. The rational assertion follows from exact arithmetic and
the rank argument, rather than identifying rational zeros with modular zeros.

A useful transfer also applies to a 3-integral systematic generator H of an
8-dimensional rational code, if its reduction is coordinate-sign-equivalent
to `C_3`. The same minor argument proves `d_2(row_Q H) >= 72`. This is a
conditional implication; it does not classify rational decoding codes.

## 5. Scoped common-frame consequence

Assume a rational code has the reduction specified in the preceding
paragraph. If two independent channel rows in that code are both acquired
from ports in one binary frame F, then F contains their support union.
It therefore contains at least 72 ports. The cited PR6166 hyperplane
capacity is 60. Every proper subspace of `F2^9` is contained in a hyperplane,
so `F = F2^9`.

Dually, suppose two independent receiver-coefficient columns are in a code
with the same support bound. If every receiver of either column must accept
its delivery in one common landing frame B, and partner l's legal frame is
inside `q_l^perp`, then

```text
B subset intersection_{l in union of receiver supports} q_l^perp = {0}.
```

The equality holds because those at least 72 binary ports span `F2^9` by
the same capacity bound. Thus a common landing frame must be ZERO.

This is a conditional obstruction to common-frame synchronization. It does
not say that two independently scheduled channels each require FULL-to-ZERO
descent. With distinct acquisition or delivery cuts, a nine-dimensional
partner code, extra canceling carrier directions, or public relays, the
common-frame hypotheses can fail. No additional paid cost is inferred
without an actual trajectory and complete invoice.

## 6. Verification boundary

The exhaustive claim is about the specified 104-coordinate codes. No
selected word, native operator, compiler, outer supplier, rounded multiplier,
or predecessor uniqueness certificate is replayed. The common-frame
consequence uses the named predecessor capacity and the stated code/support
hypotheses. Human and formal proof-kernel review are unclaimed.
