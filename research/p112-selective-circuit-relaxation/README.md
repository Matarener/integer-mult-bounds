# Query-only circuit relaxations preserve marked recovery

Requiring a full characteristic-dependent matroid representation can retain
decoder candidates that cannot improve the P112 invoice. This package proves
that relaxing a circuit-hyperplane containing no marked target preserves every
old target recovery and every query coordinate-zero pattern, whenever the
relaxed matroid has a characteristic-two representation.

The fixed three-hub signed-graph/Dowling dictionary supplies an explicit F4
witness. Exactly one of its 512 augmented subset ranks changes: a query-only
triangle changes rank2 to rank3. All192 marked target/support requests transfer.
Arbitrary actual readers and arbitrary placements of three disjoint canonical
marks consequently have at least their unchanged canonical bill: 18 for three
ordinary marks, or 334 after retaining the other canonical projectors.

This is a scoped negative result and a useful screening criterion. It does not
construct a cheaper decoder, lower the selected multiplication bound, or assert
that every query-only relaxation is representable in characteristic two.
The proof also records the conditional extension to query-only stressed
hyperplanes, using the exact rank-change theorem of Ferroni, Nasr and Vecchi.

## Evidence and reproduction

`PROOF.md` contains the general lemma, explicit witness, actual-reader transfer
and self-contained full-group rank argument. `verify.py` checks the192 recovery
requests, all512 augmented subsets, both immutable scientific inputs, all111556
entries of the canonical I334 expansion, every canonical term invoice, and an
I18 local restriction. `independent.py` reconstructs ranks independently with
integer determinants and finite F4 spans; it does not import the producer.
Finite replays support the fixed witness and geometry; the general lemma is a
written proof, not a finite enumeration theorem.

From the repository root, using Python3.12 or later and no third-party modules:

```sh
python3 -I -O -Werror -B research/p112-selective-circuit-relaxation/verify.py
python3 -I -O -Werror -B research/p112-selective-circuit-relaxation/independent.py
python3 scripts/research_package.py --package research/p112-selective-circuit-relaxation
```

The producer default is read-only and requires byte-equal `RESULT.json`.
`--write-receipt` explicitly regenerates that receipt. Only the two foundational
geometry files listed in `VERIFY.json` are live scientific inputs. The selected
record and original priority card are historical provenance. No pending PR is
required to reproduce or prove this result.

## Open next questions

- Can a new dictionary retain characteristic-dependent **marked recovery** after
  all admissible query-only relaxations? First specify its marked basis and
  exhibit a recovery obstruction preserved under those relaxations. No such
  replacement dictionary or full physical invoice is supplied here.
- Can a proposed relaxation give a cheap screening certificate before physical
  placement? First supply one characteristic-two representation and verify
  target recoveries and coordinate-zero patterns. Finding a representation is
  an additional obligation, not guaranteed by the lemma.

Structured relevance, first steps and blockers are in `TASK.json`.

## Sources and credit

Thomas Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf),
Section5.6, PDF page24, gives the complete signed-graph configuration consisting
of coordinate vectors and their pairwise sums/differences. The marked choice,
F4 witness, query-only relaxation lemma and P112 invoice consequence are local
deductions, not attributed to that source. Standard circuit-hyperplane relaxation
facts used by the lemma are proved in `PROOF.md`.

Luis Ferroni, George D. Nasr and Lorenzo Vecchi,
[Stressed Hyperplanes and Kazhdan-Lusztig Gamma-Positivity for Matroids](https://arxiv.org/pdf/2110.08869),
arXiv:2110.08869v2 (27 June 2022), Theorem3.4 and Proposition3.7, supply the
rank-change theorem for the conditional stressed-hyperplane corollary. Its
marked-recovery consequence is a local deduction.

The foundational P112 geometry is retained with its existing repository credit;
the package does not modify or vendor it. Exact source blobs and hashes are in
`SOURCES.json`. Prepared for flyingviper with substantial OpenAI Codex assistance
for proof, code, separate-agent auditing and packaging. No independent human or
formal-kernel verification is claimed. Apache-2.0.
