#!/usr/bin/env python3
"""Independent failure controls and minimal Git-free, read-only replay."""
from pathlib import Path
import copy,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile,types,unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def module(path):
    m=types.ModuleType(path.stem);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m
V=module(HERE/'verify.py')
class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=V.sources()
        cls.template=V.load_template(cls.data['research/community-frontier1042-audit/selected-replay.tar.gz'])
        cls.packet=V.parse(gzip.decompress(cls.data['research/joint-query/certificate.json.gz']))
        cls.word=V.parse((HERE/'vendor/pr3952/WORD.json').read_bytes())
    def test_source_provider_and_duplicate_cut(self):
        t=copy.deepcopy(self.template);t['calls'][0]['provider_id']='QQ16'
        with self.assertRaisesRegex(ValueError,'provider'):V.schedule(t,self.packet)
        t=copy.deepcopy(self.template);t['calls'][1]=copy.deepcopy(t['calls'][0])
        t['async_schedule']['order'][1]=t['async_schedule']['order'][0]
        with self.assertRaisesRegex(ValueError,'incidence'):V.schedule(t,self.packet)
    def test_frame_and_family_identity(self):
        t=copy.deepcopy(self.template)
        next(c for c in t['calls'] if c['stage']==1)['window']['prefix_axes'].append(17)
        with self.assertRaisesRegex(ValueError,'window'):V.schedule(t,self.packet)
        t=copy.deepcopy(self.template);t['calls'][0]['owners'][0][0]=14336
        with self.assertRaisesRegex(ValueError,'family map'):V.schedule(t,self.packet)
    def test_producer_rank_and_centre_credit(self):
        p=copy.deepcopy(self.packet)
        for recipe in p['native_line_recipes'].values():recipe['rank']=2
        with self.assertRaisesRegex(ValueError,'rank'):V.producer(p)
        p=copy.deepcopy(self.packet);next(iter(p['core_words'].values())).append(['center'])
        with self.assertRaisesRegex(ValueError,'centre'):V.producer(p)
    def test_owned_dirt_may_not_be_read_before_clear(self):
        word=[['add','F0','W0',1]]+copy.deepcopy(self.word)
        with self.assertRaisesRegex(ValueError,'read before clear'):V.projection_invoice(word,self.packet['U_ports'])
    def test_typed_result_and_duplicate_keys(self):
        self.assertNotEqual(V.canonical({'count':1}),V.canonical({'count':True}))
        self.assertNotEqual(V.canonical({'count':1}),V.canonical({'count':1.0}))
        with self.assertRaises(ValueError):V.canonical({'n':float('nan')})
        with self.assertRaisesRegex(ValueError,'duplicate'):V.parse('{"count":1,"count":2}')
    def test_wrong_incidence_and_sharp_integer_cap(self):
        a=module(HERE/'arithmetic.py');result=V.parse((HERE/'RESULT.json').read_bytes())
        profile={int(k):v for k,v in result['complete_producer_profile_144'].items()}
        target=a.F(result['conditional_screens']['selected_a'])
        with self.assertRaisesRegex(ValueError,'incidence'):a.screens(profile,target,144,14336,72)
        s=a.screens(profile,target,144,14336,16)
        self.assertEqual(s['native_module_parameter_cases']['553']['decision'],'strict_pass')
        self.assertEqual(s['native_module_parameter_cases']['554']['decision'],'strict_fail')
        self.assertEqual(s['native_module_parameter_cases']['336']['decision'],'strict_pass')
        self.assertEqual(s['paired336_reference']['decision'],'strict_fail')
    def test_minimal_readonly_export_and_source_tampering(self):
        with tempfile.TemporaryDirectory(prefix='qq16-incidence-') as tmp:
            root=Path(tmp);dest=root/'research'/HERE.name
            shutil.copytree(HERE,dest,ignore=shutil.ignore_patterns('__pycache__'))
            for name,raw in self.data.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            vm=module(dest/'verify.py')
            pin=dest/'vendor/pr3952/WORD.json';raw=pin.read_bytes();pin.write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'retained source hash'):vm.sources()
            pin.write_bytes(raw)
            source=root/'certificates/selected-result.json';raw=source.read_bytes();source.write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'source hash'):vm.sources()
            source.write_bytes(raw)
            manifest=dest/'SOURCES.json';raw=manifest.read_bytes();manifest.write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'manifest binding'):vm.sources()
            manifest.write_bytes(raw)
            receipt=dest/'RESULT.json';raw=receipt.read_bytes();r=V.parse(raw)
            r['schedule_ledger']['literal_projection_invocations']=False
            receipt.write_text(json.dumps(r))
            p=subprocess.run([sys.executable,'-I','-O','-B',str(dest/'verify.py')],cwd=tmp,capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0);self.assertIn('complete typed RESULT mismatch',p.stderr)
            receipt.write_bytes(raw)
            before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            try:
                for p in root.rglob('*'):p.chmod(0o555 if p.is_dir() else 0o444)
                root.chmod(0o555)
                for flags in ([],['-O']):
                    p=subprocess.run([sys.executable,'-I',*flags,'-Werror','-B',str(dest/'verify.py')],cwd=tmp,capture_output=True,text=True)
                    self.assertEqual(p.returncode,0,p.stderr)
                    self.assertEqual(p.stdout.strip(),'PASS_QQ16_INTEGER_CONSUMER_INCIDENCE no_new_kappa')
                after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(before,after);self.assertFalse((root/'.git').exists())
            finally:
                root.chmod(0o755)
                for p in root.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
if __name__=='__main__':unittest.main(verbosity=2)
