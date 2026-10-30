# Source coefficient preparation and complete physical consumption

The exact source histogram in PR5820 contains the fourteen rational coefficients
in RESULT.json. Multiplication by4 gives fixed integers k in[-16,16]. A later-
target shear over odd Q therefore needs c=k*4^-1 mod Q and the positive binary
descriptor c+1. This is a permutation for every c, including zero and nonunits.
The source runtime-affine proof does not require c to be invertible.

## Retained arithmetic with the complete source envelope

For Q>=17, choose t in{0,1,2,3} with k+tQ divisible by4. If t=0 and k<0,
use t=4. Since abs(k)<=16<Q, the integer (k+tQ)/4 lies in[0,Q), and

    c+1 = (k+tQ+4)/4.

The retained finite transducer reads Q's low bits and canonical ending, then
multiplies its bits by fixed t with signed carry initially k+4. Each bit emits
the low bit of t*b+carry and changes carry to its integer half. These are finite
compile-time states, not runtime arithmetic instructions. The first two bits
are zero and are checked/dropped. The machine flushes its nonnegative final
carry, trims high zero bits, writes the marker and returns both heads. The
predecessor proof supplies this method. The new envelope uses five low prefix
bits and threshold17; smaller odd Q=3..15 have exact compiler-generated outputs.
Q=1 has a separate literal branch which emits1, the descriptor of its sole
residue0. These statements cover every odd Q, not only prime powers.

The two-token interface of the predecessor uses five symbols and explicit next
states on writes/moves. The compiler maps its source to tape5 and destination
to tape14 and maps blank,0,1,END,LEFT to the retained seven-symbol alphabet.
A branch stays one branch. A write or move becomes the same local instruction
followed by one fixed goto. Terminal states keep their meaning. The wrapper
checks odd Q and a blank owned destination, handles Q=1, and positions the
legacy destination at its declared first bit. Induction on original steps
proves identical cells and heads at every translated state boundary. No jump
computes a runtime address, and every physical move has length one.

## Paid leaf and original owner

The nineteen-tape bank supplies only the complete source stream and canonical
P,Q,G,S extent descriptors. Coefficient tape14 and offset tape16 are owned
blank inputs. A fixed local program writes offset+1=1. The descriptor producer
writes c+1 from Q. PR5842's completed in-place affine kernel then performs the
full later-target shear, with either compile-time orientation, into the original
physical owner. Literal scans erase both owned descriptors and markers and
return their heads to the original blank origins. All other private tapes
already return by the affine proof. Tape1 remains arbitrary and untouched.
There is no extra clean output bank, free owner rename or runtime inverse.

## Uniform physical bill

Let n=bit_length(Q). For the translated descriptor, a direct local-instruction
ledger has the following conservative bounds. The general branch scans n bits
at three transitions each, returns through at most n+2 positions at three each,
and multiplies each bit in at most seven transitions. It flushes at most three
carry bits, each with one write/goto and one move/goto. The output has at most
n+1 provisional bits. Trimming uses at most five transitions per discarded bit;
the final two returns use at most6n+12. Wrapper, initial marker, flush and final
markers contribute fewer than128 transitions. The sum is below64n+128.
The small-Q and Q=1 branches are shorter. The literal checker tests this bound
on every executed descriptor; the loop ledger proves it for unbounded n.

The coefficient eraser costs at most8n+8. The fixed zero-offset producer and
eraser together cost less than40. Thus all added producer/cleanup work costs
at most72n+176. For Q>=3, n<=Q and176<=59Q, so this is at most131Q<=44Q^2<=44V.
For Q=1 the explicit producer and both descriptor erasers cost at most100;
there is no general transducer pass. The retained affine proof's detailed
ledger is802V, and the original-owner version saves three transitions.
Consequently the complete leaf costs at most846V for Q>=3 and at most902V
for Q=1, both within the declared1024V allowance. Linking replaces halts by
fixed gotos, each of cost one, so no boundary transition is omitted.

The retained detailed space ledger is at most56V, including input descriptors,
all private counters, erased buckets and markers. Only the coefficient producer
can reach beyond those intervals: its provisional output visits at most n+4
cells. This is at most Q+4<=5Q<=5V. All Q input positions and the fixed offset
interval are already in the retained ledger. Total visited space is at most61V,
inside64V. Translated origins do not change interval sizes. These bounds include
cleared cells; a blank initial private tape remains an explicit valid-input premise.

## Complete source scope and evidence

The accepted coefficient set is reconstructed from all three frozen ADD
histograms, not a hand-picked list. Fourteen producers and28 complete leaves
are retained. The source explicit-edge interpreter and the new sparse/dense
literal interpreters agree on descriptors, including long carry chains and
large moduli. Full leaves are checked by a coordinate gather oracle, complete
owner/descriptor/private/head checks, exact physical meters and inverse pairs.
The Q1 smallest-volume fixtures prevent setup from being hidden in a large
payload. Actual Q125 complete pair fibers execute both missing fractions.
Finite cases support the written proof; they are not an all-size proof alone.

An actual G20 caller must still supply the declared later-target stream and
P,Q,G,S descriptors, low cache and type/carry actions. Earlier-target movement,
physical ROW heads, padding, borrowed return and the final full invoice are not
supplied here. No native, compiler, precision/tape, owned-erasure or analytic
framework assumption is discharged, and no new kappa is claimed.
