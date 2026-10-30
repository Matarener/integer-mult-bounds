# The sharp two-axis native cutoff is six

For the **two-axis affine/quadratic Gaussian monomial group**, a fixed
scalar register identity holds at every positive tensor width exactly when
it holds at widths **6, 7, 8 and 9**. This is the earliest sufficient
consecutive window. A fixed nonzero residual vanishes at every width from
1 through 8 and has a matrix entry equal to one at width 9.

This answers the two-axis case of the least-cutoff question in
[PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369).
Its general sufficient window specializes to 8–11; the new result gives
the exact two-axis minimum and an obstruction to every earlier test set.
The original general-axis theorem and checker remain unchanged.

## Exact statement and why the lower bound holds

Use the predecessor's input-phase convention
`U(g,q)|x> = i^q(x)|g(x)>`, where `g` is binary affine on two axes and
`q=c+a1*x1+a2*x2+2*b*x1*x2 (mod 4)`. External coefficients remain outside
the tensor power. There are 128 phase recipes and 24 affine maps.

At width `f`, the central scalar relation is `[iI]=i^r`, with `r=f mod 4`.
After this relation, the group-algebra evaluation has zero kernel exactly
at the following widths and every subsequent width of the same residue:

| Residue r | First faithful width | A sharp witness's address multiplicities |
| --- | ---: | --- |
| 0 | 8 | (2,2,2,2) |
| 1 | 9 | (1,0,4,4) |
| 2 | 6 | (0,2,2,2) |
| 3 | 7 | (1,2,2,2) |

Address order is `(00,10,01,11)`. Thus the least common stabilized cutoff
is **F=6**. The kernels are periodic in the central residue; they are not
all the same kernel. More generally, a set of test widths is complete
**if and only if** it contains a threshold-reaching width in every residue.
The same recipes, external coefficients and program must be used at all
widths, with all independent dirty inputs and specified output roles retained.

The [proof](PROOF.md) establishes necessity as well as sufficiency.
`AGL(2,2)=S4`: three distinct input addresses determine an affine map,
while a tuple using at most two addresses has an odd permutation in its
pointwise stabilizer. The alternating sum of affine maps therefore kills
such tuples. Combining it with a normalized phase projector supplies four
explicit fixed residuals, one per residue. Exact multiplicity congruences
and an analytic case split prove the four sharp thresholds. This necessity
argument is special to two axes; a phase-character census alone would not
establish a representation-kernel minimum.

For the residue-one residual, the width-nine input and output are both
`(0,2,2,2,2,3,3,3,3)`. Its diagonal entry is exactly `1`, and its column
has 24 distinct signed outputs. The [receipt](RESULT.json) gives all four
witnesses. No enormous tensor matrix is built.

## Reproduce and evidence

Python 3.12 and the standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/two-axis-native-cutoff --check-only
python3.12 -B scripts/research_package.py --package research/two-axis-native-cutoff
python3.12 -I -O -B research/two-axis-native-cutoff/verify.py
```

Expected marker: `PASS_SHARP_TWO_AXIS_NATIVE_CUTOFF`.

[verify.py](verify.py) checks the minimum formula for all 128 phase characters
against a separate complete 625-count normal-form census and exact fixed-width
realizations through 13. Reducing each positive multiplicity to 1–4 preserves
its phase and support, which proves the minimum census complete.
[literal.py](literal.py) independently evaluates all 128 Fourier terms and
signed affine images. It checks all 24 affine maps, 576 sign compositions,
3,072 phase pullbacks, all 15 nonempty pointwise stabilizers, all 1,364 ordered
tuples at the relevant below-threshold widths, and 2,856 phase sums on count
classes through width 9. Controls omit affine signs, omit the quadratic phase,
tensorize external Fourier coefficients, or confuse phase realization with
full affine separation. They give different exact outcomes as required.
Neither implementation imports a predecessor evaluator. The shared mathematical
contract and Python runtime remain limits to computational independence.

[VERIFICATION.md](VERIFICATION.md) records the normal, optimized,
committed-byte/source-history and Git-free export checks. Finite results
corroborate the proof; they do not establish an unbounded-width theorem by
sampling. No independent human review or proof-kernel acceptance is claimed.

## Scope, coordination and remaining work

This is a scoped mathematical result. It does not supply a physical supplier,
complete native caller adapter, tape/precision invoice, or new multiplication
exponent. The selected conditional κ remains 0.003027288235, with its inherited
assumptions. In particular, the current nine-axis supplier does not acquire
a new cutoff from this two-axis result. Hadamards, arbitrary width-dependent
programs and nonlinear or rectangular interfaces are outside this grammar.

The round starts from canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7; the predecessor
head is `18354f41de4dc7bfda4692e814cf1d91a6d619ef`.
[SOURCES.json](SOURCES.json) pins its exact proof, scope and attribution bytes.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19174077)
records this bounded specialization. It complements
[Mihir Srivastava's active one-axis/general-proof audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19174027),
which explicitly excludes least cutoffs for n>=2. Its small-character
enumerations are overlapping corroboration, not the new result claimed here.

The initial fresh snapshot covered 378 open PR bodies and 4,790 Discussion
records, with complete local-note coverage. Targeted successor and canonical
thread checks found no two-axis sharp-cutoff contribution in that coverage;
arbitrary diffs and unpublished work remain unknown. [TASK.json](TASK.json)
records the scope change from the formal-interface card: a written kernel
lemma and exact certificates, with no proof-assistant build. The current picker
was run once (seed `77f1c0eee02e0484b09774f596f29b84`, bit-mechanism suggestions);
the explicit least-cutoff question supplied this scoped mathematical assignment.

## Open next questions

For n>=3, which phase-fiber permutation representations are needed for the
exact central-quotient kernel? The two-axis sign obstruction does not establish
necessity of affine-span tuples there. A useful next step is to calculate the
pointwise-stabilizer coset-sum row spaces in one specified three-axis phase
fiber, and compare their common kernel with affine-bucket isolation. That
representation-theoretic bridge, rather than another character table alone,
is the missing step toward a sharper general cutoff. No general-n search
is claimed or reserved by this package.

## Credit

Prepared by Hiroki KUMAZAKI with substantial OpenAI Codex assistance, including
separate automated proof, literal-checker and adversarial-review subagents.
Ali Romman supplied the native grammar, Fourier-separation method, uniform
cutoff and open least-width question in #5369. Jose Manuel's native recipe
and phase-sector conventions, ywz65's affine-basis argument, Chris R's
finite-alphabet tensor-separation lineage, Douglas Colkitt, and the retained
source contributors keep their credit. The source NOTICE remains pinned.
Fourier inversion and symmetric-group sign representations are classical;
no global literature-priority claim is made. New work is Apache-2.0.
