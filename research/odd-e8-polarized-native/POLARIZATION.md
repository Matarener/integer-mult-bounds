# Polarization of the literal cross-cube block

Use the literal tetrads `a=(0,1,2,3)` and `b=(0,1,4,5)` in the pinned
normalizers, with the two other factors fixed to cube a. Write `C_ab` for
the root Gram cross block divided by four, and `K=I-B` on a fixed cube.
The #5439 polynomial gives exactly

```
H_ab = -C_ab tensor P,       P=(I-K tensor K)/2.
```

The two tetrads share coordinates u=0 and v=1. For a root row m put
`w_+=(m_u+m_v)/2` and `w_-=(m_u-m_v)/2`. Each w has four nonzero entries
within either eight-root cube. The standard rank-two polarization is

```
C_ab = (w_+,a w_+,b^t + w_-,a w_-,b^t)/2.
```

For the 64 two-factor selector pairs put `T=K tensor K`. Choose J to be
the 32 selectors whose first selector has even relative-sign parity, and set

```
U_j=e_j-T e_j,       V_j=(e_j^t-e_j^t T)/2,       j in J.
```

`T^2=I`. It reverses that first parity, so the two diagonal half blocks of
T vanish. Multiplication in these two halves gives `UV=(I-T)/2=P`.
Therefore the 64 literal dyadic factors are

```
H_ab = -sum_(sign,j) (w_sign,a tensor U_j)
                         (w_sign,b^t tensor V_j)/2.
```

Each factor has 68 nonzero source ports and 68 nonzero reader ports. The
finite checker regenerates every coefficient, compares all 512-by-512
entries against the original F3 polynomial, and checks every supported
binary cross-pairing. Each source and reader span has dimension eight,
each self-pairing rank is two, and the two spans are perpendicular. They
share a six-dimensional radical and have joint span ten of pairing rank four.

The literal 64 pairs deduplicate into four pairs of spaces, with 16 factors
per pair. Their source sets partition the 512 source fields; their reader
sets partition the 512 reader fields. `module.py` independently regenerates
this deduplication from actual binary bases before emitting any ADD.
These are exact claims for the specified literal block, not a finite check
standing in for every cube pair or the whole odd-E8 side map.

The previous unpolarized factorization used the two coordinate features
separately, with span nine and cross-pairing rank two. The new factorization
exposes truly orthogonal eight-space rectangles. Zero cross-pairing is an
orthogonality statement. The physical ground-to-S8 path still costs H8,
as explicitly charged by the native module.
