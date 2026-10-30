# Three G20 exchanges still need 18 ADDs under joint synthesis

**Source-bound application of a known lower bound; no new kappa.** Arbitrary
cross-component ADDs cannot lower the three PR5840 bank exchanges below
18 unit ADDs per boundary side, even after allowing independent invertible
binary bases within each two-wire bank. Exactly eight of the 46,656 allowed
endpoint maps attain 18; every other map needs at least 19. This closes the
specific direct-sum question in [the released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19230486).

The lower-bound technique is **Bu, Fan and Joo**, [Minimum Synthesis Cost of
CNOT Circuits, arXiv:2408.07898](https://arxiv.org/abs/2408.07898), Lemma 3.6
and Theorem 5.2. We claim its source-bound application, endpoint census and
sharp witnesses, not a new general CNOT bound. The proof below is self-contained;
no external paper download or executable is needed for replay.

## Exact contract and proof

The source is Ali Romman's PR5840 at
`6a043d0fc0199ee5b24c61f883f1943eaf6424be`, its controller retained unchanged
by PR5851. The three bank exchanges are `(8,14)`, `(9,13)`, `(10,12)`:
physical wires `(16,17,28,29)`, `(18,19,26,27)`, `(20,21,24,25)`.
Each bank pair has endpoint `[[0,A],[B,0]]`, with `A,B in GL(2,F2)`.
All twelve inputs are independent; every ADD costs one, including any operation
implementing a basis choice. Gates may connect any of these twelve wires.
There is no scratch, reset or free physical permutation.

For completeness, count two disjoint sorts of gates. Build the undirected
interaction graph by adding each gate's source/destination edge as the word
runs. A gate joining two previously separate components is a join. Every row
of the current linear map has support within its interaction component.
Thus a join adds a source row with zero coefficient at the destination's own
input coordinate: it cannot alter a diagonal entry. Any other gate alters at
most one diagonal entry. If the final map has `z` zero diagonal entries, it
therefore requires at least `z` non-join gates. If its undirected support graph
has `v` components, the final interaction graph has at most `v` components,
so at least `n-v` joins occurred. Consequently every word has length
`L >= n-v+z`. This is the cited link/diagonal bound, with monotone interaction
components used for the counting proof.

Every allowed endpoint here has `n=z=12`. Its support graph has no singleton:
a singleton would have an all-zero row because its diagonal is zero, contrary
to invertibility. Hence `v<=6` and `L>=18`. Cross-component gates do not evade
this argument. If `L=18`, then `v=6`, so all support components have two
vertices. Invertibility and the zero diagonal force each such component to
be an ordinary swap. Within a bank pair only the straight and crossed
matchings qualify; there are `2^3=8` global endpoints. Each is attained by six
three-ADD swaps. For every other endpoint `v<=5`, proving `L>=19`.

The exact graph-bound histogram is `{18:8, 19:408, 20:6936, 21:39304}`.
The entries above 18 are **lower bounds**, not asserted exact distances.
The source has the straight matching in each block, so both its boundary and
inverse cost exactly 18 on these twelve wires, or 36 together per port.
For 111 independent ports this subtotal is 3,996 ADDs under the source's
per-port tariff. No vectorized cross-port optimality is asserted.

## Evidence and reproduction

```sh
python3 -I -W error -B research/g20-joint-exchange-floor/verify.py
python3 -I -O -W error -B research/g20-joint-exchange-floor/verify.py
python3.12 -B scripts/research_package.py --package research/g20-joint-exchange-floor
```

Expected: `PASS_G20_JOINT_EXCHANGE_FLOOR maps=46656 floor=18 attaining=8
GL3_edges=1008 no_new_kappa`. Standard library only; no search on twelve-wire
circuits. The verifier checks source hashes, literal source words and serialized
rows, every allowed endpoint with two separate graph algorithms, all eight
18-ADD witnesses and inverse actions on every independent input column.
It also checks all 168 GL(3,2) matrices and 1,008 ADD edges against the graph
bound, plus gate-omission, identity and nonmatching-bank controls. Finite checks
corroborate the written argument; they are not its universal proof.

## Limits

The 18-wire chain/exchange component remains excluded. PR5942's component-local
20-ADD floor cannot simply be added to this 18-ADD floor when gates may mix
those two larger components. Thus no 32-wire optimum, new paid-rank saving,
native admission, changed supplier or kappa follows. All five selected
framework assumptions remain. General GL2 bases affecting the chain, scratch,
changed controllers and nonunit tariffs remain outside this task.

## Open next questions

The next useful question is whether the exact 32-wire boundary admits fewer
than 38 ADDs when gates mix the chain and these exchanges. First compute the
same endpoint graph bound and identify its shortfall from 38 before expanding
search; the missing obligation is a bound or constructive word across that cut.
Structured scope and next steps are in TASK.json.

## Sources and credit

Canonical base `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8,
selected PR6030 conditional kappa `0.003125804`, unchanged.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5804#discussioncomment-19233737).
The overlap snapshot covered 341 open PRs, 5,722 Discussion records and
8,348 local notes with complete reported coverage on 2026-10-28 at 04:55 UTC;
unpublished work and full remote closed-PR history remain limitations.

Retain Ali Romman/PR5840 and its G20/native/controller lineage; Charan . /
PR5851 `c698080add27ea02f62da393f27f05c537558ff8` for the isolated floor;
Nick Petalas/PR5942 `1f1c37ba713d027fb0c568f0dcfa41c42feaa884` and the explicit
remaining direct-sum question. Their executable replays are not re-run.
Bu, Fan and Joo own the general lower-bound method. This source application,
proof presentation and exact checks were prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0; no independent human or
proof-assistant acceptance is claimed.
