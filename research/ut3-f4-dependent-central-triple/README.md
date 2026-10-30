# Twelve calls suffice and are necessary for one UT3(F4) central triple

**Scoped formal minimum; no new kappa.** In `F_2[UT_3(F_4)]`, every word in the four involutory labels `X_1,X_w,Y_1,Y_w` with rank-one idempotent calls that realizes

```text
diag([Z_1], [Z_w], [Z_{w^2}])
```

on three registers, and the identity on every extra dirty register, has length at least **12**. The disjoint commutator schedule

```text
[X_1,Y_1], [X_1,Y_w], [X_w,Y_w]
```

attains 12. The six-call composite previously used for `Z_{w^2}` attains the same endpoint in **14** calls and is not minimal. The selected decimal stays `0.001672660197076918`.

The proof is the nilpotent corner expansion of the defining `6×6` representation together with a rank-nullity count on each letter class: `n_X>=6` and `n_Y>=6`. Full group-algebra evaluation checks the twelve-call word, the fourteen-call composite, a restored spectator, and every one-call deletion. Details are in [PROOF.md](PROOF.md).

This is a side result about one finite address alphabet. It does not change a supplier profile, a hosting bill, or `κ`. The operative donor priority revision is 6. The pinned catalogue object in this checkout is historical revision 3; the selected decimal above is the one revision 6 still binds.

## Costs

| Schedule | Calls | Letter split |
|---|---:|---|
| Disjoint commutators `[X_1,Y_1]`, `[X_1,Y_w]`, `[X_w,Y_w]` | 12 | `n_X=6`, `n_Y=6` |
| Previous composite on the third output | 14 | four + four + six |
| Rank-nullity floor | 12 | `6+6` |

At a positive per-call price `α` the sharp bill is `12α`. The two-call improvement over the composite is only an invocation saving inside this formal alphabet.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3 -I -B research/ut3-f4-dependent-central-triple/verify.py
python3 -I -O -Werror -B research/ut3-f4-dependent-central-triple/verify.py
python3 -I -B research/ut3-f4-dependent-central-triple/independent.py
python3 -I -B research/ut3-f4-dependent-central-triple/test_package.py
python3 -B scripts/research_package.py --package research/ut3-f4-dependent-central-triple
```

Expected verifier line:

```text
PASS_UT3_F4_DEPENDENT_TRIPLE minimum=12 predecessor_direct=14 nX=6 nY=6 group_order=64 idempotents=28 spectator=1 omission_controls=12 no_new_kappa
```

`verify.py` is read-only. It rejects a corrupted temporary copy of [CERTIFICATE.json](CERTIFICATE.json) and rejects duplicate JSON keys. Checks remain active under `-O`.

## Scope

The predecessor two-register minimum is eight calls for `diag([Z_1],[Z_w])`, proved by a radius-three search plus an even-length parity cut, and it left the dependent three-output word open. The block family tested there used only `Y_1`. This note keeps that alphabet and role model, replaces the unsearched length bound by an exact minimum, and does not reopen the two-register census.

Nearby bipartite commutator tariffs count independent central edges in a larger Heisenberg group. The center of `UT_3(F_4)` is the two-dimensional quotient of that four-dimensional center, so those edge multiplicities do not apply verbatim. The argument here is the quotient corner, not a citation of the cover bound.

Not claimed: a shorter word after adding `X_{w^2}` or `Y_{w^2}`; a physical bit-supplier realization; any selected-profile or `κ` change. The result is disjoint from Q8 negative-target minima, odd-kernel tariffs, flag-0 tail hosts, gate-operand parity, C5 charging, present-head side corrections, rank-7 width audits, and stock-leaf packaging.

## Open next questions

Can the involutions `X_{w^2}=(w^2,0,0)` and `Y_{w^2}=(0,w^2,0)` reduce this triple below 12 calls? Extend the complementary-summand rank identity, which uses coefficients in `{1,w}` only, to the coefficient `w^2=(1,1)`, and test whether a length-10 word appears. The blocker is that `w^2` mixes the two `F_2` summands, so the present `n_X>=6` split does not apply.

Can one of these twelve formal calls be embedded in a pinned bit supplier below the complete price of a rank-one factor? Charge frame changes, hosting, restoration, and dispatch for the `w=3,k=1` boundary of this word. The blocker is the absence of a legal physical realization; the formal count does not supply one.

## Credit

The two-register minimum, the fourteen-call composite, and the open three-output question are Cinna Davis's UT3(F4) central-pair note. The rank-one idempotent register model follows the eumemic / woklerx address-call lineage used there. The rank-nullity shape is the same style as the UT3(F2) central arguments; the corner identities and the twelve-call schedule are specific to this `F_4` quotient.

Prepared by Wentao Li with substantial AI assistance. No independent human or proof-assistant review is claimed. Apache-2.0.
