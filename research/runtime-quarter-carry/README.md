# Complete runtime carry rotation with a tight physical bill

For every positive P,Q,S and supplied0<=C<Q, two fixed literal tape programs
rotate the complete[P] x [Q] x [S] payload by x -> x±C mod Q in its original
owner. Their exact ledger gives tight uniform bounds393V transitions and43V
visited cells, V=PQS. All eight private tapes return blank at their origins;
the extent and offset descriptors, other tapes and all other heads return.
There is no dummy Q coordinate or separate clean output owner.

Two linked fixed programs physically read a supplied five-bit quarter-code
packet k+16, prepare C=k*4^-1 mod Q for odd Q, execute the full rotation, erase
the owned C+1 descriptor and preserve the packet. They cover every integer
-16<=k<=12, both directions and Q=1. Their tight uniform bill is468V transitions
and49V visited cells, including dispatch, preparation, cleanup and all markers.
All four uniform bounds are attained in the one-bit case. These are bounds for
the retained tables; they are not lower bounds on other algorithms.

The exact two released PR5820 bases,111 ports and both directions have3552
columns. A column inequality proves that every fused carry of all444 routes
has code k in this packet domain, for every odd q and width. The checker also
tests42,624 full-width modular identities. An actual port9 inverse fixture has
k=-3 and Q=125, so C=93; it runs through the complete physical consumer. This
connects the all-route algebra of[PR5841](https://github.com/CrocSwap/integer-mult-bounds/pull/5841)
to a paid carry leaf with volume linear in the declared stream. See[PROOF.md](PROOF.md).

Both independent literal interpreters agree on all cells, heads, transitions
and visited intervals for804 generic cases and523 linked quarter cases over
66,675 payload bits. Tests include all payloads through Q=4, all runtime offsets
through Q=9, nontrivial prefix/record lengths, all29 packets and complete Q125
streams. There are273 whole-bank inverse pairs and12 semantic rejection
controls. Every generic run checks the exact ledger, and all four serialized
tables are compared by canonical content. Exact receipts are in RESULT.json.

Run from the repository root:

```sh
python3 -B scripts/research_package.py --package research/runtime-quarter-carry
```

The direct command is `python3 -B research/runtime-quarter-carry/verify.py`.
Python3.12 and the standard library suffice. `--write` explicitly regenerates
TABLE.json.gz and RESULT.json; ordinary replay writes no package files. The
input copies are byte-pinned and authenticated before import. SOURCE pins give
exact pending-head attribution; they do not establish scientific acceptance.

The claim is limited to the supplied complete stream, extent descriptors and
quarter-code packet. Actual low-cache code formation and selection, whole-T
staging, low-type commit, physical G20 ROW heads, ancestor stock/P3 and the full
caller invoice remain open. This does not close the entire released R17 carry
layer. All five framework assumptions retain their status; no new kappa or
selected-frontier change follows. See[TASK.json](TASK.json) for the scoped card.

## Open next questions

Bind a real PR5820 low-cache row to the five-bit packet, then join its formation,
the complete homogeneous route, this carry leaf and low-type commit. Start with
the retained port9 witness and materialize the entire low-type domain with
arbitrary payloads and spectators. Charge code selection and cache erasure as
well as the high stream. Then install the completed route in the actual ROW
layout. The blockers are the missing whole-T consumer and physical caller map,
not the width of this descriptor or a bounded-translation restriction.

Credit JoyboyBrian PR5332/5019/5052 for quarter arithmetic, runtime affine work
and owner reuse; David Arias PR2776 for the literal machine and counter/stream
macros; Charles Bethin, Jose Manuel and the retained tape/ROW authors; Nick
Petalas for the selected q-adic carry identity; Tekalign PR3343/4000 for carry
and dyadic streams; ToikY PR5801/5805 and PR5820 for released G20 words; and
PR5841/5842/5846 for the retained algebra and interfaces. Input source comments
and the prior README retain the full contributor lineage. The new work is the
one-coordinate consumer, exact physical ledger, linked runtime packet interface
and complete source envelope. Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. Independent scientific review is pending.

The source manifest pins replay inputs to copies in this publication history.
Its `retained_predecessors` records keep each original head, path, blob and
SHA256, plus its exact retained file or archive member. Each source was checked
byte-for-byte before this rebind. This removes an unavailable side-commit
dependency from clean CI; no source bytes or scientific checks are changed.
