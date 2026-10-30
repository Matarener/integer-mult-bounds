# Sharp four-term pair-reader floor

Any at-most-four-term exact realization of two literal indicator terms has
actual-reader tariff at least the original two terms, over every coefficient
field. Queries and readers can both have arbitrary external directions and
cancel outside the targets. The theorem applies to every even partition of
binary labels into orthonormal groups, with arbitrary cross-group pairings.
Original terms attain the bound. There is no supplier or new kappa claim.

For two indicators a,b with group sizes m_A,m_B, the precise statement is

```text
aa^T + bb^T = sum_(i<=4) u_i q_i^T
sum_i rank_F2 Gram(cl(q_i),cl(u_i)) >= m_A + m_B
```

Here cl completes every touched matched plane. This is the actual rectangular
query-reader bill. Disjoint pair replacements of the retained PR3370 matrix
keep total 224. Changed fitting matrices and shared native execution are outside
the theorem.

[PROOF.md](PROOF.md) gives the self-contained argument. Sylvester's rank
inequality leaves the rank-three/rank-three factor case. Its four queries and
two target vectors form a six-point configuration. Nine incidence templates
represent every rank-three configuration on six points in GF16. Subset-rank
preservation supplies new factors that retain every old source and reader zero.
The characteristic-two expanded identity supplies the bill. This closes the
explicit four-query continuation in PR3472, including the dependent case on
both sides.

## Evidence and reproduction

From the repository root, use Python 3.12 and a private existing external
directory for disposable test copies. The scripts need only the standard library.

```sh
mkdir -p "$HOME/.cache/integer-mult-bounds-runs/four-term-replay"
TMPDIR="$HOME/.cache/integer-mult-bounds-runs/four-term-replay" \
  python3.12 -Werror -B scripts/research_package.py \
  --package research/p112-four-term-reader-floor
```

Direct scientific commands also support isolated and optimized execution:

```sh
python3.12 -I -O -Werror -B research/p112-four-term-reader-floor/verify.py
python3.12 -I -O -Werror -B research/p112-four-term-reader-floor/independent.py
TMPDIR="$HOME/.cache/integer-mult-bounds-runs/four-term-replay" \
  python3.12 -I -O -Werror -B research/p112-four-term-reader-floor/test_controls.py
```

RESULT.json records all nine types and 352 labeled incidence configurations,
330 rational configurations with 21,120 source/reader requests, 256 degenerate
requests, six exact literal operator transfers at 150,528 entries, and all
50,176 entries of expanded I224. Zero/parallel elements and rank-two cases are
included in explicit controls. These fixture bills are not global search minima.

The separate implementation embeds GF16 into GF256 with different polynomial
arithmetic, reproduces the nine orbit counts, and compares all 63,360 subset
ranks for 990 configurations over F3,F5,F7. It checks 63,360 span/zero requests,
coordinate-matrix rectangular bills and 225 seven-point proof-boundary cases.
Six actual optimized CLI corruptions must reject, with positive replays before
and after restoration. See [VALIDATION.md](VALIDATION.md) for environments,
proof review, controls and limits.

Universal coverage comes from the written classification and transfer proof.
Finite checks corroborate it. Independent human and formal proof-kernel review
are unclaimed. Native acquisition, coefficients, frames, dirty restoration,
hosting, stock, precision, all-size/compiler and outer transfer remain open.
The full selected cold replay, Lean, Docker and hosted CI are not claimed.

## Sources and credit

Baseline canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. TASK.json explicitly changes the coverage-law-change card to the
released decoder handoff. This is one bounded theorem; it does not authorize
another native construction round or change the selected frontier.

Tekalign retains credit for PR3370's sixteen-group fixture. RETAINED-RANK32.json
is unchanged from its attributed predecessor. The live labels come from the
canonical DATA-PHASES.json pinned in SOURCES.json. Philippe Van Velzen and
PR3345 retain credit for the expanded identity. Credit also stays with the
PR3398 actual-reader distinction, PR3414 independent-three-query proof,
PR3463 all-finite pair-span proof, PR3472 common external-star continuation,
PR3475 triple-dictionary boundary, ctoth, Matarener/Mark, ywz65, Cinna Davis,
Adam Gall, Jeremy Diviney, Sagar Thakrar and the retained P112/E8/native/compiler
and supplier lineage. Nick Petalas supplies this six-point transfer proof and
its checks. Apache-2.0.

Exact public predecessor proof heads/blob/SHA receipts are comparison records,
not imported proof or runtime dependencies and not publication-ancestry pins.
The new proof includes its own representation, transfer and expanded-identity
arguments. Only the one declared live canonical input is needed for replay.

## Open next questions

Can five arbitrary actual terms beat the literal pair bill? A fifth term allows
seven-point configurations. The explicit non-Fano example in PROOF.md shows
that this proof's rank-preserving characteristic-two transfer can fail there.
It is not a lower-cost P112 witness. The first useful step is one exact
five-term factorization with its complete literal rectangular bill, before native
synthesis. The blocker is the absence of such a witness. Other fitting matrices,
larger target blocks and shared physical operations require their own contracts.
Stop the present four-term construction route at the sharp theorem.
