# Mixed ranks one through seven cannot repay the active-mode centers

Any number of immutable, fixed-chart channels of Gaussian ranks 1 through 7
needs at least **65 units of rank mass** to repair all eight retained modes.
This includes arbitrary rational payloads, repeated chronological scatter and
joint cancellation of output noise. It grants free helper restoration.
For every power tariff H_r=r^q H_1 with 0<q<=1, the channel price exceeds
the removed **8H8** allowance by a factor of at least **65/64**.

This closes the full lower-rank part of the mixed-rank question left by
[PR5755](https://github.com/CrocSwap/integer-mult-bounds/pull/5755) and
[PR5745](https://github.com/CrocSwap/integer-mult-bounds/pull/5745).
Rank-eight/rank-nine mixtures and changed native or feedback contracts
remain open. No new kappa or selected-frontier change is claimed.

[PROOF.md](PROOF.md) gives the response-space quotient and the rank cuts.
[CERTIFICATES.json](CERTIFICATES.json) contains exact rational duals.
[RESULT.json](RESULT.json) records the complete check. The source census
covers 22,585 events, 1,002 charts and 8,298 temporal responses. Stronger
bounds are 90 units for maximum rank five and 77 for maximum rank six.

A cost-62 integral rank-four support cover misses five target directions.
[COVER-LIMIT.json](COVER-LIMIT.json) retains this failure witness. Support
coverage alone does not establish delivery. The exact support relaxations
and their matching primal/dual witnesses are retained for comparison.

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/active-mixed-rank-obstruction
```

Direct exported replay is `python3.12 -B research/active-mixed-rank-obstruction/verify.py`.
The scientific verifier uses no solver, Git, network or predecessor executable.
To regenerate only the new receipt, add `--write-receipt`. The verifier checks
source bytes, all exact quotient ranks and capacities, the predecessor's
rank-one census, seven semantic controls and a joint-noise positive control.
See [VALIDATION.md](VALIDATION.md) for execution evidence and limits.

## Open next questions

- Resolve a mixed rank-eight/rank-nine completion with at least nine useful
  channels. Use the retained temporal spaces; retain the matrix-rank condition
  and full Y restoration. A coordinate cover is not sufficient.
- Change the immutable-payload or fixed-chart premise. Bind each new native
  transport and feedback read to the physical word and its complete bill.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
The canonical temporal contract and eight-H8 attainment come from PR5745.
Flyingviper's PR5755 supplies the restored-Y invariant, rank-one obstruction
and separate forward census; PR5720 supplies the active-mode proposal.
Retain Cao Yifan, Cinna Davis, Dugongue and every native, mode, controller and
source author in the unchanged archive. [ORIGINS.json](ORIGINS.json) and
[SOURCES.json](SOURCES.json) bind the exact records. This contribution adds
quotient-rank certificates for arbitrary lower-rank mixtures. It does not
claim the preceding mechanisms or independent human acceptance.
