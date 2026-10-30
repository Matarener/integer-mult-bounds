# Submission review: operator repair and staged receiver composition

The submitted replacement gives the conditional claim

`κ = 0.001730970419199163702738 - 10^-46 - 10^-70`.

The authoritative final claim is
[late-staged-composition/CLAIM.json](../kappa-operator-repair/late-staged-composition/CLAIM.json).
The top-level `kappa-operator-repair/CLAIM.json` is the earlier, weaker checkpoint
at `0.001730824595303184580890` before outer losses. Both are retained unchanged.
The selected repository frontier is not updated by this submission.

## What this fixes

The earlier high complex supplier failed the full operator identity. Its
counterexample and our [previous review](../kappa-next-regime-review/README.md)
remain valid for that old construction. This replacement discards the faulty
phase-axis transfers. It combines [PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945)'s terminal refit, an exact dirty
receiver-sharing identity, and [PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076)'s staged entries/owner allocation.

The supplied operator proof normalizes the complete signed eight-stream
controller, including final translation and global phase. It checks 10,416
exact phase-polynomial identities over 112 ports. Equality of the phase forms
is an all-character argument and survives positive tensor multiplicities;
the dense character examples are implementation checks, not the basis of
that universal statement. The old move file still rejects.

The final owner check reconstructs 1,321,920 hosted rows using actual native
widths, disjoint original child axes and scalar-observation windows. Hosted
and residual factors reassemble their original children before applying the
controller identity. The 70,876 owner reassignments are not phase-axis transfers.
This addresses the previously reproduced obstruction within the declared
local-endpoint/common-cover interface. Uniform implementation of that interface
remains conditional; this review is not a new independent proof of every layer.

## Local validation result

The portable review completed **14 scientific stages and 29 comparisons** in
115.20 seconds: twelve unchanged core stages plus two complete five-stage native
provider rebuilds. All three portability rejection controls passed. See
[FRESH-REPLAY.json](FRESH-REPLAY.json), [FRESH-CORE.json](FRESH-CORE.json),
the fresh native receipts and `logs/`. Every one of the 3,178 imported files
matched its staged Git bytes. The separate arithmetic check passed.

## Arithmetic checked separately

[check_price.py](check_price.py) uses the independent exact rational log/exp
method from the previous review, generalized to ambient width 73. It imports
no submitted price engine. The final supplied profile has rank mass 23,431,680
and productive stock 322,560. Its strict root bracket is

`0.001730970419199163702738 < a_complex < 0.001730970419199163702739`.

[PRICE-REVIEW.json](PRICE-REVIEW.json) contains the exact moment intervals and
headline arithmetic. The complex endpoint lies below both the retained stronger
BIT endpoint `0.001738137188329345368427` and the sufficient BIT endpoint used
by the outer release, `0.001733427039589844234749`.

**Direct improvement over [PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076):**
its lower endpoint is `0.001730809033576552081734`, so the new conditional κ is
larger by exactly `1.61385622611621004e-7` (+0.0093243% of the displayed endpoint).
Both claims subtract the same outer losses. The reviewed [PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076) head is
`9744f9df268590295a9872b1952c695a678192b9`.

The gain `2.30638900806381119e-7` compares conditional headlines with the same
outer losses, or equivalently their complex supplier endpoints. It is relative
to the supplied prior operator-valid endpoint `0.001730739780298357321619`,
not to the repository's selected frontier. The new claim remains below [#3959](https://github.com/CrocSwap/integer-mult-bounds/pull/3959)'s
old displayed `0.001736738651088946052684` and the research target `0.001745`.
No best-public-bound or unconditional multiplication claim is made.

## Reproduce

Use Python 3.12 with assertions enabled. The native checker requires NumPy,
which is not installed by the supplied replay script. The local isolated
environment uses `numpy==2.2.6`:

```sh
python3.12 -m venv /tmp/kappa-repair-env
/tmp/kappa-repair-env/bin/python -m pip install numpy==2.2.6
/tmp/kappa-repair-env/bin/python -B research/kappa-operator-repair-review/verify.py \
  --out /absolute/path/to/a/fresh-directory
python3.12 -B research/kappa-operator-repair-review/check_price.py
python3.12 -B research/kappa-operator-repair-review/check_import.py --git-ref HEAD
```

The portable review runner freshly executes the core/operator/owner/invoice/claim checks and
both five-stage native providers. It authenticates retained full-release
evidence; it does **not** rerun the long full release. The original
`research/kappa-operator-repair/replay_latest.py --native` is also retained;
its `--full` option additionally executes the inherited release. The retained
BIT supplier is source-bound and was not freshly rebuilt during this review.
Discovery searches are retained evidence, not all rerun. No hosted CI, Lean,
formal-kernel acceptance, independent human review, complete GL64 physical
execution or maintainer admission is claimed.

The initial local attempt passed all twelve core stages, then stopped in the
first native local audit because NumPy was unavailable. That failed attempt
is retained separately; it is not counted as a successful native replay.
No scientific source, expected receipt or assertion was changed to address it.

With NumPy installed, the original replay passed all five stages for the first
native provider, then rejected its gzip container bytes. Both native gzip
payloads were exactly equal; only gzip header byte 9 differed (macOS OS marker
19 versus Linux marker 3). [GZIP-PORTABILITY.json](GZIP-PORTABILITY.json) records
the exact hashes. The derived native receipts differed only in those container
hash fields and the documented phase-review runtime.

[verify.py](verify.py) is a separate portable adapter. It invokes the unchanged
12-stage core replay and both original five-stage native runners. It compares
the two gzip files by exact decompressed bytes; independently authenticates
each receipt's canonical-word/program hashes against its own actual files;
and then compares every remaining field, omitting only the validated phase
runtime. Local checks and residual adapters still require byte identity.
Changed payloads, forged container pins and invalid runtimes are rejection
controls. No expected scientific value or source-authentication gate is relaxed.
The original replay attempts are preserved under `attempts/`.

## Exact source packaging

[IMPORT.json](IMPORT.json) records all 3,178 compact-archive members and their
hashes. ZIP SHA256:
`e6ac75bbe10e5862d2e175fac9bc50a718de6453b0ebb77ffa171c75f7afe12b`.
Its 3,176-file replay manifest excludes the two manifest/validation files.
There were 683 byte-identical existing files and 2,495 new files at intake.
The new files occupy five continuation directories and preserve every supplied
byte, predecessor notice, original path and pinned receipt. Existing frozen
inputs are unchanged. Narrow Git attributes prevent newline conversion.
The ZIP itself is not committed; the unpacked sources and replay dependencies
are available directly to a clean checkout. The separate split full-repository
archive was not supplied and its preservation claims were not checked here.

Canonical main was refreshed to `bb4bccbf42844d2801487450727c2f63e10d1d0f`.
Its entry, contribution, research-priority, family-status and selected-result
guidance did not differ from the previous review base. The latest 20 open PRs
were checked for overlap, and [PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076)'s live head matches the supplied pin
`9744f9df268590295a9872b1952c695a678192b9`. Its public body still labels its own
final release pending; this submission's retained composed release is separate
evidence, not a claim that upstream completed that run. Coverage is partial.

## Attribution and open next questions

Retain the supplied complete notices. Principal dependencies include
Rohan Arun/[PR4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076), David Ganz (Dugongue)/[PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945), Tekalign's native runner, Ross Richardson, dataisfire,
ChaloupeMusic/Erwan Secousses, Marius-Paul Dumitrean, Sagar Thakrar, roger-sato,
the T360/[PR3815](https://github.com/CrocSwap/integer-mult-bounds/pull/3815) lineage, and the prior BIT and outer-composition authors.
The historical obstruction credits Nick Petalas, Matarener and Erwan's [PR4046](https://github.com/CrocSwap/integer-mult-bounds/pull/4046).
This packaging and review were prepared under the user's direction with
substantial OpenAI Codex assistance. Apache-2.0, subject to retained notices.

1. **Admit the remaining uniform interfaces.** Start with the actual
   native-to-owner chart embedding and retained precision/fallback tariff.
   The finite operator checks do not themselves discharge these assumptions.
2. **Independently review the full release.** Start with the source-bound
   completed admission and outer receipts, then run `--full` in a suitably
   provisioned environment. This portable review authenticates that evidence
   without claiming fresh execution of it.
3. **Seek further gains on the repaired word.** Start with the exact final
   staged/receiver word and a complete owner invoice. Earlier finite negative
   searches on other pinned words do not exclude new mechanisms here.
