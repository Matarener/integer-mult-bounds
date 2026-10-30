# Sharp five-term pair-reader floor over every field

Every realization `aa^T+bb^T=sum u_i q_i^T` with at most five actual terms
pays at least `m_A+m_B` in complete-plane rectangular binary Gram rank, when
a,b are two disjoint alternating-half indicators in any even binary-orthonormal
partition. Both factors may have arbitrary external values and directions.
The two original terms attain equality. Thus disjoint replacements of this
kind retain the literal bill `2n`, or 224 for a 112-port partition.

[PROOF.md](PROOF.md) gives the universal argument. Its new finite certificate
classifies all 23 simple seven-point rank-three incidence types: 22 have
explicit GF16 representations, and the remaining non-Fano type admits the
two-marked-target support transfer from PR3506. An independent construction
matches all 8,390 labeled line systems, including the single rank-two orbit.
Both checkers verify 2,816 subset ranks and all 21 marked non-Fano pairs.
[RESULT.json](RESULT.json) records their exact counts; [TEMPLATES.json](TEMPLATES.json)
contains the field columns and line masks.

This closes the five-term pair gap left by PR3489 and PR3506. It is a scoped
negative result with exact finite certificates, not a global P112 decoder
floor. Six terms, three or more targets, altered fitting matrices and shared
physical operations remain outside the theorem. Native execution, restoration,
hosting, precision, compiler/all-size admission, the full consumer invoice,
both suppliers and the outer theorem are unproved here. No new kappa or
selected-frontier change is claimed. Independent human and formal proof-kernel
review are unclaimed.

## Reproduce

Python 3.12+; standard library only. From the repository root:

```sh
python3 -I -O -Werror -B research/p112-five-term-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-five-term-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-five-term-reader-floor/test_controls.py
python3 scripts/research_package.py --package research/p112-five-term-reader-floor --check-only
python3.12 scripts/research_package.py --package research/p112-five-term-reader-floor
python3 -B scripts/check_research_commit.py --package research/p112-five-term-reader-floor --check-source-history
```

Expected prefixes are `PASS_FIVE_TERM_PAIR`, `PASS_INDEPENDENT_FIVE_TERM`, and
`PASS_FIVE_TERM_CONTROLS faults=7 optimized_cli=18 copy_controls=2 source_immutable`. Scientific
checks use explicit exceptions and remain active with `-O`. The fault suite
uses private regular copies and leaves source bytes unchanged. Set `TMPDIR`
to a session-owned directory when keeping temporary outputs in one location.
[VALIDATION.md](VALIDATION.md) records the checks and bounded implementation limits.

The three direct commands also work in a Git-free committed export. The generic
metadata runner and source-history preflight need Git history; they are
separate checks. Export the committed package with the repository helper:

```sh
python3 scripts/export_research_package.py export --package research/p112-five-term-reader-floor --ref HEAD --output /path/to/session/five-term.tar
python3 scripts/export_research_package.py check /path/to/session/five-term.tar
```

Check the archive, extract its regular files into a fresh session-owned directory,
and run the same three direct commands from that export root. No external input,
foreign Git object, network service or undeclared scientific module is needed.
`VERIFY.json` contains the complete package-local runtime closure.

## Sources and credit

Canonical baseline `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
`TASK.json` records the changed scope of the coverage-law-change card: close a
released literal-pair proof gap rather than claim a new coverage law. The card's
first working ceiling control is existing planning arithmetic, not new science.

Philippe Van Velzen's PR3345 supplies the expanded-identity method. Credit also
stays with ctoth, Tekalign and the paired-plane/actual-reader lineage, including
PR3414, PR3463, PR3472, Nick Petalas's PR3489 and PR3506, and the complementary
PR3491/PR3505 representability criteria. This contribution adds the exhaustive
seven-point classification and its composition into the full five-term theorem.
It does not republish PR3505's arbitrary-target sufficient criterion as new.

The unchanged PR3506 proof and three GF4 templates are retained locally with
exact origin/blob/SHA256 receipts in [SOURCE-CLOSURE.json](SOURCE-CLOSURE.json).
The templates are proof-premise inputs rechecked here; the predecessor proof
is comparison/credit context. Its pending origin commit is not an ancestry pin
or a runtime dependency. [SOURCES.json](SOURCES.json) contains only canonical
baseline provenance. No frozen predecessor package is edited.

Nick Petalas. Apache-2.0.

## Open next questions

- Six terms first permit factor ranks `(4,4)`. Start with one exact cheaper
  literal factorization and its actual rectangular bill, or prove a rank-four
  support-transfer lemma. Neither is supplied here.
- A changed consumer, fitting matrix or shared operation may leave this tariff
  model. Specify the new endpoint and price coefficient delivery, dirty
  restoration and the full consumer before expanding native implementation.

The concurrent three-target non-Fano transfer-boundary question is disjoint:
this theorem uses exactly two independent marked indicators. A failed transfer
for more targets would not by itself exhibit a cheaper literal factorization.
