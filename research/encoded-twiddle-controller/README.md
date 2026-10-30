# Encoded sequential shape control for twiddle headers

The direct data-tape producer in PR3582 used a supplied immutable shape
scheduler. This package replaces it with an actual finite-alphabet descriptor
scan and 21 sequential binary-counter tapes. The controller emits data
instructions online, retains no program or topology table, reads every physical
address bit once, emits the exact forward/opposite exponent, clears private
tapes and restores every head and borrowed input.

[PROOF.md](PROOF.md) gives an author-written theorem for every finite valid
mixed long/short shape. The 26 fixed tapes use O(p) cells and O(p^3) complete
transitions under the retained source bands. This polynomial overhead fits the
source's asymptotic O(rp) per-record allowance. The result charges actual
descriptor/counter movement and closes the supplied-scheduler assumption for
this header producer. No optimized quadratic total-machine bound is claimed.

For descriptor interior length N and M=A+ell+1, the exact finite-alphabet
capacity is Cdata+22N+86, at most 90M. The data tapes contain
Cdata=A+max(1,d*max(a,1))+h+1+ell+1 Boolean cells. Distinct finite-alphabet
symbols require up to two bits per counter cell and three per descriptor cell;
a binary encoding uses at most 182M bits plus constant finite control.

## Evidence and reproduction

[RESULT.json](RESULT.json) records all 16,440 addresses in 240 complete small fixtures,
480 actual zero/one controller runs with identical schedules and invoices, and four
larger examples through ell=32. Each result agrees with independent named-bit
arithmetic and the authenticated canonical circuit. An independently assembled
access sequence checks every data read/write/unit move and Boolean count.
Counter and descriptor accesses are charged by their actual current-cell
execution. The executable caps ell at 32 and axes at 16.

The controls check every pair of four-bit counter values, overflow/underflow,
malformed descriptors and addresses, and poison the diagnostic counter decoder.
Optimized actual CLI fault tests reject changed masking, branch/pending state,
counter copy, remainder, erasure, motion accounting, receipt and source inputs.

Use standard-library CPython3.12 and an existing private temporary directory.

```sh
python3.12 -I -Werror -B research/encoded-twiddle-controller/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/encoded-twiddle-controller/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/encoded-twiddle-controller
python3 -B scripts/check_research_commit.py --package research/encoded-twiddle-controller --check-source-history
```

VERIFY.json registers normal/optimized science and controls. Runtime and
mathematical inputs are pinned in SOURCES.json. PREDECESSOR.json records the
exact retained PR3582 algorithm/proof bytes, origin and credit. Scientific and
control replay works from the committed Git-free package export. Git is needed
for the separate provenance/publication checks.

## Scope and credit

The producer accepts a valid self-delimiting descriptor, matching borrowed
physical address and fresh blank private/output tapes. Host admission rejects
malformed inputs; its rejection work is not an executed physical invoice.
There is no failure/retry restoration theorem. Python representations and
diagnostic trace collection are outside the physical cell bill; production
trace retention is disabled. Read PROOF.md for this boundary and the explicit
finite-control lowering of the simulator.

The source already states polynomial-time exponent computation. This result
supplies a specific executed descriptor/counter/data implementation and linear
tape-space proof. It does not provide address enumeration, signed-packet
consumption, a complete layer/root bill, arbitrary dirty-private restoration,
supplier admission, independent human/formal acceptance or a new kappa. The
selected frontier remains unchanged.

Nick Petalas's PR3582 direct tapes and PR3571 direct registers are predecessors.
Credit Douglas Colkitt and the retained transform source, its Nussbaumer/Quandalle
and Harvey/van der Hoeven lineage, Philipp / mightyOil's positional engine and
Jose Manuel / jmbarrancoml's signed-packet and phase work. PR3534 and PR3550
instead execute supplied circuit programs. Existing source notices remain
unchanged. New work is Apache-2.0.

## Open next questions

Bind one emitted header to an actual signed-packet consumer and one normalized
round, including its descriptor, packet movement, spectator state and returned
heads. This matters because a header producer alone is not a paid transform.
Start with ell=8,K=4,h=5 and the twelve mixed axes in RESULT.json. The blocker
is a complete matched caller/consumer contract and invoice. Stop if it is
unspecified or cannot fit its allowance; another isolated header optimization
does not settle that decision. The structured question is in TASK.json.
