# Six code dimensions force 164 support incidences at eleven pieces

For arbitrary pieces spanning a six-dimensional subspace of the characteristic-zero
P112 root-evaluation code, the total support-incidence bill satisfies

    sum_i |supp(p_i)| >= 224 - 6n + (n-2)z,

where z is the number of coordinates vanishing on that same code subspace.
A pair-incidence strengthening gives

    sum_i |supp(p_i)| >= ceil(((2n-3)(112-z)-binomial(n,2)(12-z))/(n-2)).

In particular eleven pieces require at least 164+4z, hence164, incidences. This excludes the
literal historical (6,5) profiles 5^10,7 and5^9,6^2, whose inherited support
caps total156 and148. Their exact quotient is five-dimensional and their
code intersection is six-dimensional under the stated inherited second-weight
bound. The contradiction itself only requires six code dimensions.

[PROOF.md](PROOF.md) pairs generalized Hamming weights with rational root-matroid
contraction fibers and singleton incidence. Charging common zero roots raises
the naive152-incidence floor to 158, and pair incidence strengthens this
to 164. The first named caller is excluded with margin eight. The dominated profiles 5^11 and5^10,6 also follow. No complete
current residue count or first-exclusion claim is made.

The primary checks all 4,900 rank-two and 85,680 rank-three root-spanned flats
using rational elimination. The separate checker proves the needed cap of six
root lines through 23 integral rank-three Gram patterns and 2,875 target vectors.
All 393 positive definite rank-four Gram patterns, covering 245,625 integral
targets, independently certify the pair-fiber cap of twelve root lines.
It imports no primary geometry or elimination code. Both literal profiles
pass the unchanged original PR3154 necessary filter. A separate team agent
critiqued the scalar-extension/common-zero argument and supplied the Gram
certificate; this is assisted-team corroboration, not independent human or
proof-kernel acceptance.

## Reproduce

From the repository root, with Python3.12 and its standard library:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-six-dimensional-incidence
```

The registered commands are also directly runnable in the official Git-free
export. Normal replay is read-only; only `verify.py --write-expected` regenerates
the receipt. `SOURCES.json` authenticates every canonical-main input; the
historical filter is reused for binding and the capacities remain inherited
proof dependencies. The bounded root-capacity theorem itself needs neither a
Weyl-chamber theorem nor an embedding of the coefficient field into the reals.

## Open next questions

First independently audit the common-zero charging and the characteristic-zero
rank transfer. A further application should name an actual caller whose total
support cap reaches164 and identify additional multi-piece incidence structure.
The uniform bound's attainability and such a caller are not established here;
a larger census is not automatically warranted.

This local C5 progress does not construct a cheaper decoder or improve kappa.
Full C5, physical supplier admission, the full multiplication theorem and
human/formal acceptance remain open. The selected conditional kappa remains
0.001672660197076918.

## Credit

Nick Petalas/PR3269 and3300 supply the inherited12/20/36 capacities;
DreamingOfClouds/PR3154 supplies the historical reduction. Retain the
root-simplex lineage, David Arias's quadratic-model work and joaqcoo's decoder
context. Exact source pins and scope distinctions are in `PREDECESSORS.json`
and `SOURCES.json`. Chris R / Clear1nsight with substantial OpenAI Codex
assistance. Apache-2.0. Predecessor packages and selected artifacts are unchanged.
