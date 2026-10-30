# Complete binary coframe optimization of the actual restricted C source

## 1. Exact result and source

The actual restricted source is `INTERSECTION153-ROUND3-ACTUAL-WORD.json.gz` from native-dual-suppliers. Its decompressed SHA256 is `7f137c4b95db519d04ad2336ef1a146fbc953124e95940d10b572a63ab958c87`. It has 632 arbitrary persistent inputs: 224 main inputs and 408 independent helpers. Its one owned field is scrubbed and returns zero. It retains the actual 56 A / 56 C port partition, all four output retimings and eight H7 centre queries.

Set the coframes at the six frame IDs

`59,60,61,62,63,64`

to identity. Keep every other coframe. The complete new profiles in either source orientation are

`P = 1618 H1 + 619 H2 + 418 H3 + 139 H4 + 12 H6 + 8 H7`,

`T = 26 H3 + 2 H4 + 12 H7 + 368 H8`.

All 408 helpers remain independent. There are 2,814 positive recursive calls, compared with 3,015 in the original source. The paid and target rank masses are 4,794 and 3,114. The local rank deficit remains 1,680; this is not a funded complete Gaussian caller.

Dugongue PR5687 supplies the two-line construction at frames 59 and 60. Its source profile is independently reconstructed here. The four additional folds change its paid profile by `-192 H1 +96 H2` and keep its targets. The full signed-moment gain over the original source exceeds `206 C` for every `0<C<=.00351`. At C=.00351 its exact interval contains .876907816598408, compared with .410349854119189 for the two-line proposal.

The optimization covers every binary assignment `H_f in {F_f,I}` on all 423 active unprotected proper-transport frames. Main boundaries, native warp endpoints, centre frames and ground stay fixed. Every changed helper endpoint is debited and replaced. Every recursive child must have rank at most seven. At C=.00351, no legal assignment in this class improves the displayed signed moment by more than `1.604e-21`. This is a rigorous numerical headroom bound for this class and test exponent. It is not an exact real optimum or a bound on arbitrary coframes, different source words or a new kappa.

## 2. All-input operator construction

For each old frame f, let F_f be its retained exact Clifford coframe and H_f its chosen new coframe. Emit every scalar instruction at the common new coframe of its operands. Replace every proper transport f to g by the exact physical operator `H_g H_f^-1`. The logical action of that operator is identity. Keep each physical native warp: both of its endpoint frames are protected, so its logical generator is unchanged. Keep the centre and owned instructions with their original full-payload semantics.

The source's free-group endpoint therefore applies to precisely the same logical instruction stream. It gives the same main logical map and autonomous identity on every helper logical input. The main input and output coframes are unchanged, so the complete physical main interface and its source monomial adapters are unchanged. Helper i has the new physical endpoint `H_final(i) H_start(i)^-1`. Its complete two-sided normalizer converts that operator to one canonical positive Gaussian job. The old helper is debited; it is not also credited.

No independent input is erased. Source COPY and CLEAR instructions still act only on the owned centre. The source all-column replay includes an arbitrary dirty owned entrance and checks its zero output. A coframe is an invertible unitary change of interpretation; it is not a free operation applied at an arbitrary live cut. Every nonidentity physical conversion appears in the emitted plan with its own exact recipe and phase.

For the backward orientation use the source's conjugated Clifford convention and its own scalar/native stream. The full proper-edge multiplicity table is identical in both orientations. This is checked exactly from all records, not inferred from their aggregate old histograms. Thus the same assignment and complete price apply to both orientations.

## 3. Complete binary domain and rank tables

A source read finds 618 active proper-transport frame IDs and 195 protected IDs. Exactly 423 active IDs are unprotected. Unused frame-table entries have no effect on the program or invoice. All helper start and final frames lie in the protected or active sets.

Let x_f=0 retain F_f and x_f=1 use identity. For a proper edge f to g, the original nested spaces give rank r=dim(g)-dim(f). The four exact grades are

| x_f | x_g | Gaussian grade |
| ---: | ---: | ---: |
| 0 | 0 | r |
| 0 | 1 | dim(f) |
| 1 | 0 | dim(g) |
| 1 | 1 | 0 |

The same table applies to an original nested helper endpoint, with its actual two boundary dimensions. An inverse coframe has the same Gaussian grade as that coframe. Rank zero has no recursive query or productive Gaussian credit. Its ordinary instructions are still retained and charged.

Only two free frames, 181 and 182, occur as helper outputs. Only 59 and 60 occur as free helper inputs. Thus fixing the two output choices makes every helper term a constant or a unary term. All remaining pair terms come from paid proper edges.

In fact the child cap forces both outputs to stay. Each has a literal proper edge to protected frame 2, of dimension eight. Folding its source would create H8. For example, the source has an edge from 182 to 2 on owner 399, and from 181 to 2 on owner 440. These occurrences are retained in the emitted word. No other frame choice can remove this violation while preserving frame 2. The three branches with a folded helper output are therefore infeasible under the rank-seven cap.

The package retains all four minimum-cut certificates, plus these direct forbidden-event witnesses. It does not silently remove those output variables from the initial domain.

## 4. Exact graph reduction and certificate

Fix C=351/100000 and t=1-C. Minimize the complete cost

`E(x)=sum_paid grade(x)^t - sum_helpers grade(x)^t`.

Centre costs are fixed and included. For a paid pair, write its four costs E00,E01,E10,E11. Since r<=dim(f)+dim(g) and 0<t<1,

`E00+E11 <= E01+E10`.

This is the submodular condition. The binary term has the exact expansion

`E00 +(E10-E00)x_f +(E11-E10)x_g`

`+ (E01+E10-E00-E11)*(1-x_f)*x_g`.

The final coefficient is a nonnegative directed cut capacity. Positive unary costs connect source to vertex; negative unary costs connect vertex to sink and add their constant. A vertex on the sink side means x_f=1. Helper terms are already unary after the two branches are fixed. This gives an exact cut representation of every assignment in each branch.

For the executable certificate, each r^t, 1<=r<=8, is enclosed by `[L_r,U_r]/10^24`, with integer endpoints of width at most one. The checker obtains log r from the positive atanh series and an explicit geometric tail. It then uses alternating exponential partial sums for exp(-C log r). Rank zero and rank one are exact. All arithmetic is rational.

The integer network uses L_r. A forbidden child grade receives capacity cost M=10^40 instead of its ordinary price. Every cap-feasible absolute objective is below `(3015+408)*8*10^24`, which is less than M/2. An assignment with one forbidden child has objective above M/2 even after every possible helper debit. Thus this penalty preserves the legal minimum and certifies infeasible branches.

Dinic's classical integral flow algorithm is used only for discovery. Registered replay checks each saved edge flow against its exact capacity, verifies conservation at every vertex, and checks equality of the flow value and the declared cut capacity. These conditions prove the global integer optimum without rerunning or trusting the solver. A separate direct histogram computation agrees with the cut expression on 256 deterministic assignments, including forbidden-child penalties. The algebraic reduction above covers all assignments.

The best cut folds precisely the six listed lines. For any legal assignment, its true real objective is at least its integer objective divided by 10^24 minus `408/10^24`. The six-line witness's true objective is at most its integer optimum divided by 10^24 plus `1196/10^24`; its H1 costs are exact and its other paid counts sum to 1,196. Therefore its possible remaining signed-moment gain is at most

`(408+1196)/10^24 = 1.604e-21`.

This bound covers all 2^423 binary assignments before the cap removes infeasible cases. It is a bound at C=.00351 only. The all-C gain theorem below is a separate comparison, not an assertion that one cut is optimal at every exponent.

## 5. Complete gain and higher-moment transfer

The two-line profile from PR5687 is reproduced from the literal source. Its complete signed gain is

`G_2(C)=201-78*2^t+9*3^t-27*4^t+12*5^t-18*6^t-36*7^t+42*8^t`.

The four new folds add

`A(C)=192-96*2^(1-C)`.

They do not change any helper start or final frame. Thus the full six-line gain is G_6=G_2+A, with every old target debited. Its direct coefficient list is

`393,-174,9,-27,12,-18,-36,42`

on ranks one through eight. Both gains are enclosed by exact rational intervals in RESULT.json.

The retained elementary derivative proof gives G_2(C)>74C on the stated interval. The checker verifies its strict rational margins. Also log 2>56/81, log 2<7/10, and exp(-x)>=1-x. Hence

`A'(C)=192 log(2) 2^-C`

`>192*(56/81)*(1-(351/100000)*(7/10))`

`=55862408/421875 >132`.

Since both gains vanish at zero, integration proves `G_6(C)>206C` for every `0<C<=.00351`.

Now put u=1/5 and s=t+u. The complete paid higher-moment change is

`-393+174*2^s-9*3^s+27*4^s-12*5^s+12*6^s`.

For `119649/100000<=s<6/5`, monotonicity bounds each positive term at the upper endpoint and each negative term at the lower endpoint. Rational log/positive-exponential series bounds give an upper bound less than 137. All twelve H6 jobs are included. The result is not obtained by assuming that a first-moment improvement also improves the higher moment.

The productive t-moment gain is unchanged from the two-line construction and exceeds 47 per call. The old helper rank mass is 3,066 and its largest rank is eight, so its t-moment exceeds 3,000. Take an explicitly supplied compatible caller with n>0 old C occurrences, cutoff c>=17, the same completion convention, and old guards `gamma<31/32`, `delta<19/20`. Let T be its complete old productive t-moment. Then

`T>3000n`, `T_new>T+47n`, `P_new,s<P_old,s+137n`.

Since c^(1/5)>7/4,

`gamma_new < [(31/32)T+(548/7)n]/(T+47n)`

`<=7597/7756 <49/50`.

The rational expression decreases as T/n increases. The independent field count and target floor stay fixed while the productive denominator increases, so delta strictly decreases. The new complete caller's first-moment gain is n G_6(C)>206n C. This is a preservation theorem for a supplied compatible caller. No such newly funded caller is instantiated here.

## 6. Native verification and positive ordinary work

CONSTRUCTION.json.gz gives every chronological record in both 21,166-record programs, all actual transport/native recipes, every helper's whole-job normalizers and the unchanged source main-normalizer reference. It is an emitted program, not only a histogram.

The source free-group replay checks all 632 persistent columns and the arbitrary owned entrance in each orientation. Every scalar contact and final coframe is checked. The actual compiler synthesizes 4,268 distinct oriented maps. Registered replay independently decodes each stored recipe and compares its full Clifford tableau and exact zero-state phase with the specified operator. These two comparisons identify the complete native Clifford, including absolute scalar phase. It also checks 24 distinct helper-normalizer pairs and all 408 assigned helper outputs. The phase claim is in the retained nine-direction native model; its uniform-width implementation retains the source framework assumptions.

The plan charges 7,333 ordinary monomial field passes per orientation: transport wrappers, ordinary native maps, 448 main adapter passes and 816 helper adapter passes. Identity transports retain a conservative ordinary dispatch/pass charge. The retained real-scalar allowances are 158,120 forward and 158,168 backward. COPY, CLEAR, field routes and owned initialization are not converted into productive targets or free actions. There are 633 retained payload fields, plus the inherited wrapper/ROW working stock; no smaller stock claim is made.

The source exact logical prefix L1 bounds are 457 forward and 169 backward, with denominator bounds 32 and 64. Unitary coframes preserve the corresponding block-operator bound. A separate product envelope multiplies `1+|coefficient|` for each scalar operation and charges COPY positively; RESULT.json records a conservative power-of-two exponent for every prefix and suffix. The new monomial descriptors, input/output passes, suspended stock, tape movement and finite compiler fees must still be bound to a complete caller. No old machine threshold is reused by assertion.

Normal and optimized replay use explicit checks rather than Python assert for the new obligations. Failure controls cover cut flow, chronology, missing calls, missing or stale targets, main adapters, protected frames and absolute phase. Actual source corruption is rejected before import. The phase certificates and exact cut prove this finite scoped construction; they do not discharge every inherited ROW, uniform native, precision, tape or outer recovery assumption.

## 7. Remaining boundary and credit

This result preserves the actual C interface. It does not replace its 56 A / 56 C ports by a common uniform interface, transpose it into a different geometry, or instantiate the proposal's separate two-call consumer. The local deficit remains 1,680. A compatible complete Gaussian caller, fresh compiler constants and ordinary/outer admission remain necessary before any numerical kappa claim. Arbitrary coframes, changed native generators, changed words and higher child caps are outside the optimization certificate.

Credit Dugongue PR5687 for the actual two-line construction and the prior moment/tail proof. Credit the native-dual-supplier source, Cao Yifan PR4610/4470, Cinna Davis and the native/frame/ROW/controller lineage, DaysSky, Nick Petalas, Ryanson Jonathan, zxv, Jacob Alan Sussman and all retained helper, phase, scalar, compiler, stock and analytic notices. Dinic's algorithm and the binary submodular cut reduction are classical. The new contribution is the full source-bound 423-frame optimization, four additional line folds, exact executable physical certificates and the fully charged stronger gain with preserved tail guards.

Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0. No selected-frontier change, global literature priority, independent human review or proof-kernel acceptance is claimed.
