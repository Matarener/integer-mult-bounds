# Packed exact dyadic transpose endpoints

This contribution was produced by Nick Petalas. Apache-2.0.

The claim is an exact alternative implementation of a linear endpoint
checkpoint. It is not a new proof of the selected construction. Classical
Kronecker substitution supplies the integer evaluation method. The bounded
dyadic planning pass and its application to the retained checkpoint are the
new implementation.

## Contract

There are n roles. Initially the coefficient matrix is I_n. In chronological
order, ADD replaces row r by row r + q row s; COPY overwrites row r by
q row s; SCALE multiplies row r by q; INIT and CLEAR replace row r by zero.
Here q is dyadic. The requested endpoint is the transpose of this matrix,
with every one of its n squared entries specified. This treats INIT and CLEAR
as their linear maps only. Allocation, erasure legality, frames, native
operators and all non-linear semantics require the surrounding checks.

Transposition reverses chronology. A transposed ADD adds q times row r to
row s. A transposed COPY does that addition and then zeros row r. Transposed
SCALE, INIT and CLEAR have their original row action. The dense source
checkpoint implements precisely these operations. MOVE is the identity
in this scalar projection and remains checked by the surrounding source
verifier. This backend does not replace that verifier.

## Numerators and bounds

Represent a row as c/2^e, with integral coefficient vector c and e >= 0.
For q = p/2^d an ADD to s uses level L = max(e_s,e_r+d) and numerator

    2^(L-e_s) c_s + p 2^(L-e_r-d) c_r.

SCALE replaces c_r by p c_r and e_r by e_r+d. Resetting a row sets c=0,e=0.
There is no cancellation-based denominator normalization.

A first pass replaces each numerator row by an upper bound on its l1 norm.
It starts at one and performs exactly these updates with |p| and addition
of the nonnegative bounds. The triangle inequality proves its bound at
every event. It includes rows later discarded by COPY, INIT or CLEAR, so
the bound also controls all intermediate integer lengths. Parsing enforces
role, event, coefficient, exponent, growth and packed-storage limits before
the packed pass begins.

At each endpoint row, align its numerator and its requested dyadic row to
one exponent. The sum of their l1 bounds bounds the l1 norm of their
difference. Let M be the maximum of these difference bounds and all
intermediate bounds, at least one. The implementation chooses

    b = bit_length(M) + 1, B = 2^b.

Thus B > 2M. It also checks the fixed resource limit n squared times b.

## Injectivity

Encode an integer row c by E(c) = sum_j c_j B^j, allowing negative digits.
Encoding commutes exactly with every integer sum, shift and multiplication
above. Intermediate radix carries do not alter this identity. No digitwise
division, parity test on the packed integer, modular reduction, truncation
or machine-width arithmetic is used.

If a nonzero endpoint difference d satisfies E(d)=0, take its least index k
with d_k nonzero. Dividing by B^k and reducing modulo B gives d_k=0 mod B.
But |d_k| <= ||d||_1 <= M < B, a contradiction. Hence encoded equality is
equivalent to equality of every endpoint coefficient. The larger choice
B>2M is conservative. A single evaluation here is deterministic exact
arithmetic, not a probabilistic polynomial fingerprint.

The independent finite oracle instead executes chronological Fraction
matrices and explicitly transposes them. It checks all coefficients of
every stated small word, including overwrites, negative coefficients,
different denominators and zero rows. Incorrect endpoints and an explicit
unsafe-radix collision are rejection controls. The complete retained word
is a workload and source-syntax compatibility test, without repeating its
native, caller, compiler or exponent claims.

## Scope and resources

This implementation is bounded to 1024 roles, 60000 scalar events,
numerators below 2^20, denominator exponents at most 32 per coefficient,
4096 bits of planned growth and 128000000 packed coefficient bits. It
rejects instances beyond those bounds. At most n packed rows and a bounded
number of temporary packed arithmetic integers are live in the second pass. The
128000000-bit bound is 16 MB of coefficient payload, not a byte-exact heap
or RSS claim. Parsed events, Python objects and interpreter allocations are
additional bounded storage. No fixed-allocation native runtime is claimed.

Power of Ten rule 3 has a managed-runtime deviation in packed.py, verify.py
and benchmark.py. CPython allocates arbitrary-precision integers and
containers during execution. Fixed input and growth limits, bounded fixture
counts and sequential benchmark processes control their size and lifetime.
Library allocation internals are not inspected. A fixed-pool implementation
would be required for a fixed-allocation runtime claim. Rules 8 and 9 use
ordinary Python functions and bounded standard-library dispatch. Benchmark
dispatch has exactly two targets. Warning-strict ordinary and optimized
execution and available static diagnostics check the new files. All new
functions fit within 60 physical lines.
