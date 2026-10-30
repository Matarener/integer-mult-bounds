# Independent rational moment enclosure

For an integer rank r >= 1, choose e=floor(log2 r), u=2^e and z=(r-u)/(r+u), so 0 <= z < 1/3. Then

```
log r = e log 2 + 2 sum_{j>=0} z^(2j+1)/(2j+1),
log 2 = 2 sum_{j>=0} (1/3)^(2j+1)/(2j+1).
```

After N=50 terms, the positive omitted tail is at most

```
2 z^(2N+1) / ((2N+1) (1-z^2)).
```

The checker evaluates each finite sum and tail exactly with rational arithmetic. It rounds the lower sum down and the sum-plus-tail up on the binary grid 2^-128. Combining these intervals gives rigorous log(r) bounds. This proof does not assume binary floating-point log, exp or fractional power accuracy.

For each tested saving k, x=k log r lies in [0,1), checked explicitly. The alternating series for exp(-x) has decreasing term magnitudes. Its degree-15 truncation is a lower bound and its degree-14 truncation an upper bound. Since exp(-x) is decreasing, evaluating the lower polynomial at the upper x endpoint and the upper polynomial at the lower x endpoint encloses exp(-x). Multiplying by r encloses r^(1-k).

Weighted addition gives target and paid moment intervals. Subtracting the upper paid bound from the lower target bound proves each positive margin; the opposite subtraction proves the negative raw-upper margin. All computations use fractions of integers, without floating point. The sign crossing enclosure is not asserted to be the only root.

The two complete invoice reconstructions are (1) literal LOCAL/QUERY_SHEAR/IDLE events plus the actual diagonal target exponents, and (2) eighteen local profiles, fifteen rank-1 query batches and the length-seven/eight path formulas. They agree with every rank of the public target/paid histograms. The exact separately audited local helper and paid profiles provide the input binding.
