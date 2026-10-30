# The eight-carrier code of the P104 local word is unique

**This is a scoped negative result. No new κ is claimed.**

Every legal P104 local word decodes through owned deliveries. The owned part
`w_l` delivered to partner `l + 112` has two properties. Its coordinate at `l`
is 1. It is zero on the 55 ports that conflict with `l`, where ports `i` and
`j` conflict when `<q_i, q_j> = 1`. So the span of the `w_l` is a *decoding
code* over the 104 ports. It has dimension at least 8, because the conflict
graph contains 8-cliques.

This package proves, with computer assistance, that over `F_3` there is
**exactly one 8-dimensional decoding code, up to sign changes of the
coordinates**. Its minimum weight is **49**.

The code is the one that the eight carriers of the PR5907 and PR6030 words
already deliver. In each word, the ten owned deliveries of support 52 span it
exactly. Any 49 ports span a space of dimension at least 8, since at most 36
ports fit in a codimension-2 subspace. It follows that, in a single-stage
design whose partner code is 8-dimensional:

- every carrier needs a root frame of dimension at least 8;
- every carrier must land in a frame of dimension at most 1.

So each carrier pays at least 7, which is 56 per call. That is exactly what
the PR5907 word pays. The paid H1 of the local word therefore cannot be cut by
cheaper carriers for any eight-dimensional code, not only for PR5907's.

**Card:** `complex-rank-shape-decoder`, refined to the decoder code of the
local word. See [TASK.json](TASK.json).

**Base:** canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`. Inputs are
pinned in [SOURCES.json](SOURCES.json).

## What is proved

The full statements and proofs are in [PROOF.md](PROOF.md).

1. **Lemma 1, frame decomposition.** A public row's lives-in-frame part stays
   on ports of its frame. It follows that partner parts `w_l` give a decoding
   code. Dyadic scalars make this code reduce mod 3 to a decoding code of the
   same dimension, and supports can only shrink under the reduction.
2. **Theorem 3, uniqueness.** We fix the conflict clique
   `T = {1, 5, 18, 20, 80, 85, 100, 103}`. An 8-dimensional code is then
   determined by 384 trits `w_t[m]`, plus, for every other port, a
   combination of the four clique members orthogonal to it.

   The search is a depth-first enumeration over `F_3`. It uses exact
   incremental Gaussian elimination and a complete sign gauge on `T`. It finds
   one solution, and that solution has no free variable.

   The solution's decoding matrix is sign-symmetric, so the row and column
   codes agree. The weight distribution is 49 (208), 52 (32), 62 (16),
   65 (448), 68 (1504), 69 (1408), 70 (512), 71 (192), 72 (768), 73 (1024),
   75 (64) and 76 (384).
3. **Corollary 5, scoped cost floor.** Assume a partner code of dimension 8,
   dyadic scalars, and a basis of eight delivered vectors, each carried down
   one owned chain directly to its receivers. Then every chain costs at
   least 7.

| Word | Weight-52 owned deliveries | Their rank mod 3 | Same code as the solution | Partner-code rank mod 3 |
|---|---:|---:|---|---:|
| PR5907 (`p104-helper468-rung-removal`) | 10 | 8 | yes, up to signs | 8 |
| PR6030, selected (`p104-helper470-twin-rung-removal`) | 10 | 8 | yes, up to signs | 9 |

PR6030's partner code has one bookkeeping direction outside the unique code.
Corollary 5 therefore describes its carriers but does not bound the word as
written.

## Certificate

[gen8.py](gen8.py) and [code8.py](code8.py) wrote a pre-order certificate of
the search. Its four parts are split by root option, and each was generated in
one Kaggle process.

The search branches first on port 0, which has 15 canonical options. The
four parts hold:

| Part | Root options | Internal nodes | Dead nodes | Leaves | Generation time |
|---|---:|---:|---:|---:|---:|
| 0 | 4 | 48,696 | 26,162 | 0 | 4,411 s |
| 1 | 4 | 48,328 | 25,730 | 0 | 4,389 s |
| 2 | 4 | 40,897 | 27,884 | **1** | 4,814 s |
| 3 | 3 | 49,050 | 21,251 | 0 | 3,715 s |

Each part is about 50 KB gzipped. An earlier, independent run of the same
enumeration also found exactly one solution, with identical node totals in
every part. The replay takes about 107 s per pair of parts.

[verify.py](verify.py) needs no trust in the certificate. At every node it
recomputes all canonical consistent options of the named port, descends into
each, and checks that dead nodes have none. The certificate only says in which
order to branch.

## Verification

```sh
python3.12 -B research/p104-carrier-code-uniqueness/verify.py --parts 0,1
python3.12 -B research/p104-carrier-code-uniqueness/verify.py --parts 2,3
```

The verifier uses only the standard library ([replay.py](replay.py),
[wordcode.py](wordcode.py)). Each command does the following:

1. Authenticates the pinned words.
2. Checks the structure: the ports agree between the words, all 104 have odd
   weight, the conflict graph is 55-regular, `T` is a clique,
   `f(8) = 60` and `f(7) = 36` (by enumerating all hyperplanes and all
   codimension-2 subspaces).
3. Replays the Lemma-1 decomposition of both words. This checks the frame
   invariant after every event and every partner endpoint. It also checks
   that the weight-52 deliveries span an 8-dimensional decoding code that
   satisfies the model equations.
4. Replays its two certificate parts.
5. For the part that holds the solution, checks the solution: it decodes, it
   is sign-symmetric, its weight distribution and minimum weight are as
   stated, and it is sign-equivalent to both words' codes.
6. Runs the controls:
   - one trit changed in the code breaks the model equations;
   - a certificate whose first internal node is marked dead is rejected;
   - a certificate whose first dead node is replaced by a leaf is rejected.
7. Compares its sections of [RESULT.json](RESULT.json). It also checks that
   the recorded parts cover every root option and contain exactly one
   solution.

The final marker is `PASS_P104_CARRIER_CODE_UNIQUENESS`.

## Lean

[`lean/`](lean) formalises everything in PROOF.md except the finite search. It
uses the same Mathlib revision as `fragmentation-ceiling`.

**Machine-checked:**

- [`CarrierCode/Word.lean`](lean/CarrierCode/Word.lean) models a word as a
  list of events with the checker's frame rules. It proves:
  - Lemma 1, the frame invariant along any legal run (`inv_run`), starting
    from the initial state (`inv_init`), together with the fact that owned
    parts lie in the span of the delivered owned rows;
  - that `row = lp + od` is the real row semantics (`step_row`);
  - Corollary 2 (`decoding_vector`);
  - that the word's arithmetic commutes with any ring hom (`run_map`,
    `legalRun_map`, `row_map`), which is the formal reduction of a dyadic
    word to `ZMod 3`.
- [`CarrierCode/Cost.lean`](lean/CarrierCode/Cost.lean) proves:
  - `dim B + dim B^⊥ = 9` for the dot product;
  - that a frame holding at least 49 ports has dimension at least 8, and a
    frame orthogonal to at least 49 ports has dimension at most 1;
  - that the decoding vectors of an 8-clique span the code
    (`span_of_clique`);
  - Corollary 5 (`carriers_cost`): at least 7 per chain and at least 56 for
    the eight chains.

**Taken as hypotheses, checked by `verify.py`:**

- `CodeFact`: every 8-dimensional decoding code has row and column minimum
  weight at least 49. This is Theorem 3 together with the weight facts. It is
  established by the certificate replay.
- `Capacity`: at most 36 ports lie in a subspace of dimension at most 7. This
  is Lemma 4, checked by enumeration.

Both are finite computations that are too large for kernel `decide`, and the
axiom policy rules out `native_decide`.

To build and audit, run from the repository root:

```sh
cd research/p104-carrier-code-uniqueness/lean && lake exe cache get && lake build && cd -
python3 scripts/check_lean_axioms.py --project research/p104-carrier-code-uniqueness/lean \
  --audit research/p104-carrier-code-uniqueness/lean/Audit.lean
```

The audit reports `propext`, `Classical.choice` and `Quot.sound` only, for all
14 declarations.

## Search-free proof via E8

[`e8/E8-PROOF.md`](e8/E8-PROOF.md) proves Theorem 3 a second time, without the search. The 104 ports are 104 of
the 120 root lines of E8, and two ports conflict exactly when their roots are orthogonal. The argument has five
steps: frame factorisation `M = M[:,F] M[F,:]`; frame sums of `N = M ∘ Mᵀ`; a linear lemma on each row of `N`
(proved by hand with the tables in [`e8/handcert.md`](e8/handcert.md)); the A2 triangle trick, which makes `M`
symmetric with `±1` entries; and signs, which give `M = D (Gram/2) D`.
[`e8/verify_e8hand.py`](e8/verify_e8hand.py) re-checks the finite inputs in about a minute.

The whole argument is also formalized in Lean (`lean/CarrierCode/E8*.lean`, final theorem
`CarrierCode.E8.decoding_unique`). All finite inputs are checked by the kernel, with no `native_decide`, and the
axioms are the standard three. These files are outside the default build target because they are heavy (about
8 GB per step-3 chunk, 35 minutes in total); `e8/E8-PROOF.md` gives the build commands and the exact scope.

## Open next questions

- **The link from `decoding_unique` to `CodeFact`.** The E8 theorem is stated
  for the matrix of decoding vectors. Deriving the word-level `CodeFact`
  hypothesis from it (row space and minimum weights) is not formalized.
- **Partner codes of dimension 9 or more are not classified.** PR6030 is one,
  because of a bookkeeping direction. A cheaper design would need carriers
  that are each cheap but together decode. The clique and cover bounds alone
  do not exclude this.
- **Multi-stage relays are outside Corollary 5.** In a relay, partners receive
  mixtures through public roles.
- **This is not a κ improvement.** The 56 paid H1 per call in owned descents is
  forced only within the stated scope. The larger local-word lever remains the
  fragmentation of public and helper lifts; see
  [`research/fragmentation-ceiling`](../fragmentation-ceiling/README.md).

## Credits and scope

- The local word lineage is aliromman's PR5827 and DreamingOfClouds's PR5907
  and PR6030.
- The checker rules are taken from PR5827's verifier, as used by those
  packages.
- The decoding-code view, the enumeration, the certificate and this package
  are by Matarener, prepared with Claude (Anthropic) via Claude Code.
