# Exact signed packets between synthetic rounds

This package implements the retained synthetic transform's J_E operation on
complete MSB-first Gaussian coefficient packets. A sequential data-tape
interpreter performs the signed negacyclic rotation, preserves the borrowed
source, clears private data and rejects incomplete words or signed overflow.
Its inverse uses headers -E. The source already proves the rotation identity
and asymptotic scan cost. This contribution makes that data boundary executable
and gives an explicit data-role, movement and restoration contract.

[PROOF.md](PROOF.md) covers every finite record count, polynomial extent and
word width. Five data roles use 2N+2L+w cells, including input and output, where
L=2rw and N=nL. Successful data-tape work is at most 37N+6L+3w, below the checked
public bound 64N+16L+16w+8n. Externally supplied headers and host counters are
excluded. The closed disk fits in p+2 signed bits, with no width growth or
additional rounding under J_E. These are data-boundary statements, not a
production fixed-tape caller or full runtime invoice.

## Evidence and reproduction

Use CPython 3.12 and an existing private external directory for TMPDIR:

```sh
python3.12 -I -Werror -B research/synthetic-monomial-packets/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/synthetic-monomial-packets/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/synthetic-monomial-packets
python3 -B scripts/check_research_commit.py --package research/synthetic-monomial-packets --check-source-history
python3 -B scripts/export_research_package.py export --package research/synthetic-monomial-packets --output /absolute/private/run/package.tar
python3 -B scripts/export_research_package.py check /absolute/private/run/package.tar
```

`verify.py` authenticates all three external source inputs and compares the
entire recomputed receipt to [RESULT.json](RESULT.json). It checks 32,370
word/phase combinations, four mixed packets through 128-bit components and
62-bit signed headers, invalid data/extent/header rejection, and a valid retry.
Eight rounded forward/opposite transforms exercise mixed long/short shapes and
the current named-slot layout. They check 2,240 component-error inequalities
and compare exact-grid outputs with the retained unnormalized engine divided
by its complete factor M. The arithmetic uses exact fractions.

`test_controls.py` runs the optimized actual CLI in a private source-only copy.
It checks a valid smoke replay and rejects unsigned wrap, lost negative quotient,
wrong signed negation, splitting a Gaussian coefficient, wrong opposite phase,
changed source bytes and missing source. It does not copy or chmod runtimes.
`--smoke` is a smaller semantic test and is not the complete receipt replay.

## Scope and attribution

The supplied per-record exponents and loop counters are host control. The
executable bounds are n<=128, r<=64, w<=128 and |E|<2^63. The full-transform
fixtures use a rational simultaneous-butterfly reference and the retained
indexed layout engine. They do not execute the production T74 root. Encoded
header production, physical layout movement, the recursive layer, ordinary
callee, hosting, complete storage/cost invoice, outer recovery and supplier
admission remain separate. No improved kappa or selected-frontier change is
claimed. Independent human and formal proof-kernel review are unclaimed.

Credit Philipp `mightyOil` for the unchanged positional engine, Jose Manuel
`jmbarrancoml` for the unchanged signed packing oracle and PR2298, and Douglas
Colkitt and the retained synthetic-transform source for the construction and
dependency audit. The source credits Nussbaumer and Quandalle, and Harvey and
van der Hoeven. Existing source notices remain unchanged. New material is
Apache-2.0. [SOURCES.json](SOURCES.json) pins canonical live bytes and provenance.

PR3493 at c0ee30f63a89c3bd0eabb3ea7eaa7786d5ad707f and PR3504 at
c68e1a539c4df689a048e97fa0285640fd7e8911 motivate the boundary question. They
are comparison context, with no imported runtime or proof dependency. Their
dimension/format and integral-algebra results remain distinct. The earlier
PR673 transform and PR1462 truncation/frame audit are not repeated here.
PR3087 at e7e49fb8176772c71ad7006920a407109a89e440 already implements encoded
Gaussian i-phases and affine record-address monomials on LSB-first fields.
This package instead rotates polynomial coefficient positions by y^E inside
each record, with MSB words and supplied headers. It claims no first signed
negation primitive or improvement to PR3087's encoded controller.

## Open next questions

Implement the per-record exponent producer on encoded descriptors and stream
addresses, then connect one complete round to an actual normalized physical
root with its native and ordinary contracts. Start from the supplied header
formula in PROOF.md and preserve exact whole-record extents, disk/grid format,
source/head restoration and a complete control/data movement invoice. This
matters because the present packet proof alone cannot fill the remaining
outer-round implementation gap. The producer, actual root refinement and full
caller bill are the blockers. No additional phase census is needed first.

Engineering bounds and runtime deviations are in [ENGINEERING.md](ENGINEERING.md).
