# Equal gains uniquely minimize cycle conditioning at fixed product

This contribution was produced by Nick Petalas. Apache-2.0.

Let `W>=2`, `d>=1`, and let `U_0,...,U_(W-1)` be arbitrary complex unitary
`d x d` matrices. For positive real gains `g_j` with geometric mean
`r=(product_j g_j)^(1/W)` in `(0,1)`, define

\[
 (T_gx)_j=g_jU_jx_{j+1\bmod W},\qquad A_g=I+T_g.
\]

In the ordinary, unweighted Euclidean norm,

\[
 \boxed{\kappa_2(A_g)\ \geq\ \kappa_2(A_r),
 \qquad\text{equality if and only if every }g_j=r.}
\]

Here `A_r` uses the **same unitary edges**, with every gain replaced by `r`.
Thus unequal positive gains cannot improve conditioning, even before the
unitary edges are optimized. Individual gains may exceed one.

This is a **scoped algebraic proof**, with exact finite corroboration. It
settles the fixed-product algebraic part of the nonuniform-gain question
left by [PR #4880](https://github.com/CrocSwap/integer-mult-bounds/pull/4880).
That predecessor proves the equal-gain optimum and is cited as a premise,
not audited or replayed here. No new supplier, kappa or multiplication
theorem is claimed.

## Sharp fixed-product optimum

Put `a=1+r^2`, `b=2r`, `c=cos(pi/W)`, and `H=U_0...U_(W-1)`.
Combining the new comparison with #4880 gives

\[
 \min_{\substack{g_j>0,\ \prod g_j=r^W\\ U_j\text{ unitary}}}
 \kappa_2(A_g)=
 \begin{cases}
 \sqrt{(a+bc)/(a-bc)},&W\text{ even},\\
 (1+r)/\sqrt{a-bc},&W\text{ odd}.
 \end{cases}
\]

Equality holds exactly when every gain equals `r` and
`H=(-1)^(W+1) I_d`. The numerical formula and the ordered-product criterion
on this equal-gain locus belong to #4880. The new step is that no nonuniform
positive gain vector can attain or beat them. At three banks and product
`1/8`, the exact optimum remains `sqrt(3)`; every unequal gain vector has a
strictly larger condition number, whatever its unitary couplings.

This fixes the product, rather than the arithmetic mean or a physical gain
tariff. It does not compute the exact optimum for a prescribed unequal vector.

## Proof of the strict comparison

### Positive diagonal similarity preserves the spectrum

Set `D_0=1` and `D_(j+1)=r D_j/g_j` for `0<=j<W-1`. Regard `D` as the block
diagonal matrix with blocks `D_j I_d`. All blocks are positive. The product
constraint gives `g_(W-1)=r D_(W-1)/D_0`, so the closing edge satisfies the
same identity as every other edge. Direct substitution yields

\[
 T_g=D(rS)D^{-1},\qquad A_g=D(I+rS)D^{-1}=DA_rD^{-1},
 \qquad (Sx)_j=U_jx_{j+1}.
\]

The operator `S` is unitary. Hence `A_r` is normal, every eigenvalue `z` of
`T_g` has modulus `r`, and every eigenvalue `1+z` of `A_g` is nonzero.
In particular all matrices in the statement are invertible, even when an
individual gain exceeds one.

Let `M` and `m` be the largest and smallest eigenvalue moduli of `A_g`.
The normal matrix `A_r` has the same spectrum, so
`kappa_2(A_r)=M/m`. The spectral-radius inequalities give

\[
 \|A_g\|_2\geq M,\qquad \|A_g^{-1}\|_2\geq 1/m.
\]

Their product proves the non-strict comparison. This uses similarity only
to identify eigenvalues; it does not assume similarity preserves Euclidean
singular values.

### Equality forces all gains to agree

Suppose the condition numbers agree. Each of the preceding inequalities has
a positive right side, so equality of their product forces `||A_g||_2=M`.
Choose a nonzero eigenvector `x` of `T_g` with eigenvalue `z` for which
`lambda=1+z` has modulus `M`. Then `A_g x=lambda x` attains the operator
norm, so

\[
 A_g^*A_gx=M^2x,
 \qquad A_g^*x=\overline\lambda x,
 \qquad T_g^*x=\overline z x.
\]

The middle identity follows by dividing the first by the nonzero `lambda`.
Consequently `T_g^*T_gx=r^2x`. But direct block multiplication gives

\[
 T_g^*T_g=\operatorname{diag}
 (g_{W-1}^2I_d,g_0^2I_d,\ldots,g_{W-2}^2I_d).
\]

Every block `x_j` is nonzero. Indeed `g_jU_jx_(j+1)=z x_j`, and `g_j>0`,
`z!=0` and invertibility of every `U_j` propagate a zero block around the
whole cycle, contradicting `x!=0`. The diagonal identity therefore forces
`g_j^2=r^2` for every `j`. Positivity gives `g_j=r`. Conversely those gains
make `A_g=A_r`, proving the equality statement.

The corollary now follows from #4880's equal-gain theorem. Its attaining
closing edge remains available, so the minimum is achieved in every `d`.
The spectral-radius and norm-attainment tools are classical; no literature
priority for those methods is asserted.

## Exact finite evidence

The standalone verifier constructs literal rational matrices, with no
predecessor imports or scientific replays. Its fixed domain has
`W in {2,3,4,5,7}`, `d in {1,2}`, `r in {1/3,1/2}`, two signed scalar edge
products, and two rational orthogonal bank-gauge families. One matrix family
has a noncentral ordered product. The dimension-two cases include
noncommuting edges and nonmonomial rational orthogonal matrices.

For each edge tuple it checks three gain profiles `g_j=r 2^(e_j)`:
all exponents zero, `(1,-1,0,...)`, and `(2,0,...,-2)`. It checks exact
diagonal similarity, both weighted-shift Gram diagonals, and normality of
the uniform comparator. Independent rational positive-definiteness tests
enclose both extreme eigenvalues of each literal Gram matrix. The resulting
condition-ratio brackets are strictly separated for every nonuniform fixture.
The global sharp formula is not numerically retested as the deliverable.

The generated receipt enumerates 120 literal cycles, 80 strict gaps and 40
uniform controls, including 54 cycles with noncommuting edges and 40 with
a gain above one. Thirteen named boundary controls cover invalid gains,
product, mean, bank count, shape and unitarity, a reversed similarity gauge,
singular and indefinite pivots, and two changes of contract.

In the same-spectrum exhibit, `A=[[1,1],[-1/4,1]]` has the uniform comparator's
eigenvalues but a nonscalar Euclidean Gram matrix satisfying
`det(tI-A^T A)=(16t^2-49t+25)/16`. In the changed-metric exhibit, its diagonal weighted
bank norm makes it a scaled isometry. This shows why the unweighted Euclidean
norm and the distinction between eigenvalues and singular values matter.

The arbitrary-width, arbitrary-complex theorem rests on the written proof.
Finite rational comparisons corroborate it within the enumerated domain.
Receipts come from the verifier and bind all five package files by SHA256;
none is hand-written or retained as a generated checkout output.

## Reproduce

From the repository root, using only the Python standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unequal-gain-cycle-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unequal-gain-cycle-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unequal-gain-cycle-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unequal-gain-cycle-optimum --check-source-history
```

Other hosts may substitute any CPython 3.12 interpreter. The direct marker is
`PASS_UNEQUAL_GAIN_CYCLE_OPTIMUM`. Redirect stdout outside the checkout to retain
the generated receipt. The registered normal and optimized commands run every
fixture and control; scientific checks use explicit exceptions.

The selected source-binding orientation passed on canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8, after its
omitted inputs were materialized with the sparse helper. That command is
metadata orientation, not a supplier replay. The original formal-interface
card is explicitly changed to a written algebraic theorem rather than a
proof-assistant formalization or predecessor audit. TASK.json records this
scope and the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213514).

## Attribution and limitations

Credit Nick Petalas #4880 for the equal-gain theorem and open nonuniform
question. Chris R / Clear1nsight #4842 supplies the complete-cascade context;
hexapode #4818/#4819/#4826 supplies the proposed schedules. The retained
construction lineage includes Dugongue #4743, Yiyang / Lyy-iiis #4710,
lee-phys #4688 and Jacob Alan Sussman #4628. William Lawyer #852 studies
balanced weighted-cycle inverses in the infinity norm under local weight caps;
it is a different contract and is not replayed or contradicted here.
All predecessor credit and source notices remain unchanged by citation.

The theorem assumes scalar positive gains, unitary edge factors, one directed
cycle and unweighted Euclidean bank norms, with geometric mean strictly below
one. Nonunitary factors, zero gains, singular mean-one cases, changed graphs
and other norms are excluded. No quantitative uniform gap away from equal
gains or exact optimum for a prescribed unequal vector is supplied.

Native emission of changed gains/couplings, arbitrary dirty-bank ownership and
restoration, independent targets, normalization, intermediate amplification,
complete caller costs, stock, compiler, physical tape, rounding and analytic
recovery remain unpriced. A diagonal similarity is not a free physical
normalization. No family construction expansion or selected-frontier change
follows. Lean, Docker, predecessor scientific suites and the selected complete
cold replay are unrun. Independent human and formal proof-kernel review are
unclaimed.

Power-of-ten inspection: no recursion; all scientific loops have fixed finite
domains, matrices have at most 14 rows and each root bracket uses exactly 24
iterations. Functions stay below 60 physical lines. Python fractions and
collections allocate dynamically, a managed-runtime deviation; fixed rational
inputs and bounded matrix sizes bound live data. The rejection helper's only
indirect targets are the two named local functions `cycle` and
`check_similarity`. Warning-strict ordinary and optimized replay are registered.
No package verifier writes files or launches processes.

## Open next questions

- Can one physical three-bank native word realize the attaining closing
  product while retaining arbitrary input banks and every independent target?
  Start with one literal caller and its full paid invoice. Native compatibility,
  ownership and restoration costs are the blockers.
- For one prescribed nonuniform gain vector, what is the exact optimum over
  unitary couplings? Start with a priced two- or three-bank vector and a full
  singular-value calculation. The present fixed-product theorem gives strict
  exclusion of the uniform benchmark, not that different optimum or its tariff.
