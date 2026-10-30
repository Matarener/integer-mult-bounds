# Compact universal certificates for rectangular dirty circuits

This contribution was produced by Nick Petalas. Apache-2.0.

This is a scoped written proof and exact implementation of the independent
rectangular-operator interface missing from zxv's [PR5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235).
Registers may belong to different payload spaces. An arrow has a fixed source
and target type, and every initial register is arbitrary. Equality certificates
retain all returned dirt. No supplier or new kappa is claimed.

[PROOF.md](PROOF.md) extends the predecessor's r+q dependency-state method to
this interface. Two programs need D=2r+q_left+q_right states. An equality
certificate has at most D reachable rows and finite closure equations.
A nonzero path of length k has a concrete zero/one rectangular counterexample
using one coordinate per visit to each type, totaling k+1 coordinates.
This replaces padding every type to a common square witness dimension.
It is an upper bound, not a general minimum-dimension claim.

The contribution adds the typed compact compiler, closure checker, explicit
per-type witnesses and runnable examples. Classical weighted-automata/PIT
methods and zxv's equal-space bridge retain their credit. Philipp / mightyOil's
PR1294 already proves expanded typed block identities following Charles Bethin
PR1278; that result is cited rather than reverified. Krzysztof Wójt's PR5262
handles named inverses in a common space, a different operator model. The
retained dirty-echo lineage includes androolloyd, Chafik Boukhalfa / chafreaky
PR628 and Ali Romman PR621; the tensor and universal-phase lineage retains
Cinna Davis PR4100/4088, ToikY, Sagar Thakrar and roger-sato.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rectangular-dirty-certificates
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rectangular-dirty-certificates/verify.py
```

The registered normal and optimized checks print a generated JSON receipt
with source hashes. They write no files. The finite suite covers 160 program
pairs against explicit ordered-word expansion, 86 equal and 74 different;
all 74 differences have literal rectangular matrix witnesses. It also covers
64 dimension vectors and 352 full-column or zero-input echo cases, including
zero-dimensional spaces; six dirty product witnesses through degree six;
and fourteen rejecting or discrepancy controls. The degree-six example uses
type dimensions 4 and 3, totaling seven rather than a square padded total
of fourteen. That comparison concerns this path construction only.

Run a single problem and check its inspectable certificate with a fresh output
path inside a scratch directory:

```sh
PYTHON=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$PYTHON" -I -B research/rectangular-dirty-certificates/typed_words.py \
  research/rectangular-dirty-certificates/echo.json --output /tmp/rectangular-certificate.json
"$PYTHON" -I -B research/rectangular-dirty-certificates/check_certificate.py \
  research/rectangular-dirty-certificates/echo.json /tmp/rectangular-certificate.json
```

The output path must not exist. To inspect a negative matrix witness, replace
the two example paths with `chain6.json` and its committed `chain6.certificate.json`.
Arrow endpoints are `[source_type,target_type]`. Scalar instructions require
equal types. APPLY requires a loop; QUERY permits rectangular arrows. Scalars
are integers or explicit rational strings. Order QP means P applies first.

## Scope and trust

The executable uses Q. The written theorem works over any field. Inputs are
bounded to sixteen roles, eight types, sixteen arrows and 128 instructions per
side. Exact scalar encoding caps and the trusted shared compiler are documented
in PROOF.md. A scalar-size refusal is not a verdict of equality or inequality.
The checker performs no elimination; it shares compilation and arithmetic with
the producer. The two finite oracles are separately written, not independent
human reviewers. Independent human and formal proof-kernel review are unclaimed.

Inverse, finite-group and commutation relations are excluded. So are native
implementation, nonlinear inputs, external aliases, rounding, precision,
hosting, physical tapes and a complete paid/target invoice. None of the five
selected framework assumptions is discharged, and the selected record is
unchanged. This is a changed scope from `joint-query-controller`: it supplies
an algebraic gate for mixed-width interfaces rather than a cheaper caller.
The card's selected-baseline orientation passed, with no supplier replay.

Live open/merged searches, main README searches and reservations were checked
before the advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267728).
The overlap cache covered 317 open PRs and 5858 discussion records; the local
working search omitted 8486 sparse note paths, so main was also searched
directly for rectangular certificates, typed operators and quivers. This is
bounded overlap evidence, not proof of global novelty.

## Open next questions

- Bind a mixed-width supplier's literal source and complete endpoint to this
  grammar. Start with one declared producer/consumer boundary and record all
  arrows and dirt. Native relations or unpriced physical delivery may prevent
  applying this independent-arrow test.
- Characterize the type graphs for which scalar spaces already separate all
  paths. Start with acyclic graphs, then isolate the obstruction from multiple
  cycles. This could reduce diagnostics further; no such classification or
  random-testing guarantee is supplied here.

Structured questions are in TASK.json. The first proved interface improvement
is frozen; these follow-ons are outside this contribution.
