# Conditional reconciliation of the P112 b=5 caller cells

Six fixed published contracts account for all38 historical TWOSIDE (5,5)
survivors and76 of77 historical (5,6) survivors. These are nested cells,
with77 distinct profiles. This package supplies exact caller composition,
source authentication and independently reconstructed coverage; predecessor
exclusions retain their credit.

The only row uncertified **by this inventory** is `2^5,6,7^5`. Its eleven
independent pieces require code-intersection dimension5. The six small
pieces force quotient dimension6 and have common support cap30; all462
six-piece subsets have individual-capacity sum at least30. Five independent
rank-seven residual directions are therefore required after that ONE common
support. This is a precise interface, not a global-open or realizability
claim. A separate concurrent investigation owns its common30 geometry.

[PROOF.md](PROOF.md) proves deletion and quotient transfers and states every
conditional input. [RESULT.json](RESULT.json) retains all six rule attempts
for every row, including failed assignments, minima and indexed witnesses.
The original PR3154 filter and an independently written filter agree across
both complete domains (7,798 and12,166 multisets). A separate implementation
checks all690 rule/row combinations using different enumeration order and
packing logic. Controls reject source/metadata/receipt mutations under
optimized Python and exercise strict excess, deletion and common-cut limits.

## Reproduce

Python3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-b5-caller-inventory
```

The three direct scripts are `verify.py`, `independent.py` and
`test_controls.py`, with `-I -O -Werror -B`. All compare committed receipts;
none regenerates frozen inputs. The package and declared canonical-main
inputs suffice for a Git-free direct replay. Pending PR3931/3960 proof texts
are retained locally with exact public heads and hashes; no pending Git
objects or network are needed. Registered metadata additionally checks
historical provenance against canonical main.

## Open next questions

Bind the separately established common30 result to the literal
`2^5,6,7^5` interface, after its finite coverage and characteristic-zero
argument are reviewed. A span bound below5 would close the final row of
this fixed inventory. If a relaxation fails, retain actual common-support
and quotient-coefficient obligations rather than treating it as a literal
counterexample. This package stops before that separate geometric theorem.

## Credit and limits

DreamingOfClouds/PR3154 supplies TWOSIDE, the exact original filter and
completed beta7p2 geometry. Nick Petalas supplies PR3262, PR3283 and PR3205,
and the earlier PR3282/3289 caller-composition framework. Chris R /
Clear1nsight with substantial OpenAI Codex assistance supplies PR3931/3960.
The retained E8/P112 lineage includes joaqcoo. [PREDECESSORS.json](PREDECESSORS.json)
and [SOURCES.json](SOURCES.json) preserve exact sources and usages.

The new conditional inventory was produced by Chris R / Clear1nsight with
substantial OpenAI Codex assistance, Apache-2.0. Separate implementations
and same-session review are not independent human or formal-kernel approval.
Predecessor heavy scientific replays and complete decoder reduction remain
unrun here. No full C5, global decoder floor, supplier or new kappa is claimed.
