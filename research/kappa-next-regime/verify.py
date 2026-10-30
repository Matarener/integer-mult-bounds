#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Git-free, read-only replay of the complete finite kappa continuation.

Default mode reruns the native catalogue, complete symbolic word, controlled
physical probe and complex fill audit. --reuse-expensive-receipts is an
explicit packaging smoke mode: those four checks are source-bound reuse,
while all word/template regeneration and arithmetic still execute freshly.
All writes go to a new absolute directory outside the source repository.
Neither mode asserts an unconditional all-size multiplication theorem.
Substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

# This must precede the local-module import, including when users omit -B.
sys.dont_write_bytecode=True
import build_manifest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=HERE/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
GEOMETRY=HERE/'geometry-search'
WORD=HERE/'word-search/candidate/WORD.json.gz'
POOL=GEOMETRY/'pool35-word'
WORD_SHA='3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'
COMPLEX=HERE/'sources/PR3959/research/rank7-idle-frame-select'


def need(ok,reason):
    if not ok:raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def digest(path):return build_manifest.digest(path)['sha256']


def payload_digest(path):
    h=sha256()
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def source_path(name):
    path=ROOT/build_manifest.relative_name(name)
    need(path.resolve().is_relative_to(ROOT),'source pin remains in the repository')
    return path


def source_pins(value):
    """Authenticate all explicit file SHA maps, including nested AST records."""
    count=0
    if isinstance(value,dict):
        pins=value.get('source_sha256')
        if isinstance(pins,dict):
            for name,expected in pins.items():
                need(isinstance(expected,str) and len(expected)==64,'complete source SHA256')
                need(digest(source_path(name))==expected,'retained receipt source pin: '+name)
                count+=1
        elif isinstance(pins,str) and 'source' in value:
            need(digest(source_path(value['source']))==pins,'nested source/AST byte pin')
            count+=1
        for child in value.values():count+=source_pins(child)
    elif isinstance(value,list):
        for child in value:count+=source_pins(child)
    return count


class Replay:
    def __init__(self,output,reuse):
        self.output,self.reuse=output,reuse
        self.steps,self.comparisons=[],[]
        self.started=time.monotonic()
        (output/'logs').mkdir();(output/'receipts').mkdir()

    def receipt(self,name):return self.output/'receipts'/name

    def run(self,label,script,*arguments,cwd=ROOT):
        index=len(self.steps)+1;log=self.output/'logs'/('%02d-%s.log'%(index,label))
        command=[sys.executable,'-B',str(script),*map(str,arguments)]
        environment=os.environ.copy();environment['PYTHONDONTWRITEBYTECODE']='1'
        print('[%02d] %s: running'%(index,label),flush=True)
        started=time.monotonic()
        with log.open('xb') as handle:
            completed=subprocess.run(command,cwd=cwd,env=environment,stdout=handle,stderr=subprocess.STDOUT)
        step={'label':label,'mode':'fresh','argv':command,'exit_code':completed.returncode,
              'elapsed_seconds':time.monotonic()-started,'log':log.relative_to(self.output).as_posix(),
              'script_sha256':digest(script)}
        self.steps.append(step)
        if completed.returncode:
            tail=log.read_text(encoding='utf-8',errors='replace')[-5000:]
            raise ValueError(label+' failed; '+str(log)+'\n'+tail)
        print('[%02d] %s: PASS (%.2fs)'%(index,label,step['elapsed_seconds']),flush=True)
        return log

    def equal(self,label,actual,expected,omit=(),bytes_only=False):
        if bytes_only:
            need(digest(actual)==digest(expected),label+': exact fresh bytes differ')
            value={'sha256':digest(actual)}
        else:
            a,b=read(actual),read(expected)
            for key in omit:
                need(key in a and key in b,label+': expected nonsemantic field is missing')
                a=deepcopy(a);b=deepcopy(b);a.pop(key);b.pop(key)
            need(canonical(a)==canonical(b),label+': complete canonical payload differs')
            value={'canonical_sha256':sha256(canonical(a)).hexdigest()}
        self.comparisons.append({'label':label,'actual':actual.relative_to(self.output).as_posix(),
            'expected':expected.relative_to(ROOT).as_posix(),'omitted_nonsemantic_fields':list(omit),**value})

    def expensive(self,label,script,retained,*arguments,omit=()):
        target=self.receipt(label+'.json');saved=read(retained)
        pins=source_pins(saved)
        need(pins>0,label+': retained expensive receipt has no exact source binding')
        if self.reuse:
            shutil.copyfile(retained,target)
            self.steps.append({'label':label,'mode':'source-bound receipt reuse',
                'receipt':retained.relative_to(ROOT).as_posix(),'receipt_sha256':digest(retained),
                'validated_explicit_source_pins':pins,'fresh_execution':False})
            print('[%02d] %s: exact-source receipt reused'%(len(self.steps),label),flush=True)
        else:self.run(label,script,*arguments,'--output',target)
        self.equal(label,target,retained,omit=omit)
        return target

    def scientific_replay(self):
        # Generated copies are checked first; retained paths are subsequently
        # used because the unchanged checkers bind repository-relative paths.
        fresh_word=self.output/'constructed-word'
        self.run('construct-word',HERE/'word-search/construct_bit_candidate.py','--out',fresh_word)
        self.equal('literal changed word',fresh_word/'WORD.json.gz',WORD)
        need(payload_digest(fresh_word/'WORD.json.gz')==WORD_SHA,'definitive regenerated word content pin')
        for directory in (fresh_word,WORD.parent):
            receipt=read(directory/'CONSTRUCTION.json')
            need(receipt['word_archive_sha256']==digest(directory/'WORD.json.gz'),'actual generated gzip digest')
        self.equal('word construction receipt',fresh_word/'CONSTRUCTION.json',WORD.parent/'CONSTRUCTION.json',
                   omit=('word_archive_sha256',))
        self.run('native-xcheck',BASE/'vendor/xcheck_p.py',fresh_word/'WORD.json.gz')
        native=self.output/'native';native.mkdir()
        self.run('native-record-export',BASE/'vendor/export_records.py',fresh_word/'WORD.json.gz',native/'records')
        self.run('native-local-counter',BASE/'code/local_counter.py',native)
        for name in ('records/249-records.bin','records/249-states.json','records/frames.json',
                     'cout/legality.json','cout/columns.json'):
            self.equal('fresh native '+name,native/name,HERE/'word-search/native'/name,bytes_only=True)
        local=self.receipt('local-independent.json')
        self.run('local-independent',HERE/'width-search/review_composed_word.py','--out',local)
        self.equal('complete independent local review',local,HERE/'width-search/COMPOSED-WORD-INDEPENDENT-NATIVE-REVIEW.json')
        for directory,builder in (('pool35','build_pool5.py'),('pool35-word','build_word_pool35.py')):
            fresh=self.output/directory
            self.run('reconstruct-'+directory,GEOMETRY/builder,'--out',fresh)
            for name in ('GLOBAL-TEMPLATE.json.gz','OWNER-INVENTORY.json.gz','IDLE-INVENTORY.json.gz',
                         'POOL-MOVES.json','RESULT.json'):
                self.equal(directory+' '+name,fresh/name,GEOMETRY/directory/name)
        tasks=[('pool35-independent','review_pool5.py','pool35','POOL35-INDEPENDENT-REVIEW.json'),
               ('pool35-all-T','fixed_slot_ceiling.py','pool35','POOL5-ALL-T-CEILING.json'),
               ('word-all-T','fixed_slot_ceiling.py','pool35-word','POOL5-WORD-ALL-T-CEILING.json'),
               ('word-block-prefix','block_prefix_word.py','pool35-word','BLOCK-PREFIX-REVIEW-WORD.json')]
        for label,script,candidate,retained in tasks:
            output=self.receipt(label+'.json')
            self.run(label,GEOMETRY/script,'--candidate',GEOMETRY/candidate,'--out',output)
            self.equal(label,output,GEOMETRY/retained)
        invoice=self.receipt('complete-invoice.json')
        self.run('complete-invoice',HERE/'complete_invoice.py','--pool',POOL,'--word',WORD,
                 '--block-review',GEOMETRY/'BLOCK-PREFIX-REVIEW-WORD.json','--output',invoice)
        self.equal('complete finite invoice',invoice,HERE/'COMPLETE-WORD-INVOICE.json')
        native_result=self.expensive('native-catalogue',HERE/'native-catalogue/review.py',
            HERE/'native-catalogue/WORD-REVIEW.json','--pool',POOL,'--word',WORD,'--word-content-sha256',WORD_SHA)
        whole=self.expensive('whole-word',HERE/'native-catalogue/whole_word.py',
            HERE/'native-catalogue/WHOLE-WORD.json','--template',POOL/'GLOBAL-TEMPLATE.json.gz',
            '--word',WORD,'--word-content-sha256',WORD_SHA,omit=('elapsed_seconds',))
        physical=self.expensive('physical-probe',HERE/'word-search/physical_probe.py',HERE/'word-search/PHYSICAL-PROBE.json')
        nr,wr,pr=read(native_result),read(whole),read(physical)
        need(nr['actual_word_content_sha256']==wr['native_binding']['actual_word_content_sha256']==
             pr['word_content_sha256']==WORD_SHA,'all expensive checks bind the regenerated actual word')
        need(nr['binding_sha256']==wr['native_binding']['binding_sha256']==pr['catalogue']['binding_sha256'],
             'native, whole-word and physical receipts share one complete catalogue')
        output=self.receipt('physical-independent.json')
        self.run('physical-independent',HERE/'width-search/review_physical_probe.py','--out',output)
        self.equal('independent physical scope review',output,HERE/'width-search/PHYSICAL-PROBE-STATIC-REVIEW.json')
        self.complex_replay()
        outer=self.output/'outer-package'
        shutil.copytree(HERE/'outer/package',outer,
                        ignore=shutil.ignore_patterns('__pycache__','*.pyc','LEDGER.json','INDEPENDENT.json'))
        for script,receipt in (('check_ledger.py','LEDGER.json'),('independent_check.py','INDEPENDENT.json')):
            self.run('outer-'+script[:-3],outer/'outer'/script,cwd=outer)
            self.equal('fresh outer '+receipt,outer/'outer'/receipt,HERE/'outer/package/outer'/receipt)
        output=self.receipt('invoice-outer-independent.json')
        self.run('invoice-outer-independent',HERE/'width-search/review_invoice_outer.py',
                 '--invoice',HERE/'COMPLETE-WORD-INVOICE.json','--out',output)
        self.equal('independent complete invoice and outer',output,HERE/'width-search/FINAL-INVOICE-OUTER-REVIEW.json')

    def complex_replay(self):
        retained=HERE/'complex/FRESH-FILL-REVIEW.json';saved=read(retained)
        pins=source_pins(saved)
        need(pins>0 and saved['fill_rebound'] is True and saved['moves']==521798 and
             len(saved['controls_rejected'])==9,'complete retained fill-bound complex audit')
        upstream=read(COMPLEX/'AUDIT.json')
        need(digest(COMPLEX/'AUDIT.json')==saved['original_receipt_sha256'] and
             upstream['rejected_controls']==saved['controls_rejected'],
             'unchanged complete upstream complex receipt and controls')
        if self.reuse:
            shutil.copyfile(retained,self.receipt('complex-fill-audit.json'))
            self.steps.append({'label':'complex-fill-audit','mode':'source-bound receipt reuse',
                'receipt':retained.relative_to(ROOT).as_posix(),'receipt_sha256':digest(retained),
                'validated_explicit_source_pins':pins,'fill_rebound':True,'fresh_execution':False})
            print('[%02d] complex-fill-audit: exact-source receipt reused'%len(self.steps),flush=True)
            return
        fill=self.output/'t740-materialized'
        self.run('complex-fill-materialization',ROOT/'research/coupled-carrier-cap740/materialize.py','--output',fill)
        materialized=read(fill/'MATERIALIZED.json')
        need(materialized['sha256']==digest(fill/'COMPOSED-FILL.json.gz') and
             materialized['payload_sha256']==payload_digest(fill/'COMPOSED-FILL.json.gz'),
             'independently hashed complete fresh compressed and uncompressed fill')
        for name,key in (('ORDER.json','order_sha256'),('DISPATCH.json','dispatch_sha256')):
            need(materialized[key]==digest(fill/name),'fresh fill '+name+' source hash')
        need(read(HERE/'complex/MATERIALIZED.json')==saved['materialized'],'retained materialization receipt binding')
        self.equal('complete fresh materialized fill',fill/'MATERIALIZED.json',HERE/'complex/MATERIALIZED.json',omit=('sha256',))
        log=self.run('complex-fill-audit',COMPLEX/'verify.py','--t740',fill)
        need('PASS_IDLE_FRAME_SELECT_AUDIT moves=521798 controls=9 ' in log.read_text(),
             'all complete complex moves and controls executed with actual --t740 binding')
        result={'status':'PASS_FRESH_COMPLEX_FILL_AND_UNCHANGED_MOVE_AUDIT','fill_rebound':True,
                'materialized':materialized,'moves':saved['moves'],'controls_rejected':saved['controls_rejected'],
                'upstream_audit_sha256':digest(COMPLEX/'AUDIT.json'),'source_sha256':saved['source_sha256'],
                'scope':saved['scope']}
        self.receipt('complex-fill-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


def authenticate_loader():
    path=ROOT/'research/selected-bit-physical-caller/loader.py'
    spec=importlib.util.spec_from_file_location('next_regime_replay_loader',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.authenticate()


def main():
    need(sys.version_info>=(3,11),'Python 3.11 or later is required')
    need(__debug__,'assertions must be enabled; do not run Python with -O')
    sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='new absolute directory outside the source repository')
    parser.add_argument('--reuse-expensive-receipts',action='store_true',
                        help='packaging smoke mode: source-bound reuse of native/whole/physical/complex checks')
    args=parser.parse_args()
    need(args.output.is_absolute(),'--output must be absolute')
    output=args.output.resolve()
    need(not output.exists() and not args.output.is_symlink(),'--output must not already exist')
    need(not output.is_relative_to(ROOT),'--output must lie outside the source repository')
    print('Authenticating complete source/dependency inventory.',flush=True)
    manifest=build_manifest.check();authenticate_loader()
    output.mkdir(parents=True,exist_ok=False);replay=Replay(output,args.reuse_expensive_receipts)
    result={'mode':'source-bound expensive receipt reuse' if args.reuse_expensive_receipts else 'full fresh replay',
            'manifest':manifest,'unconditional_supplier_admission':False,
            'scope':'Reproduction of the stated finite construction, native/symbolic and controlled physical checks, exact coefficient invoice and conditional outer arithmetic. Inherited all-size and physical primitive hypotheses remain explicit.'}
    try:
        replay.scientific_replay()
        need(build_manifest.check()==manifest,'source inventory changed during replay')
        result['status']='PASS_SOURCE_BOUND_FINITE_REPLAY_WITH_EXPLICIT_REUSE' if args.reuse_expensive_receipts else 'PASS_FULL_FRESH_FINITE_CONTINUATION_REPLAY'
    except Exception as exc:
        result.update(status='FAIL_CONTINUATION_REPLAY',error=str(exc))
        raise
    finally:
        result.update(steps=replay.steps,comparisons=replay.comparisons,
                      elapsed_seconds=time.monotonic()-replay.started)
        (output/'VERIFICATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'steps':len(replay.steps),'comparisons':len(replay.comparisons),
                      'receipt':str(output/'VERIFICATION.json')},sort_keys=True),flush=True)


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('FAIL: '+str(error),file=sys.stderr)
        raise SystemExit(1)
