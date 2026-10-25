#!/usr/bin/env python3
"""Actual source failures, all-counter tariffs, losing controls and integrity."""
import json,sys,subprocess,tempfile,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runtime,bench
from runtime import need,load,adapt
from powers import Powers
from tariff import probe,rundown,index_copy
from verify import read,canonical
from independent import check as independent_check


def main():
    passed=[]
    def rejects(name,fn,text):
        try:fn()
        except ValueError as error:
            need(text in str(error),'wrong rejection '+name+': '+str(error));passed.append(name)
        else:raise ValueError('accepted '+name)
    env=load();w=env.words;I=12;arena=w.Arena(I,128)
    for e in (0,1,2,3,7,8,9,15,16,31,32,63,64):
        word=arena.literal(e)
        for probing in (False,True):
            before=bench.actions(arena.meter);c=env.stream.Counter(word)
            if not probing:
                while not c.finished:c.decrement()
            c.close()
            expected=probe(e,I) if probing else rundown(e,I)
            need(bench.actions(c.tape.meter)==list(expected),'complete actual source Counter tariff')
            need(bench.sub(bench.actions(arena.meter),before)==list(index_copy(I)),'actual Counter encoded-index copy tariff')
        arena.free(word)
    passed.append('26-source-counter-tariff-calibrations')
    # Correctness is not a universal cost claim: an exponent-one kernel has
    # no removable radix traversal, so the extra probe is an actual loss.
    def kernel(shared):
        env=load();w=env.words;ia=w.Arena(9,64);ra=w.Arena(3,64)
        m=ra.literal(3);ring=w.Ring(m);e=ia.literal(1);v=env.cardinal_counts.Count.literal(7)
        tapes=[];old=env.records.Tape.__init__
        def track(t):old(t);tapes.append(t)
        env.records.Tape.__init__=track
        start=[bench.actions(ia.meter),bench.actions(ra.meter)]
        value_start=bench.actions(v.tape.meter)
        if shared:p=Powers(env);p.multiply([(v,e)],ring,3)
        else:env.cardinality.multiply_atom_power(v,e,ring,3)
        total=sum(sum(bench.actions(t.meter)) for t in tapes)+sum(sum(bench.sub(bench.actions(bank.meter),b)) for bank,b in zip((ia,ra),start))+sum(bench.sub(bench.actions(v.tape.meter),value_start))
        env.records.Tape.__init__=old
        return bench.decode(v.tape),total
    a,b=kernel(False),kernel(True)
    need(a[0]==b[0]==21 and b[1]>a[1],'same-output exponent-one losing control')
    passed.append('same-output-exponent-one-cost-loss')
    for name,change,message in (
        ('zero-width',{'width':0},'positive recursive child width'),
        ('reversed-chunks',{'first':90,'second':0},'ordered disjoint recursive child chunks'),
        ('overlapping-chunks',{'first':0,'second':4,'width':14},'ordered disjoint recursive child chunks'),
        ('outside-complete-body',{'second':128,'width':14},'recursive child lies in the complete body'),
        ('embedding-discontinuity',{'first':63,'second':90,'width':2},'physically contiguous'),
        ('original-gap-crossing',{'n':64,'first':63,'second':90,'width':2},'does not cross the original gap'),
    ):
        c={'q':3,'w':1,'n':65,'first':0,'second':114,'width':14};c.update(change)
        for shared in (False,True):rejects(name+str(shared),lambda:bench.run(c,shared),message)
    class OmitTail(Powers):
        def multiply(self,items,ring,q):return super().multiply(items[:2],ring,q)
    saved=bench.Powers;bench.Powers=OmitTail
    try:rejects('actual-incomplete-three-power-adapter',lambda:bench.run({'q':3,'w':2,'n':193,'first':6,'second':210,'width':3},True),'independent actual ordered geometry values')
    finally:bench.Powers=saved
    env=load();ia=env.words.Arena(9,64);ra=env.words.Arena(5,64)
    modulus=ra.literal(9);ring=env.words.Ring(modulus);e=ia.literal(2);v=env.cardinal_counts.Count.literal(1);p=Powers(env)
    rejects('aliased-output-role',lambda:p.multiply([(v,e),(v,e)],ring,3),'disjoint power outputs')
    alias=Powers(env,v.tape)
    rejects('counter-output-alias',lambda:alias.multiply([(v,e)],ring,3),'counter workspace separate from outputs')
    zero=ia.literal(0);original_radix=env.cardinality.radix_power
    env.cardinality.radix_power=lambda *_args:(_ for _ in ()).throw(ValueError('zero exponent must not validate modulus'))
    try:
        original=bytes(v.tape.cells);p.multiply([(v,zero)],ring,3)
        need(bytes(v.tape.cells)==original,'zero exponent preserves full Count serialization')
    finally:env.cardinality.radix_power=original_radix
    passed.append('zero-exponent-preserves-source-no-validation-path')
    p.busy=True;rejects('reentrant-counter-workspace',lambda:p.multiply([(v,e)],ring,3),'non-reentrant');p.busy=False
    bad=ra.literal(12);bad_ring=env.words.Ring(bad);initial=(set(ia.live),set(ra.live))
    rejects('non-prime-power-validator',lambda:p.multiply([(v,e)],bad_ring,3),'cardinality prime-power context')
    need(not p.busy and p.workspace.head==1 and all(x==env.words.BLANK for x in p.workspace.cells[1:]),'failed validator returns private record role')
    # The inherited validator can retain its failing quotient/remainder. Its
    # rejection is preserved; full malformed-input rollback is not claimed.
    ra.rollback(initial[1])
    rejects('legacy-non-prime-power-validator',lambda:env.cardinality.multiply_atom_power(v,e,bad_ring,3),'cardinality prime-power context')
    passed.append('failed-validator-private-record-return-only')
    receipt=read(HERE/'CERTIFICATE.json')
    for name,path,value,message in (
        ('free-counter-invoice',('pairs',0,'saving','record'),[0,0,0],'independent complete exact action delta'),
        ('missing-gap-value',('pairs',0,'shared','output_values'),['1','1','1'],'independent full marginal bytes/values'),
        ('boolean-counter-width',('pairs',0,'shared','index_width'),True,'typed source widths'),
        ('floating-action-count',('pairs',0,'total_action_saving'),float(receipt['pairs'][0]['total_action_saving']),'typed complete action gain'),
    ):
        bad=json.loads(json.dumps(receipt));cursor=bad
        for key in path[:-1]:cursor=cursor[key]
        cursor[path[-1]]=value
        need(canonical(receipt)!=canonical(bad),'typed full-receipt projection differs')
        rejects(name,lambda:independent_check(bad),message)
    with tempfile.TemporaryDirectory(prefix='child-power-controls-') as td:
        root=Path(td);package=root/'research/encoded-child-spectators';package.mkdir(parents=True)
        manifest=(HERE/'SOURCES.json').read_bytes();(package/'SOURCES.json').write_bytes(manifest)
        for row in json.loads(manifest)['files']:
            if row['usage']!='input':continue
            target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(runtime.ROOT/row['path'],target)
        saved_here,saved_root=runtime.HERE,runtime.ROOT
        try:
            runtime.HERE,runtime.ROOT=package,root;runtime.authenticate()
            target=root/runtime.PREFIX/'predecessor/vendor/words.py';target.write_text("raise RuntimeError('UNAUTHENTICATED_EXECUTION')\n")
            rejects('source-corruption-before-execution',runtime.load,'source SHA256')
            broken=json.loads(manifest);broken['files']=[r for r in broken['files'] if r['path']!=str(target.relative_to(root))]
            (package/'SOURCES.json').write_text(json.dumps(broken))
            rejects('source-inventory-removal-before-execution',runtime.load,'sealed source inventory')
        finally:runtime.HERE,runtime.ROOT=saved_here,saved_root
        duplicate=root/'duplicate.json';duplicate.write_text('{"x":1,"x":2}')
        rejects('duplicate-receipt-key',lambda:read(duplicate),'duplicate receipt key')
    before=(HERE/'CERTIFICATE.json').read_bytes()
    proc=subprocess.run([sys.executable,'-I','-B',str(HERE/'verify.py'),'--write'],capture_output=True,text=True,timeout=10)
    need(proc.returncode!=0 and 'refuse certificate overwrite' in proc.stderr and (HERE/'CERTIFICATE.json').read_bytes()==before,'CLI overwrite refusal before recomputation')
    passed.append('CLI-overwrite-refusal')
    print('PASS_CHILD_SPECTATOR_CONTROLS '+json.dumps({'groups':len(passed),'checks':passed},sort_keys=True))


if __name__=='__main__':main()
