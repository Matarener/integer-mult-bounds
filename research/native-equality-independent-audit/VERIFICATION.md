# Verification record

Environment: Linux x86_64, Python 3.12.13, standard library only.
Base: canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`.
Reviewed PR5588 head: `97db3fb45cd93a350e300781d75440d14e6a1f73`.
Its proof and README are byte-identical at the base; `SOURCES.json`
authenticates their exact Git blobs and SHA256 hashes.

The following completed successfully on 2026-10-26:

```sh
python3.12 -B scripts/research_selected_baseline.py
python3.12 -B scripts/research_package.py --package research/native-equality-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/native-equality-independent-audit
python3.12 -I -O -B research/native-equality-independent-audit/verify.py
```

The selected-baseline command checks source bindings and metadata only.
No selected native replay or supplier admission was run. The registered
normal replay and direct isolated optimized replay produce the same
scientific receipt, `RESULT.json`. Every check uses explicit exceptions
and remains active with assertions disabled.

The arithmetic modules are independent implementations. No source verifier
is imported. `stabilizers.py` uses Pauli labels with explicit phases modulo4,
integer projector numerators, rational elimination and Gaussian-integer
complex controls. `contracts.py` uses literal rational matrices throughout.
The written proof, not the finite enumerations, establishes all-size claims.

Committed-byte/source-history and deterministic export checks also passed:

```sh
python3.12 -B scripts/check_research_commit.py --package research/native-equality-independent-audit --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/native-equality-independent-audit --output /tmp/imb-20261026-equality.tar
python3.12 -B scripts/export_research_package.py check /tmp/imb-20261026-equality.tar
```

The export contains 13 scientific/package/input files, including the three
declared inputs. It was extracted with Python's tar data filter into a fresh
`/tmp` directory outside the checkout. Direct `-I -O -B` replay from `/tmp`,
using an absolute Python executable with `PATH=/nonexistent` and empty
`PYTHONPATH`, reproduced the complete receipt without Git. In that disposable
copy, changing the receipt and changing the pinned proof input independently
caused the expected explicit failures. The source checkout stayed unchanged.
After recording these results, the final committed bytes were exported and
checked again, with a second fresh Git-free optimized replay.

Pre-submission canonical-main refresh retained the same base. The fresh overlap
snapshot at 05:37:18 UTC covered 7,676 HEAD notes plus the two new package notes,
374 open PRs and 5,002 Discussion records, with complete reported pagination
and no warnings. No new overlapping audit appeared. The reviewed source head
and its proof/README bytes were rechecked separately. These checks establish
transport, source bindings and reported search coverage; they are not
mathematical acceptance or a guarantee about unpublished work.

Hosted CI status is reported in the PR, not frozen into this note.
