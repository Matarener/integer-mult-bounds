# An independent audit of the 20-prefix confinement step in `f(7) = 24`

**Bounded independent verification, no kappa, no frontier change.** This
package re-derives and re-checks one step of the length-22 argument in
[PR #3058](../../research/connector-covering-code/README.md) (*the minimum
universal restored seven-source singleton word has 24 steps*), and records a
word-level search with a validated positive control. It does **not** re-prove
`f(7) = 24`; the part it leaves open is named below.

## What is checked, and at what strength

In PR943's singleton prefix-walk model a word of even length `L` is restored
when every label appears a positive even number of times, and universal exactly
when its **set** of prefix states `P` satisfies `P + P = F2^7`. A 22-step word
therefore has `20 <= |P| <= 22` (the covering bound `ell(7,2) = 19` and the
size-21 and size-22 arguments are **imported**, not re-proved here).

**Step audited: `|P| = 20` is impossible.** If `|P| = 20`, every position of
the walk lies in the twenty-point set `T = P`, so the walk would be a closed
walk spanning `T`; the graph induced on `T` by the walk's seven directions `D`
must then be connected. Each direction of `D` contributes only the pairs of `T`
at that one difference, so

```
edges(G(T, D)) <= (sum of the seven largest multiplicity classes of diff(T)),
```

while a graph on twenty vertices with at most two components needs at least
eighteen edges. Every 20-point cover is an affine image of `{0} u S` for one of
the five 19-point representatives classified in DMP's Table 1 (imported), and
`G(M T + b, D) = G(T, M^-1 D)`, so one inequality per representative covers
every basis and every cover.

| Representative | largest 7 difference multiplicities | their sum | edges for <= 2 components | verdict |
|---|---:|---:|---:|---|
| 1 | 3,3,3,3,3,3,3 | 21 | 18 | arithmetic bound insufficient |
| 2 | 3,3,3,3,3,3,3 | 21 | 18 | arithmetic bound insufficient |
| 3 | 3,3,3,3,3,3,3 | 21 | 18 | arithmetic bound insufficient |
| 4 | 2,2,2,2,2,2,2 | **14** | 18 | **excluded for every basis, by arithmetic** |
| 5 | 2,2,2,2,2,2,2 | **14** | 18 | **excluded for every basis, by arithmetic** |

For representatives 1-3 the inequality does not decide the case. The verifier
therefore reports them as **open**, with two pieces of bounded evidence only:
the exact component count in the canonical basis is 9, 12 and 4 respectively,
and over 200 deterministic pseudo-random bases per representative the minimum
component counts are 6, 5 and 5. No sampled basis produced two components, but
sampling is not a proof and this package does not claim one.

So the deliverable is: a complete, enumeration-free exclusion of `|P| = 20`
for two of the five cover classes, a reproducible partial record for the other
three, and the arithmetic that reduces a simple 22-cycle to exactly two
multiplicity patterns. This is a **bounded audit**, not a replacement for
PR #3058's own component/rank argument, which it neither confirms nor refutes
in the three open classes.

## Word-level search with a positive control

`search_words.py` is a deterministic-seed simulated-annealing search over
arrangements of a fixed multiset of even label counts, maximising the number of
masks of `F2^7` realised as `XOR` of a contiguous subword. It is calibrated on
the one case where a universal word is known to exist.

| Length | multiplicity pattern | best coverage found | word | verdict |
|---:|---|---:|---|---|
| 24 | `(6,4,4,4,2,2,2)` | **128/128** | `145164232614626031626540` | universal, restored, `|P| = 24` (positive control) |
| 22 | `(4,4,4,4,2,2,2)` (pattern B) | 126/128 | `1206231531046325014203` | near miss; masks 82 and 120 unrealised |
| 22 | `(6,4,4,2,2,2,2)` (pattern A) | 125/128 | `2130240236105010621045` | near miss; masks 50, 73 and 92 unrealised |
| 22 | unrestricted | 126/128 | (pattern B word) | no universal 22-step word in ~6.2M evaluations |

The 24-step word is a second, independently found universal construction in the
PR943 model, so the search method is not one-sided; `f(7) <= 24` is therefore
recertified here by an explicit certificate rather than imported. The 126/128
pattern-B word is a simple 22-cycle (|P| = 22) with no repeated prefix, so it
lives in the exact case PR #3058's section 5 claims to exhaust; it is a
two-mask near miss, which is what an exclusion there would have to survive. The
search is stochastic: the table records verified words, and a rerun is not
guaranteed to reproduce the same best coverage.

The two simple-cycle multiplicity patterns `(6,4,4,2,2,2,2)` and
`(4,4,4,4,2,2,2)` are re-derived in the verifier from the imported projections
`f(6) = 16` and `f(5) = 12`: deleting one or two source coordinates projects a
universal word to a universal word on fewer sources, so every multiplicity is
at most six and every pair sums to at most ten.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/f7-l22-confinement-audit/verify.py
python3 -B research/f7-l22-confinement-audit/search_words.py --seconds 60
```

Expected marker from the verifier:

```
PASS_F7_L22_CONFINEMENT_AUDIT arithmetic_complete=2/5 sampled_only=3 f7_untouched
```

The verifier runs in well under a second. `search_words.py` is the stochastic
search of the table above; its default budget is one minute per pattern and it
prints every verified improvement.

## Open next questions

1. **Do representatives 1-3 admit a basis with three components or fewer?** The
   counting inequality is short by three edges (21 against 18). `first_step`:
   search bases that use the three-edge multiplicity classes greedily, and
   decide the 2-component case for one representative completely.
   `blocked_by`: the naive independent-subset enumeration did not finish inside
   this session's budget; a smarter connectivity-only search is needed.
2. **Is the near-miss pattern-B word two masks short of an impossibility
   certificate?** `first_step`: run PR #3058's `verify_cycles.py` search on the
   two masks 82 and 120 and report which structural condition rejects exactly
   those two.
   `blocked_by`: it is a 760-line C++ search; this session did not run it.
3. **Does an unrestricted-multiset 22-step word ever exceed 126/128?**
   `first_step`: repeat the search with the three-edge classes forced early.
   `blocked_by`: none; it is a longer stochastic run, not a proof.

## Scope, credit and verification limits

No supplier, tariff, kappa, certificate, frozen input or selected result is
changed; `certificates/selected-result.json` is untouched.

Credit Ross Richardson for the PR943 prefix-walk model; Alexander Davydov,
Stefano Marcugini and Fernanda Pambianco for the published covering-code facts
and the minimal 1-saturating classifications transcribed in
`research/connector-covering-code/table6.json`; Nicholas Stone for the corrected
word-census budgets in PR #2973; and the PR #3058 contributor for the `f(7)=24`
theorem, its component/rank argument and its section 4 multiplicity reduction,
which this audit re-derives independently rather than assuming. Douglas Colkitt
for the selected source bindings and review.

This contribution was produced by Nick Petalas with AI assistance. Independent
human and formal proof-kernel review are unclaimed.

Three obligations are not discharged. The classification of 20-point covers,
the covering bound `|P| >= 20`, `f(5) = 12`, `f(6) = 16`, the size-21 argument
and the size-22 simple-cycle exhaustion are **imported**, so nothing here
re-establishes `f(7) = 24` on its own. Representatives 1-3 carry sampled
evidence, not proof. And no hosted CI replay or registered-launcher 3.12 run is
claimed unless the PR records one.
