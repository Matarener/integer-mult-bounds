"""Explicit rational job recipes and positive finite fees; no exponent claim."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import gzip,json
from local_ir import need
def read(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gz'else json.loads(p.read_bytes())
def mm(a,b):return[[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def eye(n):return[[F(i==j)for j in range(n)]for i in range(n)]
def inv(a):
 n=len(a);w=[r[:]+[F(i==j)for j in range(n)]for i,r in enumerate(a)]
 for j in range(n):
  k=next(i for i in range(j,n)if w[i][j]);w[j],w[k]=w[k],w[j];z=w[j][j];w[j]=[v/z for v in w[j]]
  for i in range(n):
   if i!=j:
    z=w[i][j];w[i]=[v-z*y for v,y in zip(w[i],w[j])]
 return[r[n:]for r in w]
def project(f):
 b=[[F(x)for x in r]for r in f['B']]
 if not b:return[[F(0)]*8 for _ in range(8)]
 bt=list(map(list,zip(*b)));return mm(mm(bt,inv(mm(b,bt))),b)
def text(a):return[[str(x)for x in r]for r in a]
def digest(a):return sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def construct(root,write=False):
 root=Path(root);inp=root.parent/'inputs';data=root/'data';frames=read(inp/'FRAMES.json')['frames'];base=read(inp/'BASELINE-LOCAL.json.gz');ref=read(inp/'REFERENCE111.json.gz');controller=read(inp/'CONTROLLER.json');axes=read(inp/'ACTIVE-AXES.json');saved=read(inp/'BASELINE-RATIONAL-BINDING.json');glob=read(data/'GLOBAL-RESULT.json');I=eye(8);ports=[];Acols=[]
 need(len(ref['lines'])==111,'Actual orderedSOURCE111')
 for i,line in enumerate(ref['lines']):
  v=list(map(F,line));need(sum(x*x for x in v)==4,'ActualSOURCErootnorm4');P=[[x*y/4 for y in v]for x in v];K=[[I[a][b]-P[a][b]for b in range(8)]for a in range(8)]
  need(project(frames[str(base['start'][i])])==P and project(frames[str(base['final'][i])])==I and project(frames[str(base['start'][111+i])])==[[F(0)]*8 for _ in range(8)]and project(frames[str(base['final'][111+i])])==K,'Unchanged actualSOURCE/YrationalABI')
  u=[F(j==0)-v[j]/2 for j in range(8)];norm=sum(x*x for x in u);S=I if norm==0 else[[F(a==b)-2*u[a]*u[b]/norm for b in range(8)]for a in range(8)];A=[row[1:]for row in S];AT=list(map(list,zip(*A)))
  need(mm(list(map(list,zip(*S))),S)==I and [2*row[0]for row in S]==v and mm(A,AT)==K and mm(AT,A)==eye(7),'ExactSOURCEline/complementcoordinates')
  rho=[P[j]+A[j]for j in range(8)]+[row+[F(0)]*7 for row in AT];local8=[[F(a==b and a<8)for b in range(15)]for a in range(15)];want=[[P[a][b]if a<8 and b<8 else F(a==b and a>=8)for b in range(15)]for a in range(15)]
  need(mm(rho,rho)==eye(15)and mm(mm(rho,local8),rho)==want,'Actual15DwholefiberENTRY/RETURNchart')
  need(digest(text(rho))==saved['ports'][i]['chart_sha256'],'Unchangedfrozenroutebytes')
  ports.append({'port':i,'root':list(map(str,v)),'unit_line':list(map(str,[x/2 for x in v])),'orthogonal_complement_columns':text(A),'rho15':text(rho),'rho15_sha256':digest(text(rho))});Acols.append(A)
 partial={}
 for f in sorted(set(base['final'][222:])):
  p=project(frames[str(f)]);rank=frames[str(f)]['dim'];need(mm(p,p)==p and sum(p[i][i]for i in range(8))==rank,'Actualhelperendjobidempotent')
  if rank==8:need(p==I,'Actualfullhelper');continue
  need(rank==4,'Onlyactual4partialjobs');b=[[F(x)for x in r]for r in frames[str(f)]['B']];a=[[F(x)for x in r]for r in frames[str(f)]['A']];s=list(map(list,zip(*(b+a))));si=inv(s);q4=[[F(i==j and i<4)for j in range(8)]for i in range(8)];need(mm(mm(s,q4),si)==p,'Actualcanonicalrank4wholejobmatcher')
  partial[str(f)]={'rank':4,'native_P':text(p),'S_Q4_to_native':text(s),'S_inverse':text(si),'physical_input_ROW_route':'g->g*S_inverse','completed_return_route':'h->h*S'}
 need(len(partial)==3,'Threeactualdistinctpartial4projectors')
 templates=[];target_roles=[]
 for bank,term in enumerate(controller['diagonal']):
  selected=[j for j,a in enumerate(axes)if term>>(a['stage']+1)&1];need(term&1 and(sum(1<<(axes[j]['stage']+1)for j in selected)|1)==term,'Alltargetfactorsareactualretainedorthogonalaxes')
  centralfull=0 in selected;image=[a for j in selected if j for a in axes[j]['axes']];kernel=[a for j in range(1,18)if j not in selected for a in axes[j]['axes']];rank=(8 if centralfull else 1)+len(image)
  need(rank==1+7*len(selected)and len(image)+len(kernel)==119,'ExactMAINsourcejobrankanddisjointspectatoraxes')
  # The centralblock is either I8 or(unit_line,complementA); it is already
  # exactlyorthogonal above. Othercolumns are distinctcoordinatevectors.
  template={'id':f'MAIN_BANK_{bank}','bank':bank,'rank':rank,'native_target_phase_mask':int(term),'central_image':'I8'if centralfull else'unit_line[port]','central_kernel':'none'if centralfull else'complementA[port]','image_fresh_axes':image,'kernel_fresh_axes':kernel,'column_order':'imagecentral;imagefresh;kernelcentral;kernelfresh;futureambientidentityspectators','S':'Columnmatrixfromtheliteralrecipe; S*Q_rank*S^-1=P_native','inverse':'TransposeoftheorthogonalS; allfutureaxes>=127fixed','physical_input_ROW_route':'g->g*S_inverse','completed_return_route':'h->h*S'}
  templates.append(template)
  for port in range(111):target_roles.append({'original_owner':bank*111+port,'rank':rank,'matcher':template['id'],'port':port,'operator':'D_(P_line+selectedorthogonalstageblocks)','route_pair_required_in_generic_job_matching':True})
 for call in read(data/'CALLS.json'):
  begin=call['helper_owner_begin']
  for r in range(436):
   frame=base['final'][222+r];rank=frames[str(frame)]['dim'];target_roles.append({'original_owner':begin+r,'rank':rank,'matcher':'IDENTITY_FULL8'if rank==8 else'PARTIAL_FRAME_'+str(frame),'native_frame':frame,'route_pair_required_in_generic_job_matching':rank!=8})
 need(len(target_roles)==11400 and len(set(x['original_owner']for x in target_roles))==11400,'Exactlyoneindependenttargetperoriginal,noownedcredit')
 need(Counter(x['rank']for x in target_roles)==Counter({int(k):v for k,v in glob['targets'].items()}),'Jobrecipesexacttargetinvoice')
 route_fields=[x for x in target_roles if x['route_pair_required_in_generic_job_matching']];routes=[]
 for x in sorted(route_fields,key=lambda x:x['original_owner']):routes.append({'position':'BEFORE_COMPLETE_GLOBAL_BODY','owner':x['original_owner'],'matcher':x['matcher'],'port':x.get('port'),'direction':'S_inverse','whole_fiber':'g->g*S_inverse','no_live_owned':True})
 for x in reversed(sorted(route_fields,key=lambda x:x['original_owner'])):routes.append({'position':'AFTER_COMPLETE_GLOBAL_BODY','owner':x['original_owner'],'matcher':x['matcher'],'port':x.get('port'),'direction':'S','whole_fiber':'h->h*S','no_live_owned':True})
 # Evenidentitymainrecipescanbechargedbythisuniformbound; no numerical
 # optimizationusesanunchargedmatcher. Allroutesarebijectionson(role,g).
 n=11400;M=sum(glob['paid'].values());ops=glob['operation_counts'];raw=glob['expanded_event_count'];primitive_adds=ops['ADD']+ops['LOCAL_ADD']+ops['THIN_ADD'];copies=ops['LOCAL_COPY_QUERY']+ops['THIN_COPY'];clears=ops['LOCAL_PAID_CLEAR']+ops['SHADOW_PAID_CLEAR']+ops['THIN_PAID_CLEAR'];parking=4*(n+2)*M
 fees={'status':'POSITIVE_FINITE_PROGRAM_FEE_SCHEMA_NO_ORDINARY_SAVING_YET','raw_bit_IR_records':raw,'raw_record_cap_only':10**9,'raw_cap_guard':raw+2*M+2*n+144<10**9,'literal_VALUE_XOR_passes':primitive_adds,'compound_pointwiseCOPY_assignments':copies,'new_shadow_ZERO_INIT_passes':ops['SHADOW_PAID_INIT'],'all_paid_owned_CLEAR_passes':clears,'initial_owned_bank_ZERO_scans':2,'final_owned_bank_teardown_scans':2,'new_shadow_copy_ADDs_already_in_VALUE_count':18,
  'in_BODY_paid_MAINport_wholefiber_routes':ops['PAID_PORT_ROUTE'],'canonical_job_matching_route_pairs':len(route_fields),'canonical_job_matching_routes':len(routes),'of_these_partial4_helper_routes':144,
  'parent_parking':{'paid_child_calls':M,'allocated_parent_originals_plus_owned':n+2,'safe_inactive_and_IO_FIELD_pass_bound_perQUERY':4*(n+2),'total_FIELD_pass_bound':parking,'meaning':'BeforeeachQUERYparkinactiveparentoriginalsandBOTHownedbanks,copyactiveARRAYtochildIO; onreturnrestoreinactiveorderandparentheads/stacktop. Parentancestorregionsareneverswept. Thisisaconservativepositivefixedconstant,notasaving.'},
  'normalizer_and_ROW_route_costs':{'source_catalogue':'AllfixedrationalP/S/rho/targetrecipesincluded; chooseqavoidingallfiniteunits/denominators/rankwitnesses AFTERfiniteprogramcompile. No inheritednumericq/H threshold.','QUERY':'EachactualcurrentARRAYjobnormalizesonlyinthecompleteduniformprogram. Goodclassesuseorderedproperchild; badclassesusechargedlocal-ringfallback. Newrank4isfreshgeometricjobwithG22matcher,notoldticket.','wholefiber_route':'Useinheritedfixedrationalright-multiplicationstreamingprimitive,chargedO_(N,S,q)(V*w^(1-a_backend)), includinglowtypes/highcarry/counters/headreturn. NotfreeADDRESSgather.','symbolic_fixed_fee':'C_new(N,q)=C_stream*(rawVALUE+COPY+INIT+CLEAR+parkcounts)+SUM_FIXED_ROUTES C_route(N,q,S)+SUM_QUERY C_normalizer(N,q,P). Constantsarefinite/positiveandfixedBEFOREinputwidth. Thisreceipt doesNOTsupplyanumericalall-in1e9bound fornormalizers.'},
  'majorants':{'LOCAL_direction_bits':{k:v['majorant_bits']for k,v in read(data/'LOCAL-INVOICE.json')['directions'].items()},'GLOBAL_bits':glob['majorant_bits'],'GLOBAL_majorant':glob['majorant'],'scope':'Positivecancellationfreeenvelope regeneratedfromnewprogram. Old21/30bitthresholdsareNOTreused.'},
  'stock':{'original_productive_fields':11400,'owned_OUTPUT_credit':0,'per_primitive_GLOBAL_unit_owned_banks':2,'per_finite_DAG_allocation':'ReserveTWOwholeownedbanksforeachcompiledunitinstance(orconcurrentliveunit),withunit-scopedtagsandzeroINIT/CLEAR. NeverreuseoneC0perdepthwhenunits suspended.','child_source_on_owned':'AQUERYonacurrentownedSUMusesitastheactualchildtargetslot; correlatedvaluesarevalidarbitrary-inputinstances. ItdoesNOTaddanindependentparentinput. Descendantownbanksgetdistincttags.','row_split':'Originalunitrolewidthremains11400; twoownedbanksareworkstreams,notnewproductiveROWclasses. Freshdescendantrolesexcludeexposedparentfields.','asymptotic':'WithnewfixedfiniteN,B,q,source/park/tapeconstantsregenerated,theinheritedstocklog_q S=O_new(w loge)andborrow/restoreproofremainconditionalinputs. OldnumericH/prime/precisionthresholdsnotasserted.'},
  'pending_before_ordinary_bound':['Freshthree-tensor-tail/finitecompiler/primefallbackcertificateonnewP/T','Actualnewfixedconstants/H/reserve/cutoffchosenandchecked','Finiteleafbootstrapwithfrozenalready-establishedordinarybackend','Parentindependentvalidationandnorecordclaimuntilthen']}
 need(fees['raw_cap_guard']and primitive_adds==378039 and copies==1827 and clears==1845 and len(routes)==7248,'Regeneratedfinitefeeandroutecounts')
 result={'ports':ports,'partial_matchers':partial,'main_matcher_templates':templates,'targets':target_roles,'canonical_route_program':routes,'fees':fees}
 if write:
  for name,key in [('PORT-CHARTS.json','ports'),('PARTIAL-JOB-MATCHERS.json','partial_matchers'),('MAIN-JOB-MATCHERS.json','main_matcher_templates'),('TARGET-OWNERS.json','targets'),('JOB-MATCHING-ROUTES.json','canonical_route_program'),('FULL-FEES.json','fees')]:
   (data/name).write_text(json.dumps(result[key],indent=2)+'\n',encoding='utf-8')
 return result
if __name__=='__main__':
 result=construct(Path(__file__).resolve().parent,True);print(json.dumps({'status':'PASS_EXACT_SOURCE_CHARTS_AND_POSITIVE_FIXED_FEE_SCHEMA','target_owners':len(result['targets']),'explicit_canonical_routes':len(result['canonical_route_program']),'partial_routes':144,'new_bound':None}))
