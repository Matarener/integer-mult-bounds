# Review of the submitted T35 permanent-carrier construction

This review accompanies the byte-preserved [submitted package](../kappa-next-regime/README.md).
The BIT invoice has the strict root bracket
`0.001736847843363802786320 < c_BIT < 0.001736847843363802786321`.
This is a finite paid-profile result under the retained tariff assumptions.
The proposed multiplication κ additionally requires a valid complex supplier;
the inherited PR3955 construction has a concrete operator objection, not merely
an outstanding review checkbox. The submitted headline must not be treated as
an established improved multiplication bound.

## Arithmetic and construction scope

The submitted change combines three permanent dirty carriers in R437 with
seven groups of five replicas. Its paid profile is
`{1:416430, 2:437829, 3:23310, 4:30030, 5:32445, 6:18690, 7:28980, 42:441}`.
There are 988,155 requests, rank mass 1,977,885 and productive stock 31,080.
The raw deficit is 11,235. The invoice includes the stated bad-class surcharge.

[check_price.py](check_price.py) imports no submitted price engine. Positive
atanh series with geometric tails bound logarithms; positive Taylor series
with geometric tails bound exponentials. All bounds use exact fractions and
outward rounding. The recomputed moment is below one at the lower endpoint
and above one at the upper endpoint. [PRICE-REVIEW.json](PRICE-REVIEW.json)
records exact intervals as well as rounded displays. The reported increments,
outer-loss subtraction, prefix integer and coefficient bit lengths also agree.
These checks do not derive the profile from a physical multiplication algorithm
or establish applicability of the inherited fallback/precision tariff.

The original advertised κ is the lower BIT endpoint minus `10^-46 + 10^-70`.
Its arithmetic gain over PR3959's displayed endpoint is approximately
`1.09192274856733636e-7` (0.00628720244052088%). This comparison is against that
specific conditional endpoint, not a claim of global novelty or a public record.

## Complex supplier objection

[PR4046](https://github.com/CrocSwap/integer-mult-bounds/pull/4046), head
`84c2b2072e7cba265fc1e43f28ccd558b5a4cbfa`, reports that PR3934/PR3955 retain
the operator-changing moves behind the author's
[PR3251 retraction](https://github.com/CrocSwap/integer-mult-bounds/pull/3251).
The submission vendors PR3955's exact move file through its PR3959 sources:
SHA256 `01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b`.

[check_complex_witness.py](check_complex_witness.py) binds that exact file to
the existing PR3187/PR3296 operator replay. It uses **all submitted moves at
owner 0, port 0**, including axis `2^72` transfers `14 -> 8` and `15 -> 10`.
It checks the baseline scalar operator, the complete port overlay, an empty
overlay control, and invalid self/absent-axis controls. It tests the retained
literal-frame, unchanged-invocation contract; it does not rule out a repaired
schedule or a different hosted realization.

The local replay confirms **10 changed exact matrix entries** after all six
submitted moves in this port. Both invalid-move controls reject and the empty
overlay preserves the operator. [COMPLEX-WITNESS.json](COMPLEX-WITNESS.json)
records every changed entry as Gaussian integer pairs. This reproduces the
objection against the attached package itself, rather than relying solely on
PR4046's reported conclusion.

The supplied `complex-fill-audit` checks the fill binding, axis geometry,
profile and moment. Reading its exact source shows that it does not replay
the full eight-stream operator. Passing that audit cannot discharge this
objection. A conditional numerical composition may still be stated with its
premise, but the present complex realization cannot support admission of the
advertised multiplication κ under the tested contract.

## Reproduction and provenance

From the repository root:

```sh
python3.12 -B research/kappa-next-regime/verify.py --output /tmp/kappa-next-fresh
python3 -B research/kappa-next-regime-review/check_price.py
python3 -B research/kappa-next-regime-review/check_complex_witness.py
python3 -B research/kappa-next-regime-review/check_import.py --git-ref HEAD
```

The first command requires a fresh absolute output directory outside the
checkout. Use **Python 3.12** for the frozen AST receipts. The submission says
3.11 or later, but its `ast.dump` hashes are interpreter-version-dependent:
3.11.11, 3.13.5 and 3.14.5 give different AST hashes, while 3.12.8 matches.
A first full attempt on 3.14.5 completed the symbolic word execution but failed
its receipt equality at stage 14: four AST hash fields differed (besides the
explicitly omitted elapsed-time field). No symbolic counts or other receipt
fields differed. This is a reproducibility limitation; no hash check was
relaxed and the frozen evidence remains unchanged.
Do not enable Python optimization. It is the
full fresh replay, not `--reuse-expensive-receipts`. Its symbolic schedule uses
formal primitive contracts, and its physical protocol probe is a controlled
46-bit fixture; neither is complete GL64 numerical execution. Discovery searches
are retained as submitted evidence and are not all rerun by this replay. No
hosted CI run, Lean proof, or all-size supplier admission is claimed.

[IMPORT.json](IMPORT.json) binds every extracted file to the supplied 18,736,979-byte
ZIP, SHA256 `728cc39a8ff17550c74e7edd519a70b89cde62b8b62ac91e7406d5db919fad39`.
The 459 package files and two previously absent outer dependency scripts are
imported unchanged; 210 existing repository inputs are byte-identical.
The two outer scripts retain their original `kappa-adaptive-continuation`
paths because the replay pins those paths. No existing predecessor file is
replaced. Narrow Git attributes preserve the imported CRLF and other exact
bytes. The supplied report differs from the package README only in link
presentation and is retained as [SUPPLIED-REPORT.md](SUPPLIED-REPORT.md).

The original [VALIDATION.json](../kappa-next-regime/VALIDATION.json) is producer
evidence; the new [FRESH-REPLAY.json](FRESH-REPLAY.json) records a successful full fresh
Python 3.12.8 replay: **21 stages and 31 exact comparisons**, in 431.60 seconds.
The associated command logs are retained in `logs/`. No expensive receipt was
reused. The frozen package manifest also passes in the destination checkout. The supplied full-repository
ZIP preservation claims have not been checked because only the compact ZIP was
provided. The selected frontier remains `0.001672660197076918`.

## Overlap and credit

Canonical main was refreshed to `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The start-here discussion, eight recently updated discussions and the latest
50 open PRs were inspected. This is partial overlap coverage. PR3959's live
head agrees with the submission's `babd2e36471422cd3e97f912a5cf2846da52a222`.
[PR4067](https://github.com/CrocSwap/integer-mult-bounds/pull/4067) supplies a
different two-window R437 rewrite and also distinguishes a paid-profile gain
from supplier admission. No new research family or selected-frontier update
is inferred from this intake.

The submitted construction and preserved notices credit Rohan Arun, ai-nanachi,
Nick Petalas, Ali Romman, Sagar Thakrar, mightyOil, Chris R / Clear1nsight,
Jeremy Diviney and the full inherited source lineage. The operator replay
retains Nick Petalas's PR3187 model and Matarener's PR3296 binding, with Erwan's
PR4046 identifying the open-chain connection. This review adds the exact
submitted-file binding and an independently implemented invoice price check.
Prepared under the user's direction with substantial OpenAI Codex assistance;
no independent human or formal-kernel review is claimed. Apache-2.0.

## Open next questions

1. **Repair or replace the complex supplier.** This is necessary before this
   BIT endpoint can support the advertised multiplication κ. Start with an
   explicit operator-preserving schedule or hosted cell-to-axis map for the
   owner-0/port-0 witness. The unchanged-invocation counterexample is the blocker.
2. **Admit the changed BIT word and pooled schedule uniformly.** Start with
   the exact native preparation, routing and fallback/precision interfaces.
   Finite symbolic and controlled-payload checks leave the general primitive
   and all-size contracts open.
3. **Explore larger carrier networks only with complete invoices.** Start
   from the supplied three-carrier word and retain dirty capture rows, source
   histories, inverse costs and owner geometry. The supplied fixed-slot packing
   ceiling and finite failed searches do not exclude new word mechanisms.
