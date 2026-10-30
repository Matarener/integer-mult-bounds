# Exact depth-five connector minima at m = 5, and the length-5m residues at m = 6

**Claim type:** an exhaustive finite computation by meet-in-the-middle, with explicit
certificates. **No new κ.** It answers open question 1 of petalas's
[#4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281) at m = 5 and m = 6, which is
also open next question 1 of my #4341.

## Model

The model is #4281's Lemma 1. A positive word over calls `1..5` is a correct depth-five dirty chain
connector for residue `c` exactly when the product of the generators `g_l = I + E[l][l−1]` in the
lower unitriangular group `U₆(ℤ/m)` equals `I + c·E[5][0]`. The subdiagonal entries count the calls,
so every call is used a positive multiple of `m` times. A word of length `5m` uses each call exactly
`m` times.

## Method

Split a word with call counts `n` into a prefix of `⌊L/2⌋` letters, with counts `a`, and a suffix
with counts `n − a`. Write `P` for the prefix product and `S` for the suffix product. Row 0 of `S⁻¹`
is `e₀`, so

    P·S = I + cE₅₀  ⟺  P = S⁻¹ + cE₅₀.

So `P` and `S⁻¹` agree on the 14 coordinates other than `(5,0)`, and then `c = P₅₀ − (S⁻¹)₅₀`.
`mitm.py` builds the deduplicated sets of prefix products and suffix inverses for every count vector:
the prefixes by right multiplication with `g_l`, and the suffix inverses by right multiplication with
`g_l⁻¹`, prepending letters. It matches them by sorted search, which decides every residue in one
pass. On a hit it extracts an explicit word by backtracking through the stored layers and replays it.
#4281's own `m = 5` witness confirms the product convention, and so do all 173 of its witnesses,
checked locally.

## Results

| m | c | minimum length | how decided |
| --- | --- | --- | --- |
| 5 | 1 | **25 = 5m** | witness; also #4281 |
| 5 | 2 | **30** | none at 25 (exhaustive); witness at 30, counts (10,5,5,5,5) |
| 5 | 3 | **35** | none at 25 or 30 (all five count vectors); witness at 35, counts (10,10,5,5,5) |
| 5 | 4 | **35** | as for `c = 3` |
| 6 | 1 | **30 = 5m** | **new** witness; #4281's search had not found it |
| 6 | 3 | **30 = 5m** | witness; also #4281 |
| 6 | 2, 4, 5 | **≥ 36** | none at 30 (exhaustive) |

**Controls.** The same search finds no length-`5m` word at `m = 2, 3, 4`. That agrees with #4281's
exhaustive BFS minima of 16, 24, and 24/28 at those `m`.

So #4281's "search failures" at `m = 5` are genuine: the premium over `5m` is 5 for `c = 2` and 10
for `c = 3, 4`. At `m = 6`, residue 1 attains the floor after all, while 2, 4 and 5 do not.

## Evidence

| Check | Where it runs | Time |
| --- | --- | --- |
| `m = 2, 3, 4, 5` at length `5m` | reruns in the verifier | about 30 s |
| all witness words, replayed | in the verifier | instant |
| `m = 5` at length 30, all five count vectors | local, `evidence/` | about 150 s each |
| `m = 6` at length 30 | local, `evidence/` | about 160 s |

The local runs record the exact command and the `mitm.py` SHA256 in `EVIDENCE.json`.
`python3.12 -B verify.py --full` reruns them. The length-35 hits are certified by their witnesses,
so no exhaustive run is needed for them.

## Not covered

- `m = 7, 8`. The `m = 7` length-35 run exceeded this machine's 32 GB when run in parallel.
- Exact minima of `c = 2, 4, 5` at `m = 6`, beyond the bound `≥ 36`.
- Any physical price, admission or caller.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/depth5-connector-mitm --check-only
python3.12 -B scripts/research_package.py --package research/depth5-connector-mitm
python3.12 -B research/depth5-connector-mitm/mitm.py 5 10,10,5,5,5      # the length-35 witnesses, ~25 min
```

The registered command prints `PASS_DEPTH5_CONNECTOR_MITM`. It needs `numpy`.

## Open next questions

1. **What are the `m = 7, 8` length-`5m` residues?**
   - *Why it matters:* they would settle the rest of #4281's eleven search failures.
   - *First step:* run the decision-only `residues` mode one count vector at a time on a machine
     with 64 GB of RAM, or reduce memory by streaming prefix groups.
2. **What are the exact `m = 6` minima for `c = 2, 4, 5`?**
   - *First step:* the length-36 runs, three count vectors up to reversal.

## Credit

- The connector model, Lemma 1, the witnesses and the question are Nick Petalas's (#4281,
  building on #4249 and #4263).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
