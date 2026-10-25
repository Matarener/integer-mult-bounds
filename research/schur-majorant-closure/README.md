# Same-rho principal Schur closure

For every finite complex matrix `A=I+H`, if an entrywise nonnegative majorant of H has both row and column sums at most rho<1, every principal Schur descendant of every principal restriction retains the **same rho** defect budget. The majorant can bound complex modulus or the submultiplicative component envelope mu(z)=|Re z|+|Im z|. PROOF.md gives the arbitrary-size argument; finite checks are corroboration.

This independently audits one conditioning premise of Jose Manuel Barranco's completed recursive PR4205 at203d04313c0cb2b4a4663a5a2d4d407e5a5b6d20. Its actual component admission is rho=1/2. Under that admission, descendant direct norms are at most3/2 and inverses at most2; source K and ZK are at most1 and completed local shears/inverses at most2. Source parity equality uses commuting truncated lower-Toeplitz algebra. No generic noncommuting reorder is asserted. Ordinary modulus admission alone does not imply the component admission; an exact counterexample is included.

## Evidence

- Primary:64 exact Gaussian-rational matrices,1440 restriction/Schur cases and656 nested quotient identities;12 Toeplitz roots,78 recursive nodes and33 local shear checks.
- Independently frozen cofactor oracle:2441 matrices,13501 E/K/D partitions,1244 nested histories; no primary imports or Gaussian elimination.
- Source arithmetic probe: unchanged original toep/lower/invseries/conv/triangle_plan functions with only floating diagnostic replaced by a collector. Exact array facade and algebra-only callbacks return empty plans.10 dyadic roots produce74 nodes,32 Schur/commutation checks,104 Cramer entries and64 completed local shear checks. A wrong-sign mutation still passes norm checks but fails the exact Schur identity.
- Separate algorithm comparison and proof review are distinct from human or formal-kernel acceptance. Run every VERIFY.json command from the repository root with Python3.12; no dependencies. Registered commands write no receipts unless explicitly passed --output.

## Scope and remaining obligations

The source probe does not run FFTs, stored gates, rounding or the full Triangle.plan factory. This package does not recalculate global prefix/grid/rounding/online-offline allowances, implement the author's active compensated generator, certify physical coefficient delivery, discharge native/outer transfer or claim a multiplication theorem/new kappa. The selected frontier is unchanged. Integrating local constants into a pinned global allocator is separate work.

## Open next questions

Can these local constants improve the completed recursive caller's global prefix/grid/rounding allowance? Pin the finished generator and its actual contract, then audit that implication separately. The present result supplies the local invariant; it leaves global allocation and physical delivery open. The author's active compensated-generator implementation is separately claimed and is not duplicated here.

## Sources and credit

Jose Manuel (`jmbarrancoml`) supplies the retained rational parity-triangular execution and precision proof. Vlado Vojdanovski/PR1673 supplies the parity factorization, recursion, descendant argument and circuit. Chafik Boukhalfa/PR628 supplies the certified phase lineage, and Cinna Davis supplies the later caller context. Classical Schur-complement, Neumann-series and nonnegative-majorant ideas underlie this lemma; no broad mathematical-priority claim is made. Douglas Colkitt/OpenAI and research/unconditional-batched-crt/NOTICE.md retain their predecessor credit. Four minimal PR4205 exports are unchanged and pinned in an own-branch ancestor, with original authorship recorded in SOURCE-PINS.json. Substantial OpenAI Codex assistance includes coordinating integration, primary proof/checker, a separately frozen determinant oracle and a separate review context. These are not independent human reviewers.
