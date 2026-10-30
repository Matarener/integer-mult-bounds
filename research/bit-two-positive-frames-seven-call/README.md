# Two added positive frames cannot give a seven-call word

This package answers open question 1 of JoyboyBrian's
[handoff #6104](https://github.com/CrocSwap/integer-mult-bounds/discussions/6104),
which is also apoursh's two-frame question in
[PR #6089](https://github.com/CrocSwap/integer-mult-bounds/pull/6089). Add two
nonzero positive rational rank-one addresses `R` and `S` to the PR2085/2112
four-target alphabet. Then **no exact word of at most seven calls uses both
of them**. This holds for every direction and scale of `R` and `S`, every
finite restored dirty width and any free binary mixing.

The proof uses only necessary conditions: the determinant identity, the four
target-support systems, and first-order character rank on the exact address
lattice. It needs no word census. A stdlib verifier enumerates every count
profile, settles the pinned splits exactly, and checks the uniform lemma for
the seven continuous families on a direction grid. No new κ, supplier or
native saving is claimed.

## Model

As in PR6089 and the handoff, put

```text
A = [[1,0],[0,0]]   B = [[0,0],[0,1]]
P = (1/2)[[1,1],[1,1]]   Q = (1/2)[[1,-1],[-1,1]]     (A+B = P+Q = I)
```

Let `R`, `S` be nonzero positive semidefinite rational symmetric rank-one
matrices. They may coincide with each other or with an old address. Let
`Lambda = ZA + ZB + ZP + ZR + ZS`, which has rank three. Work in
`F2[Lambda]`. A paid call is `I_w + ([F]-1)N` with `F in {A,B,P,Q,R,S}` and
`N` a binary rank-one idempotent on any finite width `w >= 4`. Free
address-independent `GL_w(F2)` maps cost nothing. The endpoint is

```text
T_w = diag([A+P], [A+Q], [B+P], [B+Q], 1, ..., 1)
```

with every extra role restored. Write `a,b,p,q,r,s` for the label counts. The
question requires `r, s >= 1` and `a+b+p+q+r+s <= 7`, so `n = a+b+p+q <= 5`.

## Theorem

For every finite `w >= 4` and every such `R, S`, no exact word with at most
seven paid calls has `r >= 1` and `s >= 1`.

Combined with PR6089's single-frame theorem (an `R`-using word has at least
`m+7 >= 8` calls) and the known eight-call floor for `{A,B,P,Q}`, this means
no word with at most two added positive frames beats eight calls. That
combined statement inherits PR6089's review status. PR6089 is pending and is
not re-verified here.

## Proof

**Step 1 (determinant; Nick Petalas, PR2910).** `det(I+([F]-1)xy^T) = [F]`,
free maps have determinant 1, and `det T_w = [4I]`. So

```text
rR + sS = M := 4I - aA - bB - pP - qQ.
```

Since `R` and `S` are positive and nonzero, `M` is positive semidefinite and
nonzero. Write `X = rR`, so that `S = (M-X)/s`. Both `X` and `M-X` must be
positive rank one. Of the profiles with `r,s >= 1` and `n+r+s <= 7`, 442 have
positive semidefinite nonzero `M`.

**Step 2 (support).** Conjugate the free maps to the end. By augmentation the
last free map is the identity (PR6089 §1). Expand each factor as
`(I+N) + [F]N`. The coefficient of `[H]` in a diagonal entry is a sum over
subsets of calls whose labels sum to `H`. So for each target exponent
`H_j`, there are integers `0 <= u_F <= count(F)` with
`sum_F u_F F = H_j`. With `alpha = u_R/r - u_S/s` and `beta = u_S/s`, this
reads

```text
alpha X = H_j - (u_A A + u_B B + u_P P + u_Q Q) - beta M =: K.
```

There are two cases:

- If `alpha = 0`, the solution holds for every split exactly when `K = 0`.
  Call that solution *free*.
- If `alpha != 0`, it forces `X = K/alpha`. This counts only when `X` and
  `M-X` are positive rank one.

A target with no free solution confines `X` to a finite set. Exactly seven
profiles have a free solution for all four targets:
`(1,1,1,1,1,1)`, `(1,1,1,1,1,2)`, `(1,1,1,1,2,1)`, `(2,1,1,1,1,1)`,
`(1,2,1,1,1,1)`, `(1,1,2,1,1,1)` and `(1,1,1,2,1,1)`. All seven use the
old-only support, which is unique: for `A+P` it is `u_A = u_P = 1` and the
rest zero, and similarly for the other targets. The enumeration finds no
balanced free support (`alpha = 0`, `beta > 0`) at seven calls. In every other
profile, the four finite sets intersect in 32 splits in total. Every one of
them has `R` and `S` proportional to old addresses, for example
`(0,1,1,1,1,3)` with `R = 2B` and `S = A`.

**Step 3 (characters; method from PR6089 and the handoff).** An additive
`chi: Lambda -> F2` induces the ring map `[F] -> 1 + chi(F) eps` into
`F2[eps]/(eps^2)`. Exactness gives
`sum_{i: chi(F_i)=1} N_i = diag(chi(H_1),...,chi(H_4),0,...)`. Hence the
number of detected calls is at least the number of targets with
`chi(H_j) = 1`. For each of the 32 pinned splits, the verifier computes an
integer basis of the actual `Lambda` and tests all eight characters. Each
split fails for some character, with 2 detected calls against 4 targets.

**Step 4 (the seven continuous families).** Let
`L = Z_(2)A + Z_(2)B + Z_(2)P`, the old lattice with odd denominators
allowed. Its coordinates are `(alpha, beta, gamma) = (m11-m12, m22-m12, 2m12)`.
If `R, S` lie in `L`, then two functionals restrict to characters of
`Lambda`:

```text
chi_PQ = gamma mod 2      (A,B -> 0; P,Q -> 1; all four targets -> 1)
chi_AB = alpha+beta mod 2 (A,B -> 1; P,Q -> 0; all four targets -> 1)
```

If such a character also kills `R` and `S`, it detects exactly two calls in
every family (`p+q = 2` or `a+b = 2` respectively) against four targets. That
is a contradiction. Write the split direction as a primitive integer vector
`(x,y)` and `pi = (x^2, y^2, xy)/h` with `h = x^2+y^2`.

- *`M = 2I`: profiles `(1,1,1,1,r,s)`, `(r,s)` in `{(1,1),(1,2),(2,1)}`.*
  Here `det(2I - t vv^T) = 0` forces `X = 2 pi_u` and `M - X = 2 pi_{u⊥}`.
  So `{R,S}` is `{2pi_u, 2pi_{u⊥}}`, `{2pi_u, pi_{u⊥}}` or `{pi_u, 2pi_{u⊥}}`.
  - If `x` and `y` have opposite parity, `h` is odd. Then `pi_u` and `pi_{u⊥}`
    have 2-integral entries and lie in `L`. Their `gamma = ±2xy/h` is even, so
    `chi_PQ` kills all four matrices.
  - If `x` and `y` are both odd, then `h = 2k` with `k` odd. Now
    `2pi_u = (x^2,y^2,xy)/k` lies in `L` with `alpha+beta = (x-y)^2/k`, which
    is divisible by 4. Also `pi_{u⊥} = (y^2,x^2,-xy)/(2k)` has
    `alpha = y(y+x)/(2k)`, `beta = x(x+y)/(2k)` and `gamma = -xy/k`, so it
    lies in `L` with `alpha+beta = (x+y)^2/(2k)`, which is even. The
    `u <-> u⊥` swap covers the remaining two matrices. So `chi_AB` kills them.

  This extends the handoff's `M = 2I` argument to `r` or `s` equal to 2, where
  `R` or `S` is no longer in `2L`.
- *`M = diag(1,2)`: profile `(2,1,1,1,1,1)`.* The matrix determinant lemma
  forces `X = 2uu^T/(2x^2+y^2)`, with `R = X` and `S = M - X`.
  - If `y` is odd, the denominator is odd, `X` lies in `L`, and
    `gamma = 4xy/(2x^2+y^2)` is even.
  - If `y = 2y1`, then `x` is odd and `X = (x^2, 4y1^2, 2xy1)/k` with `k`
    odd. So `X` lies in `L` and `gamma = 4xy1/k` is even.

  Since `M = A + 2B` has `chi_PQ(M) = 0`, `chi_PQ` kills `R` and `S`.
- *The other three doubled profiles.* They are images of `(2,1,1,1,1,1)` under
  PR6089 §3's symmetries. Conjugation by `J` fixes `chi_PQ`. Conjugation by
  `H` permutes `A,B,P,Q`, preserves `L`, and exchanges `chi_PQ` with
  `chi_AB`. So `(1,2,1,1,1,1)` uses `chi_PQ`, and `(1,1,2,1,1,1)` and
  `(1,1,1,2,1,1)` use `chi_AB`. The verifier checks all four doubled
  profiles directly, without using the symmetry.

Every profile is now excluded. QED

## Evidence

`verify.py` uses only the stdlib and exact `Fraction` arithmetic. It imports
no repository module or predecessor executable. It checks the following:

- the live source hash;
- all 442 positive semidefinite residual profiles of length at most seven;
- the support classification: exactly the seven free families and 32 pinned
  splits;
- an exact-lattice integer basis and all eight characters for every pinned
  split;
- for each free family and every primitive direction with
  `|x|, y <= 30`, 7,784 cases in all:
  - the parameterization;
  - membership in `L`;
  - the lemma's character kills `R` and `S`, with 2 detected calls against 4
    targets;
  - an independent exact-lattice check that agrees.

These grid cases are regression checks; the uniform claim rests on Step 4.

As an independent route that bypasses the `alpha`/`K` classification, the
verifier also picks 46,916 concrete splits over all 442 profiles. It uses
primitive directions up to height 8 for definite `M` and rational scales
`k/m`, `m <= 40`, for rank-one `M`. It tests literal subset sums for all four
targets: 648 pass, and the exact-lattice characters kill every one of them.
The verifier also runs these controls:

- *Positive control.* At eight calls, real words survive every filter: 77
  survivors, including `R = S = A` at `(0,2,2,2,1,1)` and the free
  `(1,1,2,2,1,1)`. One literal eight-call word, with `R = A` and `S = B`
  relabelled, is multiplied out in `F2[Lambda]` and equals the endpoint.
- *Negative controls.* Without the support step, 28 seven-call profiles
  survive the characters at the split `u = (1,0)`. Naive mod-2 reduction of
  `1/2` is rejected. A mutated target changes the free-family list.

Runtime is about 30 s per command.

## Reproduce

```sh
python3.12 -I -W error -B research/bit-two-positive-frames-seven-call/verify.py
python3.12 -I -O -W error -B research/bit-two-positive-frames-seven-call/verify.py
```

## Limits

- This is a formal-model lower bound. It provides no native operation,
  tariff, supplier or κ change, and makes no all-field claim.
- Only at most two added positive rank-one frames are covered. Three or more
  frames, negative or indefinite frames, and higher-rank added addresses are
  not covered.
- The combined "nothing beats eight" corollary depends on the pending PR6089
  and is not independently re-verified here.
- The grid checks are regression evidence, not the proof of Step 4.

## Open next questions

1. **Three or more added positive frames.** With `k` frames, the residual
   becomes a `k`-term positive rank-one decomposition of `M`. That gives
   `k-1` continuous parameters. Relevance: this would close the "more
   positive frames" route for this endpoint at seven calls. First step:
   repeat Step 2 with `alpha` replaced by a linear form in the `k` split
   matrices. Check whether the free families still need
   `a, b, p, q >= 1`, which leaves at most `7-4 = 3` added calls. Blocker:
   the 2-local membership of a general decomposition is not automatic.
2. **Eight-call words using two frames.** The eight-call survivors include
   new non-duplicate candidates, for example `(1,3,0,1,1,2)` with `R = 2A`
   and `S = P/2`. Decide which are realizable, as in PR6089's `{m+7, 2m+6}`
   spectrum. Relevance: this is the complete length spectrum, not a cheaper
   word. First step: try subdivision words.
3. **Non-positive added frames.** The positivity of `M` is what makes the
   finite residual list. Indefinite rank-one frames remove it. A different
   bound on the residual is needed first.

## Credit

- JoyboyBrian (#6104): the two-frame question, the residual
  parameterization, and the `M = 2I`, `r = s = 1` character argument
  extended here.
- apoursh (PR6089): the one-frame classification, the reduction to paid-only
  words, and the symmetries.
- Nick Petalas (PR2910): the determinant method.
- Cinna Davis (PR2085/2112): the model and endpoint.
- Philippe Van Velzen: the eight-call floor.
- The retained BIT lineage credited in those sources.

New material prepared for JosieElliston by Claude Opus 5.5 via Claude Code,
Apache-2.0. Substantial AI assistance. There is no human or proof-kernel
acceptance.
