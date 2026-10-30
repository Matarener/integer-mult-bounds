# Sharp bank-exchange floor with one clean helper

This finite certificate was produced by Nick Petalas. Exchanging two arbitrary
two-wire binary banks needs at least **six paid ADDs**, even with one initially
zero helper restored to zero and arbitrary invertible endpoint bases within
the banks. All 36 endpoint choices are excluded at length at most five.
Two ordinary matching exchanges attain six. Exact lengths above the floor
for the other endpoint choices are unclaimed.

This extends the no-scratch model of Charan .'s
[PR #5851](https://github.com/CrocSwap/integer-mult-bounds/pull/5851).
Ali Romman's [PR #5840](https://github.com/CrocSwap/integer-mult-bounds/pull/5840)
supplies the G20 bank-boundary construction and general-basis question.
Neither predecessor's verifier is imported or replayed. The new contribution
is the added-helper exclusion, not their no-scratch census or standard swap
construction. Exact heads and roles are recorded in [SOURCES.json](SOURCES.json).

Every ADD among the five wires costs one. No reset, free basis change,
overwrite or other data operation is granted. The proof also gives the same
floor for arbitrary vector width and for a restored dirty helper by restriction
to zero initial dirt. See [PROOF.md](PROOF.md) for the exact model and reduction.

## Evidence

The forward radius-two ball has 183 injection states. Each of the 36 backward
radius-three balls has 1,485 states. All 36 intersections are empty. A generator
using coefficient rows emits [CERTIFICATE.json](CERTIFICATE.json); a separate
checker enumerates literal truth tables on all sixteen data assignments.
It checks 441 padded prefix words and 333,396 padded suffix words for the main
exclusion, both six-ADD attainments, seven rejection controls, twenty one-ADD
positive controls and a helper-touching five-ADD positive meet.

This is a complete finite exclusion with a scoped mathematical reduction.
Independent human and formal proof-kernel review are unclaimed.
The direct verifier prints a generated receipt binding every package file's
SHA256 to the actual counts and interpreter version. Receipts and replay logs
are outputs, not handwritten package evidence.

## Reproduce

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clean-helper-bank-exchange/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clean-helper-bank-exchange/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clean-helper-bank-exchange
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clean-helper-bank-exchange --check-source-history
```

Both direct commands must end with `PASS_CLEAN_HELPER_BANK_EXCHANGE`.
Use another CPython 3.12 path when reproducing on another machine. Direct
verification needs only this package and works without Git or network.
The source-history preflight needs the committed package and full Git ancestry.

To regenerate the certificate, redirect `generate.py` stdout to an external
scratch file, then compare that file byte for byte with `CERTIFICATE.json`.
The generator never writes the package. Both registered verification commands
have a 120-second timeout. Their measured local runtimes belong in the PR body.

## Scope and research record

Base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision 8. [TASK.json](TASK.json) records the changed connector card premise,
stop rule, source attribution and
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216124).
The first working example was the five-by-four identity injection with one
zero row. The original card's old connector census was read for its interface;
replaying another result was excluded by the research assignment.

This is a local obstruction to an added-workspace route. Two or more helpers,
cross-component gates, shared chain operations and the complete physical bill
remain outside its scope. No global CNOT minimum, new supplier, kappa or
complete multiplication theorem is claimed. The selected frontier is unchanged.
No full native/caller replay, Lean, Docker or historical suite was run.

## Open next questions

Can two clean helpers reduce the floor? A first step is the same length-five
meet with two zero rows, with every ADD counted. That is a new finite domain
and is not decided here. It matters only if ownership, initialization and
movement can also fit the complete caller bill.

Can cross-component synthesis or sharing with the fixed chain shorten the
whole boundary? A strictly shorter exact source-bound boundary and inverse
would be the first useful witness. Complete native and caller costs remain
the blocker to supplier use.

## Credit and license

The added-helper result, certificate and independent checker were produced by
Nick Petalas. Credit Charan . for #5851, Ali Romman for #5840, and the retained
#5834, #5807/#5828, #5708/#5671, ai-nanachi #5512, Dugongue, ToikY and native,
controller, compiler and BIT source lineage credited there. No predecessor
source is copied or modified. Breadth-first enumeration, meet in the middle,
elementary transvections and the three-ADD swap are standard techniques.
New work is Apache-2.0 under the repository license.
