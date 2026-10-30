# Audit of #4100 COMPLEX.md: common cover, defect correction and stock arithmetic

**Audit with a positive scoped result; no new κ.** The selected κ is unchanged.

Pinned #4100 head: `337d04939571a637aeab54a0f58f54fde811663a`
(`research/unconditional-batched-crt/COMPLEX.md`). The provider words are the
literal PR4088 inputs `research/staged544-mixed-fourth-entry/inputs/{THREE,FOUR}-{base,extra}.json.gz`.

The #4311 coverage map lists "COMPLEX.md's arbitrary-f lift and complete-cover
execution" with no audit. Its free-word lift row, however, shows #4184
(ToikY) as positive: an exact formal cancellation on all four PR4088
programs. This package therefore audits the common-cover algebra: the cover
size, the terminal `X_delta` defect correction, the `H0` factorization and
the depth and row-stock arithmetic. It only cross-checks the lift, with
phase-carrying representations. The complex moment and root are already
certified by #4171 and are not redone.
The reading of the rank-r transition (one `C⊗rf` child versus f copies) is
#4375's subject and is not redone either.

## Results

| Statement in COMPLEX.md | Outcome |
|---|---|
| `Gamma = 2^1296 prod_{i=1}^{36}(2^(2i)-1) = |O(73,2)|` | Holds (proof below). Brute-force counts of `O(n,2)` for n = 1, 3, 5, 7 are 1, 6, 720, 1,451,520 = `|Sp(n-1,2)|` (n = 7 with `--full`, about 8 minutes). |
| `P_g C_all P_g^-1 = C_all X_delta`, `delta_i = (wt(row_i g)-1)/2 mod 2` | Holds for orthogonal g, with or without a translation (proof below). Checked on all of `O(3,2)` and `O(5,2)` and on 400 random elements of `O(73,2)` × 200 vectors each. It fails for non-orthogonal g, and `delta = 0` fails whenever `delta != 0`. |
| `H0 = ((1-i)/2) D C D`, tensor diagonals `i^wt`, `((1-i)/2)^h` split by parity | Holds exactly (Gaussian rationals), tensor powers h ≤ 6. `H0` is `[[1,1],[1,-1]]/2`. |
| `D(e) = 1 + D(48 floor(e/73))`; every child decreases D; two levels halve e | Holds (proof below; scanned for e ≤ 2·10^5, and ≤ 2·10^6 in the development run). |
| Row stock padded to `R = ceil(2^q/M) M`, `M = (W Gamma)^D(h)`, factor below two | Factor below two holds. **Presentational correction:** `R > 2^q` at every tested h (73 … 10^30), so the padded range needs `q+1` reserved bits (or a radix-R field), not `q`. Only a constant changes. |
| Each native warp is a monomial `i^a` matrix | Holds: all 720 warp edge classes of the four words (`native_warps.py`). |
| Arbitrary-f lift: each warp generator `G -> G⊗f`, each scalar kept as a scalar, constant monomial phase `i^a -> i^(fa)` | Already audited by #4184 (exact pullback, all 5,784 output functionals). The supplementary check below agrees: there are no complex scalars, and `i^a` monomial representations pass for f = 1, 2, 3. |

## Supplementary lift check (complements #4184)

#4184 proves the formal free-word cancellation exactly and specializes it
over F101 and the rationals. This section adds two things: the phase/scalar
separation that COMPLEX.md's `i^a -> i^(fa)` sentence relies on, and
execution with phase-carrying monomial generators.

**What the certificate is.** In PR4088's exact interpreter
(`vendor/audit_core.py`) a register value is a dict
`{(input, reduced word): Fraction}`. Warps are free generators, reduced only by
`g g^-1 = 1`. Every ADD, SCALE and correction coefficient is a rational. The
four words have 17,428–17,429 scalars each, all real dyadic rationals (about
9,040 negative), 72 warp generators and 36 initial corrections. The event kinds
are only add, scale and warp. So the certificate cancels in `Q[F_72]` and has
no complex phase coefficient at all. A phase `i^a` can only sit inside a warp
generator, and it is tensored with that generator to give `i^(fa)`, as
COMPLEX.md says. A sign or SCALE is a field coefficient and stays scalar.

**Why that suffices.** `w -> rho(w)^(⊗f)` is a group homomorphism of the free
group for any assignment `rho` of the generators. Extended linearly, it is an
algebra homomorphism of `Q[F_72]`, and every identity certified in `Q[F_72]`
survives. Corrections `c G_word x` stay separate terms, giving `G_word^(⊗f)`
and not `(G_word - I)^(⊗f)`. The dual orientation uses `D_k = K_k^(-T)`, and
`(K^(⊗f))^(-T) = (K^(-T))^(⊗f)`.

**Execution check.** `verify.py` executes each word end to end with its own
interpreter. The order is corrections, wrapper, A, cut, B with the warps,
restore and cleanup, read from the pinned format, with nothing imported. Each
generator becomes `M^(⊗f)` for a random 4×4 monomial matrix M with entries
`i^a`, for f = 1, 2, 3. Inputs and the 91 dirty private buffers are random
complex vectors. In all 24 runs (4 words × 3 widths × forward/dual), the
contract holds to relative error ≤ 1.7·10^-14:

- targets become `x_t + x_(t-V)` (forward), or sources `x_r - x_(r+V)` (dual);
- every other live register returns;
- every private buffer is restored, with no leakage.

**Controls** (`test_verify.py`). Reading every scalar sign as a phase symbol
breaks the lift. So does replacing each `G^-1` by an unrelated matrix.

## Proofs

**Cover size.** Let n be odd and `j` the all-one vector. For every x,
`x·x = Σx_i = j·x`. So an isometry g gives `j·(gx) = j·x`, i.e. `g^T j = j`.
Since `g^T` is also orthogonal, `g j = j`. Because `j·j = 1`,
`F_2^n = ⟨j⟩ ⊕ j^⊥`, and on `j^⊥` (the even-weight vectors) the form is
alternating and nondegenerate. Restriction is a bijection
`O(n,2) → Sp(n-1,2)`: it is injective since g fixes j, and surjective since
any symplectic map extended by `j ↦ j` is an isometry. At n = 73 this gives
`2^(36^2) prod(2^(2i)-1)`.

**Defect correction.** Entrywise, `C_all[x,y] = ((1+i)/2)^n (-i)^wt(x⊕y)`.
With `P_g|x⟩ = |gx⟩`, the identity is equivalent to
`wt(g^-1 z) ≡ wt(z ⊕ delta) (mod 4)` for all z. Since `g^-1 = g^T`, write
`g^-1 z = Σ_k z_k c_k` with `c_k` the rows of g. Then

    wt(g^-1 z) ≡ Σ_k z_k wt(c_k) - 2 Σ_{k<l} z_k z_l |c_k ∧ c_l|   (mod 4).

Orthogonality makes each overlap even and each `wt(c_k) = 1 + 2 delta_k`, so
`wt(g^-1 z) ≡ wt(z) + 2(delta·z)`. In the Hadamard picture
`C_all = H S H` with `S = diag(i^wt)` and H the unitary Walsh–Hadamard
transform, `H P_g H = P_(g^-T) = P_g`. So the conjugate is
`H S' H` with `S' = diag(i^wt(g^-1 y)) = S Z^delta`, and
`H S Z^delta H = C_all X^delta`. This proves the identity. Comparing the
`z = 0` entries of both sides then forces `wt(delta) ≡ 0 (mod 4)` for every
orthogonal g, which the check also observes on every sampled g. A translation `x → x+v` cancels in `x⊕y`.
Applying the identity on each of the f columns gives `X_delta` columnwise.

**Depth and stock.** `floor(e/73)` is nondecreasing, so D is nondecreasing by
induction. A child `r floor(e/73)` with `r ≤ 48` has
`D ≤ D(48 floor(e/73)) = D(e) - 1`. Two levels give at most
`(48/73)^2 e < e/2`. A node passes `R/(W Gamma)` rows to its children, which
is divisible by `(W Gamma)^(D-1)`, enough by monotonicity. Parked ancestor
volumes `V/(W Gamma)^k` form a geometric series. From
`M ≤ 2^q < 2M` we get `2^q ≤ R < 2^q + M ≤ 2^(q+1)`, with `R > 2^q` unless
M divides `2^q`. M is divisible by odd primes (for example
`2^2-1 = 3` divides Gamma), so that never happens for D ≥ 1.

**Height and time (given #4171).**
- `A(e) ≤ A(48f) + Sf + E` with `e ≥ 73f` gives `A(e) ≤ αe` once
  `α ≥ (S+E)/25` and α covers the leaves. #4178's incoming height `t0` is a
  separate reported defect and is not re-examined here.
- Internal nodes cost `O(V e^(1-a2) polylog p) ≤ O(V e^tau polylog p)`, since
  `a2 = 0.0017333948 > a_eff`.
- A leaf of width `l ≤ h^eta` costs `l = l^(1-b) l^b ≤ l^(1-b) h^(eta b)`
  per volume. The `(1-b)` moment then bounds the leaves by
  `O(V h^(1-b+eta b))`, and `(1-eta) b > q` gives the stated
  `O(V h^(1-q) polylog p)`.

## Native warps are Z4 monomials

`native_warps.py` (numpy) answers the native-realization question that #4184 left open. A warp
event of operator k, moving its lender from frame U to frame E, executes
`Z = T_E K_G^(±1) T_U^-1` on the lender's 9 hosted axes. Here `K_G` is the
phase-corrected permutation `|x⟩ → i^(q(Gx)) |Gx⟩`, with q the Z4 form of
`M = I + G^-T G^-1`, and `T_U = K_c (C on |U| axes) K_c^-1`. These
definitions are read from PR4088's `bw_gauss.py`; the script imports nothing
from it.

- **Binding.** Each canonical word (`evidence/{NATIVE,THREE}-CANONICAL-*`, where
  NATIVE is FOUR by its PHASES hash) matches its literal input word: the same
  72 warps by B position and G columns, and the same frame spans. Only the
  register labels are compacted.
- **Result.** All 180 warp edge classes of each of the four words, 720 in
  total, give a matrix with exactly one entry per row and column, each in
  `{1, i, -1, -i}`, global phase included. So every native warp is a monomial
  `i^a` matrix. Its `⊗f` lift is again monomial, with phase `i^(Σa)`, which is
  COMPLEX.md's `i^a → i^(fa)` statement. This independently re-derives
  PR4088's own `PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS` receipt.
- **Controls.** The plain permutation `P_G` without the quadratic phase is
  not monomial on any of 40 tested classes, and swapping the frames breaks 86
  classes. So the phase correction in `K_G` is essential.

## Not covered

- The composition of these local recipes into the global emitted program,
  which PR4088's PHASES receipts list as a separate obligation (see
  `TASK.json`).
- The rank-r child reading (#4375), and the physical gather/execute schedule
  and work-slot count of the cover.

## Validation

```sh
python3.12 -B research/complex-cover-lift-audit/verify.py
python3.12 -B research/complex-cover-lift-audit/test_verify.py
python3.12 -B research/complex-cover-lift-audit/native_warps.py   # numpy, about 2.5 min
python3.12 scripts/research_package.py --package research/complex-cover-lift-audit
```

The finite checks support the written proofs above; they do not replace them.

## Credit

The construction is by Cinna Davis (#4100, PR4088). The formal lift audit is
#4184 (ToikY). The exact free-word
interpreter whose format is read here is by Sagar Thakrar (in PR4088's
vendor). The coverage map is #4311 (Ryanson Jonathan), the complex moment
certificate is #4171 (petalas), and the rank-r reading is #4375 (unpaidmoon).
Prepared for Mark (Matarener) with substantial Claude Code assistance.
Apache-2.0.

## Open next questions

Does each PR4088 word's global emitted program compose its local frame,
centre and warp recipes into exactly the free-word shadow? First step:
regenerate LOCAL-PROGRAMS for one word and check that the frame labels between
consecutive events cancel exactly. See `TASK.json`.
