# Independent exact score of the two-role T16 swap

This bundle independently checks the arithmetic of worker 1's frozen `two-role-swap-001` map. It is supporting evidence for one construction PR, not a separate baseline or decimal-refinement contribution.

The accepted rational is `836809769328269/500000000000000000`, or `0.001673619538656538`. Its exact gain is `523880761/500000000000000000` over PR3308 and `47967078981/50000000000000000` over selected PR1094. The native complex endpoint is `419106309171938950571/250000000000000000000000`. The unchanged bit endpoint is `1733427039589844234749/1000000000000000000000000` and retains its bad-residue surcharge. The complex side binds.

This is an arithmetic check. Physical placement, the full invoice and inherited theorem premises are separate gates. The raw input hashes in `RESULT.json` identify the exact OWNERS, PLAN, SPEC, ASSEMBLY and PREFIX-AND-INVOICE used by those gates. There is no fresh native-circuit reconstruction here. The bootstrap cutoff rows reproduce fixed-allowance arithmetic samples, not actual carried-constant algorithm thresholds. No unconditional multiplication theorem or selected-frontier change is claimed.

## Reproduction

Python 3.12 or later, standard library only. No Git objects, repository imports or network access are required. Set `bundle` to this directory and `work` to a fresh external output directory:

```sh
mkdir "$work"
python3.12 -B "$bundle/score.py" \
  --assembly "$bundle/inputs/ASSEMBLY.json" \
  --data "$bundle/inputs/data" \
  --invoice "$bundle/inputs/PREFIX-AND-INVOICE.json" \
  --owners-audit "$bundle/inputs/OWNERS-AND-PROFILE.json" \
  --bit-source "$bundle/inputs/PR589-EXPECTED.json" \
  --output "$work/RESULT.json"
cmp "$work/RESULT.json" "$bundle/RESULT.json"
TMPDIR="$work" python3.12 -W error -B "$bundle/test_score.py"
TMPDIR="$work" python3 -O -W error -B "$bundle/test_score.py"
```

The scorer writes only to a fresh requested output, after all checks succeed. Tests remove their own temporary directory. The manifest inventories every committed proof-relevant byte in this bundle. The original selected and candidate inputs are copied without modification.

## What is checked

- Native and conservative complex root brackets and the unchanged bit root bracket. Each lower endpoint is accepted and the next `10^-24` endpoint is rejected, with the applicable surcharge.
- Independent integer-root enclosures at 160 exponent bits with 256 fractional bits, and contained enclosures at 192/320 bits.
- Both halving guards, complete complex rank mass and source-bound bit data.
- The native and conservative seven-step bootstrap recurrences and all 47 raw outer slacks. Every rational agrees exactly with the emitted construction assembly.
- Next-headline, zero-eta, zero-beta, unit-beta and margin-equality rejection controls. Omitting the bit surcharge changes the upper-endpoint decision, as expected.
- Source hash chains from OWNERS through PLAN/SPEC, owner audit, full invoice and assembly. These bindings do not replace the placement proof.
- Eleven test groups, including 372 direct rational power comparisons, invalid inputs, a rank-48 count mutation, a false slack, changed surcharge/invocation metadata, a mismatched invoice and preservation of an existing output under optimized Python.

## Enclosure proof

For a rational `x >= 1`, start with integer bounds for `x*2^P`. Repeatedly take a floor square root on the lower bound and a ceiling square root on the upper bound. Induction gives bounds for each `x^(2^-j)` on the same fixed-point grid. The binary digits of `floor(a*2^B)/2^B` select a finite product of these roots. Round every multiplication outward. Since `x^a` increases with `a`, the lower dyadic exponent gives a lower bound and the upper dyadic exponent gives an upper bound. All comparisons and products use integers and exact rational arithmetic.

For each child, multiply this enclosure for `(m/r)^a` by `n_r*r/(m*W)`. Add every term. When required, add the full retained surcharge `32*m*sum(n_r)/(10^16*W) * m^a`. The scorer imports neither retained moment engine nor the producer or outer-assembly function. The second precision is a consistency check of the same independent method, not a claim of a second independent implementation.

## Outer-parameter stopping decision

The retained compact-layer constraint requires `kappa < epsilon*q`. The geometric constraint gives `epsilon*(1+c) < 1`, and the reservation constraint gives `c > q`. Thus `kappa < q/(1+q)`. With `q < a` and both supplier caps, the same family cannot exceed `min(cap_bit, cap_complex)/(1+min(cap_bit, cap_complex))`. Using the independently rejected next primitive endpoints still places that ceiling less than one existing `10^-18` headline-grid unit above the current candidate. Fifteen bounded eta/beta/bootstrap variants respect this inequality. There is no meaningful parameter-only opportunity left in this family at the existing headline precision. This is not an obstruction for a changed outer contract or a changed paid profile.

## Source and credit

Canonical base `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. PR3308 predecessor head `8bc0555b484bf4aec4b91c680763d930d6754974`. The new map and its strict replay are separate artifacts. Credit for the predecessor packing stays with Gonzalo Mier, Rohan Arun, Jeremy Kothe, Hao Yan and the retained supplier lineage. The bit supplier is PR589 with its PR555 predecessors. The 47-constraint balanced assembly retains eumemic, icekylinx, Zhihao Chen and RaD/hipotures credit. Nick Petalas supplies this independent arithmetic implementation. Apache-2.0. No independent human review is claimed.

## Engineering bounds

Every root/product loop has at most 256 iterations. Profiles have at most 64 ranks, bootstrap depth at most 16, and the parameter probe has 15 cases. Input files must be regular files no larger than 16 MiB. Python's managed allocation is a documented Power of Ten rule 3 deviation, bounded by these finite inputs and loop sizes. Directly controlling Python allocator timing would require a different runtime and would not improve this exact checker. There is no recursion or dynamic code loading. Functions remain below 60 lines. Runtime `require` checks remain enabled with optimized Python. Diagnostics use `-W error` and normal/optimized behavioral tests.

## Open next questions

The candidate owner should combine these exact arithmetic checks with the identical frozen map's physical admission and full-invoice review, then replay the public exact head in hosted CI. A later packing improvement must supply a new source-bound assembly rather than reuse this report with changed hashes. A genuinely different outer contract needs its own cost argument; recovering finer decimal slack is not a new mechanism.
