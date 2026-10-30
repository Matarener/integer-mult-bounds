# The eight-port REL floor survives ambient frames

The fixed eight-port REL model of [PR6229](https://github.com/CrocSwap/integer-mult-bounds/pull/6229)
still has exact minimum paid cost eight when gathering and landing frames may
leave the source span. This closes that source's explicit outside-reaching
question, retaining its local-source, chronological arrival and receiver rules.

For every move, replace `g,L` by `g intersect W,L intersect W`, where W is the
span of the eight source labels. Every local source remains available, every
permitted parent and receiver remains permitted, and the same coefficients
produce exactly the same vectors and complete endpoint. The induced quotient
map is injective, so each dimension gap weakly decreases. The contracted network
can contain zero-gap steps. [PROOF.md](PROOF.md) extends Nick Petalas's cumulative
debt invariant to these steps explicitly; it does not apply a strict-descent
theorem without checking that hypothesis.

The result is a written scoped proof for every finite REL network with this
source contract. Finite geometry and network fixtures provide discriminating
controls, not an exhaustive enumeration of networks or a formal proof.

## Evidence and reproduction

Run from the repository root with CPython 3.12:

```sh
python3.12 scripts/research_package.py --package research/p104-ambient-relay-floor --check-only
python3.12 scripts/research_package.py --package research/p104-ambient-relay-floor
python3 -B scripts/check_research_commit.py --package research/p104-ambient-relay-floor --check-source-history
```

The registered commands run the same bounded exact checks normally and with
`-O`. [CERTIFICATE.json](CERTIFICATE.json) records the finite result;
[VALIDATION.md](VALIDATION.md) records the executed environment and acceptance
boundary. The unchanged predecessor `model.py` is vendored once, authenticated
against its source pin, and used for elementary exact operations. New ambient
validation and the non-strict cumulative checker are separate code.

Source pins bind PR6229 head `50540b2a7e0d219bc4920e6252e75113b5a9d8d8`,
PR6170's retained REL question and the PR5599 port definition. The scientific
base is canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision8, selected #6030. A local ancestry-only merge retains the pending
PR6229 source commit for cold-clone provenance checks; its tree is not imported.
The diff from main adds only this package. No upstream PR is merged or closed.

The canonical [claim and finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19284373)
records live overlap, scope and publication. See [TASK.json](TASK.json) for the
frozen card and its changed scope: this is a relaxation obstruction, not a new
helper split or an improved complete invoice.

## Limits

The eight independent local sources and the REL availability predicates are
essential. A network with additional local sources or a changed arrival rule
is outside this statement. The proof does not justify adding eight for each
block of a larger network when paid moves are shared across blocks. REL grants
free public transport, re-ascents and rational scalar work; an attaining REL
network supplies no native synthesis, owned restoration, physical cost invoice,
supplier admission, multiplication theorem or change to the selected frontier.
No independent human or proof-kernel acceptance is claimed.

## Open next questions

1. Specify a broader source/arrival contract before asking whether outside
   sources change the block bill. Start with the complete source set and
   endpoint; shared-cost accounting is the unresolved prerequisite.
2. Bind an attainer to legal native P104 entry and exit frames, including
   ownership, restoration and delivery. A favorable complete invoice is needed
   before implementation expansion.

These questions, relevance and first steps are also in [TASK.json](TASK.json).

## Attribution

Prepared by AAAmirinu with substantial OpenAI Codex assistance, including
parallel proof and checker work and a separate AI review. Apache-2.0.
Nick Petalas's PR6229 supplies the confined cumulative proof and unchanged
exact helpers. DreamingOfClouds's PR6170 defines the REL question; Ali Romman's
PR5599 supplies the retained port labels. Credit Matarener and the retained
P104/native/helper/controller/caller lineage. Intersection, quotient injection
and rank arguments are classical linear algebra. The new contribution is their
source-contract reduction of the stated outside-reaching case, with an explicit
zero-gap extension and bounded controls.
