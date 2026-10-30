# Frozen research routing fixture

`research-routing-v7.json` retains two exact task cards from priority revision 7:
`portable-replay` and `centre-path-sharing`. They exercise the generic-baseline
and historical-ceiling routes in `choose_current_research_task.py`. The fixture
records the source commit, path and SHA256. The card objects are unchanged.

The source is commit `553d26d796fde9871ff2661a49ac7732e945410f`, file
`docs/research/agent-task-catalog.json`. The test places these cards in a small
catalogue with one track of weight 100. This carrier is test data, not a change
to research priorities. Current cards are checked separately from the live
catalogue. Every live card must preserve its other fields; each distinct direct
command also passes through both real CLIs.

The CLI fixture copies the two real scripts. It creates inert reference files
for path validation and copies the current selected record for receipt fields.
It does not execute those references or verify a mathematical claim. Missing
references, sparse omissions, deleted files and staged replacements have separate
negative tests. No Git history, network request or change to the live catalogue
is needed to run the fixture.

```sh
python3 -B -m unittest discover -s tests -p test_research_current_assignment.py -v
python3 -B -m unittest discover -s tests -p test_research_assignment.py -v
```

This fixture repairs the CI handoff in
[Discussion 5722](https://github.com/CrocSwap/integer-mult-bounds/discussions/5722).
The [investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5758)
records the failure, checks and publication status. The original scripts, task
catalogue and selected frontier are unchanged.

On base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, the old suite has eight
failures and two errors. After the repair, all 12 current-assignment tests pass
under Python 3.14.7 and Python 3.12.14, including an isolated optimized run.
All 16 related assignment tests pass under Python 3.12.14. This is test coverage,
not a mathematical replay. See the investigation for hosted-plan status.

Retain the original catalogue, routing and test authors, including Douglas
Colkitt, Ali Romman and Mihir Srivastava. New fixture and test repair: Ali Romman
with substantial OpenAI Codex assistance. No subagents. Apache-2.0.
