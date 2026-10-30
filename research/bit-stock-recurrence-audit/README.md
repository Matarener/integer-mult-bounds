# Audit of #4100 BIT.md: local-ring algebra, row stock, depth, recurrence and wrapper

**Audit with a positive scoped result; no new κ.** The selected κ is unchanged.

Pinned #4100 head: `337d04939571a637aeab54a0f58f54fde811663a`
(`research/unconditional-batched-crt/BIT.md`).

The #4311 coverage map lists BIT.md's "row stock, whole high packets and fixed
tapes" and "weighted leaves and fast header routes" with no #4100-specific
audit. This package checks every finite or algebraic statement in BIT.md
§1–§4. The moments `mu_1`, `mu_(1-c)` and the body word are #4330's and are
used, not re-certified.

## Results

| Statement in BIT.md | Outcome |
|---|---|
| §1: `q = 2^89-1` prime; `2·64^3/q < 10^-16` | Holds. Primality is confirmed by Lucas–Lehmer, independently of #4100's Pratt certificate. The bound is 8.5·10^-22. |
| §1: `N(P) = [[I-P,PC],[CP,I-CPC]]` gives `N(P)^2 = I`; disjoint commuting projectors add; nested differences multiply; conjugation by `diag(A,I)` keeps these; split rank over `Z/q^w` | Holds when C is an involution, as NORMAL-FORM.md's coordinate reversal is (proof below). Checked exactly on 150 instances over `Z/3`, `Z/27`, `Z/25`, `Z/49` and `Z/961`, with C the reversal or a random involution. The rank of P mod q equals its split rank. |
| §2: `K(w) = 269241600 N q^(4096(w-1))`, and splitting family, low matrix and high matrix leaves `U = 9475 t K^(D-1)` | Holds exactly, with `269241600 = W·9475` and `N q^(4096(w-1)) = |GL_64(Z/q^w)|`. The order formula is proved below and brute-forced on small rings. Exact big-integer division (N has 364,544 bits) gives U, and every child's stock divides it, for w = 1, 2 and D = 1..3. |
| §2: D monotone; every child `r floor(n/64)`, r ≤ 42, drops D; two coarse levels halve; `h ≤ 2 log2 e + O(1)` | Holds (proof below). Scanned for n ≤ 3·10^5 (3·10^6 in the development run); `max(D − 2 log2 n) = −11`. |
| §3: header routes come from the low-digit carry plus an ordered high-field addition; doubling and halving are a two-piece split/interleave | Holds: the identity `xA = (x_lo A_lo mod q) + q(carry + x_lo A_hi + x_hi A)` is checked over `Z/q^w` on 800 cases, and doubling maps `[0,(M+1)/2)` onto the evens and the rest onto the odds. |
| §3: `F = 32·64^2·ΣH = 118606528512`; the fallback's at most 49,911 children fit `32·64^2` | Holds. |
| §3: the recurrence gives `T ≤ C/(1-mu_1) n + C/(1-mu_t) n^t w^(1-a)` | The induction is correct (below). The equality recursion stays below the envelope for a ∈ {0, a1}, w ∈ {1, 10, 10^6} and n up to 10^9, and it is monotone, which the `max_(j≤f)` step needs. |
| §4: `k = O_q(w log(e+1)) = o(e)`; elementary fallback only at finitely many widths | Holds. With the literal constants, `2k < e` and `n ≥ 64` first hold at `e = 2^19` (k ≈ 1.6·10^5) and keep holding up to `2^400`. |
| §4: stage cost `O(V e^(1-c+c^2-ca))`, `a_next = c(1-c)+ca`, reaching `a2` | Holds exactly. Every cost term (`n`, `n^(1-c) w^(1-a)`, `k`, `w`) is dominated because `a ≤ c`. |

**Minor wording.** §2 says each child's payload has volume `V/(WN)`. The split
also divides by the high-matrix fibre `q^(4096(w-1))`, so the payload is
`V/(W N q^(4096(w-1)))`. It is smaller, so the geometric-series step holds a
fortiori.

## Proofs

**`N(P)` identities.** Let `C^2 = I`.
- For an idempotent P, the top-left block of `N(P)^2` is
  `(I-P)^2 + PC·CP = I - P + P = I`. The top-right block is
  `(I-P)PC + PC(I-CPC) = PC - P^2C = 0`, and the other two blocks are
  symmetric.
- For idempotents with `P1 P2 = P2 P1 = 0`, multiplying `N(P1) N(P2)`
  block by block gives `N(P1+P2)`, because every cross term carries
  `P1 P2` or `P2 P1`.
- For `Q = PQ = QP`, the same expansion gives `N(P) N(Q) = N(P-Q)`.
- Conjugation by `diag(A,I)` is an algebra automorphism, so it keeps all
  three identities.
- Over the local ring `Z/q^w`, an idempotent's image is free with rank equal
  to its rank mod q (idempotents lift uniquely). The characteristic
  polynomial is `x^(n-r) (x-1)^r`.

The controls in `test_verify.py` show that `N(P)^2 = I` fails for a
non-involution C, and that additivity fails for overlapping projectors.

**`|GL_n(Z/q^w)|`.** Reduction mod q is surjective onto `GL_n(F_q)`. Its
kernel is `{I + qM}`, which has `q^(n^2 (w-1))` elements, because every such
matrix is a unit. So `K(w)/269241600 = |GL_64(Z/q^w)|`, and dividing
`R = t K^D` by `W·|GL_64(Z/q^w)|` leaves `9475 t K^(D-1)`.

**Depth.** `floor(n/64)` is nondecreasing, so D is nondecreasing. A child
`r floor(n/64)` with `r ≤ 42` has `D ≤ D(42 floor(n/64)) = D(n)-1`. Two levels
multiply the width by at most `(42/64)^2 < 1/2`, so
`D(n) ≤ 2 log2 n + O(1)`.

**Recurrence.** Put `A = C/(1-mu_1)` and `B = C/(1-mu_t)`, where
`mu_x = (Σ_r H_r (r/64)^x + η F (1/64)^x)/W`. Since `rf ≤ rn/64`, the
children contribute at most `mu_1 A n + mu_t B n^t w^(1-a)`. The `max_(j≤f)`
term is bounded by the envelope at f, which is monotone. The local toll
`C(n + w^(1-a))` is absorbed because `A(1-mu_1) = C` and
`B(1-mu_t) n^t ≥ C`. Leaves need `B ≥ C`.

**Wrapper exponents.** With `w = e^c` and `n ≈ e^(1-c)`, the term
`n^(1-c) w^(1-a)` gives `e^(1-c+c^2-ca)`. The other terms have exponents
`1-c` and `c`, both at most that, because `a ≤ c`. The identity
`(1-c)^2 + c(1-a) = 1 - a_next` gives `a1 = c(1-c)` and
`a2 = c(1-c^2)`.

## Not covered

- The PR2809 block construction itself: the encoded continuation stack,
  stream serialization, capsule copying and restoration.
- The finite word certificate and owner data, which `evidence/bit-local-ring-current.log` replays.
- The Schwartz–Zippel density step, which #4227/#4228 audit.

These are prose constructions or are audited elsewhere.

## Validation

```sh
python3.12 -B research/bit-stock-recurrence-audit/verify.py
python3.12 -B research/bit-stock-recurrence-audit/test_verify.py
python3.12 scripts/research_package.py --package research/bit-stock-recurrence-audit
```

The finite checks support the written proofs; they do not replace them.

## Credit

The construction is by Cinna Davis (#4100). The moment certificate is #4330
(pinterbanget), and the coverage map is #4311 (Ryanson Jonathan). Prepared for
Mark (Matarener) with substantial Claude Code assistance. Apache-2.0.

## Open next questions

Does the PR2809 block construction's encoded stack keep the claimed `O_q(V)`
visited space when the continuation is serialized at every recursive cut, at
the new c? First step: bound the parked bytes per ancestor level against
`V/(W N q^(4096(w-1)))^level`. See `TASK.json`.
