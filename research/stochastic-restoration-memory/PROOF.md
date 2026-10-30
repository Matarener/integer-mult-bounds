# An optimal 76-bit retained log for the exact PR6066 forward map

This proof concerns the historical 748-role, 9,589-event scalar prefix used by [PR6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066). It does not transfer the result to the different selected PR6030 word. All incoming integer values are arbitrary dirty data. Fix every forward coin to zero; this is a permitted finite tape with positive probability under the fresh-coin model. The tape is retained unchanged.

## 1. A surjective prefix with exactly 2^60 preimages per state

For a dyadic denominator d and fixed u, write S(n,d,u)=floor((n+d-1-u)/d). An ADD x_r += S(n*x_s,d,u), with r != s, is a bijection of the full integer state: subtract the same function of the unchanged source. A sign SCALE is also a bijection.

A signed half SCALE is exactly two-to-one and surjective. For sign s in {-1,1}, output y, and u in {0,1}, its two distinct preimages are

    x = s * (2y + (2u-1)r),    r in {0,1}.

The first 8,411 source events contain 60 signed half SCALEs, no doubling, and otherwise only ADDs and sign SCALEs. Composition of a surjective a-to-one map and a surjective b-to-one map is surjective and ab-to-one. Therefore, for **every** fixed tape and every prescribed state after event 8410, this prefix has exactly 2^60 distinct original input states. The choice bits in the reverse interpreter give an explicit parametrization of them.

Counting all 84 halvings alone would be invalid: the later program has 32 doublings, and double followed by stochastic half is injective. This is why chronology and the tail need separate checks.

## 2. Eight independent four-preimage tail blocks

The next 1,121 events partition into eight consecutive programs on the disjoint role sets 272..287, 288..303, ..., 384..399. The first three blocks have 137 events each; the last five have 142 each. No block reads or writes outside its own sixteen roles. Each has three signed halvings and four doublings.

[COLLISIONS.json](COLLISIONS.json) supplies four distinct 16-integer preimages and their common output for each literal source block, with every coin zero. The verifier replays all 32 input vectors directly against the authenticated source events. It also runs an independently structured reverse branch interpreter: each halving branches into its two preimages and each inverse doubling rejects odd values. For the nominated output it checks that the complete surviving fiber is exactly the four committed vectors. These are finite lower-bound witnesses. Section 5 independently proves a four-preimage upper bound for every output and tape by recovering one of each block's three residues.

Take the Cartesian product of these eight four-element sets, fixing all other coordinates to zero at the start of the middle program. Disjoint support proves that its 4^8 = 2^16 distinct states have one identical complete 748-role output. Every following event is deterministic with the fixed tape, so the final 57 ADDs preserve this collision.

## 3. Lift through the first prefix

Every one of those 2^16 middle input states has exactly 2^60 distinct original preimages by section 1. The preimage sets of distinct middle states are disjoint. Hence the complete forward map F_0 has a fiber of cardinality at least

    2^16 * 2^60 = 2^76.

This large cardinality is proved by composition; the verifier does not claim to enumerate 2^76 inputs. It checks the complete small fibers that generate the product, all 516 signed-half identities over the stated finite corroboration range, and 86 complete lifted source executions. The latter cover all-zero/all-one/unit choice patterns for the sixty early residues and each of the other three choices in each tail block. They all reach the same full endpoint.

The witnesses are finite integers. A conservative reverse interval bound starts with the largest absolute middle-collision coordinate. In reverse, an ADD increases the global magnitude bound B by at most ceil(|n|B/d), a signed half changes it to at most 2B+1, and a sign leaves it fixed. Applying this to all 8,411 events gives a bound with 4,563 magnitude bits. Eight additional bits cover the sign and scalar numerator/addition guards. Thus the collision proof also applies to sufficiently wide finite implementations (the supplied conservative sufficient width is 4,571 bits); it is not a lower bound for every tiny fixed-width or restricted-input variant. The 86 executed fixtures actually stay within ten magnitude bits. The guard calculation is deliberately an upper bound, not an optimized precision requirement.

## 4. Consequence for retained information

Suppose the exact forward stage of a pathwise restorable implementation has the boundary

    (x, U, 0) -> (F_U(x), U, A(x,U)).

All additional state capable of distinguishing inputs is included in A: logs, temporary registers left live, control state, or head-position information. Fix U=0 and restrict x to the proven 2^76-point fiber. The first two output components are identical on that set. Injectivity, necessary to restore arbitrary dirty x, therefore requires at least 2^76 distinguishable values of A. An auxiliary capacity below 76 bits is impossible. Copying F_U(x) to a disjoint accumulator with the same initial value does not distinguish these inputs.

This is a **worst-case** bound for exact pathwise restoration and the same forward map/tape. It does not bound average compressed length or prove that every tape needs 76 bits. It does not cover a changed rounding law, bounded-error restoration, restricted reached input set, or a different forward interface that leaves further input information in other outputs. Such extra information is payable and cannot be called clean scratch.

## 5. Recover eight residues instead of retaining them

Number a block's local roles x0,...,x15. Its first half acts on x9, after a twelve-ADD phase whose only source is x9. The source has two block templates. Immediately before this phase they satisfy, for arbitrary incoming integers and every fixed tape,

    first three blocks:  x15 = 0             (mod 2),
    last five blocks:    x10 + x15 = 0       (mod 2).

These are literal source invariants. The verifier derives them by propagating integer parity rows through the pre-phase program. Each fractional ADD is replaced by an entirely arbitrary independent integer contribution to its target. This enlarges the possible states, so any relation annihilating all original bits and all these extra noise bits holds for the actual rounded word. The derived annihilators are masks 0x8000 and 0x8400, respectively. Every coefficient column is checked.

In the following twelve-ADD phase, x15 receives x9 exactly once with coefficient +1; x10 is unchanged. None of the fractional ADDs targets a parity holder. The holders do not include x9. Therefore, immediately after the signed half of x9, its discarded input parity is exactly

    first three blocks:  x15 mod 2,
    last five blocks:    (x10 + x15) mod 2.

The relation is independent of the rounding coins and of the magnitude of the data. In reverse, all later block events have already been undone when this half is reached. The displayed parity is consequently available from the current state. Recover it, apply the usual matched-coin inverse half, and continue. No retained bit is required for these eight particular halves.

The other 76 signed halves use PR6066's original retained parity and cleanup rule. Forward arithmetic and every coin are unchanged; forward processing merely omits eight log writes. Reverse processing infers those eight bits using thirteen existing-value parity reads. All retained bits are cleared after reconstruction, as in the predecessor. The complete logical boundary is

    (x, y, U, 0^76) -> (x, y + F_U(x), U, 0^76).

The intermediate forward boundary retains F_U(x), U and exactly 76 residue bits, with no additional input-dependent retained payload. This supplies a computable inverse on the reached image. Together with section 4 it proves **76 is the minimum worst-case retained information capacity at this logical boundary**. Equivalently, every fixed-tape fiber has size at most 2^76, and section 3 attains that size on the all-zero tape. Each tail block has at most four preimages: only its other two half residues can vary after the first is inferred.

The source-bound checker compares the new forward endpoint with the exact unmodified PR6066 interpreter on 64 full protocols, using all-zero, all-maximum and independently generated mixed tapes and arbitrary signed dirty values. It checks exact restoration, all 76 cleaned residues, unchanged tape, and the same dirty accumulator update. A wrong parity-holder control fails on an actually reached state. The symbolic parity invariant, rather than these finite protocols, supplies the all-input/all-tape proof.

This is an eight-bit reduction from the original 84-bit retained log (2/21, about 9.52%). It does not bound total physical working memory or execution time. Temporary integer scratch and its reversible cleanup, finite guards for arbitrary callers, tape access, the next native MOVE and the full supplier bill remain unpriced. Fewer retained bits do not alone imply a runtime improvement, new kappa, or a complete rounded multiplier.

## Credit

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance. [Nick Petalas](https://github.com/petalas)'s [PR6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026) supplies the stochastic prefix and error context. [Ali Romman](https://github.com/aliromman)'s [PR5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) and the retained P104 lineage supply the source word. The round-and-restore ABI is PR6066's. Fiber counting and injectivity are classical; the contribution is this source-bound 2^76 collision and its exact restoration implication. Apache-2.0. No independent human or formal proof-kernel review is claimed.
