# Validation record

Canonical base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
Selected conditional kappa remains 0.001672660197076918. Checks used Python 3.12.
All changes are package-local; canonical runtime input bytes are unchanged.

Completed locally on 2026-10-19:

* Registered metadata validation succeeded.
* Registered normal verifier: PASS, 11 original/adapted serialized coefficient
  pairs and two malformed-input pairs; source/AST/false-guard controls passed.
* Registered optimized quick verifier: PASS, one original/adapted pair with
  assertions disabled and AST/source guards active.
* Git-free declared-input export: PASS optimized quick replay and four corruption
  controls (changed input, missing input, symlink input, false receipt).

The initial combined run passed its first two commands but the symlink-control
setup tried to overwrite a restored regular file. Only that export test setup
was corrected to unlink the target before creating the symlink. Its registered
export command then passed. No mathematical code or RESULT.json was changed by
this repair. Hosted CI remains a separate publication check.

At d=3 fixed-head PAIR depth, complete coefficient-call measurements are:

| Component | Original | CSE |
|---|---:|---:|
| Matrix preparations | 7 | 3 |
| Record reads/writes/moves | 2,840,912 | 2,228,010 |
| Numerical-word reads/writes/moves | 90,711,429 | 39,007,018 |
| Created record tapes | 11 | 11 |

Record saving is 21.5741%; numerical-word saving is 56.9988%. This meter omits
finite-control tariff and host allocator metadata and is not total physical
multiplication time. All borrowed bytes/public heads and numerical ownership are
checked after successful and rejected calls. Peak retained word backing does not
increase in the finite fixtures. Mathematical arbitrary-depth and high-lift
scope rests on PROOF.md, not finite tests.

A separate read-only same-session AI reviewer tested six additional pairs with
coordinate 3, GOOD/UNIT/nonfixed-PAIR ancestors, an ordinary negative UNIT, and
nontrivial mod27 high lifts. These passed their independent native matrix oracle,
bytes/heads and arena checks, including a GOOD output of 10 mod27. Those extra
in-memory variations are supplemental review evidence, not registered fixtures.
No independent human or proof-kernel acceptance is claimed.

A separately labelled local-only applicability probe used PR4008's exact actual
IDLE27776/rank26 to COPY1603/rank7 fixture. All 143 predecessor source rows matched
their hashes. Replacing only its expected duplicate preparation count by the CSE
count retained its original independent value/bytes/heads/arena checks and gave
value 1, slots [1,0], two preparations versus three. That pending predecessor
probe is outside this package's canonical-only replay dependency graph, and no
R437 frequency or completed physical payload claim follows from it.
