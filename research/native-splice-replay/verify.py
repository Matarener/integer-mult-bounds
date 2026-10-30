"""Whole-word source binding, prefix audit and rejection controls. Apache-2.0."""
from pathlib import Path
import json,sys,types,copy
HERE=Path(__file__).resolve().parent
spec=types.ModuleType('native_splice_authenticated');spec.__file__=str(HERE/'install.py')
sys.modules[spec.__name__]=spec;exec(compile((HERE/'install.py').read_bytes(),spec.__file__,'exec'),spec.__dict__)
B=spec

def rejects(action,label):
    try:action()
    except (ValueError,KeyError,IndexError,StopIteration):return
    raise ValueError('Invalid control accepted: '+label)

def verify():
    words,chart,v,n=B.sources(B.authenticated());patches=B.read('PATCHES.json')
    new,local=B.install(words,patches,n.primitive_allowance)
    B.need(new==B.read('NATIVE.json'),'Committed full native artifact matches guarded generator')
    segments=B.retained_event_segments(words,local)
    for direction in ('forward','backward'):
        mapped=[]
        for segment in segments[direction]:
            lo,hi=segment['old_range'];start=segment['new_start']
            B.need(words[direction][lo:hi+1]==new[direction][start:start+hi-lo+1],'Exact surviving event range')
            mapped.extend(i for i in range(lo,hi+1) if words[direction][i][0]!='scalar')
        B.need(mapped==[i for i,e in enumerate(words[direction]) if e[0]!='scalar'],'Every inherited physical event retains an index mapping')
    original=B.check_whole(words,chart,v,n);modified=B.check_whole(new,chart,v,n)
    for direction,old_cost,new_cost in [('forward',158120,158020),('backward',158168,158068)]:
        a=original[direction]['prefix'];b=modified[direction]['prefix']
        B.need(a['real_scalar_allowance']==old_cost and b['real_scalar_allowance']==new_cost,'Complete strict scalar saving')
        for k in ['paid_profile','paid_rank_mass','independent_persistent_input_fields','independently_initialized_owned_C_fields']:
            B.need(a[k]==b[k],'Retained paid profile and field stock')
        for k in ['max_formal_row_l1','max_abs_coefficient','max_abs_numerator','max_denominator']:
            B.need(a['prefix'][k]==b['prefix'][k],'Unchanged global ideal prefix envelope')
        B.need(b['all_408_helpers_exactly_restored_in_logical_coordinates'] and b['owned_C_fields_zero_at_exit'],'Full dirty helper and owned exit contract')
        rs=[r for r in local if r['direction']==direction]
        B.need(sum(r['old_cost'] for r in rs)==766 and sum(r['new_cost'] for r in rs)==666,'Local-to-whole invoice binding')
    # Corrupt the actual generated full word, not only a local stand-in.
    bad=copy.deepcopy(new);r=next(r for r in local if r['direction']=='forward' and r['old_cost']==52)
    bad['forward'].pop(r['new_indices'][1])
    rejects(lambda:v.replay(bad['forward'],chart,[],False,False),'missing borrowed-input restoration in complete word')
    bad=copy.deepcopy(new);r=next(r for r in local if r['direction']=='backward' and r['old_cost']==52)
    bad['backward'].pop(r['new_indices'][0])
    rejects(lambda:v.replay(bad['backward'],chart,[],True,False),'missing dirty-target subtraction in complete word')
    bad=copy.deepcopy(patches);bad[0]['source_indices'][0]+=1
    rejects(lambda:B.install(words,bad,n.primitive_allowance),'stale source window')
    bad=copy.deepcopy(patches);bad[0]['replacement'][0][2]+=1
    rejects(lambda:B.install(words,bad,n.primitive_allowance),'wrong scalar chart')
    bad=copy.deepcopy(patches);bad[0]['replacement'][0]=['center',0,0,1,9]
    rejects(lambda:B.install(words,bad,n.primitive_allowance),'hidden paid operation')
    return {'status':'PASS_NATIVE_SPLICE_FULL_IDEAL_REPLAY','local_rules':local,'retained_event_segments':segments,'original':original,'rewritten':modified,'columns_per_orientation':633,'persistent_fields':632,'original_owned_fields':1,'additional_owned_fields':0,'paid_calls_per_orientation':3562,'paid_rank_mass_per_orientation':5157,'scalar_saving_per_orientation':100,'unchanged_global_ideal_prefix_envelopes':True,'new_kappa':False,'rounded_induction_checked':False,'physical_phase_recipes_regenerated':False}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=json.loads(json.dumps(verify()))
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:B.need(result==B.read('RESULT.json'),'Deterministic semantic receipt')
    print(json.dumps({k:v for k,v in result.items() if k not in ('local_rules','retained_event_segments','original','rewritten')},sort_keys=True))
