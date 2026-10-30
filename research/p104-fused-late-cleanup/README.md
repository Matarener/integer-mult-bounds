# P104 fused late delivery and compressed query cleanup

Combine the actual PR3981 copy-free late FULL delivery with PR3943's early
correction and compressed Q cleanup. The source-bound composed word preserves
all 280 input columns, every endpoint row/frame, and all 72 arbitrary dirty
helper returns. **Unit ADDs fall from5472 to4704; native mass stays2520**, with
2616 halves and2616 doubles unchanged. No private storage is introduced.

The point is an executable fusion of already credited ingredients. The
correction now creates residual `q=x_J+B x_N` while Q still equals `h-Dx`;
the actual extracted factorization `D=T[I B]` permits64 unit ADDs to restore Q
instead of the old832. The ordering and donor restoration are checked explicitly.
An actual source-preserving variant inserts the cleanup inside PR3940's fused
tail while q still exists:5856→5088 ADDs,2712 halves/doubles and native2520.
This preserves all X=x FULL and Y=x+y in their hyperplanes. The inherited
post-encoding return adapter also composes, costing5664 ADDs,2720 halves/doubles
and native2712; this is contextual integration, not a new optimality claim.

See [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [VERIFY.json](VERIFY.json).
Run `python3.12 -B research/p104-fused-late-cleanup/verify.py` or the registered
package launcher. Native transport events are literally unchanged; prior phase
checks are inherited, not freshly replayed here. The old conditional two-axis
gate still fails32448. No supplier, all-size result or selected-frontier claim.

## Provenance and overlap

Canonical main20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority6, fetched and
read at entry. The explicitly assigned task is this bounded composition; no
new dependent native/kappa search follows the failed global gate. The overlap
helper used702 open PR bodies including drafts, complete at08:30:14UTC on
2026-10-19, with49 possible matches. It had no Discussion cache; the root
coordinator separately checked live boards and posted the canonical scoped
claim at https://github.com/CrocSwap/integer-mult-bounds/pull/3954#issuecomment-6263112891 .
This is bounded overlap coverage, not a novelty certificate. The optional
selected-frontier orientation command could not run in this sparse checkout
because its unrelated selected ASSEMBLY archive is omitted; no full selected
replay or successful baseline command is claimed.

Credit Chris R / Clear1nsight's PR3981 late delivery, PR3943 residual cleanup
and return adapter, PR3882 encoded correction, and PR3940's actual fused source-preserving tail. Unchanged builder exports record
original heads, Git blobs and hashes; they require no unavailable unmerged
commit in a main-only source export. Credit Rohan Arun's PR1972 witness,
Chafik Boukhalfa's PR1991 native realization, Adam Gall's PR1940 delivery,
icekylinx PR531 compiler and PR1862 interpreter lineage, and Josie Elliston,
Sagar Thakrar, Douglas Colkitt and Dominik Scholz's E8/P104 work. PR3954's gate,
PR3965's fixed-consumer audit, and PR3961/3962/3966's distinct boundary/coverage/
gauge constraints remain credited. PR3956's adapter comparison is not repeated
as a new result. Prepared with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

An independently proposed changed global caller needs its own physical,
entrance, ownership, coverage, precision and all-size invoice. First test that
caller's full gate with the exact native profile before optimizing scalar
cleanup further. The present result changes no native cost, so another local
scalar tweak cannot resolve the retained two-axis obstruction by itself.
