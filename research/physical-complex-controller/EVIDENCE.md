# Local verification receipt

I completed the three registered cold commands on October 18, 2026 at
00:01:52 UTC with Python 3.12.13 on macOS arm64. I used the current main
runner at 6f100d4bb5083f8c35d96fd95a539811c62f245c and code snapshot
1ea7ce1774d1bd3879257cbd5946c8d6ed815a7b.

I received `PASS_PHYSICAL_COMPLEX_SOURCES` for five component checks,
`PASS_PHYSICAL_COMPLEX_EXECUTION` for ten, and
`PASS_PHYSICAL_COMPLEX_PLANNING` for one, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE`. I used the exact command arrays in
VERIFY.json. The component timers total 266.344 seconds; these timings do
not establish an asymptotic bound or predict another host's runtime.

| Complete check | Receipt SHA256 |
|---|---|
| Forward source word | `d2a3976bd0f5acb9db49fe5e403ca2185c12c6e41a4db5fc48160a7305d45e76` |
| Backward source word | `bff34c26dbf8d4ad45246b9db563cc280200e286f791195fd9ba15a21df7ecc6` |
| Fixed-prime admission | `190a6084d678e30aeaad977db1a8b75b78366bfacd62e6146c1d3d1e3122189f` |
| 349 scalar packets | `53a92a8027282b9349f8a73ce2d3ea64886b7116db325b9d2c5350e2d61060d4` |
| Recursive width 2 | `67108dc5b6eae0e118fc391dc6e76e5d9d7174c8374b86694526435bda1f004f` |
| Recursive width 3 | `d78c20b210f4088c85284d89ecfa38330d0d4c7291dbfcef7daa54d6d868693a` |
| Four direct normalized roots | `4fced21f9e114bff265815a79dfe0b02e2989a195c87a6c5a16b7041193fd760` |
| Reduced fast normalized root | `75b19b9d75e245f1720eaccc048c366a7a68cf7741805e908b0a2222067d4b40` |
| Encoded planning | `5e77a03170fef2fc8dfa544dab496760cfa116a22f99246d9c08d608e7414df3` |

Before that replay I passed the additional `check_machine.py --width 4`
fixture: 2,048 Gaussian values, 49,152 payload bits and 110 child calls/returns,
with SHA256 `ab4136849dcb8c92b30dddea36c972365442ac2b9733f9f705c411becc63ab1c`.
I retained the same two-level geometry and used 12-bit components with an
initial factor 16. I do not include this longer check in the registered
aggregate budget. An earlier 20-bit fixture also passed; I report the
current fixture's receipt here.

After the registered replay I corrected descriptive scope strings in the
parking and monomial checks, added the explicit fast-gate implication to
the proof, and declared its direct Compact proof input. I made no execution
algorithm change. At 00:04 UTC I passed both affected checks again, with
unchanged mathematical digests, and passed the final metadata/pin check.
I record the committed-byte and source-history preflights in the PR.

The raw local replay log has SHA256
`41988faa1577dd073a94a929c2da33e6c304ea9f36a1e4804c7e884baf59626b`.
It includes measured times and the two earlier descriptive scope strings.
The commands reproduce the mathematical receipts, not a byte-identical
timing log. I stopped the optional 132-case exponent sweep before completion
and claim no pass for it.

I distinguish this local verification from hosted CI, independent review,
formal refinement and complete selected-payload execution. I have not run
the production O73/GL64 payload or production guard width. I retain the
native, hosting and outer-transfer limitations in PROOF.md.
