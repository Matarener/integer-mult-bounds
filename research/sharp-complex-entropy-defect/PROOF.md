# A sharp complex entropy defect and a stronger sparse-feedback bound

This scoped proof was produced by Nick Petalas. Apache-2.0.

## The new scalar lemma

Use base-two logarithms in `h(z)=-z log_2|z|`, with `h(0)=0`.
For every pair of complex numbers,

```text
|h(p)+h(q)-h(p+q)| <= |p|+|q|.                         (1)
```

The constant one is sharp. For a nonzero pair, equality holds exactly when
`p=q != 0`. The zero pair also gives equality. In particular, this is a
modulus bound on the full complex defect, rather than just its real part.

Here is a self-contained proof. Work first with natural logarithms and put
`D=-p ln|p|-q ln|q|+(p+q)ln|p+q|`, using continuous zero conventions.
The terms containing `ln|gamma|` cancel, so
`D(gamma p,gamma q)=gamma D(p,q)` for every complex gamma. If either input
is zero, the defect is zero. Otherwise divide by `|p|+|q|` and exchange
the inputs if necessary. Write

```text
a=|p| >= b=|q| > 0,    a+b=1,    s=p+q,    r=|s| <= 1.
```

If `r=0`, then `q=-p`, `a=b`, and the defect is zero. For `r>0`,

```text
D = s ln(r/a) + q ln(a/b).                            (2)
```

For `r>=a`, both logarithms in (2) are nonnegative. The function
`u ln(u/a)` is increasing for `u>=a`, so the triangle inequality gives

```text
|D| <= r ln(r/a)+b ln(a/b)
     <= ln(1/a)+b ln(a/b)
      = -a ln a-b ln b <= ln 2.                       (3)
```

The last inequality is the binary entropy maximum, obtained by differentiating
in `a`. Equality requires `r=1` and `a=b=1/2`. Equality in the ordinary triangle
inequality `|p+q|<=|p|+|q|` then makes the inputs parallel with the same phase,
so `p=q`. Conversely, equal nonzero inputs give `D=2p ln 2`.

For `0<r<=a`, the first logarithm in (2) is nonpositive. The standard
calculus inequality `u ln(1/u)<=1/e` for `u>0` gives

```text
r ln(a/r) <= a/e.
```

Apply the same inequality to `u=2b/a` to obtain

```text
b ln(a/b) = b ln 2 + (a/2)*(2b/a)*ln(a/(2b))
          <= b ln 2 + a/(2e).
```

Consequently

```text
|D| <= 3a/(2e)+b ln 2 < (a+b)ln 2 = ln 2.            (4)
```

For an exact coarse justification of strictness, `e>8/3` follows from its
positive power series. Cauchy-Schwarz on the integral of `1/u` over `[1,2]`
gives `ln 2>2/3`, whereas `3/(2e)<9/16<2/3`.
Equations (3) and (4), homogeneity, and division by `ln 2` prove (1) and its
equality classification. No matrix premise is needed for this lemma.

## Application to the cited sparse-feedback contract

Chris R / Clear1nsight's [PR #4036](https://github.com/CrocSwap/integer-mult-bounds/pull/4036),
at the source bytes pinned in SOURCES.json, supplies the following premises.
They are cited results here, not new verification claims:

- The fixed machine prefix is an invertible complex matrix `M`.
  With its fixed analytical preconditioner `J`, `||J||_2=1`, put
  `N=M^{-*}J`, `p_ij=M_ij conjugate(N_ij)` and `Phi(M)=sum_ij h(p_ij)`.
- The legal coupled endpoint has `Re Phi = lambda f V`; the initial value
  is zero. This includes the source's restored dirty auxiliaries and its
  returned-clean auxiliary reduction. Its boundary is
  `F=[[C,lambda B],[0,I]]`, `C=BA`, with unitary `A,B`, and each `B` row
  has `2^f` equal-magnitude nonzero entries.
- The actual sole native call has jump `Delta_Q`. Invertible monomial steps
  preserve Phi. Under the source's child-first, payload-preserving monomial
  premise, the native jump is zero. General interleaving retains the jump.

Replace only the local scalar estimate in that argument. An arithmetic update
`G=I+c e_t e_s^T` changes row `t` of `M` and row `s` of `N`, since
`N'=G^{-*}N`. For each column `j`, its two affected products obey

```text
p'_tj+p'_sj = p_tj+p_sj.
```

Subtract the common `h(p_tj+p_sj)` from the old and new pair sums.
Applying (1) to each pair yields

```text
|Delta Phi| <= sum_j (|p_tj|+|p_sj|+|p'_tj|+|p'_sj|).
```

For any row at a prefix, Cauchy-Schwarz gives the already cited row estimate

```text
sum_j |p_ij| <= ||row_i M||_2 ||row_i N||_2
             <= ||M||_2 ||M^{-1}||_2 ||J||_2 = cond_2(M).
```

Writing `kappa^-` and `kappa^+` for the conditions before and after the update,
we have the stronger local estimate

```text
|Delta Phi| <= 2*(kappa^-+kappa^+) <= 4 K_t,             (5)
```

where `K_t=max(kappa^-,kappa^+)`. Telescope exactly as in the source. The new
necessary conditions are

```text
4 sum_t K_t + Re(Delta_Q) >= lambda f V,
4 K S       + Re(Delta_Q) >= lambda f V.                (6)
```

Here `S` counts every updated scalar coordinate and `K` bounds every full
formal machine prefix, including the internal cuts of masked operations.
At `lambda=1/2`, the source's child-first zero-jump class therefore satisfies

```text
S >= f V / (8 K).                                     (7)
```

The predecessor states `8 sum K_t` and `fV/(16K)`. Equations (6) and (7)
halve the former coefficient and double the latter lower bound. This
improvement uses the new sharp scalar inequality. It does not require
recounting any predecessor endpoint or numerical fixture.

The scalar constant in (1) is optimal. We do not claim optimality of the
matrix coefficient four: the triangle inequality and row estimates in (5)
may leave joint slack. The native jump, conditioning premise and original
boundary hypotheses remain explicit. General ill-conditioned or native-
interleaved sparse algorithms are not excluded by (7).

## Credit and limits

Credit Chris R / Clear1nsight #4036 for the preconditioner, boundary potential,
native-cut accounting and returned-clean argument, and #4009/#3989 with
Gonzalo Mier #3975 and their retained selected/native lineage for the Pauli
boundary. Nir Ailon and Gal Yehuda supply the classical conditioning and
preconditioned quasi-entropy method cited by #4036. Triangle inequalities,
binary entropy and elementary calculus are classical. No general literature
priority is claimed for them or for scalar entropy bounds.

The new contribution is the sharp all-complex defect proof, equality
classification and its stronger source-relative sparse-feedback consequence.
This is a written scoped proof with finite corroboration. It supplies no
physical caller, new native word, complete multiplication theorem, supplier
admission or new kappa. Physical routing, precision, stock and all-size
compiler/outer obligations remain outside this package. Independent human
and formal proof-kernel review are unclaimed.
