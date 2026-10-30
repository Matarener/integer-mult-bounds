# Exact projective-normal reuse

This contribution was produced by Nick Petalas. Apache-2.0.

The input is Jose Manuel / jmbarrancoml's unchanged H4 verifier from
[PR1867](https://github.com/CrocSwap/integer-mult-bounds/pull/1867).
Its mathematical results and complete check domain remain predecessor work.
The claim here is equivalence of one implementation change.

Write phi for a root of phi^2=phi+1. The field Q(phi) has conjugation
phi'=1-phi. A normal n has four entries a_i+b_i phi in Z[phi].
Let p=c+d phi be its first nonzero entry. Its field norm is

    D = p conjugate(p) = c^2+cd-d^2 != 0.

Multiplication of n by conjugate(p) gives the eight integer coefficients

    u_(2i)   = a_i(c+d)-b_i d,
    u_(2i+1) = b_i c-a_i d.

The first nonzero field entry of u is the integer D. Divide all eight
coefficients by their positive integer gcd, then negate them if D<0.
Call the resulting primitive integer tuple k(n).

## The key is exact

The tuple u/D is exactly the coefficient representation of n/p. Therefore
two normals are proportional over Q(phi) if and only if their tuples u are
proportional over Q. Primitive integer normalization with the same positive
pivot gives

    k(n)=k(m) if and only if Q(phi)n = Q(phi)m.

This covers arbitrary nonzero field scalars, including nonunits of Z[phi].
Normalization by the gcd of the original eight coefficients alone would
only remove rational scalars and would miss some reusable normals.

Nonzero proportional normals have the same annihilated roots. Thus every
cache hit replaces a repeated root scan by the already established fact
that the same projective normal defines the same flat. No approximate key,
modular comparison, hash collision assumption or rounded division is used.

## First occurrences and complete output

Both versions enumerate the same 34,220 root triples in the same order.
Both compute each cofactor normal, skip precisely the zero normals and
check cofactor annihilation against all three generating roots. On the
first occurrence of a projective class, the accelerator performs the same
sixty root products and inserts the same flat mask and original normal
with the same `setdefault` operation.

On later occurrences the original code computes that same flat and leaves
its first normal unchanged. The accelerator leaves it unchanged directly.
Induction over the triple order proves equality of the flat dictionaries,
their insertion order and the exact retained normal coefficients.

The complete remaining source `main` is unchanged. It receives the same
dictionary, so reflection orbits, chosen witnesses and their order,
support-receipt digest, budget predicates and all eight rejection controls
remain identical. No mathematical theorem is newly certified by the timing
comparison. The complete historical source runs in both conformance sides;
only its `hyperplanes` function is replaced on the accelerated side.

## Scope and bounds

The cache belongs to one `hyperplanes` invocation. It contains 1,320 keys
on this fixed sixty-line domain and holds no persisted result or source
state. The normal integer input contract is four pairs with absolute
coefficients at most 2^32. The key is mathematically valid beyond that
bound, but the implementation deliberately rejects larger inputs.

The universal equivalence argument is written mathematics. The finite
checks compare a separate rational-division key with the integer key,
exercise golden-field scalings, and compare complete flat dictionaries
under four root order/sign variants. Complete original and accelerated
stdout are compared byte for byte. Independent human and formal
proof-kernel review are unclaimed.
