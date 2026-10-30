# Every two-grid selector has the same translation obstruction

This contribution was produced by Nick Petalas. New work is Apache-2.0.
The elementary set-translation argument below is the new scoped extension of
woklerx's [PR #1845](https://github.com/CrocSwap/integer-mult-bounds/pull/1845).
Its leaf increments and admission conditions are cited premises.

## Model and theorem

Fix integers a,b and an integer h >= 2. A target value q in Z is measured in
fine-grid units. Fine precision admits every q. Coarse precision admits only
q in hZ. At fixed values of the source and all other visible state, the two
executions add a and b respectively. They leave the other visible state
identical. The selector may use any subset S of hZ, choosing coarse precisely
at q in S. No periodicity, regularity or computability is assumed.

Write delta = a-b. The visible output is

    F(q) = q+b+delta*1_S(q).

Then:

1. F is injective on Z if and only if S+delta is contained in S.
2. F is surjective onto Z if and only if S is contained in S+delta.
3. F is bijective if and only if S+delta=S.
4. A nonempty admission-respecting injective selector exists if and only
   if h divides delta. When divisibility holds, S=hZ attains bijectivity.

These statements concern the unbounded lattice, without clipping, saturation
or a quotient identifying different integer inputs.

## Proof

Each branch is a translation, hence injective within its own branch. A
cross-branch collision must have q in S and r outside S, with

    q+a = r+b, hence r=q+delta.

It exists exactly when some q in S has q+delta outside S. This proves 1 and
also supplies an explicit collision witness for every failed inclusion.

After subtracting b, the image is exactly

    (S+delta) union (Z minus S).

This covers Z exactly when S is contained in S+delta, proving 2. Combining
1 and 2 proves 3. In fact every output has at most two preimages, one per
branch; no assumption about finite or infinite S enters the argument.

For 4, suppose S is nonempty and F is injective. Choose q in S. Both q and
q+delta belong to S by 1 and therefore to hZ. Their difference delta is
divisible by h. Conversely, if h divides delta, take S=hZ. Translation by
delta preserves hZ, so 3 gives bijectivity. Since h>=2, both precision
branches occur in this attaining policy. This includes delta=0.

## Why injectivity and bijectivity must be separated

For h=2, a=2, b=0, let S be the nonnegative even integers. The output sends
each nonnegative even input two places forward and fixes every other input.
It is injective on Z and misses exactly 0. Thus replacing the inclusion in
1 by equality would falsely exclude a nonperiodic injective selector.
Reversing the ray, S the nonpositive even integers, creates the collision
F(0)=F(2)=2. Both examples satisfy coarse admission.

## Conditional application to the actual PR628 leaf

Use the fixed source-one, zero-imaginary-target slice specified in PR1845's
README at `b0a7acdd39a6943218d312ae93e8bbc65ab8c56c`. Its retained parameters
are outside factor 1/4, scale 1, phase [1], beta=1/2, direction +1 and no
scratch. Its stated premises are:

- Target inputs are q/32 for every integer q.
- Precision four is admitted only when q is even and adds -10/32.
- Precision five is admitted for every q and adds -11/32.
- Both executions restore the source and leave the imaginary coordinate zero.

These predecessor statements are assumed here, not replayed or independently
validated. In fine-grid units they give h=2, a=-10, b=-11 and delta=1.
The divisibility condition fails. Therefore an injective selector on this
whole slice must choose precision five at every q. If it chooses coarse at
even q, the adjacent input q+1 is ineligible for coarse and is forced fine:

    F_leaf(q/32) = (q-10)/32 = ((q+1)-11)/32 = F_leaf((q+1)/32).

This witness does not require knowing the selector elsewhere. It covers
arbitrary nonperiodic, source-conditioned policies after fixing this source
slice, provided they have only these two precisions and no additional visible
branch state. It strengthens PR1845's single coarsest-compatible-policy
counterexample to every selector making any coarse choice on this slice.

It does not require a policy to make a coarse choice on this slice. A policy
may use fine precision here and save elsewhere. Three or more precisions,
changed increments, additional retained state, a different source, restricted
reachable inputs or non-restored auxiliary outputs require separate analysis.
No multiplication theorem, physical implementation or kappa improvement follows.
