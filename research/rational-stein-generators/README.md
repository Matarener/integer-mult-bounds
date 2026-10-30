# Exact rational Stein generators

I implement bounded rational generators for the coefficient stage of the
retained Gaussian dirty-shear compiler. For a rational complex Stein
displacement \(E\), I emit exactly \(\operatorname{rank}E\) pairs
\[
E=\sum_j g_ja_j,\qquad
\|g_j\|_2\le1,\quad\|a_j\|_2<2\|E\|_2,
\]
where \(a_j\) is an explicit row and every coefficient lies in \(\mathbb Q(i)\).
I use exact orthogonal residuals and dyadic norm scaling. I compute neither
a numerical rank cutoff nor a square root.

The source already gives a polynomial-time route through rational
Gram–Schmidt and approximate square-root normalization. I refine that
construction with an exact producer, explicit bit bounds and source-bound
macro evidence. I do not report irrational normalization as an error.

## Result and caller

I prove a conservative preprocessing height bound
\(4096(m+1)^6(b+1)\) for \(m\times m\) input with component height \(b\),
and retain the source's generator count. I choose a dyadic
\(\Gamma\ge2\sum_k(|\Re a_k|+|\Im a_k|)\), making
\(P=I+U(a)/\Gamma\) admissible to the original triangular child on its
dyadic tiles.

I replay the source's order
\[
Px;\quad y+\Gamma L(g)x;\quad P^{-1}x;\quad y-\Gamma L(g)x
\]
with exact matrix callbacks. I prove a polynomial macro-prefix and
inverse-prefix bound using additive completed shears, and show how one
unfinished child's separate bound combines with it.
[PROOF.md](PROOF.md) gives the normalization, conjugation convention,
bit estimates and full scope.

At PR4100 `GAUSSIAN.md:102–117`, this producer can replace the bounded-generator
normalization stage for rational reference Schur matrices. The source's
numerical implementation already uses a correct coefficient-row convention;
I make its relation to the adjoint-column notation explicit. FFT roots and
complete child circuits remain separate.

I start from main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority 7,
and pin PR4100's retained source
`337d04939571a637aeab54a0f58f54fde811663a`.
[SOURCES.json](SOURCES.json) records the actual bytes.
[Discussion4196](https://github.com/CrocSwap/integer-mult-bounds/discussions/4196)
records the claim, live overlap and publication handoff.

## Verification

From the repository root, with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py \
  --package research/rational-stein-generators
```

I run two ordinary/optimized commands, each with a 180-second limit.
I authenticate the retained exact Schur producer and preserve its assertions,
adding one collection hook. I then extract the original generator macro's
seven-statement tail, preserve its order and reversed source indices, and
replace SVD/scale selection with the new producer.

The finite evidence covers 56 matrices, 67 generators and 268 macro stages.
I check exact displacement/product reconstruction, ranks, norm bounds,
observed component/norm/scale heights, full endpoints, inverse-prefix
identities and a conservative prefix envelope. The fixtures include
actual recursive Schur shears, a tiny second independent residual, both
real and complex matrices, zero rank and a large scale.

Controls reject omission of a \(2^{-200}\) nonzero rank term, an extra
complex conjugation, missing compensation, missing source restoration,
zero normalization, floating inputs and altered source bytes.
I compare the complete typed [RESULT.json](RESULT.json).
The observed heights are not an exhaustive profile of arithmetic temporaries.

I use exact matrix callbacks for `triangle_plan`, `toeplitz_shear` and
`inverse`. This is a source-bound macro-schedule replay. I do not report
FFT/butterfly execution, physical tape behavior or complete Gaussian
acceptance. The separate written height and norm proofs carry the
universal statements.

## Prior work and attribution

I inspected 100 recent PR records and 35 hub comments, the original
shallow-Toeplitz preprocessing proof, earlier core/outer reviews and
local generator searches. I found no matching rational bounded-generator
implementation in that coverage. I did not exhaust arbitrary diffs,
older comments, unpublished work or literature priority.
The repository overlap helper searched 5,236 local records and returned
106 broad terminology matches; it had no usable remote cache. I used
separate live snapshots, including 60 PRs and 10/696 hub comments before
publication. The new PR4195 concerns CRT shared rows and PR4197 concerns
compensation forests.

I retain PR4178's incoming-height/rounded-caller result, PR4186's boundary
rounding result, PR4193's conditioning result and PR4192's compiler arena
audit as separate contributions. The new source adapter does not replace
their respective obligations.

I credit Vlado Vojdanovski/PR1673 for the bounded-generator compiler,
exact Schur producer and polynomial-time preprocessing argument; Cinna
Davis for the later caller; and classical Gram–Schmidt and structured-matrix
methods. I preserve the frozen source bytes and notices.
Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Source-analysis agents belong to the author process. I claim no independent
human or formal-kernel acceptance, worldwide novelty or selected-frontier change.
Apache-2.0.

## Open next questions

In [TASK.json](TASK.json) I specify two next questions with first steps
and blockers: certified rounded child-circuit execution using these
coefficients, and source-bound delivery into the full Gaussian caller's
coefficient pages and error budget. Reviewers must retain those obligations
when using this generator.
