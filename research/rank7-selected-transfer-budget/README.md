# PR2979's allowance for a selected-contract transfer

No new kappa was obtained. The literal PR2979 histogram passes both primitive
moment tests at `a = 17/10000`, including the unchanged BIT bad-residue
surcharge. It can pay at most **395 additional rank-one children total** at
that rate. The 396th fails. One extra child per each of its 666 invocations
therefore fails this trial. At the limiting rate required to exceed the selected
kappa, the corresponding allowance is **730**. One extra child per invocation
remains numerically possible there. These are fixed-profile allowances, not
claims that any missing operation has that tariff or can be implemented.

This audit tests the complete-cost admission decision requested by the revision-6
family gate. It does not run another lowering census or reconstruct the already
covered joint-frame controls. The trial exponent is `kappa = 1697/1000000`.
`17/10017` is only the limiting `a/(1+a)` value, and is not a strict finite target.

## Source and complete ledger

Canonical base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The selected source-bound conditional kappa is
`836330098538459/500000000000000000`. Its complex primitive saving is
`67018507072324140917/40000000000000000000000`; BIT supports
`1733427039589844234749/1000000000000000000000000`. The complex side binds.
The cheap `scripts/research_baseline.py` control passed. It is not a circuit replay.

The changed candidate is Marius-Paul Dumitrean's PR2979 at
`be191346391661f4d35fc0d1508d0a6029572576`. Its 22 grouped endpoint lowerings,
five extra paired extractions and Jeremy Kothe's fourteen rewrites give the
source-declared per-call profile `{1:2445,2:706,3:232,4:108,5:18,8:8}`.
The complete T74 bill is
`{1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190}`,
with width 73, denominator `W=66304`, 666 invocations, and rank mass 4,816,512.
All 408 helper families and 91 private buffers remain charged. Nominal physical
stock is `66304+408+8+91+2=66813`. The stage-one local delta is
`-4H1+90H2-50H3-2H4-8H5`; the final source includes all later stages and idle work.

The evidence categories remain separate:

- The complete histogram, rank mass, primitive moments, strict extra-child
  thresholds and 47 selected outer arithmetic inequalities are proved by exact
  rational calculations here, conditional on the supplied finite bill.
- The native program, owner realization, dirty/private endpoints and finite
  invoice are checked by the source's unchanged complete replay. This reuses
  its implementations and is computational corroboration, not a new independent
  proof of all source validators. The finite invoice charges Horner coefficient
  work, each warp's complete monomial routing reserve, wrappers, actual private
  clears and storage, prefix/precision/tape and the halving guard.
- A uniform physical time coefficient for each changed bootstrap stage, its
  actual stock envelope and the implication from those finite receipts to the
  selected all-size caller remain unestablished in this audit. No value is
  assigned to those missing premises. Existing selected all-size/compiler,
  common-label/mutable-source, whole-call hosting, precision/tape, analytic and
  BIT H1-H5 assumptions remain explicit.

The actual fresh finite invoice has prefix 1475 bits within its 2048-bit reserve,
local primitive bound 9,292,791,433,960, physical row coefficient 19,545 below
20,161, and required C0 width 200,012 bits below 210,000. All nine finite guards
pass their independently recounted integer inequalities here. The source's
enlarged `PAYLOAD=2048` is a prefix reserve. The selected assembler
uses 512 in its fresh-coefficient cutoff expression. Neither this difference nor
a finite `C0=2^210000` precision guard proves that the required time coefficient
is too large or small. A source-bound compiler implication is needed. This is an
admission gap in this audit, not a counterexample to PR2979, a proof that its
modern release is false, or a new barrier to multiplication.

The selected outer arithmetic is reused under its original source hash.
Three bootstrap exponent steps suffice arithmetically for the strict trial;
all 47 rational inequalities pass. The recorded stage coefficients and stock
premises stay null. Passing those exponent inequalities does not complete the
physical induction. The newer PR1673/fine-padding outer is not adopted here.

## Exact allowance proof

For a paid profile `n_r`, let

`M(a) = sum_r n_r (r/73)^(1-a) / 66304`.

A new rank-one child has weight `w(a)=(1/73)^(1-a)/66304`.
For an integer number `t` of additional rank-one children, the bill passes
exactly when `t < (1-M(a))/w(a)`. The independent positive-series enclosures
certify `395 < (1-M(.0017))/w(.0017) < 396`. Both strict endpoint signs are
stored in RESULT.json. At `a=k_selected/(1-k_selected)`, the bounds lie strictly
between 730 and 731. Monotonicity of every positive child weight means that
731 such added children cannot improve the selected kappa through this retained
transfer with all other charges fixed. Passing with 730 is only a possible
allowance; a complete consumer and the analytic hypotheses still matter.

The logarithm uses 96 positive atanh terms after at most seven binary reductions.
The omitted tail is bounded by `2 z^193/(193(1-z^2))`, with `z<=1/3`.
The exponential uses degree 24 and tail
`(x^25/25!)/(1-x/26)`, valid for `0<=x<1/10`.
All arithmetic is rational. RESULT.json rounds outward to 160-bit dyadics.
No floating-point value selects an accepted endpoint. BIT includes its retained
`32*64*sum(n_r)/(10^16*28416) * 64^a` surcharge.

## Reproduction and limits

From the repository root, Python 3.12 and the standard library suffice:

```sh
python3 -B research/rank7-selected-transfer-budget/verify.py
python3 -O -W error -B research/rank7-selected-transfer-budget/verify.py
python3 -B scripts/research_package.py --package research/rank7-selected-transfer-budget
python3 -O -W error -B research/rank7-selected-transfer-budget/test_source_auth.py
```

The direct verifier is read-only and needs neither Git nor a network connection.
Its pinned inputs are listed in VERIFY.json and exported with the package.
It rejects Boolean counts, noncanonical/full-width ranks and zero counts.
The 395/396 and 730/731 signs are separate behavioral controls; the strict
trial and selected-rate one-per-invocation tests have opposite outcomes.
Typed canonical receipt comparison distinguishes Boolean and integer values.
The fixed SOURCES.json byte hash binds the exact path/usage inventory before
any executable source is consumed; its schema version must be an integer, so
Boolean true is rejected. The retained outer engine is compiled from the same
immutable bytes that passed authentication, without rereading its path. Three
actual CLI controls use writable private copies, inject a marker-writing outer
engine, and test usage reclassification, Boolean schema and changed executable
bytes. Every mutation rejects before its marker or exception executes. The
control script uses a private temporary directory by default and accepts an
existing scratch parent through --work. Source hashes authenticate bytes, not
mathematical admission.

The complete source replay passed with exit0 and is documented in REPLAY.json.
It freshly bootstrapped retained evidence, rebuilt both current native providers,
replayed the complete finite admission and the source modern release. Its retained
assembly discovery reports conditional kappa0.001726049584259595; its modern
release reports0.001729033982646513517717 minus the source slacks. Those are
source-replay results, not new kappa claims by this package. Actual raw receipts
are preserved in evidence/ and their source/native/admission/release bindings
are rechecked by the bounded verifier.
It is not rerun by the bounded registered hook. No selected cold replay, Lean,
Docker, human review or proof-kernel certification is claimed.

The family decision is **narrow, then stop** at this source-bound admission
question. No additional construction round is reserved.

## Open next questions

Pin the generic selected compiler/bootstrap statement that converts this exact
finite native invoice into a cutoff-independent time bound and actual reserve
for the changed caller. State the coefficient function, all width domains and
stock restoration hypotheses, then bind them to this source. If the missing
module adds recursive children, first compare its literal profile against the
395-child trial allowance and 730-child selected threshold. Physical linear
work has a different tariff and must not be silently converted to free work or
to a rank-one child. No further lowering or packing search is justified solely
by the passing numerical relaxation.

## Credit and overlap

Marius-Paul Dumitrean supplied PR2979 and PR2942. Jeremy Kothe supplied the
frame/cleanup compiler and PR2957 rewrites; Mason Hale and Jeremy Diviney
supplied the paired-extraction chain. Dugongue, Yiyang Lu, Tekalign, icekylinx,
Sagar Thakrar, Ross Richardson and the native/geometry/owner lineage retain
their credit. The BIT supplier is DreamingOfClouds's PR589 on eumemic's base.
Rohan Arun's PR1094 and its credited predecessors supply the selected result.
Nick Petalas contributes this source-bound allowance and admission-boundary audit.
New work is Apache-2.0; retained notices are unchanged.

PR2993/3236/3237/3285 already cover the group controls, complete local native
paths or packing-cap comparisons. PR3238/3245 cover private-return obligations.
They are credited evidence, not rediscovered results. Current exact heads were
checked after the shared intake. Its coverage is 247 open PRs at 22:04:28 UTC,
2170 Discussion records at 22:05:00 UTC and older 2630 closed PRs at 20:44:55 UTC
on October 17, 2026. Newly closed non-prior-batch bodies, arbitrary diffs and
unpublished work are outside complete coverage. No search match is not proof
of novelty.

## Scoped review

The designated review passed at scientific commit `3b703079ffb97b1347ac142fcae8e218365daac1` plus authentication fix `4f5b5ce946cf46afcdf1567a70aae305ee70e1e4`. [REVIEW.json](REVIEW.json) retains the final receipt verbatim (SHA256 `17a9e5b6d368affc52d43c4c5e5ce12c0e2cffd3d6437f527dd443cf873dc3fb`). [REVIEW-ROUND1.json](REVIEW-ROUND1.json) preserves the original executable-input usage finding. The fix binds exact manifest bytes and executes the authenticated bytes; the original bypass now rejects before execution. Arithmetic, source evidence and the no-new-kappa scope are unchanged. This is an internal scoped review, with inherited all-size and compiler premises unproved here.
