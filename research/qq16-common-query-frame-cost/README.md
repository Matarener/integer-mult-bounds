# Common-frame normalization gate for the QQ16 ordered residual

A single shared query-frame change cannot reduce the native phase-normalization
moment of PR4003's 104 separately normalized owner branches. The result holds
for **every positive λ**, including input frames coupling different planes,
and for `0≤a≤10/13`. The optimal normalization-only bill is the unchanged
`104 λ^(1-a)`; every nonzero common binary polar perturbation is strictly worse.

The new ingredient is an exact partition of the 104 pulled-back defect directions
into **12 independent groups**. It has the minimum possible group count, since
their span has rank9. The partition controls image intersections for any
73λ-dimensional input-frame change, yielding

    Σ branch defect ranks ≥ 104λ + 80 rank(Δ).

Concavity converts this to the moment bound. [PROOF.md](PROOF.md) gives the
quantified argument. No frame census over the 2^2701 base polar matrices, or
over lifted frames, is needed. The stronger λ=1 bound for `0≤a≤1/2` is >144
phase-moment units for a nonzero change, versus baseline104.

This is a **scoped negative result** about separately normalized one-owner-route
branches with a fixed F16 output frame and a specified formal phase-normalizer
tariff. The104 source owner routes are fixed; a different owner decomposition
is outside the result. The tariff is an accounting model, not a wall-clock or
bit/tape lower bound.
It does not exclude shared/joint normalizations, changed output frames/producers,
paid address-valued scans or other native alphabets. It is not a native-call
lower bound for every circuit, a physical supplier admission, or a new κ.
Actual routing, query retention, helpers, restoration, precision, control and
consumer charges remain unresolved; they are granted zero only in the favorable
lower-bound test, never asserted free in an implementation.

## Reproduce

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`; Python3.12, standard library.

```sh
python3.12 scripts/research_package.py --package research/qq16-common-query-frame-cost
```

Expected primary result:
`PASS_QQ16_COMMON_QUERY_FRAME_COST ports=104 groups=12 all_lambda_frame_gate=PASS`.
The hook also runs an independent source/character check, the exact bounded
partition reconstruction and behavioral controls. All canonical runtime inputs
are in SOURCES.json and declared in VERIFY.json; no pending-PR code or network
source is imported. A direct `verify.py` replay works from the repository's
committed Git-free export with those inputs.

[CERTIFICATE.json](CERTIFICATE.json) records every actual normal, pulled-back
direction, owner character image, affine shift and complete source pins.
[PARTITION.json](PARTITION.json) records all 12 groups and the bounded construction:
OS assignment seed47, balanced greedy partition with capacity9, stopping at the
first complete partition or 1,000 shuffled restarts. It succeeded on restart1.
This was a positive certificate construction, not exhaustive partition coverage;
optimality of the group count follows from the rank9 capacity bound and witness.
Run `find_partition.py --check` to reproduce that exact construction.

The independent checker executes no predecessor code. It reads the original
recipe, uses row matrices and direct character polarization at 2,701 points per
port, and verifies the independent groups using a separate elimination routine.
The primary checker authenticates every retained input before inherited source
execution, checks complete Z4 frame identities, and validates 15,834 small
rank-one cases, 4,164 symmetric matrix pairs and a nonuniform λ=2 plane-mixing
fixture. These finite guards accompany the written all-parameter proof; they
are not formal verification of that proof or of integer multiplication.

## Open next questions

The useful next circuit changes the branch independence, output frame or
producer contract, then prices its native phases and retained queries at the
actual consumer boundary. Another common-input-frame search under this same
contract cannot reduce the normalization moment. TASK.json records the scoped
next questions and first experiments. The source's all-size/compiler and actual
physical execution correspondence remain inherited rather than supplied here.

## Credit and scope provenance

Tekalign (`tekuuu`), with substantial OpenAI Codex assistance in the rank argument,
source analysis, code and verification. Apache-2.0; predecessors and notices unchanged.

The exact ordered residual and failed scalar bypass are Chris R / Clear1nsight's
[PR4003](https://github.com/CrocSwap/integer-mult-bounds/pull/4003), head
`309189077d0f760248bbdaadab42ecbff4f3ea2d`. Its prefix/surjection proof is inherited,
not independently rerun or imported here. The physical data are independently
regenerated from canonical ywz65 PR2707 / Arham Tahir PR2681 sources, retaining
Ali Romman's QQ16/native and full compiler/geometry lineage. PR3985 at
`400df7fca8f60c19bf163c77564fe3fbe9154b04` supplies the comparison with104 removed
normalizers; its executable is not imported. PR4015's streamed query-bank lifetime
is a distinct construction. Ross Richardson's PR4023 paid-scan example is a
related scope warning, not a dependency of this phase-matrix argument.
