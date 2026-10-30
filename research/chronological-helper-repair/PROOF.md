# Chronological helper spill and sharp boundary repair

This is a scoped all-field linear-algebra proof. It gives no native price,
physical supplier or multiplication exponent. The contribution was produced
by Nick Petalas. Apache-2.0.

## The fixed replacement model

Let F be any field and let h in F^k be k arbitrary initial helper values.
An invertible scalar word returns h unchanged. It can have any number of
invertible events. Fix k ordered cuts. At cut i the original prefix is P_i.
Choose a cut row a_i and column b_i such that a_i b_i=1. Define

```text
c_i = a_i P_i,       d_i = P_i^-1 b_i,
C   = matrix with rows c_i,
D   = matrix with columns d_i.
```

Assume C is invertible. No invertibility assumption is made on D or CD.
The choice of cuts, rows and columns is fixed before seeing any data.
There are k further arbitrary independent inputs z_1,...,z_k, all public
from the start. At cut i return t_i=a_i x, retain that output, and replace
the live state by

```text
x <- x + b_i (z_i - t_i).
```

This is an invertible replacement, not an erasure. Since a_i b_i=1,
decompose x=b_i(a_i x)+(x-b_i a_i x). The event swaps the first coordinate
with z_i and preserves the second. The old coordinate t_i remains an
output. Any realization by local bases still has to pay for those bases.

This is the independent-input replacement semantics of Ali Romman's
[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599),
applied to several fixed cuts of one identity helper word. Its physical
common-chart hypotheses are additional requirements, not consequences
of the scalar model here. Main fields, owned lifetimes and nonidentity
helper endpoints are outside this theorem unless a separate reduction
to this identity block is supplied.

Write the pairing matrix as

```text
K = CD = I + L + U,
```

where L is strictly lower triangular and U is strictly upper triangular.
The diagonal is one because c_i d_i=a_i b_i=1. Let f denote the final live
helper vector, after the original word's terminal identity has completed.

## The complete causal map

The following identities hold for every h,z over every field:

```text
(I+L)t = Ch + Lz,
Cf     = (I+U)z - Ut.                         (1)
```

To prove them, pull the current live state back through the original prefix.
If u is this boundary-coordinate state, replacement i changes it by
d_i(z_i-t_i). The original scalar events between cuts do not change u.
Consequently,

```text
t_i = c_i h + sum_(j<i) K_ij (z_j-t_j),
f   = h + D(z-t).
```

The first equation gives the first line of (1). Multiplying the second by
C and substituting Ch=(I+L)t-Lz gives the second line. No simultaneous-cut
commutation, joint basis or pairwise-independence premise was used.

Let A=(I+L)^-1, which exists because L is nilpotent. The two cross-input
coefficient maps have exact ranks

```text
rank(z -> t, holding h fixed) = rank(AL) = rank(L),
rank(h -> f, holding z fixed) = rank(-C^-1 UAC) = rank(U).       (2)
```

Both statements are invariant under separate invertible changes of basis
within the early-output bank and within the final-helper bank.

Thus individual equations c_i d_i=1 do not certify independent splits.
The early outputs depend only on old inputs exactly when L=0. The final
helpers depend only on new inputs exactly when U=0. Both requirements hold
without communication between the two output banks exactly when CD=I.
Here independence means the prescribed old/new input partition; allowing
a new input basis that mixes h and z changes the contract.

## Exact repair tariff when the early targets are already valid

Suppose L=0. The early bank is then t=Ch and can remain untouched. Define
r=rank(U). Grant free invertible linear operations confined to either bank.
A cross-bank update adds B times one bank to the other and costs rank(B).
Rank-one updates therefore cost one unit. Coefficients and local basis
operations are unrestricted over F. This is a relaxation of physical
delivery, not a native rank tariff.

The least total cross-bank cost that makes all final helpers independent
of h, preserves the early outputs, and restores every auxiliary field is
exactly r. Any finite clean or dirty workspace is permitted on either side
of a fixed bank partition. Auxiliary fields must return to their original
values. Cross-bank updates in either direction are allowed.

For the lower bound, fix z and every auxiliary input, and vary h. The
coefficient of h in all live-side fields initially has rank r by (2).
Adjoining fixed clean or dirty workspace only appends zero rows. An
invertible operation confined to the live side preserves this rank.
An operation confined to the early side leaves it unchanged. A cross-bank
update into the live side with matrix B changes the coefficient matrix
by rank at most rank(B). The inequality

```text
|rank(M+E)-rank(M)| <= rank(E)
```

therefore forces total charge at least r before that coefficient can be
zero. At the desired endpoint every final helper and every restored
live-side auxiliary is independent of h. Updates into the early side
cannot reduce this lower bound. The proof uses neither a workspace limit
nor a sign, characteristic or nonzero-state assumption.

For attainment, take any rank factorization
U=sum_(s=1)^r v_s w_s^T. Execute

```text
f <- f + (C^-1 v_s)(w_s^T t),       s=1,...,r.
```

These are r rank-one updates from the retained early bank. Equation (1)
then gives Cf=(I+U)z. The live-side normalizer (I+U)^-1 C returns f=z.
The early bank remains t=Ch; no workspace is needed. This proves both
the exact cross-bank charge and a constructive endpoint decoder.

If the early outputs are physically unavailable for later reading, this
attainment is unavailable. The rank lower bound still applies to any
implementation in the stated larger relaxation. Similarly, free local
bases in this tariff must receive their actual scalar, native, routing,
precision and storage charges before use in a supplier invoice.

## A sharp obstruction of arbitrary size

For every k>=2 choose C=I and D=I+N, where N has ones on the first
superdiagonal and zeros elsewhere. Then L=0 and U=N has rank k-1.
Every individual replacement is normalized, and every early output is
exactly t_i=h_i. Nevertheless,

```text
f_i = z_i + z_(i+1) - h_(i+1)       for 1<=i<k,
f_k = z_k.
```

The final helpers retain k-1 independent old-input directions. They need
exactly k-1 cross-bank rank units to repair. In particular, counting k
individually valid cuts as k independent target splits misses a deficit
of arbitrary size in this fixed-direction model.

An explicit scalar repair adds t_(i+1) to f_i for all i<k. Processing
i=k-1,...,1, subtract the already normalized f_(i+1) from f_i. This word
uses k-1 cross-bank additions and k-1 within-bank additions, returns
f=z, and preserves every early output. Optimality is claimed for the
cross-bank rank charge only, not the total scalar addition count.

## Evidence and scope

`verify.py` builds an explicit identity source word with changing invertible
prefixes, performs the literal cut replacements on all input coefficients,
and compares its endpoint with (1). It checks (2), the full reversible
endpoint and the attaining rank-factor repair. Finite-field and rational
domains are bounded and enumerated in its output. A separate binary
outer-product enumeration rejects every one-unit repair of a rank-two
sharp-family defect. Incorrect diagonal, basis and field fixtures fail.

The universal result rests on this written proof. The finite replay is
corroboration, not proof-kernel or independent human acceptance. Causal
elimination, nilpotent triangular inverses, rank factorization and rank-cut
lower bounds are classical. The proposed new contribution is their exact
chronological helper-replacement application, with both leakage ranks,
the sharp repair tariff and the explicit family. No general literature
priority is claimed.

Ali Romman's #5599 supplies the single-cut replacement contract and its
retained P104 lineage. His [#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the dyadic single-cut pairing context. This theorem does not
compute a dyadic module capacity or recheck either predecessor.

No actual P104 cut is constructed here. Distinct output charts, physical
availability of retained early outputs, restricted coefficient alphabets,
native operators, dirty-state physical restoration, the complete signed
moment, compiler and outer transfer remain separate obligations. The
selected frontier and all five selected framework assumptions are unchanged.
