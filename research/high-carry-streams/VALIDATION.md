# Validation

Implementation and receipt freeze: `8376965a54f12604c23c45ca458d606d1c1f6f28`.
The complete registered CPython 3.12.14 replay passed at this commit. The
publication amendment changes only this validation record.
Base: 6f100d4bb5083f8c35d96fd95a539811c62f245c. Priority revision 6, seed 6.

The author ran the complete kernel, route, catalogue and optimized control
suites with CPython 3.12.14 on Linux. The same-input benchmark uses that runtime
and three alternating fresh-process pairs. See BENCHMARK.json for every sample.
No formal kernel, independent human review, selected cold replay, whole-machine
execution or new κ is claimed.

Overlap metadata at entry covered 249 open PRs, 2,761 closed/merged PRs and
2,171 Discussion records with complete pagination. A later refresh covered 256
open PRs and the latest #2319 replies; main was unchanged. PR3340 addresses the
separate fitted native bridge. These metadata checks do not cover unpublished
work or every code diff. The only open issue remained #913's clarity concern.

## Committed verification

- All four registered suites pass, including the 1,123-chart catalogue census
  and optimized controls; no artifact generation occurs during verification.
- A read-only Git-free export of all 51 package/input files passes the optimized
  CPython 3.14.7 control suite and all 96 complete kernel comparisons. Every
  exported byte matches the scientific commit.
- An AST comparison verifies that the adapted execute function is identical
  to PR2915 except for the intended dispatch name. This was a separate local
  check, not a formal proof or a registered additional suite.
- `git diff --check` passes. Runtime constructors and numerical inspection are
  forbidden inside the physical fixtures. Counter traffic and source-column
  provenance are observed together, without replacing the semantic observer.

The registered comparison covers 6,624 independent kernel columns and 8,893
complete-route columns. The opt-in path has no measured I/O regression in the
96 retained pairs; that finite observation is not a universal timing theorem.
The direct negative-carry cases use 66.8–95.1% less physical I/O in these inputs.

The source/archive merge and hosted CI remain separate from scientific admission.
Hosted CI status is reported in the PR rather than inferred from local success.
