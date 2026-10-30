# Exact first-decomposition preservation

Consider a finite sequence of additions on independent input basis supports.
Node 0 has empty support. Input node `j+1` has support `{j}`. A valid addition
has two previously allocated node IDs whose supports are disjoint. The original
rule returns either operand when the other is zero. Otherwise it returns the
first node with the union support, or appends a node with that support and
the ordered argument pair. Assume the declared capacity is not exceeded.

Choose arbitrary bit strings `h_j` of one fixed width, including width zero.
For a support `S`, define `h(S)` as the XOR of `h_j` for `j in S`. Disjointness
gives `h(A union B) = h(A) XOR h(B)`. This identity requires no randomness and
no injectivity assumption.

Maintain a bucket for each key, containing exactly the allocated node IDs with
that key. Initialization establishes this invariant. On an addition, the new
rule computes the full union support and its XOR key. A prior node with equal
support necessarily has that key and is in that bucket. The bucket search
compares full supports, so it finds that node. If there is no equal support,
it appends the new node and inserts its ID into the bucket. Colliding unequal
supports therefore cause extra comparisons, never a false match or a missed
equal support.

Induct on the addition sequence. Both rules initially have the same supports
and node IDs. The zero cases return the same ID. In every other case the bucket
argument proves that the same existing node is returned or that the same new
node is appended. An existing node's arguments are never replaced; a new
node records the same ordered pair. Thus the complete support and argument
sequences are equal after every call. Any deterministic caller receiving those
IDs follows the same subsequent branches and obtains the same output IDs,
traversal and pruning.

The frozen mixed-point caller accesses the interning table only during
initialization, addition and the paired-kernel handoff. The two adapters change
the first two sites and carry the key array together with the table at the
handoff. `verify.py` checks the entire adapted source against those exact
changes. The proof applies to its valid addition sequences. The unchanged
builder's mathematical identity is a predecessor dependency, not a new claim.

The new overlap guard rejects invalid, nondisjoint additions before any write,
including under `-O`. Input-shape and capacity guards also fail before a write.
The node-capacity guard acts only when an actual new node would be needed;
an already interned support remains usable at capacity. This does not promise
identical failure behavior to the old assertion-based rule outside valid input.

There are at most 25,000 input coordinates and 4,000,000 stored nodes. Each
bucket contains at most the current node count. Each stored support has at most
25,000 bits, and each key has at most 64 bits. In the absence of collisions,
the key lookup uses fixed-width integers. Complete support union, disjointness
and equality still use the original bitmasks. No worst-case asymptotic speedup
is claimed: all keys may collide, and then the bucket scan is linear in its
size. Correctness is unconditional on collision frequency.
