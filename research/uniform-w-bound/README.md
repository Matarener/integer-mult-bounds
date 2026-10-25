# Dividing by the role count does not bound the recurrence alone

**Partial. No new exponent.**

The transfer review uses the normalized recurrence

```text
F(e) <= (1/W) sum_i F(t_i floor(e/m)) + C
```

and proves `F(e) <= A e^tau` when `Psi(tau) < 1`. The factor `1/W` is not
enough by itself. Four children of width 2, with two roles and modulus 4,
satisfy `1 <= t < m`. At `tau = 1/2` the square of Psi is 2, so Psi exceeds 1.
The recurrence gives the normalized value 3 at width 8, and `9 > 8`, so the
value exceeds the square root of the width.

One child of width 1, with four roles and modulus 4, has Psi `1/8`. The
allowance `8/7` covers the normalized values through width 64.

## What was executed

The checker evaluates that recurrence exactly. It pins the review's displayed
formula and the audit sentence that names normalization by W. It does not
replay a network or open a parking schedule.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
recurrence boundary. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the audit guide and the transfer review. No
selected frontier file changes.

Upstream checkpoint: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6, checked 2026-10-18 04:40 UTC. Canonical main and the fork main
were at that commit. The task draw was `uniform-transfer-audit`, seed
`9205c870f1ce88c8dd17feaa57cac8c3`. The latest handoff comments are completed
releases.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/uniform-w-bound/verify.py
python3.12 -B research/uniform-w-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/uniform-w-bound
```

The replay finishes in under a second.

## Open next questions

The counterexample is a legal width list under `1 <= t < m`. The next reading
is whether one retained parking node already has Psi below 1.

## Credit

The normalized recurrence and the Psi hypothesis are stated in the maintainer
transfer review. The audit guide names normalization by W as the assertion
that a finite identity test does not settle.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
