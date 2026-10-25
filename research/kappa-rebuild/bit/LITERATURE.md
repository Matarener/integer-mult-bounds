# Literature mapped to the actual accounting problem

Research pass: 21 October 2026. These are primary papers and institutional
author copies. A paper's abstract notion of rank, space or circuit size does
not automatically price native recursive calls. The application statements
below are the current research team's deductions, with their finite tests
identified separately.

## 1. Reversible linear circuits and shared producer state

**K. N. Patel, I. L. Markov and J. P. Hayes, “Optimal synthesis of linear
reversible circuits” (2003 preprint; later journal version).**
[Primary preprint](https://arxiv.org/abs/quant-ph/0302002).
Their binary linear-circuit synthesis gives a systematic alternative to naive
elimination, with asymptotic `O(n^2/log n)` gate counts. The relevant import is
explicit reversible ADD/SWAP programs and shared intermediate linear forms.
It does not remove the native frame in which an addition must be delivered.

**A. Visconti, C. V. Schiavo and R. Peralta, “Improved Upper Bounds for the
Expected Circuit Complexity of Dense Systems of Linear Equations over GF(2).”**
[NIST author record](https://www.nist.gov/publications/improved-upper-bounds-expected-circuit-complexity-dense-systems-linear-equations-over),
[NIST paper](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=925478).
This is relevant to dense shared sums followed by a smaller number of row
edits. Our deferred-original construction keeps the sum itself alive until
all its readers and dirty pools finish, rather than recomputing it for every
consumer. The finite exact result is `DEFERRED-RECONSTRUCTION.json`.

**A. Parent, M. Roetteler and K. M. Svore, “Reversible circuit compilation
with space constraints” (2015).**
[Primary preprint](https://arxiv.org/abs/1510.00377).
The useful viewpoint is a joint time/space compilation problem, with explicit
uncomputation rather than a free cleanup assumption. Our version must also
respect a monotone subspace frame. The actual PR589 helper-pair census shows
why ordinary lifetime reuse is insufficient here: all five geometrically
eligible coalescings fail a subsequent exact primitive or response check.

## 2. Rectifier networks, coding width and consumer interfaces

**D. Chistikov, S. Iván, A. Lubiw and J. Shallit, “Fractional Coverings,
Greedy Coverings, and Rectifier Networks.”**
[Primary preprint](https://arxiv.org/abs/1509.07588),
[STACS 2017 publication](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2017.23).
This connects shared intermediate computation with combinatorial covering
objectives. It motivated comparing the entire consumer map with individual
reads and minimizing a source-neighborhood path cover. Rectifier size alone
does not pay arbitrary dirty baselines, inverse operations or frame motion.

**G. D. Forney Jr., “Minimal realizations of linear systems: The ‘shortest
basis’ approach” (2009; final revision 2010).**
[Primary shortest-basis paper](https://arxiv.org/html/0910.4336v3).
**N. Kashyap, “On Minimal Tree Realizations of Linear Codes” (2007).**
[Primary paper](https://arxiv.org/html/0711.1383v1).
The relevant question is the smallest state space needed across a specified
cut or decomposition, not just the rank of one arbitrary factorization.
Our actual nine-center consumer matrix has rank nine, as does the producer
response. This rejects a fixed-cut eight-signal carrier before its native
transport and cleanup bill is assessed. Moving the cut or changing the
consumer frame remains a different, open design choice.

## 3. FIR delay factorization and exact projector controllers

**Z. Doğanata, P. P. Vaidyanathan and T. Q. Nguyen, “General synthesis
procedures for FIR lossless transfer matrices, for perfect-reconstruction
multirate filter bank applications” (1988).**
[Caltech author copy](https://authors.library.caltech.edu/records/mv71c-vqj75),
[DOI](https://doi.org/10.1109/29.7544).
The paper constructs lossless FIR transfer matrices through a state-space
and cascaded-lattice approach. This suggested treating recursive stages as
formal transfer factors with a boundary basis, rather than preserving every
old intermediate frame alignment.

**H.-J. Park, “A Computational Theory of Laurent Polynomial Rings and
Multidimensional FIR Systems” (Berkeley thesis, 1995).**
[Institutional PDF](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1995/ERL-95-39.pdf).
Section 7.4 records the one-variable projector/delay factorization
`I-P+zP`; Theorem 7.4.8 gives the lossless factorization in its original
setting. The multivariable discussion also warns that factorization does
not become automatic merely by adding variables.

Our use is an exact algebraic analogue: transport each stage projector
through the constant scalar prefix, demand the appropriate commutation,
and check the complete coefficient identity. We import no SVD, unitary
rotation, irrational coefficient or automatically legal frame change.
This led to the successful p3 endpoint basis and the exact complex Laurent
lift, followed by the broader 4,096-mask and 123,904-choice negative rounds.
The same idea later proves the H controller factorization with genuinely
noncommuting stage symbols; the extra endpoint bill is then visible rather
than hidden by a commutative simplification.

## 4. Catalytic computing as an operator identity

**A. Vinciguerra, “An Operator Approach to Register Programs for Catalytic
Computing” (2026).**
[Primary paper](https://arxiv.org/abs/2609.18692),
[HTML](https://arxiv.org/html/2609.18692v1).
The paper represents register programs through derivation operators and
reduces catalytic restoration to an operator identity. Its polynomial
construction has an explicit characteristic restriction; it is not a
ready-made construction over the BIT word's `F2` scalar field.

The useful methodological import is exact restoration of every arbitrary
input, including the supposedly incidental work fields. Our controller
audits initialize all productive fields independently. The owned stream
used in the nine-row and three-row completions is separately declared and
never receives productive credit. A future embedded-query logger would
alter the helper interface; its baseline must be restored before that
helper is again counted as a clean independent transform output.

## 5. Matrix completion and low-rank feedback

**I. Baragaña and A. Roca, “Fixed rank perturbations of regular matrix
pencils” (2019).**
[Primary paper](https://arxiv.org/html/1907.10657v2).
The paper distinguishes fixed-rank from bounded-rank perturbation problems
and treats prescribed determinant/structure under field-size hypotheses.
It also points back to Thompson's rank-one perturbation work (1980),
Silva's prescribed-similarity work (1988), and Zaballa's pole assignment
with fixed-rank perturbations (1991). Those hypotheses must be checked
before using a theorem in the two-element scalar field.

**A. Amparan, I. Baragaña, S. Marcaida and A. Roca, “Row or column completion
of polynomial matrices of given degree” (2023; revised 2024).**
[Primary paper](https://arxiv.org/abs/2306.06104).
It studies completion with prescribed rows/columns and eigenstructure over
an arbitrary field. This is a better conceptual fit for our local problem
than unconstrained numerical low-rank approximation: only designated
output holes have the cheap rank-one delivery interface.

The actual BIT completion is proved directly, rather than inferred from
these general theorems. For `J=I+UV`, selecting an invertible `V_A` and
changing `U` to `U+E_A V_A^-1 VU` makes the defect square-zero. This gives
a nine-row involution. Dropping the unnecessary involution requirement
reveals `rank(J)=108`, so only three row changes are necessary and
sufficient for invertibility. The native three-gather word and both
orientation-dependent wrappers are replayed exactly. This is the latest
concrete literature-to-probe refinement, but the global head normalization
still consumes more rank than its complete target credit provides.

## Next research gate

The highest-value next probe is an **actual owner-aware completion and
controller designed together**. Its objective must be the total recursive
moment after all three interval head corrections, not a local correction
rank or an elegant scalar identity. Candidate routes include a shared
query state with a proven final erase, a changed center family with
compatible physical monodromies, or a mixed controller that removes some
endpoint products without losing independent output credit.

The first disproof gate should be exact noncommuting endpoint algebra;
the second should be actual rational port charts and arbitrary dirty
inputs; the third should be the full paid profile and strict child/job
separation. Only a survivor reaches the delayed-cover and outer-supplier
compiler. The stable p3 construction remains separate throughout.
