# The R439 scalar drop leaves the paid histogram in place

**Partial. No new exponent.**

The four recorded words have native ADD counts 11,783, 11,515, 11,500 and
11,715. Each word has nine copies and nine erasures, and every copy rank is
7. The owner check compares every word with one profile

```text
{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
```

whose rank mass is 5,129. The certificate's `new_kappa_claim` is false.

The ADD counts are four different numbers. The copy ranks are not. Under the
published check, a scalar drop that leaves those ranks in place does not
change the paid histogram.

## What was executed

The checker reads the certificate and the profile constant. It does not
replay the 661 columns.

The card's orientation command is the R439 verifier. This package uses the
histogram sentence and the certificate fields that verifier records.

## Scope and evidence

Original card: `scalar-to-moment`, priority revision 6, refined to this
histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the note, the certificate and the profile
check. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/r439-scalar-histogram/verify.py
python3.12 -B research/r439-scalar-histogram/test_verify.py
python3.12 -B scripts/research_package.py --package research/r439-scalar-histogram
```

## Open next questions

These four ADD counts share this histogram. Another scalar pass would leave
this obstruction.

## Credit

Sagar Thakrar prepared the R439 note with Anthropic Claude. That note credits
Aaron Wang for the PR 1015 block programs and Ross Richardson for the PR 923
frame-520 program.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
