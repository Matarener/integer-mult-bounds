# Completed recursive outputs without intermediate payload copies

The retained C1/B1 adapter copies each completed result twice: first from an
ordinary scratch lease into its output port, then into a parent lease. This
opt-in adapter exchanges ownership of those already allocated physical roles.
The output remains distinct from the borrowed source, and dense-body validation,
dirty leases, cleanup, reuse and the original C0/A0 child bindings are retained.

The two handoffs cost **4V + 29** physical tape operations instead of **26V + 42**
for V returned symbols: an exact saving of **22V + 13**, with **zero payload
writes** at those boundaries. No extra tapes or numerical words are introduced.
[PROOF.md](PROOF.md) gives the finite-control permutation construction, ownership
invariants, complete local invoice and enclosing recurrence. A role transposition
does not move a payload between immutable physical ports; the internal role
contract explicitly changes. An immutable external output port still needs its
transfer.

This lowers a linear boundary expense. It does not change recursive child ranks,
the asymptotic saving, the selected frontier, or κ. Inherited all-size/compiler,
stock, precision and caller assumptions remain. The complete selected GL64
payload and the separately claimed complex recursive controller are not executed.

## Reproduce

Base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
Exact live source files and immutable nested archives are pinned in
[SOURCES.json](SOURCES.json). Standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/recursive-output-exchange
```

Expected: `PASS_RECURSIVE_OUTPUT_BOUNDARY`, `PASS_RECURSIVE_OUTPUT_ROUTES`,
`PASS_RECURSIVE_OUTPUT_HANDOFF`, `PASS_RECURSIVE_OUTPUT_CONTROLS`, and a successful
registered replay. The fitted before/after pair is the costly check. Direct
Git-free replay uses `python3 -I -B research/recursive-output-exchange/verify.py
--suite boundary`, replacing `boundary` with the other suite names as needed.
Keep declared inputs at their original relative paths.

[RESULT.json](RESULT.json) holds complete typed receipts. Eight literal boundary
fixtures verify the exact tariff, including record-alphabet and empty bodies.
Four complete high-route pairs retain all original independent column checks
and add occupied dirty leases plus physical-inventory audits at every handoff.
The fitted pair executes two actual preceding C0 roots, checks all 1,024 columns,
preserved parent numerical objects and heads, distinct output and full cleanup.
Controls reject aliases, inactive leases, dirty output ports, wrong origins,
malformed bodies, a missing pool-table update and corrupted source bytes.

The 486-bit swap-route fixture falls from **284,709 to 263,273** physical
operations (7.53% less). Three alternating fresh-process pairs measured median
instrumented execution of **0.209s to 0.189s** (1.11x), with nearly unchanged
whole-process time (**0.618s to 0.615s**); startup dominates that small fixture.
These are observations on this host, not universal runtime guarantees.
The fitted pair drops only **185,828,183 to 185,805,642** operations (0.0121%):
its unchanged recursive core dominates. No material fitted wall-time speedup is
claimed. Run `python3 -I -B research/recursive-output-exchange/benchmark.py` for
the same alternating route experiment. Raw measurements are in BENCHMARK.json.

## Using the adapter

`exchange.ExchangeAdapter` replaces `stage.Adapter` when compiling a fresh
PR2915 stage with the same actual `Ordinary` instance. Its publication hook is
scoped to that instance and restored on context exit. The ordinary wrapper and
pool must obey the completed-lease and disjoint-role invariants in PROOF.md.
Existing frozen modules and default dispatch remain unchanged. This package
does not compose its savings with the earlier carry or permutation-frame changes.

The implementation follows the existing finite physical reference controllers;
the finite-control refinement argument remains open to independent review.
Finite tests are not a full formal proof of the multiplication theorem.
[VALIDATION.md](VALIDATION.md) records publication checks.

## Open next questions

- Can an enclosing admitted caller adopt the finite internal role selector?
  Review its alias lifetime and immutable external-port requirements first.
  A consumer caching raw physical output references needs a new contract or a
  paid transfer; this adapter is not an automatic universal replacement.
- Which other completed handoffs retain the same ownership premises? Start
  with one named boundary, inventory every live alias, retain validation and
  derive its complete recurrence before extending this implementation.

Credit Jose Manuel/jmbarrancoml PR2809/2899/2915, David Arias PR2753,
Nick Petalas PR2808, the fixed-role/ordinary and PR2157 factor lineage, and the
retained high-cube accounting work. Tekalign, substantial OpenAI Codex assistance.
Apache-2.0.
