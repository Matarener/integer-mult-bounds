# Pooled local words in the existing physical instruction language

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Jose Manuel authored the retained physical compiler, controller and
primitive arguments; the frozen texts retain their complete attribution.
Cinna Davis's borrowing/warp construction and Rohan Arun's pooled fill retain
their original credit. This contribution binds those constructions to each
other at their stated interfaces.

## Result and evidence boundary

The older R480-only interpreter is not the strongest available predecessor.
The canonical `research/t74-physical-layer/compile_word.py` already supports
exactly the persistent/centre/Z layout used here. Its **unchanged** `Compiler`
successfully lowers all three active pooled providers in both orientations.
No warp or Z operation introduces a positive-rank child.

`physical_bridge.py` pins all twelve actual native files from the completed
pooled release and the retained compiler/scalar/affine sources. Its immutable
26-member closure is in `frozen/physical-t74/SOURCE-BUNDLE.tar.gz`; every raw
member and the archive itself are authenticated before use. Python source is
compiled from authenticated bytes, without a bytecode-cache lookup. The
archive is checked for a complete unique regular-file inventory and contained
paths before temporary extraction. This check needs only the standard library
and does not need Git objects or network access.

The finite result is:

| Provider | Source events per orientation | Lowered instructions per orientation | Positive children per orientation |
| --- | ---: | ---: | ---: |
| gauge44 | 22,807 | 29,915 | 3,554 |
| extra | 22,807 | 29,915 | 3,554 |
| extra-four | 22,808 | 29,920 | 3,556 |

Each orientation contains 240 warp events and 182 Z allocation/release events.
The six programs use 3,848 distinct monomial literals and 36 scalar literals.
The largest affine word has 61 gates. Each scalar recipe has at most ten
instructions, prefix denominator at most eight and affine row l1 norm at most
nine. These scalar-prefix figures are local lowerer facts; the complete caller
still needs the already invoiced whole-word guard.

The private map is explicit: `L0..L631 -> 0..631`, `C0..C7 -> 632..639`, and
the provider's sorted 91 Z labels map to `640..730`. There are 731 local packet
roles, including 99 owned private packets. Z allocation is distinct from
clearing an arbitrary dirty input. Each provider has one complete Z lifetime.

The checker additionally proves every compiled affine map and its inverse on
all `2^73` addresses by exact symbolic affine rows. It exhausts all 512 native
addresses for every phase polynomial. The higher 64 coordinates have explicit
identity affine action and zero phase coefficients. The separate native
operator admission establishes that these serialized recipes implement the
intended frame/warp products; recompiling a serialized recipe alone would not
establish that semantic claim.

Nine controls reject missing or premature Z release, the wrong warp entrance
frame, a positive-rank warp, an omitted or inverted lowered warp, a misbound
warp recipe, unchecked clearing in place of Z release, and release of the
wrong private packet. The latter controls test the independently checked
event-to-instruction binding, including the required `inverse=False` flag.
The inherited runtime's actual zero check is source-pinned separately.

## All-width local refinement lemma

The following is a written compositional proof under named primitive
contracts. It is not inferred by enumerating numerical packet sizes.

Fix one of the six authenticated local programs. Let `f>=1`, `K>=1`,
`0<=rho<K`, and `G>=1`. Supply complete aligned Gaussian packets, arbitrary
complete prefix/suffix spectators, and the retained three compact fields.
Each of the 73 vector fields has exactly `fK` bits. Each of the three compact
fields has exactly `(f-1)G` bits in the retained earlier/later placement,
including width zero at `f=1`. Any additional complete capacity is represented
by separately named prefix/suffix spectator fields. Outer
row count and the number of coefficients per record are positive integers.
Components have one common dyadic grid and signed width `h>=2`. Assume the
caller guard covers every exact half and signed arithmetic prefix. Persistent
inputs may be arbitrarily correlated and dirty. Private C/Z packets are owned
work, initially blank. Borrowed source and descriptor ports have canonical
heads and the inherited complete-word markers.

Assume the existing all-width scalar, monomial, copying and ordered child
contracts, including their source/spectator preservation, work erasure and
head returns. A positive-rank child is the exact completed tensor on the full
prescribed `rf` axes, not one child per coefficient or unused row.

For a warp event, select its exact `(sign,operator,old,new)` record. The emitted
monomial is the rank-zero physical product

```
Gamma_new K_operator^(sign) Gamma_old^-1.
```

Apply its columnwise lift once. Each column retains the serialized affine
map and quadratic/linear phase; a constant phase `i^a` becomes `i^(fa)`.
Role-level ADD/SCALE coefficients occur once and are not tensor-powered.
The separately supplied backward scalar word uses the same physical warp
record under the retained free-operator convention. Replacing that record
by its complex conjugate or inverse changes the specified contract.

The retained monomial lowerer implements each fixed affine gate with the
completed Compact routine; its phase pass evaluates the phase on the source
address and, on an inverse invocation, on the recovered source address.
Its encoded phase accumulator keeps a residue modulo four. Induction on the
`f` column iterations gives the sum of the `f` phase polynomials, including
`fa`. Thus the construction works on the entire tensor space, including
correlations between columns and helpers.

For a Z allocation, fill the declared owned packet with exactly the encoded
packet extent of zero bits and return its head. For a Z release, scan that
entire extent and require every bit to be zero before erasing it and returning
the head. The pinned `T74Machine.release_zero_step` performs this check before
`clear()`. The native free-operator cleanup proves that the required zero is
reached for every persistent input; it is not an assumption that the original
dirty helper was zero. Live Z packets exist only in the FULL-frame cleanup.
The original centre CLEAR remains owned-work disposal with its separate
source-word semantics.

At an ADD/SCALE, the exact three-word scalar lowering preserves its source and
returns its scratch to logical zero; the physical scalar interpreter consumes
complete components and erases owned work. At a positive child, apply the
right monomial, the completed exact child, then the left monomial. The literal
frame and lifetime checks ensure that these contracts compose at every event.
Induction over the finite instruction sequence establishes the native local
endpoint for every admitted `f`, width and complete payload. All 632 persistent
packets return under their specified endpoints; all private work is blank and
all primitive interfaces have returned their heads. The local endpoint alone
does not assert a global physical owner map or an enclosing multiplication
algorithm.

## Paid tariff for the new macros

Write `C_rows` for the number of complete outer rows, `a` for the within-row
address width, `R` for the record width in bits, `M=C_rows*2^a`, `V=MR`, and
`A=2+a+ceil(log2(R+1))`. For `f>1`, put `b=(f-1)G` and

```
delta = min(1,(f-1)*(2*2^-G + 8*2^(G-K))).
```

The retained Compact theorem charges, for each affine gate, four completed
ordinary calls per row for an earlier source/toggle or twelve for a later
source, plus

```
O(V + M A^6 + delta M A(R+A)).
```

The phase pass additionally costs `O(V+M A^2)`. Summing the actual affine word,
each of our monomials therefore costs at most

```
s_R * sum_(row=1)^C_rows T_ordinary(V/C_rows,b)
 + O(61*(V+M A^6+delta M A(R+A)) + V+M A^2),
```

where the exact source-order sum satisfies `s_R<=524`. This is a bound on
ordinary primitive calls, not on recursive complex children. The `f=1` branch
uses the retained direct bit-permutation/phase routines and has no Compact
call at width zero. It retains the displayed preparation/scan charges.

Each Z allocation and checked release costs `O(V+log(V+1)^2)` symbol steps,
including extent arithmetic, encoded counters, terminal probes, writes,
checks, erasure and rewind. Hence it is `O(V)` for positive complete packets.
This is a uniform asymptotic bound with fixed primitive constants, not an
unmeasured numerical microtransition count. Allocation uses one owned packet;
release returns it to blank. All 91 Z packets remain charged throughout their
literal lifetimes. No scan or disposal is treated as free.

Consequently the 240 added monomial events and 182 Z events contribute no new
positive-rank recursive call and a fixed multiple of the paid primitive bill.
Under the retained long-record/compact guard and a completed ordinary bound
`T_ordinary(v,b)=O(v(1+b^tau))`, this is
`O(V(1+(f log p)^tau))`, with `O(V)` local workspace plus fixed compilation
storage. Without those input-domain hypotheses the unabsorbed terms above
remain part of the tariff.

## Finite control and separate global binding

All local event, role, recipe and program-counter labels range over fixed
finite sets determined before input. The largest local code has 29,920
instructions, below the inherited 65,536 bound. Component widths, packet
extents and row counts remain encoded on tapes. This permits the retained
local finite-state composition of the primitive controllers; it does not
license a host integer, seek, stack or Python event loop as a free operation.
No literal universal transition table or formal-kernel proof is supplied.

This result resolves the **local opcode/lifetime** part of the gap: the new
warps and private buffers fit an already available physical instruction
language, with exact source binding and a paid all-width local argument.
The companion PHYSICAL-GLOBAL.md supplies the separate new global owner
dispatcher, actual cover charts/translations, bank and recursive root binding.
Its main layer rate uses the existing PR3599 completed ordinary B1 contract;
it does not assume the optional B2 bootstrap. Root/outer domain compatibility
remains separate from this local lowering certificate. Any further ordinary
bootstrap must construct its actual backend noncircularly; changing a `Profile`
constant alone does not replace C0's primitive calls.

## Reproduction

```
python3 -I -B research/complex-pooled-full-admission/physical_bridge.py
python3 -I -O -B research/complex-pooled-full-admission/physical_bridge.py
```

To additionally compare every frozen native input with an actual fresh release,
pass `--release-providers /absolute/path/to/global/base/providers`. `--out`
may name a receipt outside this package. Normal and optimized runs perform the
same exact checks; the output distinguishes local lowering from global machine
admission.

The immutable local bundle also includes the exact `scalar_words.require_zero`,
`ScalarEngine.run` and `FullScalarEngine` bodies reached by the described scalar
and Z-release macros. This is a source pin, not a new execution of their physical
tape cohort. The all-width statement retains the scalar-stream theorem and its
encoded Count/Tape, signed-arithmetic, scratch and source-cohort contracts.
