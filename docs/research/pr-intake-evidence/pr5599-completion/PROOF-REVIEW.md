# P104 helper-subspace construction: application review

This review concerns PR5599 at `09dd0965711ca7eeb169057a420abab1c9052137`,
claiming κ = 62009/20000000 = 0.00310045. Execution and admission status are
recorded separately in VALIDATION.json and INTEGRATION.json. This text does
not turn a partial or failed replay into a pass.

**Decision: the conditional κ = 0.00310045 passes this maintainer review under the five retained assumptions.** The Linux run at `09062e91a942f205a529779b74c13c412afdb483` completed primary, independent positive-control, independent candidate and optimized primary replays. The normal and optimized scientific outputs agree exactly. The original caller positive control agrees byte-for-byte with its frozen output. The candidate checks 316 distinct signed-Pauli/independent phase anchors and 9,720 fresh helpers; its ordinary pass bound 124,625,152 is below the retained 184,647,552 allowance. The primary independently covers paid native maps; the caller's scoped `paid_native_maps_replayed: false` flag remains intact.

Elapsed times were 180.86, 27.34, 27.34 and 108.35 seconds respectively. Peak sampled descendant RSS was 487,100 KiB, below the 1 GiB cap. This is a successful Linux replay, not an extrapolation from the earlier Mac timeout. The 600-second Mac stop and the later intentional Linux handoff remain preserved. No Lean, Docker or unrelated historical suite was run. Discovery-screen/global-optimality claims are not selected obligations or separately certified here.

## Independent inputs, cuts and target credit

The scalar proof uses a helper-only prefix functional c and suffix direction d,
and cut vectors a,b with aP=c, Sb=d and ab=cd=1. The helper group shares both
boundary charts, while a,b and the pivot share the cut chart. There are explicit
invertible dyadic scalar bases G,J with e_p^T G=c, Gd=e_p, e_p^T J=a and Jb=e_p.
Apply G^-1 before the word. At the cut, J exposes the original independent
pivot input. Retain it as an early output, substitute a new independent input
in its place for J^-1 and the suffix, and apply G at the final helper chart.
The resulting output change is Gd(z-ch)=e_p(z-ch). All other helper outputs
and all main outputs are unchanged. This preserves two distinct independent
inputs, rather than crediting two outputs derived from one input.

The source emits the bases as common-chart ADD and dyadic-unit SCALE events,
including inverses; it does not assign a dense linear transformation zero cost.
Every basis coefficient and owned-role renaming is checked by full exact
replay after each split. The dense reverse interpreter checks all 756 squared
scalar endpoint coefficients separately. Ideal owned initialization/erasure
is explicit and has no productive credit. There are 748 public inputs,
including 540 helpers, and eight owned lifetime labels with one live at a time.
The new early outputs remain live public fields until the complete caller ends.

Six splits replace H9 by H4+H5, five by H2+H7, and two by H1+H8. The target
change is 2H1+5H2+6H4+6H5+5H7+2H8−13H9, with zero rank-mass change. Strict
concavity gives a positive target-moment gain for 0<t<1; paid Gaussian
occurrences are unchanged. The 342 additional scalar events are charged.

## Native and complete caller contract

A common-chart scalar operation commutes with the chart operator. Thus the
scalar induction extends factorwise to every positive column multiplicity,
with scalar coefficients outside tensor powers. The submitted native checker
compares signed Pauli images and absolute phases for all distinct paid changes,
helper endpoints and main adapters; unsigned tableaux alone would not suffice.
The universal implementation theorem remains one of the explicit assumptions.

For a helper endpoint U=M_left G_r M_right, applying M_right^-1 before its own
fresh call and M_left^-1 after it delivers G_r on an arbitrary independent
input. Both monomial normalizers are ordinary work. This permits nested
noncanonical start and finish charts; no clean-helper assumption is introduced.
It is the P104 all-input contract, not the selected neutral caller's narrower
canonical-start convention. The free-endpoint discussion in PR5567 identified
this distinction; the adapted PR5550 checker independently checks the actual
new normalizers and input allocation.

All eighteen local invocations are forward. The sixteen backward main
interfaces are implemented by signed exchanges and Q^2 translations around a
forward call. Q^2 is the native translation with phase +1 at every width;
scalar signs stay outside tensor powers. The wrapper touches only the main
pair. It does not transpose COPY or CLEAR and does not touch returned helpers.
The Laurent identity retains Q as a formal invertible variable. Actual
265-axis routes, their inverses, spectator support and phase corrections are
checked separately. Whole main targets and idles are normalized as whole jobs.

The independent caller adaptation changes input paths and inventory constants,
recounts scalar work, and leaves the phase/chronology/layout equations intact.
It must reproduce PR5550's complete original output byte-for-byte before its
candidate result is accepted. Candidate ownership allocates 18*540=9,720 fresh
helpers disjointly from 3,328 main fields; all 13,048 productive fields and the
owned query slot are counted. Checks include alias, phase, missing-translation,
missing-idle and query-lifetime fault controls.

## Full invoice and compiler funding

The complete bill contains 66,726 paid calls, rank mass 241,268, against
13,048 productive fields of rank mass 242,028: surplus 760. It includes all
thin queries and 3,120 whole idle jobs. A second count from path lengths 7 and
8 agrees with the emitted controller. Largest target rank is 145 and paid
rank 72. The local contact improvements are consumed as complete words;
incorrect historical predecessor headline decimals are not admission inputs.

The raw crossing is enclosed by exact rational interval engines in
(0.00310045630724, 0.00310045630725). The claim uses κ=0.00310045 and tests at
0.0031004505, strictly below that crossing. This is a ceiling for this invoice,
not a general optimum. At the tested point, the paid/target ratio is below
0.999999994094861, the higher-moment tail ratio below 0.967537821927969, and
the completion ratio below 0.972208404163140. Crucially, the last uses the new
13,048-field count. Both tails are below 39/40; (39/40)^128<1/16 and eight
blocks give the retained 2^-32 bound. Power 1024, cutoff 17, floor 18, tail
offset 1/5 and reserve 10^-10 yield normalized cost
5242880004882813/5242880536870912<1. The old cutoff fails its explicit control.

Compiler logarithm power 1024 replaces 1000. With complement factor 63/64,
all initial-range, shifted-exit and complement-capacity inequalities are
checked. The explicit height is H=707182000000000, N=2^H. The preceding height
grid point fails the defining integer inequality. This does not prove a
maximal κ. All 54 strict and four functional outer predicates must pass.
The admitted ordinary BIT saving remains 17/5000, above the new complex
requirement, with its unchanged source-bound supplier and stock allowance.

## Precision, storage and the inherited application

Do not reuse PR5557's sharper numerical cut norms for this changed word.
A coarse bound suffices under the retained precision/tape contract. The new
word checks fewer than 26,000 events, dyadic coefficients with 1+|q|<2^16,
local paid-rank mass 6,014, scalar allowance 220,232 and route allowance
5,183,000. Complete ordinary allowance is below 184,647,552<10^9. The
independent caller recounts its finite address/phase/scalar passes against that
allowance. These are descriptor-pass bounds, not constant arbitrary-width tape
instruction counts; the retained fixed-map implementation supplies the width
and precision factors.

For the max coordinate norm over all fields, scalar operations have elementary
doubling/addition bounds, monomial routes have norm one, and a rank-r Gaussian
has row-norm bound at most 2^(rf). COPY can be implemented as ADD into an ideal
owned zero and must retain injected residuals in that implementation. The same
ADD majorant bounds those residuals; no argument discards them merely because
the ideal owned value is zero. INIT/CLEAR obey the retained owned-erasure
contract. Taking every elementary norm majorant at least one bounds every
prefix, suffix and contiguous interval, not just the final exact operator.
A conservative complete envelope is 2^(10^9+241268f), with additional fixed
local arithmetic guards from the retained realization. Summing propagated
local defects against that envelope supplies a constructive precision choice.
Dyadic denominator growth is bounded by the same finite scalar and butterfly
counts. This uses no dimension-free l2-to-coordinate conversion.

Storage must use the new public inventory and explicit owned/movement scratch,
not the old helper count. The field-ID join checks productive/owned separation.
The large fixed constants and finite template size are absorbed at fresh outer
input thresholds using the strict exponent gaps. They are not assumed absorbed
at the fixed carrier N. This is an application of the inherited framework,
not a new proof of its uniform closure, tape or analytic hypotheses.

## Scope and credit

Exactly five preceding assumptions remain: native implementation at all
column multiplicities; owned allocation/erasure; uniform mixed-target compiler
closure; precision and fixed-tape execution; analytic decomposition and exact
integer recovery. The full uniform word and rounded multiplier are not
materialized. No complete Lean theorem or independent human acceptance is
claimed. Successful finite replays plus this application review support a
conditional admission only; publication is recorded separately.

Ali Romman supplied the helper-subspace construction, complete assembly and
all-forward P104 caller; Pierre-Loic Doulcet / hexapode supplied PR5565's
commuting-contact improvement. GamingPuzzled supplied PR5569's priced handoff,
DreamingOfClouds the endpoint retiming, and thu-nmrc the coupled contacts.
Chris R / Clear1nsight supplied the independent caller and native audit tools;
Matarener clarified and audited the endpoint contract. Retain David Arias,
Cinna Davis, Gareth Davidson, Cao Yifan, zxv, Jacob Alan Sussman and the complete
credited native, BIT, compiler, geometry and analytic lineage. Prepared by
Douglas Colkitt with substantial OpenAI Codex assistance, Apache-2.0.
