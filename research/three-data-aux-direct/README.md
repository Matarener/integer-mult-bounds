# Nine coordinate calls still meet three identity targets beside one idle auxiliary

**Partial. No new exponent.**

The three-register theorem prices three invertible targets at nine rank-one
calls, and it leaves extra registers outside that claim. Adding one dirty
auxiliary does not change the direct schedule. On four roles, the nine factors

```text
D_{E_ww}([E_ii]),  w = 0,1,2,  i = 0,1,2
```

multiply to `diag([I],[I],[I],[0])`. The auxiliary is restored because no
factor writes it. Each frame `E_ii` has rank one, and each target `I` has
rank three.

Every way of assigning eight coordinate-projector calls to the four roles
leaves some data register with at most two calls. A sum of two rank-one
frames has rank at most two, so that register cannot hold `I`.

The same span arithmetic that excludes five calls for two data registers
leaves spans 4, 5 and 6 open for eight calls and three data registers. This
package does not classify the 120 four-register projectors.

The compared alphabets are different. The reviewed GL3 census uses two
registers and coordinate-CNOT words through length eleven. The reviewed
mixed-root tariff is a UT4(F2) quotient and does not convert rational frames.
Free address maps between calls stay outside the model, as in the
three-register note.

## What was executed

The checker multiplies the nine factors in the group algebra of `3×3`
integer matrices and enumerates the eight-call coordinate distributions.
It also recomputes the two published span windows.

## Scope and evidence

Original card: `bit-new-register-model`, priority revision 6, refined to this
nine-call word with one idle dirty auxiliary. [TASK.json](TASK.json) records
the scope change. [RESULT.json](RESULT.json) is the executed receipt and is
not rewritten. [SOURCES.json](SOURCES.json) pins the two register notes and
the review through #2027. No selected frontier file changes. The word is a
formal product, not a bit-circuit supplier.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:05 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3527 note at 2026-10-18
04:49 UTC, was released work. Draw seed `8dcfcac65abe8406658ec91a7fe397f4`,
track `bit-mechanisms`, second card `bit-new-register-model`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/three-data-aux-direct/verify.py
python3.12 -B research/three-data-aux-direct/test_verify.py
python3.12 -B scripts/research_package.py --package research/three-data-aux-direct
```

The replay finishes in under a second.

## Open next questions

Coordinate projectors cannot make this auxiliary save a call, and the
remaining spans are the 120-projector classification already marked infeasible
without a new reduction. This package does not open that classification.

## Credit

The three-register note states the nine-call model and the operations it
excludes. The dirty-auxiliary note states the span test and the open
eight-call case. The review through #2027 states the GL3 census and the
mixed-root tariff.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
