"""Fresh cold BCCBBC; full original and every new finite/native check billed."""
import json,statistics,sys
import guard
guard.SOURCE=guard.HERE.parent/'feasibility'
guard.CLOSURE=tuple(sorted(str(p.relative_to(guard.SOURCE)) for p in guard.SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts))+('/usr/lib/python3.12/fractions.py',)
guard.AGGREGATE=600
sys.path.insert(0,str(guard.SOURCE))
from frozen import payload,require
EXPECTED=json.loads(payload()['research/p104-single-pass-qualification/RESULT.json'])
ORDER=[('B1','full_B.py'),('C1','full_C.py'),('C2','full_C.py'),('B2','full_B.py'),('B3','full_B.py'),('C3','full_C.py')]

def receipt(label):
    p=guard.HERE/'runs'/label
    r=json.loads((p/'receipt.json').read_text());require(r['status']=='PASS','full bounded command '+label)
    out=json.loads((p/'stdout.txt').read_text().splitlines()[-1]);require(out['mode']=='qualify' and out['receipt']==EXPECTED,'unchanged full scientific receipt '+label)
    if label.startswith('C'):
        rows=[json.loads(x) for x in (p/'stdout.txt').read_text().splitlines() if x.startswith('{')]
        require(sum(x.get('status')=='PASS_COMPLETE_NATIVE_COVERAGE' for x in rows)==1,'native and compiler coverage '+label)
    return r

def gate(labels):
    groups={arm:[receipt(label) for label in labels if label.startswith(arm)] for arm in 'BC'}
    medians={arm:dict(wall=statistics.median(x['wall_seconds'] for x in rows),cpu=statistics.median(x['usage']['user_seconds']+x['usage']['system_seconds'] for x in rows)) for arm,rows in groups.items()}
    saving={k:1-medians['C'][k]/medians['B'][k] for k in ('wall','cpu')}
    result=dict(medians=medians,saving=saving,order=labels,all_full_receipts_equal=True,cold_compile_included=True)
    (guard.HERE/('GATE-'+str(len(labels))+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    require(min(saving.values())>=.15,'15% complete wall AND CPU gate')
    return result

require(len(sys.argv)==2 and sys.argv[1] in ('pair','remaining'),'pair or remaining')
with (guard.HERE/'execution.lock').open('a') as lock:
    guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
    if sys.argv[1]=='pair':
        for label,script in ORDER[:2]:guard.run(label,script);receipt(label)
        result=gate(['B1','C1'])
    else:
        gate(['B1','C1'])
        for label,script in ORDER[2:]:guard.run(label,script);receipt(label)
        result=gate([x[0] for x in ORDER])
    print(json.dumps(result,sort_keys=True))
