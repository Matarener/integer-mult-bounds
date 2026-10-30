# Independent AI review and reproducibility scope

Two separate GPT-6 Astra Ultra reviewers examined the proposed theorem and
code on 2026-10-29. They did not write the original proof or solver. A third
reviewer checked upstream overlap and attribution. This is independent AI
review, not independent human review or formal mathematical acceptance.

## Findings and correction

Neither mathematical reviewer found a defect in the stated minimal-alphabet
theorem, its strict discriminant domination, all-profile reduction, common
padding, optimizer ties or exact-search completeness.

The proof/code reviewer found one conditional source-integrity weakness:
Python's `-B` disables bytecode writes but can still load a matching cached
`.pyc`. The original `verify.py` imported `optimum.py` with SourceFileLoader,
then hashed source text. In a scratch copy, an inert cached marker executed
instead of the source marker despite `-B`. The original package had no such
cache, and the recorded scientific replays were not affected.

The prepared package corrects this by capturing `optimum.py` bytes, compiling
those exact bytes with `dont_inherit=True`, and hashing those same bytes in the
receipt. Both independent checker scripts use that approach too. This binds
the executed subject module to the receipt; it does not make the filesystem
an atomic snapshot or formally certify Python execution.

The adversarial reviewer supplied the endpoint-coordinate proof now included
in PROOF.md: D=9k+6v+4ell with k,ell>=1 and v>=3. It proves the threshold 31
and uniqueness through 34 algebraically, removing the finite base-case table
from the theorem's logical dependencies. The polynomial (5,15,11) itself was
already a semantic control in PR6153; its prior existence is credited.

## Independent domains

`independent_check.py` starts from all bounded signed quartics with Q(1)=Q(2)=0,
before assuming alternating signs or using the author's quadratic eligibility
predicate. Exact polynomial division and a generic rational Sturm sequence
test the interior-root condition. At h=1 and per-profile N<=150 it checks
13,590,150 coefficient triples, 323,071 bounded endpoint polynomials, ten
eligible polynomials and all 151 budget prefixes.

Its separate Farey-neighbor root census compares the exact ratio of rational
roots rather than the author's discriminant score, square test or divisor
routine. It covers all 1,867 discriminant-one residuals through L=4096 and
all 4,062 budgets 35..4096, including 1,211 budgets with multiple optima.
Primitive rational linear factors have determinant one when the quadratic
discriminant is one; this supplies the census parametrization. The written
domination lemma is still required to exclude other discriminants beyond
the signed-quartic census. It also rejects 741 malformed certificates, checks
ten valid controls and six endpoint/repeated-root/rational/irrational fixtures.

`endpoint_coordinate_check.py` independently uses the increasing change of
variable y=(x-1)/(2-x) and positive-root conditions in y. Its weighted-cost
census through L=512 checks 98,182 positive coordinate triples, 31,238 eligible
residuals, all 513 budget prefixes, and all tie lists, with four excluded
boundary/sign controls. It imports neither the author's eligibility predicate
nor its certificate verifier. It calls the solver only to compare answers.

Both scripts are standard-library-only, bounded, stdout-only and reproducible
from the package. Their default domains are registered in VERIFY.json in
normal and optimized modes. Acceptance checks remain active under `-O`.

## Overlap and attribution

PR6153's [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19246930)
expressly excludes the general finite-budget optimum. Its
[completion handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19247488)
releases that scope and leaves the exact optimum outside its attainment set open.
This package supplies the discriminant domination and all-budget optimization
procedure; it does not claim PR6139's bound or PR6153's equality classification.

The bounded upstream audit inspected current main, topical all-state PR searches,
Discussion6052, the latest 150 handoff comments and latest 30 mechanism comments.
It found no competing same-instance result or later matching active claim in
those inspected records. Uninspected older comments and the broader literature
remain outside that coverage; no absolute novelty claim is made.

## Remaining obligations

Finite corroboration and separate AI reviews do not prove the uniform theorem
in a formal kernel. The same model family and shared predecessor mathematics
can produce common errors. Human review should focus on the all-profile
reduction, strict domination inequality and exact-search completeness.

The reference implementation's finite caps are separate from the uniform
mathematical statement. No arbitrary-rank, larger-support, physical-supplier,
native, compiler, restoration, stock, precision/tape or analytic-recovery
obligation is discharged. No selected cold replay or new kappa is claimed.

Substantial OpenAI Codex assistance throughout. Apache-2.0. Predecessor and
classical attribution is retained in PROOF.md and SOURCES.json.
