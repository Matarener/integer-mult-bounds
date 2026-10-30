# Sources, attribution and overlap

This user-assigned follow-up starts from canonical
`bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision6, and the
frozen shared-source package in
[PR4068](https://github.com/CrocSwap/integer-mult-bounds/pull/4068) at
`5a34918402ae2c0c683d8820ad832970e77f6382`. That predecessor saves four
scalar ADDs and identifies the two independent dirty query inputs; it does
not claim a recursive-query saving. Its new query-sharing question motivates
this package's broader scalar-mixing model and precise fixed-join answer.

The bundled WORD and GEOMETRY are copied byte for byte from that public head.
Their paths and hashes are in [INPUT-SOURCES.json](INPUT-SOURCES.json).
The unchanged `inputs/PREDECESSOR-PINS.json` records historical lineage at
`8eefab699338b93400ca72ab22c6cf64352f7e05` and
`b628ba738802587a38e61affaa01fd188d0644f9`. Public byte-identical archives
also occur in [PR4021](https://github.com/CrocSwap/integer-mult-bounds/pull/4021)
at `c01f97ecfc7fa64847f6abd8f7b231e1df8c7b70`, as recorded in PR4068's
PUBLIC-PREDECESSOR.json. Reproduction needs only the bundled copies, not
historical local commits or checkouts.

The source lineage credits Ali Romman's R438/PR1043 substitution, Sagar
Thakrar's transported word and window analysis, PR540 frame conventions,
PR589 hosting, PR1023 width-eight hosting, and the five-terminal package.
The retained controller lineage credits DreamingOfClouds, Zhihao Chen,
eumemic and chafreaky. These constructions are inherited, not new results.
The focused source checker was written for this package without importing
the producer implementation; the full predecessor metric audit is not repeated.

## Mathematical antecedents

Jose Manuel's
[two-register-three-mix / PR2108](https://github.com/CrocSwap/integer-mult-bounds/blob/bb4bccbf42844d2801487450727c2f63e10d1d0f/research/two-register-three-mix/README.md)
(package commit `b25eb9b6a95d8b644c582a5c0d8229bc2ffc3eb7`) is a direct
antecedent: two registers, arbitrary group and field, at most three
nonmonomial scalar blocks, and full group-diagonal endpoint admit unary
routes without increasing a subadditive tariff. A two-query word has at
most three scalar blocks, so the no-ancilla two-query case is not presented
as a new general discovery. Its bounded operator-separation argument also
motivates care about formal versus actual address actions.

The source-archived
[S4 four-role census](https://github.com/CrocSwap/integer-mult-bounds/blob/bb4bccbf42844d2801487450727c2f63e10d1d0f/research/s4-noncommuting-threecycle-r4-seeda27b/README.md)
at package commit `90405b9498e4abfdd7d0eececcf11c7e83c6d13b`
uses formal F2[S4], four dirty roles and adjacent-transposition labels to
certify four-call minima for eight three-cycle target pairs. Its fixed
alphabet, role count and unit tariff differ from the present actual
rank-two involution pair and arbitrary finite clean/dirty ancilla allowance.

The
[binary-affine register bound](https://github.com/CrocSwap/integer-mult-bounds/blob/bb4bccbf42844d2801487450727c2f63e10d1d0f/research/binary-affine-register-bound/PROOF.md)
at `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2` is a precedent for
augmentation normalization and representation-rank bounds with arbitrary
restored dirty registers. Its homogeneous address representation has
characteristic two. Rational dyadic address matrices cannot simply be
substituted into that representation over the payload field F2.

The
[nonlinear frame-cut bound](https://github.com/CrocSwap/integer-mult-bounds/blob/bb4bccbf42844d2801487450727c2f63e10d1d0f/research/nonlinear-frame-cut-bound/README.md)
at `78a1810e44bf08f845252cfe4c785ccc967c07a2` gives weighted cut
certificates and a common-flag corollary. The present pair has
`tr([P,Q]^2)=-1`, excluding simultaneous triangularization over any
characteristic-zero extension, so that common-flag corollary is not used
to certify this pair. Its general certificate framework is not refuted.

These sources were read for attribution and scope; their full suites were
not rerun or silently imported as broader theorems. Defect rank,
telescoping, generic-point separation, the sign quotient and Sylvester's
inequality are standard tools. The contribution here is their complete
source-bound tariff argument, including clean input columns and the
explicit field-uniformity premise, together with reproducible controls.

## Interface leads and limits

Hanson Sun's [PR1522](https://github.com/CrocSwap/integer-mult-bounds/pull/1522),
building on Ross Richardson's PR953 and Wentao Li's PR840, already gives
restored source tours for distinct additive outputs. These do not supply
the missing action on two independent dirty helper inputs. The tagged
joint-child proposal in [PR1764](https://github.com/CrocSwap/integer-mult-bounds/pull/1764)
was read through its cached metadata/body as an interface lead; its source
implementation was not replayed or used as proof of an admitted BIT tariff.
Our product-carrier and tagged-bank discussion is explicitly conditional.

The entry overlap scan at 2026-10-19T21:06:25.817477Z covered797 open PRs
and2627 Discussion records with complete pagination and no warnings. It
searched public titles/bodies and local package notes, not every code diff
or all closed PRs; it is not a novelty certificate. The three coordination
hubs and relevant nearby package statements were read. Local standalone
scope and review records preserve the full scan and exact source reads.

The selected record and its inherited supplier assumptions remain unchanged.
No global BIT lower bound, native supplier admission, outer recurrence
improvement, human certification or new kappa is claimed. Ross Richardson,
with substantial OpenAI Codex assistance and separate AI review. Apache-2.0.
