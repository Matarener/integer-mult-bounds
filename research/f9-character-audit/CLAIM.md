# Local sprint claim

- Track: independent verification (OS assignment seed **83**, drawn with
  `secrets.randbelow(100)` on 2026-10-25 at session start).
- Base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, canonical main fetched
  from CrocSwap; initial preloaded `66849e1` was historical and not used.
- Scope: independently check PR5459's automorphism determinant character
  over F9, particularly nonlinear terms, unequal heights, and scalar-field
  conventions. Source head: `bef3575ddb19c44434a7e2460a353eac7c4d9387`.
- Method: new exact quotient-algebra implementation, direct determinants,
  division-free determinant checks and restriction-of-scalars norm checks.
  No predecessor executable imports.
- Domain: all 72 automorphisms of F9[x]/x^3; every F9[x]/x^9 substitution
  with at most two nonlinear monomials; all flag-preserving linear maps,
  single-monomial nonlinear tails, and 83 seed-83 dense nonlinear maps on
  F9[x,y]/(x^3,y^9). Stop at this fixed domain, including failure controls.
- Deliverable: exact deterministic receipt, scope/proof note, source pins,
  standalone and registered replay, committed branch and publication kit.
- Finish: 2026-10-25 13:40 UTC; final ten minutes reserved for verification
  and handoff.

## Selection and overlap

Three candidates: independent signed-invoice order check; neutral-completion
bookkeeping; extension-field automorphism character. The first already has
an exhaustive independent discrete-slope test; the second has the primary
eight-engine and PR5414 companion coverage. The third offers distinct coverage:
PR5459's scientific checker supports only F2, F3, F4, F5, F7. Seed 83 selects
odd characteristic 3 and 83 deterministic dense samples in addition to exact
finite censuses. Increasing field size alone is not the claimed contribution:
the F3 norm oracle and semilinearity rejection control test distinct obligations.

Read the selected certificate, promotion, scientific review and current status:
selected kappa is 605457647/200000000000, conditional on the five retained
framework assumptions. No selected construction or upstream source is changed.
PR ledger lists #5252 and #5316 as partially reviewed; #5459 has no entry at
this base. Its theorem is pending, not accepted because its PR is open.

At 13:05-13:07 UTC, checked 100 recently updated open PRs, all-state searches
for Frobenius/determinant and F9/determinant, discussion search for Frobenius,
and the latest 20 handoff comments. PR5540 addresses tensor recognition over
prime fields; that is a separate task. PR5459 already includes F4 tests, so
those are not repeated. Search coverage is bounded, not a novelty theorem.
GitHub GraphQL returned no pinned issues. This local claim follows the donor's
fallback; no new reservation issue or unsolicited Discussion post was made.

Credit Ali Romman (#5459/#5316), Nick Petalas (#5252), David Ganz and the
classical local-algebra/character theory they cite. Prepared for Charan /
theon199 with substantial OpenAI Codex assistance. Apache-2.0.
