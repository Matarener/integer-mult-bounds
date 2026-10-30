# The frozen [PR #5687](https://github.com/CrocSwap/integer-mult-bounds/pull/5687) G5 invoice has negative raw moment for every positive exponent saving

This is a paper qualification of one explicitly supplied invoice. It assumes the complete paid and productive lists stated in [PR #5687](https://github.com/CrocSwap/integer-mult-bounds/pull/5687), Theorem G5, at head `b3b0fc751d3f5ecdd1498a99a4bfcfa97a0a5b97`. It does not independently establish the physical construction or dispute its relative improvement. The method is elementary rank separation after cancellation; repository precedent includes [PR #5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673) section 4 for a different invoice. No new general inequality is claimed.

## Exact input and conventions

The primary text is `research/restricted-gaussian-coframe-improvement/caller.md`, section 7. The authenticated local copy has SHA256 `f5fe6f217a55a684132114522e15c0f3424c10248fb5d0d4b48ccea0a8c08650` and Git blob `2d6cbce0f076a325cf498989eb2ed2268f16d5f3`. Its immutable public source is [the frozen caller](https://github.com/Dugongue/integer-mult-bounds/blob/b3b0fc751d3f5ecdd1498a99a4bfcfa97a0a5b97/research/restricted-gaussian-coframe-improvement/caller.md).

For a real parameter C define H_r(C)=r^(1-C), for positive integer r. Use the source's complete two-call lists:

$$
P(C)=3732H_1+1046H_2+836H_3+278H_4+24H_6,
$$

$$
T(C)=52H_3+4H_4+24H_7+736H_8+224H_{15}.
$$

The target-minus-paid raw Gaussian moment is M(C)=T(C)-P(C). All original 224 main inputs and the two distinct 408-helper banks have the source's declared independent ownership. No target is added for scratch, no banks are identified, and no helper is credited a second time. These ownership statements bind the invoice being qualified; they are not an independent replay of the physical endpoint.

## Scoped inequality

Cancel exactly the common 52H3 and 4H4 terms. Then

$$
M(C)=24H_7+736H_8+224H_{15}
      -3732H_1-1046H_2-784H_3-274H_4-24H_6.
$$

Each complete original invoice has rank mass 9,588. Canceling the common terms removes 172 from each side. The remaining productive rank mass is

$$
24\cdot7+736\cdot8+224\cdot15=168+5888+3360=9416.
$$

The remaining paid rank mass is

$$
3732+1046\cdot2+784\cdot3+274\cdot4+24\cdot6
=3732+2092+2352+1096+144=9416.
$$

For every C>0, the function r^(-C) is strictly decreasing in r. Write each H_r as r times r^(-C). Every remaining productive rank is at least 7, and every remaining paid rank is at most 6. Consequently

$$
M(C)\le9416\left(7^{-C}-6^{-C}\right)<0
\qquad(C>0).
$$

At C=0, M(0)=0. This proof uses no approximated logarithm, numerical power evaluation, monotonicity of a difference of signed moments, or inference from one tested point. Its declared domain includes every positive C, in particular .0033.

## Meaning for the next gate

The frozen G5 invoice cannot supply a positive raw moment. If a proposed admission route requires a strictly positive target-minus-paid raw moment for these same lists, it fails this necessary condition before nonnegative additional recursive charges or a positive reserve. Positive finite ordinary costs remain separate obligations; they do not turn a negative recursive moment into a positive one.

This does not prove failure of an unspecified compiler architecture or outer theorem with a different premise. Any claimed alternative route must name and justify its actual admission inequality. Nor does this rule out a different consumer, target census, helper profile, source invoice or resource contract.

The source's predecessor-relative gain greater than 148C on its stated interval can coexist with M(C)<0: the predecessor can have a still lower absolute moment. The relative gain and operator construction remain source-author contributions. The present result only settles the previously unproved absolute sign for the displayed frozen lists.

Let an actual changed construction supply productive increment DeltaT(C), paid increment DeltaP(C), and a reserve R(C) expressed in the same units only when a compiler theorem justifies doing so. A necessary raw funding condition is

$$
\Delta T(C)-\Delta P(C)>-M(C)+R(C).
$$

The displayed upper bound on M implies the weaker necessary threshold

$$
\Delta T(C)-\Delta P(C)>
9416\left(6^{-C}-7^{-C}\right)+R(C).
$$

Neither inequality grants an implementable repair budget or a new target. Actual physical changes must preserve arbitrary inputs, native phases and charts, observations, ownership and restoration, and carry their complete new invoice plus ordinary, precision, stock, tape, compiler and outer obligations.

## Scope and credit

The result applies only to [PR #5687](https://github.com/CrocSwap/integer-mult-bounds/pull/5687)'s stated G5 lists at the frozen head. [PR #5698](https://github.com/CrocSwap/integer-mult-bounds/pull/5698)'s separate actual-C coframe optimum, [PR #5678](https://github.com/CrocSwap/integer-mult-bounds/pull/5678)'s P104/535-helper stream, historical rank17/rank16 templates, and every other consumer have different contracts. Their inventories are not combined here. The source's two-call endpoint contains rank15 jobs; it is not replaced with a rank16 grant.

Credit Dugongue and the retained source authors for the uniform provider, two-call endpoint, complete lists and relative improvement; [PR #5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673) for the repository's earlier use of the elementary rank-separation technique on another invoice; and Cao Yifan, Cinna Davis and the native/helper/code/controller/compiler lineage retained in the source. Prepared with substantial OpenAI Codex assistance. Static mathematical review is separate from independent physical validation, hosted CI and formal proof-kernel acceptance. No construction, numerical experiment, paid saving or new kappa is claimed.
