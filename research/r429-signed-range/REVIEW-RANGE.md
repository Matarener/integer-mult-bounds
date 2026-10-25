# Independent B04 range and atomic-defect review

The selected sign change lowers the conditional controller range upper bound,
but worsens forward local range and forward additive-error amplification. The
inverse improvement is substantial for ADD defects. It gives no improvement
to the exact inverse MOVE/COPY aggregate in this atomic model.

The frozen parent and candidate each have 651 public inputs, 429 dirty helpers,
one private coordinate, 16,102 records, three COPY/ERASE pairs, and paid rank
mass 4,989. The candidate changes exactly 23 of the 47 phase-23 ADD signs.
No sign search is performed by this review.

| Exact local quantity | Parent forward | Candidate forward | Parent reverse | Candidate reverse |
| --- | ---: | ---: | ---: | ---: |
| Maximum prefix row L1 | 34,285 | 80,639 | 5,839,860 | 239,014 |
| Maximum suffix row L1 | 136,729 | 138,976 | 7,658,958 | 324,924 |
| Maximum single destination impulse | 3,457 | 3,935 | 86,476 | 4,366 |
| Exact aggregate, ADD+MOVE+COPY | 880,068 | 1,081,994 | 34,848,225 | 1,255,309 |
| Loose sum of individual maxima | 965,052 | 1,099,680 | 34,872,847 | 1,289,381 |
| Exact aggregate, MOVE+COPY only | 383,045 | 479,557 | 1,239 | 1,239 |

The aggregate is `max_output sum_event |suffix_entry|`, not
`sum_event max_output |suffix_entry|`. It is exact for arbitrary independent
scalar additive defects after the indicated atomic operations. Each aggregate
has a saved simultaneous-error sign witness and a direct forward attainment
check.

All assignments are interpreted literally in the extended linear model:
COPY overwrites the private coordinate with the source and ERASE assigns zero.
In the main aggregate ERASE defects are zero. **This entire assignment premise
is conditional:** zero ERASE defect does not prove that an actual rounded
private register has returned to an erasable zero state. Actual rounding rules,
native-child error support, interior prefixes and physical cleanup are absent.

The per-event comparison is also mixed. In the forward word, 1,556 corresponding
single-destination weights increase, 667 decrease and 13,879 are equal. In the
reverse word, 842 decrease and 15,260 are equal; none increases. All reverse
MOVE/COPY rank-group constants are unchanged.

The controller calculation independently reconstructs complete local block
prefix envelopes and follows all 56 controller events, including every one
of the 63 additional code factors. Hosted helper entrance magnitudes are
bounded by the largest **current encoded bank** magnitude.

| Conditional coefficient upper bound | Parent | Candidate |
| --- | ---: | ---: |
| Ordered controller bit length | 458 | 401 |
| Ceiling to a multiple of 64 | 512 | 448 |
| With nine inverse-code factors per terminal bank | 601 | 519 |
| Terminal ceiling to a multiple of 64 | 640 | 576 |

These are coefficient-growth upper bounds under admitted isometric native
charts and exact restoration. They are not finite-precision guard counts,
physical register sizes, exact global maxima, or supplier admission.

## Source binding found during review

The current words have a selected source code of 1,499 actual ADD records in
phases 21–24. The controller JSON retains a historical 6,372-gate binary code.
The two binary endpoints differ in nine source rows. Therefore its stored gate
list cannot be used as the implementation underlying the new range numbers.

The checker instead binds every abstract sweep to the selected local source
code or its literal inverse. It verifies that the local binary interfaces are
`(x,y,h)->(A x,y+A x,h)` and `(x,y,h)->(A^-1 x,y+x,h)`. It independently evaluates
the complete abstract schedule on eight formal bank columns in the free
noncommuting polynomial algebra over GF(2), obtaining the common endpoint
`diag(G8...G0)`. This justifies replacing the abstract source maps in the binary
VALUE schedule. Native physical charts, ownership and integer terminal identity
are separate obligations.

The older `root-rounding/SUFFIX-WEIGHTS.json` belongs to the different
660-public-input, 438-helper, six-copy word with gzip digest `33d5c73f...`.
None of its weights is reused. All four present suffix calculations are fresh
and bind to the exact 651-input source bytes.

## What the checker establishes

`frozen/reviews/range/check_range.py` uses only the Python standard library and imports no producer
code. It authenticates both words and the decoded controller bytes; JSON and
gzip JSON controller transport are supported. It then:

1. Reconstructs exact sparse block-prefix envelopes, endpoint blocks and source
   code matrices, including literal inverse and ideal private/helper cleanup.
2. Replays every ordered controller factor with full bank bounds and records
   every intermediate recurrence value.
3. Scans every atomic suffix with correct COPY/ERASE adjoints, saving every
   individual influence, opcode/rank row-sum vector, full-column-stream digest,
   exact aggregate and attaining witness.
4. Cross-checks source-specific peak impulses, range/suffix sign witnesses and
   simultaneous-error witnesses by forward scalar propagation.
5. Detects wrong-adjoint, reversed-order, ignored-COPY and error-sign controls
   after authentication, on the actual source events.

The full receipt is deterministic and compressed without timestamps. It
contains complete operation/rank coverage, all block-envelope triples, all
16,102 individual weights per orientation, aggregate rows and witnesses.
`frozen/reviews/range/SOURCE-DEPENDENCIES.json` records exact source and historical
receipt hashes. `frozen/reviews/range/VALIDATION.md` gives the executed commands
and outcomes. The complete receipt is `frozen/reviews/range/CHECKS.json.gz`.

The calculation covers the two pinned finite words, all real entrance values
in the stated scalar model, and every independent additive-defect choice in
that model. The proof of the error formula and exact aggregate is all-input
linear algebra. The constants are finite exhaustive integer computations.
No formal-kernel proof is supplied.

## Reproduction

From the package root:

```sh
python3.12 frozen/reviews/range/check_range.py \
  --parent-word frozen/parent/WORD.json.gz \
  --candidate-word frozen/candidate/WORD.json.gz \
  --controller frozen/controller/WORD.json.gz \
  --verify frozen/reviews/range/CHECKS.json.gz
```

Use `--output NEW-RECEIPT.json.gz` to write a fresh deterministic receipt.
Transport digests are included, so a receipt made from raw controller JSON
differs in its transport digest from one made from the unchanged compressed
controller. The decoded controller digest and all mathematical results agree.

There is no new sign optimization, general optimality claim, global defect
constant, concrete rounded implementation, tape/stock invoice, terminal
correctness admission, or new multiplication exponent.
