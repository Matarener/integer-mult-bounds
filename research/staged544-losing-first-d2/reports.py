# SPDX-License-Identifier: Apache-2.0
"""Construct source-bound census/ledger summaries; ordinary use is read-only."""
from collections import Counter
from fractions import Fraction
import gzip,json
from pathlib import Path

def scale_height_bound(S,word):
    # Any retimed ADD crosses each SCALE in its unchanged native corridor at
    # most once. For two different ADDs this applies separately; selecting the
    # same ADD twice telescopes to a single original move (PR3942 reduction).
    maximum=0;max_scale=0;corridors=0
    for sec in S.PHASES:
      gates=word[sec]
      for lo,hi in S.R.segments(word,sec):
        corridors+=1;by_register=Counter()
        for g in gates[lo:hi]:
          if g[0]=='scale':
            q=Fraction(g[2],g[3]);num,den=abs(q.numerator),q.denominator
            if not num or num&(num-1) or den<=0 or den&(den-1):raise ValueError('non-dyadic power scale')
            exponent=(num.bit_length()-1)-(den.bit_length()-1)
            by_register[g[1]]+=abs(exponent);max_scale=max(max_scale,abs(exponent))
        for g in gates[lo:hi]:
          if g[0]=='add':maximum=max(maximum,by_register[g[1]]+by_register[g[2]])
    adds=[g for sec in S.PHASES for g in word[sec] if g[0]=='add']
    nb=max(abs(g[3]).bit_length() for g in adds);db=max(g[4].bit_length() for g in adds)
    return {'status':'constructive finite upper bound, not a measured maximum or uniform all-size precision tariff',
      'corridors':corridors,'maximum_absolute_scale_exponent':max_scale,
      'maximum_sum_absolute_scale_exponents_per_ADD_corridor':maximum,
      'all_two_edit_numerator_bits_at_most':nb+maximum,
      'all_two_edit_denominator_bits_at_most':db+maximum,
      'argument':'Each ADD conjugates only through existing corridor scales once; two selections of the same ADD telescope. All other coefficients and all native maps are unchanged.'}

def summaries(P,S):
    census={'schema_version':1,'scope':'Strictly losing first ADD, final displacement exactly two; second ADD unrestricted in legal scalar corridor; fixed interfaces.','providers':{}}
    ledger={'schema_version':1,'acceptance':'Scoped raw-moment obstruction; no new supplier, kappa or physical admission.','providers':{}}
    for tag in ('base','extra'):
        r=json.loads((P/('RESULT-'+tag+'.json')).read_text());c=r['pair_census'];v=c['variable_frame'];states=v['states']
        if sum(x['count'] for x in v['profiles'])!=v['counts']['second_cut_dimensions']:raise ValueError('combined price count')
        if sum(x['count'] for x in v['first_profiles'])!=len(states):raise ValueError('first profile count')
        if len(states)!=c['first_counts']['losing_subspace_records']-len(v['boundary_rejected']):raise ValueError('legal first inventory')
        if not all(x['certificate'] for x in v['profiles']):raise ValueError('unresolved sign')
        census['providers'][tag]={'first_price_cells':c['first_counts']['first_price_cells'],
          'neutral_price_cells_excluded':c['first_counts']['neutral_price_cells_excluded'],
          'legal_first_subspace_states':len(states),'rejected_first_states':len(v['boundary_rejected']),
          'second_prices':v['counts']['second_cut_dimensions'],'combined_signed_types':len(v['profiles']),
          'first_signed_types':len(v['first_profiles']),'max_first_quotient_dimension':c['max_first_quotient_dimension'],
          'first_interval_dimensions':len(c['first_intervals']),'exact_dirty_blocks':v['dirty_block_checks'],
          'first_by_phase':dict(sorted(Counter(x['first'][0] for x in states).items())),
          'whole_word_first_samples':len(c['dirty_validation']['whole_word_samples']),
          'whole_word_final_samples':len(c['dirty_validation']['whole_word_samples']),
          'single_move_premise_cases':r['single_move_candidates'],'combined_profiles':v['profiles']}
        word=json.loads(gzip.decompress((P/'inputs'/('BORROW-WORD-43'+tag+'.json.gz')).read_bytes()))
        ledger['providers'][tag]={**c['ledger'],'all_two_edit_scalar_height':scale_height_bound(S,word),
          'inherited_outer_profile':json.loads((P/'inputs/PROFILE.json').read_text()),
          'inherited_outer_profile_status':'Authenticated predecessor source only; no fresh outer reconstruction or admission.',
          'second_relaxed_recursive_children_range':[min(c['ledger']['recursive_children']+sum(x['delta']) for x in v['profiles']),max(c['ledger']['recursive_children']+sum(x['delta']) for x in v['profiles'])],
          'all_second_price_rank_masses':c['ledger']['rank_mass'],
          'local_status':'Proved finite chronological invoice and compositional dirty algebra under fixed word/frame contract.',
          'physical_status':'Unknown/inherited obligations are explicitly listed; no physically admitted implementation is claimed.'}
    census['total_second_prices']=sum(x['second_prices'] for x in census['providers'].values())
    return census,ledger
