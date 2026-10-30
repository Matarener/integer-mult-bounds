# Sharp P112 six/seven-flat bounds and actual d=1,2 invoices

[D1.md](D1.md) closes the actual **d=1 invoice for t=2 and t=3**:
the root-marked invoice is `I>=65`, and the unmarked floor is `I>=64`.
It also proves the cost-64 floor for the stated actual singleton-pivot
consumer. The proof includes every non-adapted basis and the t=3
cost-seventeen/slack-nine boundary, without N8 or a minimum actual basis.
[D2.md](D2.md) extends all three conclusions to **d=2, t=2 and t=3**.
It exhausts the actual basis, including every nonadapted and weight-nine
surplus case, and derives the low-space dimension without source-list
completeness. Its new intrinsic inputs in [RIGIDITY.md](RIGIDITY.md) exclude
**7,7,6,4** and **7,6,6,5,1** at code intersection at least two.
[RAW-SHAPE.md](RAW-SHAPE.md) also removes every positive-d threshold-dimension
defect under the raw budgets and a putative I<=64. It does not force basis
adaptation. Its actual d3 transfer also excludes every r>=2 defect and every
nonadapted eta=r branch. Complete d>=3 invoices and the global decoder
reduction remain open.

[D2-PROFILE.md](D2-PROFILE.md) additionally excludes any independent
four-piece family of support ranks at most **7,7,5,5** whose span meets
the code in dimension at least two. The proof uses actual coefficient
ratios after forcing two frame directions. It closes that literal d=2
profile and, by dimension deletion, the recorded d=3 profile 7,7,7,5,5.
The full d=2 actual invoice is proved separately in D2.md.

Every nonzero P112 evaluation-code word over a characteristic-zero field
leaves **at least five sites** outside one binary rank-six flat and one
rank-seven flat. [UNIFORM.md](UNIFORM.md) proves that five is attained for
every nonframe root and every puncturing frame, by a coefficient partition
of sizes **5,16,32** and support ranks **4,6,7**. It classifies exactly
three optimal pairs per nonframe root. Frame-root words have sharp
remainder eight and exactly 945 optimal pairs; nonroot directions leave
at least fourteen sites.

Equivalently, no nonzero codeword is a sum of a rank-six piece, a rank-seven
piece and a piece on at most four arbitrary sites. All overlaps, coefficients
and cancellations are allowed. In particular, ranks **3,6,7** are impossible.

The [analytic proof](PROOF.md) identifies a 32-root completion and its
24-root deleted quarter. A six-flat meets that quarter in at most sixteen
sites; carrying the self root reduces the capacity to twelve. Keeping that
self root is essential to the sharp four-versus-five boundary.

## Named applications

[CALLERS.md](CALLERS.md) proves nine independent-piece exclusions from the
literal positive-d C1 lists in [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
at `708f0ad8928c383de8294aea3c126e9461d2066d`. Four are t=2 profiles and
five are t=3 profiles. The implication uses a dimension-deletion lemma;
it does not assume a minimum basis, N8, completeness of those lists or the
source's global normalization.

The support theorem supplies nine T-level applications; D1.md adds the
actual d=1 invoice and consumer using the retained matched-cut geometry.
D2.md closes the corresponding actual d=2 invoice and consumer.
The CALLERS appendix also composes PR3171's coordinate-kernel/root-pencil
method with dimension deletion, giving 85 further literal profile
implications (two t=2, 83 t=3). These are historical-list implications,
not a claim of 85 currently open cases or first closures.
The new shared-frame coefficient argument supplies the two further
literal t=2 applications described in D2-PROFILE.md.
Complete C1, the global P112 decoder floor, d>=3 invoices, supplier
admission and a selected-frontier change remain outside the result.

## Evidence and scope

Two separately implemented exact engines reconstruct the declared geometry
and its historical label convention. The primary uses simple-root coordinates
and polar equations. The second reconstructs roots and quadratic coordinates
independently and uses ordinary-dot RREF annihilators. Their complete results
and completion-set digest agree:

| Finite input | Coverage |
|---|---:|
| Full root lines / live lines / punctured frame | 120 / 112 / 8 |
| Affine six-spaces, including all four offsets | 43,180 |
| Root/affine-space intersections | 5,181,600 |
| Classified live residuals of size at least 29 | 6,216 |
| All ordered orthogonal-root completions | 7,560 |
| Unordered 24-root quarter families | 3,780 |
| Nonzero hyperplane functionals per quarter | 127 |
| Literal historical profile applications | 9 |
| Optimal five-site / eight-site root covers | 336 / 7,560 |
| Matched frame-plane cuts, with every one-point deletion | 42,840 |
| Root planes, each containing at most three root lines | 4,900 |
| Credited four-six pencil profile implications | 85 |
| Shared-frame sign halves / literal profile implications | 56 / 2 |
| Distinct complementary 28-root sections / root-high cases | 12,000 / 15,360 |
| Six-quadric affine-four / affine-five sections | 2,604 / 126 |
| Four-axis form inventories / A2 planes | 70 / 1,120 |
| d2 cost-24 four-weight / cost-25 five-weight profiles | 203 / 386 |

The numerical counts corroborate finite proof inputs; the theorem is the
written argument. The root-rigidity step retains the standard real
Weyl-chamber theorem, with a rational-nullspace transfer to every
characteristic-zero field. The global 12/20/36 support capacities and
the new completion/quarter bounds are proved analytically.

The exact sharpness witness is checked on all 112 scalar coordinates.
Splitting its five-site remainder gives an independent-piece space of
profile 7,6,3,1, code intersection dimension one and minimum basis cost
seventeen: a genuine nearby slack-nine T-space boundary. D1.md proves
that its actual correction budget cannot lower the invoice below the
stated floors. It is not a decoder counterexample.

The newly used inherited frame-plane no-coloop input is recomputed on
all 42,840 cases: one engine enumerates ambient dual restrictions, while
the other tracks fundamental binary dependencies. Both agree. Separate
profile enumerations check every minimum-profile case through cost17.
Two actual d=1 factorizations verify all 25,088 Gram entries, actual
factor ranks, nonparallel factors, restricted duals, term costs and the
complete low-space support strata. These controls use one audited
implementation and attain costs 71 and 72. Two further **actual d=2**
controls, for t2 and t3, have live-root marks and three corrected weight-nine
highs each. They check all 25,088 additional Gram entries, actual ranks,
nonparallel factors, restricted duals and exact term costs (77 in both).
Their invoices are 76 and 77; no sharpness at 64 is claimed.

For both d2 controls the complete threshold space is certified, rather
than inferred from selected low pieces. Outside each of all 43,180
affine-six flats, disjoint low-piece coordinates are eliminated; the
remaining six-dimensional C/T evaluation matrix has rank six modulo3.
Its nonzero integer minor proves the same full rank in every
characteristic-zero field. Thus any low word lies in the exhibited T,
of dimension 4 or 5 and code intersection dimension two. The complete low-space certificates are
independently replayed in
`independent_d2.py`: ordinary-dot RREF coordinates and full evaluation-matrix
elimination over F5 replace the primary polar coordinates and F3 anchor
differences. It authenticates its inputs separately and rejects a zeroed
quotient column. The exact factorization/term-cost construction itself uses
one implementation, separately reviewed as code and mathematics. These
fixtures do not exhaust all actual decoder factorizations.

Meaningful controls distinguish the self root from its open neighborhood,
reverse the completion, alter a coefficient, omit a live root, omit the
puncturing frame and change the quadratic sign. The CLI controls execute
nine scientific code mutants on private copies, including the actual
singleton compensation sign, along with changed/linked source and
strict-receipt controls. Default replay changes no input bytes.

[FORMAL.md](FORMAL.md) describes nineteen kernel-checked Lean declarations:
the concrete split four-dimensional quadric, its radical lift and cap16,
and the finite-set sparse obstruction with its self-site case. They also
prove pair-avoiding sections, the frame-eight bound and the actual-vector
dimension-deletion mechanism. Two further Init-only declarations prove the
actual shared-piece cross-product identity and self-site obstruction,
with explicit multiplication/embedding premises. The complete E8 identification,
root-completion
theorem, field transfer and invoice/consumer assembly remain outside Lean.
Internal AI cross-checks are separate from
independent human or full proof-kernel review.

## Relation to earlier work

PR2816's `cover761.py` excludes the **one-extra-site** shape. Its printed
nine-site minimum uses pruning that retains only target intersections of
sizes at least 32 and 20. That figure is not a global minimum over all
six/seven-flat pairs: the present 32+16 cover leaves five sites and falls
outside that pruned domain. The earlier one-extra-site result remains valid.

PR3269 and PR3300 supply the signed-quadratic method and analytic global
capacities. PR3418 treats the distinct four-piece shape sparse-four plus
ranks 5,6,6. The present proof handles a rank-seven piece directly.
PR3455 establishes the marked d=0 invoice. This package extends its actual
basis and consumer arguments to d=1 and d=2, retaining its raw marked correction
cap and geometric row-edit inputs. Sources and exact predecessor heads
are in [SOURCES.json](SOURCES.json).

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p112-six-seven-supplement --check-only
python3.12 -B scripts/research_package.py --package research/p112-six-seven-supplement
```

Direct replay is also available:

```sh
python3.12 -I -O -Werror -B research/p112-six-seven-supplement/verify.py
python3.12 -I -O -Werror -B research/p112-six-seven-supplement/test_package.py
python3.12 -I -O -Werror -B research/p112-six-seven-supplement/independent_d2.py
```

`verify.py --emit` deliberately replaces RESULT.json; default verification
compares its exact typed scientific content. `--sources-only` reports only
input integrity and has a distinct PASS label. Lean reproduction is separate
and explicit in FORMAL.md. Hosted CI, a repository-wide build and the selected
cold replay are not claimed or needed for this isolated theorem.

## Open next questions

1. Bind the remaining E8/label/completion steps to the formal cores. First
   formalize the quadratic affine normal-form map; the present handwritten
   bridge is the missing premise of a full kernel proof.
2. Resolve actual d>=3 C1 invoices, retaining their actual coefficient and
   correction contracts; d=1 and d=2 are closed here. First kill d-2 minimum
   low-piece coordinates and apply the intrinsic 7755/7764/76651 exclusions
   where the remaining profile is dominated by one of those shapes. A
   T-level deletion alone does not preserve the actual invoice or correction
   ledger. RAW-SHAPE.md already proves full threshold dimension under a putative bad
   invoice for every positive d (raw budget alone through d=6). Actual
   higher-d invoices and surplus cases are open. Global rank/pivot normalization remains separate.

These scoped next steps and blockers are recorded in TASK.json. Neither
requires another global flat census as an initial experiment.

## Credit

DreamingOfClouds supplies the P112 piece model, earlier cover and circuit
methods and PR3154's reduction and literal lists. Nick Petalas supplies
PR3269/3300's analytic capacities and the adjacent PR3418 support work.
PR3171 supplies the coordinate-kernel/root-pencil method composed in
the CALLERS appendix; that mechanism is credited predecessor work.
David Arias's `masked-root-star-assembly` supplies earlier E8 quadratic-model
work explicitly credited by those predecessors.
The retained geometry follows PR3161/3162 and the E8/P112 lineage including
joaqcoo. The new theorem, witness, caller implications and verification are
attributed to conorholds. Substantial AI assistance and exact retained-source
credits are disclosed in TASK.json and NOTICE.md. Apache-2.0.
