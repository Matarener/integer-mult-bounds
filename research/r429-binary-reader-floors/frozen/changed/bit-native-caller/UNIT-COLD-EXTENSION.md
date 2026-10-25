# Eleven terms in two one-coordinate extensions still cost at least56

Let D be the actual dimension9 reader code. Allow source rows in
D+<unit_b> and target columns in D+<unit_a>, for any two live coordinates.
No eleven-term binary factorization of M=KR in these spaces has total
rational source/target pairing tariff<=55. This rejects the proposed
nine-hyperplane-plus-two-cold-tail mechanism. It does not cover larger
extensions or tariff56..59.

The executable checks every one of the56,721 nonzero codeword/unit toggles.
All rank8 statements have modular rank8 certificates. Every rank7 statement
has a modular rank7 lower certificate and an exact rational normal witness.
The sole lower-span direction is the unit itself. Apart from the nine old
hyperplane code labels, only f_a=M[a,:] can become a new hyperplane code
label in D+<unit_a>; its toggle f_a+unit_a is the cap with live normal a.
The old labels may also be toggled when a lies within their cap. Thus the
rank7 code parts have ten possible labels, with some optional unit flags.

Project both extension spaces onto D. Rank(M)=9 forces at least nine terms
with nonzero code parts on both sides. Each such high/high term pairs spans
of dimensions>=7 and costs at least6. Ten high/high terms cost at least60.
A putative bill<=55 therefore has exactly nine, with baseline54 and at most
one excess unit. At least one side has all nine spans7: a span8 on each side
either costs8 in one term or gives two terms of cost>=7. Transpose the actual
symmetric M if necessary so all nine source spans are7.

Their code parts form a basis selected from the ten labels. Across all111
source units, exactly638 such independent nine-row bases exist. For every
one, all nine exact dual target code parts are generic rank8 directions in
D. A target one-unit extension can make at most one of these nine distinct
directions rank7, namely its own f_a. At least eight target spans remain8,
so their core bill is at least8*7+6=62, contradicting<=55. No unit-flag SAT
or tail equation can repair this failed necessary basis condition.

Run `python3 -B unit_cold_extension.py` and
`python3 -O -B unit_cold_extension.py`. UNIT-COLD-EXTENSION.json stores the
complete111-unit span census,638 bases, exact dual code masks, root/code
data and hashes. There is no global floor60 claim: a nine-high/two-tail
profile at tariff56..59 may contain rank8 directions on both sides. Native
COPY/ERASE, dirty restoration and a new exponent are not established.

Root proposed the two-unit construction. This lane identified the additional
live-cap label, supplied the complete census and corrected the proof scope.
Substantial OpenAI Codex assistance; Apache-2.0.
