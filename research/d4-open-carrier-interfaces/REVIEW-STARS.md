# Independent review of the eight A/B star normalizers

**PASS for the eight fixed A/B ports and their stated tensor lifts.**
The written proof and executable source correctly complete the A/B
normalization obligation alongside the separate four C-port witnesses.
They do not establish a globally routed caller or a multiplication bound.

Reviewed source files in `carrier-normalizer/`:

| File | SHA256 |
|---|---|
| `check_stars.py` | `2f02cee8b75f630851f3a6c4ab3014c43e119bf54ee7f0036300bc9c02d7c88a` |
| `STAR-NORMALIZATION.md` | `146473d471b584095641a688c98b80cd335ff17320fb0d669e793b2fadf2fec3` |
| `STARS.json` | `d7a382016abfcf3a62ab13773cd1b09188c624c2b0e3bc93f53aeaac6e11008b` |
| `STAR-INVENTORY.json` | `15b7ca82057a47b75e36446727ab78d64d19bf5b593e37f58958ffae5a50fb73` |

This review separately reconstructed every row from the frozen geometry
and authenticated compiler already retained in `carrier-native/frozen/`.
It executed 12 exact signed-Pauli-plus-global-phase comparisons per port,
96 in total. Those comparisons covered the star involution, full-F
covariance, source normalization, logical kernel, both physical H cuts,
AB, BB, T², the ungauged phase correction, the corrected backward cross
and its Y diagonal. No frozen carrier file was modified.

## Exact phase and eight-row table

The phase argument is correct. For `w=q xor r`, orthonormality gives
nonzero isotropic w, and `R=I+w w^T` fixes p and swaps q,r. The character
eigenvalue of the actual positive-native F7 is `i^wt(x)`. Thus

```
wt(Rx)-wt(x) = 2 epsilon (w·x) modulo 4,
epsilon = wt(w)/2+1 modulo 2
```

implies `R F7 R^-1 = X_(epsilon w) F7` exactly. The zero-frequency
character fixes the constant scalar. The actual gauge then cancels
precisely when `w·33=epsilon`.

The independent reconstruction produced:

| Group | p | q | r | w | epsilon | R(33) | AB=BB mask | T² mask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 7 | 13 | 117 | 120 | 1 | 89 | 10 | 117 |
| A | 2 | 61 | 64 | 125 | 0 | 33 | 63 | 64 |
| A | 50 | 8 | 69 | 77 | 1 | 108 | 58 | 69 |
| A | 55 | 56 | 112 | 72 | 0 | 33 | 15 | 112 |
| B | 13 | 117 | 7 | 114 | 1 | 83 | 120 | 7 |
| B | 61 | 64 | 2 | 66 | 0 | 33 | 125 | 2 |
| B | 8 | 69 | 50 | 119 | 0 | 33 | 77 | 50 |
| B | 56 | 112 | 55 | 71 | 1 | 102 | 72 | 55 |

This agrees with the proof's complete eight-row table. The correction is
nontrivial at exactly four ports. The source correctly limits the
ungauged-F rejection control to those four ports; it does not assert that
the other four fail.

## Operator order and both physical cuts

For the actual OPEN A/B source boundary
`S=F C_r^-1 C_p^-1`, exact covariance gives `R S R=T`.
Taking `P=post=R` yields physical
`K=T^-1 J R=C_q C_p^-1 R`, while the logical kernel is
`A=C_q^-1 K C_p=R`. The independent ranks are
`(r(S),r(T),r(K),r(A))=(5,5,2,0)` at every row.
The source now explicitly states and tests that physical K is not an
involution. It does not replace K^-1 by K because logical A is involutive.

Since `H=A^-1=R`, conjugation into the actual entrance C_p and the actual
target return frame `F C_p^-1` gives R at both cuts. Therefore the
companion's pre-X/post-Y common-code identity applies in both normalized
orientations. No commutation of different ports' R operators is assumed.

The ordered backward corrections are correct:

```
AB=T K^-1 T^-1 K^-1 = X_(p xor q),
BB=T AB^-1 T^-1 = X_(p xor q),
T²=X_(127 xor p xor q).
```

In particular `TK=F X_p R` and exact full-F covariance imply
`(TK)²=X_127`. This verifies the proof's alternative BB derivation.
Direct multiplication gives
`T² K T^-1 AB=T K^-1` and `BB T AB=T`.
The two T² maps, AB and BB must all remain paid.
Consistently exchanging bank operands compiles the conjugated inverse
word; any required physical routing belongs to the caller and is not
silently supplied by this local argument.

## Literal cost and finite-check scope

Every added wrapper is a phase-free address involution. In one base
chart R has 64 fixed addresses and 32 two-cycles. A nonzero translation
has 64 two-cycles. Across f independent bit positions, the fixed space
of R has dimension 6f, so its cycle count is
`(2^(7f)-2^(6f))/2`; a nonzero lifted translation has `2^(7f-1)`
two-cycles. Enumerating addresses once and swapping only the smaller
endpoint executes each two-cycle exactly once.

The proof's unfused invoices are therefore correct: four R maps for the
forward common-code spelling, and four R maps plus four translations for
the backward spelling. These are 128 and 384 base coordinate swaps per
port. Each swap is charged three signed complex ADDs and one NEG.
The one-sum intermediate has the stated extra magnitude-bit bound in
exact arithmetic; this is not a whole native or rounded-network
precision theorem. Address calculation, counters and the carrier's
existing native and monomial-adapter charges remain separate.

The source authenticates its geometry and compiler, executes the same
captured compiler bytes, retains its assertions under outer `-O`,
reconstructs all eight R matrices, and verifies complete signed Pauli
data plus exact phase. Its 1024 character checks cover all 128
characters at each port. Its 8192 address checks concern 64 lowered
monomial recipes, as stated, rather than an independent execution of
every full native history at every input.

The reviewed source requires 36 control outcomes: 28 rejected
mutations and eight actual phase-guard deletions. It uses the production
equality predicate, matches its intended error names, and leaves
unexpected acceptance outside the catch. This review inspected that
source and independently checked the mathematical identities. It also
read the owner's final normal and optimized output files and confirmed
that both are byte-identical to the frozen `STARS.json` named above,
with all 36 control records and the matching final checker hash. Those
complete checker runs are the owner's execution evidence; the separate
96-identity probe described above is this reviewer's execution evidence.

No mathematical correction remains requested. Preserve the fixed-port,
exact-phase, paid-wrapper and caller-routing boundaries when integrating
this addendum with the native carrier and four C-port package.
