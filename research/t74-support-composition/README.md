# Physical T74 on arbitrary selected coordinates

I replace PR3599's reference-permutation composition with a complete physical
call: encoded forward exposure, the actual-width T74 root, inverse exposure
and record restoration. I use [PR3619's router](https://github.com/CrocSwap/integer-mult-bounds/pull/3619)
and [PR3599's root](https://github.com/CrocSwap/integer-mult-bounds/pull/3599)
in one authenticated runtime cohort, with two fresh native instances.

I receive a complete n-bit address rectangle of p-grid Gaussian coefficients
and an encoded list of g sorted distinct selected coordinates. I physically
prepare actual long records and retain them through the root call. I return
normalized H0 on the original selected coordinates, preserve borrowed input
and descriptors, and restore owned-work baselines. I keep the original p-grid
format and return the componentwise truncation toward zero of the ideal
selected transform. I retain error below `sqrt(2)*2^-p`; I return the ideal
result exactly whenever it already lies on the p-grid.

Under the retained source contracts and fixed positive c,C0,B with
`c*p<=n<=C0*p`, `g<=min(n,floor(p^.997))` and `log2(r+1)<=B*p`, I prove

    O(V*(g^alpha*log p + (g+1)^tau*(log p)^(1+tau))) time,
    O(V)+F_q space,
    alpha=.99827101, tau=332353/332929.

Here `V=2(p+2)*C*2^n*r`, r is the original coefficient count per address and
C is an arbitrary positive outer-row count. I retain the input unit-disk,
source-admissible fixed q and universal native/hosting/refinement premises.
I give the complete invoice and explicit fallback cutoff in
[PROOF.md](PROOF.md). I keep both time terms; the extra logarithm does not
disappear uniformly in arbitrary g.

## The composition boundary

I authenticate both official source exports and compare 21 Compact package
files, 15 external Compact inputs and 23 ordinary backend files. I open the
T74 runtime once, retain its Count/Tape classes and register compatible router
context views. I compile two fresh retuned natives before reading input.

I extend the prescribed selected-to-target map to a permutation on their
union, with at most 2g listed coordinates. I move an untouched complete
`ell=ceil(log2 p)^2` block to the actual suffix. I conjugate the permutation,
sort both forward and inverse descriptors, and group that suffix into
`r_eff=2^ell*r` complete Gaussian coefficients. I retain r_eff throughout
the actual root invocation. I then invert the exposure, ungroup and undo
the physical suffix swap.

If the target span or untouched block is unavailable, I use an exact-grid
literal route. I lift once to precision p+g, execute single-bit roots whose
intermediate values remain exact on that grid, and round once at the final
p-grid return. I charge their short-record work on the explicitly bounded
failure domain. Repeated truncation at the original p can produce a different
answer; I include a physical mutant that exposes this error.

## Evidence and replay

```sh
python3.12 scripts/research_package.py --package research/t74-support-composition
```

I use Python 3.12 and the standard library. [VERIFY.json](VERIFY.json) declares
seven bounded commands. I check 98 encoded support extensions, persistent-field
geometry and inverse ordering against finite oracles. I exercise complete
Gaussian packets through both the direct and recursive root paths, multiple
outer rows, output reuse and the lifted fallback. I compare the final output
with a rational Walsh-transform oracle on the original selected coordinates.

The recursive fixture carries 512 Gaussian coefficients and makes five
balanced child calls. I retain actual grouped coefficients at both physical
routers and the root. I check nonzero Walsh outputs across distinct spectator
labels. I also reject malformed supports, omitted inverse sorting, premature
physical truncation, protected-output overwrite, fresh physical allocation,
altered source archives and a second cold runtime.

I use q=2 and declared reduced root guards/reservations in the physical
fixtures. I reduce the external suffix to one bit where declared. These
packets use the router's literal branch; PR3619 separately checks its sparse
branch. I retain the production formulas and prove their composition, but
I do not execute production GL64/O(73,2) packets in these bounded fixtures.
[EVIDENCE.md](EVIDENCE.md) records exact coverage and limitations.

## Open next questions

1. Bind this complete arbitrary-support call to a full-address transform.
   Start from its actual selected-width schedule and include the number of
   calls, tail groups, precision conversions and accumulated error. The local
   bound alone does not determine an integer multiplication exponent.
2. Bind the enclosing integer multiplication assembly and both supplier
   obligations. Start from the selected source's actual producer/consumer,
   full coarse rectangle and online precision. Raw-H scaling, packing and
   scientific review of the inherited universal premises remain open.

I coordinate in [Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).
[TASK.json](TASK.json) records the revision-6 task, overlap and family-expansion
decision. I leave the selected frontier unchanged.

## Attribution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source analysis, verification and prose.
I claim no independent human or formal-kernel review. Apache-2.0.

I retain RaD/hipotures's PR20 routing lineage as recorded by Zhihao Chen in
PR23; Vlado Vojdanovski's PR1673 support-sensitive router and compiler argument;
Douglas Colkitt's compact construction; my PR3055/3562/3477/3599/3608/3619
physical and rate components; and the native, borrowing and scalar contributors
and notices inside their frozen exports. I use the retained Gaussian grid
boundary and Tekalign's normalization component through those source APIs.
I retain Hiroki Kumazaki's PR3576 factory credit and Nick Petalas's PR3581
B1-only exposure boundary. I add the executing consumer composition and its
complete record, ownership and fallback proof.

I also credit Chris / Clear1nsight's [PR3623](https://github.com/CrocSwap/integer-mult-bounds/pull/3623),
head `328c40966b650f60b1d62cfb0b1d67b2b755eb62`, for the adjacent old-d versus
actual-g spacing audit. I compute K from the actual g and restore the incoming
coordinate frame. I do not claim that the older outer caller accepts this
root unchanged; its diagonal, format and full-round lifecycle remain separate.
