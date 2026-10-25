# Vendored file

`pr4174_allocator.py` is a byte-identical copy of
`research/crt-reservoir-placement/allocator.py` from
[PR #4174](https://github.com/CrocSwap/integer-mult-bounds/pull/4174).

| Field | Value |
| --- | --- |
| Head | `5fec853f0c048871de3b8098d1e30d4ee19cda23` |
| Git blob | `4b3ad89652a28f7d142248d1b5747272e696493c` |
| SHA256 | `b764195fc6291e3c8fa8297b1f4ceaefc119d5664d8ff348b49eac8a2e79c688` |

It is copied, not pinned, because that PR head is not reachable from canonical main, and
package pins resolve only against reachable Git objects. `verify.py` checks the SHA256
before importing the file.

Author: Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance. It implements
the CRT.md §3 placement of Cinna Davis's PR #4100. Apache-2.0, as stated in the file. It is
unmodified.
