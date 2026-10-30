# Typed actual-width H and one rounded return

**Partial result, no new κ.** One typed round of the normalized transform
`H0 = [[1, 1], [1, -1]] / 2` on the matched actual-width bits, followed by one
toward-zero return `Q_p` and an MSB-first component bridge. The selected
frontier is unchanged.

This takes the first open question of the handoff in
[discussion 1166, comment 19016699](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19016699),
left by [PR #3623](https://github.com/CrocSwap/integer-mult-bounds/pull/3623).
The multi-round tape allowance in that handoff is still unspecified, so this
package does not start that construction.

## Result

For `p >= 1` and `g` selected bits, an exact `H0` tensor sends a `p`-grid unit
disk to integer numerators in units of `2^{-(p+g)}`. Those numerators fit in
signed width `p + g + 2` and do not fit in width `p + g + 1`. One truncation
toward zero returns the `p`-grid disk in width `p + 2`, with Euclidean error
strictly below `sqrt(2) 2^{-p}`. The truncation commutes with signed
permutations; floor division does not. The bit bridge preserves values and is
exactly the conversion from the LSB-first root word to an MSB-first scan.

On the matched layout, common-round root bits are the physical slots of that
height. The degree-2 witness (`d = 4`, so `K_d = 2` and `K_g = 1`) puts a
numerator `(8, 0)` at address 0 and `p = 3`:

| Selected bits | Address 2 after `Q_p` |
|---|---|
| matched `{0, 1, 2}` | `(1, 0)` |
| old stride `{0, 2, 4}` | `(0, 0)` |

The 32-address witness invoice is 192 real add/sub operations, 64
truncations, and 960 bit reads plus 960 bit writes. Those bit counts include
the input load, the MSB-first bridge, and the read of the returned tape.
Temporary width is 8 and final width is 5. The `g = 1`, `p = 3` disk is exhaustive (197 points, 38,809
pairs). Production floors at `k = 2, 3` are exact integers, including the
six-multiple offsets `+2` and `+5` at `k = 2`. The extent ratio between the two
chunk widths has base-2 logarithm `k^{500} - 1`; that cube is not allocated.

The argument, the finite domain, and the claims that are not made are in
[PROOF.md](PROOF.md).

## Evidence

Canonical main for this package is `bb4bccbf42844d2801487450727c2f63e10d1d0f`,
priority revision 6. The predecessor proof was written against
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The two frozen sources have the same
git blobs at PR #3623 heads `328c40966b650f60b1d62cfb0b1d67b2b755eb62` and
`c5ab698bba8b35323e40ae3b132e78f26179d393`.

```sh
python3.12 -I -B research/typed-actual-width-h/verify.py
python3.12 -B scripts/research_package.py --package research/typed-actual-width-h
```

Both the normal command and the same command under `-O` print
`PASS_TYPED_ACTUAL_WIDTH_H` and the same receipt. The local run below used
CPython 3.12.3 and finished in about two seconds. It does not import the frozen
modules.

## Credit

The `(1, 40)` outer guard is Nick Petalas's PR #3493, as vendored by
Clear1nsight in PR #3623. The selected-width `K` law and the normalized `H0`
endpoint are Jose Manuel's PR #3599 (`jmbarrancoml`), retaining Hiroki
Kumazaki's factory work. The matched layout, the address-2 witness, and the
decision to stop when the multi-round allowance is unspecified are
Clear1nsight's PR #3623, incorporating Sagar Thakrar's PR #3617 diagonal as an
unexecuted predecessor. The transform lineage retained there includes Douglas
Colkitt, Philipp, and the authors named in that proof.

New work is the typed width, the single toward-zero return, the MSB/LSB bit
invoice, and the independent checker. unpaidmoon, with substantial AI
assistance. No independent human review or formal-kernel proof is claimed.
Apache-2.0. The frozen files keep their original notices.

## Open next questions

1. **Can one fixed cube and packet inventory carry every round?** The
   sufficient bound `Q <= C M R (r w + A + p^3) + poly(p)` still does not name
   descriptor updates, previous-output reset, borrowed restoration, or the
   constant number of cube buffers. First step: write those operations for one
   common round and one prefix round on the 64-address three-short cube, with
   an explicit simultaneous tape count. Blocked by: that contract is not in
   PR #3623 or in this package, and the handoff says to stop while it is
   unspecified.
2. **Does this one-round invoice plug into PR #3617 without a second producer
   charge?** PR #3617 already pays a fixed-h diagonal. First step: add this
   bridge's `6 N (p + 2)` bit scans once per record and show which of its 38
   roles, if any, already move those bits. Blocked by: PR #3617 is unmerged,
   and its full-array pass was not replayed here.
3. **Is the `k = 2` extent gap visible to any executable outer instance?** The
   ratio is `2^{2^{500} - 1}` and the source band forces
   `ell >= 45,812,984,491`. First step: none that allocates the cube. A
   symbolic tape-count identity would still not be a physical execution.
