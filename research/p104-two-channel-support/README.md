# Two independent P104 root-code channels need 72 ports

The exact second generalized support weight of the specified P104 root code
is **72**, both over F3 and over Q. There are **704** minimizing ternary
two-dimensional subcodes. This is a finite certificate with a scoped proof;
no new kappa or cheaper physical word is claimed.

Matarener's [PR6166](https://github.com/CrocSwap/integer-mult-bounds/pull/6166)
identifies the ternary code and proves its single-channel minimum 49. The
new quantity is the minimum union of supports of two independent channels.
An explicit independent pair attains 72. The full 5,377,560 projective-pair
census proves the lower bound. [PROOF.md](PROOF.md) gives the coverage
argument and lifts the result to rational coefficients by a minor argument.
The predecessor theorem is cited, not independently validated here.

The shared-frame consequence is narrow but useful. With PR6166's cited
binary hyperplane capacity 60, a common acquisition frame for two such
independent channels must be FULL. A common landing frame for two independent
receiver columns satisfying the same code hypothesis must be ZERO. These
are constraints on synchronized sharing; they do not exclude separately
scheduled carriers, relays or larger partner codes.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-two-channel-support/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-two-channel-support
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-two-channel-support --check-source-history
```

Use any CPython 3.12 interpreter in place of the local path. Both registered
normal and optimized commands must print
`PASS_P104_TWO_CHANNEL_SUPPORT d2=72 pairs=5377560 minimizing_subcodes=704`.
The runner must print `PASS_REGISTERED_RESEARCH_PACKAGE`.

Normal replay only reads files. The generated [RESULT.json](RESULT.json)
binds all seven proof/input/metadata files by SHA256 and records the complete
support histogram, census counts and rational/ternary witness. To regenerate
it explicitly, pass `--emit-receipt /path/to/RESULT.json`. A changed receipt
is rejected, including under optimized Python.

## Source and scope

`PORTS.json` retains the exact coordinate bytes from PR6166 at
`096938513138868f0ed27639061f1a5054900f96`. Its URL, SHA256 and source role are
in [SOURCES.json](SOURCES.json). That open PR head is external to this
publication's ancestry; the generic source-history check covers the canonical
catalogue and selected record, not the external head. The direct verifier
checks the retained coordinate bytes against their recorded hash and derives
all code entries locally. No predecessor executable or proof is copied.

Base `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision 8.
The selected source-binding baseline passed. The selected conditional
κ = 0.003125804 is unchanged. Main, merged-PR, live open-PR and Discussion
searches found no same-question result; these bounded searches do not prove
novelty. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267579)
states the ternary target. The same certificate also supplies the rational
lift, without another search.

All loops have fixed bounds: 104 ports, nine root coordinates, eight
coefficient coordinates, 6561 coefficient tuples, 3280 projective words and
5,377,560 pairs. Minimizer storage is at most the finite pair count and in
this certificate holds 4224 pairs. Each function is under 60 lines. Checks
use explicit exceptions and remain active under `-O`. CPython and Fraction
allocate dynamically; this is a documented Power of Ten rule 3 deviation
bounded by these fixed census sizes and input dimensions. There is no
recursion, network, subprocess, dynamic code execution or normal replay write.
Warning-strict normal and optimized replay provide the recurring diagnostics.

Limitations are mathematical as well as practical. This is not a theorem
about arbitrary nine-dimensional decoding codes or asynchronous relay
programs. Complete native, caller, restoration, stock/precision, compiler and
outer costs remain open and are not assigned zero. No Lean, selected-native
or complete multiplication replay is run. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

- Can an asynchronous relay use distinct acquisition and delivery cuts to
  avoid the common-frame constraint and improve a complete invoice? Start
  with two explicit independent channel rows and pay for every transition
  and restoration in an actual caller. That caller and its invoice are missing.
- What joint-support bound holds for a specified nine-dimensional decoding
  code outside the minimal-code reduction? First exhibit the code and two
  delivered channels. Its decoding and physical delivery contracts remain
  blockers. No larger-code census is included here.

[TASK.json](TASK.json) records the same questions and scope change.

## Credit

This contribution was produced by Nick Petalas. Credit Matarener PR6166 for
the decoding-code identification, source coordinates, single-channel result
and cited frame capacity; Ali Romman PR5827 and DreamingOfClouds PR5907/6030
for the retained local-word lineage; and their E8, native, helper, controller
and compiler predecessors. Generalized Hamming weights and rank reduction
by minors are standard. The new contribution is this exact joint-support
certificate, rational lift and scoped common-frame consequence. Apache-2.0.
