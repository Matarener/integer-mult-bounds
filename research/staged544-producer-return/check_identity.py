"""Exact scalar-prefix identity and explicit commuting release cuts."""
import gzip,json
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
V={544:Q(1),672:Q(1,2),676:Q(-1,2)}
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def core(gs):return [g[:-1] for g in gs if not(g[0]=='scale' and Q(g[2],g[3])==1)]
results=[]
for tag in ('base','extra'):
 old=load(P/'staged544'/f'PRE-{tag}.json.gz');new=load(P/'words'/f'BORROW-WORD-43{tag}.json.gz');values=[V.get(r,Q(0)) for r in range(704)]
 assert old['B'][43]==['add',208,544,1,2,[51]]
 for i,g in enumerate(old['B'][:247]):
  assert not any(rec[0]==i and values[rec[1]] for rec in old['warps']), 'non-scalar column encountered'
  if g[0]=='add':values[g[1]]+=Q(g[3],g[4])*values[g[2]]
  else:values[g[1]]*=Q(g[2],g[3])
 assert values==[V.get(r,Q(0)) for r in range(704)],'P v=v exact on all registers'
 for g in old['B'][:693]:assert g[1]!=544 or g[0]=='scale' and Q(g[2],g[3])==1
 for donor in (672,676):
  for g in old['B'][247:693]:
   assert not(g[0]=='add' and (g[1]==544 or g[2]==donor))
   assert not(g[0]=='scale' and g[1] in (544,donor) and Q(g[2],g[3])!=1)
  assert not any(247<=r[0]<=693 and r[1] in (544,donor) for r in old['warps'])
 expected=[]
 for i,g in enumerate(old['B']):
  if i==693:expected+=[['add',672,544,1,2,[]],['add',676,544,-1,2,[]]]
  if i!=43:expected.append(g)
 assert core(new['B'])==core(expected),'only declared two releases and deleted target read'
 assert core(new['A'])==core(old['A']) and core(new['restore'])==core(old['restore'])
 assert [r[1:3] for r in new['warps']]==[r[1:3] for r in old['warps']]
 for field in ['cut','compensation','precondition','initial_corrections','helper_final','removed','ports','centers','center_frames','target_levels']:
  assert new[field]==old[field],field
 assert new['start_extra']==dict(old['start_extra'],**{'544':[414,51]})
 results.append(dict(provider=tag,prefix_cut=247,release_cut=693,prefix_identity='P v=v',v={str(r):str(v) for r,v in V.items()},changed_scalar_word='delete B43, insert 672+=544/2 and676-=544/2 beforeB693; identity scales ignored',native_operator_ids_and_maps_unchanged=True))
print('PASS_EXACT_PREFIX_IDENTITY_AND_COMMUTING_RELEASES',flush=True)
