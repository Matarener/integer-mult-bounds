# Existing weighted Jensen applied to one compiler contract

This is an explicit sufficient-condition derivation and one exact numerical
application. Weighted Jensen, PR4416's rank-one-tail endpoint and the generic
higher-moment/logarithmic-majorant theorem are credited predecessors, not new
theorems claimed here. All physical/native/ordinary hypotheses remain explicit.

## General sufficient criterion

Let positive paid ranks r have nonnegative multiplicities p_r, not all zero.
Set P_s=sum p_r*r^s, P1=P_1, w_r=p_r*r/P1 and mu=sum w_r*ln r.
For0<C<1 and t=1-C, convexity of exp(-Cx) and weighted Jensen give

    P_t/P1=sum w_r*exp(-C ln r)>=exp(-C mu).

The weights are rank-mass probabilities, not call-count probabilities.
If ln c>mu, then P1/c^C<P_t. For any positive target moment T_t,

    gamma_C=P1/(c^C*T_t)
           <=alpha*exp[-C(ln c-mu)]<alpha=P_t/T_t.

If also bB<=P1, then delta=bB/(c^C*T_t)<=gamma_C<alpha. Thus
alpha<1, ln c>mu and bB<=P1 suffice for all three ratios to be below1
at the allowed endpoint u=C. Strictness already follows from ln c>mu;
no unstated strict version of Jensen or probabilistic input independence is
needed. These conditions are sufficient, not necessary or a lower bound on
all compilers.

The primary Jensen citation and exact locator are in the preserved literature
note. The authenticated higher-moment README§2 explicitly permits u>=C and
identifies u=C,sigma1 with the existing PR4416 endpoint.

## Fixed offset at two points

Freeze u=C_test=.0033000005. At either declared C, s=u-C>=0 and
t+u=1+s. With Rmax the largest paid rank,

    P_(1+s)<=P1*Rmax^s,
    gamma_u<=alpha*exp[-C(ln c-mu)+s ln(Rmax/c)].

At the tested point s=0. At the goal s=5*10^-10 and this is a transport
bound, not the exact rank-one endpoint identity. Completion remains
delta=(bB/P1)*gamma_C; no monotonicity of gamma_u in u is assumed.

For the frozen paid bill, P1=241268, Rmax72, c12 and b13. Exact rational
logarithm bounds certify

    mu<2940373489/1206340000,
    ln12>1553/625,
    d=ln12-mu>57140143/1206340000.

The common fixed-u exponent gap is greater than
188561391079677/1206340000000000000>0. Since exp(x)>=1+x,
gamma_u<1/(1+x)<19997/20000. Separately,
13*15424/P1=50128/60317<.84. The checker derives these rational
witnesses from the exact paid coefficients and authenticated log intervals.
Direct moment intervals independently confirm both ratios and the raw reserve.

## One hypothetical whole invoice

Retain exact PR5565 paid profile and its eighteen-FULL controller.
Replace145 distinct original rank9 helper targets per FULL by independent
rank4/rank5 targets, remove every parent credit and grant no paid saving.
This formal inventory changes local helpers from
{4:83,5:5,8:14,9:425} to{4:228,5:150,8:14,9:280}.
It adds2610 productive fields globally and retains rank masses241268/242028.
All complete coefficients, including queries, whole idles and main targets,
are shown in INVOICE.json and independently bound by the checker.

The145 physically distinct target splits are not supplied. The additional
original arbitrary-input fields, endpoint autonomy and zero added paid debit
are assumptions about a missing word. Disjoint-axis factoring on one paid
owner does not establish them. Existing13 or historical15 constructions are
not added to this145 target proposal.

## Complete charged compiler and finite majorant

Under source-native chronological product/owner/adapter/spectator hypotheses,
the raw tensor has66726^v paid positions,15424^v targets and ambient/max-target
rank145^v. Per-owner paid completion raises each target below13^v to13^v.
Original and completion paid jobs split into integer12^v blocks and a remainder.
The complete source overcount is

    alpha^v+2gamma_u^v+2delta^v.

No completion creates another productive input. At v32768, reserve10^-6
and rho19997/20000, exact comparisons give rho^v<1/128 and

    alpha^v+2gamma_u^v+2delta^v
      <1/(1+32768*10^-6)+4/128=516137/516384<1.

Direct evaluation gives the stronger actual normalized upper bounds in README.
Both coefficient-two charges are retained; dropping a positive charge would
improve a false bound rather than demonstrate impossibility.

For theta_bar39/40, exact12^40<13^39 and2*12^40<145^39 establish
rank separation and the shifted-exit premise at integer v. The generalized
source README§4 permits any positive logarithm power p; at p22000, direct
intervals prove theta_bar^p<eta=t*145^(-vC) and145^(vC)<2^p.
Source integer-flow, complementary-source and exit bounds remain premises.

Using z-t=1/14000000000, the sufficient uniform condition is
(14000000000*j+1)^22000<2^j. Exact binary bisection in the one declared
bracket finds j1185397 and rejects predecessor1185396. The source's strict
convexity/unique positive crossing argument supplies the first passing-grid
interpretation. H=16595558000000000 is sufficient for this majorant, not
a minimum native program or realized finite word.

## Evidence and limits

All source texts and the complete source word are authenticated before imports.
The engine, original checker/request and entire root result are byte-preserved.
The qualified positive-C engine plus exact rational transport encloses all
tail quantities; it is reused rather than independently reimplemented.
The absolute10^-320 mesh preserves positive eta capacity intervals. No float
tolerance, optimizer, parameter sweep or materialized huge template accepts a
predicate. The complete normal/-O result equality and independent static
review are retained; human or formal acceptance is not claimed.

A numerical pass provides no actual145 cuts, new physical word, native
all-width/phase/product/adapters/owned proof or ordinary cost bound. All
new expanded U/R/W/P/G, simultaneous owned banks, scalar/growth/denominator,
precision, storage, movement, tape and rowstock constants remain unsupplied.
No source1000 or prior1100 cap transfers. Applicable BIT/outer admission
is unrun. There is no constructed, funded or selected kappa claim.
