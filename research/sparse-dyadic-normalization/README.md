# Rational rank one does not bound sparse dyadic acquisition

Claim type: scoped algebraic obstruction with finite corroboration.
For every n >= 1 there is one scalar source, one mandatory observation and
an n-entry eligible menu whose exact minimum incremental acquisition count is
n, although the rational observation rank is one throughout.

Take distinct odd primes p_i, mandatory coefficient a = product_i p_i, and
eligible coefficients b_i = a/p_i. Every entry is necessary and all suffice.
The three-entry example observes 105x and may acquire 35x, 21x, 15x. Its exact
decoder is -105x + 2*35x + 21x + 15x = x. Any missing entry leaves an odd-prime
obstruction to all coefficients in Z[1/2].

More generally, any finite weighted Set Cover instance embeds exactly by
setting b_i = product of the primes outside set S_i. The feasible selections,
their complete declared acquisition charges, every optimum and infeasibility
are preserved. [PROOF.md](PROOF.md) gives the criterion, construction and
scope. No new complexity-theory classification is claimed.

This answers an eligible-menu version of the rational-versus-dyadic boundary
in Ali Romman's [PR #5789](https://github.com/CrocSwap/integer-mult-bounds/pull/5789).
Its rational-rank implementation is cited, not replayed or audited. The
contribution concerns a constrained acquisition interface; no current physical
caller is asserted to realize this synthetic menu.

## Reproduce

From the repository root, using CPython 3.12 and only its standard library:

```sh
PY=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$PY" -W error -B research/sparse-dyadic-normalization/verify.py
"$PY" -W error -B -O research/sparse-dyadic-normalization/verify.py
"$PY" -B scripts/research_package.py --package research/sparse-dyadic-normalization
"$PY" -B scripts/check_research_commit.py --package research/sparse-dyadic-normalization --check-source-history
```

Any CPython 3.12 path can replace the local interpreter path. The direct marker
is `PASS_SPARSE_DYADIC_NORMALIZATION`. Each direct invocation emits actual
enumeration counts and a generated SHA256 receipt for all six package files,
without writing outputs into the checkout. The registered commands run the
normal and optimized checks separately. The source-history preflight requires
the package to be committed first.

The executable covers all ordered menus of at most three subsets of a universe
of size at most three, including duplicate and empty sets, and all positive
integer prices in {1,2,3}. It independently checks subset coverage, integer
gcd, constructed Bezout decoding and literal scalar outputs. It also checks
all selections in the singleton family through n=12, plus failure and boundary
controls. Finite execution corroborates the proof; it does not prove the
unbounded theorem by enumeration.

## Limitations

Acquisition means selecting one declared observation. Mixing an unacquired
row, inventing a coefficient-one observation or using an odd denominator is
outside the interface. Coefficient production, magnitude, basis changes,
dirty-state restoration, source realization and a complete physical invoice
remain unpriced. The result supplies no new kappa, physical supplier, selected
frontier update, complete multiplication theorem or proof-kernel validation.

The formal-interface card was changed to an informal eligible-menu obstruction
because the cited rational tool explicitly leaves dyadic/physical completion
open. The selected-baseline orientation passed. The implementation contains no
predecessor code or live external input. SOURCES.json pins only historical
orientation and card provenance; TASK.json records the contextual predecessor
head and guide hash. Current tool limits in that PR are not hypotheses of the
unbounded theorem.

## Open next questions

- Find a named physical cut with several odd-prime losses and a priced eligible
  menu. First derive its coefficients from the actual producer and consumer.
  Without this source adapter the result is an algebraic interface obstruction.
- Identify a useful restriction on physical eligible menus that makes minimum
  acquisition tractable or bounded. First test whether prime-loss sets are
  nested, disjoint, or subject to a proved bounded-incidence condition. Generic
  rational rank supplies none of these hypotheses.

TASK.json records relevance, first steps and blockers for both questions.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman #5789 for
the rational-certificate interface and its explicit completion boundary.
Bezout identities, ideal localization, prime factorization and weighted Set
Cover are classical. The new contribution is their exact sparse acquisition
encoding and sharp unbounded rank-one family in this interface. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
