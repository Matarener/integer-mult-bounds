# Eight endpoint caches do not supply the coupled-query observer

All eight actual raw-PR5402 partial-frame endpoint caches, together with every
retained full-frame native value, still cannot determine the consumer's
`b=ZQY_return=ZRy` on arbitrary independent original inputs. An exact 104-role
input displacement leaves the entire enlarged channel unchanged but changes
mode one of b by an invertible map of an arbitrary whole field. This is an
all-positive-width information obstruction, with no new kappa or physical
price lower bound.

The result closes the endpoint-cache case explicitly excluded by
[PR5447](https://github.com/CrocSwap/integer-mult-bounds/pull/5447). Its old
fixed-helper kernel is not reused: each of the eight caches defeats one such
old kernel direction. The new witness changes 57 X inputs, three Y inputs
and 44 dirty helper inputs; all nine initial owned inputs stay fixed.

[PROOF.md](PROOF.md) states the exact channel and the uniform implication.
[KERNEL.json](KERNEL.json) supplies every displacement coefficient.
[RESULT.json](RESULT.json) records the complete source-bound check:

- 21,473 source records, 5,897 full-frame touches and 4,891 distinct nonzero
  full-frame observations, including all versions after intended exits.
- All eight nonzero rank-eight endpoint caches included at their actual slots
  and frames; arbitrary initial owned dirt is represented and cleared.
- Exact `M^T delta Y=(0,-4,0,0,0,0,0,0)` and all 112 input-Y wrapper phase
  bindings. The actual observer changes by `-2 K_m,1^-1 R v` in mode one.
- Original helper retraction changes by the same raw target vector, hiding it
  in the caches. The corresponding **post-word** helper retraction is exactly
  zero on every input, so it is not an interchangeable observation.
- Freezing helper displacements or removing X compensation exposes the
  source histories; eight controls show each added cache supplies genuinely
  new information relative to the earlier full-frame channel.

The primary engine tracks all 641 independent input columns in the free-word
algebra and checks every coefficient. The separate direct-displacement engine
imports none of its parser or row code and checks every full-frame event,
storing chronological words in the opposite order. Both inherit the pinned
normalized native semantics. This separation is not independent human review
or a new physical proof of the native instructions.

## Reproduce and source contract

```sh
python3.12 -B scripts/research_package.py --package research/partial-cache-history-observer
python3.12 -B scripts/check_research_commit.py --package research/partial-cache-history-observer --check-source-history
```

Direct normal and optimized commands use only the standard library:

```sh
python3.12 -I -B research/partial-cache-history-observer/verify.py
python3.12 -I -O -B research/partial-cache-history-observer/verify.py
python3.12 -I -B research/partial-cache-history-observer/check_displacement.py
python3.12 -I -O -B research/partial-cache-history-observer/check_displacement.py
python3.12 -I -B research/partial-cache-history-observer/test_package.py
```

Six disposable on-disk controls reject a changed Y coefficient, a vacuous
kernel, changed input bytes, a missing receipt, a Boolean changed to integer
one, and a wrong event count. Kernel/source controls bypass stored-receipt
comparison; all child checks run under optimization. Typed canonical JSON
comparison prevents Python Boolean/integer equality from authenticating an
altered receipt.

Four actual JSON/gzip inputs are declared in VERIFY.json and authenticated by
SOURCES.json. The official exporter includes them at their exact paths; no
`--input-ref` is needed because all use the canonical base source bytes.
Direct replay from that export needs no Git or remote object. The older proof
and checker paths are provenance-only references, not runtime imports; the
external PR5447 citation is not a pending Git-object dependency. Source-history
preflight checks the declared canonical pins, not the truth of external prose.

Sparse rational elimination discovered the witness. The certificate and
replay do not depend on that search, a modular rank, actual monomial
independence or a numerical tensor cutoff. Coefficientwise free-word
cancellation proves the invariant after any consistent all-width native
assignment. The primary representation has 119,521 terms; PR5447's actual
monomial canonicalization has 119,515. They are deliberately not identified
as the same representation or count.

## Meaning of the negative result

The whole machine is not claimed to hide Y. Lower-frame main values, other
partial-frame histories, original helper observations, changed words and extra
paid responses give different information. Physical entrance bases and chart
maps are invertible, so the raw witness corresponds to legal independent
physical inputs; no free physical preparation is asserted. Actual normalizers
and their R-commutation are retained source premises, with input-Y equality
checked here including phase.

If the original eight retractions `E h_original` were supplied, the exact
cache formula would recover `M^T Y` and yield an unrestricted linear decoder
for b. That conditional observation is not available from the post-word
retraction, and its retention, frame transforms and Gaussian action have not
been priced. No decoder, observer job, new return credit, complete supplier
bill, finite-precision guarantee or selected-frontier change is claimed.

[Discussion5488](https://github.com/CrocSwap/integer-mult-bounds/discussions/5488)
is the canonical investigation. The base is
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision seven.
The changed task scope and overlap coverage are recorded in TASK.json.
PR5489's parallel local helper-transport contract concerns another fixed block
and role, not this complete-history/cache channel.

## Open next questions

Identify one actual correctly versioned source for original helper modes or
another useful partial-frame observation, then test the explicit witness at
that cut and charge its ownership, retention, transforms and cleanup. Merely
postprocessing this unchanged enlarged channel cannot resolve the ambiguity.
TASK.json gives the concrete first steps and missing contracts.

## Credit

Dillon Amburgey / dillona's PR5402 supplies the provider and its native row
semantics; Ali Romman supplies the cache/retraction/basis lineage;
Mark/Matarener's PR5427 and THU New Media Research Center's PR5447 supply the
history question and earlier kernel; zxv's PR5415/5419 supplies the actual
consumer and observer interface. Cao Yifan, Cinna Davis, Dugongue, Chris R,
Jacob Alan Sussman and the retained native/phase/compiler/analytic contributors
retain their credit and notices. The literal monomial evaluator adapts zxv's
canonical consumer checker, with attribution in the source.

JoyboyBrian with substantial OpenAI Codex assistance in source inspection,
witness discovery, proof, implementation, controls and writing. Apache-2.0.
No independent human or formal-kernel acceptance is claimed.
