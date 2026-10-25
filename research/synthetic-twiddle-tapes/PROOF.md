# Sequential interpretation of synthetic twiddle headers

This is an author-written proof. Independent human and formal proof-kernel review are unclaimed. The theorem concerns every finite well-formed program below. The executable admission boundary caps the program at 2,000,000 symbols and the wire count at 4,096. These caps bound the replay, not the theorem.

## Contract and changed obligation

Supply an immutable A-bit address, A>=1, and a topologically ordered circuit with wire 0 equal to zero, wire 1 equal to one, address wires 2 through A+1, G AND/XOR gates, and Q>=1 ordered output wires. Gate j has result wire c_j=A+2+j and operands a_j,b_j<c_j. Put B=A+G+2. All output indices w_t lie in 0,...,B-1.

The input contract supplies the unary program specified below, rather than an encoded outer shape descriptor. Four fixed tape roles suffice to evaluate it. They preserve both borrowed strings and return both borrowed heads to their origins. The private wire tape is blank on return, its head is at the origin, and the output tape contains the ordered Q-bit result with its head at the origin. This is a successful-execution contract for well-formed inputs. Host admission rejects malformed strings before tape construction. No recovery from an interrupted or corrupted running machine is claimed.

PR3522 already supplies the exact twiddle circuit and a written binary-index scan simulation. This successor executes a different, simpler unary-index simulation and charges its larger program storage. It does not improve the prior O(p log p) program-space bound. The supplied-program boundary closes an execution gap without claiming an encoded shape-to-program compiler, address-stream producer or data consumer.

## Encoding and algorithm

All tapes use one fixed finite alphabet. The program begins with `^` and ends with `$`. Encode an operand wire w as w+1 copies of `1`, followed by `0`. A gate row is its opcode `A` or `X` followed by its two operands. After all gates, an output row is `O` followed by its operand. Thus the program length is exactly

    L = 2 + sum_j(a_j+b_j+5) + sum_t(w_t+3).

The address tape is `^`, the A bits, then `$`. Both borrowed tapes start at `^`. Initialize the blank wire tape by writing `^`, the constant bits 0,1, then copying the address bits sequentially. Rewind both heads to their `^` markers. Wire w now occupies cell w+1.

Read the program in order. For each unary operand, start the wire head at `^`, move it one cell right per `1` read from the program, and read its bit at the terminating `0`. Advance the program past `0` and rewind the wire head by unit left moves until `^`. The interpreter retains only the opcode and at most two bits in finite control. It never converts a wire index into a host integer or jumps to a tape position.

For a gate, compute its one Boolean result in finite control. Scan the wire tape right to the first blank, append that result, and rewind to `^`. For an output, append the fetched bit to the output tape. Upon program `$`, terminate the output with `$` and rewind its head. Scan the wire tape to its first blank, then erase its written prefix backwards, erasing `^` last. Rewind the borrowed program. All head movements in this algorithm are by one cell.

The Python Tape object implements this cell interface with an array and a current head. Only Tape.read, Tape.write and Tape.move access execution cells. The array representation, loop exhaustion guards, extent/cost instrumentation, initial allocation, admission parser, compiler and final observations are host infrastructure. They do not perform a semantic indexed wire read inside the executed algorithm. Loop bounds are defensive caps, while the tape symbols determine the normal stopping decisions. This is an executed sequential tape model, not a claim about CPU timing or a production fixed-tape library integration.

## Correctness and restoration

Induct on the gate rows. Before gate j the wire tape contains exactly the constants, address bits and the first j correct gate values, in that order. Each operand index precedes c_j, so its unary motion reaches an existing bit before the blank frontier. Rewinding returns to the unique unchanged `^`. The finite-control AND/XOR equals gate j, and appending at the first blank places it at c_j+1. This proves the invariant at j+1. Repeated operand indices, constant operands, unused gates and reconverging paths require no additional assumption.

All gate rows precede the outputs. Each output fetch therefore returns its correct final wire value, and the output cursor appends them in order. No write method can write to a borrowed tape. Address copying and program execution only move those heads; explicit rewinds restore their initial positions. The wire prefix remains contiguous throughout. Its reverse erase reaches and removes every written bit and the unique origin marker, then stops at cell zero. Every other wire cell was blank throughout. The output origin remains present and its final rewind restores head zero. These arguments prove every stated return condition.

The two origin markers on private tapes are initialization writes, not free supplied data. Their writes and the wire origin's erasure are in the invoice. The output is a retained result, not claimed blank private workspace.

## Exact primitive and storage invoice

Count every executed Tape.read, Tape.write and unit Tape.move as one primitive. Do not count host parsing, compilation, allocation, assertions, instrumentation or observation as tape primitives. For an operand w, fetching costs exactly 5w+9 primitives. Before gate j, c_j wires exist. Seeking its append position, writing the result and returning costs 4c_j+7. Opcode read/advance adds two. Hence a gate costs

    5(a_j+b_j)+4c_j+27.

An output row costs 5w_t+13, including its opcode and output write/move. Initialization costs 8A+18. Interpreter start/end and output-origin return cost 2Q+8 beyond the rows. Wire erasure costs 5B+7. Final program rewind costs 2L-1. The total is exactly

    T = 8A + 2Q + 5B + 2L + 32
        + sum_j [5(a_j+b_j)+4c_j+27]
        + sum_t [5w_t+13].

The allocated tape extents include one blank after each private written prefix. They are L for the program, A+2 for the address, B+2 for wires and Q+3 for output, or exactly

    C = L+A+B+Q+7 cells across four tape roles.

These are finite-alphabet cells, not ASCII byte tariffs or exact bit-operation counts. At most eight symbols suffice, so a constant-size binary encoding changes these asymptotic bounds only by a constant factor. No unbounded register or integer address is a machine primitive. The emulator's host allocations, Python objects and returned observation tuples are outside this physical-cell invoice and are separately bounded by its admission caps.

Since a_j,b_j,w_t<=B-1,

    L <= 2 + G(2B+3) + Q(B+2).

Consequently T and C are O((G+Q+1)B+A). This includes program scans and restoration, not just the Boolean gate count. The encoded program is supplied and retained, not treated as zero-width auxiliary control. Host compilation has O(L+A+G+Q) output/construction work in the ordinary character model and is not an executed encoded tape compiler. Converting binary circuit indices to unary with bounded binary counters gives a written O((L+A+G+Q)log(B+2)) bit-operation construction upper bound. That construction is not counted among the executed primitives or claimed executed here.

## Synthetic specialization and source comparison bands

Use the pinned PR3522 circuit and its proved named-slot interpretation. For ell>=2, long/short axis lengths a_i in {ell,ell-1}, chunk width 1<=K<ell and round 0<=h<ell, let I_h={i:h<a_i}, b_i=x_(i,h), and k_i=sum_(v<h)2^v x_(i,v). The forward Q=ell+1 output bits encode

    E = -2^(ell-h) sum_(i in I_h) b_i k_i modulo 2^(ell+1).

The opposite output negates E. PR3522 proves this formula, its gate counts and source layout binding; those are explicit inherited mathematical premises, retained as authenticated inputs. This proof establishes sequential interpretation of that circuit, rather than independently redoing the source layout theorem. Zero rounds and empty participation have G=0 and are covered by the same interpreter.

Under the pinned source bands d ell=O(p), D=d-1, A<=D ell, the predecessor has G=O(p), B=O(p), Q=O(p). Thus the executed per-header interpreter has O(p^2) tape primitives and O(p^2) supplied program/working/output cells. The separate written compilation bound is O(p^2 log(p+2)). As in the pinned source and predecessor proof, assume fixed positive a_r,b_d and 0<epsilon<1 with d<=b_d p^epsilon and r>=2^(a_r p/d). Then log2(r)>=(a_r/b_d)p^(1-epsilon), so r eventually dominates every fixed power of p. Both bounds are absorbed by O(rp) per polynomial record. This is an asymptotic statement with those hypotheses, not a numeric threshold or an improvement to kappa.

There is no executed address incrementer, supplied-program compiler or complete header stream in this package. Materializing headers for all 2^A addresses would require another 2^A Q output cells. An actual streaming packet consumer and its buffers, spectators, head positions, component formats, normalization, native/root/ordinary refinement and complete physical invoice remain unproved. None is assigned zero cost.

## Evidence and its limits

RESULT.json is generated by independent integer exponent evaluation and the executed tape engine. checks.invoice derives the formula above without reading the machine counters. Every finite case checks exact primitive and allocation counts, all returned heads, borrowed restoration and wire blankness. The generic truth tables cover constant operands, repeated operands and a gate reading an earlier result. Small synthetic cases exhaust every address when A<=6; larger small shapes use four declared addresses. Wide cases extend through ell=48. The finite evidence corroborates the algorithm; the preceding induction proves the unbounded statement.

Actual optimized CLI controls change arithmetic, counted moves, private erasure and borrowed program rewind, then alter/remove a pinned source and alter the committed receipt. Each must fail with its intended diagnostic, followed by a valid retry. These mutants demonstrate check sensitivity and do not identify a defect in the predecessor circuit or selected construction.
