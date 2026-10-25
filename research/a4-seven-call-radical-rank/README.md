# The four-output A4 target has exact minimum eight: no seven-call word

**Scoped exact closure in a formal model; no new `kappa`.** In the formal
`F2[A4]` four-role model of [PR #2116](https://github.com/CrocSwap/integer-mult-bounds/pull/2116),
every word realizing `T = diag([a],[b],[c],[d])` uses at least three `a`-calls
and at least three `b`-calls, and the numbers of `a`- and `b`-calls agree
modulo 3. A written proof therefore excludes length 7 and every length up to 5.
Length 6 would need exactly three calls of each label. Two exhaustive joins,
implemented separately in the same session, exclude every word of length up
to 7, including that case. Together with the direct eight-call word, this gives an **exact minimum
of 8**. The model has no cross-role paid-call saving for this target.

| Length | Status | Evidence |
|---|---|---|
| 1-5 | impossible | written proof (Lemmas 1-2); also both joins |
| 6 | impossible | exhaustive joins A and B (reproduces #2116); not covered by the written lemmas |
| 7 | impossible | written proof (Lemmas 1-2); also both exhaustive joins |
| 8 | realized | direct word (`a`, `b`, `abba`, `ab` on roles 1-4), replayed exactly on all 48 basis inputs |

The evidence has three different kinds. For length 7 and lengths up to 5 it is
a proof of impossibility. For length 6 it is a finite exhaustive certificate.
For length 8 it is an explicit construction. None of these is a multiplication
theorem, a supplier result or a `kappa` change.

**New here: a per-label radical-rank floor over `F2[A4]`.** Steps 1-5 below use
nothing specific to `T` beyond its lift modulo the radical `J` and the
resulting defect. So, in this alphabet with any number `r` of roles, every word equal to a target
`T in GL_r(F2[A4])` has `n_b >= rank_F4 Phi(L^-1 T - I)`, where `L` is the unique
lift of `T mod J` into `GL_r(F2[<a>])`; symmetrically for `n_a` with base `b`.
The verifier checks this floor (at `r = 4`) on random words and on two targets:
rank 3 for `T`, rank 2 for the three-output control. Whether it extends beyond
`A4 = V x| C3` is open question 2.

## Model

The model is unchanged from #2116. Take `a=(123)`, `b=(124)`,
`c=aba^-1b^-1=(12)(34)`, `d=ab=(13)(24)` and `e=ba=(14)(23)` in `A4`, composing
as `(pq)(t)=p(q(t))`. Then `V = {1,c,d,e}` is the normal Klein subgroup. A paid
call is

```text
D_N(g) = I + ([g]+[1]) N,   g in {a,b},   N = x y^T in M4(F2),   x,y != 0,   y^T x = 1.
```

There are 120 rank-one idempotents `N`, so the alphabet has 240 factors.
Factor `120*gi + n` uses label `a` (`gi=0`) or `b` (`gi=1`). It also uses the
`n`-th pair `(x,y)`, ordered by `x` and then by `y`. This is the ordering of
#2116, so its direct word is `[0,128,24,144,144,24,56,176]`. A word realizes `T`
when the 4x4 product over `F2[A4]` equals `T` in every formal coefficient. The
model has four roles, allows arbitrary dirty inputs and has no workspace. Each
call costs one, and no helper, copy or restoration operation is charged.

Free scalar mixing does not change the answer. Suppose free matrices
`G_i in GL4(F2)`, including role permutations, may be interleaved with the
paid calls. Conjugate each one to the left: `G^-1 D_N(g) G = D_{G^-1 N G}(g)`
is again a paid factor, so `W = H * W'` with `W'` a pure paid word of the same
length and `H in GL4(F2)`. Entrywise augmentation gives `aug(D_N(g)) = I` and
`aug(T) = I`, so `H = I`. The search over pure paid words is therefore complete.

## Proof

Write `n_a` and `n_b` for the numbers of `a`- and `b`-calls in a word.

**Lemma 1 (C3 determinant; the screen named in #2116).** Map `F2[A4]` to the
commutative ring `F2[A4/V] = F2[t]/(t^3-1)`, with `a -> t` and `b -> t^2`.
The matrix determinant lemma gives `det D_N(g) = 1 + (g+1) y^T x = g`.
So a word has determinant `t^(n_a - n_b)`. The target has determinant
`t * t^2 * 1 * 1 = 1`. The elements `1,t,t^2` are distinct, so
`n_a = n_b (mod 3)`.

**Lemma 2 (radical rank).** Every word equal to `T` has `n_b >= 3`, and
symmetrically `n_a >= 3`.

*Setup.* Let `J` be the kernel of `F2[A4] -> F2[A4/V]`. This is the Jacobson
radical. It has dimension 9 and `J = sum_i a^i I_V`, where `I_V` is the
augmentation ideal of `F2[V]`. Also `J^2 = sum_i a^i I_V^2`, and
`I_V^2 = F2 * sum_{v in V} [v]`. Put `S = F2[<a>] = span{1,a,a^2}`. Then
`S` meets `J` only in `0`, so `S` maps isomorphically onto `F2[A4]/J`. Write
`eps_v = [v]+[1]`, which lies in `J`.

1. *Splitting the b-calls.* For a fixed idempotent `N`,
   `D_N(g) D_N(h) = D_N(gh)`. Since `b = a^2 d`, this gives
   `D_N(b) = D_N(a^2) D_N(d)` and `D_N(d) = I + eps_d N`. Each call is therefore
   `F_k = B_k E_k`. Here `B_k` is `D_{N_k}(a)` or `D_{N_k}(a^2)` in `GL4(S)`.
   The factor `E_k` is `I` for an `a`-call and `I + eps_d N_k` for a `b`-call.
2. *Moving radical parts right.* Put `C_k = B_{k+1}...B_L` and
   `A = B_1...B_L`, which lies in `GL4(S)`. Then
   `W = A * prod_k (I + X_k)`. The product runs over the `b`-calls in order,
   with `X_k = C_k^-1 eps_d N_k C_k` in `M4(J)`.
3. *The lift.* If `W = T`, then `A = T (mod J)`. Since `S` meets `J` only in
   `0`, the lift is unique: `A = diag(a, a^2, 1, 1)`. Hence
   `U := A^-1 T = diag(1, a^-2 b, c, d) = diag(1, d, c, d)`.
4. *A twisted functional.* Let `mu: V -> F4` be given by `mu(1)=0`, `mu(c)=1`,
   `mu(a^-1 c a)=w` and `mu(a^-2 c a^2)=w^2`, where `w^2+w+1=0`. Because
   `1+w+w^2=0`, the map `mu` is `F2`-linear on `V = F2^2`. It is injective and
   satisfies `mu(a^-1 v a) = w mu(v)`. Define the linear map
   `Phi(sum beta_{i,v} [a^i v]) = sum beta_{i,v} mu(v)` from `F2[A4]` to `F4`.
   For `y` in `J` and `r,s` in `S`, we have
   `Phi(r y s) = aug(r) Phi(y) psi(s)`, where `aug(a)=1` and `psi(a)=w`. The
   reason is `a^i (a^m eps_v) a^j = a^(i+m+j) eps_(a^-j v a^j)`. Also
   `Phi(J^2) = 0`, because `sum_v mu(v) = 0`.
5. *Counting rank.* Modulo `M4(J^2)` we have
   `prod (I+X_k) = I + sum X_k`. Apply `Phi` entrywise, and note that `aug`
   is a ring map `M4(S) -> M4(F2)`. This gives

   ```text
   sum_{b-calls k} aug(C_k)^-1 (mu(d) N_k) psi(C_k)  =  Phi(U - I)  =  diag(0, mu(d), mu(c), mu(d)).
   ```

   Over `F4`, the left side is a sum of `n_b` matrices of rank at most 1. The
   right side has rank 3 because `mu` is injective. So `n_b >= 3`.

The same steps with base `b` start from `a = b^2 e`. The lift is
`diag(b^2, b, 1, 1)` and the defect is `U = diag(e, 1, c, d)`, again of rank
3, so `n_a >= 3`.

**Theorem.** Every word realizing `T` has `n_a, n_b >= 3` and
`n_a = n_b (mod 3)`. So its length is 6, with `(n_a,n_b)=(3,3)`, or at least 8.
At length 7, Lemma 1 allows only `(2,5)` and `(5,2)`, and Lemma 2 rules out
both. The exhaustive joins below exclude length 6, and the direct word has
length 8. The exact minimum is 8.

Lemmas 1-2 explain why no one-call saving (length 7) exists; length 6 is
excluded only by exhaustive search. Each role whose label is not a power of the
base generator contributes one independent rank unit through its
`V`-component: roles 2, 3 and 4 in base `a`, roles 1, 3 and 4 in base `b`.
Every call of the other label can pay at most one unit of that rank, after any
conjugation by the semisimple part. The C3 determinant then rules out the
unbalanced splits `(2,5)` and `(5,2)`.

The written exclusion of length 7 and of lengths up to 5 also holds with any
number of additional dirty roles whose target is `1`: the defect becomes
`diag(1,d,c,d,1,...,1)`, still of rank 3, and the target determinant is still
1. Length 6 is certified only for four roles.

## Separately implemented exhaustive joins

Both programs build `P<=3`, the distinct products of length at most 3 (the C
output and #2116 call this set `S3`; it is unrelated to the ring `S` above). They
deduplicate by the full 4x4 state of 12-bit coefficients and keep each state's
minimal length. Any word of length at most 6 is `X Y` with `X` and `Y` in `P<=3`.
A word of length 7 is `X f Y`, where `X` can be taken to have minimal length
exactly 3; otherwise a shorter word would exist. So each join tests
`X^-1 T in P<=3` for every `X`, and tests `f^-1 X^-1 T in P<=3` for every
minimal-length-3 class `X` and every factor `f`. That covers all lengths
through 7.

| | Join A (`join_a.c`) | Join B (`join_b.c`) |
|---|---|---|
| state representation | 4x4 matrix of 12-bit masks over `A4` | 12 coefficient matrices `M_g` in `M4(F2)`, 16 bits each |
| group construction | all even permutations | closure of `<a,b>` on packed codes |
| `P<=3` built by | right multiplication | left multiplication |
| enumerated end | left: `X^-1 T`, then `D_f^-1 (X^-1 T)` | right: `T Y^-1`, then `(T Y^-1) D_f^-1` |
| hash | `GF(2)`-linear (child hashes by XOR) | nonlinear multiply-xorshift |
| distinct `P<=3` states by minimal length | 1, 240, 41,920, 6,655,830 (total 6,697,991) | identical |
| minimal-length-3 classes expanded | 6,655,830 | 6,655,830 |
| children looked up | 1,597,399,200 | 1,597,399,200 |
| words of length at most 7 found | none | none |
| local wall time / peak RSS (2 threads, `-march=native` development build) | 27 s / 369 MB | 39 s / 316 MB |

The `P<=3` total, 6,697,991, matches #2116's `right_distinct_exact_states`. The
verifier reads that value from the pinned predecessor `RESULT.json`. Every
reported hit is confirmed in C, by comparing full states and multiplying out
the word. Python then replays it independently. The Python code does not reuse
#2116's `search.cpp` or its verifier.

## Controls

- Direct eight-call word: its exact product equals `T`, and it agrees on all
  48 role/address basis inputs. All 8 single-call omissions are rejected, and
  so is a mutated final label (`b -> a`).
- Lemma 2 checks: `D_N(b) = D_N(a^2) D_N(d)` and `D_N(a) = D_N(b^2) D_N(e)`
  hold for all 120 idempotents. `J` is exactly the kernel, with dimension 9.
  `S` meets `J` only in `0`, and lifts are unique. The twisted bimodule law
  holds for all 512 elements of `J` and all `r,s` in `S`, and `Phi(J^2)=0`.
  The defect rank is 3 in both bases. The step-5 identity
  `Phi(A^-1 W - I) = sum aug(C_k)^-1 mu(v) N_k psi(C_k)` holds for 60 random
  words per base, of lengths 1 to 8, with rank at most the number of calls of
  the other label. Lemma 1 holds for 200 random words.
- Mutation control for the lemma: the three-output target
  `diag([a],[b],[c],[1])` has defect rank only 2 in each base. Both joins find
  a 6-call word for it, `128 144 34 0 34 144` from A and `144 34 0 34 144 128`
  from B, with `(n_a,n_b)=(3,3)`. Python replays both words exactly.
- Planted 7-words: two random seeds per join (sampled run, every 64th class plus
  the planted class). Each must return a length-7 word, confirmed in Python to
  equal the planted product. This exercises the `X f Y` path in both joins.

## Reproduce

From the repository root, with Python 3 and a C compiler with POSIX threads:

```sh
python3 -I -B research/a4-seven-call-radical-rank/verify.py
python3 scripts/research_package.py --package research/a4-seven-call-radical-rank --check-only
```

The expected final line is `PASS_A4_FOUR_ROLE_EXACT_MINIMUM_EIGHT`, preceded by
a JSON report with the counts above. Local runs took about 80-90 s wall time
with 369 MB peak RSS, using Python 3.14.4 and gcc 15.2.0 on 4 shared CPUs. The
generic runner `scripts/research_package.py --package
research/a4-seven-call-radical-rank` also passed under a private Python 3.12.15
(`PASS_REGISTERED_RESEARCH_PACKAGE`, 84 s, 369 MB).

## Scope, inherited assumptions and unresolved obligations

- This is a formal model only. It inherits #2116's alphabet, unit call
  prices, four roles, dirty inputs, absence of workspace and exact-coefficient
  target. The lemmas are proved for this alphabet and target. The rank argument
  uses only that each call is `I + (g+1)N` with `N` an `F2`-rational rank-one
  idempotent.
- Unresolved, and not addressed here: native conversion of `F2[A4]` calls,
  restored workspace, a physical caller, chronology, hosting, precision,
  recursive transfer and supplier admission. These costs are unknown, not
  zero.
- Decision consequence: the A4 four-role endpoint gives no formal saving, so
  this target gives no reason to price a native conversion of `F2[A4]` calls.
  The package closes #2116's named open question and extends the existing
  direct-optimal pattern of the formal finite-group family (for example `Q8`
  in #2047 and #2248, `SL2(F3)` in #2010) to one more target. It changes no
  current lead, supplier or selected result. A 7-word would have saved 1 of 8
  calls in the formal model only.

## Open next questions

The same questions are structured in [TASK.json](TASK.json).

1. **Can the length-6 case `(n_a,n_b)=(3,3)` be excluded in writing?** This
   would turn the exact minimum into a fully written theorem. That matters for
   role counts where exhaustive search is infeasible. First step: at `(3,3)`,
   both step-5 identities must be tight rank-3 decompositions with
   `F2`-rational columns `aug(C_k)^-1 x_k`. Look for a contradiction between
   the two bases, or at the `J^2` layer. Blocked by: nothing beyond the
   bookkeeping.
2. **Does the radical-rank bound extend to `G = P x| H`, with `P` a normal
   2-group and `H` of odd order?** An example is
   `SL2(F3) = Q8 x| C3`. The goal is uniform label-count floors in place of censuses.
   First step: state the lemma with `S = F2[H]` and an equivariant functional
   `mu` on the Frattini quotient of `P`, then test it against the existing
   `SL2(F3)` census of [PR #2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010)
   (`research/sl2f3-conjugate-triple-seed592f`). Blocked by: nothing for the
   formal statement. Native conversion stays unpriced.

## Predecessors and attribution

- Model, alphabet, direct word, C3 screen and the length-6 exclusion come from
  [PR #2116](https://github.com/CrocSwap/integer-mult-bounds/pull/2116)
  (`research/a4-commutator-four-role-seed-dcbf`, GitHub `1337isnot1337`,
  commit author Cinna Davis, head `19cdf74af162f1444830f1a0f0a8e0fe306564ad`;
  Discussion [#2095](https://github.com/CrocSwap/integer-mult-bounds/discussions/2095)).
  This package answers that package's named open question. It re-proves the
  length-6 exclusion with new code and does not modify the predecessor.
- Prior untwisted `J/J^2` arguments, all by GitHub `1337isnot1337` (commit
  author Cinna Davis) and merged: the coefficient-matrix argument for the
  2-group `Q8` in [PR #2047](https://github.com/CrocSwap/integer-mult-bounds/pull/2047)
  (`research/q8-central-minus-one-any-registers-seed0332f4`, head `46bce88f`)
  and [PR #2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248)
  (`research/q8-r3-two-central-one-generator-seed809fc39d`, head `835bd7b1`);
  and the abelian four-role rational-frame floor of
  [PR #2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085)
  (`research/bit-four-register-rational-frame-floor-seed3573e12e`, head
  `5302b9ba`), whose `J/J^2` per-label count with rank-one calls is the closest
  analogue of the step-5 rank count. To our knowledge (a search of
  `research/*/README.md` and open PRs at base `20ecf289`), three ingredients
  here are new: splitting off the semisimple part `F2[<a>]` in a group algebra
  that is not local; the twisted functional `Phi` that absorbs conjugation by
  that part; and using both bases together with the C3 determinant. The open
  [PR #3893](https://github.com/CrocSwap/integer-mult-bounds/pull/3893)
  (`1337isnot1337`, S3 three-register rank lower bound) is a concurrent,
  different rank floor.
- Exact pins are in [SOURCES.json](SOURCES.json). The base is
  `20ecf2891d80b5acf18d980b2164fb44ea7faa90` and priority revision 6 is in
  force. The live input is #2116's `RESULT.json`.

Provenance: the lemma, both joins and the verifier were written in one
AI-assisted session; the two joins are separately implemented, not
independently authored. The written proof's steps are each checked numerically
by the verifier, as described above. The package was reviewed by four
independent AI review passes in the same loop. No independent human review is
claimed.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
