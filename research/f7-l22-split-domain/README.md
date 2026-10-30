# The complete length-22 parity-split domain at seven labels

**Arithmetic reduction only. No seven-label word is enumerated, no length-22
split is excluded, and `f(7)` is untouched.** This package derives, from
scratch and with a separately written implementation, the complete set of
Hamming-weight parity splits a restored universal length-22 word over seven
labels could possibly have. It is the first half of the open question recorded
in [PR #2973](../f7-weight-parity-census-correction/README.md) ("derive and
audit its complete split domain before a bounded feasibility probe").

Within PR #943's abstract singleton prefix-walk model the derived conditions
leave **11 split representatives at length 22**; importing the standing
17-point set-level exclusions of PR #2773 and PR #2870 removes exactly two of
them and leaves **9**. Nothing further is excluded by the counting or identity
conditions. A length-22 exclusion is therefore still open, and the number of
distinct configurations a future census must cover is now known exactly.

Base main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
No frozen package, pinned source, production engine or selected result is
modified.

**Overlap note.** PR #3699 independently recomputes the same `01021323`
fixture and classifies which linear functionals make the old substitution
falsely prune. That is a different deliverable: it answers *which groupings
are affected* at small `n`, while this package answers *what the admissible
split domain is* at `n = 7, L = 22`, which PR #3699 does not address. The
shared fixture arithmetic agrees exactly in both packages.

## The derivation, and what is proved here

For a word `w` of even length `L` over `n` labels, put `q_0 = 0` and
`q_i = q_(i-1) XOR (1 << w_i)`; restoration is `q_L = 0` with every label used
a positive even number of times. Universality is `P + P = F2^n` for the
**set** of distinct prefix states `P`. Because `wt(q_i) = i (mod 2)`, the
distinct even-weight states `E` and odd-weight states `O` have `s,t` bounded by
`L/2`, and `|P| = s + t`. Writing `Q = 2^(n-1)`, the four conditions are all
necessary, not sufficient:

| Condition | Statement | Where it comes from |
|---|---|---|
| Time bound | `s <= L/2`, `t <= L/2` | `L/2+1` even-time positions with `q_0 = q_L` forced to coincide; `L/2` odd-time positions |
| Odd budget | `s*t >= Q` | all `Q` odd masks need an `E x O` representation |
| Even budget | `B0 = C(s,2)+C(t,2)-(Q-1) >= 0` | all `Q-1` nonzero even masks need a same-class pair |
| Pair identity | `B0 + a*b >= need = ceil((s*t-Q)/2)` | `sum_y C(r_y,2) = 2 sum_x A_x B_x` and `C(r,2) >= r-1`; expanding on the shared support bounds `sum_x A_x B_x <= |S| + a + b + a*b` with `|S| = B0 - a - b` |

Rotation by one label translates `P` and swaps `E, O`, so existence at `(s,t)`
is equivalent to existence at `(t,s)`; the domain below lists `s >= t` only.

`verify.py` recomputes all four from their definitions. It does not import a
census engine, a predecessor package, or any recorded receipt.

## The length-22 domain

Enumerating `1 <= t <= s <= 11` and applying the four conditions gives:

| Split | `\|P\|` | Revisits forced | `B0` | `need` | Odd budget `s*t` |
|---|---:|---:|---:|---:|---:|
| `(11,11)` | 22 | 0 | 47 | 29 | 121 |
| `(11,10)` | 21 | 1 | 37 | 23 | 110 |
| `(11,9)` | 20 | 2 | 28 | 18 | 99 |
| `(10,10)` | 20 | 2 | 27 | 18 | 100 |
| `(11,8)` | 19 | 3 | 20 | 12 | 88 |
| `(10,9)` | 19 | 3 | 18 | 13 | 90 |
| `(11,7)` | 18 | 4 | 13 | 7 | 77 |
| `(10,8)` | 18 | 4 | 10 | 8 | 80 |
| `(9,9)` | 18 | 4 | 9 | 9 | 81 |
| `(11,6)` | 17 | 5 | 7 | 1 | 66 |
| `(10,7)` | 17 | 5 | 3 | 3 | 70 |

**Excluded, with the responsible condition named.** The time bound removes
`(13,5)` and `(12,6)`, which are counting-feasible at `|P| = 18` but cannot
occur in a 22-step walk because `s <= 11`. The pair identity removes `(9,8)`,
whose `B0 = 1` cannot reach `need = 4`. That leaves the 11 rows above.

**Importing the standing 17-point result.** PR #2773 and PR #2870 exclude all
six counting-feasible 17-point splits set-level. Independently, the four
conditions above already reduce `|P| = 17` to exactly `(10,7)` and `(11,6)`: the
identity removes `(9,8)` and `(8,9)` there, and `|P| <= 16` fails the odd budget
for every split. Those two remaining 17-point splits are exactly the ones the
imported result excludes, so the length-22 domain after import is the **9 rows
from `(11,11)` down to `(9,9)`**. That import is a standing claim of PR #2773
and PR #2870 and is **not re-proved here**.

**Two further consequences, both consequences of the arithmetic.** The same
conditions give a covering-cardinality floor of **17** points at `n = 7`: no
smaller prefix set satisfies the odd and even budgets. And a self-avoidance
restriction is valid at length 22 **only at `(11,11)`**, the single split where
`|P| = L`; at the other ten splits revisits are forced (1 to 5 of them), so a
census that assumes a simple cycle would silently miss most of the domain.

**What this does not say.** The necessary conditions admit all 11 splits; none
is excluded by them. An admitted split may still have no universal word, as the
fifth-length evidence at `n = 7` shows. This is a reduction of the search space
and a correction of one census precondition, not a length-22 exclusion, not a
`f(7)` bound, and not a claim about any supplier, tariff or kappa.

## Controls

`verify.py` is standard library only. Every check below was developed against
a 37-mutant battery; the survivors are reported at the end rather than hidden.

1. **The calibration fixture, reconstructed independently.** `01021323` at
   `n = 4, L = 8` has prefix set `{0,1,2,3,4,6,8,12}`, covers all 16 masks,
   has weight split `(4,4)` and bit-0 split `(6,2)`. Its bit-0 collision excess
   is 8, above the wrongly substituted balanced budget 5 and at most the correct
   actual-size budget 9. The old word-level prune is unsound on this fixture
   even inside the simple balanced class, and the bit-0 grouping is not itself
   invalid. This agrees element for element with
   `check_math.py`'s `simple_n4_counterexample` block.
2. **Published small-domain counts *and split histograms*, from my own
   enumeration.** All restored words at `(3,6)`, `(3,8)`, `(4,8)` are
   enumerated: 90/60/10, 1260/1092/182 and 2520/624/26
   restored/universal/canonical-universal, and the per-split histograms match
   `check_math.py` exactly (for `(4,8)`: 48 `(3,4)`, 48 `(4,3)`, 528 `(4,4)`).
   Histograms are a strictly stronger control than totals. Five further domains
   `(3,4)`, `(4,6)`, `(4,10)`, `(5,10)`, `(5,12)` are enumerated without a
   published comparison.
3. **The universality oracle is cross-checked and non-vacuous.** All 256 subsets
   of the fixture's prefix set are tested against a separately written per-mask
   existence loop; they agree on every subset, and exactly 7 subsets cover. An
   always-true `covers` fails this. Note the fixture is *not* minimal — four of
   its points can be dropped and the rest still covers — so a naive
   single-point-removal control would have been wrong.
4. **The conditions reject, not only admit.** On the 168 non-universal restored
   words at `(3,8)` the four conditions reject all 168. Without this the
   necessity audit inside the enumerator is one-sided and cannot fire.
5. **The published length-18 and length-20 domains and budgets.** The same code
   returns the single split `(9,9)` at length 18 and the five length-20
   representatives `(10,10)`, `(10,9)`, `(10,8)`, `(9,9)`, `(10,7)`, with even
   budgets `27,18,10,9,3` and odd excesses `36,26,16,17,6`, matching
   [MATH.md](../f7-weight-parity-census-correction/MATH.md).
6. **Condition independence, measured not assumed.** Each condition is removed
   in turn over the full enumeration range and the resulting domain compared.
   At length 22 the time bound, odd budget and identity are load-bearing and the
   **even budget is redundant**: `need >= 0`, so `B0 <= 0` already fails the
   identity. It is reported as redundant rather than presented as a fourth
   filter.
7. **Identity tightness.** The minimum slack `B0 + a*b - need` over the admitted
   splits is 2 at length 22, and the `a*b` term never decides an eligible split
   at lengths 18, 20, 22 or 24. Both are asserted, so an off-by-one in `need`
   or a weakened `a*b` bound is caught.
8. **The `ceil` in `need` is checked directly**, including odd remainders where
   floor and ceiling differ, because no length-22 verdict actually turns on
   rounding.
9. **The padding lemma.** Appending `(j,j)` pairs preserves restoration,
   containment of the prefix set and coverage, checked on every universal word
   at `(3,6)` and `(4,8)`.
10. **Input guards reject**, verified by calling the function with an odd length
    and with out-of-range dimensions.

### Mutants that did not discriminate

Two mutants survive and are **not defects**:

- Replacing `== universe` by `>= universe` inside `covers`. The pair-sum set is
  always a subset of `F2^n` by construction, so the two are equivalent.
- Appending `(j,j,j,j)` instead of `(j,j)` in the padding check. That is
  exactly two pad steps, which is the lemma under test.

One real limitation was found this way: the necessity audit in
`enumerate_restored` cannot fire on correct code, so deleting it changed
nothing. That is control 4, now fixed.

## Reproduce

Python 3.12 or newer, standard library only, from the repository root:

```sh
python3 -I -B research/f7-l22-split-domain/verify.py
python3 -I -B research/f7-l22-split-domain/verify.py --emit
```

Expected marker:

```
PASS_F7_L22_SPLIT_DOMAIN length22_self_contained=11 after_17pt_import=9 f7_untouched
```

Observed on macOS arm64, CPython 3.15.0: about 32 s, dominated by the
`(5,12)` enumeration of 6,237,000 restored words. Nearly all of that time is
in domain 8, which is a non-vacuity control; the length-22 arithmetic itself is
microseconds. No temporary files, no subprocesses, no network, no compiler.

`scripts/research_package.py --package research/f7-l22-split-domain` runs the
same command through the registered launcher with its bytecode-isolation and
timeout policy.

## Open next questions

1. **Does a restored universal length-22 seven-label word exist?** The domain
   is now exactly the 9 imported splits above, so this is a census over a known
   finite domain rather than an open one. `first_step`: run the corrected
   revisit-aware engine at `(11,11)` alone, where self-avoidance is valid and
   no revisit handling is needed, as the cheapest single case.
   `blocked_by`: the `(11,11)` node count is not estimated here. `blocked_by` is
   also a resource budget and a named decision: excluding length 22 would settle
   `f(7) = 24`, so the search needs an explicit budget and a stop rule before it
   starts. PR #2973's session stop rule was "no L22 census".
2. **Can the revisit requirement be priced rather than enumerated?** At the ten
   non-`(11,11)` splits, `L - |P|` revisits are forced. A revisit forces a
   contiguous subword with every label appearing an even number of times.
   `first_step`: derive which subword lengths can realize the forced revisit
   counts 1 to 5 at each split, which is a bounded combinatorial question with
   no search. `blocked_by`: nothing structural.
3. **Do the 18-point splits open any length-22 route?** `(11,7)`, `(10,8)` and
   `(9,9)` are the only 18-point splits in the length-22 domain, and
   [PR #2911](../community-efficient1900-audit/originals/2911/research/f7-18point-cover-question-seed6d34356c/README.md)
   leaves all four of its 18-point splits undecided. `first_step`: intersect
   PR #2911's remainder rows with this package's per-split budgets.
   `blocked_by`: `(12,6)` is not in the length-22 domain at all, so only three of
   its four splits are reachable here; the rest stays a set-level question.

## Scope, credit and verification limits

This package changes no supplier, tariff, kappa, certificate, frozen input or
selected frontier. The selected result `certificates/selected-result.json` is
untouched, and `scripts/research_baseline.py` still reports
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with the same values.

Credit Ross Richardson for the PR #943 prefix-walk model; Aaron Wang for the
PR #2542 word model and the Gray construction, and for the PR #2773/#2870
17-point set-level exclusions imported here as standing claims; Nicholas Stone
for PR #2691 and the corrected weight-parity census in
`research/f7-weight-parity-census-correction`, including the `01021323`
calibration and the length-18/length-20 domains this package independently
recomputes; Douglas Colkitt for the selected source bindings and review.
Existing source notices and licenses remain unchanged. This contribution adds
the independent derivation, the length-22 domain and its verifier.

Nick Petalas' repository workflow is followed here; this automated research
donation session wrote the code and the prose. Separate internal source
inspection and self-review are **not** independent human or proof-assistant
review. No formal-kernel proof, no full seven-label replay, no all-size transfer
and no hosted CI run are claimed.

Three obligations are not discharged. The 17-point exclusions are imported, not
re-proved, so the 9-split figure is conditional on PR #2773 and PR #2870 holding.
No test here can show that an admitted split is realizable; the conditions are
necessary only, so the length-22 domain is an upper bound on what a census must
search, not a candidate list of existing words. And the registered launcher
(`scripts/research_package.py`) was **not** run here: it gates on Python 3.12,
which is not installed on this host, so only `--check-only` (metadata and pins)
was executed locally. The commands above were run directly under CPython 3.15.0;
CI remains the first 3.12 run.