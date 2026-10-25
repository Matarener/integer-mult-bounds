# Does PR4091's pooled ceiling transfer to the retained PR4088 head?

Independent source-bound transfer audit, priority revision 7 card
`independent-moment`. **No new kappa, no supplier admission, and no change to
the selected record.**

PR4091 (`research/staged-fourth-mixture-ceiling`) certifies a sharp pooled
ceiling `0.001730980255989036959962..963` for a fixed two-provider invoice
pinned to PR4088 head `76088d49e3ed4142a958659aa996b0ca4da5e88e`
(1,080 fourth-entry calls of 3,240). The retained PR4088 head on main
(`research/staged544-mixed-fourth-entry`, `72d7efc181edb21806a878f174847c96
dd410ab0`) uses 1,090 fourth-entry calls. Revision 7 requires verifying word,
capacity and stock equivalence before applying the ceiling to the later fill.

## Verdict (all checks pass; `verify.py`)

1. **Words identical byte-for-byte.** All four shared scalar-word inputs
   (`THREE/FOUR × base/extra`) hash identically (gzip payload and canonical
   JSON) between the ceiling package's `source4088/inputs/` freeze and the
   retained head's `inputs/`: 4/4. The four-entry profile derived from
   PR4091's published `L3` and `d = L4-L3` equals PR4088's published table.
2. **Capacity and stock identical.** Bin inventory `8:241,920`,
   `16/32/48: 161,280` each, total 725,760 bins (= 360 replicas × 2,016),
   agrees with the later fill's published totals (725,760 bins; 1,321,920
   roles); the residual mass is constant at 162,900 across both fills.
3. **Same word law.** Each package's published paid profile decomposes
   uniquely as `3,240 x L3 + x (L4-L3) + idle residuals`, with `x` derived
   independently from rank-1, rank-3 and rank-4 coordinates giving exactly
   the published fourth-call counts (1,080 and 1,090).
4. **Independent moment reproduction.** A fresh Decimal bisection of
   `sum_r n_r (r/73)^(1-a) / (896*360) = 1` (no reuse of either package's
   solver) reproduces all three published roots inside their own brackets:
   pooled optimum `0.001730980255989036959962261...` (the ceiling), pinned
   literal `0.001730978305075885693430489...`, and the later head
   `0.001730979115670792472760579...`.
5. **Transfer verdict with exact numbers.** The later root stays strictly
   below the ceiling; remaining headroom is
   `1.140318244487202e-9`, i.e. 58.45% of the original
   `1.950913151266532e-9` margin. The consumed `8.10594906779330e-10`
   agrees with PR4088's published gain over its previous revision
   (`>= 8.10594906779328e-10`, checked as exact rationals).

## Reproduction

From the repository root with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fourth-entry-ceiling-transfer
python3.12 -B scripts/check_research_commit.py --package research/fourth-entry-ceiling-transfer --check-source-history
python3.12 -I -Werror -B research/fourth-entry-ceiling-transfer/verify.py
python3.12 -I -O -Werror -B research/fourth-entry-ceiling-transfer/verify.py
python3.12 -I -Werror -B research/fourth-entry-ceiling-transfer/test_verify.py
```

`verify.py` reads only the two retained packages and the selected record;
`test_verify.py` carries five rejecting controls (extra rank-1 children,
wrong stock divisor, tampered word delta, corrupted word payload, shifted
idle total). `RESULT.json` is the generated evidence snapshot.

## Scope and limits

This is a finite source-bound audit of two retained packages: premise
equivalence plus independent recomputation of their published moment roots.
Not re-derived here:

- PR4091's 841 whole-helper-pattern coverage and its three dual certificates
  are taken as published; this audit does not replay that coverage proof.
- Whether legal exchanges can reach an arbitrary idle multiset with the same
  residual total (PR4091's own open question) remains open; the transfer
  verdict is at the level of the pooled model's premises, not chronological
  attainability.
- Native, owner/phase, chronology, precision, tape, BIT and outer-transfer
  obligations are inherited unchanged; the selected #1094 record and its
  kappa `0.001672660197076918` are untouched.

## Open next questions

- Can a legal chronological exchange reach the pooled eight-pattern idle
  multiset at x=1090 (PR4091 open question 1, now with the exact remaining
  headroom `1.140318244487202e-9` stated against the retained head)?
- Do later PR4088 revisions that change any word, capacity or stock premise
  invalidate the transfer for subsequent ceilings? Any such change requires a
  new model per PR4091's own scope note.

Prepared by Nick Petalas with AI assistance. Credit Ross Richardson/PR4091
and Cinna Davis/PR4088 with their packages' full retained lineages
(Rohan Arun/PR4076, Dugongue and David Ganz/PR4085/3945, dataisfire/PR3734,
ChaloupeMusic and Erwan Secousses/PR3949/3815, and the staged-release,
solver, native, owner and transfer lineage). Apache-2.0.
