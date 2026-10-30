# Validation of the PR5713-focused draft

Checks were run serially on Windows with the bundled Python interpreter.
The scientific adapter and interface code are unchanged from the independently
reviewed PR5684 package. The original PR5550 positive control previously matched
its complete frozen output in 25.625 seconds, with sampled RSS 73,019,392 bytes.

The PR5713 candidate at a5348f7143f95fe0046b92b96172e30763c7d731 passed
its independent full caller run in 26.313 seconds, with sampled peak RSS
76,578,816 bytes, under separate 120-second/512-MiB caps. Its complete output
SHA256 is 9fe876e5e74e878e691b0f9277ebbc39ce4610262526632db489816a4dd741ac.
The result checks 66,348 paid jobs, 12,958 targets, 302 normalizer/phase anchors,
9,630 fresh helpers, eleven local lifetimes with peak two, and all sixteen
negative controls. Ordinary allowance is 124,284,844 below 184,647,552.

The source primary verifier passed separately before the independent run;
its short output is retained in evidence/primary-prerequisite.log. That is
prerequisite evidence, not an independent primary-map replay by this package.

The portable wrapper retains the reviewed Windows UTF-8/LF stdout fix. The
original scientific checker and expected bytes remain unchanged. The wrapper's
summary now reads the candidate head from its authenticated scientific output.
The registered normal and optimized replay pair passed after integration.
Normal original/candidate times were 25.891/26.797 seconds; optimized times
were 24.157/25.078 seconds. All four complete scientific output hashes matched
the frozen originals, and sampled peak child RSS stayed below 76 MiB.
The package metadata and pins check passed, and a separate agent checked the
integrated source bindings, literal inventory and public-hole schedule.
Committed-byte, source-history and standalone-export checks are publication
gates, reported in the PR after execution. Historical PR5684 compact evidence
is labeled as historical.
