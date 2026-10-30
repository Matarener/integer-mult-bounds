# Affine native phase tags at one retained warp

The first retained PR3987 warp recipe has affine offset 426 and scalar phase 1.
It is exactly `J_(A,426) Z_16`; its actual retained inverse is
`J_(A^-1,330) Z_64`. This extends PR4002's linear K/adjoint tag discipline
across this specific translated monomial, with the translation-induced scalar
retained. It does not change the compiler or claim a cheaper native interface.

## Algebra and scope

Use the predecessor ket convention and right-to-left composition. For invertible
binary A and binary b, let `F(x)=Ax+b`, `P_F|x>=|F(x)>`, and
`J_F=D P_F D^-1`, where `D|x>=i^wt(x)|x>`. Thus

```
J_F|x> = i^(wt(F(x))-wt(x)) |F(x)>,
J_H J_F = J_(H o F),
Z_u J_F = (-1)^(u dot b) J_F Z_(A^T u).
```

The first composition follows by cancelling adjacent D factors. The last
identity follows by evaluating `u dot (Ax+b)` on each basis vector. Both
retain absolute phase, including the value at zero.

Represent an admitted tagged monomial as `M(F,c,t)=i^c J_F Z_t`, with c modulo
four. For `H(x)=Bx+d`, direct substitution gives the exact law

```
M(H,e,u) M(F,c,t)
  = M(H o F, c+e+2(u dot b), t+A^T u),
H o F(x) = BAx + Bb+d.
```

Binary additions are XOR. Its adjoint is

```
F^-1(x) = A^-1 x + A^-1 b,
u = A^-T t,
M(F,c,t)^adjoint = M(F^-1, -c+2(u dot b), u).
```

Indeed the composition rule gives zero residual tag and scalar, and identity
permutation; the other product also cancels. For a chronological signed word,
first replace each inverse by this adjoint descriptor. Start `P=I,b=0,C=0,v=0`.
For each descriptor `(A_i,b_i,c_i,t_i)`, use the OLD P,b on the right:

```
C <- C+c_i+2(t_i dot b) mod4;   v <- v+P^T t_i;
b <- A_i b+b_i;                P <- A_i P.
```

Induction with the displayed composition law proves the word is
`i^C J_(P,b) Z_v`. This is an arbitrary-dimension theorem for this admitted
alphabet. It does not say every serialized Clifford monomial belongs to it.
In particular, checking coordinate inputs alone does not certify that a general
quadratic residual is linear; the source application below checks all512 states.
Nonmonomial children remain outside this rule.

## Actual source application

The pinned `research/native-lift-phase-tags/source/RECIPES.json` exports PR3987
at `fc536202fdaa924158789a5ef59ac079bbe21922`. Items0 and1 are opposite signs
of the same warp with swapped entrance/terminal frames, not invented adjacent
gates. Their coverage records include base/extra providers, new version,
index42/register1 and index44/register6. The forward left recipe is

```
matrix_rows = [265,202,396,184,128,136,16,64,384]
offset = 426; phase = 1
quadratic_rows = [264,200,392,119,184,152,202,246,5]
linear_Z4 = [0,2,0,2,1,2,1,1,0]
```

Its phase polynomial is evaluated on INPUT x, while the permutation outputs
`Ax+426`. Subtracting `wt(Ax+426)-wt(x)` gives exactly `2(16 dot x)`.
The inverse has rows `[289,162,308,48,64,104,128,16,272]`, offset330 and
source phase0; its normalized constant and tag are `(0,64)`. The zero normalized
constants do not license dropping source scalar1: it is already incorporated
in `wt(426)=5`. Both inverse compositions are checked on all512 basis states.

The separate calibration `Z_2 M` has scalar correction2, since `2 dot 426=1`,
and pulled-back mask202. Dropping that scalar reverses all512 columns. This
calibration is not asserted to be a source-word adjacency. Reusing forward
426 as inverse offset instead of330 also breaks all512 columns. Dropping the
forward source phase1 breaks all512 columns. No free implementation, physical
tariff, whole-program dirty restoration, or supplier admission follows.

## Reproduce

```
python3 -B scripts/research_package.py --package research/native-affine-phase-tags
python3 -B research/native-affine-phase-tags/verify.py
python3 -O -B research/native-affine-phase-tags/verify.py
```

Python standard library only; the standalone verifier requires declared source
files but no Git/network. It imports no predecessor executable, verifies pinned
source bytes, and compares exact integer phase exponents. This finite evidence
corroborates the general proof; it is not proof-kernel or human acceptance.

Overlap gate: current main721c038 and complete cached PR/discussion snapshot
(2026-10-28 06:17/06:18 UTC) were searched for affine phase-tag/signed-word
closure. PR3987 already checks affine serialization/inverse action; PR4002 at
d593941ea0a4926021cba9d01fe60500579e464f explicitly leaves translations open.
The addition is the scalar-aware tag law and this binding, not the predecessor
inverse audit. A cache search does not establish exhaustive novelty.

## Open next questions

Bind the tag rule to a priced actual neighboring interface and its native
caller. First authenticate that adjacency and every compensating phase, then
compare the complete physical bill. No such adjacency or bill is supplied here;
there is no selected-frontier update or new kappa claim.

Credit ToikY's PR4002 normalization, Chris R / Clear1nsight's PR3987 phase audit,
Dugongue PR3945/3929, dataisfire PR3734, Cinna Davis PR2226, and the retained
native/compiler lineage and notices. New extension/checker: JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0. Sources remain unchanged.
