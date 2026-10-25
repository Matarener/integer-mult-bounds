# Independent review of the many-axis prime-supply port

Scope: mathematical and uniform-setup review only. No repository edits,
publication, selected-frontier claim, production-sized prime search or formal
proof-kernel review.

## Source binding

Canonical main: 20ecf2891d80b5acf18d980b2164fb44ea7faa90.
Tensor PR3935 head: 240597ed313fc2854c0462b23c89dc3bae72aaf5.
`research/physical-gaussian-tensor/tensor_plan.py` has
`dimensions=axes+1=D` and `d=dimensions+1=D+1`.
Its `production_axis` requires, for gap g=t-s,

    4*d*g > s, (2*d-1)*g < s.

Thus the required strict gap interval is
`t/(4*d+1) < g < t/(2*d)`.
Target lengths are `t=2^ell` or `2^(ell-1)` and the final axis has the first
length. The repeated 7x7 finite fixture is not a CRT prime-supply witness.

Primary analytic source independently consulted:
Fiori, Kadiri and Swidinsky, *Sharper bounds for the error term in the Prime
Number Theorem*, arXiv:2206.12557v2 (17 May 2023), Corollary 22:
https://arxiv.org/pdf/2206.12557v2 . Corollary22 gives exponent0.84768363; using0.8476 is a safe weakening.
The resulting pi-minus-Li error is
`9.2211*x*sqrt(log x)*exp(-0.8476*sqrt(log x))` for every x>=2.

## Interior interval and prime count

For each target t use

    a=t*(1-1/(3*d)), b=t*(1-1/(4*d)), interval (a,b].

Every selected prime satisfies the strict source ratios. This alone does not
supply the independent source period guard. Write H for the actual
`target_halo` field and K=H+2w. Add the explicit condition
`K<=2^(ell-3)` (the sufficient executable bit-length check
`K.bit_length()<=ell-3` avoids forming that power). Then for both targets,
`s>a>=5*2^(ell-1)/6>2^(ell-2)>=2K`, which discharges the third
`production_axis` predicate. Polynomial H,w eventually meet this condition
under the retained growth laws; a p cutoff needs their fixed constants.
None of `production_common` is inferred from this prime lemma. The length is
`t/(12*d)`. Write `y=log(t)`.
For the stated large domain, endpoint logs lie in [y/2,y], hence the sum of
the two FKS endpoint errors is at most
`20*t*sqrt(y)*exp(-sqrt(y)/2)`.
The Li increment is at least `(b-a)/y=t/(12*d*y)`.
It follows that the interval contains at least D primes whenever

    480*d*y^(3/2)*exp(-sqrt(y)/2) <= 1,
    t >= 24*d*D*y.

Neither an integrality nor an open-endpoint term is missing: pi(b)-pi(a)
counts exactly the integers in (a,b], including b if prime.

## Uniform sufficient threshold

Suppose ell>=2^32, 2<=d<=ell^334, D=d-1, and
`t in {2^(ell-1),2^ell}`. Then ell/4 <= y <= ell.
The function `y^(3/2)*exp(-sqrt(y)/2)` decreases for y>36. Therefore the
first left side is at most `480*z^671*exp(-z/4)`, z=sqrt(ell)>=65536.
At z=65536 its logarithm is less than

    7+671*16-16384 = -5641.

Here log480<7 follows already from e>5/2 and (5/2)^7>480; log2<1.
The logarithmic derivative `671/z-1/4` is negative throughout this range.

For the second condition, dD<=ell^668 and y<=ell. It suffices that
`ell/4 >= log24+669*log(ell)`.
At ell=2^32 the right side is below `5+669*32=21413`, while the left side
is 2^30; the difference increases because `1/4-669/ell>0`.
Thus both sufficient conditions hold uniformly.

## Distinctness, ordering and product budget

All these primes exceed 2, so they are odd. The intervals at t=r/2 and t=r
are disjoint. Enumerating ascending distinct primes in each therefore gives
pairwise-coprime lengths across both groups. Two monotone source tables plus
one scan of the target flags suffice to assign primes in original axis order;
the final axis is assigned from the r table.

For every selected length s/t>1-1/(3d). Bernoulli's inequality gives

    S/T > (1-1/(3d))^D >= 1-D/(3d) > 2/3,

so `T/S<3/2<2`. No floating logarithmic estimate is needed here.

## New-regime distinction and predecessor credit

The source08 selector and CinnaDavis's `prime-source-selector-transfer` already
provide an all-size selection argument on the domain `log(t)>8d`. Chafik's
PR1786 already uses the same general strategy of explicit PNT error bounds for
fine intervals. Trial division itself is inherited. This review claims none of
those general ideas as new.

The changed source binding matters: at ell=2^32 and d=ell^333, the new
`d<=ell^334` criterion holds, while `log(t)<=ell<8d` contradicts the old lemma's
premise. The independent checker represents this enormous dimension only by
an integer power/bit-length certificate; it creates no prime-sized target or
axis-length list. Under the retained D=Theta(p^.997), ell=Theta(p^.003) family,
`D+1<=ell^334` holds eventually, whereas log(t)/d tends to zero.

## Conservative uniform setup bill and limits

Trial division is inherited from source08, not a new algorithm. A deliberately
loose fixed-tape implementation can examine all candidate integers below r in
the two intervals and trial-divide by every divisor below the candidate.
There are O(r^2) divisions, each performed by binary scans in O(ell^2) steps.
Encoded candidate/divisor counters and rational endpoint preparation have
polynomial overhead; repeated buffers are cleared after each division.
At most D ascending primes from each of the two bands suffice.
Two sequential tables of at most D primes need O(D*ell) output/backing cells.
The flags-to-axis assignment uses monotone cursors, not numerical random access.

For the explicit large domain, log2(d)<=334*log2(ell)=O(ell), so endpoint
arithmetic and candidate/divisor/count buffers all have O(ell) bits. Ordinary
binary long division uses O(ell^2) reads/writes/unit moves on fixed many tapes.
The two tables and final output require O(D*ell) cells and linear total scans.
Consequently setup is O(r^2*ell^2+D*ell) steps and O(D*ell+ell) visited cells,
including cleared scratch backing. Each candidate and divisor is an encoded
counter, not a host control integer. Ascending enumeration supplies distinct
primes without retaining rejected candidates or a growing recursion stack.

The head contract is: borrowed encoded inputs and flag stream return unchanged
at LEFT+1, the declared source/flag outputs return at LEFT+1, and temporary
working bodies are erased with their heads at LEFT+1. Rewinding and erasing
O(ell) arithmetic buffers after each test is absorbed into O(ell^2); the final
sequential table clearing/rewind costs O(D*ell). No dirtied register is treated
as free. This is a written fixed-tape implementation argument; the small host
reference is not an executed literal encoded implementation.

In particular the setup bound is `r^2*poly(ell,D)` steps and
`poly(ell,D)` visited cells. Under the retained caller laws ell=Theta(p^.003),
D=Theta(p^.997), and V>=2^(c*p) for fixed c>0, this setup is `2^o(p)=o(V)`.
An explicit p cutoff requires the fixed constants in those Theta statements;
the (ell,d) threshold above is already explicit and directly checkable.

Remaining obligations: full caller/source08 integration, all non-prime Gaussian
and routing premises, native supplier execution, production tensor precision,
CRT/integer recovery, physical reserve and any selected-frontier admission.
This review establishes no new kappa and no independent human/formal acceptance.
