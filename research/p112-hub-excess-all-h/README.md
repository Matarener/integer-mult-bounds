# Hub excess 4h(h+1) for every hub count

Scoped answer to Open next question 1 of unpaidmoon's
[PR4145](https://github.com/CrocSwap/integer-mult-bounds/pull/4145)
(`research/p112-third-hub-extremal`): does the extremal actual-reader excess
stay equal to \(4h(h+1)\) for every hub count, not only through three hubs?

**Result (scoped proof, every \(h \ge 1\)).** Yes. In the unchanged relaxed
literal actual-reader model on the \(h\)-hub star, over any field of
characteristic zero, the complete extremal table has
\(2\bigl(3h(h+1)+2^{h+1}\bigr)\) rows, the minimum charge is

\[
16h(h+1)+2^{h+3},
\]

and the excess over the one-unit baseline is exactly \(4h(h+1)\). The charges
are 48, 128, 256, 448 and 736 for \(h=1,\ldots,5\). No new \(\kappa\); the
selected record is unchanged.

PR4145 proved the lower bound for every \(h\) and equality for \(h\le3\) by
subset census. The new step here is the extremal table and the matching upper
bound for every \(h\):

- **Readers.** Eliminating each hub coordinate \(V_j\) reduces every minimal
  reader to a circuit through \(E\) in one fixed seven-vector configuration
  \(\{E,\,G,\,E+F,\,E+F+G,\,E+G,\,F+G,\,E-F\}\) of a three-dimensional space,
  with distinct hubs assigned to the last three vectors. That configuration
  has exactly nine such circuits, so the readers are the PR4145 list for every
  \(h\): \(3h(h+1)\) per mark.
- **Sources.** Every maximal source is the zero set of a functional \(\phi\) with
  \(\phi(E)=1\), \(\phi(F)=0\) and \(\phi(G)\in\{0,-1\}\); each hub then picks
  one of two bundles. That gives \(2^{h+1}\) per mark.
- **Costs.** Outside PR4145's families A–C, the evaluator with
  \(\phi(G)=0\) if \(g\) is present (else \(-1\)) and every \(\phi(V_j)=0\) leaves
  exactly one query nonzero. Every source has a one-hub reader of cost 1.

[PROOF.md](PROOF.md) gives the argument.

## Evidence

`verify.py` checks the finite core of the proof exactly over \(\mathbb Q\):
the nine reduced circuits (all 63 subsets), the excluded three-query hub, the
per-hub source cases, and every cost-one witness on the closed-form table for
\(h\le12\). As a control it enumerates every query subset of the \(h\)-hub star
for \(h\le4\), compares the census with the closed-form table, and recomputes
every row cost by exhaustive paid-set search. A second registered command runs
the same census at \(h=5\) (\(2^{18}\) subsets). `test_controls.py` rejects
three mutations (a moved \(t\), a dropped circuit, a family-C row treated as
cost one) and confirms that the cost-two readers at \(h=2\) are exactly
families A–C.

The census is a check, not the proof. The proof covers every \(h\).

## Reproduction

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p112-hub-excess-all-h
```

Direct checks:

```sh
python3.12 -B research/p112-hub-excess-all-h/verify.py
python3.12 -B research/p112-hub-excess-all-h/verify.py --hmax 5 --closed-form-hmax 3
python3.12 -B research/p112-hub-excess-all-h/test_controls.py
```

Expected tokens: `PASS_HUB_EXCESS_ALL_H` (twice) and
`PASS_HUB_EXCESS_ALL_H_CONTROLS`. Local times on CPython 3.12: about 9 s,
40 s and under 1 s. Not run: Lean, Docker, any selected cold replay.

## Scope

Task `uniform-transfer-audit`, scope **changed**, as in PR4145. The card asks
for one caller-bound all-size implication. This package instead completes an
open question from a merged package on the same card: the all-\(h\) shape of
one finite row model. It is a side result, not a supplier or caller
implication.

What it does not establish: a characteristic-two statement (PR4145's
question 2), a physical tariff, any supplier invoice, or a change in
\(\kappa\). The cost-two lower bound for families A–C is cited from PR4145, not
reproved; `verify.py` and the controls only recompute those costs at
\(h\le5\). The 21-premise \(K_{3,2}\) certificate of PR3583/PR3698 is not
revisited.

Base `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.

## Credit

The extremal table through three hubs, families A–C and the lower bound
\(4h(h+1)\) are unpaidmoon's PR4145. The one-hub star is Nick Petalas's PR3573,
the second hub and its certificate PR3583, and the relaxed row model PR3698;
that chain retains Philippe Van Velzen's expanded identity, ctoth's coverage
question and the actual-reader lineage. The all-\(h\) reduction, source
classification, cost-one witnesses and closed-form charge are produced by
Nick Petalas.

## Open next questions

1. **Characteristic two.** Over GF(2) the vector \(E-F\) equals \(E+F=d\), so
   the reduced configuration changes and the nine circuits need not persist.
   Does the extremal table, and the excess, change in characteristic two? The
   first step is to rerun Lemma 3's 63-subset check over GF(2) and GF(4). This
   is related to PR4145's question 2 but asks about the whole table.
2. **Other star shapes.** The reduction applies to any star whose hub queries
   are \(V_j\) and two fixed core vectors minus \(V_j\). For which core triples
   and hub vectors does the excess stay quadratic in \(h\)? The first step is to
   parametrize the seven reduced vectors and enumerate their circuits through
   \(E\). No caller currently uses such a change.
3. **Charge-transfer meaning.** The row model is a relaxation. Whether the
   quadratic excess transfers to a physical actual-reader tariff is still the
   open link PR4145 names. That needs a caller, not more census.
