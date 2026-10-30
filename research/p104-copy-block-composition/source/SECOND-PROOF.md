# Proof and full cost

## Exact local change

Let C(F) be the retained native chart map for binary subspace F. A MOVE from F
to G implements `C(G) C(F)^-1`. The source checker factors each map into its
recursive calls and ordinary operations. It checks the signed Pauli action
and the exact global phase. The frame induction then applies at every positive
tensor width. A scalar instruction acts on registers in one common chart.
Changing that chart preserves its abstract scalar action.

The constructor uses the two exact runs in PLAN.json. It keeps their scalar
instructions unchanged and assigns the rank-four chart. It rebuilds all MOVE
instructions from the complete scalar sequence. The only changed public
boundary charts belong to helpers 742 and 225. The source contract permits
these free helper endpoints and charges their resulting target transforms.
No main endpoint changes. No helper input is assumed to be zero.

`verify.py` checks every scalar coefficient on all 767 public inputs and nine
owned coordinates. It separately checks every transpose column in reverse
chronological order. The native replay checks all maps and phases, every main
adapter and every helper normalizer. Thus this check includes the boundary
cost, not just the interior rank-four operations.

The local paid profile is:

```text
rank:   1     2    3   4    5  6  7
count: 2221  454  492  94  173  6 15
```

The local productive helper profile is:

```text
rank:   1  2   4  5  7   8    9
count: 23  5  93  8  6  36  388
```

Compared with the frozen source, the paid delta is `H1+H4-H5` and the helper
delta is `-H1+H4+H5-H8`. Paid rank mass stays 5,987. The scalar allowance stays
224,138. There are eleven owned lifetimes and at most two live owned fields.

## Physical caller and complete price

The unchanged productive controller makes eighteen full local calls. It also
pays fifteen thin queries, each of cost `104 H1`, and fifteen whole idles.
The idle ranks are `8L`: two instances of each L from two through eight and
one instance of L=9. Each instance costs 208 such jobs.

Its main productive targets are `208 H145` and the fifteen idles with rank
increased by one. The full target profile is this main profile plus eighteen
copies of the local helper profile. The full paid profile is eighteen copies
of the local paid profile plus all thin queries and all whole idles.
The physical replay checks each contact and each central-square column.
The full profiles appear literally in RESULT.json. They contain 13,390 targets
and 66,870 paid calls, with rank-mass surplus 760.

For a saving k, set `t=1-k`. The raw condition compares the complete moments
`sum(T[r] r^t)` and `sum(P[r] r^t)`. Both exact rational interval engines give
a positive margin at the tested saving `0.003113259895`. They put the raw zero
in `(0.00311325991155, 0.00311325991156)`. The retained derivative bound is
negative throughout `[0,0.0034]`, which gives the fixed-profile ceiling.
The old complete source profile has a strictly negative upper margin at the
new claimed kappa. This proves a new profile gain, not extra decimal places
from the old profile.

The completion proof uses cutoff 16, floor 17, tail offset 1/7, decay 125/128,
power 1024 and reserve 1e-12. It bounds the whole tail, productive stock and
normalized paid cost. The compiler checks all 54 strict inequalities and
four functional conditions. It includes ordinary scalar operations,
COPY/CLEAR, restoration, native adapters, thin queries, idles and routes.
The inherited BIT saving is 0.0034. The complex cost binds the resulting
conditional multiplication saving `0.00311325989`.

`PRICING-EDITS.json` declares all edits to the archived PR #5751 pricing code:
the claim and tested value, previous claim, full paid-call count, result label
and attribution. The verifier requires those exact edits. It does not weaken
any mathematical price predicate.

## Failure controls and limits

The replay rejects an old helper entry, an old block chart, a missing native
MOVE, a wrong scalar coefficient, an unpaid query, an extra target credit,
a damaged source byte and a missing central translation. The native checker
also rejects the wrong global phase. Explicit exceptions preserve these checks
under Python `-O`.

The finite receipts and inherited frame induction remain conditional on the
five framework assumptions listed in README.md. They do not materialize a
uniform word or rounded multiplier. These are author checks. Independent
review and any selected-frontier admission are separate obligations.
