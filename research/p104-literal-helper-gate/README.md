# Literal slot exchange against the #3954 helper gate

**Negative interface certificate. No new κ.** Selected κ stays
`0.001672660197076918`.

Open question 1 of `research/p104-literal-slot-defect` asks whether one
adjacent pair that uses `Π P_enc Π`, rather than `P`, matches every helper
role as well as both data banks, and whether the bill is favorable. On the
PR #3954 scaffold the answer is no.

## Result

The retained caller has source charts `(T, I)` and terminal charts `(F, E)`,
with `T = C_U`, `F = C_0` and `E = F T^{-1}`. For every nonzero address `u`
and every address `v`, the exit pair `(C_0, C_u^{-1})` is not the next
entrance pair `(C_v, C_0)`. Both pairs agree only for the degenerate address
`u = v = 0`, which the scaffold excludes. `Π P_enc Π` intertwines one call's
literal encoding. It does not rewrite those chart pairs.

#3954 extends every compatibility map by identity on the 72 dirty helper
roles of a fiber. The inventory has `14976` such roles. The completed
contract charges `81` dimensions on each of them, `1213056` in total, while
the identity extension contributes `0`. A helper basis vector is fixed, so
the boundary map does not turn the identity helper entrance into the full-`F`
exit.

`Π` itself swaps the `96` N-ports. That count is the support of the
permutation, not a native tariff. Under the published hypotheses (a)–(e),
every nonnegative added rank-mass `s` leaves the excess equal to
`44096 + s`. The zero-price gate is already over capacity `2965248` by
`44096`. The bill is not favorable.

The block arithmetic and the integer identities are in [PROOF.md](PROOF.md).
`verify.py` recomputes the charts on `(F_2)^4`, the helper direct sum on a
two-port witness, and the gate.

## Scope

Task `p104-side-correction`, scope **refined**. The card asks for a changed
producer/consumer with a complete bill. This package answers the first open
question of the literal-slot certificate instead of building that producer.
The scalar obstruction in that certificate does not mention helpers or the
gate; the commutation-gap certificate has no helper roles. Those two results
stay as they are.

Base `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7.
The #3954 head retained by the family record is the source of the entrance,
exit and gate integers. This package does not import that code.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-literal-helper-gate
```

Direct check:

```sh
python3 -B research/p104-literal-helper-gate/verify.py
```

Expected marker:

```text
PASS_P104_LITERAL_HELPER_GATE charts=F2^4 nonzero_mismatch=true helper_extension=identity helper_progress=1213056 excess0=44096 ports_n=96 nonnegative_price=unfavorable no_new_kappa
```

The same command passes under `-O`. Not run: Lean, Docker, a selected cold
replay, the #3954 native census, and hosted CI.

## Open next questions

1. Can one named helper word advance one of the 72 roles per fiber and be
   subtracted from the `1213056` helper-progress charge without a new
   nonnegative cost that restores the excess? The identity extension
   contributes none of that progress. First step: freeze one fiber, write
   the identity entrance and the full-`F` exit for one role, and give the
   rank-mass of the word that connects them. Blocker: no such word is in
   the #3954 extension, and unknown physical costs are not negative
   rank-mass.
2. Is there an adjacent pair whose charts are not `(T, I)` and `(F, E)`,
   with an operator other than `Π P_enc Π`, that matches every data and
   helper role under a freshly derived gate? First step: name the two chart
   pairs and the helper schedule, then recompute capacity. Blocker: a
   different inventory or coverage law needs its own gate. The excess
   `44096` is not a theorem about that law.

## Credit

The entrance, exit, identity helper extension, N-port slot swap and the
`44096` gate are Chris R / Clear1nsight's PR #3954. The request for an
adjacent pair on every data and helper role is discussion #1166 comment
19034066. The question of whether `Π P_enc Π` answers that request is open
question 1 of `research/p104-literal-slot-defect`. The chart formula is the
one used in `research/p104-uniform-commutation-gap`. Predecessor lineage
named in those packages remains theirs, including Rohan Arun, Chafik
Boukhalfa and Adam Gall.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No
independent human or formal-kernel review is claimed. Apache-2.0.
