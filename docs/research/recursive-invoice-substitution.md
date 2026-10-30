# Substitute a recursive bill without counting its target twice

Use this command to replace two rank-12 paid jobs by a rank-4 inner template
at scale three. `fees.json` states all added outer-level costs; it is required
even when its paid histogram is empty.

```sh
python3 -B scripts/substitute_recursive_invoice.py OUTER.json INNER.json fees.json \
  --replace 2 12 > candidate.json 2> substitution-receipt.json
python3 -B scripts/compare_recursive_invoices.py OUTER.json candidate.json
```

The output is a standard invoice. The receipt binds all three input byte streams,
the replacement multiplicities, each rank scale and the exact output bytes.
All checks complete before any invoice is written. Invalid input exits 2 with
an error on stderr. Shell redirection can still create an empty output file.

Each replacement consumes one inner target at its ambient rank R. It removes
one outer paid job at rank sR, adds the inner paid jobs at scaled ranks, and
adds all inner targets except the consumed one at scaled ranks. Several targets
at rank R are allowed; only one is consumed. Side targets are not discarded.
Copies and repeated demand entries are added exactly. The fee invoice is then
added once, at the outer ranks, and cannot contain target credits.

For `F = paid - targets` under `r^t`, this gives the exact identity

`F_new(t) = F_outer(t) + sum copies * s^t * F_inner(t) + F_fees(t)`.

The removed outer charge and the consumed inner target cancel algebraically.
This cancellation explains why simply adding both invoices counts the matched
interface twice. It also explains why omitting the remaining coproduct targets
can change the proposed gain.

## Checked contract and limits

The model, rank semantics and boundary declarations must match. The inner
ambient rank can differ. Every replacement scale must be a positive integer,
and demand cannot exceed the original paid inventory. The inner must have a
target at its ambient rank and every inner paid rank must be strictly smaller.
This last check prevents a circular recursive bill. All output count, rank and
support limits remain those of the existing invoice schema. At most 128 demand
entries are accepted; no rank is rounded and no excess demand is truncated.

These checks do not prove that a scalar/native operator lifts at scale s, that
the matched target serves the outer input, or that side targets are independent
of existing outputs. Restoration, adapters, stock, routes and compiler fees
must be derived from the construction before they enter the explicit fee file.
An empty fee bill is a declaration, not proof that those costs vanish.

## Open next questions

Apply this operation to a source-bound pair of compatible physical interfaces.
Prove target matching and independent coproduct ownership, then compare the
complete candidate bill with the existing fixed-power or concave-order tools.
The arithmetic identity alone does not establish a new κ.

Credit the signed-invoice interface and zxv/mightyOil predecessor work, plus
PR5733's integer composition helper. PR4167 supplies a different, physical
shared-primitive protocol; this tool does not verify or replace that protocol.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
