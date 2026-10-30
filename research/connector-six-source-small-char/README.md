# Six-source depth-two connector blocks: none in characteristics five and six (local SAT)

**Scoped finite exclusion for the unchanged unsigned dirty connector; local
solver evidence only; no new κ.**

In the interface of [PR4231/PR4248](../connector-depth-blocks/README.md), no
word on six sources that calls each source exactly five times has depth two
in characteristic c = 5. Three SAT solvers report UNSAT on the same exact
encoding, and the result already holds for the 16 masks of weights 2 and 6.
Six-source depth-two blocks exist for every c ≥ 8
([PR6057](https://github.com/CrocSwap/integer-mult-bounds/pull/6057),
[PR6061](https://github.com/CrocSwap/integer-mult-bounds/pull/6061)), and
five-source ones for every c ≥ 5
([PR6035](https://github.com/CrocSwap/integer-mult-bounds/pull/6035)).
Deleting a source keeps depth two (PR4232/PR4248), so the largest depth-two
block in characteristic five has exactly five sources. The same encoding is
also UNSAT at c = 6 (CaDiCaL 1.9.5 and MapleChrono agree), so the largest depth-two block there has five sources too. c = 7 is
still open.

This answers the c = 5 and c = 6 cases of open question 1 of PR6061 and of the open item
in PR6057 / [#6058](https://github.com/CrocSwap/integer-mult-bounds/discussions/6058)
("characteristics five through seven remain open").

**What is and is not established.** The c = 5 verdict is the output of
CaDiCaL 1.9.5, CaDiCaL 1.5.3 and Glucose 4 on one machine, plus CaDiCaL
1.9.5 on the encoding without weight pruning; the c = 6 verdict is CaDiCaL
1.9.5 and MapleChrono. No DRAT/LRAT proof
was checked, and no human proof is given. `verify.py` (standard library)
checks only the literal words: the positive controls and the encoding's
pruning identity on them. Treat the exclusion as a reproducible local
computation, not a certificate.

## Interface and question (inherited, unchanged)

Let a word w of length kc call each source operator B_j exactly c times (a
floor word on its k sources). Let q_t ∈ Z^k count the calls of each source in
the first t letters. PR4248 says w has **depth two** if every nonzero binary
mask m ∈ {0,1}^k is congruent mod c to q_s + q_t for some boundaries s ≤ t
(s = 0 gives a single read, since q_0 = 0). Depth-two blocks with total depth
at most c concatenate to a floor word for the whole batch, so larger blocks
raise the source count N(c) at which the complete-call floor is attained.
No operation is added and nothing about the alphabet changes.

## Result

| k | c | verdict | evidence |
|---|---|---|---|
| 5 | 4 | UNSAT | control; matches PR4271's c = 4 obstruction (Nick Petalas) (2.8 s) |
| 5 | 5 | SAT | control; word checked by `verify.py` |
| **6** | **5** | **UNSAT** | CaDiCaL 1.9.5 153 s, CaDiCaL 1.5.3 197 s, Glucose 4 237 s; without weight pruning (`--no-weight-prune`) CaDiCaL 1.9.5 2332 s |
| 6 | 5, weights {2,6} only | UNSAT | CaDiCaL 1.9.5 160 s (16 masks suffice) |
| 6 | 5, weights {1,2,3} only | UNSAT | CaDiCaL 1.9.5 106 s |
| 6 | 5, weights {1,2,6} only | UNSAT | CaDiCaL 1.9.5 130 s |
| 6 | 5, weights {1,2}, {1,6}, {1,5,6} | SAT | each found in < 4 s; one word is a `verify.py` control |
| **6** | **6** | **UNSAT** | CaDiCaL 1.9.5 1263 s, MapleChrono 2056 s |
| 6 | 7 | open | no verdict within the session |
| 6 | 8 | SAT | control (PR6057/PR6061 range); found word checked by `verify.py` |

A subset of masks is a relaxation, so UNSAT on weights {2,6} alone implies
the full UNSAT. The SAT rows bound how far that core can shrink by weight
class.

## Encoding (search_sat.py)

Variables: the source at each position (one-hot, exactly c per source by a
sequential counter); the residue of every prefix coordinate mod c (one-hot,
with the one-step transition); for each mask and admissible pair (s, t) a
selector y whose truth forces q_s + q_t ≡ m coordinatewise
(`y ∧ [q_s[j] ≡ v] → [q_t[j] ≡ m_j − v]`); one clause per mask over its
selectors. Symmetry breaking: sources first appear in label order, which is
sound because relabeling sources permutes mask coordinates and preserves the
set of binary masks.

Pruning: a pair can realize m only if s + t ≡ |m| (mod c), because the
coordinate sum of q_t is t (the weight identity of PR6107). Other pairs are
omitted. Boundary kc is dropped since q_{kc} = c·1 ≡ q_0.

Positive and negative controls (k = 5 at c = 4 and 5, k = 6 at c = 8)
reproduce the known answers. The c = 8 word the solver found is in
`verify.py`.

```sh
# registered standard-library replay (< 1 s)
python3.12 -I -W error -B research/connector-six-source-small-char/verify.py
# local search (python-sat 1.9.dev15; minutes per run)
python search_sat.py 6 5 --solver cadical195        # UNSAT
python search_sat.py 6 5 --solver glucose4          # UNSAT
python search_sat.py 6 5 --weights 2,6              # UNSAT
python search_sat.py 6 6                            # UNSAT (about 21 minutes)
python search_sat.py 6 8                            # SAT, prints a word
```

Expected `verify.py` output:
`PASS_CONNECTOR_SIX_SOURCE_SMALL_CHAR words=2 new=0 pair_checks=154 controls=4 sha256=9ab60914ac0d881d`.

## Consequences and limits

- In characteristics five and six, PR4248-style block concatenation cannot
  use a depth-two block on more than five sources. It does not decide N(5)
  or N(6): blocks
  of depth three or more, and floor words not built from blocks, are not
  covered.
- The bound concerns the generic schedule of the inherited interface
  (arbitrary dirty connector and outputs, arbitrary noncommuting maps).
- No supplier, consumer, selected record or κ changes.

## Open next questions

1. **c = 7.** *Why:* it closes PR6061's question 1 and fixes the smallest
   characteristic with a six-source depth-two block (7 or 8). *First step:*
   cube-and-conquer on the first five or more letters with the same encoding;
   c = 5 took 2.5 to 4 minutes and c = 6 took 21 minutes on one core, while
   c = 7 had no verdict after about 25 minutes. *Blocked by:* solver time.
2. **A checkable certificate for c = 5.** *Why:* the exclusion currently rests
   on solver output. *First step:* emit DRAT for the weights {2,6}
   sub-instance (the smallest UNSAT core found) and check it with drat-trim or
   cake_lpr; or look for a human proof using only weight-two masks plus the
   all-ones mask. *Blocked by:* no checker in this environment.
3. **Depth three in characteristic five.** *Why:* with depth-two blocks capped
   at five sources, an improvement of the c = 5 floor needs a depth-three
   block on more than 7 sources (density above 5/2), PR6035's question 2.
   *First step:* the same encoding with triple sums.

## Credit

Prepared by JosieElliston with substantial Anthropic Claude (Claude Code,
session 50) assistance. The interface, depth notion, concatenation and the
c = 4 obstruction are Nick Petalas's (PR4231, PR4248, PR4271, PR6035), with the
retained Ross Richardson PR934/943 lineage. zxv's PR6057 and JosieElliston's
PR6061 supply the c ≥ 8 six-source blocks and the open question; PR6107 supplies the weight
identity used for pruning; apoursh's PR6071 supplies the Gray-walk family.
Apache-2.0; no predecessor file changes.
