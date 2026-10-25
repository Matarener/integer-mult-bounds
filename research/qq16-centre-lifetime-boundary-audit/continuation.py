#!/usr/bin/env python3
"""Independent constant-cover boundary audit; no predecessor executable imports.
Apache-2.0. Chris R / Clear1nsight with OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip,hashlib,json
from pathlib import Path

PINS={
'research/joint-query/certificate.json.gz':'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7',
'research/qq16-line-normalized-decoder/WORD.json':'5623b9cd62635d47f84e78135d817cfddec7ae31c154c565bf6e16cf5ed75475',
'research/qq16-line-normalized-decoder/PROOF.md':'0a0995e70f2a64c15cdd1aee66634d1ba221cbcb2a7cfa3a4d4950a37d0e143a',
}
DEMAND_WORD_PIN='f513d235b8206211a4716d013a6dacf34aaebda6839da721b0231981cb8b905e'
def need(ok,reason):
 if not ok: raise ValueError(reason)
def sha(b):return hashlib.sha256(b).hexdigest()
def invoice(w):
 c=Counter(e[0] for e in w)
 for e in w:
  if e[0]=='add':
   q=abs(Q(e[3]));need(q in (1,Q(1,4)),'unpriced scalar')
   c['unit_ADD' if q==1 else 'quarter_ADD']+=1
 c['scalar_allowance']=8*c['unit_ADD']+12*c['quarter_ADD']+2*c['clear']
 c['native_wrappers']=2*c['line']
 return dict(sorted(c.items()))
def run(repo,demand):
 raw={}
 for name,pin in PINS.items():
  raw[name]=(repo/name).read_bytes();need(sha(raw[name])==pin,'source:'+name)
 draw=(demand/'WORD.json').read_bytes();need(sha(draw)==DEMAND_WORD_PIN,'demand word')
 packet=json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
 A,T,U=map(tuple,(packet['A_ports'],packet['T_ports'],packet['U_ports']));V=A+T
 R=[[Q(row.get(str(p),0)) for p in range(112)] for row in packet['R_rows']]
 word=json.loads(raw['research/qq16-line-normalized-decoder/WORD.json']);dw=json.loads(draw)
 checkpoints=[i for i,e in enumerate(word) if e==['checkpoint','original_F0_outputs']]
 need(checkpoints==[2740],'checkpoint changed');suffix=word[2741:]
 need(suffix[0]==['add','W0','Z0','1'],'first continuation event changed')
 # Read-before-write audit treats ADD as read-modify-write, including old dst.
 written=set();needed=set();first={}
 for i,e in enumerate(suffix,2741):
  if e[0]=='add':
   for name in e[1:3]:
    if name not in written:needed.add(name);first.setdefault(name,i)
   written.add(e[1])
  elif e[0]=='clear':written.add(e[1])
  elif e[0] in ('begin','end'):pass
  else:raise ValueError('unexpected suffix op')
 expected={s+str(p) for s in 'ZW' for p in range(112)}
 need(needed==expected,'suffix input contract')
 supplied={'W'+str(p) for p in U};missing=needed-supplied
 need(len(missing)==128,'missing boundary count')
 need(set(e[1] for e in dw[-16:] if e[0]=='clear' and e[2]=='identity')=={'W'+str(p) for p in V},'selected temp disposal')
 def query(bank,subset):return [sum(R[k][p]*bank[p] for p in subset) for k in range(8)]
 def inject(q,subset):return [sum(R[k][p]*q[k]/4 for k in range(8)) if p in subset else Q(0) for p in range(112)]
 def plus(x,y,c=1):return [a+c*b for a,b in zip(x,y)]
 def zero():return [Q(0)]*112
 def invert_f0(x1,y1):
  f=query(x1,T);c=query(x1,A);kf=inject(f,U)
  x0=[x1[p]+kf[p] if p in U else Q(0) for p in range(112)]
  ru=query(x0,U);old_a=[f[k]-c[k]-ru[k] for k in range(8)]
  ia=inject(old_a,A);it=inject(c,T)
  for p in V:x0[p]=ia[p] if p in A else it[p]
  y0=[y1[p]-x1[p] if p in U else x1[p]+y1[p]-x0[p] for p in range(112)]
  return x0,y0
 def forward(x,y):
  f=query(x,range(112));c=query(x,T);kf=inject(f,U+T);old=inject(c,A)
  x1=[x[p]-kf[p] if p in U else old[p] if p in A else kf[p] for p in range(112)]
  y1=[y[p]+x1[p] if p in U else x[p]+y[p]-x1[p] for p in range(112)]
  future=inject(query(y1,U+T),A);u=plus(y1,future)
  a=query(x1,T);b=query(u,range(112));ku=inject(a,U);pa=inject(a,T);pb=inject(b,T)
  y2=[y1[p]+ku[p] if p in U else u[p] if p in A else u[p]-pb[p]-11*pa[p] for p in range(112)]
  x2=[x1[p]-y1[p] if p in U else x1[p]+y1[p]-y2[p] for p in range(112)]
  return x2,y2,x1,y1
 def project(y2):
  correction=inject(query(y2,range(112)),U)
  return [y2[p]-correction[p] for p in U]
 def replay_suffix(x1,y1,events=None):
  state={s+str(p):bank[p] for s,bank in [('Z',x1),('W',y1)] for p in range(112)}
  active=set()
  for e in (suffix if events is None else events):
   op=e[0]
   if op=='add':state[e[1]]+=Q(e[3])*state[e[2]]
   elif op=='clear':state[e[1]]=Q(0)
   elif op=='begin':
    active={s+str(k) for s in 'FG' for k in range(8)}
    for i,name in enumerate(sorted(active)):state[name]=Q(i+17) # adversarial private dirt
   elif op=='end':
    need(all(state[name]==0 for name in active),'suffix scratch leak')
    for name in active:del state[name]
    active=set()
  need(not active,'unterminated suffix')
  return [state['Z'+str(p)] for p in range(112)],[state['W'+str(p)] for p in range(112)]
 # Every omitted boundary coordinate has a valid original input, with demanded
 # y1_U identically zero. Inverting then forwarding each basis confirms legality.
 basis_count=0
 for name in sorted(missing):
  x1,y1=zero(),zero();(x1 if name[0]=='Z' else y1)[int(name[1:])]=Q(1)
  original=invert_f0(x1,y1);x2,y2,xx,yy=forward(*original)
  need((xx,yy)==(x1,y1),'F0 inverse basis legality '+name)
  need(project(y2)==[0]*96,'projection basis collision '+name)
  need(replay_suffix(x1,y1)==original,'literal suffix basis '+name)
  need(any(original[0]+original[1]),'nonzero original '+name);basis_count+=1
 # Stronger current-Y-only collision: all current Y are zero in both runs,
 # current X differs only at selected port0; the first suffix input Z0 differs.
 x1,y1=zero(),zero();x1[0]=1
 original=invert_f0(x1,y1);x2,y2,xx,yy=forward(*original)
 need(x2==x1 and y2==zero(),'current-Y collision')
 need(replay_suffix(x1,y1)==original,'collision suffix')
 # Mutate an actual dependency and a live final scratch clear, not source hashes.
 bad=[list(e) for e in suffix];bad[0][2]='Z1'
 need(replay_suffix(x1,y1,bad)!=original,'missing first Z0 dependency control')
 k=next(k for k in range(8) if R[k][0]);victim='G'+str(k)
 last_clear=max(i for i,e in enumerate(suffix) if e==['clear',victim,'identity'])
 bad=[list(e) for i,e in enumerate(suffix) if i!=last_clear]
 rejected=False
 try: replay_suffix(x1,y1,bad)
 except ValueError as e:rejected=str(e)=='suffix scratch leak'
 need(rejected,'scratch disposal negative control')
 encode=lambda v:{str(p):str(x) for p,x in enumerate(v) if x}
 # Full-phase mismatch: identity has no coefficients, F17 has linear coeff1
 # on e0; constant-array witness above is semantic, this separate statement
 # concerns the universal typed boundary, not its zero specialization.
 result={
 'status':'PASS_LITERAL_SUFFIX_BOUNDARY_OBSTRUCTION','scope':'PR2707 F0-inverse suffix consumes 224 F17 x1/y1 fields; PR3952 alone supplies96. Not a lower bound for new decoders using retained borrowed inputs.',
 'pins':PINS,'demand_word_sha256':DEMAND_WORD_PIN,
 'checkpoint_zero_based_event':2740,'first_suffix_zero_based_event':2741,'first_suffix_instruction':suffix[0],
 'entry_read_count':len(needed),'entry_missing_count':len(missing),'missing_fields':sorted(missing),'first_read':dict(sorted(first.items())),
 'supplied':{'W_U':96,'W_selected':'zero in identity frame, owned temps','Z':'absent','borrowed_current_XY':'still available but not x1/y1 and not owned'},
 'suffix_invoice':invoice(suffix),'full_decoder_invoice':invoice(word),'projected_invoice':invoice(dw),
 'negative_controls':['replace first Z0 read with Z1 changes original output','omit final live G scratch CLEAR rejects scratch leak'],
 'complete_missing_basis_checks':basis_count,'current_Y_zero_collision':{'current_X':encode(x2),'current_Y':encode(y2),'demanded_y1_U':'all zero','checkpoint_x1':encode(xx),'original_x0':encode(original[0]),'original_y0':encode(original[1]),'first_suffix_W0_after_add':'1 versus 0'},
 'frame_obstruction':{'cleared_W0':'identity','required_W0':'F17','differing_phase_coefficient':{'coordinate':0,'identity':0,'F17':1}},
 'retirement_conclusion':'No centre retirement established: true recovery continuation needs128 additional boundary values. The complete retained fallback costs336 H1,464 maps,25840 scalar primitives; private peak16. Projection cleanup cannot establish retirement of unrelated producer centre work. The root provenance audit must decide whether those charges exist in the actual QQ16 source.',
 }
 need(result['suffix_invoice']['scalar_allowance']==10144,'suffix price')
 need(result['full_decoder_invoice']['line']==336 and result['full_decoder_invoice']['scalar_allowance']==25840,'full price')
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--demand',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 result=run(a.repo,a.demand);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status']);print('128 omitted-boundary basis checks; exact all-zero-current-Y collision; suffix scalar10144/full scalar25840.')
