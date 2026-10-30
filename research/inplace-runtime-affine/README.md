# Original-owner runtime affine shear

The complete runtime affine shear now writes its result into the original
physical owner. It needs no separate clean output bank or source-retirement
oracle. The construction covers every positive P,Q,G,S, all0<=c,C<Q, both
orientations, and the linked half-coefficient programs with paid descriptor
preparation and erasure. The old separate-output tables stay byte-for-byte
unchanged when the new keyword `inplace` is false.

The four new fixed tables have874 generic or931 linked-half instructions.
They use the retained19-tape/seven-symbol layout; tape1 is never accessed and
can hold arbitrary spectator data. The all-size bounds remain1024V transitions
and64V visited cells, where V=P Q^2 G S. Relative to the matching source program,
every valid execution uses exactly three fewer transitions and V+1 fewer visited
cells. The main gain is the complete same-owner interface and removal of a
full output bank, not a claimed multiplier runtime improvement.

The source gather already retains every payload bit in two owned buckets before
emission. The new program rewinds the original owner at that boundary, writes
the complete result there, consumes both buckets and restores all private heads.
[PROOF.md](PROOF.md) proves endpoint, termination, costs and the exact source
delta. DELTA.json binds every adapted source edit; all frozen sources stay intact.

Run `python3 -B scripts/research_package.py --package research/inplace-runtime-affine`.
Python3.12 and the standard library suffice. The standalone command is
`python3 -B research/inplace-runtime-affine/verify.py`.

Both retained disjoint sparse/dense interpreters execute all496 generic and10
linked-half cases, covering26,920 payload bits. Checks include complete small
coefficient families, all Q3 basis columns, all Q2 payloads, nonunit/zero
coefficients, composite moduli, translated origins,50 whole-bank inverse round
trips and10 rejection controls. A regenerated missing-rewind program fails;
an endpoint-preserving extra-work program changes the exact physical bill.
Source tables, final cells/heads, steps and visited spans are compared exactly.
These finite executions support the written all-size proof; they do not replace it.

General coefficient descriptors remain supplied inputs. Earlier-target routing,
complete low/high ROW layout, caller cache/stock/padding, native and rounded
children, final compiler and supplier admission remain open. All five framework
assumptions and the selected frontier retain their status. No new kappa follows.

## Open next questions

Connect one actual G20 later-target marker to this complete-stream interface,
including all extent and rational coefficient producers. Retain the full cost
of low-type commit, high carry, ROW padding and borrowed return. The separate
earlier-target route needs its own physical implementation and allowance.

Credit JoyboyBrian PR5019/5052 for the runtime-affine kernel and direct original-
owner scaling pattern; David Arias PR2776 for macros and both machine engines;
Charles Bethin, Jose Manuel and the retained native/ROW/tape lineage. Sagar
Thakrar's expired ownership proposal is prior context; its XOR construction is
not used. New source adaptation, proof and checks by Ali Romman with substantial
OpenAI Codex assistance; no subagents. Apache-2.0. Independent acceptance remains open.
