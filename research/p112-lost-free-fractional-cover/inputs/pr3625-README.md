# Lost-free P112 plane decoders cannot beat the incumbent: |S| ≤ 56

**Scoped negative result with an elementary proof. No new κ; the selected record is unchanged.**

philippeVV's plane-port follow-up 4 (Discussion 1587) proposed a family of exact masked plane decoders.
Choose a set S of ports and planes `E_a = <q_a, r_a>` (with `r_a·q_a = 0` and `r_a·r_a = 1`) such that every
q-orthogonal pair in S also has orthogonal planes. Such an S is called *lost-free*. Then
`(G/2)[S,S] ⊕ I_{S^c}` is an exact decoder, priced at `72 + 2(112 − |S|)`: the block uses at most 8 terms of
pairing rank at most 9, and every other port pays its private rank-2 term. The README there records
|S| = 32 (total cost 224). It notes that beating 224 needs |S| ≥ 37, and that no 33-set was found.

## Result

**Theorem.** Every lost-free set satisfies **|S| ≤ 56**.

*Proof.*
1. The 112 labels have exactly **4,032** orthonormal 8-sets ("frames"), and every label lies in exactly
   **288** of them (exhaustive, `verify.py`).
2. The labels of a frame are pairwise q-orthogonal, so their planes in a lost-free S must be pairwise
   orthogonal. Each plane `<q,r>` has the orthonormal basis `{q,r}`. Then k pairwise orthogonal planes carry
   2k orthonormal, hence linearly independent, vectors, so `2k ≤ 9` and `k ≤ 4`. Every frame therefore
   contains at most 4 ports of S.
3. Double counting gives `288·|S| = Σ_frames |S ∩ F| ≤ 4·4032`, so `|S| ≤ 56`. ∎

**What it means for the decoder.** Thresholds below are in the same pricing as plane-port-copy-budgets;
`w = 896/9` live families per call.

| goal | decoder cost needed | lost-free size needed | status |
|---|---|---:|---|
| beat the naive plane decoder 224 | < 224 | ≥ 37 | open (32 ≤ max ≤ 51) |
| any positive saving (`2w = 1792/9 ≈ 199.1`) | < 199.1 | ≥ 49 | open (solver bound 51) |
| **beat the incumbent** (tie budget 164 for rank-2 copies, 160 for rank-8) | ≤ 164 | **≥ 66–68** | **closed: max ≤ 56** |

At |S| ≤ 56 the family costs at least `72 + 2·56 = 184` per call, above every tie budget. So **this
family cannot raise κ**. Scope: the family as priced, with block cost 72. A block cheaper than about 52 units
(eight terms averaging below rank 6.5) is not excluded here. It would be a different construction from the
one proposed.

## Supporting evidence (computational; labelled)

- **Witness |S| = 32** ([evidence/best-32.json](evidence/best-32.json)), checked by `verify.py`. It meets every
  frame in at most 4 ports.
- **Port transitivity.** [evidence/symmetry.json](evidence/symmetry.json) holds 112 explicit linear isometries
  of `(F2^9, ·)` that preserve the label set. `verify.py` checks that they send port 0 to every port. They
  were found by `tools/symmetry.py`; the search log is in [evidence/symmetry-orbit-proof.log](evidence/symmetry-orbit-proof.log).
- **CP-SAT bound |S| ≤ 51, not a certificate.** `tools/solve.py` uses an exact model: bit-encoded planes,
  parity constraints, the no-five-orthogonal cut, the ≤ 28 plane-orthogonal neighbours cut (philippeVV
  result 1), one port fixed (valid by transitivity) and lex-leader cuts from sampled isometries. Its proven
  objective bound fell from 89 to 51 over about 7 hours on a laptop, and a further one-hour run with the lex-leader cuts did not lower it
  ([evidence/progress.log](evidence/progress.log)). This is solver output; no proof log is supplied, and
  `verify.py` does not rely on it.
- **Negative screens** (not used in the proof): exact maxima inside unions of 2 and 3 disjoint frames are
  exactly half (8/16, 12/24). Hyperplane sections of 48–64 labels already contain lost-free 32-sets
  (`tools/density.py`, `tools/frames_density.py`). So local averaging stalls near 56. The no-five-orthogonal
  condition alone allows a 38-label set (`tools/k5free.py`), but that set admits no planes (`tools/csp.py`).
  A symmetry-reduced Lovász-theta descent (`tools/theta.py`; 14,336 port-plane vertices, 8 vertex orbits)
  stalled at the trivial bound 112 because of a highly multiple top eigenvalue. A proper reduced SDP is open.

## Reproduce

```sh
python3.12 -B research/p112-lost-free-plane-bound/verify.py          # ~5 s, standard library only
python3 scripts/research_package.py --package research/p112-lost-free-plane-bound --check-only
```

`--write` regenerates RESULT.json. Controls reject five ports of one frame and a degenerate plane. The
scripts in `tools/` reproduce the evidence. They need `ortools`, `numpy` or `scipy`, use local absolute
paths, and are not part of verification.

## Open next questions

1. **Is any positive saving possible (|S| ≥ 49)?** The solver bound is 51; proving `≤ 48` would show the
   family never saves anything. First step: an independently checkable proof, either a symmetry-reduced SDP
   or a solver run with a DRAT/proof log.
2. **Does a lost-free S of size 33–36 exist?** It would beat the naive 224 without raising κ.
   First step: a search restricted to frame-structured sets meeting each frame in exactly 4 ports.

## Credit

philippeVV (Discussion 1587, follow-up 4) defined the lost-free family, its pricing and the 32-set record, and
proved the 28-neighbour cap. ctoth and Discussion 1587 supplied the plane-port contract.
JosieElliston's plane-port-copy-budgets supplied the tie budgets. thakrarsagar's PR2484 verifier supplied
the label primitives reused here. Found and checked by Claude (Anthropic) via Claude Code, in a session
donated by Mark. Apache-2.0. No human or formal review is claimed.
