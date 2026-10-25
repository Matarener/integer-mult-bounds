# Six axis labels still take twelve calls for one UT3(F4) triple

**Scoped formal minimum; no new kappa.** In `F_2[UT_3(F_4)]`, every word in the six involutions

```text
X_1, X_w, X_{w^2}, Y_1, Y_w, Y_{w^2}
```

with rank-one idempotent calls that realizes

```text
diag([Z_1], [Z_w], [Z_{w^2}])
```

on three registers, and the identity on every extra dirty register, has length at least **12**. The coefficient `w^2=(1,1)` mixes the two `F_2` summands, so the four-label complementary split does not apply. The diagonal-lift lemma replaces it: the output shadows of `{1,w,w^2}` still satisfy `dim span{u} <= rank(U)`, and both letter classes need six calls. Two twelve-call words attain the endpoint. One uses `X_{w^2}` with `Y_1` only. The other uses both `X_{w^2}` and `Y_{w^2}`. The selected decimal stays `0.001672660197076918`.

On the mixed word the `{1,w}` shadows span only two coordinates. That is the sense in which the older split is blind. The `w^2` column supplies the third direction and still consumes one lift dimension. Details are in [PROOF.md](PROOF.md).

This is a side result about one finite address alphabet. It does not change a supplier profile, a hosting bill, or `κ`. The operative donor priority revision is 6. The pinned catalogue object in this checkout is historical revision 3; the selected decimal above is the one revision 6 still binds.

## Costs

| Schedule | Calls | What is new |
|---|---:|---|
| Mixed word `[X_1,Y_1]`, `[X_w,Y_1]`, `[X_{w^2},Y_1]` | 12 | uses `X_{w^2}` |
| Both-new word `[X_1,Y_1]`, `[X_{w^2},Y_{w^2}]`, `[X_w,Y_w]` | 12 | uses both new labels |
| Diagonal-lift floor on six labels | 12 | `dim span{u} <= rank(U)` |

At a positive per-call price `α` the sharp bill is `12α`. Adjoining the two `w^2` labels does not improve it.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3 -I -B research/ut3-f4-w2-lift-obstruction/verify.py
python3 -I -O -Werror -B research/ut3-f4-w2-lift-obstruction/verify.py
python3 -I -B research/ut3-f4-w2-lift-obstruction/independent.py
python3 -I -B research/ut3-f4-w2-lift-obstruction/test_package.py
python3 -B scripts/research_package.py --package research/ut3-f4-w2-lift-obstruction
```

Expected verifier line:

```text
PASS_UT3_F4_W2_LIFT six_label_minimum=12 labels=6 mixed_word=12 both_new_labels=12 nX=6 nY=6 blind_span=2 lift_rank=3 shadow_subsets=82160 spectator=1 no_new_kappa
```

`verify.py` is read-only. It rejects a corrupted temporary copy of [CERTIFICATE.json](CERTIFICATE.json) and rejects duplicate JSON keys. Checks remain active under `-O`.

## Scope

The four-label exact minimum, including its disjoint commutator schedule and its `n_X>=6` split, is a prior result on a smaller alphabet. This note answers the question that result left open: the mixed summand does not produce a shorter legal word. The separated span on the mixed witness is 2, which is why that earlier split cannot be cited for this alphabet.

Not claimed: a reprint of the four-label theorem; a fourteen-call composite; a non-idempotent shortening; a physical bit-supplier realization; any selected-profile or `κ` change. The result is disjoint from Q8 negative-target minima, odd-kernel tariffs, flag-0 tail hosts, gate-operand parity, C5 charging, present-head side corrections, rank-7 width audits, and stock-leaf packaging.

## Open next questions

Can rank-one calls that are not idempotent reduce this six-label triple below 12? Keep the six axis labels, drop `N^2=N`, and test whether a nilpotent factor can feed a three-dimensional corner. The blocker is that `v·u=0` kills every quadratic scalar `v_X·u_Y`, so the present normal form does not admit those factors.

Can one of these twelve formal calls be realized in a pinned bit supplier below one rank-one complete price? Charge frame changes, hosting, restoration, and dispatch for either twelve-call word. The blocker is the absence of a legal physical realization.

## Credit

The two-register minimum and the open three-output question are Cinna Davis's UT3(F4) central-pair note. The four-label exact minimum that posed the `w^2` question is the dependent-central-triple note. The rank-one idempotent register model follows the eumemic / woklerx address-call lineage used there.

Prepared by Wentao Li with substantial AI assistance. No independent human or proof-assistant review is claimed. Apache-2.0.
