# Exact recovery across precision changes and repeated native recoding

**Status:** proposed scoped theorem with a constructive integer codec and finite
calibration. The argument below supplies the all-input implications; the probes
do not constitute independent proof review or a complete multiplication theorem.

The source matrix and finite kernel are pinned in [SOURCES.json](SOURCES.json).
The same-grid `13^8` result belongs to [Ali Romman](https://github.com/aliromman),
[PR #5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323).
The additions here are the exact relative-precision frontier, its code-coset
decoder, and the sharp composition law under changing integer frames.

## 1. General rounded low-rank maps

Let `M` be an integer `n × r` matrix of full column rank, `β` a positive
integer, and `R` componentwise nearest rounding with half ties away from zero.
Write

```text
K(z) = z − M R(Mᵀz/β),       H = MᵀM − βI.
```

Inputs lie in `B Z^n`, where `B` is a nonsingular integer matrix. The input
coordinate is `x`, the actual fine-grid input is `z=Bx`, and the output is `y`.
Set `s=Mᵀy`.

**Fiber theorem.** Preimages of `y` correspond bijectively to integer vectors
`q` satisfying

```text
y + Mq ∈ B Z^n,
R((s + MᵀMq)/β) = q.                                      (1)
```

Reconstruction is `x=B⁻¹(y+Mq)`. The second condition is equivalently
`−β/2 ≤ s+Hq ≤ β/2` componentwise, with the following endpoint rules:
at residual `−β/2` the corresponding `q_j` must be at least one; at residual
`+β/2` it must be at most minus one.

*Proof.* A forward input has `z=y+Mq`, hence (1). Conversely (1) gives an
integer `x` whose defining rounded quotient is exactly `q`. Distinct `q`
give distinct inputs because `M` has full column rank. The endpoint rules
follow directly by rounding `q_j±1/2` away from zero. ∎

**Finite-state dichotomy.** A fixed finite alphabet suffices to recover every
input from its output and a retained tag if and only if `H` is nonsingular.
When `H` is nonsingular, every fiber lies in a translated parallelotope and
has at most

```text
∏_j ( floor(β · ||row_j(H⁻¹)||₁) + 1 )                     (2)
```

points. If `H` is singular, choose a nonzero integer kernel vector `u`.
Then `K(kMu)=0` for every integer `k`. Multiplication by `det(B)` puts these
inputs in `B Z^n`, since `B adj(B)=det(B)I`, and preserves their distinctness.
Thus that fiber is infinite. In the nonsingular case, the coordinate widths
of the parallelotope give (2).

The exact minimum tag alphabet is the maximum fiber size: a tag must separate
inputs in the same fiber; conversely, order the finitely many candidates in
each fiber and retain their index. This is an effective finite enumeration for
rational data. Its running time can grow exponentially with rank; no general
efficient reversible synthesis follows from this existence statement.

## 2. The pinned 112-owner matrix

For the literal matrix in [FIXTURE.json](FIXTURE.json),

```text
n=112, r=8, β=52, MᵀM=56I, H=4I,
A=I−MMᵀ/4,                L=A⁻¹=I−MMᵀ/52.
```

Each row has four signs in `{−1,+1}`. Consequently `K(z)=Lz+e(z)` with
`||e(z)||∞≤2`; the physical error is at most two output-grid units. This is
the map implemented by [Brian](https://github.com/JoyboyBrian)'s unchanged
[PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035) kernel.
Its owned zero-writing is classical destructive cleanup.

Let `C` be the binary span of the rows of `M`. Direct finite source identities,
checked in `source_facts` and printed in [RESULT.json](RESULT.json), give

```text
C=C⊥, |C|=16, W_C(a,b)=a^8+14a^4b^4+b^8.                  (3)
```

There is also, for each `j`, a pair of actual signed rows whose sum is `2e_j`.
Their row indices and signs are in the receipt. These facts give the complete
integer row lattice

```text
row_Z(M) = {v ∈ Z^8 : v mod 2 ∈ C}.                        (4)
```

Indeed reduction modulo two gives one inclusion. For the reverse inclusion,
lift a binary row combination with the desired parity and correct its even
coordinate differences using the eight `2e_j` witnesses.

It follows for every `g≥1` that

```text
Mq = 0 mod 2^g
  ⇔ q=2^(g−1)v with v mod 2 ∈ C⊥=C.                       (5)
```

Necessity of the divisibility of `q` follows by applying the `2e_j` row
combinations. After division, the remaining condition is exactly binary
orthogonality to all rows. This proves (5) at every precision, rather than
only those tested.

## 3. Exact relative-precision frontier

The coarse input is `x∈Z^112` and the fine output is

```text
y = K(2^g x),       δ_out = δ_in / 2^g.                    (6)
```

The integer `g≥0` is fixed known **relative** refinement. Increasing both
absolute precisions together leaves `g` unchanged.

**Theorem.** The exact maximum fiber sizes and minimum fixed-length recovery
tags for (6) are:

| Relative bits `g` | Maximum states `F_g` | Packed bits | Sufficient coarse bound `||x||∞≤H` to attain it |
|---:|---:|---:|---:|
| 0 | 815,730,721 = `13^8` | 30 | 24 |
| 1 | 51,008,161 | 26 | 12 |
| 2 | 362,401 | 19 | 6 |
| 3 | 4,096 | 12 | 16 |
| 4 | 16 | 4 | 14 |
| ≥5 | 1 | 0 | 0 |

Thus five relative bits are necessary and sufficient for tag-free
injectivity on the unbounded coarse lattice. The displayed bounds on `H`
are sufficient witnesses, not claimed minimal range thresholds.

### Upper bound

For each mode, with `s=Mᵀy`, (1) gives the consecutive candidates

```text
ceil((-26−s_j)/4) ≤ q_j ≤ floor((26−s_j)/4),
R((s_j+56q_j)/52) = q_j.                                  (7)
```

The closed interval can have fourteen integers only when both boundary
residuals occur. Its lower endpoint would require `q_j≥1` while its upper
endpoint would require `q_j≤−1`; they cannot both survive. Removing invalid
boundary endpoints leaves at most thirteen consecutive integers. For `g=0`,
the modes are independent, giving `13^8` as in the predecessor result.

For `g≥1`, two solutions to the coarse-lattice condition `y+Mq=0 mod 2^g`
differ by (5). Thus each coordinate has a fixed residue modulo
`d=2^(g−1)`. Its candidates in (7), divided by `d`, are at most
`ceil(13/d)` consecutive integers. Splitting by parity gives a preferred
parity with at most `a` choices and the other with at most `b` choices, where

```text
(a,b) = (7,6), (4,3), (2,2), (1,1), (1,0)
         for g=1,2,3,4,≥5, respectively.                  (8)
```

The remaining parity condition is one coset of `C`. Allowing every coordinate
its maximal counts bounds the fiber by a coset weight enumerator. For every
binary linear code and `a≥b≥0`, the zero coset maximizes this enumerator:

```text
Σ_{c∈C+z} a^(8−wt(c)) b^wt(c)
 = |C|/2^8 · Σ_{u∈C⊥} (−1)^(u·z)
                         (a+b)^(8−wt(u)) (a−b)^wt(u)
 ≤ Σ_{c∈C} a^(8−wt(c)) b^wt(c).                           (9)
```

This is the elementary character-sum form of the classical MacWilliams
identity; all coefficients on the right of the middle expression are
nonnegative. Coordinatewise preferred parities simply change the coset `z`.
Equations (3), (8), and (9) give the table. For `g≥5` the upper bound is one;
an input supplies a nonempty fiber, so the map is injective.

### Attaining fibers

For `g=0,1,2`, use `y=0` and `q∈{−6,…,6}^8`, subject to (5).
For `g=1`, even/odd counts are `(7,6)`. For `g=2`, write `q=2v` with
`v∈{−3,…,3}^8`; its preferred parity is the all-one word, which belongs
to `C`, so the count is `W_C(4,3)`. Reconstruct `x=Mq/2^g`.
The four-term rows give the first three displayed bounds on `H`.

For `g=3`, set `y=−M(2·1)`, where `1` is the eight-mode all-one vector.
Now `s=−112·1`, and (7) includes the thirteen integers centered at `28`.
The coarse congruence requires `q−2·1` in the kernel modulo eight, so
each `q_j` is in `{22,26,30,34}`. There are two choices of each residual
parity per coordinate and sixteen allowed parity words: `16·2^8=4096`.
The reconstruction `x=M(q−2·1)/8` has norm at most sixteen.

For `g=4`, use `y=−M(4·1)`. The scalar interval is centered at `56`;
the coarse congruence leaves `q_j∈{52,60}`. Equation (5) selects exactly
sixteen parity words. Here `x=M(q−4·1)/16` has norm at most fourteen.
All these candidates have residual strictly inside the half-tie endpoints.
Finally the zero input attains the singleton bound for every `g≥5`.

### Constructive codec

[frontier.py](frontier.py) implements (7) without enumerating the enormous
fibers. The `2e_j` witnesses determine `q` modulo `2^(g−1)`. The remaining
112-bit parity syndrome determines at most sixteen binary code-coset words.
For each word the admissible quotients form a Cartesian product of eight
lists. A block offset plus mixed-radix rank indexes all candidates exactly.
Decoding unpacks that rank, computes `(y+Mq)/2^g`, and checks the defining
forward relation. The codec therefore attains the minimal state alphabet.

The implementation accepts `0≤g≤16`; this is an operational resource limit,
while the proof covers all nonnegative `g`. It uses arbitrary-precision
Python integers, with no bit-operation/tape price or reversible cleanup claim.
The source identity, relative precision, output, and tag must belong to the
same invocation. Packet metadata is a validation interface; fixed source and
precision data are not a hidden variable recovery channel.

For `N` independent real coordinates the exact maximum is `F_g^N` and the
minimum packed tag uses `ceil(log₂(F_g^N))` bits. With differing fixed
relative precisions the maximum is the product of their `F_g` values.

## 4. Sharp history accumulation under changing frames

Put `F=13^8`. Let each step be

```text
f_i = V_i ◦ K ◦ U_i,       U_i,V_i ∈ GL_112(Z),
```

where the frame changes are fixed and known independently of the input.
Only the final 112-owner output and retained history are available for exact
recovery; additional observations must be counted separately.

**Theorem.** The exact maximum fiber of `f_t◦…◦f_1` on `Z^112` is `F^t`.
Thus the minimal retained-history alphabet has `13^(8t)` states and needs
`ceil(8t log₂13)` packed bits. Commutation of the frames is unnecessary.

*Upper bound.* Each step has maximum fiber `F`, since integer unimodular
pre/post changes are bijections. Induction bounds each composite fiber by
`F^t`. Retaining each step's tag allows reconstruction in reverse order,
attaining an alphabet of this size.

*Lower bound.* The matrix `L` has eigenvalue `−1/13` on the eight-dimensional
column space of `M` and eigenvalue one on its complement. Hence
`|det L|=1/F`. Each step is a bounded perturbation of `V_iLU_i`, and a finite
composition remains a bounded perturbation of its matrix product. Its
determinant magnitude is `F^(−t)`. Apply the following counting lemma. ∎

**Lattice-volume lemma.** If `f:Z^n→Z^n`, `L` is nonsingular, and
`||f(x)−Lx||∞≤E` uniformly in `x`, the maximum fiber is at least
`ceil(1/|det L|)` (or is infinite).

*Proof.* The number of lattice points `Lx` in `[-R,R]^n` is
`(2R)^n/|det L|+O(R^(n−1))`. This follows by tiling with the fundamental
parallelotopes `L(x+[-1/2,1/2]^n)`; their boundary thickness is bounded
independently of `R`. Their corresponding outputs lie in
`[-R−E,R+E]^n`, containing at most `(2R+2E+1)^n` integer points.
If all fibers have size at most `m`, divide the resulting counting inequality
by `(2R)^n` and let `R` increase. This forces `m≥1/|det L|`. ∎

The conclusion concerns the unbounded integer domain, and therefore some
sufficiently large finite input range. It need not hold in a prescribed small
range. The two-dimensional noncommuting controls in `verify.py` exhibit this:
one finite window reaches only sixty of the eventual sixty-four states.

For stationary frames there is an explicit sufficient range. On `x=Mv`,

```text
K(Mv) = −M R(v/13).
```

The identity uses `56/52=1+1/13`; for integer `v`, denominator thirteen
excludes half ties, making integer translation of nearest rounding legitimate.
All vectors with `|v_j|≤(13^t−1)/2` reach zero after `t` steps. Induct on
the radius recurrence `R_t=13R_(t−1)+6`. These distinct inputs give
`13^(8t)` preimages and obey `||x||∞≤2(13^t−1)`.

For `N` independent real coordinates, replace `K` by its direct product and
allow arbitrary fixed unimodular mixing of all `112N` integer fields between
steps. The same proof gives `13^(8Nt)` states. At eighteen steps and `N=1`,
packing all history together needs **533 bits**, rather than the 540 bits
from eighteen separately padded thirty-bit records.

## 5. Precision and side information conservation

Suppose step `i` instead uses `K(2^(g_i)z)`, with fixed known `g_i≥0`,
and let `G=Σ_i g_i`. For `N` real coordinates, `n=112N`. The final integer
map is a bounded perturbation of a matrix of determinant magnitude

```text
2^(112NG) / 13^(8Nt).
```

If a retained side observation has at most `S` possible values and the history
has at most `T`, injective recovery requires

```text
T S ≥ ceil(13^(8Nt) / 2^(112NG)),
T ≥ ceil(13^(8Nt) / (2^(112NG) S)),
b + log₂S + 112NG ≥ 8Nt log₂13    when T≤2^b.             (10)
```

Apply the same counting proof with at most `TS` states above each final output.
The lower bound on `T` is at least one. These are necessary bounds; sharpness
is asserted only for `G=0,S=1`. In particular the exact one-step table is
strictly stronger than the volume relaxation at positive `g`.

Nonuniform fixed diagonal refinements have the same volume argument with
`112NG` replaced by the sum of their added fractional bit positions. Other
nonunimodular maps require their determinant and actual lattice covolume.
Input-dependent frame/precision choices require counting their recoverable
control data among the retained observations or history.

This excludes indefinitely many recodings with bounded cumulative refinement,
bounded history, and bounded side information when every initial input on
growing ranges must remain recoverable. Rereading the original input, keeping
another output, changing the map, or admitting irreversible disposal changes
that contract. The result imposes no paid-query, average-entropy, or physical
thermodynamic lower bound.

## 6. Classical input, source novelty, and proof limits

Weight-enumerator duality is classical: see MacWilliams,
[A Theorem on the Distribution of Weights in a Systematic Code](https://doi.org/10.1002/j.1538-7305.1963.tb04003.x),
and Forney,
[Codes on graphs: Duality and MacWilliams identities](https://arxiv.org/abs/0911.5508).
The pigeonhole and lattice-volume arguments are elementary, and are proved
here rather than claimed as new general mathematics. The proposed repository
contribution is their exact application to this native code, including
attainment, the codec, and arbitrary changing-frame composition.

The unchanged selected record at the source pin has conditional
`κ=0.003027288235`. This package changes no selected result. Mathematical
injectivity at five relative bits does not make the retained destructive kernel
a reversible program. Source access, wrappers, output magnitude, carry widths,
codec cost, variable control, additional observations, and eventual restoration
still need a complete caller-bound implementation and invoice.
