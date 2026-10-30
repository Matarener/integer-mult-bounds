"""Whole odd-E8 K native template; phase-complete emitted root cube.

All 15^3 product cubes use this same constructor with literal cube indices.
The default replay emits/checks cube(0,0,0); --cube a,b,c checks another
instance. Global geometry and the generic proof justify the structured
forall-family word without expanding131328000 ordinary ADD instructions.

Credits: Ali Romman's #5439 geometry; PR5464 polarized physical phase tools;
the retained original native/Clifford and coded-normalizer source lineage.
Apache-2.0; substantial OpenAI Codex assistance. No kappa/caller claim.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import product
from hashlib import sha256
import argparse,gzip,importlib.util,json,sys,time
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
PINS={'NORMALIZERS.json':'0a27b5be30a78c0f418860c65eea2dd4221fc026cf9f2c86b7a8e865ab4d42df','COVER.json':'151c03c9f527e1bc242e0e6d50bee51f7db3163e4a7ae6a9e54e129328f09f89',
      'clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def canonical(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:p[x.bit_length()-1]=x
 for j in sorted(p):
  for k in p:
   if k!=j and p[k]>>j&1:p[k]^=p[j]
 return tuple(p[j]for j in sorted(p,reverse=True))
def add(dst,src,q):
 for k,v in src.items():
  value=dst.get(k,F(0))+q*v
  if value:dst[k]=value
  else:dst.pop(k,None)
def calculate(cube_tuple=(0,0,0)):
 for name,pin in PINS.items():need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==pin,'pin '+name)
 geometry=load('wholeK_geometry',HERE/'geometry_tools.py');frames=load('wholeK_frames',HERE/'frame_tools.py');ce=load('wholeK_clifford',HERE/'inputs/clifford_exact.py')
 normal=json.loads((HERE/'inputs/NORMALIZERS.json').read_bytes());roots=list(zip(*normal['mode_columns']));labels=[p['q']for p in normal['ports']]
 cover=json.loads((HERE/'inputs/COVER.json').read_bytes());cubes=[]
 for ci,record in enumerate(cover['cover15']):
  ports=record['ports'];colors={p:j for j,side in enumerate(record['source_parity_classes'])for p in side};parity=[colors[p]for p in ports]
  K=[[F(int(i==j))-F(sum(a*b for a,b in zip(roots[ports[i]],roots[ports[j]])),4)for j in range(8)]for i in range(8)]
  need(all(sum(K[i][j]*K[j][k]for j in range(8))==int(i==k)for i,k in product(range(8),repeat=2)),'actual Weyl cube involution')
  need(all(sum(bool(v)for v in row)==4 and all(v in (0,F(1,2),F(-1,2))for v in row)for row in K),'actual full120 four signed half entries')
  need(all(not K[i][j]or parity[i]!=parity[j]for i,j in product(range(8),repeat=2)),'actual graph-derived cross parity')
  cubes.append({'root_support':ci,'ports':ports,'parity':parity,'K':K})
 need(len(cubes)==15 and len(cube_tuple)==3 and all(0<=i<15 for i in cube_tuple),'valid15^3 actual cube tuple')
 selected=[cubes[i]for i in cube_tuple];n=25
 U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j))for b in range(3)for j in range(1,9)]
 orth=geometry.ortho_basis(U)
 def qlabel(triple):
  raw=sum(labels[p]<<(9*j)for j,p in enumerate(triple))
  need(geometry.span_contains(U,raw),'actual port in U25')
  q=sum(geometry.dot(raw,b)<<j for j,b in enumerate(orth))
  need(geometry.dot(q,q)==1 and q!=(1<<25)-1,'ambient normone noncharacteristic source')
  return q
 def port(t):return sum(selected[j]['ports'][t[j]]*120**(2-j)for j in range(3))
 triples=list(product(range(8),repeat=3));ports=[port(t)for t in triples];local={p:i for i,p in enumerate(ports)}
 qs={port(t):qlabel([selected[j]['ports'][t[j]]for j in range(3)])for t in triples}
 parity={port(t):sum(selected[j]['parity'][t[j]]for j in range(3))&1 for t in triples}
 def scalar_row(t):
  out={}
  for axis in range(3):
   for j,value in enumerate(selected[axis]['K'][t[axis]]):
    if value:
     source=list(t);source[axis]=j;out[port(source)]=value/2
  for j,k,l in product(range(8),repeat=3):
   value=-selected[0]['K'][t[0]][j]*selected[1]['K'][t[1]][k]*selected[2]['K'][t[2]][l]/2
   if value:need(port((j,k,l))not in out,'single and triple scalar supports disjoint');out[port((j,k,l))]=value
  need(len(out)==76 and Counter(abs(v)for v in out.values())=={F(1,4):12,F(1,16):64},'literal oddK row76 with correct signed coefficients')
  need(all(parity[s]!=parity[port(t)]for s in out),'oddK entire support crossparity')
  return out
 Krows={port(t):scalar_row(t)for t in triples}
 need(all(Krows[r].get(s,F(0))==Krows[s].get(r,F(0))for r in ports for s in Krows[r]),'literal oddK symmetric')
 peak=[1];sparse,monomial=frames.install(ce,need,peak);R=ce.fourier(n);Q=ce.fourier(n,[0]);D=ce.fourier(n,range(1,n));definitions={}
 def word_id(word):
  word=json.loads(json.dumps(word));key=sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest();definitions.setdefault(key,word);return key
 def literal(word):
  op=ce.ident(n)
  for e in word:
   if e[0]=='P':a=ce.perm(n,e[1])
   elif e[0]=='D':a=ce.diag(n,e[1],e[2])
   elif e[0]=='X':a=ce.xgate(n,e[1])
   elif e[0]=='phase':a=ce.Op(n,ce.identity(n),[tuple(e)])
   else:need(e[0]=='C','known primitive');a=ce.cgate(n,e[1],e[2])
   op=op.then(a)
  return op
 def only_monomial(word):need(all(e[0]in('P','D','X','phase')for e in word),'no hidden Gaussian in wrapper')
 def grank(op):return ce.rank([x for x,z,p in op.tab[n:]])
 def path(before,axes,after,expected):
  only_monomial(before);only_monomial(after);actual=literal(before).then(ce.fourier(n,axes)).then(literal(after))
  need(actual.tab==expected.tab and grank(actual)==len(axes),'exact paid path signed tableau and rank')
  return {'before_monomial':word_id(before),'child_axes':list(axes),'after_monomial':word_id(after),'rank':len(axes),'absolute_phase_proof':'low-rank exact gauges; proved native full-conjugate anchor; remaining factors cancel literally'}
 normalizers={};wrapper_records={};entry_frames={};exit_frames={};full_anchors=[]
 def transvection(v):return tuple((1<<j)^(v if v>>j&1 else 0)for j in range(n))
 def compose(A,B):return tuple(ce.mv(ce.transpose(B,n),row)for row in A)
 def real_normalizer(q):
  if not q&1:G=transvection(1^q)
  else:
   j=next(j for j in range(1,n)if not(q>>j&1));G=compose(transvection((1<<j)^q),transvection(1^(1<<j)))
  need(ce.mv(G,1)==q and compose(G,ce.transpose(G,n))==tuple(1<<j for j in range(n)),'actual orthogonal line normalizer')
  z=sum((((row.bit_count()-1)//2)&1)<<j for j,row in enumerate(G))
  need(all((row.bit_count()-1-2*((z>>j)&1))%4==0 for j,row in enumerate(G)),'all-address weight congruence linear coefficients')
  phase=ce.diag(n,(0,)*n,tuple(2*((z>>j)&1)for j in range(n)))
  L=ce.perm(n,G).then(phase);need(grank(L)==0,'real normalizer ordinary')
  return L,{'G_rows':G,'Z_after_permutation':z,'full_gaussian_commutation_proof':'orthogonality removes all Z4 cross terms and wt(G^-1 x)-wt(x)=2z.x modulo4; hence L R L^-1=R exactly'}
 for p in ports:
  L,rec=real_normalizer(qs[p]);normalizers[p]=L;normalizers_key=word_id(L.circuit)
  own=ce.canonical_frame(n,[qs[p]]);input_X=monomial(Q.adjoint().then(L).then(own))
  entry_frames[str(p)]={'q25':qs[p],'own_line_frame':word_id(own.circuit),'normalizer_proof':rec}
  wrapper_records[str(p)]={'input_X':word_id(input_X.circuit),'input_Y':normalizers_key,'output_X':word_id(L.adjoint().circuit)}
 # All original logical geometric inputs u_s and v_r remain independent;
 # u_s=L_s Q^-1 x_s, v_r=L_r y_r are invertible functions of original x,y.
 rows={('X',p):{('X',p):F(1)}for p in ports};rows.update({('Y',p):{('Y',p):F(1)}for p in ports})
 charts={('X',p):'line:'+str(p)for p in ports};charts.update({('Y',p):'ground'for p in ports})
 expected={k:dict(v)for k,v in rows.items()}
 for r,row in Krows.items():
  for s,value in row.items():expected['Y',r]['X',s]=value
 paid=Counter();ordinary=Counter();program=[];group_records=[];common_paths={};source_paths={};reader_paths={};path_applications=0
 def apply_mono(role,p,key,name):
  word=definitions[key];only_monomial(word);ordinary.update(e[0]for e in word);program.append(['MONOMIAL',role,p,key,name])
 def paid_path(role,p,target,record):
  nonlocal path_applications
  old=charts[role,p];program.append(['PAID_PATH',role,p,old,target,record]);charts[role,p]=target;paid[record['rank']]+=1;path_applications+=1
  for name in ['before_monomial','after_monomial']:ordinary.update(e[0]for e in definitions[record[name]])
 for p in ports:apply_mono('X',p,wrapper_records[str(p)]['input_X'],'normalized_virtual_Q_entry');apply_mono('Y',p,wrapper_records[str(p)]['input_Y'],'real_reader_entry')
 for source_parity in [0,1]:
  sources=sorted(p for p in ports if parity[p]==source_parity);readers=sorted(p for p in ports if parity[p]!=source_parity)
  S=list(canonical(qs[p]for p in sources));other=list(canonical(qs[p]for p in readers))
  need(len(sources)==len(readers)==256 and len(S)==len(other)==9,'two actual256port9spaceclasses')
  need(all(not geometry.dot(a,b)for a in S for b in other),'actual orthogonal classes')
  Phi=ce.canonical_frame(n,S);cols=ce.basis_extend(S,n);Kframe=frames.native_K(ce,cols);chart='S9:'+str(source_parity)
  T,anchor=frames.native_full_conjugate(ce,need,monomial,cols);full_anchors.append({'role':'source_full_exit','source_parity':source_parity,**anchor})
  reader_entry=path(Kframe.adjoint().circuit,range(9),Kframe.circuit,Phi)
  source_exit=path(Kframe.adjoint().circuit,range(9,n),T.circuit,Phi.adjoint().then(R))
  common_paths[str(source_parity)]={'S9_basis25':S,'frame_word':word_id(Phi.circuit),'reader_entry':reader_entry,'source_exit':source_exit}
  for p in sources:
   q=qs[p];own=ce.canonical_frame(n,[q]);flag=[q]
   for v in S:
    if len(geometry.basis(flag+[v]))>len(flag):flag.append(v)
   need(len(flag)==9,'actual source ownline nested in S9')
   flags=ce.basis_extend(flag,n);Ks=frames.native_K(ce,flags);small=frames.flag_frame(ce,flags,1);wide=frames.flag_frame(ce,flags,9)
   before=monomial(own.adjoint().then(small));after=monomial(wide.adjoint().then(Phi))
   record=path(before.circuit+Ks.adjoint().circuit,range(1,9),Ks.circuit+after.circuit,own.adjoint().then(Phi))
   source_paths[str(p)]=record;paid_path('X',p,chart,record)
  for p in readers:paid_path('Y',p,chart,reader_entry)
  for r in readers:
   for s,value in sorted(Krows[r].items()):
    need(charts['X',s]==charts['Y',r]==chart,'every actual source/read scalar ADD shares one literal frame')
    add(rows['Y',r],rows['X',s],value);program.append(['ADD','Y',r,'X',s,value.numerator,value.denominator,chart]);ordinary['ADD']+=1
  for p in sources:paid_path('X',p,'full25',source_exit)
  for p in readers:
   q=qs[p];V=S[:]
   for v in ce.nullspace((q,),n):
    if len(geometry.basis(V+[v]))>len(V):V.append(v)
   need(len(V)==24 and all(not geometry.dot(q,v)for v in V),'actual reader qperp24 contains S9')
   vcols=ce.basis_extend(V,n);Kv=frames.native_K(ce,vcols);low=frames.flag_frame(ce,vcols,9);target=frames.flag_frame(ce,vcols,24)
   before=monomial(Phi.adjoint().then(low));record=path(before.circuit+Kv.adjoint().circuit,range(9,24),Kv.circuit,Phi.adjoint().then(target))
   reader_paths[str(p)]=record;exit_frames[str(p)]={'q25':q,'qperp24_basis25':V,'frame_word':word_id(target.circuit)};paid_path('Y',p,'qperp24:'+str(p),record)
   # D L^-1 Phi_V^-1 = Q^-1 L^-1 (R Kv R^-1) C_last Kv^-1.
   # Both sides have the same exact phase by literal cancellations and [L,R]=0.
   Tv,anch=frames.native_full_conjugate(ce,need,monomial,vcols);full_anchors.append({'role':'reader_output_wrapper','port':p,**anch})
   low_word=Kv.adjoint().then(ce.fourier(n,[24])).then(Tv).then(normalizers[p].adjoint()).then(Q.adjoint())
   desired=target.adjoint().then(normalizers[p].adjoint()).then(D)
   need(low_word.tab==desired.tab and grank(low_word)==0,'reader ordinary wrapper exact tableau and algebraic full-rank cancellation')
   output_Y=monomial(low_word);wrapper_records[str(p)]['output_Y']=word_id(output_Y.circuit)
  group_records.append({'source_parity':source_parity,'source_ports':sources,'reader_ports':readers,'S9_basis25':S,'opposite9_basis25':other})
 for p in ports:apply_mono('X',p,wrapper_records[str(p)]['output_X'],'autonomous_source_D_exit');apply_mono('Y',p,wrapper_records[str(p)]['output_Y'],'reader_D_normalization')
 need(rows==expected,'all1024 independent geometric input columns exact K-only side transfer')
 need(paid=={8:512,9:512,15:512,16:512}and ordinary['ADD']==38912,'complete literal native K paid and ADD bill')
 need(ordinary=={'P':7680,'D':7680,'X':3072,'phase':3072,'ADD':38912},'all normalized monomial wrappers and direct scalar work counted: '+str(ordinary))
 # Meaningful phase/frame/scalar controls, executed on the emitted gates.
 first_source=group_records[0]['source_ports'][0];first=source_paths[str(first_source)]
 phase_reference=literal(definitions[first['before_monomial']]).then(ce.fourier(n,first['child_axes'])).then(literal(definitions[first['after_monomial']]))
 wrong=phase_reference.then(ce.Op(n,ce.identity(n),[('phase',1)]));need(wrong.tab==phase_reference.tab and sparse(wrong)!=sparse(phase_reference),'actual phase-i mutation detected')
 P0=literal(definitions[common_paths['0']['frame_word']]);P1=literal(definitions[common_paths['1']['frame_word']]);wrong_frame_rank=grank(P0.adjoint().then(P1));need(wrong_frame_rank==2,'different parity S9 charts require real rank2 transport')
 first_reader=group_records[0]['reader_ports'][0];missing_source=next(iter(Krows[first_reader]));bad=dict(rows['Y',first_reader]);bad.pop(('X',missing_source));need(bad!=expected['Y',first_reader],'omitted emitted ADD changes an actual independent source column')
 endpoint_rows={'source_identity_fields':ports,'reader_rows':{str(r):[[role,s,value.numerator,value.denominator]for (role,s),value in sorted(rows['Y',r].items())]for r in ports}}
 v=120**3
 template={'schema':'full120-odd3-E8-whole-K-native-family-template/v1','cube_parameter_domain':[15,15,15],
  'constructor':'core.calculate(cube_tuple); concatenate returned program in lexicographic cube_tuple order',
  'literal_cube_partition':[{'root_support':c['root_support'],'ports':c['ports'],'relative_sign_parity':c['parity']}for c in cubes],
  'base_K_coefficients':[[[str(v)for v in row]for row in c['K']]for c in cubes],
  'scalar_operator':'K_odd=(K1+K2+K3-K1 K2 K3)/2; factor operators act on distinct owner selector coordinates',
  'physical_ambient':25,'orthonormal_basis_raw27':orth,'whole_original_inputs':2*v,
  'whole_paid_profile':{str(r):v for r in [8,9,15,16]},'whole_ordinary_profile':{'ADD':76*v,'P':15*v,'D':15*v,'X':6*v,'phase':6*v},
  'helpers':0,'owned_fields':0,'COPY':0,'CLEAR':0,
  'phase_uniformity':'Every generated paid path uses only exact low-rank monomial gauges and the proved analytic native full-conjugation anchor; generic Lagrangian and phase proofs cover every family member. Default finite replay fully compiles cube000, not all3375 phase instances.',
  'ordinary_uniformity':'All owner coefficients applied once at field width f; phase theta lifted as i^(f theta). No tensor power of the owner matrix or packing discount.'}
 payload={'schema':'full120-odd3-E8-K-normalized-rootcase-word/v1','cube_tuple':cube_tuple,'source_pins':PINS,'axis_dimension':25,'port_order':ports,'field_roles':{str(p):[['X',p],['Y',p]]for p in ports},
  'normalized_entry_contract':'Every X_p=x_p and Y_p=y_p is an arbitrary independent physical ground-chart field.',
  'geometric_coordinate_contract':{'source':'After emitted ordinary input_X wrapper, physical X_p=Phi_[q_p] u_p with u_p=L_p Q^-1 x_p. Q^-1 is virtual inside the emitted monomial identity; no supplied Gaussian is assumed.','reader':'After ordinary input_Y wrapper physical Y_p=v_p=L_p y_p at ground.','scalar_rows':'logical_endpoint_rows track independent u_p,v_p; per-port exact incoming/outgoing factors yield the stated original-x,y normalized endpoint.'},
  'orthonormal_basis_raw27':orth,'groups':group_records,'definitions':definitions,'common_paths':common_paths,'source_paths':source_paths,'reader_paths':reader_paths,'entry_frames':entry_frames,'exit_frames':exit_frames,
  'normalization_wrappers':wrapper_records,'native_full_conjugate_anchors':full_anchors,'literal_scalar_K_rows':{str(r):[[s,c.numerator,c.denominator]for s,c in sorted(row.items())]for r,row in Krows.items()},'logical_endpoint_rows':endpoint_rows,'program':program}
 canonical_payload=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode();encoded=gzip.compress(canonical_payload,mtime=0)
 summary={'schema':'full120-odd3-E8-K-normalized-native-rootcase/v1','status':'PASS_PHASE_COMPLETE_K_NATIVE_ROOTCASE_AND_GENERIC_FAMILY_TEMPLATE','cube_tuple':cube_tuple,'axis_dimension':25,'source_pins':PINS,'original_main_inputs':1024,'source_fields':512,'reader_fields':512,'owned_fields':0,'helpers':0,'COPY':0,'CLEAR':0,
  'paid_profile':dict(sorted(paid.items())),'ordinary_literal_profile':dict(sorted(ordinary.items())),'paid_path_applications':path_applications,'all_original_scalar_columns_checked':1024,
  'normalized_entry':'All original x_i,y_i arbitrary independent at physical ground; all virtual-Q source-line entry wrappers are emitted ordinary monomials.',
  'normalized_endpoint':'F_K=diag(D,D) L(C_K Q^-1), C_K=diag(L_i^-1) K_odd diag(L_i), D=C_[1,25), Q=C_0',
  'source_endpoint':'D x_i on every independent original source x_i','reader_endpoint':'D(y_i+sum_j K_odd[i,j] L_i^-1 L_j Q^-1 x_j)',
  'code_contract':{'C_K_symmetric':True,'C_K_squared_identity':True,'C_K_commutes_full_R':True,'proof':'K_odd symmetric involution and real orthogonal direct-owner normalizer similarity; each L_i commutes R exactly'},
  'phase_compilation':{'low_rank_sparse_peak_support':peak[0],'native_full_conjugate_analytic_anchors':len(full_anchors),'source_input_wrappers':512,'reader_output_wrappers':512,'all_wrappers_monomial':True,'all_positive_widths':'literal one-copy phases tensor lift; phase opcode theta becomes i^(f theta); owner scalar coefficients applied once'},
  'mutation_controls':{'same_tableau_phase_i_rejected':True,'wrong_parity_common_chart_transport_rank':wrong_frame_rank,'missing_actual_ADD_changes_independent_endpoint':True},
  'logical_growth':{'source_max_row_l1':'1','reader_max_row_l1':'8','max_scalar_denominator_exponent':4,'proof':'Each reader retains its own v plus76 distinct independent u terms:12 magnitudes1/4 and64 magnitudes1/16. Sources unchanged; all physical charts/wrappers unitary.'},
  'scientific_program_payload_sha256':sha256(canonical_payload).hexdigest(),'environment_metadata':{'program_container_sha256':sha256(encoded).hexdigest(),'program_container_bytes':len(encoded)},
  'scope':'Whole local block-diagonal K native constructor, with phase-complete emitted cube instance and generic forall3375 proof plus independent all-family geometry. It does not implement H, install F3, close any outer caller, admit precision/work/storage, or improve kappa.',
  'new_kappa':False}
 return json.loads(json.dumps(summary)),json.loads(canonical_payload),encoded,json.loads(json.dumps(template))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--cube',default='0,0,0');args=ap.parse_args();cube=tuple(map(int,args.cube.split(',')));start=time.monotonic()
 summary,payload,encoded,template=calculate(cube)
 suffix=''if cube==(0,0,0)else'-'+'-'.join(map(str,cube));receipt=HERE/('K-MODULE'+suffix+'.json');program=HERE/('K-PROGRAM'+suffix+'.json.gz')
 if args.write:
  receipt.write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');program.write_bytes(encoded)
  (HERE/'K-TEMPLATE.json').write_text(json.dumps(template,sort_keys=True,indent=2)+'\n')
 else:
  old=json.loads(receipt.read_bytes());old.pop('environment_metadata',None);new=dict(summary);new.pop('environment_metadata',None)
  need(old==new,'frozen native K science receipt');need(json.loads(gzip.decompress(program.read_bytes()))==payload,'frozen canonical decompressed literal program');need(json.loads((HERE/'K-TEMPLATE.json').read_bytes())==template,'frozen whole-family template')
 print(json.dumps({k:summary[k]for k in ['status','cube_tuple','original_main_inputs','paid_profile','ordinary_literal_profile','scientific_program_payload_sha256','new_kappa']},sort_keys=True))
if __name__=='__main__':main()
