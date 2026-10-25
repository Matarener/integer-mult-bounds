# Gap-parametric precision for the #5413 caller: κ = 0.0030272882489783 (numerical headroom only)

**Scope.** This package gains numerical headroom only, from the compiler gap and precision carrier. The recursive economic
gain is **zero**. The complete #5413 caller is unchanged: the same word, invoice, paid and target profiles, reserve
10⁻¹², compiler tuple, BIT stock and 25-premise conjunction. No paid job, target or compiler parameter other than the
strict gap and its recomputed height carrier changes, and the raw moment is identical.

| | κ (conditional) | tested | gap | j | H |
|---|---:|---:|---:|---:|---:|
| #5413 (Clear1nsight) | .003027288235 | .003027288245 | 1/7·10¹¹ | 55099 | 38569300000000000 |
| #5462 (ours, same carrier) | .0030272882389 | .0030272882489 | 1/7·10¹¹ | 55099 | 38569300000000000 |
| **this package** | **.0030272882489783** | **.0030272882489784** | **1/7·10¹⁶** | **72096** | **5046720000000000000000** |

The gain is **1.00783 × 10⁻¹¹** over #5462 and **1.39783 × 10⁻¹¹** over #5413. κ stays below the fixed-profile
ceiling U = .00302728825 (#5409) and below the raw root, which lies in (.0030272882499, .00302728825).

## Why the gap was pinned, and why it need not be

#5413's numerical funding engine (`fund_uniform_endpoint.py`) already accepts any **unit** gap g = (tested − κ)/7.
It derives the least height grid j with (H+1)¹⁰⁰⁰ < 2ʲ, where H = j·den(g). The gap was pinned only as literals:

1. Precision checker `check_v16_precision_v3.py`, one line:
   `need(gap==(tested-kappa)/7==Q(1,700000000000), 'actual strict compiler gap')`.
   The carrier obligations next to it, `H==j*gap.denominator and (H+1)**1000<2**j`, are already parametric.
2. Conjunction `check_neutral_closure.py`:
   - the endpoint gate (κ, tested, gap and gain literals);
   - the height gate (H and j literals);
   - the hash of the accepted written proof.
3. Written proof `V16-APPLICATION-PROOF-v3.md`. The argument is symbolic in N = 2^H and M = F16(N). The carrier
   appears only as recorded values at four sites:
   - §5, the H line;
   - §5, the gap line;
   - §6, a **non-claim** ("D0 < N^gap would fail: log₂D0 = 1048576 while H·gap = j, H·r0 = j/10");
   - §8, the funded (K, C) pair.

   §6/§7 explicitly avoid any absorption at the fixed carrier ("no C0bar<N^gap is required"). The stop, layout and d
   parameters (all equal to the gap) enter only as positive rationals in outer domain-entry thresholds. A finer gap
   moves those thresholds; it does not invalidate them. The §6 non-claim stays true because j = 72096 < 1048576.

The outer 54 strict and 4 functional predicates have minimum margins proportional to the gap (minimum strict margin
gap/10), so they stay positive for every positive gap. **The only binding constraint is `funded_alpha_reserve`.**
#5413's directed moment engine puts the reserve-limited tested saving in (.003027288248978444, .003027288248978445).
Every κ < tested below that bound is therefore fundable with its own least carrier. There is no finest admissible gap.
This package certifies the 16-digit point, and its sweep funds the gaps 1/(7·10^m) for m = 12…18. At m = 18 that gives
κ = .003027288248978443, with arithmetic only.

## What `gap_endpoint.py` does (about 5 s)

1. Authenticates all 63 capsule files of `research/coupled-helper-neutral-completion` against its `SOURCE-BINDINGS.json`,
   whose SHA256 its `verify.py` pins. Copies them into private scratch.
2. Reruns #5413's invoice/funding engine with only its two endpoint literals substituted:
   - the regenerated invoice is byte-identical to #5413's;
   - paid, targets, reserve, tuple, invoice hash, BIT stock, predicates and controls are unchanged;
   - j and H are recomputed independently: the least grid point, with the preceding grid point failing.
3. Generalises the precision checker. The single pinned line becomes "positive **unit** gap"; nothing else changes.
   - **Conservativity:** on #5413's own manifest, the generalised checker reproduces #5413's expected precision receipt.
   - At the new carrier, its receipt differs from #5413's only in `carrier_H`, `carrier_j`, `carrier_gap`,
     `expanded.N`, `expanded.M` and `proof_sha256` (plus timing and hashes).
   - The written proof is instantiated by exactly four unique literal substitutions, and the script asserts that no
     old carrier or endpoint literal remains. The result is stored here as `V16-APPLICATION-PROOF-v3-R15.md`.
     `diff` against #5413's file shows four changed lines.
4. Reruns #5413's conjunction with only the endpoint/carrier literals moved (κ, tested, gap, gain, H, j and the
   accepted-proof hash): PASS, 25/25, the same premise names.
5. Controls (all must reject):
   - #5413's **pinned-gap precision checker** rejects the new funding (`actual strict compiler gap`);
   - #5413's unsubstituted conjunction rejects it (`exact_new_positive_endpoint_gap`);
   - the generalised checker rejects the old H/j with the new gap (`actual funded carrier rank`);
   - the generalised checker rejects a non-unit gap 3/7·10¹⁶;
   - tested .00302728825 and .0030272882489785 fail `funded_alpha_reserve`;
   - a non-unit gap fails the engine's unit height grid.

   The script also checks the raw-root and reserve brackets, and the sweep.

## Assumptions and non-claims

κ is conditional on exactly the five retained selected premises of #5413:

- native all-column operation;
- owned erasure;
- the compiler contract;
- precision/tape;
- analytic recovery.

The instantiated proof is #5413's reviewed proof with its carrier literals replaced. No new mathematical argument is
added, and it has not been reviewed independently in its own right. No unconditional theorem, formal-kernel
acceptance or κ-maximality is claimed. On macOS the script skips the precision checker's `RLIMIT_AS` call, which Darwin
cannot lower; Linux runs the checker text unchanged apart from the one gap line.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gap-parametric-precision-r15
python3.12 -I -B research/gap-parametric-precision-r15/gap_endpoint.py   # PASS_5413_CALLER_GAP_PARAMETRIC_PRECISION_AT_KAPPA_0.0030272882489783
diff research/coupled-helper-neutral-completion/capsule/workspace/swarm-coupled-caller-sol-high-20261024/agents/precision/V16-APPLICATION-PROOF-v3.md \
     research/gap-parametric-precision-r15/V16-APPLICATION-PROOF-v3-R15.md
```

`logs/` holds `.txt` transcripts of these runs, made on macOS:

- `gap_endpoint.txt`: PASS.
- `check_only.txt`: PASS_PACKAGE_METADATA_AND_PINS.
- `research_package_replay.txt`: the full registered replay. Our command passes. In the dependency command, #5413's own
  `verify.py`, runs 0–5 pass and run 6 (its precision checker) stops at `resource.setrlimit(RLIMIT_AS)`, which Darwin
  cannot lower. That command is meant for Linux CI. Docker was unavailable locally.

## Open next questions

- **Does a changed profile clear U?** Can a changed paid or target profile on the #4610 word fund κ above the
  fixed-profile ceiling U = .00302728825?
  - At the #5413 profile, the endpoint headroom left by the alpha reserve is now below 1.5 × 10⁻¹⁶, and the raw root is
    below U. Any further gain must be economic.
  - First step: price one candidate histogram change with `scripts/compare_recursive_invoices.py`.
- **Can the reserve itself move?** The rounding minimum is about 9.1 × 10⁻¹³, and #5413 fixes the reserve at 10⁻¹².
  Lowering the reserve would change the compiler tuple, which this package keeps fixed. 1 − α falls about one-for-one
  with the tested saving here, so the reserve change would add at most about 9 × 10⁻¹⁴.

## Credit

- Chris R (Clear1nsight) supplied:
  - the #5413 complete caller;
  - its funding engine, precision checker, written proof and conjunction;
  - #5400, #5407 and #5414.
- Ali Romman (aliromman) supplied the owned-relation chain #5377, #5383, #5392 and #5398.
- Dillon Amburgey (dillona) supplied the #5402 coupled provider.
- zxv supplied the physical/compiler/semantic precision and higher-moment machinery that the proof specialises.
- Further contributors:
  - Dugongue: reserve refinements;
  - Cao Yifan (intqwq): the #4610 word;
  - Cinna Davis: controller and helpers;
  - Jacob Alan Sussman: integer flow.
- #5409 supplied the ceiling U. Our #5462 is the pinned-gap predecessor of this package.

Prepared by Joel Pulikkan (GamingPuzzled). AI disclosure: Claude Opus 5.5 (Anthropic) via Claude Code, directed by
Joel Pulikkan (GamingPuzzled). New material is Apache-2.0.
