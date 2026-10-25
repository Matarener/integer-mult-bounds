# Independent review: retain the Q conjugations in the fresh-stage inverse bound

The literal inverse extension in PR #5408's `PROOF.md` §1 is too broad:
“also applies to B_f^-1” must refer to **Q^(-tensor f) B_f^-1 Q^(tensor f)**.
We give a source-bound counterexample to the unconjugated wording and an
independent review of the corrected statement. The actual negative-bank
postdecoder in §6 already has the correct conjugations.

For one stage, put `D_f = diag_i(K_i^(tensor f))`. Then

```
C_f^-1 = D_f^-1 (A^-1 ⊗ I) D_f,    A^-1 = (A + 12I)/13.
```

Every row of this actual inverse has 53 nonzero owner coefficients. Computing
the first term with COPY/SCALE and adding the other 52 terms uses **5,824 ADDs
for every positive f**. Keep the normalized inputs and outputs in separate
owned banks, then apply the inverse monomial maps and clear scratch. The
literal claim would require 5,826 ADDs at `k=1, f=2925`. This is an exact
coefficient-program certificate and a written construction; it does not
materialize that enormous tensor or supply a physical finite-precision invoice.
The source already has its own smaller recoding recipe; our upper bound is
an independent witness, with no optimality claim.

[REVIEW.md](REVIEW.md) checks the ordered fresh-stage factorization, the
nonzero path for every nonzero integer power, the four-entry conjugation,
and the support contraction. It records no further defect in §§2–6 under
the stated interface assumptions. [markers.py](markers.py) independently
builds local relations by joining literal row-dot signatures and propagates
constraints through the resulting layered graph. It recovers the sole owner
path for **all 13 saved certificates**, covering stage counts 1–9, 18, 19, 32
and 64, and binds them to **all 16 saved negative banks**. These finite checks
corroborate the written all-length proof; a census through 64 is not that proof.

The corrected conclusions remain `ADDs >= max(0,2f-24k)` for arbitrary fixed
fresh-stage length and at least `max(0,2f-6)` for each saved negative bank.
The per-bank bounds cannot be added, and the earlier two-stage offset-two
result remains stronger for its named banks. No new obstruction theorem,
new provider, improved κ, formal-kernel acceptance, or independent human
review is claimed. The current selected κ at our base is 0.003027288235;
this package does not change it or its five framework assumptions.

## Evidence and reproduction

Use Python 3.12 with the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/fresh-stage-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/fresh-stage-independent-audit
python3.12 -I -O -B research/fresh-stage-independent-audit/verify.py
```

Expected marker: `PASS_INDEPENDENT_FRESH_STAGE_AUDIT_WITH_INVERSE_SCOPE_FINDING`.
The verifier authenticates 14 predecessor inputs, checks all 12,544 entries
of the exact code polynomial, 57,344 literal signed normalizer entries, and
512 conjugated columns and rows. It independently counts and reconstructs
marker paths, checks all actual bank words and nonzero coefficients, and
compares the full deterministic [RESULT.json](RESULT.json).
Controls cover a missing inverse diagonal term, tensor-powered owner scalars,
a fixed central vector, wrong Q orientation, empty/zero markers (53 paths),
an impossible marker endpoint (zero paths), zero powers, repeated stages,
and the wrong bank endpoint type. Neither predecessor checker nor proposer
is imported or run. The implementations share their source data, Python,
and the finite-state mathematical invariant; this is the stated limit of
computational independence.

[VERIFICATION.md](VERIFICATION.md) records the actual normal/optimized replay,
source-history preflight and Git-free export checks. The saved endpoint and
its producer lineage remain premises. No full producer, compiler, outer,
selected cold, Lean or Docker replay was performed.

## Assignment, overlap and scope

We took the [explicit PR #5408 review handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19156413),
with the [canonical scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19173519).
The source head is `256126eeb1607c0bf52996c3d90490f2b786b94a`; the package
starts from canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
[SOURCES.json](SOURCES.json) pins the actual committed bytes and retained
notices. [TASK.json](TASK.json) records the changed formal-interface card:
this is a written/executable interface review, without a proof-assistant build.

The 04:46–04:48 UTC snapshot on 2026-10-25 covered 364 open PR bodies,
4,771 Discussion records and all 7,402 tracked local package/ledger notes.
The explicit review request and family thread were inspected. No competing
review appeared in that coverage; arbitrary diffs and unpublished work were
not searched. The existing numerical factor-cap follow-up was already
addressed by #5500; active precision/CRT claims were left separate. The
native-tensor least-width question would require a different result and was
not undertaken. The current picker was run once (seed
`bf5df56858d3ce7748b6d7c617abe1fe`, adversarial-audit suggestions); the explicit
review handoff supplied this bounded assignment. Baseline binding checks
are orientation only, not scientific acceptance.

## Open next questions

The concrete handoff is to retain the Q conjugations when restating the
inverse theorem or citing it in later decoder work. The frozen predecessor
is unchanged; this review supplies an explicit erratum and counterexample.

A formalization of the corrected contraction-to-caller implication remains
open: begin with the single shared binary line, distinct private-stage
supports, and initially independent role coordinates, then connect an exact
marker-path certificate to row support. It would give proof-kernel checking
of the reviewed interface. No formal encoding or build is supplied here.
The source's paid-decoder and correlated-history questions remain open;
this review does not take over their existing claims.

## Credit

Prepared by Hiroki KUMAZAKI with substantial OpenAI Codex assistance, including
separate proof-review, marker-checker and counterexample-review subagents.
All reviewers are automated participants in the same session.

Ali Romman / #5408 supplied the all-length theorem and marker certificates;
Dillon / #4933 supplied the physical normalizers and typed caller;
Cinna Davis / #5065 supplied the two-stage marker proof; Dugongue / #4929
supplied the center-free code. Cao Yifan / intqwq, Cinna Davis / 1337isnot1337,
zxv, Jacob Alan Sussman, Ryanson Jonathan and the retained native/controller
lineage retain their credit. Source-specific NOTICE, LICENSE and ORIGINS
remain pinned and are included by the declared-input export. New review,
counterexample and independently implemented checks are Apache-2.0.
