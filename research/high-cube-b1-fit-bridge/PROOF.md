# A fitted B1 caller/callee bridge for high cubes

## Result and status

This proves one all-width interface implication for the literal PR2915 high-route adapter. For a fixed prime q > 2^80, an integer u >= 311311, a dimension N=d^2 >= 4, a positive fibre F, and a valid pair of distinct route axes, every reached B1 swap call is exactly an ordinary q-adic interchange on

    [P][q^u][G][q^u][S]

with P,G,S positive and total volume V = Q^N F, where Q=q^u. The ordinary wrapper therefore receives the width and complete spectator extents required by PR2899's fitted-branch theorem. Under that theorem's inherited C0 hypotheses and the successful-execution/capacity conditions below, it preserves the borrowed source and spectators, returns one distinct owned V-symbol output, clears its owned work, and has a uniform time bound

    A_j <= C_q V u^(99830289/100000000).

Here C_q depends on the fixed q and the retained source. This implication applies to the fitted regime u >= 311311. The threshold is sufficient and is the least uniform threshold for the particular stock rule cited below.

This is a conditional composition result. It does not independently prove PR2899's C0 premises, execute a fitted GL64 payload, prove the enclosing caller's numerical backing, recover from an interrupted call, or extend the all-width statement to every odd q >= 3. It changes no selected result or kappa.

## Exact hypotheses

Let q be a prime with q > 2^80. Let u >= 311311, d >= 2, N=d^2, F >= 1, Q=q^u, and V=Q^N F. Assume:

1. The high-route caller supplies a canonical context with context.cap=Q, context.q=q, and route.dimension=d. Its fibre has F positions, and the route operation has valid, distinct axes x,y in {0,...,N-1}.
2. The ring loaded by high_route.execute is the exact modulus Q. The reached call is successful and its tape, numerical and scratch capacities suffice.
3. The PR2753/2809 ordinary C0 endpoint, chronology, source-refinement, and uniform-charge hypotheses used by PR2899 hold. Use the fixed selected vocabulary and the same prime q.
4. For the high-cube tape invoice corollary only, accept PR3301's separate source proof that the adapter work outside the complete B1 interval is at most 100000V. Its merged package is author-checked and still awaits independent review. The caller/callee bridge and the transfer of PR2899's tariff do not depend on this corollary.

Hypothesis 3 is a dependency, not a finite-test conclusion. Hypothesis 4 is used only in the final combined cost corollary; the call-interface theorem and the PR2899 tariff transfer do not depend on the adapter's 100000V invoice.

## Proof

Write i=min(x,y) and j=max(x,y), so 0 <= i < j < N. In high_route.extents, the source computes

    P = Q^i,
    G = Q^(j-i-1),
    S = F Q^(N-j-1).

All three are positive because Q>=2, F>=1, and their exponents are nonnegative. Directly,

    i + (j-i-1) + (N-j-1) + 2 = N,

so

    P Q G Q S
      = F Q^(i + (j-i-1) + (N-j-1) + 2)
      = F Q^N
      = V.                                                    (1)

This is an identity for every integer N>=2 and every valid pair i<j; it does not enumerate axes or payload cells. It includes the whole suffix fibre in S, so there are no omitted spectator cells after the second swapped field. The prefix and the middle field are the other complete spectators.

The source binding is literal. high_route.execute loads the ring from context.cap and passes the route's q into apply. Adapter.swap rejects q different from native.q. For a direct swap, apply passes the extents above to Adapter.swap. For a reversed ADD, apply makes one such call before kernels.added and one after it; both use the same extents. Other operations make no B1 call. Thus every reached call has the same shape (1) and the same width parameter.

Adapter.swap starts width at zero and increments it once for each yield of radix_power(ring,q). The authenticated PR2809 cardinality source inside PR2899's source archive implements that generator by exact division of the ring modulus by q until it reaches one; it rejects any nonzero remainder and requires the final quotient to be one. If the ring modulus is Q=q^u, there are exactly u yields. Consequently width=u. This uses encoded source arithmetic, not a decoded or test-only width.

Adapter.swap then calls native.run with borrowed_tape(source), borrowed_count(width), and borrowed views of P,G,S. This is exactly PR2899's run(payload, original, prefixes, gap, suffix) boundary with original=u and the three positive extents from (1). Since u>=311311, the pinned stock-fit theorem gives k(u,q)<u/2 for every permitted q. This is a sufficient fitted-branch condition for the PR2899 wrapper.

The PR2899 theorem is stated for every e>=1, P,G,S>=1 and each fixed source-admissible prime q>2^80. On a successful admitted call it gives the ordinary interchange endpoint, unchanged borrowed payload, pointwise-restored complete spectators and heads, a distinct owned output, and empty owned work. Its time is O_q(V e^(1-a)), with a=169711/100000000. Substituting e=u gives the displayed A_j bound because 1-a=99830289/100000000. The hidden constant is independent of u,P,G,S,F, but may depend on q and the pinned implementation. Its space statement is O_q(V)+F_q on a fixed tape inventory.

After native.run returns, Adapter.swap acquires a fresh live lease while source is still live, copies the distinct native output into it, rewinds the result, and clears the native output. Its finally block closes width and all three extent counts. The caller, not Adapter.swap, later clears its owned current lease after replacing it with the result. Under the pool's linear-lease invariant and the admitted B1 endpoint, this is a distinct owned result with the same complete V-symbol layout. The wrapper does not claim transactional cleanup if native.run fails midway; the theorem is for successful execution.

For a complete high cube, let t be the number of reached B1 calls. If each call is fitted, then

    sum_j A_j <= t C_q V u^(99830289/100000000).

This step is source-uniform in u; t is fixed by the selected compiled word and route. If PR3301's separately proved outside-call invoice is accepted, the cube total is at most this sum plus its recorded linear term. For fixed q,d,K and compiled word, that linear term is absorbed into O_q,d,K,word(V u^(99830289/100000000)) for u>=311311. No coefficient is inferred for the enclosing physical stock.

## Scope boundary

The all-width ordinary theorem and its fit cutoff have different prime-domain implications:

- For prime q>2^80 and all u>=1, PR2899 states the full successful-execution bound; for u>=311311 it uses the fitted branch covered above.
- For odd q in [3,2^80], the source-bound all-width theorem is not available from these pinned sources. The q=3 and q=5 fixtures are finite elementary-branch evidence only. They do not establish the fitted branch or a uniform-in-q bound.
- The result pins the unchanged PR2915 physical adapter. It does not audit PR3330's opt-in factor-word compiler, its selected-registry call-count invoice or its acceptance guard; it only covers any call that reaches this adapter with a valid distinct axis pair.
- PR2899 retains the C0 endpoint, chronology, source-refinement and uniform-charge premises. This bridge composes them into one caller; it does not prove them anew.
- No fitted call with u>=311311, actual GL64 payload, numerical backing bound, interruption recovery, full cold selected replay, proof-assistant result or independent scientific review is claimed.

The current selected record remains the conditional kappa 836330098538459/500000000000000000. This package makes no new kappa, supplier-admission or unconditional multiplication-theorem claim.

## Reproduction

From the repository root:

~~~
python3 scripts/research_package.py --package research/high-cube-b1-fit-bridge --check-only
python3.12 scripts/research_package.py --package research/high-cube-b1-fit-bridge
~~~

The standard-library verifier checks source pins, the literal route/adapter binding, the nested exact-division generator, symbolic extents for boundary and interior pairs, the fitted cutoff, and rejection controls. These executable checks corroborate source identity and finite instances. The universal extent identity is proved algebraically above; the PR2899 transfer remains conditional on its written hypotheses.

## Sources and credit

Main sources are the pinned PR2915 files high_route.py, stage.py, and stage_sources.py; the exact PR2899 archive; PR2899's physical ordinary-interchange proof; and the PR2234 stock-fit threshold proof. Source hashes and Git blob IDs are in SOURCES.json.

The released PR3301 package explicitly lists a fitted B1 call contract as its next question; the exact PR3301 proof and README are pinned in SOURCES.json. PR2915 and PR2899 retain their authors' credits. This package's proof is a conditional source bridge, not an independent review of those predecessors. Prepared by OpenAI Codex (GPT-6) under user direction; no independent human or proof-assistant review is claimed.
