# Determinant characters of a full matrix multiplication tensor

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Statement and action convention

Let K=F_q, n>=1, A=M_n(K), d=n^2, and let
mu in A* tensor A* tensor A be the tensor of matrix multiplication.
All three tensor factors have independent general-linear actions, with
no permutations of the factors and no semilinear field automorphisms.
Let Delta(mu) be the ordered determinant image of its stabilizer.
Write m=q-1, g=gcd(n,m), h=m/g, and H_n={a^n:a in K*}.

Then

```text
Delta(mu) = {(u,v,(uv)^-1): u,v in H_n}
          = {(u,v,w) in (K*)^3: u^h=v^h=1, uvw=1}.       (1)
```

Consequently the GL_d(K)^3 orbit of mu contains exactly

```text
(q-1) gcd(n,q-1)^2                                      (2)
```

orbits under SL_d(K)^3. A promised tensor in the GL orbit of mu has the
same determinant image, even when the three multiplication bases are not
given. Its dimensions and q give the three character equations in (1).
This is an extraction algorithm under an orbit promise, not recognition.

For a literal multiplication tensor, or one with a supplied multiplication
chart, an existing GL transporter with determinant triple (d1,d2,d3)
can be corrected to an SL transporter exactly when

```text
d1,d2 in H_n and d1 d2 d3=1.                            (3)
```

The proof below gives an attaining correction whenever (3) holds.

## Normalize every stabilizer

In chosen dual bases, a covariant triple (S,T,R) stabilizes mu exactly
when (F,G,H)=(S^-T,T^-T,R) satisfies

```text
F(x)G(y)=H(xy) for every x,y in A.                       (4)
```

Indeed covariant action gives R mu(S^T x,T^T y)=mu(x,y);
substitute x=F(a), y=G(b). This fixes the inverse-input convention.

Put a=F(1), b=G(1). Setting one input in (4) to 1 gives
H(x)=F(x)b=aG(x). Hence right multiplication by b and left
multiplication by a are bijective: for example R_b=H F^-1.
Surjectivity of R_b gives cb=1. Injectivity applied to
(bc-1)b=0 gives bc=1. Thus b is a unit, and the same argument
on the other side makes a a unit.

Define sigma(x)=a^-1 F(x)=a^-1 H(x)b^-1=G(x)b^-1.
It is an invertible K-linear unital map. Equation (4) gives

```text
sigma(x)sigma(y)
 = a^-1 F(x)G(y)b^-1
 = a^-1 H(xy)b^-1
 = sigma(xy).
```

Therefore sigma is an algebra automorphism, and every autotopism has
the form

```text
F=L_a sigma, G=R_b sigma, H=L_a R_b sigma, a,b in GL_n(K). (5)
```

Conversely (5) satisfies (4) for every such a,b and every algebra
automorphism sigma. This is the unital associative normalization of
David Ganz's atlas A019, written here in a two-sided form to preserve
the multiplication order. No commutativity is assumed.

## The automorphism contributes determinant one

Here is the classical matrix-unit proof, included to make the
noncommutative step self-contained. Put f_ij=sigma(E_ij).
These are matrix units, with f_ij f_kl=delta_jk f_il and sum f_ii=I.
The nonzero idempotent f_11 has a nonzero vector v in its image.
For 1<=i<=n put v_i=f_i1 v. Then f_1j v_i=delta_ji v.
Thus sum c_i v_i=0 implies every c_j=0. There are n independent
vectors v_i in K^n, so they form a basis. If P has these columns,
then f_ij v_k=delta_jk v_i proves f_ij=P E_ij P^-1.
By linearity sigma(x)=P x P^-1 for every x.

Left multiplication L_P acts independently on n columns, so its
determinant as a d-dimensional linear map is det(P)^n.
Right multiplication R_Q acts independently on n rows and has
determinant det(Q)^n. These statements are basis-independent.
Consequently

```text
det(sigma)=det(L_P)det(R_(P^-1))=1.                     (6)
```

For n=1 the same argument says sigma is the identity. For n>1,
transposition reverses the product and cannot replace sigma in (5)
with the two inputs in their fixed order. Factor permutations are
outside the action being considered.

## Image equality and the equation table

Let alpha=det(a), beta=det(b). Equations (5) and (6) give

```text
(det F,det G,det H)=(alpha^n,beta^n,(alpha beta)^n).
```

The covariant triple has determinants

```text
(alpha^-n,beta^-n,(alpha beta)^n).                       (7)
```

Every covariant stabilizer therefore lies in the right side of (1).
Conversely, for u,v in H_n choose alpha,beta with alpha^-n=u,
beta^-n=v. Take a=diag(alpha,1,...,1), b=diag(beta,1,...,1), and
sigma=identity in (5). This realizes (u,v,(uv)^-1), so no other
restriction is present.

The cyclic group K* of order m has nth-power subgroup of order h,
which is precisely the set of roots of X^h=1. This proves (1).
To put its three equations into atlas A029's bounded table, use rows

```text
(h mod m,0,0), (0,h mod m,0), (1 mod m,1 mod m,1 mod m).
```

For q=2 all entries are zero and the target determinant group is
trivial. For n=1 equation (1) gives the full product-one subgroup,
and (2) gives q-1, as it should for a nonzero scalar tensor.

If mu'=k mu for a triple of independent base changes, its stabilizer
is k Stab(mu) k^-1. Determinants are unchanged by conjugation in
each factor, so the same image holds in unknown independent bases.
Under that promise, finding n from the common dimension d=n^2,
computing gcd(n,q-1), and reducing three exponent rows extracts the
table without enumerating any automorphism group. These integer
operations take polynomial bit time in the dimensions and log q;
evaluating the resulting equations uses ordinary field powers.

## Special-linear orbits and a correction witness

Let G=GL_d(K)^3, N=SL_d(K)^3, and D=(K*)^3. The determinant
map G to D is surjective with kernel N. Since N is normal,
N-orbits in G/Stab(mu) are the cosets D/Delta(mu): two elements
of G give the same N-orbit exactly when their determinant triples
differ by an element of Delta(mu). Formula (1) gives
|Delta(mu)|=h^2. Hence their number is m^3/h^2=m g^2, proving (2).

Given g0 with g0 mu=t and determinant triple (d1,d2,d3), every
other transporter mu to t is g0 s with s in Stab(mu). Its factors
all have determinant one exactly when det(s)=(d1^-1,d2^-1,d3^-1).
Equation (1) makes this equivalent to (3).

For attainment choose alpha^n=d1 and beta^n=d2 and the diagonal
a,b above. The stabilizer

```text
s=(L_a^-T,R_b^-T,L_a R_b)
```

has determinant triple (d1^-1,d2^-1,d1 d2)=(d1^-1,d2^-1,d3^-1).
Thus g0 s is an SL transporter. If a source multiplication chart
k is supplied instead, use k s k^-1 in the source basis. Existence
of a GL transporter and any needed multiplication chart are explicit
inputs to this construction, not outputs of the extraction algorithm.

## What is new here and what remains open

This package adds the exact noncommutative full-matrix-algebra image,
its orbit count and constructive determinant correction to the
repository's promised-class extraction results. David Ganz's atlas
#2849 supplies A019's normalization and A029/A030's question and
framework. Nick Petalas's #5252 handles finite etale algebras; it
is a precedent, not a result reverified here. Innerness for full
matrix algebras and finite cyclic-group arithmetic are classical.
Global literature priority is unclaimed.

The all-field theorem is this written argument. Finite executable
checks corroborate it and do not constitute a proof-kernel derivation.
No raw-tensor recognition algorithm, general semisimple classification,
native program, supplier admission or integer multiplication saving
is established.
