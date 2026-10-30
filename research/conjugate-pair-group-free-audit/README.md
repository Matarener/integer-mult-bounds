# Independent audit of #6038: a group-free four-call floor

**Independent proof audit, a stronger written theorem and a group-free finite
certificate. No new κ.** This package is by Josie Elliston, with substantial
Claude (Anthropic) assistance. New work is Apache-2.0.

Subject: Nick Petalas's [PR #6038](https://github.com/CrocSwap/integer-mult-bounds/pull/6038)
(`research/conjugate-pair-every-group`) at exact head
`0cee0e104b68ce6f06bf84af03f46ac30680e64c`. In the rank-one-idempotent
register model of Wentao Li's
[#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089), #6038 claims
that `diag([xy],[yx],[e],…,[e])` needs exactly four paid calls, for every group,
field and width `r ≥ 2`. The package does not read #6038's files and imports no
code from #6038 or #4089.

## Results

**1. Audit of #6038's PROOF.md: no error found.** I checked each step against
the model. The model and factor form match #4089's `research/a5-conjugate-any-registers/PROOF.md`
over `F2`. I checked the facts (F1)-(F3) by cancellation, the corner
identities, Lemmas 1-3 and all eight length-three patterns. For `xxy`, `yyx`,
`xyy` and `yxx` I also checked that no other subset can take the value `xy` or
`yx`. Two remarks, neither affecting correctness:

* The last clause of (F3), "`x³, y³` cannot both equal `xy` and `yx`", is
  weaker than the truth. `x³` equals neither, since `x³ = xy` or `x³ = yx`
  gives `y = x²`. The weaker clause is enough for the `xxx` pattern.
* In the `xyx` case the "corner split and Lemma 2" are unnecessary.
  `T_xy = P_12` follows directly, because `{1,2}` is the only subset with value
  `xy`.

An OpenAI Codex read-only adversarial review of the same PROOF.md and of this
verifier also reported no error. A second Codex review of this package's
Theorem S proof reported no error either. These are machine checks, not human
review.

**2. A stronger theorem with a shorter proof ([PROOF.md](PROOF.md)).** Fix
distinct `a, b ≠ e` and the target `diag([a],[b],[e],…,[e])`. If no label
equals `a` or `b`, no product of at most three paid calls reaches the target.
This holds for every label set, every coincidence among products of labels,
every field and every `r ≥ 2`. The proof uses only the coefficient equations at
`a`, `b` and `e`. It has two cases and needs neither #6038's facts (F2)/(F3) nor
its eight-pattern analysis. #6038's length-three step is the special case
`L = {x, y}`, `a = xy`, `b = yx`.

**3. A group-free finite certificate ([verify.py](verify.py)).** #6038's
finite check covers 26 coincidence keys collected from S3, S4, S5, Q8 and the
free group. This check instead lets each subset word `g_U` of a length 0-3 word
over `{x, y}` take any class in `{e, xy, yx, other}` that the single equation
`g_U = class` allows when `xy ≠ yx`. Each of the 90 equations is decided by an
exact rule:

* *allowed*: an explicit noncommuting witness pair in S3, S4 or S5 (38
  equations);
* *forbidden*: after cyclic free reduction of `g_U · class⁻¹`, one generator
  occurs exactly once, or the relator is a cyclic conjugate of `[x,y]^{±1}`.
  Either way `xy = yx` would follow (52 equations).

The verifier fails if any equation is undecided. The search drops joint
consistency and the zero equations at "other" elements. Its feasible set
therefore contains the labeling of every actual group. It searches every tuple
of rank-one idempotents in two tiers. The *full* tier uses the table above.
The *singleton* tier constrains only the single letters, exactly as in
Theorem S.

| width r | field | tuples at k = 3 | full tier | singleton tier |
|---:|---:|---:|---|---|
| 2 | F2 | 216 | no solution | no solution |
| 2 | F3 | 1,728 | no solution | no solution |
| 2 | F5 | 27,000 | no solution | no solution |
| 3 | F2 | 21,952 | no solution | no solution |
| 2 | F7 | 175,616 | no solution | no solution (local run, 87 s) |
| 3 | F3 | 1,601,613 | no solution | no solution (local run, 1,124 s) |

The first four rows are registered. The last two are local runs of the same
verifier (`--cases 2:7`, `--cases 3:3`). Lengths 0, 1 and 2 are also excluded
in every row. A local `--cases 4:2` run hit its 1,500 s timeout before
finishing and is not claimed.

Controls, all registered:

* the direct word `D_{E00}(x) D_{E00}(y) D_{E11}(y) D_{E11}(x)` satisfies the
  relaxation, and the search finds a length-four solution by itself;
* with every nonempty subset allowed in any class (pure linear algebra), a
  length-two word fits;
* wrongly allowing one single label to equal `xy` (`y = xy`) reopens length
  three (pattern `yxy`).

The search confirms that the single-label facts are the essential ones. In a
local exploratory run at `r = 2` over `F2` (not registered), I flipped each of
the 32 forbidden equations with words of length at most three, one at a time.
Only the four that put `x` or `y` in the `xy` or `yx` class reopened a short
word.

## What this does not cover

* The finite tiers cover only prime fields at the sizes in the table. Prime-power
  fields such as F4 and widths `r ≥ 4` rely on the written proofs.
* Neither proof addresses native address operations, conversion, restoration,
  a caller or any BIT supplier. The selected κ (#6030) is unchanged.
* No independent human or proof-kernel review is claimed.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -B -W error research/conjugate-pair-group-free-audit/verify.py
python3.12 -O -B -W error research/conjugate-pair-group-free-audit/verify.py
python3.12 -B research/conjugate-pair-group-free-audit/verify.py --cases 2:7   # optional, about 90 s
python3.12 -B research/conjugate-pair-group-free-audit/verify.py --cases 3:3   # optional, about 19 min
python3.12 -B scripts/research_package.py --package research/conjugate-pair-group-free-audit
```

Expected marker: `PASS_CONJUGATE_PAIR_GROUP_FREE_AUDIT`, in about 30 s per mode.

## Open next questions

1. **Longer diagonal pair targets (#6038 open question 1).** Theorem S is a
   uniform floor of 4 for any pair target whose entries are not labels. Is
   there a uniform floor of 6 for `diag([g],[h])` when neither entry is a
   product of at most two labels, for example `diag([xyx],[yxy])`? *Why:* it
   would replace per-group pair censuses with one argument. *What fails
   already (local probe, not registered):* the support-only analogue of
   Theorem S does not hold. I kept `∅` in the `e` class, kept the singletons out
   of all three classes and let only subsets of size at least three carry `g`
   or `h`. A NumPy subset-sum search at `r = 2` over `F2` then finds solutions
   at length 4 (20 of 1,296 idempotent tuples) and at length 5 (938 of
   7,776). The control with threshold two reproduces Theorem S: no solution
   up to length 3, and 264 at length 4. So a floor of 6, if true, must use
   relations among the labels, not just support sizes. A second local probe
   (stdlib, not registered) solves the exact equations in the free group on
   `x, y`: no word of length at most 5 reaches `diag([xyx],[yxy])` at `r = 2`
   over `F2`. The same code finds the four-call words for `(xy, yx)`. A
   free-group solution would map to every group, so any saving below 6 needs
   a relation among the labels. *First step:* use this
   package's full tier for the labels `{x, y}` and the target `(xyx, yxy)`.
   That needs sound rules for when a single equation forces `xyx = yxy`; the
   commutation rule used here does not imply that. Then check whether the
   length-4 relaxed solutions survive. *Blocker:* the consistency rules
   for the new hypothesis.
2. **Formalization.** Theorem S involves only rank-one matrices over a field
   and suits a proof assistant. No Lean build was attempted.

## Credit

Nick Petalas (#6038) supplied the all-group theorem, the corner-sandwich
method, the expansion and the direct word that this package audits and builds
on. Wentao Li (#4089, #4093) supplied the model and the A5 and PSL(2,7)
results; Cinna Davis (#2246) supplied the original A5 target. Their cited
statements were not re-audited beyond what is described above. Theorem S, its
two-case proof, the group-free relaxation and the verifier are new here.
Source pins are in [SOURCES.json](SOURCES.json).
