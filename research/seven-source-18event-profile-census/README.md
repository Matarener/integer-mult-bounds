# Exact 18-event profile census and (6,2,2,2,2,2,2) exclusion

Resolves Open Question #1 of `research/seven-source-18event-connector` (PR #2397): no seven-source word of profile `(m_0,2,2,2,2,2,2)` for any even `m_0 >= 2` can exceed 61/63 weight-<=3 masks (since the 10,395-word six-source 12-event projection reaches at most 39/41, attained by 2 words). For `(6,2,2,2,2,2,2)`, the ceiling 61/63 is sharp across 105 canonical words. Across the 1,447,295,850-word `(4,4,2,2,2,2,2)` domain, a three-stage dual projection census proves that exactly 54 canonical (108 ordered) words cover all 63 masks at 144 complete calls.

## Exact interface and literal certificate
Retains the one-root F2 dirty-connector interface of PR #943, PR #2229, PR #2236, and PR #2397.

## Replay and evidence
Run: `python3 -I -O -B research/seven-source-18event-profile-census/verify.py`

## Open next questions
1. What is the minimum complete-call schedule for the 98 nonzero seven-source masks of Hamming weight at most four?

## Scope, source pins and credit
Credits commdata2338 (PR #2397), Cinna Davis / 1337isnot1337 (PR #2229, PR #2236), and Ross Richardson (PR #943). Prepared for nightangelflowerwin-ops with AI assistance under Apache-2.0. No new kappa is claimed.
 
