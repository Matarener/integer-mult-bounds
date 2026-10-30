# Four inverse C3 targets have exact eight-call cost

Four copies of the inverse of a single order-three label cannot share a
saving in the stated binary register model. The endpoint
`diag(g^2,g^2,g^2,g^2)` in the full formal algebra `F2[C3]` needs exactly
**eight positive-g rank-one idempotent calls**, even with free interleaved
`GL_4(F2)` scalar mixing and arbitrary dirty inputs on all four roles.

Claim type: scoped algebraic proof with exact finite corroboration. This is
an original changed-alphabet side result for `bit-new-register-model`.
It supplies no new kappa or selected-frontier change.

[PROOF.md](PROOF.md) proves the lower bound without enumeration. Rank and
determinant reduce every possible saving to five calls. Remove the first
factor. The remaining four updates have independent binary image directions,
so each changes one row exactly once in their image basis. Comparing the two
F4 coefficients in that triangular factorization would force a rank-one
projector to have rank four. Eight coordinate calls attain the endpoint in
the full group ring.

## Exact evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/c3-four-inverse-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/c3-four-inverse-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/c3-four-inverse-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/c3-four-inverse-tariff --check-source-history
```

Another CPython 3.12 installation can replace the absolute interpreter path.
Expected scientific output is `PASS_C3_FOUR_INVERSE_TARIFF minimum=8
five_call_hits=0`. The runner also prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
The committed-byte check requires a publication commit and full Git history.

The read-only verifier performs two exact meet-in-the-middle exclusions.
Scalarity of the target permits simultaneous binary conjugation of the
chronological first coupling to E00. Each remaining four-factor word splits
into two products of length at most two. The F4 packed-row engine and a
separate full F2[C3] coefficient-convolution engine each enumerate 8,361
distinct such products and test all 8,361 complements. Both find zero hits.
Full-ring augmentation and F4 together are also checked to distinguish all
eight group-ring elements. Product representatives are safe because only
the complete product affects a later factor; no sampling is used.

Additional checks enumerate all 65,536 binary four-by-four matrices to confirm
the complete 120-projector inventory, construct a normalization basis for
each projector, and check all 4,096 row-once binary functional choices in
the proof's factorization identity. The eight-call witness passes every
formal coefficient and all twelve faithful regular-action dirty-input columns.
All eight single-call omissions reject. Six controls include positive identity,
one-call and five-call joins, nilpotent rejection and order-three identities.
All acceptance checks remain active with Python optimization enabled.

Every run prints a generated JSON receipt bound to all package files by
SHA256. There is no handwritten receipt and no generated checkout output.
The mathematical proof and finite checks are separate evidence.

## Sources and overlap

Canonical base is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision
8. The current selected-source baseline passed its binding checks only.
[SOURCES.json](SOURCES.json) pins the historical catalogue and selected record;
no predecessor executable or scientific receipt is imported or replayed.
The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221497)
reserved the original four-role five-call question.

The retained eumemic register model and its subsequent finite-group work
supply the context. Wentao Li's #2513 cyclic 2-power theorem concerns a
characteristic-two chain ring and unit-cost arbitrary nonidentity powers.
It does not address this odd-order semisimple algebra with only positive g
paid. Ross Richardson's #4269 cubic caller uses rational rank-one nilpotent
shears over Q[N]/(N^3-1), rather than binary rank-one idempotent label calls.
Cinna Davis's #1799 uses C3 for a three-destination complex fanout family,
which is a different object. These results are cited, not re-checked.

Entry overlap covered 341 open PRs and 5,523 Discussion records with complete
remote pagination. The sparse local search covered 243 of 8,136 tracked note
paths; distinctive main-tree searches and merged/all-state PR searches
supplemented it. Unpublished work, arbitrary diffs and absent local notes
remain outside that coverage. No search is a proof of novelty.

## Limitations and implementation constraints

The theorem fixes exactly four dirty roles and permits only the positive g
label, binary rank-one idempotent couplings and binary scalar mixing.
Extra restored roles, g^2 as an independent paid label, clean state,
nonbinary mixing and restricted finite-address realizations are outside scope.
All physical scalar, frame, access, ownership, routing, restoration, native,
compiler, precision, stock, tape and complete supplier invoices are unpriced.
No complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker, the selected cold replay and
predecessor scientific suites were not run.

The verifier has no recursion, dynamic execution, external solver, subprocess
or dependency. Its largest fixed inventories are 65,536 four-bit-row matrices
and two 8,361-entry product tables. Loop bounds are fixed in the code, and
functions stay under 60 physical lines. CPython's integer/tuple/dictionary
allocation and iterator dispatch are managed-runtime deviations from Power of
Ten rules 3 and 9. The fixed domains bound live storage; the same warning-strict
normal and optimized commands check both implementations. A larger-role replay
would require a new explicit capacity bound before expanding these domains.

## Open next questions

Can one additional restored dirty role lower the eight-call count for the
same four inverse targets? First retain the same alphabet and analyze how the
first update can meet both the target and spectator subspaces. The current
scalar-target argument no longer applies, and no five-role search was run.
A physical positive-g primitive and a complete paid caller would be required
before any formal saving could affect the BIT budget.

## Credit

This contribution was produced by Nick Petalas. Credit eumemic's register
framework, Ali Romman's retained rank-one register context, Wentao Li's
cyclic-root work, Ross Richardson's separate cubic-caller boundary and the
finite-group contributors for the surrounding questions. The new four-role
obstruction and its verifier are the contribution here. Elementary finite-field,
rank and determinant arguments are classical; global literature priority is
unclaimed. New work is Apache-2.0. Predecessor files and credit are unchanged.
