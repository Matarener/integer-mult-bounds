# Wire routing obstructions for the P104 residual

**This is a scoped negative result. No new κ is claimed.**

Most of the P104 local word's cost is the delivery of the residual `E = M - I` to the partners. Swarm words use about two
dedicated helpers per partner for the last mile into `Q_j`. Every helper carries its own unit row, so it must also be cancelled
("pollution"). A natural alternative is to let **lives themselves act as wires**: a live carries other lives' content into a
partner's final frame. Its own row is wanted there, because `|E| = 1/2` on every non-conflicting pair.

This package records exact structural facts about that idea and closes its minimal form:

1. **Sign lemma** (hand proof + Lean). All common readers of a non-conflicting pair `k, i` want the same ratio sign, except
   the reader whose root is the third root of the A2 through `r_k, r_i`. Universal wire contents therefore exist.
2. **Triangle lemma** (hand proof + Lean). `G_km G_mi G_ik = -1` iff the three roots form an A2. There are 704 port triangles.
3. **Cover lemma** (computer-checked). Two 7-frames `Q_j ∩ Q_a` and `Q_j ∩ Q_b` cover the 48 ports of `Q_j` iff `{j, a, b}` is an
   A2 triangle, and then they split them 24 + 24.
4. **Capacity** (computer-checked). Such a 24-port frame has at most 16 ports in any 6-dimensional subframe.
5. **Two-source lemma** (hand proof). Assume a partner chain `{0} → G → Q`, every live a wire with one wire per `Q`, and no helpers.
   Then no legal word exists: the two registers that meet in `G` cannot span both partners' rows.

So a pollution-free "wire" architecture is impossible in its minimal form. Each partner needs a third source in its 7-frame,
and with all lives used as wires that source is a helper. The variant "wires plus one helper per partner" is left open.

Proofs: [PROOF.md](PROOF.md). Lean: [lean/WireSigns.lean](lean/WireSigns.lean).

**Card:** `p104-side-correction`. See [TASK.json](TASK.json). Inputs are pinned in [SOURCES.json](SOURCES.json).

## Reproduce

```sh
python3 scripts/research_package.py --package research/p104-wire-routing-obstructions --check-only
python3.12 scripts/research_package.py --package research/p104-wire-routing-obstructions
```

`verify.py` uses only the standard library. It takes about 10 s and checks V1–V6, two failure controls and `RESULT.json`.
The Lean file needs Mathlib (same revision as `research/p104-carrier-code-uniqueness/lean`). Build it with `lake build`
inside `lean/`. Checked build (Lean v4.33.0-rc1, Mathlib `55b7917b`): `lake build` OK, and
`lean/Axioms.lean` prints only `propext`, `Classical.choice`, `Quot.sound` for both theorems.

## Open next questions

- Is "lives as wires plus one helper per partner `G`-frame" cheaper than the swarm's two polluted helpers per partner?
  The lower bounds here leave plenty of room. A first step is a constructive test on one triangle with an exact replay.
- 104 is not divisible by 3, so at least 2 partners need another scheme; the best packing we found has 33 triangles (not proved maximal).

## Credit

Prepared by Matarener with Claude (Anthropic), via Claude Code. It builds on the E8 description of the ports and the
content-in-frame lemma in `research/p104-carrier-code-uniqueness`, and on the frame-rank law (Theorem JR) of the P104
designer toolkit (#6170). Apache-2.0.
