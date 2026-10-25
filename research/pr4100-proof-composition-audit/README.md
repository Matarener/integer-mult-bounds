# Audit of #4100 PROOF.md's transform and exact-recovery chain

**Claim type: a scoped proof audit (written re-derivation) with finite exact
and high-precision corroboration. No new κ.** This does not accept #4100, and
it changes nothing in it or in the selected record.

## Object and outcome

The object is Cinna Davis's [PROOF.md](../unconditional-batched-crt/PROOF.md)
in #4100 (head `337d04939571a637aeab54a0f58f54fde811663a`), as retained on
canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`. This audit covers
the algebraic identities that PROOF.md composes into its outer algorithm,
section by section:

1. the address isomorphism;
2. synthetic convolution;
3. the chirp identity;
4. the exact Gaussian source-transform identity;
5. exact recovery.

**Outcome: every audited identity holds exactly with PROOF.md's own
normalizations and signs.** The recovery inequalities hold with explicit
thresholds. There is one minor presentational note (item 5d) and no
downstream change. This closes the algebraic part of gap 2 in the
[#4100 coverage map](https://github.com/CrocSwap/integer-mult-bounds/pull/4311).
It does not cover precision constants, invertibility of `N`, or costs (see
[Not covered](#not-covered)).

**Conventions.** PROOF.md's chirp section fixes these: the coefficient of
`u_z` in `Q F_t u` is `T^-1 exp(2πi Σ s_i x_i z_i/t_i)`, with
`(Qv)_x = v_(-s x)`. So `(F_n u)_k = n^-1 Σ_j e^(-2πi jk/n) u_j`, the
conjugate kernel gives `F_n^+`, and a tensor DFT is normalized by its full
size. The same convention makes every identity below hold. A different
normalization on either side of the Poisson identity breaks it (control 4).

## Results and proofs

### 1. Address isomorphism

Let the `s_i` be pairwise coprime and `P_i = Π_(j<i) s_j`. Then
`φ(k) = (k P_i^-1 mod s_i)_i` is a group isomorphism `Z_S → Π Z_(s_i)`.

**Proof.** φ is additive. If `φ(k) = 0`, every `s_i` divides `k`, so `S`
divides `k`. The cardinalities agree, so φ is bijective. Its inverse is the
unique `k` with `k ≡ P_i y_i (mod s_i)`, as PROOF.md states.

With mixed-radix digits `k = Σ a_i P_i`, φ is CRT.md's root map
`Φ_G(a)_i = k_G / P_(G,i) mod s_i`, where `G` is all axes. So PROOF.md and
CRT.md use the same map, and any group isomorphism carries cyclic convolution
of length `S` to tensor cyclic convolution.

**Checked:** 6,280 addresses over the moduli sets `(3,5)`, `(3,5,7)`,
`(3,5,7,11)` and `(5,7,11,13)`. Each address agrees with the source's
`check_batched_crt.direct()`. Convolution transport is checked exactly on
`(3,5)` and `(3,5,7)`. **Controls:** non-coprime moduli are not a bijection,
and plain residues differ from the scaled map.

### 2. Synthetic convolution

Take `R = C[y]/(y^r+1)` with `r` a power of two, and `G' = Π_(i≥1) Z_(t_i)`
with `t_i | 2r` and `M = |G'|`. Let `F_∓` be the `1/M`-normalized DFT over
`G'` with twiddles `y^(∓E)`, `E = Σ (2r/t_i) x_i k_i`.

**Twiddles are principal roots.** `ω = y^(2r/t)` is a principal `t`-th root
of unity in `R`. At each root `η = ζ_(2r)^o` of `y^r+1` (with `o` odd),
`η^e = 1` holds only when `2r | e`. So `ω^m - 1` is a unit for `m ≢ 0 mod t`,
and `Σ_x ω^(xm) = t[m ≡ 0]`.

**Normalized identities.** These give `F_-(f*g) = M (F_- f)(F_- g)` and
`F_+ F_- = I/M`, so

`M F_+((F_- f)(F_- g)/r) = (f*g)/(rM)`.

**Twist.** Multiply axis-0 coefficient `x_0` by `ζ_(2r)^(x_0)`. Because
`ζ_(2r)^r = -1`, the wrap signs of negacyclic multiplication cancel. The
twisted negacyclic product is therefore the twisted cyclic product, and
untwisting yields `(f *cyc g)/T` with `T = rM`.

**Checked exactly** in `Q(ζ_(2r))[y]/(y^r+1)` with rational arithmetic, for
`r ∈ {2,4}` and four target shapes:

- `F_+F_- = I/M`;
- the complete twist/pack/transform/product/untwist pipeline equals
  `(f*g)/T`;
- the normalized `H0 = [[1,1],[1,-1]]/2` butterfly network equals `F_-` after
  bit reversal.

**Controls:** without the twist the result is negacyclic, and omitting `/r`
changes the scale.

### 3. Chirp identity

Let `a(x) = exp(-πi s x²/t)`. For all `x, z ∈ Z_t`:

`conj(a(x)) a((x-z) mod t) conj(a(z)) = exp(2πi s x z/t)`

holds if and only if `st` is even.

**Proof.** The exponent difference is `s[(x-z)² - ((x-z) mod t)²]`. This is
zero for `x ≥ z` and `-st(2(x-z)+t)` for `x < z`. It is divisible by `2t`
exactly when `st` is even.

**Consequences.** `Q F_t u = conj(a) ⊙ [a *cyc (conj(a) ⊙ u)]/T`, and this
tensorizes over the axes. `Q` is a permutation exactly when `gcd(s,t) = 1`.
PROOF.md's "Each `t_i` is even" is the right sufficient condition for odd
primes `s_i`.

**Checked exactly:** 195 coprime `(s,t)` pairs with even `t ≤ 64`, including
periodicity of `a`. **Controls:** all 18 coprime odd-`t` cases with odd `s`
fail.

### 4. Gaussian source-transform identity

`T_gauss P_s F_s = P_t F_t S_gauss` holds for every pair of positive integers
`s, t` and every `α > 0`. Coprimality is needed only so that `P_s` and `P_t`
are permutations. Write `g(x) = e^(-πα²x²)` and `h(x) = e^(-πx²/α²)`, so that
`ĝ = α^-1 h`.

**Left side.** Poisson summation in `j`, after substituting `y = tj/s - k`,
gives

`(T_gauss P_s F_s e_l)_k = t^-1 α^-1 Σ_(m∈Z) e^(2πi skm/t) h(l - sm/t)`,

using `e^(-2πi kl) = 1`.

**Right side.** Expanding `(P_t F_t S_gauss e_l)_k` combines the residue
`m mod t` with the shift `j = l + sn` into one sum over `m' = m - nt ∈ Z`.
This gives the same absolutely convergent sum.

**The factorization.** The principal (`n = 0`) diagonal term of
`N = C T_gauss D` is `e^(-aβ_j²) e^(aβ_j²) = 1` exactly. Applying `C` and
`C T_gauss = N D^-1` gives `P_s F_s = D N^-1 C P_t F_t S_gauss` whenever `N`
is invertible.

**Checked at 60 digits:** all 51 basis rows at
`(s,t,α) = (3,4,1.7), (5,6,1.3), (5,8,2), (7,8,2.5), (31,32,3)`, for both the
identity and the factorization. The worst residual is `2.1e-58`. Gaussian
windows are truncated at nine widths, which drops mass of about
`e^(-81π) ≈ 10^-110`.

**Controls:** each is detected on every row where it can be.

| Control | Rows where it can be detected | Detected |
| --- | --- | --- |
| `F_t` normalized by `1/s` | 51 | 51 |
| `S_gauss` without `α^-1` | 51 | 51 |
| `P_t` with `+sk` | 46 (`e_0` is real and symmetric, so blind there) | 46 |

### 5. Exact recovery

**(a) Dilations commute.** Write `R = Π P_(s_i)`, a dilation by the units
`t_i mod s_i`. Since `F D_c = D_(c^-1) F`, also `F_s^+ R = R^-1 F_s^+`, and so
`(R F_s^+)(RFu ⊙ RFv) = F^+(Fu ⊙ Fv) = (u*v)/S²`. Checked exactly on the
exponent kernels for 24 `(s,t)` pairs.

**(b) End-to-end product.** Eight multiplications run through the composed
chain at `s = (3,5)`, `t = (4,8)`, `b = 3`:

1. compute `RF_s = (⊗DN^-1C)(P_tF_t)(⊗S_gauss)`;
2. obtain `R F_s^+` by conjugation;
3. scale by `S² 2^(2b+4)` and round;
4. apply the inverse address map and the carry scan.

Every product is recovered exactly, and the composed `RF_s` equals its
definition. **Control:** scaling by `S` instead of `S²` fails.

**(c) Exact inequalities.**

- **Threshold:** `T < 2^b` holds exactly when `b ≥ 8`, so PROOF.md's
  "eventually" means `b ≥ 8`.
- **Length:** for every `4 ≤ n < 2^14`, the power of two `T ∈ [4n/b, 8n/b)`
  is unique, and `T/2 ≥ 2n/b > 2Ndigits - 2`.
- **Coefficients:** `c_j < 2^(3b)`.
- **Carries:** by induction, `k_j ≤ Ndigits(2^b - 1)`, which is sharper than
  the stated `< Ndigits 2^b`. Checked on 234 worst-case digit sequences.
- **Error:** `S² 2^(2b+4) < 2^(4b+4)`. So an absolute error
  `C·2^(-4p)` with `p = 6b` becomes `< C·2^(-20b+4)`, which is below `1/2`
  once `b > (log2 C + 5)/20`.

**(d) Minor presentational note.** PROOF.md uses only `S > 2Ndigits - 2`,
that is `S ≥ 2Ndigits - 1`. When `S = 2Ndigits - 1`, the top digit of the
product can arrive as the carry left after the last coefficient. This happens
in 3 of the 8 toy products. The "sequential carry scan" must therefore flush
that final carry. It is at most one `b`-bit digit, because
`2n - b(2Ndigits - 1) ≤ b`. At the real parameters `S/T → 1`, so
`S ≥ 2Ndigits` eventually anyway. No bound or cost changes.

## Not covered

- PROOF.md's precision claim, an absolute error `< 2^-4p` for every complete
  source transform. Item 5c assumes it.
- Invertibility of `N` at `θ = Θ(p^-2)`. That is GAUSSIAN.md's row-gap
  estimate, still open; see #4217's open question 1 and #4304–#4309.
- Every cost: the chirp-table head travel, the synthetic-transform tariff, the
  Kronecker products and the CRT conversions (CRT.md).
- Prime existence, the tensor carve and halo, and the upstream Section 06/07
  equivalences.
- The finite checks corroborate the written proofs above. They do not replace
  them, and no proof-kernel check was run.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/pr4100-proof-composition-audit --check-only
python3.12 scripts/research_package.py --package research/pr4100-proof-composition-audit
python3.12 -B research/pr4100-proof-composition-audit/verify.py
```

The verifier prints `PASS_PR4100_PROOF_COMPOSITION_FINITE` with the counts
above. It takes about 9 seconds locally (macOS, CPython 3.12). It also checks
the SHA256 pins and 11 exact source phrases in PROOF.md and CRT.md.

## Open next questions

1. **Bind the `2^-4p` source-transform error to explicit constants.**
   - *Why it matters:* it is the one remaining premise of exact recovery
     (item 5c).
   - *First step:* list each factor's normalized amplification in GAUSSIAN.md
     and PROOF.md, then solve for an explicit `C`.
   - *Blocked by:* the all-size narrow row gap (#4217's open question 1).
2. **Lower the chirp odometer to a fixed-tape program.**
   - *Why it matters:* PROOF.md's `O(p)`-per-record head-travel bound is
     argued but not implemented.
   - *First step:* model the interleaved table and prefix-cache tapes, and
     check the `Σ j·t_min^(1-j)` sum against literal head moves on small
     radices.
   - *Blocked by:* nothing.

## Credit

The construction and every audited identity are Cinna Davis's #4100 (OpenAI
Codex assistance), with the upstream lineage retained in that package's
NOTICE.md. This independent audit and verifier were prepared by Ryanson
Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
