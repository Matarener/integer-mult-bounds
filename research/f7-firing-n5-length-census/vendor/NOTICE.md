# Vendored file

`pr4322-verify.py` is a byte-identical copy of
`research/f7-monotone-firing-classification/verify.py` from
[PR #4322](https://github.com/CrocSwap/integer-mult-bounds/pull/4322) at head
`22c60f6687ec49e7eb6082bb450173bbed5478ef` (Git blob
`b2b9d49d04a223819e4c47d47770ca4723017a71`).

It is copied, not pinned, because that PR head is not reachable from canonical main.
This package never imports or runs it. `verify.py` checks its SHA256 and reads only the
literal `EXPECTED_5_16` dictionary, #4322's frozen (5,16) per-mask row, with
`ast.literal_eval`. It is unpaidmoon's work, Apache-2.0, as its SPDX header states.
