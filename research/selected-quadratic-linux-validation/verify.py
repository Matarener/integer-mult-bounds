"""Check retained Linux evidence and source custody; run no scientific replay.

Cold reproduction is explicit in reproduce.py. This bounded checker does not
attest that a measurement occurred or replace the retained scientific checks.
Prepared for Clear1nsight with OpenAI Codex assistance; Apache-2.0.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import statistics
import tarfile

HERE = Path(__file__).resolve().parent
EXPECTED_STDOUT = '1975d01770a017b3f0b3a98a54c7c79b887d90ba0a2e1a77c37db05c385fa42b'
ARCHIVE_SHA256 = 'a3a4478938171072f7df7547f7b1e1d0ff080aa42083103450e7d02f509bfc26'
MANIFEST_SHA256 = '7be632febc51fa5040cdd06a86c1c4f8b95c2632cc885b49af05bba838b672be'
EXPECTED_INVENTORY = '95719901778f8c6651f9cab2bf171d87d6fb015569d6d22897e0d40e3e385fc5'
BENCHMARK = ('sample-1-literal','sample-2-quadratic','sample-3-quadratic',
             'sample-4-literal','sample-5-literal','sample-6-quadratic')
QUALIFICATION = ('qualification-normal','qualification-cross-optimized','qualification-optimized','qualification-cross-normal')

def require(ok, why):
    if not ok:
        raise ValueError(why)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pairs(rows):
    result = {}
    for key,value in rows:
        require(key not in result,'Duplicate JSON key')
        result[key]=value
    return result

def decode(raw):
    def bad(value):
        raise ValueError('Nonfinite JSON constant')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)

def same(left,right):
    return json.dumps(left,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(right,sort_keys=True,separators=(',',':'),allow_nan=False)

def finite_number(value):
    return type(value) in (int,float) and math.isfinite(value)

def check_source(archive=None,manifest_raw=None):
    archive=HERE/'inputs/PR5757.tar' if archive is None else archive
    manifest_raw=(HERE/'INPUT-MANIFEST.json').read_bytes() if manifest_raw is None else manifest_raw
    require(sha(manifest_raw)==MANIFEST_SHA256,'Source manifest binding')
    require(sha(Path(archive).read_bytes())==ARCHIVE_SHA256,'Official source export binding')
    manifest=decode(manifest_raw)
    require(manifest['source_head']=='53006fe6031dab5c23d5b7d1cf6a92f411a04a68','Exact source head')
    expected={r['path']:r for r in manifest['files']}
    require(len(expected)==len(manifest['files'])==54,'Complete source closure')
    with tarfile.open(archive,'r:') as stream:
        members=stream.getmembers()
        names=[m.name for m in members]
        require(len(names)==len(set(names))==55 and set(names)==set(expected)|{'.research-export.json'},'Exact export inventory')
        for member in members:
            require(member.isfile() and 0<=member.size<=4*1024**2,'Regular bounded export member')
            raw=stream.extractfile(member).read()
            if member.name=='.research-export.json':
                receipt=decode(raw)
                require(receipt['commit']==manifest['source_head'] and receipt['package']=='research/selected-quadratic-replay','Export origin')
                continue
            row=expected[member.name]
            require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Retained source bytes')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'Retained source Git blob')
    return manifest

def check_runs(rows,read_stdout,read_stderr,runner_hash,cross_expected):
    labels=BENCHMARK+QUALIFICATION
    require(type(rows) is list and [r.get('label') for r in rows]==list(labels),'All ordered benchmark and qualification runs')
    total=0.0
    inventory_hashes=set()
    environments=set()
    scientific_stdout=read_stdout(BENCHMARK[0])
    require(sha(scientific_stdout)==EXPECTED_STDOUT,'Bound complete scientific output')
    for row in rows:
        label=row['label']
        require(row['status']=='PASS' and type(row['exit']) is int and row['exit']==0,'Successful exact exit')
        require(row['termination'] is None and row['source_bytes_and_modes_unchanged'] is True,'No stop or source mutation')
        require(row['runner_sha256']==runner_hash and row['manifest_sha256']==MANIFEST_SHA256,'Actual runner and source manifest')
        if label.startswith('sample-'):
            expected_script='research/p104-helper-subspace-splits/verify.py' if label.endswith('literal') else 'research/selected-quadratic-replay/run.py'
        else:
            expected_script='research/selected-quadratic-replay/'+('cross.py' if label.startswith('qualification-cross-') else 'verify.py')
        require(row['script']==expected_script,'Complete expected entry point')
        require(finite_number(row['wall_seconds']) and 0<row['wall_seconds']<=600,'Bounded finite runtime')
        require(type(row['sampled_process_group_rss_bytes']) is int and 0<row['sampled_process_group_rss_bytes']<=1024**3,'Sampled group memory cap')
        usage=row['usage']
        require(type(usage['exit']) is int and usage['exit']==0,'Measured exit')
        require(type(usage['kernel_max_rss_kib']) is int and 0<usage['kernel_max_rss_kib']<=1024**2,'Kernel memory measurement')
        require(all(finite_number(usage[k]) and usage[k]>=0 for k in ('user_seconds','system_seconds')),'CPU measurements')
        stdout,stderr=read_stdout(label),read_stderr(label)
        require(len(stdout)==row['stdout_bytes'] and sha(stdout)==row['stdout_sha256'],'Complete stdout evidence')
        require(stderr==b'' and row['stderr_bytes']==0 and sha(stderr)==row['stderr_sha256'],'No hidden diagnostics')
        require(row['optimized'] is (label in ('qualification-cross-optimized','qualification-optimized')),'Explicit optimization mode')
        if label in BENCHMARK:
            require(sha(stdout)==EXPECTED_STDOUT,'Exact complete scientific stdout')
        elif label.startswith('qualification-cross-'):
            expected=scientific_stdout+b'PASS_ALL_SELECTED_LITERAL_STATES '+json.dumps(cross_expected,sort_keys=True).encode()+b'\n'
            require(stdout==expected,'Complete actual-state oracle evidence')
        else:
            require(stdout==scientific_stdout+b'PASS_COMPLETE_SELECTED_QUADRATIC_REPLAY\n','Complete adapter qualification evidence')
        inventory_hashes.add(row['source_inventory_sha256'])
        environments.add((row['python'],row['platform']))
        total+=row['wall_seconds']
    require(inventory_hashes=={EXPECTED_INVENTORY},'One exact immutable read-only source inventory')
    require(len(environments)==1 and 'Linux' in next(iter(environments))[1],'One Linux measurement environment')
    require(total<=4500,'Aggregate scientific budget')
    values={mode:[r['wall_seconds'] for r in rows[:6] if r['label'].endswith(mode)] for mode in ('literal','quadratic')}
    medians={m:statistics.median(v) for m,v in values.items()}
    return {'median_seconds':medians,'median_speedup':medians['literal']/medians['quadratic'],
            'ranges_seconds':{m:[min(v),max(v)] for m,v in values.items()},
            'median_cpu_seconds':{m:statistics.median(r['usage']['user_seconds']+r['usage']['system_seconds'] for r in rows[:6] if r['label'].endswith(m)) for m in values},
            'timed_kernel_peak_rss_mib':{m:max(r['usage']['kernel_max_rss_kib'] for r in rows[:6] if r['label'].endswith(m))/1024 for m in values},
            'all_kernel_peak_rss_mib':max(r['usage']['kernel_max_rss_kib'] for r in rows)/1024,
            'all_sampled_process_group_peak_rss_mib':max(r['sampled_process_group_rss_bytes'] for r in rows)/1024**2,
            'benchmark_seconds':sum(r['wall_seconds'] for r in rows[:6]),
            'additional_qualification_seconds':sum(r['wall_seconds'] for r in rows[6:]),
            'normal_registered_commands_seconds':sum(r['wall_seconds'] for r in rows if r['label'] in ('qualification-normal','qualification-cross-normal')),
            'optimized_qualification_seconds':sum(r['wall_seconds'] for r in rows if r['label'] in ('qualification-optimized','qualification-cross-optimized')),
            'aggregate_scientific_seconds':total}

def main():
    check_source()
    report=decode((HERE/'RESULT.json').read_bytes())
    rows=[decode((HERE/'evidence'/label/'receipt.json').read_bytes()) for label in BENCHMARK+QUALIFICATION]
    read=lambda label,name:(HERE/'evidence'/label/name).read_bytes()
    with tarfile.open(HERE/'inputs/PR5757.tar','r:') as archive:
        cross_expected=decode(archive.extractfile('research/selected-quadratic-replay/CROSS.json').read())
    summary=check_runs(rows,lambda l:read(l,'stdout.txt'),lambda l:read(l,'stderr.txt'),sha((HERE/'measurement-runner.py').read_bytes()),cross_expected)
    require(same(report['runs'],rows) and same(report['measurements'],summary),'Complete recorded report and derived statistics')
    require(report['scope']=='Recorded Linux qualification of exact PR5757; no new kappa','Report scope')
    print('PASS_LINUX_RECORDED_EVIDENCE_ONLY',json.dumps(summary,sort_keys=True))

if __name__=='__main__':
    main()
