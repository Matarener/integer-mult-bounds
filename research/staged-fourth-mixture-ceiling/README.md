# Sharp pooled ceiling for a fourth staged entry

For the exact THREE/FOUR words in [PR4088](https://github.com/CrocSwap/integer-mult-bounds/pull/4088)
at `76088d49e3ed4142a958659aa996b0ca4da5e88e`, the best pooled complete moment
uses **1,080 fourth-entry calls out of 3,240**. This is the same one-third
fraction as its literal construction. Every real mixture is allowed in this
relaxation, and all whole-helper patterns and residual children are charged.

The sharp pooled root lies in

```
[0.001730980255989036959962,
 0.001730980255989036959963].
```

Thus any improvement to the pinned literal fill within this fixed two-provider
invoice is **less than 1.951e-9 in the complete-moment root**. This is an upper
bound on remaining headroom, not an achieved supplier or a new kappa.

The proof certifies all 841 bin patterns, three duals and a piecewise affine
optimum for every real staging count `0 <= x <= 3240` and every exponent
`0.00173 <= a <= 0.00174`. An eight-pattern **integer pooled** witness attains
the optimum at `x=1080`; it is not a chronological owner map. Its idle profile
is `{3:22788,5:1620,48:138492}`. The literal fill exceeds it by
`-3 H3 + 5 H5 + H16 + 2 H32 - 2 H48`, a strictly positive power cost for
`H_r=r^(1-a)` and `0<a<1`.

## Reproduction and evidence

From the repository root with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/staged-fourth-mixture-ceiling
python3.12 -B scripts/check_research_commit.py --package research/staged-fourth-mixture-ceiling --check-source-history
```

`source_binding.py` re-executes the credited predecessor binary-frame cost
ledger on all four words and extracts the current 360-replica bins.
`verify.py` checks the exact primal/dual and complete invoice.
`independent/check.py` uses a separately implemented fixed-point rational enclosure
engine and pattern enumeration; `independent/review_broad.py` separately checks the whole exponent interval and affine fills. The normal and optimized commands retain
explicit rejecting controls. `RESULT.json` and `PROOF.md` give the exact
certificate and derivation. No optimizer is needed for replay. All four standalone commands in `VERIFY.json` also run from the official committed export, with `{package}` replaced by the exported package path; add `-O` for optimized replay. The metadata commands above require Git.

Fourteen predecessor files are retained byte-for-byte. `SOURCE-EXPORT.json`
records their original head, path, Git blob and SHA256; `SOURCES.json` binds
their committed local freeze so a cold checkout needs no pending-PR objects.
The original template contains historical 37-replica material: only its
original child-port capacities are used, with the current `ORDER.json`
supplying all 360 replicas. No historical replica factor is silently reused.

## Scope and limits

The model fixes the two local invoices, width-5 through width-9 whole helpers,
all original capacity-8/16/32/48 bins, one paid residual per bin, width 73 and
stock `896*360`. It drops chronology, helper identity, family exclusions,
offsets and integral pattern multiplicities to obtain a lower cost bound.
Additional implementation costs cannot improve that bound. Changed words,
capacities, cross-slot operator fusions or stock conventions require a new model.

The mathematical result combines a written linear-program dual argument with
finite exhaustive pattern coverage and exact rational interval certificates.
There is no formal-kernel or independent human review. The predecessor ledger
is reused and freshly executed for local costs; dirty-state identities, native
phases, physical hosting, mixed-provider full release, precision, tape, BIT and
outer transfer are not freshly verified here. The selected record is unchanged.

## Open next questions

Can legal exchanges attain the pooled eight-pattern inventory? Inspect the
literal fill's one rank-16 and two rank-32 residual bins, preserve all source
windows and physical-family constraints, and require complete owner/phase and
release validation. The maximum possible gain is now explicit. A larger change
must alter a named provider or interface premise and reprice its complete cost.
Structured questions and blockers are in `TASK.json`.

Prepared for Ross Richardson with substantial GPT-6.1 Sol assistance, including
two mathematical specialists. Credit Cinna Davis/PR4088; Rohan Arun/PR4076;
Dugongue and David Ganz/PR4085/3945; Nick Petalas; dataisfire/PR3734;
ChaloupeMusic and Erwan Secousses/PR3949/3815; the staged-release, solver,
native, owner and transfer lineage. See `NOTICE.md` and the retained source
notice. Apache-2.0.
