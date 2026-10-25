# Share one encoded radix traversal in directory setup

The retained `directory.produce` computes its returned count by reconstructing
the same modulus radix once per matrix coordinate. This package supplies one
local replacement, `high_power_shared`, that traverses the encoded radix once
and repeats the identical count multiplication at each yield. The unchanged
producer is executed with either binding; frozen/shared runtime bytes are not
edited or installed.

Let d be dimension, M=d², modulus=q^w, c=q^(w−1), H=c^M, and B>0 the physical
old-prefix count. Both versions perform exactly M(w−1) ordered multiplications
by q on the returned Count and produce B H. The candidate removes exactly
M−1 complete radix traversals. For a one-traversal source Word invoice
rho=(reads,writes,unit moves), its exact saving is `(M−1)rho`.
Record/Count/Counter Tape actions, old-field index Word actions, output bytes,
lexicographic order and multiplicity are unchanged.

The actual dimension64/cap1 fixture uses the retained Q=6507 code width and
executes the complete producer. Source residue Word actions fall from
`(2793472,483328,2916352)` to `(651787,94303,639532)`:
exact saving `(2141685,389025,2276820) = 4095*(523,95,556)`.
Record Tape actions remain `(310027,91612,274870)` and index Word actions
remain `(15,0,12)`. This is an action count, not a wall-clock speed claim.
The fixture uses a projected valid finite vocabulary; it does not reconstruct
the full selected source catalogue or admit its low-code/GL specifications.

## Contract and prior work

The interval starts with an already-live valid Context and canonical valid
input tapes/Words, positive B, enough arena capacity and no concurrent mutation.
Context preparation/teardown, input/vocabulary compilation and disposal of the
returned directory/Count remain explicit caller charges outside the interval.
No numerical decoding of runtime Words is used. The independent integer model
is external mathematical verification, not runtime control.

`source/CALLER.py:207` retains the actual `Machine.residual_begin` call to this
producer. The candidate is opt-in research code; the shared caller remains
unchanged. Python controller/object/allocation costs, literal physical tape
lowering, backing/slot metadata, source admission and full caller composition
remain separate. Successful valid-input restoration is the contract; inherited
malformed-input paths do not provide general exception rollback.

[PR2590](https://github.com/CrocSwap/integer-mult-bounds/pull/2590), by ywz65,
already proves repeated radix reconstruction is cubic in w and the complete
producer is Theta_q(D), including counters and physical duplicate prefixes.
Its explicit shared-traversal question motivates this replacement. Its output
formula `D=B H(h+1)[Q+2+M(L+1)]`, the separate directory-storage allowance,
and Ross Richardson's exact successful numerical peak `max(M,6)` are credited
prior results. The peak remains unchanged here; at d=64 it is 4096 above
all entry residents. This is not a new asymptotic theorem or peak discovery.

The source Word radix term falls from M traversals to one. With fixed dimension
it retains the cubic width order; no claim removes that order. All M(w−1)
Count multiplications remain charged. `PROOF.md` and `independent.py` give the
complete exact invoice and phase boundaries, rather than treating output size
or a numerical peak as a whole physical caller bill.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/directory-producer-invoice
python3.12 -I -B research/directory-producer-invoice/verify.py
python3.12 -I -B research/directory-producer-invoice/independent.py
python3.12 -I -B research/directory-producer-invoice/test_verify.py
```

Six runtime modules and the caller/notice exports are authenticated by exact
SHA256 and Git blobs before execution. The primary meters every created and
borrowed Tape plus residue/index arena traffic, compares actual original and
candidate runs, and checks output/order, count, heads, protected state and
successful cleanup. The separate formula checker imports neither primary nor
retained executable modules. Controls target wrong yield/multiplication,
undercounted radix work, multiplicity, source authentication and typed receipts.
Normal and optimized replay must pass; default replay is read-only.

Bounded complete high cubes use small dimensions/caps. The dimension64 fixture
has cap1; no multi-lift dimension64 directory, huge-prime payload, complete GL64
source, full selected cold replay, human review or formal-kernel acceptance is
claimed. The written source argument covers valid arbitrary parameters under
its contract; finite tests corroborate it.

## Scope and coordination

Canonical base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority6. The changed
`selected-stock-envelope` card is retained exactly in `TASK.json`. The named
baseline was attempted but a sparse omitted selected-package ASSEMBLY blocks
its inventory check; this package supplies its own complete local runtime slice.
It does not derive the selected complex m73 reserve coefficient.

The canonical investigation is the claim/update on
[PR4011](https://github.com/CrocSwap/integer-mult-bounds/pull/4011#issuecomment-6264214824).
`TASK.json` records the full724-open-PR-body entry scan, latest100-body delta,
retained predecessor reassessment, live handoff checks and coverage limits.
No novelty guarantee follows from the bounded text search.

## Open next questions

See structured questions in `TASK.json`. First review this exact success
contract and bind the candidate to the complete caller with a physical control
and allocator tariff. Context, child_extents/read_prefix, geometry, coefficients,
dispatch and the other Pi phases remain charged obligations. Then join all
simultaneously live parent/child, dirty, Count, template and backing categories
at original widths before claiming reserve or recursive supplier admission.
There is no selected-frontier or kappa change.

## Credit

Jose Manuel/jmbarrancoml supplies the physical caller, encoded runtime and
canonical directory lineage; David Arias/PR2753 and Nick Petalas supply retained
caller/controller/record components. Their complete original notice is retained
unchanged in `source/NOTICE.md`. ywz65/PR2566 and PR2590 supply primitive/setup
analysis, the cubic correction and explicit optimization question; ywz65's
directory-storage package and Ross Richardson's numerical-phase audit supply
the credited storage/peak facts. Chris R/Clear1nsight PR3983/4011 supplies the
adjacent preparation/admission bill and named directory/context obligations.
New adapter, exact invoice, proof and packaging by ToikY with substantial
OpenAI Codex assistance and separate AI math/test contexts. Apache-2.0.
