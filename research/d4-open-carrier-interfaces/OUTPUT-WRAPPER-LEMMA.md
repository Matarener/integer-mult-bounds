# The inverse output wrapper is automatically monomial

This exact all-dimension lemma supplements the four explicit normalizer
witnesses. It explains a feature of the historical finite search without
using that search as a proof. It does not make the inverse input wrapper
automatic or admit a global caller.

Let `C_v=((1+i)I+(1-i)X_v)/2` on n binary address axes, and let
`F=X_b ∏_(j=1)^n C_ej` for any translation gauge b. Set

```
η = e_1 + ... + e_n,
T = F C_p^-1 C_q^-1,
J = F X_p,
K = T^-1 J P,
```

where P and `F P F^-1` are monomial. A monomial here is an actual invertible
address permutation with a pointwise Gaussian unit, including its global
phase. The operators act on arbitrary Gaussian dyadic arrays.

Define the two inverse-orientation corrections by their exact operator
products:

```
AB = T K^-1 T^-1 K^-1,
BB = T AB^-1 T^-1.
```

Then BB is monomial for every such P.

To prove this, all translations commute, as do all C_v. The native
identities retain their actual phases:

```
C_v²=X_v,       F²=X_η,       T²=X_(η+p+q),       F X_p F^-1=X_p.
```

Inverting AB in the displayed order gives

```
BB = T K T K T^-2 = (T K)² T^-2 = (F X_p P)² T^-2.
```

Put `M=X_p P`. Both M and `F M F^-1=X_p(F P F^-1)` are monomial. Therefore

```
BB = (F M F^-1) F² M T^-2
```

is a product of four monomials. This is an exact equality, not just a
symplectic or projective one.

For the actual h7 D4 chart, `η=127`, so the two Pauli factors are
`F²=X_127` and `T^-2=X_(127 xor p xor q)`. The four frozen witnesses still
check the full exact phase and literal lowering of BB. Their additional
substantive inverse-input property is that AB also has rank zero; the
present lemma does not establish that property for arbitrary P.

BB remains an executed, paid monomial correction. Its native rank zero
does not permit omitting it or its address/phase work. The literal
monomial implementation and restoration/caller limitations in
`PROOF-NORMALIZATION.md` continue to apply. The same proof holds in every
dimension under the displayed native contract, and tensor products
preserve all its identities for every positive chunk parameter.
