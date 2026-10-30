"""Semantic binding of stored complete finite release; not a fresh full replay."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json
P=Path(__file__).parent
PINS_SHA='5f2a64d8df97ab0f94f7c1524af917945b6292be277e8bd2393ea4b8cf78f1ef'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def semantic(r,release,native,invoice,independent):
 price=read(P/'LEAD1-PRICE.json');profile=price['profile'];K=Q(price['root_interval'][0])-Q(1,10**46)-Q(1,10**70)
 need(r['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE','terminal complete status')
 need(Q(r['kappa'])==Q(r['kappa_decimal'])==Q(release['kappa_decimal'])==K>Q(read(P/'sources/T360-PRICE.json')['root_interval'][1]),'strict latest endpoint and both exact backoffs')
 need(r['profile']==profile and (r['replicas'],r['actual_expected_helpers'])==(360,408),'exact full profile')
 need(r['source_file_count']==652 and r['source_manifest_sha256']==native['manifest_sha256'],'actual v2 source')
 need(native['fresh_current_provider_count']==2 and native['reused_retained_parent'] is True,'actual native execution and retained parent scope')
 for tag in ('base','extra'):need(native['providers'][tag]['word_sha256']==sha(P/'lead1-words'/f'DELAYED-{tag}.json.gz'),'changed native words')
 need([s['name'] for s in r['stages']]==['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'] and all(s['exit_code']==0 for s in r['stages']),'all seven original stages with explicit preparatory reuse')
 need(invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE','finite invoice')
 need((invoice['physical'],invoice['live'],invoice['helpers'],invoice['centres'],invoice['private_zero_buffers'])==(323069,322560,408,8,91),'all physical stock')
 need(invoice['selected_local_paid_profile']=={k:n*3240 for k,n in {'1':2437,'2':724,'3':226,'4':102,'5':20,'8':8}.items()},'every actual local bill')
 checks=invoice['strict_checks'];need(set(checks)=={'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'} and all(v is True for v in checks.values()),'every strict finite cost check')
 bn=invoice['blocknorm'];need(bn['replicas']==360 and bn['physical_families']==323069 and bn['retained_payload_bits']==2048 and bn['required_reserve_bits']<2048,'precision and block stock')
 need(invoice['global_prefix_bits']==bn['actual_prefix_bits'] and invoice['charged_prefix_bits']==2048,'actual global precision')
 for pid in ('gauge44','extra'):
  for direction in ('forward','backward'):
   e=bn['endpoint_replay'][pid][direction];need(e['all_arbitrary_columns']==632 and e['helper_to_data_response_zero'] and e['centres_first_clear_and_terminal_zero']==8 and e['zero_buffers_allocated_and_cleared']==91,'arbitrary-dirty endpoints')
 need(independent['status']=='PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW' and independent['roles']==1321920 and independent['checked_whole_helper_widths']==1321920 and independent['checked_busy_family_windows']==1321920,'all roles in fresh original independent admission')
 need(all(row=={'1':2437,'2':724,'3':226,'4':102,'5':20,'8':8} for row in independent['local_profiles'].values()),'independent actual local invoices')
 return K

def check():
 d=P/'evidence/complete';need(PINS_SHA is not None and sha(d/'PINS.json')==PINS_SHA,'frozen receipt inventory');pins=read(d/'PINS.json')
 for name,h in pins['files'].items():need(Path(name).name==name and sha(d/name)==h,'stored receipt '+name)
 r=read(d/'RESULT.json');release=read(d/'RELEASE-RECEIPT.json');native=read(d/'NATIVE-RECEIPT.json');invoice=read(d/'PREFIX-AND-INVOICE.json');independent=read(d/'INDEPENDENT.json');semantic(r,release,native,invoice,independent)
 need(r['release_receipt_sha256']==sha(d/'RELEASE-RECEIPT.json') and r['native_receipt_sha256']==sha(d/'NATIVE-RECEIPT.json') and r['package_manifest_sha256']==sha(d/'PACKAGE-MANIFEST.json')==release['manifest_sha256'],'full receipt hash chain')
 coverage=read(d/'REUSE-COVERAGE.json');need(coverage['status']=='AUTHENTICATED_PREPARATORY_STAGE_REUSE_AFTER_DECLARED_EDIT_BINDING_REPAIR' and r['reuse_coverage_sha256']==sha(d/'REUSE-COVERAGE.json'),'explicit preparation reuse')
 need(read(d/'SOURCE-DERIVATION.json')['new_manifest']==r['source_manifest_sha256'],'derived source binding')
 stages=read(d/'VERIFY-STAGES.json');need(all(s['exit_code']==0 for s in stages) and 'delayed-release-independent-review' in {s['name'] for s in stages} and 'staged3605-review' in {s['name'] for s in stages},'predecessor and new reconstruction checks')
 strict=read(d/'STRICT-STAGES.json');need([s['name'] for s in strict]==['bind','emit','audit','invoice','assembly','admission','bit','independent'] and all(s['exit_code']==0 for s in strict),'complete strict finite admission')
 need(len(read(d/'ADMISSION-CONTROLS.json')['rejected_controls'])==139 and len(read(d/'GEOMETRY-CONTROLS.json')['rejected'])==6,'retained semantic controls')
 return 'PASS_AUTHENTICATED_STORED_COMPLETE_RELEASE_NOT_FRESH_REPLAY'
if __name__=='__main__':print(check())
