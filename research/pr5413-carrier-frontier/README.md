# Smaller PR5413 carriers at fixed saving, with certified size-saving tradeoffs

For the unchanged complete PR5413 raw caller, the sufficient height H in N=2^H
falls **3.20324× at exactly the same conditional κ=.003027288235**. Four
explicitly weaker declared savings give smaller carriers, including a
31.1-million-fold H reduction at κ=.003. These compare sufficient construction
bounds, not measured multiplication runtimes or globally minimal templates.
The selected frontier, raw profile, raw root and five framework assumptions
are unchanged. No practical-size word or full unconditional theorem is claimed.

| Declared κ | Product v | Log power p | Sufficient H | PR5413 H / H |
| --- | ---: | ---: | ---: | ---: |
| Published .003027288235 | 1024 | 1000 | 38569300000000000 | 1 |
| Same .003027288235 | 1024 | 322 | 12040700000000000 | 3.20324 |
| .003 | 512 | 120 | 1239850102 | 31108034.7 |
| .00275 | 256 | 59 | 50859231 | 758353975 |
| .0025 | 256 | 58 | 25258797 | 1526965041 |
| .002 | 256 | 55 | 11738348 | 3285751964 |

The κ=.003 point retains about 99.1% of the PR5413 exponent saving. The large
height factors at lower κ explicitly spend exponent headroom; they do not
preserve the original exponent. Even the smallest carrier remains astronomical.

## What changes and what is reused

The fixed-κ tuple uses cutoff18/floor21, higher-moment offset1/10,
theta61/64 and logarithm power322. The lower-saving tuples use cutoff17/floor21,
offset1/10 and theta15/16, with the exact tested exponents in [RESULT.json](RESULT.json).
All 64,260 paid jobs and 10,928 productive fields of the raw caller are retained.

The existing higher-moment theorem pays the complete normalized sum
`alpha^v+2*gamma^v+2*delta^v`. Evaluating that sum directly replaces the old
sufficient `.97`/Bernoulli tail envelope and permits the changed tuple. Both
partial-block remainders and all target completions stay charged. It is not
enough to substitute a smaller logarithmic power in the old pinned checker.

The existing logarithmic compiler and positive slack family then fund the new
carrier. [PROOF.md](PROOF.md) gives the complete charge, rational-gap ceiling
grid, fresh finite-template application and remaining assumptions. [application.py](application.py)
makes the exact source substitutions in scratch. It generalizes three precision
sites, checks conservativity on the original payload, and changes six named
conjunction applications. The other **19 of 25 source conditions are unchanged
in the AST**, including all owner/phase/route/field-ID checks and false component
flags. All 25 adapted conditions pass for each new point. The one old minimum
reserve-envelope gate is explicitly replaced by a full paid-sum condition.

Every replay first runs the **unmodified complete eight-engine PR5413 master**.
Its source-identical native/local/wholecaller/binding/invoice evidence is reused
across the five tuples; funding, outer inequalities, precision and conjunction
are fresh for each tuple. Frozen source files are never edited. The original
arithmetic helpers and outer ledger are authenticated and reused with credit;
this package does not claim an independent implementation of those helpers.

Meaningful controls reject the unsubstituted coarse application, a preceding
height grid, product outside the declared safe domain, a missing paid job,
free completion and an invalid higher-moment offset. All 54 strict and four
functional outer predicates remain funded. Component flags retain their narrow
scope; a successful adapted conjunction is not upstream scientific approval.

## Relation to previous work

zxv's higher-moment/logarithmic compiler already reduced earlier sufficient
carriers substantially. PR5468 supplies gap-parametric precision on the same
caller with the original tuple fixed. This contribution applies a changed
fully charged tuple at fixed κ and records a size-saving frontier, rather
than more digits of the raw root. It is neither a new strictification theorem
nor the first parametric precision application. The raw native/provider/
controller and complete conditional-framework lineage keep full credit.

This was an explicitly assigned finite-size investigation. Its changed scope
from the historical `independent-moment` card is in [TASK.json](TASK.json).
Exact base/source blobs and hashes are in [SOURCES.json](SOURCES.json); the
current selection and catalogue are historical provenance. A bounded public
PR-title/body search included PR5413/5462/5468 and the exact new H value; it
is not an exhaustive novelty proof. No selected-record update is requested.

## Reproduce and inspect

Python standard library only; generic environment Python 3.12. From repo root:

```sh
python3 -B scripts/research_package.py --package research/pr5413-carrier-frontier --check-only
python3 -B scripts/research_package.py --package research/pr5413-carrier-frontier
```

To retain each generated full written application and exact precision/conjunction
review diff, with no frozen-source edits:

```sh
python3 -I -B research/pr5413-carrier-frontier/verify.py \
  --proof-output /tmp/carrier-frontier-review
```

`--write` rebuilds the committed scientific RESULT for authoring; the normal
command compares the complete deterministic payload. Both wrapper modes compile
scientific source with optimize=0. Local checkout modes must match the frozen
capsule manifest; a group-writable local umask may require restoring its declared
0644/0755 modes before the unchanged master can run. Hosted CI is separate from
local Linux replay. No Lean or actual Turing-tape execution is supplied.

Local validation passed on Linux with CPython 3.12.13: the upstream metadata/pin
check and both registered ordinary/optimized replays, each including the complete
eight-engine baseline, all five changed applications and the rejection controls.
Ruff also passed for the three new Python files. The package preserves exact
source bytes across checkout filters; publication and Git-free export checks
are recorded separately in the PR handoff.

## Open next questions

1. Independently review the source-sensitive tuple application. Start with the
   six changed conditions, complete paid-tail proof and generated proof diffs.
   This matters because numerical success is not human or proof-kernel review;
   none is claimed here.
2. Apply a different compiler geometry to this exact raw caller with a full
   ordinary/precision bill. Smaller sufficient carriers still do not give a
   practical runtime. A favorable raw moment alone does not supply that caller
   or its convergence/implementation gates.

## Credit

Richard Hoekstra prepared this package with substantial OpenAI Codex assistance.
Chris R/Clear1nsight supplied the PR5413 caller audit, exact arithmetic and
precision/conjunction checks; Dillon Amburgey the provider; Ali Romman the direct
controller; Cao Yifan the native word; Cinna Davis the helper/product lineage;
zxv the compiler/precision/higher-moment machinery; Jacob Alan Sussman the mixed
flow. Retain the full cumulative source attribution and notices. New material
is Apache-2.0. No independent human or formal-kernel approval is claimed.
