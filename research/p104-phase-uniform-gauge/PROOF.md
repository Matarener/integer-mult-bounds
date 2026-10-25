# A phase-uniform gauge with an unavoidable completion tag

## 1. Scope and conventions

Use exactly the 104 ordered odd binary labels published by Chris R / Clear1nsight in PR3954 at `f1e2839819959cd0534d008be91ed5b79ec55a6a`, retained in `source/RESULT.json`. The physical isometry and original P104/native construction are predecessor work. This note proves a changed coordinate gauge and its operator boundary; it does not supply the missing adjacent physical producer/consumer pair or admit the predecessor scaffold.

All binary vectors use the usual dot product. Coordinates are numbered from zero; tensor coordinate `(i,j)` is bit `9i+j`. Write `j=511`, `q(x)=wt(x) mod 4`, and `chi_s(x)=(-1)^(s dot x)`. The scalar field can be Q(i), extended coordinatewise to arbitrary finite arrays. Define

```
X_u f(x) = f(x+u),     Z_u f(x) = (-1)^(u dot x) f(x),
C_u = ((1+i)I+(1-i)X_u)/2,
F_m = product_(k=0..m-1) C_(e_k),
R_G f(x) = f(G^-1 x).
```

Thus `C_u chi_s = i^(u dot s) chi_s` and `F_m chi_s=i^q(s) chi_s`. The latter is the retained full native transform, not the Walsh transform. Orthogonality of G alone does **not** imply that R_G commutes with F_m. Gates `C_u^-1` have the opposite exponent. For an orthogonal G,

```
R_G chi_s = chi_(G s),
R_G X_u R_G^-1 = X_(G u),
R_G Z_u R_G^-1 = Z_(G u),
R_G C_u R_G^-1 = C_(G u).
```

These are exact ideal operator equations. A coordinate permutation on a large physical tape is not declared free.

## 2. Explicit gauge: all product-line phases agree

Let `z=420`, with support `{2,5,7,8}`, and put

```
O x = x + (x dot z) z,
O columns = [1,2,416,8,16,388,64,292,164].
```

Because `z dot z=0`, O is involutive. Expanding `(Ox) dot (Oy)` shows orthogonality: the two cross terms cancel and the last term is zero. Since `q(z)=0`, the weight identity `q(x+y)=q(x)+q(y)+2(x dot y) mod4` gives

```
q(Ox) = q(x)+2(x dot z) mod4.                 (1)
```

The source-bound finite check verifies `q(Op)=3` on all 104 published labels. Their old weight classes were 56 of class 1 and 48 of class 3. For `K=O tensor O`, the 10,816 transformed product labels obey

```
q((Op_i) tensor (Op_j)) = 3*3 = 1 mod4.
```

K is orthogonal and bijective, so all these lines remain distinct and nondegenerate; their pairings and dimensions are unchanged. In the predecessor's positive `C_u` orientation, the normalization factor `i^(f wt(u))` is consequently the retained constant `i^(9f)` for every product line and every integer parallel-column count f. This removes the 5,376 gauge-dependent sign mismatches. It does not assert that the historical compiler already uses these coordinates or this orientation.

## 3. The completion defect is necessary throughout the orthogonal class

Use one orthogonal binary G in dimension nine identically on both tensor
factors; independent row/column gauges and arbitrary 81-dimensional gauges are
outside this quantified statement. For such G, the difference `q(Gx)-q(x)` is even and has zero polar form. Dividing by two defines a linear character, so there is a unique t with

```
q(Gx) = q(x)+2(t dot x) mod4.                 (2)
```

Diagonal products have weight class 1, so any constant product class must be 1.
If all `Gp_i tensor Gp_j` have weight class 1, then all `q(Gp_i)` have the same odd class c, either 1 or 3: a pair of different classes has product 3. The 104 source labels span the full binary nine-space. Equivalently, the equations on these labels determine at most one t for each c. The source-bound linear constraints give exactly

```
c=3: t=420;             c=1: t=91=420+511.
```

An orthogonal G fixes the characteristic vector j, because `x dot x=j dot x` for every x. Substituting x=j in (2) forces `t dot j=0`. The second candidate has odd weight and is impossible. Thus **every** orthogonal gauge making these product phases constant must send the ports to class 3 and have the same nonzero input defect `t=420`. None can preserve F_9. This is a theorem about all orthogonal gauges for these fixed labels, not an enumeration of the orthogonal group or an obstruction to general nonorthogonal/paid intertwiners.

For a general such G set `K_G=G tensor G` and

```
a = z tensor j + j tensor z
  = 430582246074561917307300
  = 0x5b2de90b7a4d216f49a4.
```

The quadratic difference for K_G is linear after division by two. Evaluating on the 81 basis tensors gives

```
q(K_G s) = q(s)+2(a dot s) mod4.              (3)
```

Indeed `q(Ge_i)=1+2z_i`, so the tensor basis column has weight class `1+2(z_i+z_j)`. This proves (3) on all 2^81 frequencies from orthogonality and 81 coefficient checks. The input character a is universal across this class of G. It is nonzero and even. The general conjugacy is

```
R_(K_G)^-1 F_81 R_(K_G) = F_81 X_a,
R_(K_G) F_81 R_(K_G)^-1 = F_81 X_(K_G a).
```

Input a and output K_G a need not coincide. No general involution is assumed. For our explicit O, `Oz=z`, `Oj=j`, hence `Ka=a`, and `wt(a)=2*4*5=40`.

## 4. Exact all-role tags, and the unresolved physical seam

For the explicit involution K, define

```
E_in = R_K,             E_out = X_a R_K.
```

The preceding equations imply

```
F_81 E_in  = E_out F_81,
F_81 E_out = E_in  F_81.                      (4)
```

Thus the two tags alternate under repeated **already completed uniform** F_81 operations. Two such operations return to the entrance tag. If instead the next operation insists on the original E_in rather than accepting the alternate tag, the seam map is `E_in E_out^-1=X_a`. Omitting it is not an identity; a character with `a dot s=1` is a separating input.

Apply the same E_in/E_out on every role of an all-role completed call, including all 72 local dirty helper roles (or every role of a declared larger owner inventory). Since (4) is an operator equality on each independently arbitrary function, it holds on their direct sum. Helpers are not assumed zero. Uniform address maps commute with scalar role matrices D,H,E0 and with the predecessor's literal slot permutation Pi; this does not make Pi a free physical move. Encoded helper equations are **not** a fresh physical dirty-return/ownership certificate: any required return to the original coordinate chart still needs its explicit boundary maps.

Both address encodings act as the identity on constant address functions.
Consequently, a nonzero role-encoding defect already visible on constant
functions cannot be removed by these uniform gauge/translation tags alone;
it still requires a role-boundary transition. This observation does not
independently certify any concurrent package's specific counterexample.

This does not instantiate PR3954's row/column producer. Define F_row,j as the product of positive C gates on the old standard active basis `e_k tensor p_j`, and F'_row,j on the new standard basis `e_k tensor q_j`, where q_j=Op_j. Define the column transforms analogously using `p_i tensor e_k` and `r_i tensor e_k`, with r_i=Op_i. The row correction is `z tensor q_j`; the column correction is `r_i tensor z`. Conjugate the old bases and apply (1) to the nine coefficient frequencies to obtain

```
R_K F_row,j R_K = F'_row,j X_(z tensor q_j),
R_K F_col,i R_K = F'_col,i X_(r_i tensor z).
```

These tags vary with the fiber. They must apply to every role in the local call, including its helpers, and reconcile on shared data owners. The alternating common-tag lemma (4) supplies no such physical matching, no free source relocation and no cost-free change of required outputs. That remains the released adjacent-call obligation.

## 5. A sharp restricted tariff for a forced translation

Fix one bank and a nonzero even vector b in any binary dimension where such a vector exists. The alphabet is exactly `C_u` and `C_u^-1` for nonzero **odd** u, each charged one call. No other operations, free translation, role mixing, ancilla, measurement or borrowed helper is allowed. Then the exact word length of X_b is four.

For an upper bound choose e to be any unit vector. Both e and `e+b` are odd, and

```
C_e^2 C_(e+b)^2 = X_e X_(e+b) = X_b.
```

For the lower bound evaluate any shorter word on frequency j, the all-ones vector. Every allowed u has `u dot j=1`, whereas `b dot j=0`. A word of odd length has an odd exponent sum of plus/minus ones and cannot have phase one. A two-call word with equal signs has phase minus one at j. With opposite signs it is `C_u C_v^-1`; if u differs from v, some frequency separates their parities, giving phase plus/minus i instead of the real phase of X_b. If u=v it is the identity. Length zero is also the identity, while X_b is not. This excludes every length below four. Allowing a constant scalar phase does not help because the zero-frequency eigenvalue fixes that scalar to one.

The written proof covers arbitrary dimension and even b. The verifier checks the constructive four-call character table; the independent checker exhausts a small three-dimensional alphabet only as corroboration. This is not a native compiler/frame admission or cross-role optimality theorem. For all orthogonal phase-uniform gauges above the tensor output defect K_G a is nonzero and even, so the same restricted theorem applies to any seam that is implemented in this exact alphabet.

## 6. Complete cost decision and stopping rule

Orthogonal K changes neither dimensions/ranks, the 36,608-role inventory, 208 local calls nor the predecessor's stipulated mass 2,576 and net progress 2,312 per call. Grant all gauge and tag work free and keep the same favorable contract. Re-derive the named gate:

```
W = 2*104^2+2*104*72 = 36608,    m=81,    N=104^2=10816,
required persistent progress = mW-N = 2954432,
remaining rank >= 2954432-208*2312 = 2473536,
lower paid mass = 208*2576+2473536 = 3009344,
capacity = 2965248,    excess = 44096.
```

These are inherited conditional hypotheses, not freshly admitted local/native calls or global owners. At `0<=saving<1`, each child of rank r<=81 has moment term at least r/81. The unchanged positive mass gap therefore still rejects this scaffold. Finite fully paid auxiliary banks preserve the numerator gap. Phase homogenization cannot by itself remove a recursive child.

If one **chooses** an appended isolated correction on every completed bank in the restricted alphabet of section 5, its extra primitive-word bill is `4W=146432` calls. **Only if each isolated C primitive is additionally admitted at one rank unit in this same ledger** does that literal route have excess `190528`, before physical wrappers. Word length alone does not establish that native tariff compatibility. This is a conditional literal-route calculation, not a lower bound on arbitrary fusion, mixed roles, different encodings or different coverage. It is not a complete upper bound on implementation time: R_K routing, chart/phase wrappers, source acquisition, dirty returns, ownership/holding/control/tapes, finite widths/precision/recovery and inherited all-size/compiler/analytic obligations remain unknown or inherited, never zero.

**NARROW / STOP.** Preserve the explicit phase-uniform gauge, its unavoidable completion character and exact restricted seam tariff. Do not expand native implementation for the unchanged failed scaffold. A genuinely changed adjacent-call contract with reconciled fiber/helper tags, actual owners and a favorable complete replacement invoice is the next meaningful task.
