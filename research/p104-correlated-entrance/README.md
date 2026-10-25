# Correlated P104 producer entrance

The first P104 collector has a larger correlated ideal entrance than the
independent product contract needed to keep every prefix in the Newton lattice.
For arbitrary initial values of its 58 dependencies in `B9`, its six ideal
collector inputs are in `B9` exactly when five disjoint source-group sums
belong to `4B9`. The 52 Y banks therefore have 47 unrestricted `B9` bank
coordinates and five `4B9` coordinates after an explicit integral invertible
change of bank coordinates. [The proof](PROOF.md) states the inherited
covariance and lattice-automorphism dependencies.

There is a reachable literal separation as well. Set `Y27[0]=64` and
`Y26[0]=-64`, with every other initial component zero. Both Y banks are in
`B9` and outside `4B9`. Every event through 2024 executes exactly, D31 leaves
`B9` at event 1090, and all six collector inputs are literally zero at cut
2025. Removing Y26 reproduces the nonadmitted D31 control. Multiplying the
Y27-only input by four restores its stronger admission. The proof also derives
exact cancellation for Gaussian integer multiples of the paired fixture.

This gives the ideal classification and one literal strict example for the
final-cut cancellation gap in Clear1nsight's
[PR3423](https://github.com/CrocSwap/integer-mult-bounds/pull/3423), pinned at
`15d28c4de37dc47ea07cd7173c8b318fca7a4d75`. Its 52 stronger Y conditions still
characterize its prefix invariant. The independent product-domain result in
[PR3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406) has a different
quantifier and is retained. The ideal criterion does not classify arbitrary
literal rounded executions. It does not supply an actual correlated caller,
change the consumer, overcome the unchanged-profile cost stop, admit a supplier
or improve kappa. The selected frontier is unchanged.

## Evidence and replay

The separate standard-library checker imports no predecessor executable.
It derives all 257 producer events, 58 dependencies, six final coefficient
rows and five disjoint Y groups from the frozen word. It verifies both products
of the explicit 52-by-52 integral coordinate matrices. RECEIPT.json retains the
complete group/event lists and source-bound rows.

The literal implementation executes all 2,025 events, 883 native occurrences,
1,038 ADDs and 104 signs in each of three fixtures. It compares every active
literal signed-floor pair with a separately expressed ideal Gaussian formula.
The cancellation has 26 active native occurrences and 7,680 pair comparisons.
The broken-cancellation and stronger controls each have 20 and 6,144.
Zero-input transports are justified by their literal zero preservation.
All fractional ADDs are checked for componentwise exact division.

Five behavioral groups reject changed quarters, lost sources, wrong frames,
wrong dirty-source signs, changed/missing source bytes, nonintegral pairs,
Newton-lattice mutants and Boolean receipt drift. All 2,401 pairs of Gaussian
inputs with each component in `[-3,3]` are checked. The 1,201 integral cases
satisfy the sum and rotated-difference identities; 1,200 nonintegral ideal
cases reject. Complete receipt equality is checked by canonical JSON bytes,
including types. These are finite checks plus the written algebraic proof,
not independent human or formal proof-kernel review.

From the repository root with Python 3.12 or later:

```sh
python3.12 -I -Werror -B research/p104-correlated-entrance/verify.py
python3.12 -I -O -Werror -B research/p104-correlated-entrance/verify.py
python3.12 -I -O -Werror -B research/p104-correlated-entrance/test_verify.py
python3.12 -I -Werror -B scripts/research_package.py --package research/p104-correlated-entrance
```

The direct commands also run in a source export containing this package and
its two declared frozen inputs. They need no Git, network or third-party
module. `--emit` prints a computed receipt without writing files. The ordinary
command compares with committed RECEIPT.json. Test scratch uses Python's
configured temporary directory and is removed on exit.

SOURCES.json pins canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6, both exact
PR2586 source blobs, PR3423's producer and comparison notes, PR3382's proof,
and PR3416's native covariance proof. The source-derived statement inherits
the last two mathematical dependencies explicitly. It does not rerun their
entire suites or the selected cold replay. The catalogue's baseline command
was attempted but its selected-source closure is omitted by sparse checkout;
that orientation check is not claimed to pass.

## Open next questions

- Classify correlated inputs that guarantee exact literal arithmetic at every
  producer stage and final-cut admission. Start with the ideal congruence
  module and intersect its stagewise Gaussian-integrality constraints. This
  could distinguish legal correlated preparation from cancellation that works
  only in ideal rational arithmetic. Arbitrary rounded paths are still open.
- Bind one useful correlated family to an actual upstream caller and follow its
  downstream recipient histories. First specify the preparation, ownership,
  restoration and complete cost allowance. PR3423's unchanged-profile stop
  blocks a claimed supplier win without an explicit changed premise.

## Engineering bounds

Build the Lever produced the source-bound replay and complete receipt.
Prove It Works required the actual full prefix and broken-cancellation control.
Power of Ten keeps every new function below 60 lines, checks source bytes before
parsing, limits input reads and binds all loops to fixed source dimensions.
The retained mathematical dependencies are provenance only and are never loaded
as executable modules.

Managed Python requires dynamic integers, lists and parsing, a deviation from
Power of Ten rule 3. The scope is one bounded verification run: 358 banks of
512 components, at most 2,025 events and rank nine. Inputs have amplitude at
most 256. The conservative per-component bit bound is 9,000, from at most
883*9 pair stages and 1,038 additive doublings. The interpreter's own allocation
is not instrumented. Sources are pinned and capacity-limited; no unbounded
service, optimizer, child process or growing cache is used. A future
parameterized implementation must enforce corresponding dimension/height bounds.

The test loader is a rule-8/9 deviation for fixed-path local Python dispatch.
Its single target is this package's verify.py. It imports no predecessor code,
accepts no dynamic module name, and all rejection tests remain active under
`-O`. Replace it with ordinary package imports if this isolated-script layout
is later converted to a Python package. Scoped Ruff diagnostics accompany replay;
repository-wide diagnostic configuration is outside this new research package.

## Credit

Nick Petalas. Apache-2.0. Credit ywz65/PR2586 for the literal word and recipes,
Arham Tahir/PR2665 for the retained rounded-collector inputs,
Clear1nsight/PR3382 and PR3423 for the Newton exactness domain and actual
producer/consumer contract, Tekalign/PR3025 for the signed-floor bijection,
Ross Richardson/PR3068 for the exactness-domain question, PR3406 and PR3416,
and the retained native, geometry, compiler and precision lineage.
Independent human and formal proof-kernel review are unclaimed.
