# B04 range-review validation

The final source was executed with bundled CPython 3.12 on the three unchanged
compressed sources now staged as `frozen/parent/WORD.json.gz`,
`frozen/candidate/WORD.json.gz`, and `frozen/controller/WORD.json.gz`.
Each subprocess had an enforced 60-second timeout.

From the package root, the equivalent commands are:

```sh
python3.12 frozen/reviews/range/check_range.py \
  --parent-word frozen/parent/WORD.json.gz \
  --candidate-word frozen/candidate/WORD.json.gz \
  --controller frozen/controller/WORD.json.gz \
  --output frozen/reviews/range/CHECKS.json.gz

python3.12 -O frozen/reviews/range/check_range.py \
  --parent-word frozen/parent/WORD.json.gz \
  --candidate-word frozen/candidate/WORD.json.gz \
  --controller frozen/controller/WORD.json.gz \
  --verify frozen/reviews/range/CHECKS.json.gz
```

Both final executions passed. Receipt generation took 2.896 seconds; optimized
complete receipt verification took 2.713 seconds. All invariants use explicit
exceptions and remain active under `-O`.

The exact receipt canonical-JSON SHA256 is:

`eff9d7a72677d9ae67f8257a99efbc67e621488220e3b14f7ba127a4409ec1d4`

The checker SHA256 is:

`4aa90c275da461cbcef95b00c6088aa599c72e7b76a6cbf9b8cadb87e45e6df5`

The compressed full receipt SHA256 is:

`0e826dec630ab3ab60592d823dd425785add331b97e4b3f1bc84e71e25510780`

The decoded controller SHA256 is:

`859cdd2a87ea6ce58eb0ccdf2ca675e77c7134d6a7bbc7d450493d1abb108271`

The compressed controller transport SHA256 is:

`ff50e2df9b5a0ecb5e4a3aa24a5b93ac49f7c2b4fd3d28295e6d5a8f6154027f`

All four range/adjoint scans cover all 16,102 records. Their checks include
every opcode and paid rank; all 651 public entrance columns are represented
in the exact sparse range matrices. The full adjoints operate on 652 extended
coordinates. The controller recurrence covers all 56 events and 63 added
source-code factors. The binary abstract schedule checks all eight independent
formal bank columns.

After source authentication, each orientation executes actual source-specific
controls for the wrong adjoint, reversed suffix order, ignored COPY and
incorrect uniform error signs. It independently propagates saved impulse,
range-peak and suffix-row witnesses forward. It also directly propagates the
simultaneous error signs that attain the three reported aggregate categories.
Thus these controls test the linear calculation, not merely authentication.

An independent read-only comparison with the retained historical range JSON
confirmed both exact ordered integer upper bounds, local/source prefix
numbers, controller bit lengths and terminal bit lengths. The complete parent
block envelopes agree after adding the identically zero row, which the older
ADD-only envelope omitted. `SOURCE-DEPENDENCIES.json` records these comparisons
and all source hashes.

A preliminary verification call exposed a receipt-comparison bug: Python
tuples/integer JSON keys were compared directly against decoded lists/string
keys. Verification was changed to compare canonical JSON. That preliminary
failure and the final successful reruns are retained in
`VALIDATION-RESULT.json`. It did not change any mathematical value.

This validation is finite exact computation and written conditional proof. It
is not formal-kernel validation, hosted CI, a physical rounding test, a native
child implementation, or supplier admission.
