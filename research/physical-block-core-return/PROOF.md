# Actual block return through the Gaussian second pass

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Precisely changed boundary

PR5483 physically gathers the actual two-component RHS and recovers scalar
boundary solutions; PR5499 refines its padded-column arithmetic. Neither
consumes those solutions through the normalized Core second pass. This package
implements that missing interface, with unchanged `Core.gather`, `first_cell`,
`second_cell`, `normalize_cell`, and final `norm`. The new owner changes the
schedule and boundary solver, not those source methods. It is NOT equivalent
to the scalar BandedSolve: rounded block inverses define a different numerical
function. The reference below is the supplied factor/page function, ultimately
LU(round_P(S)) if that is how the supplier obtained the factors.

The source-relative theorem quantifies admitted pages with R=2, positive
metadata, canonical heads, fixed sufficient pool capacity, exact child primitive
contracts, and the coefficient/headroom premises below. Inputs are original
page, complex disk-grid source, four explicit block factor pages, and encoded B.
Their preparation/consistency with a desired matrix is an external premise;
our calibration executes the unchanged physical prepare_pages on exact supplied
LU factors. No global Gaussian producer, old-H coefficient or gap theorem is
assumed proved by this fixture. No selected frontier or recursive invoice changes.

## Physical reentry and return

The first pair executes gather/first_cell exactly as the original scalar method,
checks all cell row/boundary counts, consumes the original scalar factor tails,
and forms the same two RHS streams. It either retains both selected m-record
streams or clears them. Physical pack, PairBoundaryPages, and physical unpack
produce two n-record scalar solutions, preserving original row order and
checking every padded zero. The protected padded return is consumed before
second-pass work. RHS and packed scratch are cleared.

For each component, Header.repeat consumes and checks the header again. The
retained schedule consumes selection descriptors with Header.skip_selection;
the regather schedule calls unchanged gather, which consumes those same
descriptors and reconstructs exactly the same selected values. Input page and
source are immutable and only one fixed component is selected, so the selected
stream is byte-identical in either schedule. Counted source position enters the
first Cell record exactly where original Core.scalar enters its second pass.

The unchanged second_cell consumes each cell's original selected boundary and
interior records, that cell's returned boundary solution, factors, coupling and
normalizer fields. It solves the recovered interior RHS through the actual
Interior owner and calls unchanged normalize_cell. Induction over cells gives
position=m, emitted=core_length and both streams exhausted. Original scalar
factor tails are scanned and checked once more. Each component result is
rewound; the final loop reads corresponding p+2-bit records, calls original
Core.norm, and writes real then imaginary to the protected output. Both result
streams must end together. The caller consumes the return normally.

All owned RHS, selections, solutions, factors, second-interior returns and
component results are cleaned; borrowed ports rewind to their entry head1.
The original source/page and four factor-bank byte contents are never written.
Any disjoint dirty spectator is outside every owner write set and is unchanged.
The successful-domain theorem assumes blank owned scratch; it does not claim
arbitrary dirty owned pools, insufficient-capacity recovery, or every malformed
page's exception behavior. Payload aliasing with owner roles or other payload
ports is rejected before execution. Sufficient metadata nonaliasing and the
inherited encoded-count contracts remain premises.

## Seven-stage stability without an unspecified inverse constant

All real quantities below denote values represented on the P grid. Put
eta=2^-P and Q_P(x)=2^-P trunc_toward_zero(2^P x). Thus
|Q_P(x)|<=|x|, |Q_P(x)-x|<eta, and
|Q_P(x)-Q_P(y)|<=|x-y|+2eta. Rounding is coordinatewise.
Stored coefficients, not ideal Gaussian coefficients, are the reference.

For one nonempty interior, let h be its stored convolution vector and define

    mu = (||inva||inf, ||invf||inf, ||h||1, ||f||inf,
          ||h||1, ||invf||inf, ||weights||inf).

These are precisely Interior.run's seven stages. The first two, fourth, sixth
and seventh are diagonal multiply then truncate. Third is a lower convolution;
fifth is lower convolution conjugated by row reversal. Convolution performs
four exact signed Kronecker products and one final completed-coordinate
truncation, NOT per-term rounding. Its lower Toeplitz infinity norm is at most
sum |h_j|. Row reversal preserves infinity norm. Therefore every stage has
norm at most its listed mu_j before its one coordinate rounding.

Let C bound the infinity norm of the actual stored second-pass coupling matrix,
including the zero middle rows. Let b bound selected source magnitudes and X
bound each supplied boundary solution component. `subtract_row` first forms
an exact 2P-grid dot-product residual; second_cell truncates once. Thus

    M_0 = b + C X,       M_j = mu_j M_(j-1), j=1,...,7

bounds each stored interior stage; no rounding-growth term is needed because
truncation decreases absolute value. Boundary-only cells just retain X. This
also covers nonedge middle rows, whose RHS is copied unchanged.

For two boundary solutions at distance at most delta, with identical selected
source, factors and coefficients, define

    e_0 = C delta + 2eta,   e_j = mu_j e_(j-1) + 2eta.

Induction proves their actual rounded interior outputs differ by at most e_7.
This recurrence is explicit in source coefficients; no unknown inverse norm
is introduced. It is conservative even when delta=0 (actual difference is then
zero). Against the unrounded seven-stage operator, use eta rather than 2eta
for each newly introduced single-run rounding error; this does not compare
stored coefficients with original S or ideal Gaussian data.

## Intermediate width and final disk admission

Let H=2^(w-1-P), where w is the signed work-record width. Require every stored
coefficient and selected input to fit w and

    max(X,M_0,...,M_7) < H.

This bounds every record written/read in the second pass, not only its final
value. Scalar products and coupling sums live in inherited exact Count/Signed
scratch, and convolution derives its packed operand/accumulator widths from
actual magnitudes and length. Their full inherited exact primitive contracts
and storage are retained, not replaced by an unproved fixed w-bit accumulator.
The first pass and block solve must separately satisfy their own headroom
contracts. The new ledger closes only the previously missing return path.

Header sets j=ceil(log2(32p)) and normal_shift=2P-p+j. A stored normalizer d
satisfies 0<=d<=1 and actual output is Q_p(2^-j d x). Consequently each
normalized component has magnitude at most 2^-j max(X,M_7). The explicit
rational sufficient premise

    max(X,M_7) <= 2^(j-1)

makes each component at most1/2. Thus the complex squared norm is at most1/2,
the original disk check (<=1) passes, and p+2 signed storage has ample margin.
This condition is sufficient, not necessary; the implementation still performs
the actual disk guard. No promise that arbitrary factor pages satisfy it.
For two solutions the final component distance is bounded by

    2^-j max(delta,e_7) + 2*2^-p.

Cropping is a coordinate projection and cannot increase these norms. These
inequalities establish a nonvacuous conditional admission boundary, not the
complete old-H defect or an equality with scalar BandedSolve.

## Whole schedule cost and retained backing

Let G be one actual gather cost, F and S one component's full first/second
cell passes (including interior child work and return consumption), A the
physical pack/unpack work, K the complete block-consumer work, and J the final
interleave/norm/cleanup and all header/page-tail scans. Then retained schedule
cost is 2G+2F+A+K+2S+J. Regather adds two real gather executions instead of the
two descriptor-only skips; clearing/allocator placement are measured too, so
we do not assert their finite counter difference is literally2G.

For each nonempty cell and each component, the second interior invocation
pays five diagonal products and two actual convolution calls, including their
packed integers, four signed products, reversals, moves and clears. Every
original factor/coupling/normalizer field is traversed in source order; no
host decoded payload or random gather enters the sealed call. Header/selection
rescans and original scalar factor tails remain paid even though the scalar
boundary owner is unused. The fixed unused scalar owner remains allocated
and is INCLUDED in the full retained owner-bank census.

Retaining selections parks 2mw payload bits across block solve; regather
instead revisits the full target input and validates the norm for the real
component. Both retain 2nw scalar solutions until consumption, all four factor
banks, original source/page, and the full Core, word, convolution and block
owner capacities. Erased backing is NOT subtracted. Per-role high-water
capacities may shift with allocation order: a 2mw live-payload saving does not
imply a 2mw reduction in historical backing. The verifier compares matched
fresh owners on the SAME packet and reports all tape reads/writes/unit moves,
retained owner cells, external factor and page/source backing, and preparation
work separately. Complete retained cells include the consumer, preparation
owner, original page/source and live external count descriptors at each return;
the disjoint ambient dirty spectator is excluded from both schedules and adds
the same arbitrary frame size to each. The separate preparation-owner census
is explicitly after the isolated disk control, which can grow its scratch.
Counter totals are not Python-instruction counts; encoded
loop/control overhead remains the inherited source tariff. No universal net
speedup over old scalar Core, history-independent backing shrink, recursive
paid-job saving or kappa improvement follows.

## Calibration and limits

The first fixture is p4/P16/w32, five source rows with three interior rows,
two boundary rows, a skipped target index, B4, normalizer1/2 and a four-row
core crop. The PR5499 fixture's boundary diagonal is explicitly changed to
1/64 to amplify the inverse and make the final normalized output nonzero.
This is a supplied-factor ABI calibration, not a true global-Gaussian matrix
claim. Independent Fraction arithmetic supplies both the padded block
reference and a separate seven-stage second-pass oracle. The unchanged actual
source must execute four interior calls and the block solve, restore all
borrowed bytes/heads, and return the exact expected cropped complex values.

Controls distinguish changing the boundary solution, missing disk margin,
missing intermediate headroom and an actually rejected final disk value.
Finite agreement calibrates the written quantified proof; it is not a formal
or independent human proof of the inherited child machinery.

## Open next questions

- Bind the actual production coefficient producer to these stored-factor
  stability/headroom inequalities, including first-pass and block error.
- Decide the complete old-H local-defect allowance after original-S rounding,
  coefficient intervals and final normalization are all combined.
- Price a real seven-product or many-field supplier before replacing ordinary
  scalar arithmetic with an asymptotic boundary-solver claim.

Credit Jose Manuel/jmbarrancoml's physical Gaussian Core and supplied-factor
calibration, Chafik Boukhalfa's two-convolution inverse and retained runtime,
PR5483's transport and PR5499's two-column kernel. Retained helpers are pinned
and attributed in PREDECESSOR; immutable main inputs remain unchanged.
