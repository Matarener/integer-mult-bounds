# Construct rank-transfer plans

The hinge comparator decides concave cost order. This tool supplies a stronger,
more restricted witness: an explicit list of integer transfers between rank
slots. Use the list to identify the concentration or refinement that a source
construction must realize.

```sh
python3 -B scripts/plan_recursive_transfers.py OLD.json NEW.json > plan.json
```

The inputs use the [complete invoice schema](recursive-invoice-preflight.md).
Copy the `certificate` object from the report to `certificate.json`. A separate
replay checks every step against the original invoices:

```sh
python3 -B scripts/plan_recursive_transfers.py OLD.json NEW.json \
  --verify certificate.json
```

Ranks on each side are sorted in decreasing order and padded with zero slots.
There must be equal total rank mass on each side. The new paid vector must
majorize the old paid vector. The old target vector must majorize the new target
vector. The tool reports the first failed prefix or unequal mass when this
restricted certificate is unavailable. That result does not rule out a useful
invoice or a different concave-order proof.

Each step moves a positive integer amount d from rank a to rank b, with
`a - d >= b + d`. For a concave tariff with `f(0)=0`, this balancing step cannot
decrease `f(a)+f(b)`. Paid steps are stored from **new to old**; reverse their
order and direction to concentrate the old paid jobs. Target steps are stored
from **old to new** and increase the target credit. Thus both sides decrease or
preserve paid cost minus target credit. A nonempty plan gives a strict decrease
for every strictly concave tariff, including `r^t` for `0<t<1`.

The construction scans the target slots from left to right. It retains earlier
surplus slots and transfers from them into each deficit. The prefix condition
guarantees enough earlier surplus. A donor finishes at or above its target rank;
a receiver stays at or below its target rank. Sorted target ranks therefore
give the required balancing inequality. Each step finishes a donor or receiver,
so the process terminates at the exact target vector. Replay does not trust this
algorithm: it checks the indices, amount, inequality, and final vector directly.

For example, paid `[4,4]` to `[8]` and targets `[8]` to `[4,4]` each use the stored
transfer `(8,0) -> (4,4)`. At `t=1/2` their combined signed cost decreases by
`8 - 2*sqrt(8)`. This arithmetic example does not supply a physical operation.

Limits: 2048 expanded jobs per histogram and 1 MiB per certificate. Zero padding
is internal; zero is not a job in the invoice schema. Inputs are hashed. Invalid
certificates exit 2 and emit no success report.

## Open next questions

Match transfers to legal source operations. Charge adapters and restoration in
the complete invoice. Prove that refined targets are independent. The transfer
checker does not prove those obligations, a compiler lift, or a new κ.

Credits: classical majorization, the terminal-elision audit in PR122, the
signed-invoice comparator, mightyOil's T16 audit, and retained predecessors.
Prepared for Ali Romman with OpenAI Codex assistance. Apache-2.0.
