# Two fewer P104 events by sharing through a dirty output

This contribution was produced by Nick Petalas.

An exact local replacement on DreamingOfClouds's
[PR5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907) word removes
two ordinary events and twenty real scalar allowance units. Events fall from
25,998 to 25,996; the complete local scalar allowance falls from 228,664 to
228,644 under the retained PR5827 tariff. This is a scoped exact circuit
construction, with a finite certificate for the complete modified word.
It supplies no new kappa.

The original question is Matarener's global ordinary-resynthesis next question
in [PR5975](https://github.com/CrocSwap/integer-mult-bounds/pull/5975).
That package's compression and results are cited, not independently checked.
This replacement introduces a dependency between two destinations. It does
not merge repeated ordered ADD pairs, normalize signs or apply a three-gate
triangle identity. The first positive candidate ended the search.

## Exact replacement

Indices are zero-based in the pinned PR5907 program. All contacts below use
frame 3, the empty binary basis. Let a be field 159, b field 158, and

```text
f = field133 + 2 field721 + field21 - 2 field711.
```

Remove these four events:

```text
509: b += -2 field711
660: b +=    field133
663: b +=  2 field721
664: b +=    field21
```

Keep the four updates accumulating f into a at indices 667, 669, 670 and
671. Immediately before 667 insert `b -= a`; immediately after 671 insert
`b += a`. Every other event is kept in its original order. [patch.py](patch.py)
constructs this exact candidate and checks its window premises.

Fields a and b both have arbitrary initial values. Neither is read anywhere
in the old window [509,672), and the four sources of f are constant throughout
that window. The only updates to a in the window are its four shared-form
updates. Other updates to b contribute a form h. Thus both circuits have

```text
a_out = a_in + f
b_out = b_in + h + f.
```

In the replacement, the b value just before the final insertion is
`b_in + h - a_in`. Adding `a_in + f` gives the required result. This proves
the identity for every input over the rationals or complexes, including
every dirty a and b. All other rows coincide because the window contains
no observation of either output. No zero temporary or borrowed-state
assumption is used. Equality at this cut composes with the identical prefix
and suffix, so the complete exact linear operator is unchanged.

The removed coefficients are -2, 1, 2, 1. Under PR5827's ADD allowance

```text
cost(q) = 2 (3 + bit_length(abs(num(q))) - 1
              + popcount(abs(num(q))) + bit_length(den(q)) - 1),
```

they cost 10+8+10+8=36. The two inserted unit ADDs cost 8+8=16. Hence the
saving is exactly twenty units and two events. This is an instruction
allowance comparison, not a timing measurement or an optimality claim.

## Evidence and reproduction

Python 3.12 and the standard library suffice. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-dirty-anchor-window/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B -O research/p104-dirty-anchor-window/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-dirty-anchor-window
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-dirty-anchor-window --check-source-history
```

Any CPython 3.12 installation may replace that path. The expected markers are
`PASS_P104_DIRTY_ANCHOR_WINDOW`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Normal verification writes no files. The verifier
prints a generated JSON receipt containing package SHA256 hashes and the
canonical candidate payload hash. To materialize the candidate, add
`--emit-word /absolute/external/path/WORD.json`. The path must be outside the
checkout and must not exist.

The verifier authenticates the source before using it, checks exact matrix
equality on all 100 fields touched in the 163-event window, and replays only
the complete modified word on all 799 independent input columns. Its sparse
rational endpoint rows specify all 638,401 matrix entries, including zeros.
Every new ADD has physically available equal frames. All 31 owned lifetimes
return, with peak occupancy 13. Every non-ADD event and every boundary,
frame, port and helper inventory field is byte-for-byte equal as parsed data.
The canonical uncompressed candidate SHA256 is
`5c2ed3597871bcbfa5a00194671e75aab95345ba6a91b1c7c7bd1c78eb1ef495`.

Four matrix controls reject a wrong cancellation sign, wrong source, omitted
subtraction and omitted addition. Five premise controls reject an intermediate
observation of either output, a shared-source write, a wrong frame and a
changed removed coefficient. The local prefix maximum row l1 norm is 17 in
both versions, relative to independent values at this cut. This is not an
actual-input rounded-error or whole-word precision certificate.

## Scope and credit

Base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. [TASK.json](TASK.json) records the changed scope from helper splits
to a scalar side result. The selected-source baseline was used as orientation,
not a scientific replay. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19227524)
records the question before the search. Live open PRs, recent account PRs,
Discussion claims, local reservations, merged searches and main-tree searches
were inspected. The overlap tool's sparse local coverage is incomplete;
these checks are not a proof of novelty.

Credit DreamingOfClouds for the PR5907 word; Ali Romman for PR5827's source
word, tariff, exact endpoint convention and retained construction; Mason Hale
for PR5811; Matarener for PR5975's resynthesis question; Cinna Davis for
PR4692's commuting and triangle rewrites; and the retained P104, geometry,
native, caller and compiler contributors credited by those packages.
Dirty-output sharing and elementary row algebra are standard predecessor
techniques. The new contribution is this literal changed dependency window,
its twenty-unit bill and its verifier. Predecessor files and credits are unchanged.
New material is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.

The complete paid MOVE sequence and productive boundary are identical, so
the signed recursive moment receives no change from this rewrite. No native
map, physical caller, compiler, outer inequality, rounded precision/tape
contract or complete multiplication theorem is newly certified. In particular,
exact endpoint equality does not certify rounded equivalence of changed
intermediate states. The five framework assumptions remain. No selected
frontier file changes, Lean, Docker or predecessor scientific replay are used.

## Code constraints

The two Python files use no recursion, external dependencies, generated code,
background jobs or unbounded search. The replay domain is fixed at 799 fields,
fewer than 26,000 events, and at most 2,048 frame descriptions. Local symbolic
rows have at most 799 coefficients; each function is below sixty lines.

Power-of-Ten rule 3 has a managed-runtime deviation in the sparse rational
replay and JSON parsing. CPython and Fraction allocate during arithmetic.
The pinned source, fixed event and field counts bound live row storage by
799 squared rational entries. Registered commands have 120-second timeouts;
no retained runtime configuration is changed. Verification exercises the
complete fixed domain. A fixed-allocation native implementation would be a
separate backend if memory limits become a binding requirement. Rule 10 uses
warning-strict normal and optimized execution and the repository package
checks; no project-wide diagnostic configuration is changed.

## Open next questions

Does this literal rewrite compose with PR5975 compression to provide useful
headroom for a paid-profile improvement? Start at these four shared-form
contacts in the compressed word, preserve every observer, then price one new
productive or paid change. Neither the composition nor a newly funded change
is supplied here. The structured question and blockers are in TASK.json.
