# Exact normalization cost of a Pauli skew pairing

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof and explicit circuit, with exact finite
corroboration. A three-bank operator pairing can be normalized with exactly
**four cross-bank additions and one bank halving**, with no workspace. Neither
count can be reduced even with any finite restored clean or dirty workspace,
in the gate model below. No new kappa or actual productive helper split is claimed.

The classical odd-skew example already separates commutative and
noncommutative rank. The new contribution here is the specified Pauli circuit,
its matching resource lower bounds, and the resulting concrete test for a
changed helper interface. This is not a new noncommutative-rank theorem.

## Pairing and gate model

Let D=Z[1/2], N=2^n with n>=1, and let X,Z be real signed Pauli operators
on D^N satisfying X^2=Z^2=I and XZ=-ZX. For example, for binary address a,
X translates one address bit and Z changes sign on that bit. Write J=XZ.
The three input banks are arbitrary and independent, including every address
coordinate. Define

```text
          [  0   I   X ]
y = K x,  [ -I   0   Z ].
          [ -X  -Z   0 ]
```

One cross-bank addition changes one destination bank by adding a signed Pauli
image of one other bank. One bank halving multiplies all N coordinates of one
bank by 1/2. Doubling is also permitted and counted separately. Unary signed
coordinate permutations within one bank, and permutations of whole banks,
are allowed. Their physical cost is outside the two resource counts. No free
operation splits a bank or mixes coordinates of different banks. No dyadic
coefficient such as 1/2 is hidden in a cross-bank addition. Workspace, if used,
starts either at zero or with independent arbitrary dirt and must be restored.

Thus this is a tariff for an explicitly stronger operation alphabet than the
scalar helper bases of PR #5615. It does not declare a Pauli-weighted addition
free or legal at any particular physical frame.

## Inverse and attaining circuit

The inverse has nine nonzero blocks:

```text
             [ -J  -I  -X ]
K^-1 = (1/2) [  I  -J  -Z ].
             [  X   Z   J ]
```

Here is the literal in-place circuit on banks a=y1, b=y2, c=y3:

```text
c <- c + Z a
c <- c - X b
c <- J c
c <- c / 2
a <- a - X c
b <- b - Z c
swap banks a,b
a <- -a
```

Only four lines add between banks. There is one halving, one within-bank J,
one bank swap and one bank negation. These last three operations are explicit;
the two resource counts do not price their implementation. The circuit leaves
(a,b,c)=(x1,x2,x3), with no auxiliary bank.

To prove it, the forward equations are y1=x2+Xx3, y2=-x1+Zx3 and
y3=-Xx1-Zx2. They give

```text
y3 + Z y1 - X y2 = (ZX-XZ)x3 = -2J x3.
```

Since J^2=-I, multiplication by J/2 recovers x3. The next additions give
x2 and -x1, and the swap and negation finish. Substitution gives the displayed
inverse on all inputs. The same identities prove both left and right inverse
relations over D. In particular all three operator channels can be normalized.

For commuting scalars u,v over Q, the same pattern
`[[0,1,u],[-1,0,v],[-u,-v,0]]` has determinant zero and rank exactly two.
Its first two rows and columns already contain an invertible minor. This is a
comparison between operation alphabets, not an extension of a scalar cut's
capacity or evidence that an actual helper split exists.

## Matching lower bounds

Track which of the three original input banks can affect each live bank.
Initially each input bank has one such source and each workspace bank has
none. Unary operations and whole-bank permutations cannot merge these source
sets. A cross-bank addition changes at most one set, to a subset of the union
of its old set and the source set.

After the first addition no bank can depend on all three inputs. After the
second at most one bank can do so, and after the third at most two can do so.
But each of the three required output banks of K^-1 depends on all three
inputs, as its nine blocks are nonzero. Therefore at least four additions are
necessary. This argument allows any finite workspace and even arbitrary unary
linear maps that do not mix banks. Cancellations cannot exceed the union bound.

Without a bank halving, every permitted operation has integer entries, including
doublings and all Pauli additions. Starting workspace at zero or arbitrary
independent integer values then produces integer outputs. K^-1 has entries
+/-1/2 because every block in its numerator is a signed permutation. Its value
on a suitable integer basis input is nonintegral. At least one bank halving is
therefore necessary, regardless of workspace. This proof also covers clean
workspace; it does not rely on a determinant argument about unobserved clean
coordinates.

The circuit attains both lower bounds simultaneously. Consequently its cost is
exactly 4A+H for any nonnegative addition price A and halving price H, when the
listed unary relabelings are granted and only these two resources are priced.
There is no claim that 4A+H is the complete physical cost.

## Evidence and reproduction

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pauli-skew-pairing-normalizer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/pauli-skew-pairing-normalizer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pauli-skew-pairing-normalizer
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pauli-skew-pairing-normalizer --check-source-history
```

An equivalent CPython 3.12 path can replace the local path. The scientific
marker is `PASS_PAULI_SKEW_PAIRING_NORMALIZER`. The registered hook runs normal
and optimized modes. Local execution used CPython 3.12.15 on macOS arm64;
the two checks took 2.59 and 2.98 seconds. These are replay durations, not a
speedup claim. The verifier imports no predecessor program, uses no Git
or network, writes no files, and generates a stdout receipt bound to all five
package files by SHA256. No receipt is handwritten.

The verifier enumerates every pair of nonzero binary labels a,b with a dot b=1,
and both signs, for widths 1,2,3. Its 140 cases use X as translation by a and Z
as the character b. All 3,000 input basis columns pass the literal circuit and
an independently assembled closed inverse, as well as both dense inverse
identities. These are the specified translation/character families, not every
signed Pauli pair in those dimensions. The universal theorem rests on the
written involution and anticommutation argument.

It also checks 81 scalar specializations u,v in {-4,...,4}, all support-union
states through three additions with 3,4,5,6 banks, and nine rejecting controls.
The controls cover commuting or invalid labels, a bad sign, capacity overruns,
a missing addition, reversed J order, an omitted halving and an omitted swap.
An unexpected command-line argument is rejected. Support states are optimistic
unions; they certify an upper bound on dependencies, not realizability of every
state. Workspace beyond six banks is covered by the written proof.

## Source, credit and limits

The odd-skew rank phenomenon is classical. See Example 1.3 of Ankit Garg,
Leonid Gurvits, Rafael Oliveira and Avi Wigderson,
[A deterministic polynomial time algorithm for non-commutative rational identity testing](https://www.ias.edu/sites/default/files/math/csdm/15-16/GargGuOlWi2015.pdf),
arXiv:1511.03730. The pattern above is an equivalent relabeling of that example.
No priority is claimed for the rank separation, elementary elimination, Pauli
anticommutation, or support and integrality methods.

Ali Romman's [PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the scalar dyadic helper-pairing context and retains the PR #5599,
#5602, #5609, #5611 and earlier P104 lineage. Those results are cited, not
replayed or audited. The exact README is pinned as historical provenance in
SOURCES.json, not imported as an executable or live mathematical input.

Canonical base is 19fdb086ea96af9a9f87936a2b888e10af4ed810, priority revision 8.
The selected baseline binding check passed; it was not a selected operator
replay. The investigation changes the coverage-law card's scope to a local
operator-valued interface. The binding complex problem motivates testing a
coefficient algebra richer than scalar dyadics. This circuit does not supply
causal prefix/suffix modules, actual cut carriers, frame compatibility, legal
native delivery, arbitrary-dirt restoration in a surrounding word, a complete
signed invoice, compiler closure, precision or tape bounds. No physical supplier,
selected-frontier change or complete multiplication theorem follows. Full
selected replay, Lean and Docker were not run. Independent human and formal
proof-kernel review are unclaimed.

The code uses explicit exceptions under both optimization modes. Loops have
fixed capacities: address width at most three, matrices at most 24 square,
140 Pauli fixtures, three support-update rounds and at most six support banks.
Functions stay below 60 lines. No recursion, subprocesses or dynamic imports
are used. CPython's dynamic allocation in verify.py is a Power of Ten rule 3
deviation, confined to the bounded read-only replay. Fixed matrix sizes and
the enforced 8^6 support-state ceiling bound live data. The registered checks
exercise these bounds and the capacity controls. A fixed-capacity native port
would be required before using this verifier in a long-lived runtime. Static
syntax, indentation and function-size checks supplement warning-strict
execution. No external Python linter is installed in the local environment.

## Open next questions

1. Can an actual causal helper cut realize this operator-valued pairing while
   preserving every independent dirty input? Start by publishing its prefix,
   suffix and legal physical charts, then derive K in the displayed order.
   The present abstract matrix is not a construction of those modules.
2. Can a consumer pay for all four Pauli additions, the halving and unary
   relabelings while retaining a positive complete signed moment? Price their
   physical delivery and target debits before searching for a larger example.
   Actual native alignment, ownership, precision and tape costs are unknown.
