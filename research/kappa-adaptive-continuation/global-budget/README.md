# Global budget continuation

This directory contains independent physical-allocation, exact-price and
packing-ceiling checks for the adaptive continuation. The main constructive
result is a **new complete native profile on an attained physical owner fill**:

\[
a\in[0.001730739780298357321619,
      0.001730739780298357321620].
\]

Both modern outer arithmetic engines yield

\[
\kappa=0.001730739780298357321619-10^{-46}-10^{-70}.
\]

The complete supplier release is run separately by the parent continuation.
The first full attempt encountered a confirmed operating-system out-of-memory
kill in the existing controller audit; that attempt did not pass admission.
A source-bound runtime repair and fresh full attempt are tracked in the parent
directory. The finite owner, native and outer arithmetic receipts here do not
substitute for that final gate.

## What changed

There are two independent improvements over the attached PR3734 result.

| Component | Complete root lower endpoint | Gain over preceding row |
|---|---:|---:|
| Attached PR3734 native word and allocation | 0.001730448360207635461740 | — |
| Same word; adopted PR3815 clock and fill | 0.001730578437266246818740 | 0.000000130077058611357000 |
| New receiver-sharing word; same PR3815 fill | 0.001730739780298357321619 | 0.000000161343032110502879 |

The first improvement adopts existing upstream work. [PR3815], by Erwan
Secousses / ChaloupeMusic, changes one clock rule and provides a literal T360
fill and an exact global packing dual. [PR3802], by hexapode, attained the same
value first at T385. This continuation does not claim either upstream value as
new work. The fetched PR3815 source is pinned at
`77ffbf287b6ca198b4a31e3835db3bae60718b93`.

The second improvement is this continuation's native receiver-sharing edit,
constructed and checked in `../native-alternatives/`. It replaces two uses of
borrowed helper 544 by a three-addition identity on receivers 672 and 676. Exact
frame optimization combines one rank 1 and one rank 2 child into one rank 3 child:

\[
\Delta n_1=-1,\qquad \Delta n_2=-1,\qquad \Delta n_3=+1
\]

per complete local call. The original 408 ordered helper widths, all data and
helper endpoint subspaces, both providers, and all 91 owned zero buffers remain
the same. The identity is the transpose of the credited shared-source
covector rewrite; the literal program, derived dirty cleanup, native phases
and all-column proofs are in the native-alternatives package.

### Complete invoices

All three constructions use dimension 73, 360 replicas and 3,240 local calls.
The productive count is 322,560. The physical family count is 323,069, including
408 reserved helpers, eight center accumulators, 91 private zero buffers and
two coefficient fields. The stock therefore still fits 19 bits.

| Paid child rank | Attached PR3734 | Adopted PR3815 | New receiver-sharing word |
|---:|---:|---:|---:|
| 1 | 7,990,332 | 7,989,840 | 7,986,600 |
| 2 | 2,349,000 | 2,349,000 | 2,345,760 |
| 3 | 748,971 | 749,088 | 752,328 |
| 4 | 330,480 | 330,480 | 330,480 |
| 5 | 69,479 | 69,120 | 69,120 |
| 8 | 25,920 | 25,920 | 25,920 |
| 32 | 1 | 0 | 0 |
| 48 | 137,911 | 137,952 | 137,952 |

Each column has raw rank mass 23,431,680, compared with the normalizer
73×322,560=23,546,880. The raw deficit is 115,200, or 320 per replica. The gain
comes from the distribution of paid child ranks, with all raw rank units and
physical families accounted for.

The exact engine encloses

\[
M(a)=\frac{1}{322560}\sum_r n_r(r/73)^{1-a}.
\]

The lower root endpoint has an upper enclosure below 1, and the adjacent upper
endpoint has a lower enclosure above 1. All paid ranks are below 73, so the
moment is strictly increasing. `native_owner_invoice.py` also checks the same
root with the independently retained PR3734 rational-price implementation.

## Independent gates

`review_pr3815.py` freshly runs the upstream standard-library verifier, checks
all available predecessor native, template, dispatch and owner-audit files
against the frozen attachment, then independently rebuilds the exact dual
with the previously frozen invoice engine. It checks every one of 2,551 bin
patterns and rejects the lower-endpoint and perturbed-dual controls. Its
receipt is `PR3815-INDEPENDENT-REVIEW.json`.

`native_owner_invoice.py` binds both current complete five-stage native
receipts and their compiler sources. It independently recounts paid climbs
and center children in both orientations of both providers and checks their
common native frames. It then rebuilds all 6,480 physical windows and checks
every one of 1,321,920 helper-role rows: ordered identity coverage, the strict
lower/closed upper timing convention, all bin capacities and offsets,
same-call family injection and productive-data/helper nonaliasing. It emits
`receiver-sharing/PROFILE.json`, `PRICE.json` and `RESULT.json`.

`review_admission.py` independently reconstructs the full source adaptation
against the pinned replay archive. The previous staged544 review still reads
its exact retained parent word; the new edit and new independent review are
appended to the rebuild chain. The admission adapter changes only the immutable
source identity and its sole CLI selector. This review also runs the two
unchanged modern outer engines in an isolated copy, using the independently
certified new endpoint and complete profile. All 63 strict inequalities and
all 17 original rejection controls pass. The first-attempt output and script
are retained unchanged under `admission-review/` and `review_admission.py`.

`review_runtime.py` independently reviews the subsequent memory repair. After
removing exactly one unused accumulator and the diagnostic statements, the
entire scientific audit function has the same abstract syntax tree. All 76
unchanged assertions retain their order; the one hash assertion computes the
same decompressed payload hash by streaming. The report and export tail remains
byte-identical. Nineteen fresh fixtures check mutation isolation and ensure
that mutator errors, unexpected exceptions, signals, nonzero exits and missing
rejection receipts all fail. The source-bound review is
`../runtime-repair/REVIEW-INVOICE.json`.

`review_admission_runtime.py` then reviews the final repaired source: exactly
11 declared changed paths in a 664-file manifest, including the reviewed
runtime wrapper, with the original scientific auditor and emitter unchanged.
Its fresh isolated executions of both modern outer engines pass the same
63 strict inequalities and 17 controls. This review is in
`admission-review-low-memory/`. The parent's complete supplier release remains
a separate required gate.

## Fixed-component ceilings and the next useful gate

The new word reaches its **fixed-inventory packing ceiling to the certified
24 decimal places**.
`receiver_packing_ceiling.py` freshly verifies the PR3815 basis at the new
endpoint, with the new local paid profile. Its dual checks every bin pattern
and gives a strictly positive lower bound at
0.001730739780298357321620. Therefore no clock, replica count or owner
rearrangement of this exact supplier and idle template can reach that
endpoint. The actual fill's root is strictly above the adjacent lower
endpoint, so any remaining packing-only improvement is less than 10^-24.
This proves the displayed ceiling; it does not prove exact equality of
unrounded transcendental optima. `RECEIVER-PACKING-CEILING.json` binds the
actual native and physical invoice evidence.

This ceiling is limited to the fixed local profile, widths, bins and rule that
each nonempty remainder is one paid child. Another native edit or a different
template remains a valid next direction.

`changed_inventory_screen.py` is a reusable exact necessary gate for such a
candidate. It accepts either a compiled native word or explicit complete
local/width histograms. It checks the unchanged rank 73 bin dual over the
certified width alphabet 4..9. A positive lower bound rejects that candidate
at the adopted endpoint for every clock; a nonpositive lower bound means only
**not excluded**. It is never reported as a construction or a gain. The
unchanged supplier and a width-preserving two-rank-1-to-rank-2 fusion are controls.

That predecessor script and its receipts remain unchanged. The new
`current_inventory_screen.py` defaults to the actual receiver-sharing root's
upper endpoint and accepts an explicit rational `--endpoint`. It binds the
current physical invoice and both native providers. Its current-word control
has a strictly positive lower bound; a further width-preserving fusion makes
the bound negative. This provides a reusable gate for the next complete word.

[PR3862], by Sagar Thakrar / thakrarsagar, already gives the exact width-price
interpretation and staged-entry break-even calculations for this ideal model.
Its physical and complete-admission obligations remain separate. This package
uses that prior result to avoid repeating an unpaid staging screen. Widths 1..3
are deliberately not extrapolated by the local gate.

### Price targets for native rewrites

`profile_prices.py` provides exact complete-profile tariff targets. Each listed
substitution remains hypothetical until an actual native word proves it.
On the adopted PR3815 fill, one `2 H1 → H2` occurrence in every local call would
give root lower endpoint 0.001730695637425571737118. Two per call are stronger.
Reaching the retained BIT ceiling with that substitution alone requires
exactly 78,626 total occurrences, or 25 if the same number is required in every
one of 3,240 calls. The new receiver-sharing construction instead realizes
`H1 + H2 → H3` once per call.

The retained BIT root is 0.001733427039589844234749. It remains above the new
complex root; neither the outer precision conversion nor the BIT branch
currently determines the displayed gain. The modern near-lossless conversion
is `κ=a−10^-46−10^-70`; it must not be confused with the older selected record's
balanced `a/(1+a)` interface.

`remaining_budget.py` gives the exact current gap and the sharp next threshold.
At the current profile, **53,876 additional** `H1 + H2 → H3` fusions are needed
to move the complex-price endpoint above the retained BIT cap. If the same
number must occur in every call, **16 additional per call fail and 17 pass**.
That is 18 total per call including the one already realized. The certificate
checks both the BIT endpoint and that endpoint plus the current outer loss.
Only the first fusion has a literal native construction; these additional
counts assume disjoint fusions without added costs. Reaching that price would
make the BIT side constraint binding, and would not itself admit a value above
the constraint.

The current conditional κ gap to that cap is exactly

```
0.0000026872592914869131300000000000000000000001000000000000000000000001
```

The same receipt checks a second concrete tariff goal: one helper width
8→7 reduction per call together with its complete local redistribution
`Δ{1:+3, 2:+1, 3:-2}`. The all-pattern dual does **not exclude** that proposed
signature at the current endpoint. In rank-1 cost units, its local saving is
approximately 0.99100024 and the dual width tariff is approximately 0.98773564;
the receipt provides outward rational intervals. This is a necessary gate
only. It provides no native endpoint repair, feasible new owner fill, improved
κ or outer admission.

## Three-pair architecture: exact negative result

The architecture agent emitted an exact native three-pair/seven-call geometry,
with dimension 57 and 672 productive families per replica. Its raw deficit 224
looks attractive, but actual helper sizes matter. The unrestricted aggregate
pattern optimum has idle profile

\[
\{1:602/3,\quad5:896/9,\quad32:406/9\}
\]

per replica. Its root lies in

\[
[0.001718630707363138070731,
 0.001718630707363138070732].
\]

`p3_certificate.py` checks all exact primal equations and every one of 444 bin
patterns with an outward-rational dual. This ceiling covers every clock and
replica count, including asynchronous clocks. It proves that this unchanged
seven-call inventory cannot improve even the attached PR3734 result.
`P3-CEILING.json` binds the literal geometry. The earlier
`p3_pattern_screen.py` and its receipt are floating-point discovery records
only; the later exact global certificate supersedes their narrower screen.

## Open next questions

1. Find another complete native source-sharing or receiver-sharing identity
   whose exact optimized profile improves the new tariff while retaining the
   ordered inventory. The attained owner fill and both outer engines provide
   a short admission path once both native providers pass.
2. Complete a width-reducing helper entry transformation, including every
   dirty restoration and endpoint repair. Feed the actual complete profile
   and widths to `current_inventory_screen.py` before attempting a new fill.
   Passing this necessary gate leaves physical hosting and full admission open.
3. Change a hypothesis of the proved packing ceiling if pursuing a new
   architecture. The unchanged three-pair family is already excluded by its
   exact all-clock ceiling. A successful alternative must emit its native
   phase geometry and complete physical invoice before a price becomes a
   construction claim.

## Reproduce

Run from the repository root:

```sh
python3 -B research/kappa-adaptive-continuation/global-budget/review_pr3815.py
python3 -B research/kappa-adaptive-continuation/global-budget/p3_certificate.py
python3 -B research/kappa-adaptive-continuation/global-budget/native_owner_invoice.py \
  --base-local research/kappa-adaptive-continuation/native-alternatives/native-base/native/local \
  --extra-local research/kappa-adaptive-continuation/native-alternatives/native-extra/native/local \
  --out research/kappa-adaptive-continuation/global-budget/receiver-sharing
python3 -B research/kappa-adaptive-continuation/global-budget/receiver_packing_ceiling.py
python3 -B research/kappa-adaptive-continuation/global-budget/changed_inventory_screen.py \
  --out research/kappa-adaptive-continuation/global-budget/UNCHANGED-INVENTORY-SCREEN.json
python3 -B research/kappa-adaptive-continuation/global-budget/changed_inventory_screen.py \
  --native-word research/kappa-adaptive-continuation/native-alternatives/native-base/native/local/CANONICAL-WORD.json.gz \
  --out research/kappa-adaptive-continuation/global-budget/RECEIVER-INVENTORY-SCREEN.json
python3 -B research/kappa-adaptive-continuation/global-budget/profile_prices.py
python3 -B research/kappa-adaptive-continuation/global-budget/profile_prices.py \
  --profile research/kappa-adaptive-continuation/sources/PR3815/research/staged544-clock-ceiling/inputs/PROFILE.json \
  --out research/kappa-adaptive-continuation/global-budget/CEILING-REWRITE-PRICES.json
python3 -B research/kappa-adaptive-continuation/global-budget/current_inventory_screen.py
python3 -B research/kappa-adaptive-continuation/global-budget/remaining_budget.py
python3 -B research/kappa-adaptive-continuation/global-budget/review_runtime.py
```

`review_admission_runtime.py` takes `--work` pointing at a prepared parent
release workspace and requires a fresh `--out` directory. The prepared package
must already contain its T360 outer specification. The script does not write
to the active release workspace. The exact certificate and owner programs use
only the standard library. The optional exploratory pattern LP additionally
uses NumPy and SciPy.

All inherited all-size compiler, physical realization, hosting, precision and
recovery, analytic and BIT assumptions remain. These artifacts are finite
construction and arithmetic certificates, not an unconditional multiplication
theorem or a selected-frontier update.

[PR3815]: https://github.com/CrocSwap/integer-mult-bounds/pull/3815
[PR3802]: https://github.com/CrocSwap/integer-mult-bounds/pull/3802
[PR3862]: https://github.com/CrocSwap/integer-mult-bounds/pull/3862
