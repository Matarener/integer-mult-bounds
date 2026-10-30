"""Fresh serial full-qualification B,C,C,B,B,C; fail closed at the first pair."""
import json
import statistics
import sys
from pathlib import Path
import guard
from source import payload, require

EXPECTED = json.loads(payload()['research/p104-integer-error-replay/RESULT.json'])
ORDER = [('B1','baseline.py'),('C1','candidate.py'),('C2','candidate.py'),
         ('B2','baseline.py'),('B3','baseline.py'),('C3','candidate.py')]


def receipt(label):
    folder=guard.HERE/'runs'/label
    measurement=json.loads((folder/'receipt.json').read_bytes())
    require(measurement['status']=='PASS','bounded command pass '+label)
    result=json.loads((folder/'stdout.txt').read_text().splitlines()[-1])
    require(result['mode']=='qualify' and result['receipt']==EXPECTED,'complete scientific receipt '+label)
    return measurement


def gate(labels):
    groups={arm:[receipt(label) for label in labels if label.startswith(arm)] for arm in 'BC'}
    rows={arm:dict(wall=statistics.median(x['wall_seconds'] for x in group),
                   cpu=statistics.median(x['usage']['user_seconds']+x['usage']['system_seconds'] for x in group))
          for arm,group in groups.items()}
    saving={key:1-rows['C'][key]/rows['B'][key] for key in ('wall','cpu')}
    require(min(saving.values())>=0.15,'15% complete-stage wall AND CPU gate')
    return dict(medians=rows,saving=saving,order=labels,complete_receipts_equal=True)


def main():
    require(len(sys.argv)==2 and sys.argv[1] in ('pair','remaining'),'pair or remaining')
    with (guard.HERE/'execution.lock').open('a') as lock:
        guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
        if sys.argv[1]=='pair':
            for label,script in ORDER[:2]:
                guard.run(label,script)
                receipt(label)
            summary=gate(['B1','C1'])
        else:
            gate(['B1','C1'])
            for label,script in ORDER[2:]:
                guard.run(label,script)
                receipt(label)
            summary=gate([label for label,_ in ORDER])
        (guard.HERE/('BENCHMARK-'+sys.argv[1]+'.json')).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
