# Literature-to-probe map

Research date: 2026-10-21. Substantial OpenAI assistance. Apache-2.0 for this
note and the new code. Linked papers retain their own copyright/licenses.
The research uses the primary papers or authors' technical reports below.
An analogy is not treated as an admitted circuit or a paid-call saving.

## 1. Mixed production and whole-job amortization: integrated

**Jacob Alan Sussman, mixed-target recursion, PR4268 and Theorem 1G.**

- [Repository PR4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268)
- [Pinned theorem source](https://github.com/jacobalansussman/wht-power-saving-lean/blob/563b4e6e913625637f36ba7869bf5fcd0dd4975a/research/record-track/proofs/theorem-1g.md)
- Source snapshot: `sources/Sussman-563b4e6/`, with Apache-2.0 LICENSE and NOTICE.

The useful idea is a simultaneous recursion producing unequal target
sizes, with strict largest-child/smallest-target separation. Its integer
Pascal class flow specifies how target roles meet paid demands. The PR's
own DFT constants do not automatically establish a new integer-multiplication
exponent. We used the theorem's actual flow, priced our own independent
helpers and cut-prefix targets, and added whole-array batch clearing plus
a direct paid-leaf induction. This closes a different interface from the
original complete-time statement: one finite native uniform supplier is
compiled before the retained fixed-tape recursion is applied.

**Robert Robere and Jeroen Zuiddam (2021), _Amortized Circuit Complexity,
Formal Complexity Measures, and Catalytic Algorithms_.**

- [Primary ECCC paper](https://eccc.weizmann.ac.il/report/2021/035/download)

The paper connects production/consumption inequalities, formal complexity
measures and LP duality. Its main amortized Boolean setting repeats outputs
on the same input. Our productive transform jobs have distinct arbitrary
input arrays, so that theorem does not grant our batching or output credit.
Its contribution to the search was methodological: put every generated
and consumed job in one ledger, find the binding resource prices, and then
realize the resulting integer schedule rather than interpreting an LP as
an executable program. The concrete realization here is the preceding
mixed-job flow and exact owner packing.

**Observed outcome.** Actual width 6–9 helper jobs, literal prefix cuts, and
the p3 output contract produce the retained root .002305090194876....
Unsplit bills with a child larger than the smallest target were rejected.
The same discipline caught uncredited owned storage and unequal whole-batch
sizes before applying the outer theorem.

## 2. Lifting and filter-bank factorization: productive broader probes

**Ingrid Daubechies and Wim Sweldens (1998), _Factoring Wavelet Transforms
into Lifting Steps_.**

- [Author page and primary PDF](https://9p.io/who/wim/papers/factor/index.html)
- [PDF](https://9p.io/who/wim/papers/factor/factor.pdf)

The paper factors finite-filter two-band transforms into elementary Laurent
matrix steps, including nonunitary biorthogonal transforms. This directly
suggested treating native forward/backward words as lifting steps and
looking at the whole six-bank transfer matrix. It does not promise dyadic
coefficients, legal frame contacts or cheap preparation/cleanup for our
model. Our application is an exact coefficient-level controller check;
the emitted adapters use only integral ADDs, signed swaps and negations.

**Hyung-Ju Park (1995), _A Computational Theory of Laurent Polynomial Rings
and Multidimensional FIR Systems_, UCB/ERL M95/39.**

- [Primary university technical report](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1995/ERL-95-39.pdf)

The Laurent-ring framework and the univariate rank-one delay factorization
in Section 7.4 give a precise model for elementary stage factors
`I-P+zP`. We adapted that form to rational oblique idempotents, preserving
the actual coefficient ring rather than inserting orthogonal rotations.
The multivariate discussion also warns against assuming every plausible
factorization exists. In our setting the transported stage projectors were
computed and checked exactly; the paper's existence results are not used
to waive those checks.

**Observed outcome.** The companion controller work emits exact integral
Laurent factorizations for p1–p6. Arbitrary per-stage extra field subsets
produce 123904 commuting p3 choices; their best all-fresh geometry is still
the retained 25/25/57 family. All 64 asymmetric p3 window survivors and the
p4–p6 menus were separately priced. These are broader scoped screens than
changing one local basis. The negative result directs the next architecture
search toward a changed scalar controller or a different query contract.

The same p3 factorization was then checked over a free noncommutative ring
in `aggregate_h_probe.py`: no commuting-stage or involution shortcut is
needed for its six diagonal interval words.

## 3. Catalytic restoration and in-place accumulation: useful interface ideas

**Jean-Guillaume Dumas and Bruno Grenet (2024 version), _In-place
accumulation of fast multiplication formulae_.**

- [Primary arXiv version2307.12712v3](https://arxiv.org/html/2307.12712v3)

The paper permits temporary input changes followed by exact restoration
and constructs in-place accumulation from fast multiplication formulae.
Its elementary accumulator trick suggested using completed output arrays
as arbitrary dirty storage instead of requiring blank auxiliary arrays.
In this repository every such use still needs a physical contact map and
its reverse, and all preparation and cleanup are charged. The independent
native reconstruction supplies those checks; the paper does not establish
the native frame interface by itself.

**Antoine Vinciguerra (2026), _An Operator Approach to Register Programs
for Catalytic Computing_.**

- [Primary arXiv version2609.18692v1](https://arxiv.org/html/2609.18692v1)

The paper expresses register restoration as an operator identity and gives
a four-access polynomial construction with fewer registers, together with
a passive-output access lower bound. This supports checking whole arbitrary
register columns instead of only zero-initialized trajectories. Its
polynomial degree, passive-output and field assumptions differ from our
linear Gaussian jobs. Matrix lifting and coefficient divisions do not
automatically preserve the dyadic native model. The applicable probe is
the explicit reversible logger/exchange contract, followed by a complete
consumer check, not a direct import of its four-access count.

**Observed outcome.** The native full-identity reconstruction restores all
arbitrary helper inputs without an external cleanup bank. A separate
embedded logger carries a precise eight-query defect in existing helper
outputs; these outputs cannot be credited as clean independent jobs until
the defect is erased. A repeated same-future-query exchange restores its
dirty bank but, without additional work, leaves a main-output dependency.
The finite compiler now explicitly permits a copied parent center as a
child's arbitrary-input slot while excluding it from independent source
credit. New child centers have distinct lifetimes.

## 4. Causal network coding: motivation, not an arithmetic transplant

**Mark Braverman and Zhongtian He (2026), _The Multiple Unicast Conjecture
is False_.**

- [Primary arXiv version2610.10108v1](https://arxiv.org/html/2610.10108v1)

The preprint constructs a causal deterministic code over F9 from a geometric
incidence graph, separating coding from routing in its stated network
model. The relevant methodological point is that a feasible algebraic
code needs an actual processing order and local implementation. Its
characteristic-three local rules and network capacities do not translate
to dyadic Gaussian gates. We used it to motivate timed, operator-valued
query carriers and to insist on causal read/write schedules. No throughput
factor from that paper appears in our kappa invoice.

**Observed outcome.** The actual per-port owner matrices and phases remain
in the timed-query tests. A wrong future-query swap gives a concrete
physical counterexample. The current best open question is whether the
rank-eight query geometry admits a whole-controller coded correction
below 228.0645844 cost at C=.004, with all helper defects restored.

## 5. Noncommutative realization: one additional joint-boundary gate

**Christophe Reutenauer (FPSAC1994), _A Survey on Noncommutative Rational
Series_.**

- [Primary proceedings PDF](https://fpsac-archive.github.io/FPSAC94/ARTICLES/45Reutenauer.pdf)
- [Berstel–Reutenauer, minimization chapter](https://www.cambridge.org/core/books/abs/noncommutative-rational-series-with-applications/minimization/ACD53CC08C3CB9451564D3488D24FE22)

The survey relates finite linear representations to coefficient/Hankel
rank. That suggested testing the dimension of the whole boundary's
coefficient space rather than counting each word separately. Our resulting
two-query gate has an elementary proof, recorded directly in
`joint_boundary_probe.py`; it does not rely on a black-box minimal-realization
theorem over the repository's ring.

For the three interval words K_a, K_b and K_b H3 K_a, the coefficients of
`Q K Q` have a 3×3 identity minor across the independent streams. In the
stated universal model, two complete-bank Q events surrounded by arbitrary
Q-free polynomial mixing have coefficient-span at most 1. Three extra
Q-free positive streams do not fix this mismatch. The gate rejects only
that particular universal portal; it does not rule out actual native
relations, partial-bank query coding or new stateful contracts.

An independent physical sector test rejects a second shortcut: fresh-axis
H owners do not supply an old monodromy's inverse. Exact overlap accounting
also records that repeating an old Gaussian support squares its axes to
free phases, rather than producing two fresh output credits on one array.

## 6. Decision after these rounds

Integrate the full-identity mixed p3 construction and its audited finite
transfer. Preserve H as a higher-payoff branch with the actual phase lift,
completion families and explicit complete-cost budget. The companion BIT
minimum-completion probe reinforces the broader lifting lesson: paired
forward/reverse wrappers need an invertible local operator, not necessarily
an involution. It achieves a smaller local bill, while leaving the same
global monodromy interface open. A worthwhile next
probe must supply one of the following concrete objects:

1. A legal geometry-aware query carrier for the joint boundary, including
   every original input, helper defect and phase, at cost below the budget.
2. A new scalar controller whose H endpoint has fewer independent negative
   interval jobs while preserving enough productive rank credit.
3. A typed recursive contract with a costed inverse-state adapter on fresh
   axes and an exact whole-job source/complement schedule.

The searches above explain why a same-chart cancellation, an unweighted
rank count, a scalar LP alone, or a generic coding analogy is not yet that
object. They also identify exactly where the retained construction already
improves the complete recursive bill.
