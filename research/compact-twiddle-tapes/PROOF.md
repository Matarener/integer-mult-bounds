# Compact supplied programs on five tapes

This is an author-written proof. Independent human and formal proof-kernel review are unclaimed. The mathematical statement is for every finite program. The executable admits at most 4,096 wires and 200,000 program symbols.

## Contract and machine model

Let A>=1, G>=0 and Q>=1. A topological AND/XOR circuit has constants numbered 0 and 1, A input wires numbered 2 through A+1, gate j at c_j=A+2+j, and Q ordered output wire indices w_t. Each gate operand a_j,b_j is smaller than c_j. Put B=A+G+2 and H=ceil(log2 B). Let h(w)=max(1,bit_length(w)).

The supplied immutable program is `^`, then the G gate rows, then the Q output rows, then `$`. A gate row is opcode A or X followed by two operand fields. An output row is opcode O followed by one operand field. A field is the canonical least-significant-bit-first binary encoding of its index followed by `#`. Zero is `0#`. The last bit of any longer field is 1. Its complete length is

    L = 2 + sum_j [3+h(a_j)+h(b_j)] + sum_t [2+h(w_t)].

The five tapes are program P, borrowed address X, private wire values W, private binary counter C and returned header Y. X initially contains `^`, its A bits in physical MSB order, then `$`. P and X start at their first symbols. W, C and Y start blank. The allocated extents are exactly

    P: L,  X: A+2,  W: B+2,  C: H+3,  Y: Q+3.

One read, write or unit head move costs one primitive. The finite alphabet is the fixed union of program opcodes, bits, markers and blank. Finite state holds the current opcode, at most two Boolean operands, a zero flag and a flag recording whether a decrement crossed a low zero. It never holds a numerical wire index. The Python list backs a tape; executed accesses use only Tape.read/write/move at its head. Host admission, binary encoding, allocation, instrumentation and final observation are outside this primitive invoice. Host loop bounds are safety guards derived from allocated extents. The successful control path terminates on tape markers and counter zero, so it does not use those bounds as an uncharged address oracle.

This is a sequential machine-model implementation, not a lowering into the repository's production tape library. Host admission checks the complete input before constructing tapes. There is no rollback promise for interruption, external mutation or an injected fault after execution starts. Private storage is initially blank rather than arbitrary dirty workspace.

## Binary access lemma

To fetch wire w, load its h=h(w) supplied bits into C between `^` and `$`, returning C's head to its origin and advancing P past `#`. While loading, finite state records whether any copied bit is 1. This determines zero without a second scan. W starts at its origin. Move W once to constant-zero position. If C is nonzero, subtract one with a low-to-high borrow ripple, normalize its end marker as below, return C to `^`, and move W one cell right. Repeat until the decrement returns the zero flag. Read the wire bit, return W to `^`, and erase C.

Maintain C's canonical binary encoding. For a positive integer k, flip its t=v2(k) low zeros to ones and clear its first 1. Inspect the next cell. If that cell is `$` and t>0, the cleared 1 was the top bit of a power of two. Erase the old `$` and put a new `$` over the cleared bit. The new top bit is one of the t written ones. If that next cell is `$` and t=0, k was exactly 1, so the new canonical counter is `0` and the returned zero flag is true. If the next cell is another bit, a higher 1 remains because the previous encoding was canonical. Keep the marker and return false. A Boolean flag indicating t>0 suffices; no integer t is held in finite state.

After k decrements, C canonically represents w-k and W is at position k+1. Ordinary binary subtraction and the end-marker cases prove this invariant, including the returned zero flag. The process stops after exactly w decrements, reads precisely wire w, returns W's head, blanks C and returns its head. C is then `^0$` before erasure, irrespective of w. Every removed top bit also erases the old end marker, so all cells beyond the current marker are blank. W's last accessible wire is at position B, followed by a blank at B+1. The counter's largest written position is at most h+1, followed by a blank at h+2. Both tapes fit their allocated extents.

The exact costs, counting each terminating marker read, are:

| Part | Exact primitives |
|---|---:|
| Load P field, including `#` and advance | 2h+2 |
| Construct and return C after load | 4h+6 |
| Decrement k, including normalization and return | 5v2(k)+9, plus 2 if k is a power of two greater than 1 |
| Move W to w, read, return | 3w+5 |
| Erase the final `^0$` counter and return | 16 |

For a decrement without marker shortening, there are t low-zero read/write/move triples, one initial move, a first-one read/write, a successor move/read, one move back, and a home scan using t+2 reads and t+1 moves. This is 5t+9. Marker shortening adds exactly two writes. For any nonblank prefix consisting of `^` and n following symbols, erase uses 2n+3 reads, n+1 writes and 2n+2 moves, or 5n+6 primitives. The final counter has n=2.

The elementary identity sum_(k=1)^w v2(k)=w-popcount(w) follows by counting multiples of 2,4,8,... or by binary expansion. There are h(w)-1 powers of two greater than 1 at most w. Both identities also hold at w=0 with h(0)=1. The summed decrement bill is therefore 14w-5popcount(w)+2h(w)-2. Adding load, W access and erasure gives

    F(w) = 8h(w)+27+17w-5popcount(w).

No constant-time binary subtraction or full-width zero test is assumed. All bit flips, successor checks, marker shortening and head returns are charged. This is the amortization that removes the extra logarithmic scan factor.

## Circuit correctness and return

Initialization writes the two constants and the borrowed input into W. Its nonblank prefix is `^` followed by the A+2 initial wire values. Induct on j. Before gate j, all earlier wires have their circuit values, and all heads used by fetch are at their origins. The access lemma returns a_j and b_j. Finite-state AND/XOR computes the right bit. Scanning to the first blank appends it at c_j+1, then returns W's head. This proves the invariant for the next gate. Each output access then returns its designated circuit bit, appended to Y in order. The final program marker writes Y's `$` and returns Y's head.

After all outputs, W has exactly B bits after `^`; erasing that prefix blanks every W cell. C is blank after every access. P is rewound after its final `$`. X was never written and was rewound during initialization. P was never written. Therefore the result is exactly the circuit output, both borrowed tapes are preserved byte for byte with their heads at zero, both private tapes are wholly blank with heads at zero, and the output head is zero. The finite verification includes constants, repeated operands/outputs, no-gate programs and nontrivial borrow chains; induction supplies the universal claim.

## Complete invoice

Initialization costs 8A+18. Appending gate j after its two accesses costs 4c_j+9, including its opcode read/advance. Each output costs F(w_t)+4, including its opcode read/advance and bit write/advance. Interpreter setup, terminal-marker handling and output return contribute 2Q+8 outside those rows. Final W erasure costs 5B+6, and final P return costs 2L-1. Hence total executed primitives are exactly

    T = 8A+2Q+5B+2L+31
        +sum_j [4c_j+9+F(a_j)+F(b_j)]
        +sum_t [4+F(w_t)].

All allocated finite-alphabet tape cells, including borrowed program and address, output, markers and spare blanks, total exactly

    C_total = L+A+B+Q+H+10.

Since w<B and h(w)<=H<=B, F(w)=O(B). Thus

    T = O((G+Q+1) B+A),
    C_total = O(A+B+Q+(G+Q+1)log(B+1)).

These bounds do not include an accumulated output stream. Reusing the machine for many headers still requires a charged address producer and consumer. Input encoding is supplied; this proof does not execute a compiler from shape descriptors or claim that compiler's cost is zero.

## Synthetic exponent specialization and boundary

The three authenticated canonical inputs in SOURCES.json are actual runtime or mathematical premises. The retained circuit.py supplies the topological AND/XOR circuit. Its PROOF.md derives the physical named-slot order and combined exponent from the retained transform source and proves its exact circuit/gate bounds. We use that all-size theorem as a premise, rather than inferring it from finite evaluations here.

For ell>=2, each axis has ell or ell-1 address bits. In round h, the circuit has A=sum_i a_i inputs and Q=ell+1 outputs. When h>=1 and d_h>0, G=d_h(6h+5), plus 3(h+1) in the forward direction. When h=0 or d_h=0, G=0. Its output encodes the source combined exponent modulo 2^(ell+1), with the opposite sign in the opposite direction. The general theorem above executes those exact outputs. Under d*ell=O(p), A,B,G,Q=O(p), so this is an executed O(p²) primitive, O(p log(p+2)) cell implementation for a supplied compact program and physical address.

PR3534 used a supplied unary-index program with O(p²) program/cell storage and O(p²) primitives. The normalized binary interpreter combines that O(p²) primitive bound with the O(p log(p+2)) compact storage bound from PR3522's written O(p² log(p+2)) scan simulation. It uses five fixed roles. This improves the local control time/storage bound; it is not a universal strict saving for every tiny circuit or a complete transform algorithm. The exact comparison sources are retained separately in comparisons/ and COMPARISONS.json. They are not proof premises or runtime imports of this machine.

For fixed 0<epsilon<1, positive a_r,b_d, d<=b_d*p^epsilon and r>=2^(a_r*p/d), r dominates every fixed power of p. The polynomial header bound fits O(rp) eventually under those source comparison bands, with no explicit numerical cutoff supplied. This conditional absorption is not the complete caller cost.

Encoded shape/topology production, enumeration of physical addresses, movement and consumption of header packets, signed data/layer composition, complete spectator/buffer/head costs, native/root/ordinary refinement, outer recovery and all supplier/theorem obligations remain open. No selected frontier or kappa change follows.
