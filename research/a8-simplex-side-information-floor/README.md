# Orthogonal side information keeps the A8 simplex nine-term COPY floor at 72

**Finite certificate on two pinned witnesses; no new κ.** The selected record and frontier are unchanged.

[a8-simplex-decoder-floor](../a8-simplex-decoder-floor/README.md) (#1248) proves that the A8 simplex
nine-term decoder on P120 has separate-term COPY cost at least 72 for every complex row shift, with two
explicit sharp witnesses. [a7-a1-nonlinear-copy-floor](../a7-a1-nonlinear-copy-floor/README.md) (#5299)
showed that two lemmas keep the A7+A1 floor at 72 against nonlinear messages, with and without free
orthogonal side information. Its second Open next question asks for the A8 case: Lemma 1 transfers at
once, and Lemma 2 needs its own witness search. This package runs that search.

| Setting | Lower bound on the nine-term bill | Scope |
|---|---:|---|
| no reader side information | **72** | every complex shift (#5299 Lemma 1 with #1248's theorem) |
| readers know all orthogonal inputs | **72** | both #1248 sharp witnesses (finite certificate, this package) |
| same, independence bound only | 64 | both witnesses (exact maximum, a control) |

Both certified bounds equal the linear invoice. On these two witnesses, nonlinear coding does not
undercut the linear invoice, and free orthogonal side information does not either. For d-bit blocks
each bound scales to `72d`.

## Model

The model is #1248's, unchanged. There are 120 E8 root lines in the A8 frame (36 pair roots
`e_a - e_b`, 84 triple roots `1_S - 1/3`). The binary pairing is `B_ij = 1` exactly when lines i and j are
orthogonal or equal. The readers are `Y_k = {j : r_jk != 0}`, and the decoder rows are
`D_i = 2(r_i - r_i,anchor)`. The anchor is coordinate 0, except that the active witness anchors row 0 at
coordinate 1. Term k reads rows `X_k = {i : D_ik != 0}` and is billed `rho_k = rank_F2 B[X_k, Y_k]`. The
nonlinear message model is #5299's. Term k sends `m_k = f_k(x restricted to X_k)`. Every reader `j` in
`Y_k` must recover `sum_{i in X_k} B_ij x_i` from `m_k` and its own side information. The cost is
`log2 |range f_k|`.

## What is checked

The lemmas are #5299's. They are used here as written premises, not re-proved:

- **Lemma 1 (no side information).** An invertible `rho_k x rho_k` block `B[S,R]` with `S` in `X_k` and
  `R` in `Y_k` forces `2^rho_k` message values. Summed over terms this is `sum_k rho_k`, at least 72
  for every shift by #1248.
- **Lemma 2 (orthogonal side information).** If reader j knows every input orthogonal to j, then only
  readers in `X_k ∩ Y_k` need anything, and each needs exactly `x_j`. Term k becomes an index-coding
  instance on the induced orthogonality graph of its demand lines `X_k ∩ Y_k`. Two certificates bound
  its rate: an induced Petersen graph with m isolated lines has rate `5 + m` (Blasiak, Kleinberg and
  Lubetzky, Fact 5.6(1), with #5299's isolated-receiver induction), and a set of r pairwise
  non-orthogonal lines has rate r.

[verify.py](verify.py) checks the SHA256 of the pinned predecessor `CERTIFICATE.json` and rebuilds the
model from coordinates. It does not import predecessor code. For both witnesses it checks all 14,400
entries of `D T^t = 2G`, recomputes the invoices `0,9,9,9,9,9,9,9,9` and `1,8,9,9,9,9,9,9,9` from `B`,
and requires them to equal the pinned ones. Per term it then finds and checks:

| Witness | Demand lines per term | Side-information certificates | Largest non-orthogonal set |
|---|---|---|---|
| dropped, `0,9^8` | 0, then 50 × 8 | 8 × (Petersen + 4) | 0, then 8 × 8 |
| nine-active, `1,8,9^7` | 1, 49, then 50 × 7 | 1 single line, Petersen + 3, 7 × (Petersen + 4) | 1, 7, then 7 × 8 |

Each term also has an invertible fooling block of size `rho_k`. Both totals are 72 in both settings.

The largest pairwise non-orthogonal set is computed exactly by branch and bound. Every rank-9 term has
one of size 8 only, and the rank-8 term one of size 7. The independence bound by itself therefore
certifies 64 on each witness. The Petersen step supplies the missing unit in every one of the 16
nonempty high-rank terms.

## What this does and does not cover

It covers nonlinear and AND-containing message codes on #1248's fixed nine-term supports, for the
separate-term bill, and for the strongest natural side information at #1248's two sharp witnesses.

It does **not** cover:

- the side-information bound for *every* complex shift (Open next question 1);
- other A8 frames, punctures, masked exactness or shared COPY billing;
- receivers that combine several terms nonlinearly.

The two rate lemmas are inherited written premises. The Petersen rate 5 is a cited published fact. No
independent human proof review or formal proof-kernel check is claimed. No supplier, physical circuit or
κ is claimed. The selected κ is unchanged.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -I -B research/a8-simplex-side-information-floor/verify.py
python3.12 -I -B research/a8-simplex-side-information-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/a8-simplex-side-information-floor
```

Expected markers (each script runs in well under a second):

```text
PASS_A8_SIMPLEX_SIDE_INFORMATION_FLOOR roots=120 witnesses=2 no_side_info=72 orthogonal_side_info=72 independence_only=64 petersen_terms=16 certificate=e1b19301ed2e402d no_new_kappa
PASS_A8_SIMPLEX_SIDE_INFORMATION_CONTROLS rejected=12
```

The default run is read-only. It compares the rebuild with the stored [RESULT.json](RESULT.json) and
re-checks the stored certificate exactly as given. `--write` regenerates the file explicitly.
`test_verify.py` runs twelve rejecting controls:

- a singular fooling block, and a fooling line outside the term;
- swapped Petersen labels, an isolated line orthogonal to the witness, and a duplicated line;
- Petersen + 3 against rank 9, a non-independent set, and an independence-only claim on a rank-9 term;
- an invoice mismatch, a broken all-pairs identity, a tampered stored certificate, and a drifted
  predecessor input.

## Open next questions

1. Does the orthogonal-side-information floor stay at 72 for **every** complex row shift of the A8
   simplex decoder? A first step is to list each line's support-reducing shifts and find, per term, the
   largest demand set with neither a Petersen + (rank − 5) witness nor a rank-sized non-orthogonal set.
   #5299 poses the same question for A7+A1.
2. Is the Petersen step forced, or would a different induced subgraph whose broadcast rate exceeds its
   independence number also close the one-unit gap in each rank-9 term? A first step is to compare
   fractional or LP index-coding bounds with the independence number on one 50-line demand graph.

## Credit and provenance

This package was produced by Nick Petalas. It answers the second Open next question of Mark (Matarener)'s
#5299 and reuses its two lemmas and certificate format. Philipp / mightyOil's #1248 supplies the A8
simplex model, the every-shift floor 72 and both sharp witnesses. joaqcoo's #1224 supplies the
one-sided nine-term normal form. The Petersen broadcast rate is Blasiak, Kleinberg and Lubetzky's
published result, with the m=4 case certified in
[p112-characteristic-two-minrank](../p112-characteristic-two-minrank/README.md). The width pricing
premise is that of #888 and #785/#814. [SOURCES.json](SOURCES.json) pins every predecessor file at
the base commit. Only `CERTIFICATE.json` is a replay input. The new checker is separately written.
Apache-2.0.
