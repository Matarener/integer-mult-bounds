# Independent QQ16 consumer-budget audit and caller applicability

The obstruction in [PR3908](https://github.com/CrocSwap/integer-mult-bounds/pull/3908)
is confirmed for its stated equal F0/B_1_2 pair, #2707 decoder and centre-64
coverage model. Even after favorably dropping all eight reported rank-eight
children, the exact optimistic moment at the selected saving lies in

```text
[1.000097677678, 1.000097678284] > 1.
```

This package independently expands the raw producer programs and decoder
word, binds the first F0 caller audited in PR3932, and uses rational
midpoint/trapezoid logarithm bounds instead of the predecessor's atanh
method. It supplies quantitative changed-contract thresholds to guide the
next research decision. It does not implement a supplier or change kappa.

## Source and caller binding

Canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, revision 6.
Audited PR3908 head `0d8880e38ed7c88d70eec6a48e5aa829d0fb22f3`.
The seven original package files are retained unchanged in
`vendor/PR3908.tar.gz` for an actual offline predecessor replay, with exact
hashes and credit in PREDECESSORS.json. No predecessor executable is imported
by the independent checker; `ceiling.py` is used only by that retained replay.

The literal profiles are F0 `{1:2420,2:418,3:432,4:142,5:82}` and B_1_2
`{1:2436,2:418,3:432,4:142,5:82}`. The literal decoder word contains 336
rank-one lines across the pair. Its functional/native proof is inherited.
All external executable inputs have base-commit Git blob/SHA256 pins and
explicit replay invalidation in SOURCES.json and VERIFY.json.
The count check also covers all nine F and 28 B native cases. With the
decoder rate fixed at 168 per call, even the cheaper all-F profile remains
above one; F/B reweighting alone does not remove the obstruction. A different
global decoder rate is an unproved changed premise, not excluded here.

F0 event 9894 is `['climb','A',546,0,4,1]`, followed by
`L546 -= L561` in frame 4. The complete preceding-event hash agrees with
[PR3932](https://github.com/CrocSwap/integer-mult-bounds/pull/3932), head
`12c324c576821f78070627c5eeb684d03704e20e`. Thus the local caller belongs
to the profile screened here. Physical admission and the full outer
schedule are separate. Changed call weights, decoder reuse, coverage or
actual replacement of a recursive tariff require a new complete invoice.
Faster scalar/axis tape work alone supplies none of those changes.

## Decision and quantified alternatives

Pause the unchanged recipe as a route to the selected target. Retain its
local numerical and tape components as useful interface results. The
following are certified *optimistic screens*, not implemented alternatives:

| Assumed model | Largest integer decoder rank-one count per pair passing relaxation | Next count already excluded |
|---|---:|---:|
| Centre 64, eight rank-eight children waived | 121 | 122 |
| Centre 64, eight rank-eight children retained | 61 | 62 |
| Hypothetical centre 63, eight rank-eight children retained | 363 | 364 |

The existing decoder has 336. A decoder-only revision must therefore remove
at least 215 calls in the first case or 275 in the second. These are necessary
budget targets, not lower bounds on all decoders. Odd totals allow fractional
per-call averages; an equal integer split restricts the limits to 120/60/362.

Keeping all 336 calls and the reported rank-eight children, a hypothetical
one-unit centre reduction per call gives an optimistic moment in
`[0.999987387153,0.999987387763]`. Its additional normalized-cost allowance
is only about `0.0000126126`. Under the special unchanged-coverage accounting
where extra rank-one calls displace idle mass, 27 extra calls per pair still
pass; 28 fail. This is not a tariff for tape actions.

The next useful question is whether an actual F17-native consumer or an
identity specific to the fixed native operators can remove the required
work without repaying it elsewhere. Simply setting centre=63 is not such
a construction. Neither this package nor PR3908 supplies that consumer.

## Reproduce and verification boundary

```sh
python3 -I -Werror -B research/qq16-consumer-budget-independent/verify.py
python3 -I -O -Werror -B research/qq16-consumer-budget-independent/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-consumer-budget-independent
```

Expected: `PASS_QQ16_CONSUMER_BUDGET_INDEPENDENT no_new_kappa`, eleven
behavioral groups and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
RESULT.json contains the complete rational enclosure receipt; PROOF.md
derives the bounds and scope; actual environments, execution and unrun
obligations are recorded in VERIFICATION.json. No network or unmerged Git
object is needed by the standalone scripts once declared base inputs are
provided. The source archive permits exact predecessor replay offline.

The review checks PR3908's atanh positivity, exponential truncation,
rank-mass relaxation and selected-exponent implication. It also reproduces
the predecessor registered replay and its source-history preflight on a
full-history checkout. The independent implementation uses integral bounds
and a positive geometric exponential tail; all proof arithmetic is rational.
Controls cover omitted decoder work, illegal rank 52, threshold repayment,
source and receipt corruption, changed caller wire and deleted literal line.

No full F0/B1 algebraic correctness replay, inherited native/bridge proof,
decoder operator replay, huge payload execution, selected cold replay,
Lean, full physical invoice, human review or supplier admission is claimed.

## Open next questions

**One named changed consumer contract.** Pin a downstream F17-native demand
map and compose it with the literal decoder. Identify the specific output
combination or fixed-native identity that removes real centre operations,
with its owner/frame chronology, arbitrary dirty state and required return.
Then derive the changed aggregate coverage identity and complete moment.
The narrow target here is one average centre mass unit per call, with all
replacement charges inside the certified allowance; broader changes need
their own screen. Stop if no actual demand or eliminated work is exhibited.

This must distinguish the proposed contract from the selected first-transcript
counterexample (#2391), owner-local repair bound (#2461), copied-demand rank
floor (#3120) and pending uniform-oracle/selected-coverage audit (#3873).
Their scopes were inspected as adjacent evidence, not independently verified
here or automatically transferred to a new QQ16 endpoint.

Only after a changed complete budget survives should this stream expand the
physical child-plus-ADD connection from #3932: actual tape windows and heads,
entry grid/range, both monomials, movement/address/control, adjacent ADD and
eventual restoration. A proof that direct bit implementation replaces a
recursive charge is another changed hypothesis and needs an all-depth cost
transfer. Unknown costs remain unknown. TASK.json records the family decision.

## Credit

1337isnot1337's #3908 exact obstruction; dcharb78's #3181 profile/cost-screen
branch; ywz65's #2707 decoder; Ali Romman and the conserved QQ16/native
lineage; Douglas Colkitt's selected coverage-ceiling model; Sagar Thakrar
and the coverage identity lineage; Nick Petalas's producer/decoder numerical
work; the retained native, supplier and source notices. This contribution
adds a different rational enclosure, literal count/caller binding and budget
thresholds, not the original obstruction or decoder theorem.

Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Independent software/mathematical checking is distinct from independent
human review or formal-kernel acceptance. Existing frozen sources, shared
verifiers, selected frontier and other contributions are unchanged.
