# Source-to-profile proof and verification boundary

## 1. Frozen scope

The proposal is PR5657 at `2f091bc3b656ed85d26cf44b7fc84c28fb510273`. Its positions refer to the literal forward G20 record array at `5e0052ca0aa3036a3afa8b0438927377c8d97d53`. The consumed complete local baseline is PR5653 at `b13c9ae8a539c05f0f590ce9d08c7067d99c6145`. No source engine is imported.

The baseline already contains the four partial retirements and three direct SOURCE fusions, including helper 444. The new edits are six protected-reader fusions and eight paid SOURCE refinements. All fourteen helper fields and all fourteen recipients are distinct. An affected SOURCE can also be another recipient's independent SOURCE. The complete join check includes these interactions; it does not infer compatibility from disjoint helper names alone.

## 2. Source conditions and exact edits

The verifier parses all six rows of the table in `bit.md` and all eight rows of the first table in `bit-refinement.md`. It also parses all eight independent recipient-injection rows. It compares every named event with the exact forward record, including field IDs, frame IDs, direction and rank.

For each simple window, the helper interval contains exactly its entrance query, line injection, proper outgoing read and upper query. The recipient interval contains exactly the cold read, its line query and the proper read. For each refined window, the helper also has its intermediate query. Its recipient has exactly its cold read, two own queries, one independent SOURCE injection and the proper read. Every reference, including outgoing observations, is included in these checks.

Between the helper's line injection and the relevant upper SOURCE query, the SOURCE has no value change other than the explicitly permitted first query in a simple window. Its old outgoing observers remain in place. Thus the inverse snapshot captures the required old SOURCE version. These checks are stronger than a rank or frame-name comparison.

Each edit locates one unique exact inverse event in the consumed word. Overlapping edits to one old event are rejected. Six simple windows snapshot the upper SOURCE, fuse the helper return, cancel its two recipient reads and, when required, delay the recipient's old return until the SOURCE is back at the line. Eight refined windows replace the old SOURCE rank-three return with rank-two and rank-one returns, snapshot both upper and intermediate values, replace the proper read by the intermediate snapshot, and fuse the helper's three returns into one rank-four return. Their own recipient injections remain unchanged.

Twenty-two new owned fields supply these snapshots. Each is cleared before use and after its last use. They add to the seventeen fields in PR5653, for 39. The new word has 684 fields, 645 of which retain independent arbitrary input data. Initial values on every owned field are also arbitrary in the check.

## 3. Complete linear join

Normalize each field by its declared frame map. A same-frame ADD becomes binary row addition. A legal nested query changes the frame but leaves the normalized row unchanged. CLEAR removes the row. Every row starts as a separate one-bit basis vector, including the dirty owned fields.

The new replay checks the actual frame on each query and both operands of each ADD. It checks that only owned fields are erased and only entire zero fields are freely reheadered. The final frame vector must equal the baseline vector, extended by unused headers for the new fields. Every owned row must be zero. The first 662 output rows must equal the baseline's full rows; all new rows must be zero. This proves the complete normalized input map, not a test on one chosen payload.

A second oracle reads the word in reverse order and transposes each ADD by exchanging its operand roles. Erasures transpose to erasures; frame changes do not affect normalized coefficients. Its final matrix must be the exact role transpose of the forward result. This provides a separate data-flow check, not independent scientific acceptance.

The frozen baseline's physical/native theorem is retained. The next section proves the exact new nested map identities required to transfer the changed normalized word back to its physical address action. A full new controller stream, finite-width implementation and tape proof remain outside this replay.

## 4. Exact residual geometry and the frame-506 correction

For a frame with row basis B and orthogonal complement A, the verifier constructs the rational orthogonal projector

`P_B = B^T (B B^T)^(-1) B`.

It checks the declared dimensions, orthogonality, idempotence and trace. For every new query from one nested frame to another, it checks both products `P_low P_high = P_low` and `P_high P_low = P_low`. Their difference D is an idempotent of the declared query rank.

In paired address coordinates, the physical involution for D is

`R_D(x,y) = (x-D(x-y), y+D(x-y))`.

The exact composition formula is `R_H R_L = R_(H+L-2HL)`. For nested projectors, this is `R_(H-L)`. Thus all new query paths telescope with the old endpoint maps on every address, subject to the retained address-field contract. The checks use exact rational matrices, not sampled addresses or only ranks.

All new oriented query types but `506 -> 0` already occur in the consumed baseline. The existing `1 -> 506` rank-four query uses `I-P_506`, whereas the new query uses `P_506`. A claim of literal oriented-matcher reuse at this point is false.

To supply the missing algebraic matcher, form W from the columns of `B_506^T` followed by `A_506^T`. Exact inversion gives

`W diag(I_4,0) W^-1 = P_506`,

and both products `W W^-1` and `W^-1 W` equal I. These matrices are printed in RESULT.json. Their common denominator is 4. Their maximum absolute row sums are 3 and 2. Together they contain 38 nonzero coefficients; this is a coefficient inventory, not a tape instruction price. Applied to both paired address halves, they conjugate the standard rank-four involution to the required residual map. Reduction is valid over every address ring where these denominators and the retained source denominators are units.

This resolves the new residual's exact basis and inverse. It does not make either direction free. A complete physical caller must compile both ordinary address maps, account for all their coefficients and routes, and use fresh finite constants. The proposal's general finite-matcher assumption can include them, but a claim that an old oriented query was reused without change cannot.

## 5. Paid and productive inventories

The emitted word is counted directly. Each simple window replaces one H1 and one H3 with H4. Each refined window removes two helper H1 calls and one helper H2, adds one helper H4, then replaces one SOURCE H3 with SOURCE H2 and H1. Its net change is also `-H1-H3+H4`.

Relative to PR5653, the combined local delta is `-14H1-14H3+14H4`. The program has 19,043 ADDs, 78 ERASEs, one INIT, 2,864 paid Qs and nine ZERO_Qs. These ordinary operations are visible in the word; this package does not assign them zero cost or turn their count into a completed machine tariff.

The eighteen-call controller retains its calls and all nonlocal work. Substitution into the frozen complete baseline invoice gives

`P_new = P_5512 -378H1 -378H3 +306H4`,

`T_new = T_5512 -72H4`.

The target debit is entirely due to the four prior retirements. No snapshot or correlated field receives productive credit. The new complete paid and target histograms agree exactly with the proposal. There are 56,547 paid calls, 11,166 productive targets and rank surplus 753. This is an independently checked histogram substitution on an emitted local word. It does not replace a replay of all chronological global descriptors.

## 6. Rational first-moment check and raw crossing

Define `F(C)=sum T_k k^(1-C)-sum P_k k^(1-C)`. The checker obtains the histograms from the emitted word and the pinned baseline, not by importing a primary price function.

For every integer cutoff from 1 through 128 it checks

`sum_(k>=u) T_k k - sum_(k>=u) P_k k >= 0`.

For `0<=C<=.01`, the function `h(x)=x^(-C) log x` is strictly increasing on `[1,127]`, since `1-C log x>0`. Summation by parts against the rank-mass tails therefore gives `F'(C)<0`; strictness follows from the nonzero tails. The raw zero in this interval is unique.

The independent enclosure reduces logarithms to `log 2` and `log(n/2^floor(log2 n))`. It uses 32 positive terms of the atanh series and an explicit geometric tail. For `x=C log n<1/20`, the degree-13 and degree-12 alternating Taylor sums bound `exp(-x)` below and above. All arithmetic uses rational numbers. Signed coefficients select the correct interval endpoint.

At `C=3497/1000000`, the lower endpoint exceeds `1/32`. At `.0035`, the upper endpoint is negative. Rational bisection then gives the exact interval in RESULT.json, of width below `10^-13`. Decimal displays are only aids to reading the rational endpoints. The root does not include the ordinary cover loss, finite completion margins, backend chain, or outer multiplication constraints.

## 7. Failure controls and remaining work

Fourteen source mutations insert a value-changing write into a required unchanged SOURCE interval. Each fails the source conditions. Other controls remove a snapshot, a paid refined query, an owned teardown, or a recipient's independent injection; attempt to erase a retained arbitrary helper; or change the explicit frame-506 matcher. All fail. Checks remain enabled under Python optimization.

The source's informal analytical ordinary proof, full native/all-width and ROW contracts, finite compiler, complete global stream, positive ordinary constants, precision, physical tape costs and analytic outer conditions are not newly certified here. The useful handoff is the frozen local word, all edits, exact new matcher and source-bound invoice. They make a complete ordinary admission check concrete. No selected-frontier change or new whole kappa follows from this package.
