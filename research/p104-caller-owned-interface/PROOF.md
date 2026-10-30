# Independent caller interface adaptation

This is a source-bound extension of the selected PR5599 admission's independent
caller adapter, not a new multiplication bound or a replacement for the primary
native replay. The selected checker is pinned at SHA256
`6fce1e331747aebee13ecc6e33ab2fd49b9383640c20546e245be3e624933b52`.
The unchanged original PR5550 checker and its complete expected output are
separately pinned; its positive control must reproduce all original output bytes.

## Admission comparison

The completed PR5599 review permits noncanonical helper endpoints and dirty
independent inputs. Endpoint normalizers are placed before and after each fresh
forward local call. All eighteen local calls remain forward: the main-pair
signed swaps and translations are not a transpose of COPY/CLEAR. At finite
precision, COPY is an ADD into an ideally initialized owned zero; its injected
residual must survive later arithmetic. No overwrite of noisy state is justified.
These facts cover the kind of scalar dependency changes in our shared relays,
provided their complete arbitrary-input local identities are independently
verified. They do not themselves establish any new candidate's identities.

The old selected caller adapter has a narrower *inventory implementation*:
`helpers = public - 208`, every public label productive, eight owned lifetimes,
and a single scratch slot. That code cannot represent retired public role 573,
eleven owned lifetimes, or two simultaneous lifetimes. This is an evidence gap
in applying that independent adapter, not a counterexample to the primary local
construction. The present extension closes this inventory gap without changing
the spectral, Laurent, native-normalizer, target or negative-control equations.

The five retained assumptions still apply: native all-width semantics, owned
erasure, compiler closure, precision/tape realization, and analytic recovery.
This adapter does not prove those assumptions. In particular it continues to
report `paid_native_maps_replayed: false` and `machine_and_precision_admitted:
false`; parent primary replay supplies the separate native-map evidence.

## Exact scope of the extension

`interface.py` partitions the literal local fields into independent public inputs
and owned labels. For a compact word, these are consecutive public inputs and
the declared `owned_fields`; for a legacy word, `independent_public` and
`owned_roles` must form an exact disjoint partition, including any explicitly
retired holes. All 104 main pairs must remain independent. Only the remaining
independent fields receive helper targets. Their individual native endpoint
normalizers are still checked by the original signed-Pauli and independent
dense-phase routines.

The interface walk checks every event's ownership, current chart, strict nested
MOVE, active scalar sources and dyadic coefficient constraints. It does not
replace the primary exact scalar endpoint replay. Each INIT allocates the lowest
unused scratch slot and each CLEAR releases it. An explicit lifetime schedule
is checked independently for overlap, label alias and balanced exits. A COPY
is allowed only into an owned field with no scalar write since INIT; ideal zero
is preserved by any preceding MOVE. Its numerical interpretation remains the
residual-retaining ADD described above.

For each of eighteen sequential LOCAL sites, the 208 local main inputs bind to
that caller bank pair and every independent helper binds to its own fresh global
field. Retired holes have no productive global ID. Owned lifetimes instead bind
to the scratch slots immediately above the complete productive inventory.
Distinct simultaneous lifetimes cannot share a slot. Every local lifetime ends
before that LOCAL returns, so subsequent LOCALs and the intervening thin-query
scratch may reuse these slots. This is checked using explicit hierarchical
instruction addresses `(physical event, sequential port, local instruction)`.
Each local INIT/CLEAR and each query INIT/CLEAR becomes an interval in that
ordering; intervals sharing a global scratch slot must not overlap. Substituted
LOCAL instructions have a single outer event index, while thin-query recipes
have their own event index and execute by port. A mutation moves a query interval
into a live local interval and must fail. Thin-query chronology and inverse-Q
correction remain checked by the original routines.

The recursive paid and productive histograms are rederived from literal MOVEs,
the independently normalized helper endpoints, the unchanged main targets,
queries and whole idles. Scalar allowance is recounted twice from literal
coefficients. The local ordinary routing allowance is

`1000 * (paid local jobs + 2*helpers + 208 + 4*104 + 4*owned lifetimes)`.

The complete ordinary pass count then uses the original fixed controller census
and must fit the source's finite raw allowance. This is still an abstract
address/phase/scalar pass allowance under the retained tape contract, not a new
machine-time estimate. Two owned scratch fields are explicitly recorded;
constants for fixed inventories remain subject to the same compiler/storage
assumptions and threshold argument as in the selected admission.

All ten original fault controls remain present, including contact phase,
exterior sign, missing idle, helper alias, main translation, owned query alias,
missing inverse-Q correction and Laurent overflow. The extension adds deliberate
overlap of simultaneous owned lifetimes and erroneous productive credit to an
owned role. The productive-credit fault mutates the literal input inventory
and reruns the interface audit; additional full audit mutations remove an
independent field, stale the source lifetime count, and reuse a label before its
first CLEAR. An original positive-control run uses the untouched PR5550 source
and compares its entire scientific output byte-for-byte. On Windows only the
unavailable operational RSS module is supplied with a nullable value; scientific
code and output are unchanged. A separate guard samples the actual child RSS.

## Source-specific lightweight checks

For PR5713 head `a5348f7143f95fe0046b92b96172e30763c7d731`, the literal interface
has 743 independent inputs, 535 helper targets, 9 owned labels, 11 lifetimes and
peak 2. Eighteen fresh helper inventories plus 3,328 main fields give 12,958
productive fields; owned slots are 12958 and 12959. The independently recounted
local scalar and routing allowances are 220,326 and 5,164,000.

The registered lightweight compatibility fixture exchanges helper label 573 with
owned label 743 in this same frozen word. It permutes destinations and scalar
sources, relocates the corresponding independent initial/final charts, and
declares 573 a retired hole inside 744 public slots. There are still 743 independent
inputs and 752 total local labels. This is a role permutation, not a new linear
construction. The interface and full caller allocation must reproduce all
profiles and allowances, give 573 no productive ID, retain one for relocated
helper 743, and verify all 1,758 local/query lifetime intervals. Thus the public-hole
branch is exercised without relying on an additional pending source.

The literal original PR5550 interface also passes the same lightweight audit:
735 public inputs, 527 helpers, eight lifetimes, peak 1. Full original and current
candidate runs are explicitly separate, bounded serial commands. Their results
are recorded only after successful completion; preparation is not a scientific
caller pass. See the generated binding, patch, output, guard and receipt files.

The unchanged original positive control and the current PR5713 candidate
have completed in separate serial runs. The original output agrees with
all frozen bytes (SHA256 `b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009`).
The candidate verifies 7,488 contacts, 302 distinct signed-Pauli/independent-phase
checks, 9,630 fresh helpers, 66,348 paid jobs, 12,958 productive fields and all 16
negative controls. Its ordinary pass count 124,284,844 is below 184,647,552.
The candidate full output SHA256 is
`9fe876e5e74e878e691b0f9277ebbc39ce4610262526632db489816a4dd741ac`.
Original/candidate elapsed times were 25.625/26.313 seconds, sampled child RSS
peaks 73,019,392/76,578,816 bytes, under separate 120-second/512-MiB caps. These
operational results are local evidence, not a guarantee on another host.

Prepared for flyingviper with substantial OpenAI Codex assistance. Original
PR5550/PR5599 contributor notices remain in the generated checker. Apache-2.0.
