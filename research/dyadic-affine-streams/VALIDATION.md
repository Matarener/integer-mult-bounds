# Validation record

Scientific base: 20ecf2891d80b5acf18d980b2164fb44ea7faa90 (canonical main),
priority revision 6. Sources, selected record and research guidance were refreshed;
all remained unchanged at the later checkpoint. The later snapshot contained
407 open PRs and the same one open issue. No scale/carry stream overlap was found
in their metadata or the latest BIT-thread comments; this is not a novelty proof.

Environment: Linux x86_64, CPython 3.12.14 from the existing uv runtime; standard
library only. Earlier exploratory checks used system CPython 3.14.7. No shared
interpreter or dependency was modified. Exact scientific receipts are generated
from the final Python 3.12 source, not from the preliminary fuser that also
combined standalone scales.

Completed scientific checks:

- 504 incumbent/fused raw kernel pairs, 37,044 input-column obligations.
- Six complete route pairs; native B1 calls agree, borrowed/dirty/owned state
  and numerical cleanup pass, including the zero-high case.
- Actual 1,123-chart q=3 identity-low catalogue specialization with complete
  retained occurrence weights, source digest and idempotent fusion checks.
- 16,308 independent fragment cases, 1,152 bounded-residue identities and twelve
  behavioral controls. Optimization remains enabled in the registered controls.
- Three alternating fresh-process pairs on the identical 486-bit kernel and
  complete ×4 route. Instrumented medians are 0.101733s -> 0.035850s (2.84x)
  and 0.227273s -> 0.112201s (2.03x). Whole-process medians are 0.499149s ->
  0.465754s and 0.769830s -> 0.636689s. These include instrumentation and apply
  only to these reference fixtures. Full run data is in BENCHMARK.json.

The raw kernel has 36 c=0 regressions in the completed domain: 28 standalone
A=2 cases and eight tiny A=4 cases. The adapter leaves standalone scales
unchanged, so those raw cases are not selected. No nonzero-c regression occurs
in that finite domain; no universal speed inequality follows. The six complete
route totals are respectively:

    344457 -> 174573
    341877 -> 174573
    2371617 -> 2285305
    1868442 -> 1640246
    13436164 -> 11537646
    1685 -> 1685

The complete four-command registered replay passed. All four scientific suites
then passed with -O from a read-only Git-free export of scientific freeze
`bb6afaf55a24d0841b99fcb5c938fe20dbdb2eac`; all 58 exported files remained
byte-identical. Actual optimized CLI mutants rejected a changed source and a
changed typed result. Publication byte/history checks covered all 57 package/input
files. This final validation update changes only this document; scientific code,
proof, inputs and receipts match the replayed freeze. Exact commands and logs
are retained in round77-evidence. The package command is:

    python3.12 -B scripts/research_package.py --package research/dyadic-affine-streams

The source-history/publication gates and Git-free replay are separate from the
scientific checks. Full selected cold replay, selected GL64 payload execution,
independent human review, formal-kernel verification and supplier admission are
outside this component result. Source-level cost/refinement assumptions are
listed in PROOF.md and retained predecessor proofs.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
