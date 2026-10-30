# Composition with the independent helper splits

[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), exact
head `0644592d421b375c221045954fdf13932575ffa8`, reports conditional kappa
.00309839 on a different word with 750 public inputs and 542 helpers.
Its source is PR5580. This package instead consumes both stages of PR5565
and changes three contacts plus helper 307. No combined gain is claimed.

The published fifteen-split witness was read at that exact head. None of
registers 85, 307, 319 or 507 occurs in its a, b, c or d basis-operation
supports. This is a useful compatibility screen, not a proof of composition.
The supports do include registers 648, 649, 650, 652 and 198, which occur
in PR5565 Stage A. Some split witnesses use frame 597, whose contacts that
stage removes. Do not apply the complete cascade without rechecking cuts.

A bounded next test is:

1. Start from the exact PR5599 word. Authenticate its source and retain
   its larger input inventory, owned-register indices and compiler stock.
2. Test PR5565 Stage B separately from Stage A. It supplies the source
   frame paths needed by this package. Check its commuting interval against
   every inserted basis operation and repeat all split-interface checks.
3. Match this package's three ADDs by their source operands and surrounding
   accesses. Add U = `[30,44,459]`, move the first two contacts to U, and
   move the last contact and helper 307 exit to frame 235.
4. Reconstruct every transport, then replay all original inputs and the
   transpose, every native map, physical caller, both complete moment
   engines, compiler and outer inequalities. Count every helper target and
   scalar/basis operation. Publish a combined kappa only after those pass.

Credit Ali Romman's PR5599 independent-helper construction, Pierre-Loic
Doulcet's PR5565 cascade, DreamingOfClouds's event-lattice method and all
retained P104 sources. This handoff reserves no further search.
