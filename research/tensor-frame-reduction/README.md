# Tensor frame reduction under fixed boundaries

Coupling tensor copies cannot improve the optimum recursive rank moment
of the fixed contact-graph model defined in [PROOF.md](PROOF.md). This
holds for arbitrary internal Clifford frames, every positive tensor width,
and every power tariff r^t with 0<t<=1. Public input and output spaces,
including every productive helper boundary, must stay fixed and repeated
across copies. One resulting assignment in the original dimension has
no larger normalized paid moment.

**No new kappa is claimed.** This does not prove that the current P104
assignment is optimal. It reduces a proposed wider search to the original
dimension. Changed scalar words and productive boundaries remain outside
the result. Native adapters, phases, caller work, precision, the compiler
and outer transfer are not verified or assigned zero cost.

The new step uses a coordinate flag to split each projected space, then
uses concavity to choose one copy for the complete graph. The Clifford
projection inequality is credited to Cinna Davis's
[PR5140](https://github.com/CrocSwap/integer-mult-bounds/pull/5140), at
`1d1b593168a36ee524300752a5e33f6cd7a08314`. It is not claimed as new.
The argument uses standard subspace and concavity facts; no claim of
literature priority is made.

## Verification

Use Python 3.12 with the standard library:

```sh
python3 -I -B research/tensor-frame-reduction/verify.py
python3 -I -O -B research/tensor-frame-reduction/verify.py
python3 -B scripts/research_package.py --package research/tensor-frame-reduction
```

The marker is `PASS_TENSOR_FRAME_REDUCTION`. [RESULT.json](RESULT.json)
records the exact finite coverage and hypothesis controls. The written
dimension proof gives the unbounded statement. The replay has no optimizer,
network access, Git dependency or imported predecessor code. Normal replay
only reads files; `--write` explicitly regenerates the local receipt.

## Source context and scope

Base: canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority
revision 8. The selected .003125804 frontier is unchanged. The motivating
source is [PR6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167),
at `564a076b113621a93edc4e39968ee4e4a8c9caf0`; no claim about its full
retiming optimum or scientific admission follows. Its complete conditional
.003128645 remains the comparison for the donor's unmet 1% improvement
request. [PR6169](https://github.com/CrocSwap/integer-mult-bounds/pull/6169)
is the separate published scalar resynthesis result, with no invoice gain.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19209322)
records the overlap check. PR5140 proves a source-specific owned-wire floor.
This package adds a graph-wide tensor reduction with fixed target credits;
it does not repeat that floor. The live signed-stage/query work in
Discussion5593 is separate. Independent review remains open.

## Open next questions

- Can an independent reviewer check the coordinate-flag inequality, the
  common-copy choice and the fixed-credit condition? Start with proof
  sections 3 and 4 and the controls. No technical input is missing.
- Can a changed productive boundary or scalar circuit yield a profitable
  complete caller? This result leaves those changes open. Start with one
  explicit changed boundary and charge its whole signed invoice. No such
  construction is supplied here.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Cinna Davis / 1337isnot1337 retains the projection inequality
and PR5140 credit, including the prior Matarener, Dugongue and Cao Yifan
lineage. icekylinx retains the arbitrary-subspace frame construction in
`notes/general-clifford-frames.tex`. The P104, native, helper, caller and
compiler authors retain their source results. No predecessor code is copied.
