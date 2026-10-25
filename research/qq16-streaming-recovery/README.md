# Stream complete QQ16 recovery inside nine existing output banks

This preserves all 224 original F17 outputs and PR3985's 224-H1 native bill
while requiring **zero additional owned banks**. Eight persistent full-cover
query sums and one reusable work bank fit into nine existing Z_U output banks
whose initial definitions are explicitly deferred. Every borrowed current X/Y
field remains unchanged, and every output bank has the required final value.

The complete bill is **224 H1, 448 native wrappers, 352 cover maps and 26,944
scalar allowance**. Compared with PR3985, it removes all 112 additional owned
banks and 120 CLEARs, saving 240 scalar allowance. Native work and ADD counts
are unchanged. Whole-word private scratch peak remains 16; the changed future
block uses persistent full-cover banks, with no owner-private body. No tape
count or κ improvement is claimed.

[PROOF.md](PROOF.md) derives the standalone nine-bank stream, then proves the
nine-output deferral and paid restoration. `WORD.json` is the complete hosted
3,813-event word; `RESULT.json` contains both invoices, exact lifetimes and
full verification receipt. The standalone nine-external-bank reference is
also regenerated and replayed, with its zero/identity-return contract.

The hosted block, including moved output definitions, has 698 scalar passes:
1138N scalar reads and 698N scalar writes for N entries. Its prefix loses 18
passes and 18N reads/writes. Native/map/wrapper traffic, physical placement,
head movement, bit precision, outer coverage and both supplier caps remain open.

## Reproduce

```sh
python3 -I -Werror -B research/qq16-streaming-recovery/verify.py
python3 -I -O -Werror -B research/qq16-streaming-recovery/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-streaming-recovery
```

Python 3.12, standard library. Normal verification is read-only; `--write`
refuses to overwrite artifacts. Canonical runtime files are authenticated
before execution. The narrowly retained PR3985 word is data, not an unmerged
executable dependency. PREDECESSORS.json records its exact head, path, blob and
hash; all source/history and replay scopes remain explicit.

## Scope and next questions

This is the assigned streaming-linear-algebra and pebbling branch of the
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/pull/3985#issuecomment-6263114494),
from main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
It changes the intermediate ownership/access contract and removes an actual
storage obligation. One bounded composition reuses the independent parallel
output-lifetime insight; all nine source def-use conditions and full output
restoration are verified here without a sibling executable dependency.

PR2722/2794 concern scratch placement and sweep directions for different fixed
words. Parallel materialized-copy output hosting and reversible borrowed-scratch
work have separate schedules. This stream defers nine output definitions and
retains full-cover query sums across native calls. Targeted overlap checks and
the shared repository helper have partial coverage; no exhaustive novelty claim.

## Open next questions

The bounded next questions in [PROOF.md](PROOF.md#open-next-questions) and
TASK.json are actual caller output-bank ownership, a complete movement tariff,
and changed numerical-error bounds once the complete budget permits further work.

## Credit

Retain ywz65 / PR2707, Arham Tahir / PR2681, the credited QQ16/native/geometry
lineage, and PR3985's rectangular correction. Credit the parallel output-lifetime
agent's insight and the coordinating agent's composition proposal. Nick Petalas
/ PR2722 and Arham Tahir / PR2794 provide distinct access precedents. New work by
Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0;
no human or formal-kernel verification claim.
