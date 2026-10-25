# Independent acceptance of the separated A2 composition

**Audit of an existing scalar identity. No new κ. Selected κ stays 0.001672660197076918.**

## Scope and evidence

Original card: `independent-moment`, scope **changed**. The card's #2979 group audit is already
covered by open V45 work (#3543, #3911) and the merged group A–D native-width audits. This package
takes the still-open handoff on
[discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19036786):
independently accept the composition and projected-cleanup argument in
[PR #4019](https://github.com/CrocSwap/integer-mult-bounds/pull/4019), head
`f408e09df300b575235f7f77f81948071397e16d`.

The two rational identities, for distinct registers `x, y, z` and nonzero rationals `a, b`, are

```text
[S(a), T(b), U(-ab)] = [T(b), S(a)]
[U(ab), T(b), S(a)]  = [S(a), T(b)]
```

with `S(a): y += a*z`, `T(b): x += b*y`, and `U(c): x += c*z`. Both sides of the first identity end at
`(x + b*y, y + a*z, z)`. Both sides of the second end at `(x + b*y + ab*z, y + a*z, z)`, for an
arbitrary initial triple. The checker proves those endpoints, and the same maps as 3×3 matrices,
before it looks at a word.

On both vendored provider words the eight published sites each match exactly one identity:

| Section | Indices | Identity | Removed record | New-site cleanup effect |
|---|---|---|---|---|
| A | 1858, 1859, 1860 | first, drop `U` | credited PR #3998 site | not counted in the new split |
| B | 4, 53, 54 | second, drop `U` | target write | helper ADD unchanged |
| B | 7, 49, 50 | second, drop `U` | target write | helper ADD unchanged |
| restore | 20, 21, 36 | first, drop `U` | non-target write | one cleanup ADD |
| restore | 22, 23, 38 | first, drop `U` | non-target write | one cleanup ADD |
| restore | 26, 27, 51 | first, drop `U` | non-target write | one cleanup ADD |
| restore | 30, 31, 62 | first, drop `U` | non-target write | one cleanup ADD |
| restore | 32, 33, 73 | first, drop `U` | non-target write | one cleanup ADD |

Every intervening scalar event misses the site's three registers. The eight supports are pairwise
disjoint. No new B window contains a native-warp index, and the A site starts at or after the
prelude. The seven new published replacements equal the identity's right-hand side, including the
ordered frame list. The credited A1858 replacement has the same ADD edges and the same frame span,
but the ordered frame is `[42, 82]` rather than the source `[82, 42]`, which PR #4019 already
discloses. The new record split is **7 forward ADD deletions and 5 projected-cleanup ADD deletions**.
That is one forward deletion at each new site, and a cleanup deletion only where the deleted ADD
does not write a target.

This is an acceptance of that composition and record split. It is not a second recursive-histogram
replay, not a check that PR #4041's later-word transfer is valid, and not a κ claim. The predecessor
states that the histogram stays `{1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}`. This package does not
recompute those ranks.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/staged544-a2-composition-audit
```

Expected marker:

```text
PASS_A2_COMPOSITION_AUDIT providers=2 sites=8 new_forward_adds=7 new_cleanup_adds=5 known_frame_order_swaps=2 controls=3 no_new_kappa
```

The three controls reject a flipped B4 coefficient, an intervening read of register 518, and the
identity-one endpoint under the wrong `U` sign. Inputs are the two compressed provider words and
`inputs/data.json` taken from PR #4019 at the head above. Their SHA256 pins are checked before use.
Base commit is `bb4bccbf42844d2801487450727c2f63e10d1d0f`. Priority revision 6.

## Open next questions

- Does one later exact provider word, in particular a PR #3945 word, admit these same contractions?
  Pin that word and recheck every index, boundary, intervening support, cleanup count and paid
  profile. This package has only the two PR3734 providers.
- Can a different scalar graph remove a paid frame transition? Name the changed boundary and a
  complete favorable bill first. These seven sites do not, by themselves, move a rank count.

## Credit

Chris R / Clear1nsight, PR #3998, for the A2 identity and the consecutive A1858 contraction.
ToikY, PR #4019, for the seven separated witnesses, the published receipt, and the stated endpoint
argument accepted here. Dataisfire for the PR3734 words retained by that package. The ordered-frame
swap on the credited site is their disclosure, not a new defect. New audit by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0. No independent human or formal-kernel review is
claimed.
