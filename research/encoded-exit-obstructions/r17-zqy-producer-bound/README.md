# R17: no structured producer of b = Z Q Y beats break-even (negative result, no κ claim)

Question (from #5428 target 1 and #5415's encoded-output exit): can the backward FULL buy the observation
b = Z Q Y for at most break-even cost, using a producer that is **not** a termwise sum of conjugated queries?
The task listed several candidate shapes: shared higher-rank intermediate jobs, Hadamard/Fourier butterflies
over the 112 ports, block transforms, and reuse of data the controller already holds.

**Answer: no, for every producer that reads post-return data.** Any such producer needs at least **112 paid
jobs** per backward FULL, of any rank and any operator type. Under concave pricing this costs at least 112
H1-equivalents. Break-even is 63.52. The whole #5415 exit (b together with the 8 restoring calls) needs at
least **120** paid jobs, so #5415's constructive 120-H1 exit is optimal both in job count and in concave cost.
If the producer also reads a pre-return copy of y or h, the only producer known is D·Z·y at 8 H8, which buys
back the deleted centres. It costs 63.598 H1-equivalents per FULL and fails: its root is 0.0030223874, below
U. A lower bound for that wider class is open (see §5).

## 1. Cost model (as the repository prices it)
- Pricing (R16 `price16.py`, #5428 PROFILE): M(C) = Σ_T n k^(1−C) − Σ_P n r^(1−C). b-free base:
  T0+{9:128}, P0+{1:128} (8 exit H1 and 8 restored H9 targets per backward FULL, 16 FULLs).
  A purchase adds its paid jobs ×16. Root > U = 0.00302728825 iff the purchase costs
  Σ r^(1−U) < **τ = 63.5226717504634927** per FULL (`tools/price17.py`). So 63 H1 passes and 64 H1 fails.
- Fields and operations (#5415 PROOF §1, coded-native-caller/PHYSICAL.md "Universal scope"):
  - Every field is a 9-axis address space at fiber width f.
  - Physical maps are width-1 operators lifted as f-fold tensor powers. This includes absolute phase: i^γ lifts
    to i^(fγ).
  - Owner/scalar coefficients are applied once and do not depend on f.
  - Identities must hold at every f ≥ 1.
  - Ordinary (non-recursive) work: monomial field maps (P/D/X/phase, i.e. rank-0 Cliffords) plus scalar
    ADD, SCALE, COPY, CLEAR and zero_retag.
  - Paid work: recursive Gaussian children of rank r ≥ 1, each acting on one field.
  - A producer is a finite straight-line program over these operations, independent of f.

## 2. Two lemmas
**Lemma 1 (tensor-power independence).** Let x_1..x_m be distinct matrices and α_t scalars that do not depend
on f. If Σ α_t x_t^{⊗f} = 0 for every f ≥ 1, then every α_t = 0.

Proof: pick vectors a, b with distinct nonzero values λ_t = ⟨a, x_t b⟩. Pairing with a^{⊗f}, b^{⊗f} gives
Σ α_t λ_t^f = 0 for all f ≥ 1, and the Vandermonde matrix is invertible.

Consequence: give each field a *formal value* in C[G]^{vars}, a finite sum of (width-1 operator,
input-variable) terms. Free and paid operations act on formal values by left multiplication and linear
combination. Evaluation at width f is exact. A producer is correct at all widths iff its output's formal value
**equals** the target's formal value.

**Lemma 2 (one vector per paid job).**
- Setup: group each formal value by right monomial cosets x·Mon. Here Mon is the group of invertible monomial
  operators. The coset x·Mon is determined by the Lagrangian x(L_Z). The value at a coset c is the sum of the
  coefficient vectors of the terms in c, and lies in C^{vars}.
- Free operations:
  - A monomial m maps the value at c to m·c.
  - It fixes the base class Mon and permutes the non-base classes.
  - ADD, SCALE, COPY and CLEAR are linear.
- Potential: let S be the span of all values at non-base classes, taken over every field ever computed.
  Free operations never enlarge S.
- Paid jobs: a job g acting on a field v (g any invertible operator, of any rank, Clifford or not) produces
  values {v(g⁻¹c)}. Its non-base values are old non-base values plus at most the single vector v(Mon). So
  dim S grows by at most 1.
- Conclusion: **#paid jobs ≥ dim(S_0 + S_target) − dim S_0**. Here S_0 is the span of the input data's non-base
  values, and S_target is the span of the target's non-base values.
- Control (`tools/lemma_sim.py`): 300 random 3-qubit programs with random monomials, ADDs and random-rank
  Clifford jobs give max(dim S − #jobs) = 0. One job per variable attains the bound.
- Mutation: treating one C gate as free gives dim S = 4 with 0 paid jobs. The lemma really depends on
  Gaussians being paid.

## 3. Theorem (post-return producers)
The FULL return holds X = Dx − Ry + RWh, Y = Dy, H = D(h − Zy), 400 autonomous helpers and owned zero fields.

Change variables to ξ = X, η = Y, ζ = H. This change is invertible: x occurs only in X, h only in H and X,
and right multiplication by D is injective on C[G]. In these coordinates every available field is a base
variable, so S_0 = 0. Any other data that are formally independent of this FULL's inputs are also base
variables.

Target: b_k = Σ_j (M_kj/2) Km_k⁻¹ Kp_j Q η_j. For a fixed mode k, the 56 classes Km_k⁻¹ Kp_j Q·Mon are pairwise
distinct and non-base:
- every term has rank 1;
- every quotient inside a mode has rank 2;
- this holds for all four Kp^±/Km^± conventions.

So the value of b_k at class (k, j) is (M_kj/2) e_j, and S_target = span{e_j} = 112 dimensions (`tools/exit_lb.py`,
exact rational rank, repository `clifford_exact` with absolute phase):

| target | dim S_target = paid-job lower bound | non-base classes |
|---|---:|---:|
| b = Z Q Y (each of 4 K conventions) | **112** | 448 (56 per mode) |
| whole #5415 exit (H_o = QH + b, X_o = X − W H_o, Y_o = Y) | **120** | 12,552 |
| control: port maps set to identity | 8 | — |
| control: same b in y-coordinates (pre-return y as base) | 8 | — |
| control: monomial target Z Y | 0 | — |

Each paid job costs r^(1−U) ≥ 1. So any post-return producer costs ≥ 112 > τ = 63.52, and its root is 0
(`price17.txt`). □

What the theorem covers: every mechanism in the task, at once.
- Shared higher-rank intermediates: one rank-r job still serves only one new port direction, whatever its
  concave discount.
- Butterflies or Hadamard combinations over ports: the garbage cancellation they need is counted.
- Block transforms that put ports in a common coset: impossible, because the 56 classes per mode are pairwise
  distinct.
- Joint diagonalisation by a common transform, followed by any post-processing.
- Producers in which several modes share jobs.
- Non-Clifford jobs.

The R16 coset screen only covered termwise sums of conjugated queries. This bound covers all producers.

## 4. Scope of #5427 (verified)
#5427 works in the formal free-word grammar of frozen words. Its result: b is not a *free* combination of
retained versions, and no paid response can be reused. It explicitly does not bound a new paid producer.
§3 supplies that bound for post-return data.

#5427's caller-level test admits the whole caller history, which includes this FULL's input bank y. In that
wider data model a paid producer exists (§5). So "b absent from history" does not by itself imply that b is
expensive.

## 5. Not covered: pre-return copies of y or h (open, but economically it is the centre lever)
If the caller keeps a copy of the FULL input y (or h), then b = Z R y = Q·(D Z y). Also Q H + b = Q(H + DZy) = Q D h.
So one producer is **8 H8** on D Z y (or on D h), with the exit's 8 Q calls merged. This is the deleted centre
transport bought back:
- cost 8·8^(1−U) = 63.598 > τ = 63.523;
- root 0.0030223873635, below U;
- 8 H9 on R Z y costs 71.52 and fails as well.

In this data model the Lemma-2 bound becomes vacuous: y and Y = Dy are two views of one variable, so S_0 is
full. A sharp lower bound would need element-level reasoning, not class-level reasoning; this remains open. Any
gain would have to beat 8 rank-8 transforms of 8 generic independent fields by more than 0.076 H1-equivalent
per FULL. That is the centre-interface lever (#4694/#4698/#4700; merging the 8 H8 into one job is the
contested centre merge). It was out of scope for R16/R17.

Other assumptions behind the theorem, each needed for a counterexample:
1. Exact producer. Approximate producers are not covered.
2. Every paid job acts on one standard-size field. Packing 512 fields into one field of width f+1 is a
   different recursion size.
3. The purchase jobs carry no productive target credit. Crediting them would need a new target contract.
4. Free operations are monomial. If any non-monomial operation were free, the lemma would fail (see the
   mutation control).

## Reproduce
```sh
cd ~/imb-harness/r17/tools
OPENBLAS_NUM_THREADS=1 /opt/homebrew/bin/python3.12 -B exit_lb.py     # ~20 s, reads ~/imb-r17 (upstream/main 32890bc5d)
OPENBLAS_NUM_THREADS=1 /opt/homebrew/bin/python3.12 -B lemma_sim.py   # lemma control + mutation
/opt/homebrew/bin/python3.12 -B price17.py                            # break-even and route prices
```
Outputs: `exit_lb.txt`, `exit_lb.json`, `lemma_sim.txt`, `price17.txt`.

Credits:
- zxv: #5415 exit contract and the 120-H1 upper bound shown optimal here; #5428 targets; #4359 paradigm.
- Dillon Amburgey: #5402 provider and physical mode maps.
- Clear1nsight: #5413 selected caller.
- Ali Romman / aliromman: #5383/#5398 relations and caller.
- Matarener: #5427 retained-span result, whose scope is extended here.
- Dugongue, #4929/#4933 lineage: normalizers and code.
- Cao Yifan: #4610 native word.
- Cinna Davis: helper/controller lineage.

Prepared with Claude Opus 5.5 (Anthropic) via Claude Code, directed by Joel Pulikkan (GamingPuzzled).
