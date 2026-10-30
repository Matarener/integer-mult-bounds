# A second entrance direction for helper 544: exact scoped rejection

On both frozen PR4076 providers, adding one entrance direction to helper 544
fails with the existing two release slots. One fully compensated later release
is algebraically exact on arbitrary dirty inputs, including its literal inverse,
but also fails the frame contract. Neither word supplies an admitted width 6
helper or a paid recursive saving.

## Source and model

The source is PR4076 commit
`9744f9df268590295a9872b1952c695a678192b9`, specifically its `NEW-base` and
`NEW-extra` words. [SOURCE-EXPORT.json](SOURCE-EXPORT.json) binds the exported
bytes, their original paths and Git blobs. Its SHA256 is
`a53a27d6d9f1e2b2fd5612f77f752dd007293a8d4cb6342c6e7a590dffe07aa1`.
The run's canonical base is `bb4bccbf42844d2801487450727c2f63e10d1d0f`.
The PR3949 staged-entry design was consulted at commit
`9c11143b961327559e568a445a2047db2d964ef4`; none of its old census results
certifies these changed words.

The finite geometry has 112 sources, 112 targets and 408 live helpers, with
91 independent dirty private buffers. Every live input is independent. The
retained arbitrary-operator interpreter checks all 723 symbolic input columns,
including noncommuting native operators and their contragredient partners.
No helper, source or private buffer is assumed initially zero.

The inherited entrance of 544 is

`E = span(414,51)`, with dimension 2 and ordinary terminal `FULL9`.

Its first producer is old B685, `544 += 379`, at

`P = span(392,37,22)`, with dimension 3.

Since `E` is contained in `P`, the only dimension 3 extension of `E` contained
in this unchanged producer frame is `P` itself. The nominal width change would
be `9-2 = 7` to `9-3 = 6`. No A event, wrapper, correction or native warp
touches 544. The source and helper terminal contracts, A word, target levels,
centre frames, native matrices and native lenders are fixed in these trials.

## Existing releases: a short obstruction

Keep the scalar word and literal inverse, raise 544's entrance to `P`, and
propagate the least possible B/restore frames. At a scalar gate this is the
join of its registers' current frames. At a native warp it is the image under
the unchanged binary map. An induction over chronological events proves that
every feasible assignment with the same A frames contains this assignment.
Terminal frame constraints are upper bounds, so a failed terminal is decisive.
The same rejection occurs if every old scalar frame is retained as an additional
lower bound.

This walker preserves native matrices and lenders while allowing each native
entry/exit frame to become the current frame and its image. It is a favorable
relaxation used for a necessary feasibility test. It is distinct from a check
that fixes every original native frame boundary, and does not establish native
admission for a changed word. The containment witnesses below avoid native
warps entirely and survive this relaxation.

There is also a shorter proof that does not depend on the other chosen frames:

| Old gate | Operation | Forced containment |
|---|---|---|
| B683 | `672 += 544/2` | `22` enters the frame of 672 |
| B1116 | `672 += 462` | the common frame of 672 and 462 contains `22` |
| B1738 | `116 += 462` | target 116's frame contains `22` |

No native warp touches any register on this path. Target 116 must finish in
the hyperplane perpendicular to port 131, but
`popcount(22 & 131) = 1`. Monotone frames cannot meet that terminal.
The middle step is propagation through a **common gate frame**; it does not
claim that the scalar value of 462 receives the value of 672.

Exact least-frame replay forces FULL9 on targets 116, 117, 180 and 181,
although each has an 8-dimensional terminal. The scalar program remains the
source program, so all arbitrary-dirty semantic and inverse checks still pass.

## One late cut, with the actual dirty recovery

To test a different contact path, delete only the two releases

```
old B683: 672 += 544/2
old B684: 676 -= 544/2
```

and insert one compensated release block immediately before old B1752.
Between the deleted releases and this cut, 672 and 676 are only written by
additions of other registers: neither is read, nontrivially scaled or warped.
An addition of their original dirty value therefore commutes through that
interval. Old B1753 is the first later read of 672; B1764 is the first later
read of 676. The chosen boundary before B1752 is one commuting recipient write
earlier than the latest common boundary before B1753. Moving the block across
B1752 leaves both the recovery row and the obstruction below unchanged.

Write `h0` for the actual original input of 544, `a` for the actual value of
379 read at B685, and `b` for that of 236 read at B686. They include all entering
dirt. Immediately after the producers,

`544 = h0 + a - 2b`.

Using this identity at the late cut without following the source rows is wrong.
The exact chronological inverse-row updates are:

| Old gate | Recovery of `h0` in current registers after this gate |
|---|---|
| B685: `544 += 379` | `544 - 379` |
| B686: `544 -= 2*236` | `544 - 379 + 2*236` |
| B801: `379 += 395` | `544 - 379 + 2*236 + 395` |
| B1417: `379 -= 283/2` | `544 - 379 + 2*236 + 395 - 283/2` |

No other gate before the cut changes this recovery row and no native warp sees
its support. Thus the exact late recovery is

`h0 = 544 - 379 + 2*236 + 395 - 283/2`.

The literal replacement block is:

```
672 += 544/2
672 -= 379/2
672 += 236
672 += 395/2
672 -= 283/4
676 -= 544/2
676 += 379/2
676 -= 236
676 -= 395/2
676 += 283/4
```

It delivers `+h0/2` and `-h0/2`, respectively. All ten coefficients are allowed
dyadics. The exact symbolic prefix map after this block equals the old prefix
map at the chosen cut on every one of the 723 independent inputs. In
particular this is a simultaneous identity, not a concatenation of recoveries
assuming clean or unchanged sources.

The original source/current-reader frames just before the cut have dimensions

| Register | 544 | 379 | 236 | 395 | 283 | 672 | 676 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dimension | 7 | 8 | 6 | 5 | 8 | 6 | 5 |

Their complete bases, least propagated new frames and every new gate are in
[candidate-result.json](candidate-result.json). These actual source-access
frames cannot be replaced by the 3-dimensional producer frame when pricing
the late release.

For old B indices, the exact new scalar index map is:

| Old index | New index |
|---|---|
| `i < 683` | `i` |
| `683,684` | deleted |
| `685 <= i < 1752` | `i-2` |
| `i >= 1752` | `i+8` |

The inserted block occupies new B1750 through B1759. Native positions are
recomputed from their original chronological boundaries; no native event
occurs at the selected cut.

### Full inverse and semantic checks

Cleanup is regenerated by the unchanged `audit_core.derive_cleanup`, reversing
every non-target operation. The ten inverse additions occur at cleanup indices
268 through 277 in reverse order with negated coefficients and FULL9 frames.
Because 395 is a restored helper, its cleanup source is its private buffer
`395+704 = 1099`; substituting the live restored row is not the literal inverse.
The JSON records the entire inverse block, not just its operation count.
There are eight more scalar additions in B and eight more in cleanup than in
the source. No new buffer is introduced. Restoration of every original live
and private input is included in the exact semantic checks.

For both words, replay passes forward, contragredient, reverse pull-back,
forward and reverse cleanup-boundary checks; all private buffers return
identically and buffer-to-live leakage is zero. The total endpoint map has
835 nonzero terms, as required by the source contract.

### The late word also has no legal frame bill

The first inserted gate reads 544 into 672, so 672's frame contains `22`.
There is no warp of 672 before old B1754, `181 += 672`. Target 181 therefore
receives this direction in its frame. Its terminal is perpendicular to port
304, while `popcount(22 & 304) = 1`. The source corrections cannot cancel
membership of a direction in a monotone frame. Reordering those correction
additions does not remove this path.

Exact least-frame replay rejects the late word at targets 177, 181 and 208,
and at restored helpers 395, 454 and 556. The first inserted frame has dimension
8; the second forces FULL9, which then propagates through the remaining block.
These extra source and restoration failures are retained in the result.

## Complete accounting and limits

The valid source bill is

`2488 H1 + 714 H2 + 223 H3 + 102 H4 + 20 H5 + 8 H8`,

with helper inventory `{5:28,6:18,7:56,8:93,9:213}`. As a positive feasibility
control under the same native-boundary relaxation, the original entrance and
scalar word have an absolute least B/restore assignment. Its complete formal
frame-walker bill is

`2564 H1 + 697 H2 + 263 H3 + 79 H4 + 6 H5 + 8 H8`,

with the same inventory and rank mass. This control need not be cost optimal
and is not a newly admitted physical supplier bill.

Neither raised trial has a complete paid profile under the specified terminal
contract. The checker explicitly returns no profile or admitted inventory for
it; counting a downward terminal repair as a child would violate monotonicity.
The nominal width `7 -> 6`, the old staged-entry signature, and any pooled owner
shadow price are consequently unavailable as supplier savings for these words.

This result covers the two exact frozen words, the same-slot entrance raise
and this single compensated late cut. The short containment proofs apply to
every frame assignment retaining the specified contacts and terminals. The
symbolic calculation is a finite exact word replay on arbitrary independent
inputs, not sampling, an all-size supplier construction or a formal-kernel
proof. Native phases, a changed physical owner fill, all-size hosting, tape,
precision and outer multiplication transfer were not established. No new kappa
or selected-frontier improvement is claimed.

## Replay and controls

From the repository root, Python 3 standard library only:

```
python3 -B research/second-staged-544/candidate.py
python3 -O -B research/second-staged-544/candidate.py
```

The default requires and compares the complete frozen JSON without writing it;
missing fixed evidence is a failure.
`--check PATH` selects another frozen result; `--output PATH` writes a fresh
result for comparison. `--emit-dir PATH` optionally preserves the two rejected
diagnostic words per provider in an owned external scratch directory. Those
words retain an inherited report and have rejected frames; they must not be
treated as admitted provider inputs.

Source bytes are authenticated before the retained interpreters are executed
with `compile`/`exec`, avoiding bytecode caches. Checks include the feasible old
entrance, exact 723-row prefix equality, and arbitrary-dirty rejection of the
stale immediate post-producer formula and omission of each of the five actual
recovery sources. Explicit exceptions remain active under `python -O`.

## Open next questions

Reopening this mechanism requires an explicit changed recipient boundary or a
joint recovery that avoids the `544 -> 672 -> 181` frame path. It must include
the actual source rows, their access frames, restored-helper buffers and full
inverse cost. Another release timing within the same unwarped recipient path
does not discharge this obligation. No other donors, cut census or width 8/9
search was performed here.

## Sources and credit

PR4076 is Rohan Arun's construction with Anthropic Claude assistance. Its
[NOTICE.md](source4076/NOTICE.md) preserves the full Apache-2.0 lineage.
The staged-entry design is Ross Richardson's PR3605 and dataisfire's PR3734;
the general recovery/assembler method is Erwan Secousses / ChaloupeMusic's
PR3949. Dugongue's PR3945 supplies the retained frame-walker lineage.
`audit_core.py` is Sagar Thakrar's PR3687 interpreter, crediting Arham Tahir's
audit, and `audit_verify.py` is roger-sato's PR3693 adapter. This trial reuses
those interpreters and is not a new independent interpreter. The containment
and dirty recovery derivation, scoped trial and source-guarded controls were
prepared with substantial OpenAI GPT-6.1 Sol assistance. AI assistance is not
independent human review. Apache-2.0.
