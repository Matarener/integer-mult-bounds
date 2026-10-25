# Conditional target for the T74 physical layer

I record the cost implication used by the physical refinement in PROOF.md.
This calculation alone does not certify that implementation, supply the
ordinary H2 statement or establish a multiplication exponent.

I retain the complete PR2979 profile, with m=73, W=66304 and 666 calls:

    {1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190}.

I count rank mass 4,816,512 and 2,394,506 children. I divide by W
once; the profile already includes the complete call schedule and idle work.
At sigma=9983/10000, the registered exact interval engine gives

    mu_sigma in [999917587555181329277151726069,
                 999917587555181329277151726070] / 10^30,
    1-mu_sigma > 20603111/250000000000.

I retain the completed ordinary B1 exponent tau=99830289/10^8, the stopping
rule e<73 or e^1000<d, and the spaced-axis/long-record contract from PR3385.
Suppose I realize the whole T74 source with its listed children and establish
nonchild work O(V((e log p)^tau+1)), including scalar passes, private Z
lifetimes, routing, replacement scans and parent parking.

Since sigma<tau and e<=d, I have e^tau<=d^(tau-sigma)e^sigma.
I sum the normalized weighted recursion tree using the strict sigma moment.
The internal work is O(V d^tau(log p)^tau). At stopped leaves I retain the
elementary linear-in-e cost, giving exponent

    sigma+(1-sigma)/1000 = 0.9983017.

I obtain exponent 0.998 with a logarithm for root reservations. I use the
global row divisor L=66304 Gamma, where Gamma=|O(73,2)|, and pad once at
the root by less than two. I do not introduce that factor at each child.
For d=floor(p^0.997), log p=O(log(2d)). Under the physical work and height
bounds stated in PROOF.md, I obtain

    O(V d^0.99830289 (log(2d))^0.99830289).

Thus any fixed exponent above tau suffices. I choose alpha=0.998305,
leaving exact margins 211/10^8, 33/10^7 and 61/200000 over the internal,
leaf and reservation powers. I obtain the proposed layer saving 0.001695,
an increase of 17/600000 over the previous 1/600 layer saving. I do not drop the
logarithm at the exact exponent tau.

Finite scalar/parking constants need no 2^2048 ceiling. I derive their
effective upper bounds from the actual finite implementation in PROOF.md.
For numerical height I can replace the selected-source constants by
s=4816512 Gamma and a finite implementation allowance E_T. With B=s+E_T,
choose a fixed effective C0>max(32*73*B^2,2B+18) and Delta=C0 d.
Then h=p+2Delta+3<=(1+2C0)p+3 for p>=2. This pays a fixed multiplicative
precision factor; PROOF.md states the height induction and exact-half
argument for the new word. Any extra positive-rank child changes the
moment and requires repricing, even if its occurrence count is fixed.

I credit PR2979's authors for the complete word/profile, Nick Petalas for
PR3342's finite-transfer audit, Douglas Colkitt for the interval engine, and
the PR2287/3385 source-relative layer and B1/native lineage. I used OpenAI
Codex source-analysis agents to check the moment and exponents. I claim no
independent human or formal-kernel verification.
