# F2 shadow minranks of the E6 and E7 root lines: upper bounds 8 and 11

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: finite exact certificate. No new κ.** On the root lines of E6
and E7, explicit F2 matrices with unit diagonal and zeros on every orthogonal
pair have exact F2 rank 8 and 11. Combined with the lower bounds cited from
DreamingOfClouds's [PR #2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277):

```text
mr₂(Γ_E6) ∈ {7, 8},        8 ≤ mr₂(Γ_E7) ≤ 11.
```

Before this package, no upper bound was recorded for either value. PR #2277
(`research/overcomplete-and-realisation-floors`, §8 Open next question 5)
asks for both exact values. This package answers the upper side and leaves
both exact values open.

## Object

Let `L` be the 36 E6 or 63 E7 root lines, one representative per `±` pair.
A **shadow** is an F2 matrix `N` indexed by `L` with

- `N_tt = 1` for every line `t`;
- `N_ts = 0` whenever `t ≠ s` are orthogonal;
- entries on non-orthogonal pairs free.

`mr₂(Γ)` is the minimum F2 rank of a shadow. This is the definition used in
PR #2277 §9.2 (SAT-2). In graph terms it is Haemers's F2 minrank of the
non-orthogonality graph. By PR #2277's shadow lemma, a shadow of rank at most
`m` is what a B-independent F2 certificate needs to certify all lines of a
decoder with `m` terms.

## Evidence

[WITNESSES.json](WITNESSES.json) stores `N = U Vᵀ` with F2 factors `U`, `V` of
widths 8 (E6) and 11 (E7). The lines are stored explicitly as E8 roots in
doubled coordinates. The anchors are one root (E7, the orthogonal complement
of an A1) or two roots with inner product ±4 (E6, the complement of an A2).

[verify.py](verify.py) uses the standard library only. It:

1. rebuilds all 240 E8 roots and checks that the stored lines are exactly the
   lines orthogonal to the stored anchors (36 and 63 lines);
2. checks every one of the 36² and 63² entries against the pattern: 36 and 63
   unit diagonal entries, 270 and 945 orthogonal pairs (each in both orders)
   forced to zero;
3. computes the exact F2 rank of `N` by elimination: 8 and 11;
4. rejects two mutations per unit, a cleared diagonal entry and a set
   orthogonal entry, and calibrates the rank routine;
5. enumerates every pairwise non-orthogonal 7-set and 8-set of E7 lines and
   counts exact covers of the 63 lines by nine 7-sets (see Limitations).

Output:

```text
PASS E6: 36 lines, 270 orthogonal pairs forced zero, 36 unit diagonal entries, 142/720 free entries set; exact F2 rank 8 <= 8
PASS E6 controls: diagonal and orthogonal-entry mutations rejected; rank helper calibrated
PASS E7: 63 lines, 945 orthogonal pairs forced zero, 63 unit diagonal entries, 321/2016 free entries set; exact F2 rank 11 <= 11
PASS E7 controls: diagonal and orthogonal-entry mutations rejected; rank helper calibrated
PASS E7 clique cover: no 8-set of pairwise non-orthogonal lines; 288 7-sets; 0 partitions of the 63 lines into nine 7-sets
PASS e6-e7-shadow-minrank-upper: mr2(Gamma_E6) <= 8 and mr2(Gamma_E7) <= 11
```

The witnesses were found with a CaDiCaL search of the `U Vᵀ` encoding.
[search_witness.py](search_witness.py) reproduces that search. It is optional,
needs `python-sat`, and is not part of the registered replay. Fresh runs may
return different witnesses; two such regenerated witnesses also passed
`verify.py` before submission.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/e6-e7-shadow-minrank-upper/verify.py
python3.12 -B scripts/research_package.py --package research/e6-e7-shadow-minrank-upper
```

Optional witness search (needs `python-sat`):

```sh
cd research/e6-e7-shadow-minrank-upper
python3.12 -B search_witness.py E6 8 /tmp/e6.json 60
python3.12 -B search_witness.py E7 11 /tmp/e7.json 60
```

## Limitations

- The lower bounds 7 (E6) and 8 (E7) are PR #2277's DRAT-verified SAT-2
  results. They are cited, not re-run.
- Search failures are not proofs. Plain CaDiCaL runs, each fixing `U` on
  one maximum set of pairwise orthogonal lines (4 for E6, 7 for E7), did not
  finish: E6 rank 7 (stopped after 12 minutes), E7 rank 8
  (stopped after 12 minutes), E7 rank 9 (600 s limit) and E7 rank 10 (150 s
  limit). No UNSAT claim is made for any of them.
- Only F2 is covered. Larger fields of characteristic 2 remain open, as in
  PR #2277 §8.5; an F2 witness also works over every extension field, so the
  upper bounds hold there.
- No decoder, decoder floor, supplier, invoice or κ consequence is claimed.
  The global fitting minrank of PR #2277 SAT-1 is a different problem (zeros
  on non-orthogonal pairs) and is not touched.

One structural finding narrows the E7 search. The largest pairwise
non-orthogonal sets of E7 lines have size 7 (288 of them). An exhaustive
exact-cover count in `verify.py` finds no partition of the 63 lines into nine such sets.
So rank 9 cannot come from an all-ones block-diagonal clique cover. This is a
statement about that one construction, not about rank 9.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Is `mr₂(Γ_E6)` 7 or 8?** Rank 7 would equal the global fitting minrank
   of SAT-1. First step: rerun rank 7 with symmetry breaking under W(E6). A
   possible model, not checked here, is the 36 non-singular points of an
   elliptic quadric in F2⁶. Keep a DRAT proof if the result is UNSAT.
2. **Which of 8, 9, 10, 11 is `mr₂(Γ_E7)`?** Decide rank 10 first. The 63
   lines carry an Sp(6,2) structure that gives strong symmetry breaking.
3. **Do extension fields of characteristic 2 lower either value?** Encode
   GF(4) entries and repeat the E6 rank-7 test.

## Credit

DreamingOfClouds's PR #2277 supplies the shadow lemma, the definition of
`mr₂(Γ)`, the lower bounds `mr₂(Γ_E6) ≥ 7` and `mr₂(Γ_E7) ≥ 8`, the E8/E7/E6
line construction this package follows, and the open question. Those results
are used as cited premises, not re-verified here. The `U Vᵀ` Tseitin encoding
follows that package's `lib/satgen.py`. New here: the two explicit witnesses,
their standalone checker and the exact-cover negative for E7. Independent
human and formal proof-kernel review are unclaimed.
