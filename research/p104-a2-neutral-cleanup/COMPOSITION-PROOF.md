# A common functional word for the A2 exchange and three helper cleanups

This scoped composition combines [zxv](https://github.com/zxv)'s [PR #5643](https://github.com/CrocSwap/integer-mult-bounds/pull/5643), exact head `a3ff5c628bfc8825553d62d913f3e91f75d6825f`, with [Ali Romman](https://github.com/aliromman)'s [PR #5644](https://github.com/CrocSwap/integer-mult-bounds/pull/5644), exact head `c5871955d89bf73506fd68b0a5bf1cf2b3153c02`. Both consume the exact [PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627) word at `ed4dc88a09a7d201971f6603b8c2074e95dd9c32`. This is a compatibility argument for the emitted program, not an addition of headline κ gains. All source mechanisms and notices retain their attribution. New composition and this scoped audit used substantial OpenAI Codex assistance; Apache-2.0.

## The two substitutions are functional before they are priced

For the A2 substitution, write A = register 715, B = register 388 and C = register 340 at its prefix. The old scalar pair `B -= 4 A; C += B` and new scalar triple `C -= 4 A; C += B; B -= 4 A` both produce `(A, B−4A, C+B−4A)` for arbitrary prefix values. This is a matrix identity on the three full input columns; it does not assume a zero register or a special incoming relation. The new gates retain their specified charts 396, 825 and 127.

For a cleanup helper h, the exact checked prefix relation has the form

```
h(cut) − Σ_j b_j z_j(cut) = s u_h + Σ_{j ≠ h} a_j u_j.
```

Here s is an invertible dyadic unit, all initial inputs on the right share h's input chart, and every cancellation register on the left shares h's cut chart. Prepare `u_h' = u_h − Σ(a_j/s)u_j`. Execute the prefix on those prepared inputs, then replace the helper state by `(h(cut) − Σ b_j z_j(cut))/s`. The relation gives exactly `u_h` for every arbitrary input. There is no later read of h, and the removed suffix consists only of its own declared scalar cleanup gates. The original helper's scalar endpoint row is its independent input, while all other scalar endpoint rows have zero dependence on that helper input. Its physical endpoint retains the productive native map Φ_final Φ_initial⁻¹. Thus the preparation and replacement preserve every other endpoint and restore h's exact endpoint. This is the original cleanup proof applied to the actual composed prefix; the verifier reevaluates each relation after the preceding edits.

The three helpers are 291, 321 and 369. All input preparations, dyadic scalings, cancellation gates and resulting transports are present in the emitted common word. They do not use free helper output credits or a new owned-erasure rule.

## Actual composition, in both orders

Applying the three retained cleanup witnesses directly to the emitted PR5643 word passes the complete rational scalar/frame replay after every cleanup. The witnesses' exact anchors, prefix relations, absence of later helper reads, fixed productive endpoint charts and retained owned-event sequence are checked on the evolving word. This supplies an actual common program.

The separate audit reads the saved source, A2, cleanup and common words as data. After deleting MOVE instructions, it finds the unique old A2 scalar pair in the cleanup-only word. Replacing that pair by the specified triple gives exactly the common word's entire scalar skeleton. It independently rebuilds every typed monotone transport path from the cleanup-only initial charts and that skeleton. The resulting full chronological instruction list is exactly the common word, including every MOVE. Thus applying A2 after cleanup gives the same emitted program as applying cleanup after A2; compatibility does not follow merely from disjoint headline histograms.

`audit_composition.py` also checks the three-column A2 identity, all boundary data and the complete paid histograms. A missing final A2 shear fails the functional matrix identity despite retaining all helper cleanup identities. The complete verifier separately rejects a wrong A2 frame, omitted direct A2 correction, false cleanup cancellation, wrong cleanup cut, omitted initial preparation, missing owned CLEAR, extra target credit and an unpaid query.

## From scalar equality to physical action

Let Φ_f be the actual native chart operator at chart f, including its global phase. The frame invariant represents each physical register by `Φ_f z`, where z is its common-coordinate value. A coframed scalar gate obeys `Φ_f z_r + q Φ_f z_s = Φ_f(z_r + qz_s)`. A paid native chart change a→b is `Φ_b Φ_a⁻¹`, so it sends `Φ_a z` to `Φ_b z`. Induction through every chronological instruction transfers the proved scalar endpoint equality to physical endpoint equality. This argument neither commutes Gaussians nor replaces a tensor power of a sum by a sum of tensor powers. All owned instructions and their inherited contracts are retained in order.

The fresh native-map and full caller replays remain necessary evidence for the actual emitted chart transitions; the scalar audit alone does not claim to supply those checks. The inherited all-width realization, compiler, precision/tape, analytic recovery and helper-endpoint assumptions are unchanged.

## Complete bill and limits

Relative to PR5644, the common word's complete local paid change is exactly `H2 + H6 − H3 − H5`. Relative to PR5643, it is exactly `3(H6 − H1 − H5)`. Every productive target is retained. The full caller multiplies each local delta by 18. It has 66,492 paid calls, 12,958 productive fields and rank-mass surplus 760. The local ordinary allowance is 220,220, including the cleanup's extra 54 scalar units above the A2 word.

Both signed moment changes are strictly favorable for `0 < t < 1`: strict concavity gives `3^t−2^t > 6^t−5^t`, and subadditivity gives `1+5^t > 6^t`. The resulting root is recomputed from the common complete invoice. Scientific admission, hosted CI, proof-kernel verification and independent human review remain separate obligations. No global optimality claim follows.
