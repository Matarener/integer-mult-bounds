# Cyclic query networks preserve the pair-reader floor

An arbitrary finite two-terminal graphic network can replace an unmarked
query without breaking marked source/reader support transfer. Every edge
uses the difference of its endpoint potentials; all internal potentials
are fresh directions shared by the network's edges. [PROOF.md](PROOF.md)
proves the general rank-one interface lemma and graph corollary over every
field. The non-Fano application preserves the literal pair-reader floor
`m_A+m_B`, with arbitrary actual readers, term count and augmented rank.

The five-edge Wheatstone bridge distinguishes this from PR3524's read-once
series/parallel substitutions. Both its minimal-path and minimal-cut
co-occurrence graphs are connected, so its terminal-connectivity predicate
has no read-once AND/OR formula. This is a changed cyclic-sharing hypothesis,
not a larger search inside the old operation history.

Two separate implementations agree on all 1,098 edge subsets of K2 through
K5 and all 15 bridge-expanded representative/query placements, with 512
query subsets per placement. The primary uses rational/GF4 elimination.
The second checks exact integer path/cut witnesses, rational determinants,
GF4 annihilating functionals and graph-cut subset collapse. [RESULT.json](RESULT.json)
freezes their evidence. The unbounded theorem follows from the written proof.

[WITNESS.json](WITNESS.json) is a literal nine-term six-port operator with
factor ranks `(5,5)` and endpoint `diag(1,0,1,0,0,0)`. Its separate rectangular
charges are `[2,4,2,0,2,0,2,2,2]`, totaling 16 against floor 4. It is a losing
control, not a claimed optimum. No cheaper decoder, physical supplier,
new kappa or selected-frontier change is established.

## Reproduction

Use CPython 3.12 and the standard library from the repository root. Set
`TMPDIR` to an owned output directory for controls and registered replay.

```sh
python3.12 -I -O -Werror -B research/p112-graphic-query-transfer/verify.py
python3.12 -I -O -Werror -B research/p112-graphic-query-transfer/independent.py
python3.12 -I -O -Werror -B research/p112-graphic-query-transfer/test_controls.py
python3.12 scripts/research_package.py --package research/p112-graphic-query-transfer --check-only
python3.12 scripts/research_package.py --package research/p112-graphic-query-transfer
python3.12 scripts/check_research_commit.py --package research/p112-graphic-query-transfer --check-source-history
```

The direct commands print `PASS_` and reject mismatches under `-O`. Four
mutations trigger eight failing optimized CLI runs. Four positive runs
pass before/after restoration. Controls use owned regular copies with
separate inodes and leave source hashes unchanged.

The four declared predecessor inputs are included by the official exporter.
Direct replay needs only that Git-free export and CPython, with no network
or foreign Git objects. Metadata and source-history commands need Git.

```sh
python3.12 scripts/export_research_package.py export \
  --package research/p112-graphic-query-transfer --ref HEAD \
  --output /path/to/owned/output/graphic-query.tar
python3.12 scripts/export_research_package.py check /path/to/owned/output/graphic-query.tar
```

Extract into a new owned directory, retain `.research-export.json`, and run
the three direct commands there. [VALIDATION.md](VALIDATION.md) gives the
check boundaries and code resource bounds.

## Sources and credit

[SOURCES.json](SOURCES.json) binds the exact canonical base, catalogue,
selected record and all inherited mathematical inputs. [SOURCE-CLOSURE.json](SOURCE-CLOSURE.json)
records origin commits, paths, blobs and SHA256, including PR3506's original
proof/template origins. These are used premises, not comparisons. Existing
predecessor files and notices are unchanged.

Credit stays with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question and the actual-reader lineage through PR3414, PR3463,
PR3472, PR3489, PR3491, PR3505 and Nick Petalas's PR3506/PR3513/PR3524.
This package adds the rank-one interface lemma, graphic closure and cyclic
control. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can directions shared between different old query ports reduce the literal
  tariff? Start with an exact multiport operator and both rectangular bills.
  The single-port collapse does not cover this boundary.
- Can a field-sensitive single-port gadget defeat the marked implications?
  Exhibit a differing terminal-recovery subset first. Failure of transfer
  alone would not establish a cheaper decoder.

[TASK.json](TASK.json) states relevance, first steps and blockers. Acquisition,
coefficient execution, dirty restoration, frames, hosting, precision, stock,
compiler/all-size admission and complete consumers remain separate obligations.
