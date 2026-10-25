# Query series expansions preserve the pair-reader floor

The non-Fano two-target support transfer survives any finite sequence of
series and parallel rewrites of unmarked queries. Therefore every literal
pair factorization in this expanded family has complete-plane reader bill
at least `m_A+m_B`, with arbitrary actual reader values, external directions,
term count and augmented rank. [PROOF.md](PROOF.md) proves the closure for any
fixed number of independent marks and applies the retained two-mark premise.

This addresses a specific part of PR3513's six-term handoff. It does not
classify arbitrary rank-four dictionaries. Marks cannot be split, and every
series split must introduce a direction independent of the previous ambient
span. The proof includes a counterexample to dropping that hypothesis.

The 255-case certificate covers all 21 non-Fano marked pairs, all 210
one-step rewrites, and 24 nested two-step cases. Two separate implementations
agree on 7,424 source and 17,216 reader premises and the ordered result hash.
The unbounded claim follows from the written induction, not those tests.
A literal six-term control has both factor ranks four, exact endpoint
`diag(1,1,0,0)`, and rectangular charges `[2,0,4,4,2,2]`. Its bill 14 loses to
the pair floor 4; no minimum for the expanded dictionary is claimed.

No cheaper decoder, physical supplier, new kappa or selected-frontier change
is established. [VALIDATION.md](VALIDATION.md) records the checks and limits.

## Reproduction

Use CPython 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -O -Werror -B research/p112-query-series-transfer/verify.py
python3.12 -I -O -Werror -B research/p112-query-series-transfer/independent.py
python3.12 -I -O -Werror -B research/p112-query-series-transfer/test_controls.py
python3.12 scripts/research_package.py --package research/p112-query-series-transfer --check-only
python3.12 scripts/research_package.py --package research/p112-query-series-transfer
python3.12 scripts/check_research_commit.py --package research/p112-query-series-transfer --check-source-history
```

Each direct command prints a `PASS_` marker and fails by exception on a
mismatch, including under `-O`. Set `TMPDIR` to an owned output directory if
the platform's default scratch location is unsuitable. Direct replay needs
only this package's regular files and the interpreter. The registered runner
and history check need the Git checkout. [VERIFY.json](VERIFY.json) declares
the commands; [RESULT.json](RESULT.json) freezes exact finite evidence.

The package exporter can reproduce committed direct-replay bytes:

```sh
python3.12 scripts/export_research_package.py export \
  --package research/p112-query-series-transfer --ref HEAD \
  --output /path/to/owned/output/query-series.tar
python3.12 scripts/export_research_package.py check /path/to/owned/output/query-series.tar
```

Extract into a new owned directory, preserve `.research-export.json`, and run
the three direct commands there. Export integrity is separate from the
mathematical replay. No network or foreign Git object is needed by them.

## Sources and credit

[Source closure](SOURCE-CLOSURE.json) retains the exact PR3506 proof and GF4
template bytes at `9e41a7a45adc282ca2bd6b024dfbe726150ab13b`, including origin
paths, Git blobs and SHA256 values. Both are mathematical premise sources;
the template is also runtime data. They are not comparison-only records.
The new proof restates their marked implication and both checkers recheck its
finite premises. [Comparisons](COMPARISONS.json) separately identifies PR3513's
handoff and PR3505's sufficient full-representability criterion. Reversing
our rewrites recovers the non-Fano minor, so that sufficient criterion still
does not apply to this expanded family.

Credit stays with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question, and the retained actual-reader lineage, including PR3414,
PR3463, PR3472, PR3489, PR3491, PR3505 and Nick Petalas's PR3506/PR3513.
Only the query-rewrite closure and its higher-rank application are new here.

## Open next questions

- Can a different rank-four six-query pair configuration lower the actual
  tariff? Give a literal operator and both rectangular bills, or a marked
  transfer obstruction outside this family. No such witness is supplied.
- What happens when a marked target is split? State the changed target/source
  contract and test its span implications. The old-coordinate collapse proof
  does not apply unchanged.

[TASK.json](TASK.json) records relevance, first steps and blockers. Native
acquisition, coefficient delivery, dirty restoration, frames, hosting,
precision, stock, compiler/all-size admission, complete consumers and outer
multiplication obligations remain open.
