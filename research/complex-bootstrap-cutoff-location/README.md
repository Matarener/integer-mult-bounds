# The selected complex supplier's bootstrap cutoffs are the recorded branch sequences

**Source-bound location; no new κ.** This note answers the second open question
of [stock-margin-chain](../stock-margin-chain/README.md) ("Find the analogous
cutoff sequence for the complex `m=73` supplier"), whose first step was to
"locate the selected complex assembler's own per-stage cutoffs."

**Located: there is no third, `m=73`-shaped cutoff sequence in the retained
construction. The two recorded branch sequences already are the complex
branches' own per-stage cutoffs.** The frozen PR1087 assembler computes its
bootstrap inside one function, `outer_witness` (`code/assemble.py` line 205),
called exactly twice — with the conservative complex lower (line 221) and the
native complex lower (line 226). `cuts.append` appears exactly once in the
retained archive's Python sources. The m=73 supplier is priced inside those
same witnesses (native moment `check_moment('complex',H,73,owner['live'],b,5120,False)`
at line 225; conservative at line 198), and the emitted dict records the
sequences as `bootstrap=cuts` and `conservative_bootstrap=conservative_cuts`.

```sh
python3 -B research/complex-bootstrap-cutoff-location/verify.py
```

Expected:

```text
PASS_COMPLEX_BRANCH_CUTOFF_LOCATION binding=complex bootstrap.stage1_headroom_log2=6562783 branches=2 conservative_bootstrap.stage1_headroom_log2=6562783 controls_rejected=6 sigma_obligation=uncomputed stages=14
```

About 0.1 s, standard library only, CPython 3.12. Source is inspected from the
pinned tarball member, never executed.

## What is established, exactly

1. **The chain's saving is the complex supplier's discounted lower.** The
   assembler computes `s = min(c, (1-beta)*bb) - 10^-27` with `beta = 10^-24`
   (line 206). In the selected receipt the complex side binds the minimum:
   `(1-beta)*complex_lower < bit_lower` holds exactly in rational arithmetic,
   so `s = (1-beta)*complex_lower - 10^-27` for both branches. The recorded
   cutoffs are therefore driven by the complex supplier's saving; the bit
   lower enters the chain only through a non-binding minimum and through the
   assembler's `512` constant (the bit side's charged two-level coefficient
   bits) inside the cutoff formula.
2. **The formula reproduces the receipt byte for byte.** Recomputing the chain
   from the assembler's own recurrence reproduces all fourteen recorded
   `(exponent, gap, cutoff_log2)` triples of
   `research/community-frontier1094-audit/ASSEMBLY.json` exactly, and the
   assembler's inline guard `cut*gap**2 >= 36 and cut*gap >= 2*(4+512)` at
   every stage.
3. **The cutoff chain produces the selected kappa.** The assembler's rounding
   formula `q = a_7*(1-2*eta)`, `margin = (1-eta)*q/(1+q)`,
   `kappa = floor(margin*10^18)/10^18` with `eta = beta = 10^-24` reproduces
   the receipt's recorded `kappa = 836330098538459/500000000000000000` and
   `conservative_kappa = 104541262139063/62500000000000000` exactly, each from
   its own branch's chain. (At the 10^-18 rounding grain the last-stage
   increment is below one unit, so stage 6 gives the same integer; the branches
   are still distinct — control 5.)
4. **The membership margins transfer verbatim.** The twelve published
   integers of [stock-margin-chain](../stock-margin-chain/README.md)
   (`floor(s*L_j - L_{j-1})` and the routing rooms `floor((1-s)*L_{j-1})`)
   are reproduced here from the receipt's own recorded cutoffs and the frozen
   formula — an input path independent of that package's
   `RESULT.json`-based reconstruction. Both branches' margins are positive,
   and all fourteen recomputed stage headrooms match the audited
   `stock_headroom_log2` values.

## Corrected boundary for the stock card

`stock-margin-chain`'s open question 2 was blocked by "the missing recorded
cutoffs (the audit states the selected coefficient is uncomputed)". This note
resolves the premise: **the cutoffs are not missing as a separate object.**
The recorded fourteen-stage receipt is the complex branches' own bootstrap
sequence, so the card's remaining obligation narrows to exactly what the
[selected stock audit](../selected-bootstrap-stock-audit/README.md) already
names (its own open question 1): bind the stopped construction's stock
coefficient — the `(H3)` sentence `log_q S(e,w) <= sigma*w*(1+log2 e)` with
`log2(8*sigma_j) <= H_j` at every stage, `H_1 = 6,562,783` on both branches
and the headroom growing to `~10^25` bits by stage 7. Every recorded
`actual_stock_coefficient` stays null, and this package does not import the
historical `57,604` or `252` allowances.

## Controls (all must be rejected; each failure is a distinct condition)

1. A bit-driven chain (the assembler's `min` replaced by the bit lower alone)
   does not reproduce any recorded stage triple.
2. Substituting the other branch's complex lower does not reproduce either
   branch.
3. A recorded cutoff incremented by one is rejected by the byte comparison.
4. The stale-cutoff substitution (`L_{j-1}` in place of `L_j` in the margin's
   first factor) is non-positive at stage 7.
5. Cross-branch kappas: each chain reproduces exactly its own recorded kappa
   and not the other's.
6. The stage-1 headroom is the audited `6,562,783` and satisfies the largest-
   admitted-log identity `2*(H+4) <= L*delta < 2*(H+5)`.

Plus the receipt's own record: all fourteen `actual_stock_coefficient` fields
are null.

## Reproduce

From the repository root:

```sh
python3 -B research/complex-bootstrap-cutoff-location/verify.py
python3 scripts/research_package.py --package research/complex-bootstrap-cutoff-location --check-only
python3.12 scripts/research_package.py --package research/complex-bootstrap-cutoff-location
python3.12 -B scripts/check_research_commit.py --package research/complex-bootstrap-cutoff-location --check-source-history
```

Inputs are pinned by SHA-256 in [SOURCES.json](SOURCES.json); the check fails
on any drift, any stored coefficient, or any source-fact mismatch.

## Scope and limits

- No supplier, tariff, kappa, certificate, frozen input or selected-frontier
  change. `scripts/research_baseline.py` is untouched.
- The kappa reproduction recomputes the assembler's own rounding formula from
  the receipt's recorded exact lower bounds; it does not re-run the physical
  replay or re-prove the 47 strict outer constraints (the frontier audit
  binds those; the source facts here assert only the chain-level sentences).
- The `(H3)`/sigma obligation is stated, not discharged: the retained sources
  state the old-leaf reserve only as "logarithmic", exactly as the stock
  audit records.
- The `outer.py`/`moment.py` engines the assembler loads from its replay
  output directory are not vendored or executed here; the chain-level facts
  asserted are those of `code/assemble.py` itself.

## Open next questions

1. **Bind sigma for the selected stopped construction** (the stock audit's
   open question 1, unchanged): collect the selected producer's per-level row
   stock, depth factor and old-leaf reserve coefficient from the PR185/PR387
   complete-row contract. The exact per-stage allowance is
   `sigma_j <= 2^(H_j - 3)`, with `H_j` recomputed here from the receipt.
   `first_step`: read the selected invoice's stock shape
   (`physical_stock_identity` in ASSEMBLY.json) against the complete-row
   contract. `blocked_by`: the reserve coefficient is only "logarithmic" in
   the retained sources.
2. **Bind `W_j` to source** (stock-margin-chain's open question 1, unchanged):
   the routing-room sentence is still absent from the receipt.
3. **Does any other retained archive contain an `m=73`-shaped cutoff
   sequence?** The frozen PR1087 archive has none; a different lineage would
   need its own source binding.

## Credit and limits

The cutoff recurrence, the fourteen recorded cutoffs and the kappa rounding
are the frozen PR1087 assembler (Jeremy Kothe's package and its credited
lineage) and Rohan Arun's PR1094 selected receipt. The receipt audit and the
stock headrooms are the selected stock audit (ToikY, on Josie Elliston's
PR1956/PR1965 work); the twelve membership margins and routing rooms are
Kumagi's stock-margin-chain, with the native stage-2 envelope from
philippeVV's handoff and the stage-3 pair from Riquelme Soares's PR #2931.
The selected BIT supplier is DreamingOfClouds's PR589 on eumemic's base. This
note only locates the complex branches' cutoff sequences in that retained
source and transfers the published membership statement to them.

No independent human review, supplier replay, selected cold replay or formal
kernel result is claimed. New work is Apache-2.0; retained predecessors keep
their attribution. Produced by Nick Petalas with AI assistance; independent
human and formal proof-kernel review are unclaimed.
