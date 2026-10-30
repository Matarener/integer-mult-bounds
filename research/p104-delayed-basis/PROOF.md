# Helper341 boundary composition

This composes Ali Romman's PR5602 identity, pinned at
`6c224aa720203c4f4615e6538d8038a275387db8`, with the published delayed/prepared
word. The source canonical SHA256 is
`df44a24231edd04954ebf066b1efb311441e5d9d48b64d03e555cbea087b25c6`.
This is a checked composition, not a new basis identity.

Immediately after the source's last read of341, event11285,
`ADD346,341,+1` at frame240, exact rational replay gives

`current341 - 2*current337 = x341 - 2*x93 - 2*x339 + 2*x351`.

Both current rows are at240. Initially93,339,341,351 are all at frame3.
Precompose the word with the three ordinary ADDs implementing

`x341 <- x341 + 2*x93 + 2*x339 - 2*x351`.

The update is invertible and does not change its source coordinates.
The original endpoint column of input341 is the unit helper341 column, so
this precomposition changes no other final output. After the last341 read,
subtract twice337 from341. The displayed relation now gives exactly the
original independent input `x341`.

There are no later reads of341. Its remaining eight destination operations,
including its rank5 ascent240-to127, can therefore be removed, and its final
frame declared240. All other operations remain unchanged. No new input,
temporary, owned lifetime, or zeroing operation is introduced.

The exact paid change is `-H5`. Helper341's productive target changes from
rank9 to rank4, giving target change `H4-H9`. Thus the signed funding gain
is `H4+H5-H9`, strictly positive for `H_r=r^t`, `0<t<1`. The target debit is
essential; counting only the removed paid transport would overstate the gain.

The separate independent agent calculation checked all756 original
input columns, all756 endpoint rows, every common frame and ownership
transition, and the unchanged INIT/CLEAR/COPY sequence. It confirms747
independent inputs,11 owned lifetimes, and peak2. Candidate canonical SHA256:
`22aa2b59ed2900dbd7ed6060586422cc6e72927cf7045727b68ec1b0b24b4209`.
The package verify.py separately checks native, caller, ordinary-cost and compiler obligations and records the full result in RESULT.json.

Independent audit prepared for flyingviper with substantial OpenAI Codex
assistance. Retain Ali Romman's PR5602 attribution and the composed sources'
notices. Apache-2.0.
