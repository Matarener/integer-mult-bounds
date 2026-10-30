# A physical error floor for the partial-cache observer

For every positive tensor width, the exact observation channel in PR #5498
cannot approximate its coupled-query target uniformly on the physical input
unit ball to error less than `1/sqrt(19)`. The decoder can be nonlinear and
can use the complete supplied history. A randomized decoder has worst-case
expected squared error at least `1/19`.

This is a new quantitative application of an existing exact kernel. It uses
the actual PR #5402 entrance basis. It is sharp on the specified kernel
subspace, not a claim about the optimum on the full input ball. No new kappa,
paid-call bound or complete multiplication theorem follows.

## Source and observation contract

Use canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
JoyboyBrian's [PR #5498](https://github.com/CrocSwap/integer-mult-bounds/pull/5498),
head `da7f5a0c005130873f45c8e5073cd5c989cd5feb`, supplies the
[exact kernel and proof](https://github.com/JoyboyBrian/integer-mult-bounds/blob/da7f5a0c005130873f45c8e5073cd5c989cd5feb/research/partial-cache-history-observer/PROOF.md).
Dillon Amburgey's [PR #5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402)
supplies the [physical provider](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/native-rank8-helper-provider/PROOF.md).
The five exact source copies and their Git/SHA256 pins are in `source/` and
`INPUTS.json`. Source copies retain their original bytes and attribution.

The observer sees every full-nine-axis-frame value during the raw backward
word and all eight partial-frame endpoint caches. It sees 5,897 full-frame
events and the caches at roles 633 through 640. It does not see other main
values, other partial histories, original helper retractions or additional
paid responses. All 632 original inputs are independent. The nine owned
inputs can be zero for the lower-bound instances.

The predecessor proves that its scalar vector k annihilates this entire
channel in the free-word algebra. Thus k times any field v has zero
observation at every positive width. It also proves that the actual physical
target b changes only in mode one, by

    delta b_1 = -2 Km_1^-1 R v.                         (1)

This complete history identity is a credited proof premise. We do not rerun
its 21,473-record history interpreter. The native map R is the full Gaussian
on nine axes. It and the monomial Km are unitary in the Euclidean field norm.
Their all-width physical realization remains a source assumption.

## Pull the witness back through the physical entrance

Let V be the complex field space at one fixed positive width, with its usual
Euclidean norm. Give the physical input bank the direct-sum Euclidean norm.
Let L be the provider's scalar helper entrance basis. The checker obtains

    sum_X k_j^2 = 60,  sum_Y k_j^2 = 12,
    sum_H k_j^2 = 68,  L^-1 k_H = -4 e_225.             (2)

It checks (2) both by the supplied exit basis and by reversing and inverting
every entrance operation. A forward application of L to -4 e_225 gives
exactly the 44 nonzero helper entries in the source kernel. Both full inverse
products are also checked on all 122 basis owners.

Physical main inputs use unitary monomial entrance wrappers B_X,j and B_Y,j.
The raw X role has a unitary native birth frame F_X,j; its raw logical value
is F_X,j^-1 B_X,j x_phys,j. The raw Y roles have ground birth frames. Set
the physical X displacement to k_j B_X,j^-1 F_X,j v, and the physical Y
displacement to k_j B_Y,j^-1 v. The backward conjugation convention is kept
in F_X,j. Each native frame is a product of unitary Gaussian factors, so
this extra X frame preserves the norm. It is not omitted from J.
The physical helper entrance applies 2 Km_1 on role 225 before L. Therefore
set the sole nonzero physical helper displacement to -2 Km_1^-1 v. All other
physical helpers and all owned inputs have zero displacement. Call this
physical input map J:V -> input bank. Its raw image is precisely k v, and

    O J = 0,   ||J v||^2 = (60+12+4)||v||^2 = 76||v||^2,
    T J v = (0,-2 Km_1^-1 R v,0,...,0),
    ||T J v||^2 = 4||v||^2.                            (3)

Here O is the stated observation channel and T is the eight-mode physical
target. The 61 nonzero physical roles comprise 57 X, three Y and one helper.
Using the raw norm 140 would give the weaker squared ratio 1/35. Treating the
helper basis as an isometry would be incorrect. Formula (3) accounts for its
actual nonunitary scalar basis and its factor two.

The scalar coefficients in (2) act once. They are not raised to the tensor
width. The unitary one-column address maps remain unitary under tensor powers.
Thus 76 and 4 in (3) hold at every positive width.

## Minimax proof

Choose any unit v in V and put u=Jv/sqrt(76), t=TJv/sqrt(76). Both u and -u
are in the physical input unit ball. Their complete observations are zero,
and their targets are t and -t, with ||t||=1/sqrt(19).

A deterministic decoder must give the same output z on both inputs. The
triangle inequality gives

    max(||z-t||, ||z+t||) >= ||t|| = 1/sqrt(19).         (4)

For a randomized decoder the output distribution is also identical for the
two inputs. The parallelogram identity gives, pointwise in its randomness,

    (||z-t||^2 + ||z+t||^2)/2 = ||z||^2 + ||t||^2.

Taking expectations proves that at least one input has expected squared
error at least 1/19. Infinite second moment already satisfies the bound.
No assumption of linear postprocessing or a bounded instruction count enters
this argument.

On the restricted domain `{Jv: ||Jv||<=1}`, the constant-zero decoder has
maximum error exactly 1/sqrt(19), by (3). It also attains squared risk 1/19.
This proves sharpness on that subspace. It supplies only a lower bound on
the full physical unit ball. It does not show a sharp global optimum.

## Verification and limitations

Run `python3.12 -B scripts/research_package.py --package research/partial-cache-minimax-floor`.
Python 3.12 and its standard library suffice. Both registered commands use
isolated, warning-strict Python, normally and under `-O`. Each checks five
source copies, 244 basis inverse products, 115,200 literal monomial address
actions, the exact native one-axis unitarity identity, 117 rational complex
square-loss identities and 14 rejection controls. The output is
`PASS_PARTIAL_CACHE_MINIMAX_FLOOR`.

The all-width statement is the written proof, not an extrapolation from
finite address tests. The finite tests bind the consumed basis, unitary
wrappers and target coefficients. The complete predecessor history proof and
native semantics are explicit premises; their full suites, a cold selected
replay, human review and a proof-kernel check were not run. This bound uses
continuous complex inputs and Euclidean error. It does not establish a bound
for a restricted integer lattice, a particular rounding algorithm, paid work,
whole-machine observations or the changed selected completion.

## Open next questions

- Can one additional retained observation separate the subspace J(V)? This
  would change the observer contract. Start with a versioned partial-history
  row and compute its action on J; physical availability and retention are
  still required.
- What is the full norm of T restricted to ker O? This determines the sharp
  linear-information error on the full ball. Start with a fixed-width exact
  observation matrix. Its size and an all-width spectral argument remain open.
- Can admissible discrete inputs realize a comparable pair? Start with the
  actual input lattice and all entrance denominators. The continuous bound
  alone does not answer that precision question.

Credit JoyboyBrian (@JoyboyBrian) for the exact partial-cache kernel and target
binding; Dillon Amburgey (@dillona) for the native coupled provider and basis;
and the retained Mark/Matarener, THU New Media Research Center, zxv, Cao Yifan,
Cinna Davis, Dugongue, Chris R, native and compiler lineage in those sources.
Ali Romman (@aliromman) supplies this norm calculation and minimax application,
with substantial OpenAI Codex assistance. Apache-2.0. No independent human or
formal-kernel acceptance is claimed.
