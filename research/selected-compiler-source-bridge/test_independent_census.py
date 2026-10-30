"""Tiny synthetic tests only; never import the actual source tree or replay science.

Original census algorithm/control coverage retained from the verified Astra
worker. Source-only loader tests use invented temporary files, not originals.
Substantial OpenAI Codex assistance. Apache-2.0; predecessor credit retained.
Run directly with python -I -B [-O] /path/to/test_independent_census.py.
"""
import copy
import hashlib
import importlib
import importlib.util
import itertools
import json
import marshal
from pathlib import Path, PureWindowsPath
import random
import sys
import struct
import tempfile
import types
import unittest
from unittest import mock

def own_source(name, filename):
    # The package manifest is pinned by its parent verifier. Even with -I -B,
    # avoid a file-location loader here: it could read stale adjacent bytecode.
    path = Path(__file__).with_name(filename)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), module.__dict__)
    return module


c = own_source("_bridge_census_unit", "independent_census.py")
lifetime = own_source("_bridge_lifetime_unit", "independent_lifetime.py")

G=[c.Group(0,'local_cover_sweep',(0,1)),c.Group(2,'idle',(2,3)),c.Group(3,'idle',())]
LOWS=('A','B')

def cartesian_sorted(groups,replicas,lows):
    # Build unordered Cartesian points then sort by grammar, NOT emitter loops
    # or mixed-radix division. An independent finite order oracle.
    points=[]
    for gi,g in enumerate(groups):
        for rp,ip,lp in itertools.product(range(replicas),range(len(g.ids)),range(len(lows))):
            order=(gi,rp,lp,ip) if g.common else (gi,rp,ip,lp)
            points.append((order,(gi,rp,g.ids[ip],g.common,lows[lp])))
    return [v for _,v in sorted(points)]


def certificate(groups=G):
    rows=[]
    for i,g in enumerate(groups):
        rows.append({'index':i,'schedule_index':g.schedule_index,'kind':g.kind,
                     'common':g.common,'low_major':g.common,
                     'order':'low-major' if g.common else 'id-major',
                     'start':g.ids[0] if g.ids else 4,'count':len(g.ids),
                     'sequence_sha256':c.digest_ids(g.ids)})
    return {'request_count':4,'replica_count':2,'empty_groups':1,
            'empty_canonical_start':4,'groups':rows}


class CensusTests(unittest.TestCase):
    def test_handwritten_word(self):
        # A two-request local group switches request faster than LOW;
        # a two-request idle group switches LOW faster than request.
        pairs=[(0,True,'A'),(1,True,'A'),(0,True,'B'),(1,True,'B')]*2
        pairs += [(2,False,'A'),(2,False,'B'),(3,False,'A'),(3,False,'B')]*2
        actual=c.projected_word(G,2,LOWS)
        self.assertEqual([(r,v,l) for _,_,r,v,l in actual],pairs)
        self.assertEqual(c.check_word(G,2,LOWS,actual),{'visits':16,'distinct_keys':8,'multiplicity':2})
        self.assertEqual(actual,cartesian_sorted(G,2,LOWS))

    def test_counts_preserving_order_mutants(self):
        original=c.projected_word(G,2,LOWS)
        mutants={}
        wrong=original[:];wrong[1],wrong[2]=wrong[2],wrong[1];mutants['local_id_major']=wrong
        wrong=original[:];wrong[9],wrong[10]=wrong[10],wrong[9];mutants['idle_low_major']=wrong
        wrong=original[4:8]+original[:4]+original[8:];mutants['replica_swap']=wrong
        wrong=original[8:]+original[:8];mutants['group_swap']=wrong
        wrong=original[:];wrong[0],wrong[1]=wrong[1],wrong[0];mutants['request_swap']=wrong
        for name,word in mutants.items():
            with self.subTest(name=name):
                self.assertEqual(c.Counter(word),c.Counter(original))
                with self.assertRaises(c.Rejected): c.check_word(G,2,LOWS,word)

    def test_wrong_view_preserves_counts_and_multiplicity(self):
        original=c.projected_word(G,2,LOWS)
        wrong=[(j,r,i,not view,l) for j,r,i,view,l in original]
        counts=c.Counter((i,v,l) for _,_,i,v,l in wrong)
        self.assertEqual(len(counts),8);self.assertEqual(set(counts.values()),{2})
        with self.assertRaises(c.Rejected): c.check_word(G,2,LOWS,wrong)

    def test_common_integer_not_boolean(self):
        original=c.projected_word(G,2,LOWS)
        wrong=[(j,r,i,int(v),l) for j,r,i,v,l in original]
        self.assertEqual(wrong,original)  # ordinary equality would miss this
        with self.assertRaises(c.Rejected): c.check_word(G,2,LOWS,wrong)

    def test_duplicate_gap_same_total(self):
        bad=[c.Group(0,'local_cover_sweep',(0,0)),c.Group(2,'idle',(2,3))]
        self.assertEqual(sum(len(g.ids) for g in bad),4)
        with self.assertRaises(c.Rejected): c.partition(bad,4)
        word=c.projected_word(G,2,LOWS);word[1]=word[0]
        with self.assertRaises(c.Rejected): c.check_word(G,2,LOWS,word)

    def test_overlap_gap_empty_and_type_boundaries(self):
        for groups,R in [([c.Group(0,'idle',(0,)),c.Group(1,'idle',(0,))],2),
                         ([c.Group(0,'idle',(0,2))],3),
                         ([c.Group(0,'idle',(False,))],1),
                         ([c.Group(0,'idle',(-1,))],1),
                         ([c.Group(0,'idle',(0,)),c.Group(0,'idle',())],1)]:
            with self.assertRaises(c.Rejected): c.partition(groups,R)
        c.partition(G,4)
        for bad in (-1,16,True):
            with self.assertRaises(c.Rejected): c.visit_at(G,2,LOWS,bad)
        for badlows in ((),('A','A')):
            with self.assertRaises(c.Rejected): c.visit_at(G,2,badlows,0)
        self.assertEqual(c.projected_word([c.Group(0,'idle',())],2,LOWS),[])

    def test_missing_extra_replica(self):
        for rho in (1,3):
            with self.assertRaises(c.Rejected): c.check_word(G,2,LOWS,c.projected_word(G,rho,LOWS))

    def test_seeded_cartesian_crosscheck(self):
        rng=random.Random(3391)
        for _ in range(70):
            groups=[];identifier=0
            for j in range(rng.randrange(1,7)):
                count=rng.randrange(0,5)
                ids=tuple(range(identifier,identifier+count));identifier+=count
                groups.append(c.Group(j*2,rng.choice(('idle','local_cover_sweep')),ids))
            rho=rng.randrange(1,5);lows=tuple(range(rng.randrange(1,5)))
            c.partition(groups,identifier)
            self.assertEqual(c.projected_word(groups,rho,lows),cartesian_sorted(groups,rho,lows))

    def test_interval_controls(self):
        data=certificate();self.assertEqual(c.interval_data(data,G),G)
        changes=[('common',False),('low_major',False),('order','id-major'),
                 ('start',1),('count',3),('index',1),('schedule_index',3),
                 ('sequence_sha256','0'*64),('count',True)]
        for key,value in changes:
            with self.subTest(key=key):
                bad=copy.deepcopy(data);bad['groups'][0][key]=value
                with self.assertRaises(c.Rejected):c.interval_data(bad,G)
        bad=copy.deepcopy(data);bad['groups'].pop();bad['empty_groups']=0
        # A partition by itself cannot detect a dropped zero-size group.
        self.assertEqual(len(c.interval_data(bad)),2)
        with self.assertRaises(c.Rejected):c.interval_data(bad,G)

    def test_self_consistent_data_is_not_source_authentication(self):
        bad=certificate()
        # Interchange equally sized local/idle intervals, recalculate digests.
        # Partition and all totals still pass: only source linkage rejects it.
        for row,start in zip(bad['groups'][:2],(2,0)):
            row['start']=start;row['sequence_sha256']=c.digest_ids(range(start,start+2))
        c.interval_data(bad)
        with self.assertRaises(c.Rejected):c.interval_data(bad,G)

    def test_posix_spelling_preserves_windows_components(self):
        root=PureWindowsPath('E:/review/predecessor')
        path=root/'vendor'/'words.py';rel=path.relative_to(root)
        self.assertEqual(str(rel),'vendor\\words.py')
        self.assertEqual(rel.as_posix(),'vendor/words.py')
        self.assertEqual(root/PureWindowsPath(rel.as_posix()),path)

    def test_raw_request_projection_small_data(self):
        # Generic hosting fixture, not selected data or an original module.
        events=[[0,0,0,1,1,0],[1,1,0,1,1,0],[2,0,2,1,0,1,0],[3,0,2,1,0,0,0]]
        t={'replicas':2,'stages':1,
           'calls':[{'stage':0,'replica':r,'orientation':'forward','local_hash':'fixture'} for r in (0,1)],
           'local_programs':{'forward':events},
           'schedule':[{'kind':'local_cover_sweep','stage':0},
                       {'kind':'idle','idx':0,'source_level':-1,'target_level':0,'rank':7,'pair':0},
                       {'kind':'idle','idx':1,'source_level':0,'target_level':0,'rank':0,'pair':1}],
           'hosting':{'slots':[[0,0,0,7,0,0]]}}
        groups,requests,ev,mp,idles=c.raw_groups(t)
        self.assertEqual(groups[0].ids,(0,1));self.assertEqual(mp[0],(0,None,1,None))
        self.assertEqual(len(requests),223);self.assertEqual(len(idles[0]),221)
        self.assertEqual(requests[2]['role'],1);self.assertEqual(idles[1],())
        bad=copy.deepcopy(t);bad['hosting']['slots']*=2
        with self.assertRaises(c.Rejected):c.raw_groups(bad)



def record(raw):
    return {"sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}


class AuthenticationTests(unittest.TestCase):
    def test_safe_paths(self):
        for value in ("../escape.py", "/outside.py", "C:/outside.py", "C:relative.py",
                      "a\\b.py", "a//b.py", "a/./b.py", "a/../b.py", "", ".", False):
            with self.subTest(value=value):
                with self.assertRaises(c.Rejected):
                    c.safe_relative(value)
                with self.assertRaises(lifetime.Rejected):
                    lifetime.safe_source_path(value)
        self.assertEqual(c.safe_relative("research/package/module.py"), "research/package/module.py")

    def test_git_free_inventory_and_byte_mutations(self):
        # 149 tiny invented inputs, not a copy/replay of the selected source.
        with tempfile.TemporaryDirectory(prefix="bridge-auth-") as tmp:
            root = Path(tmp).resolve()
            manifest = {"package_sha256": {}, "live_inputs": []}
            for index in range(28):
                rel = c.AUDIT + f"/fixture-{index}.json"
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = str(index).encode()
                path.write_bytes(raw)
                manifest["package_sha256"][rel] = record(raw)["sha256"]
            for index in range(121):
                rel = f"fixture-inputs/input-{index}.bin"
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = str(index).encode()
                path.write_bytes(raw)
                manifest["live_inputs"].append({"path": rel, **record(raw)})
            self.assertFalse((root / ".git").exists())
            self.assertEqual(c.authenticate(root, manifest), {
                "package_files": 28, "live_inputs": 121,
                "all_bytes_checked_before_source_import": True})
            for rel in (next(iter(manifest["package_sha256"])), manifest["live_inputs"][0]["path"]):
                path = root / rel
                raw = path.read_bytes()
                path.write_bytes(raw + b"changed")
                with self.assertRaisesRegex(c.Rejected, "SHA256 mismatch"):
                    c.authenticate(root, manifest)
                path.write_bytes(raw)
            changed = copy.deepcopy(manifest)
            changed["live_inputs"][0]["git_blob"] = "0" * 40
            with self.assertRaisesRegex(c.Rejected, "Git blob mismatch"):
                c.authenticate(root, changed)
            changed = copy.deepcopy(manifest)
            changed["live_inputs"][1] = changed["live_inputs"][0]
            with self.assertRaisesRegex(c.Rejected, "unique independent pin"):
                c.pin_index(changed)
            extra = root / c.AUDIT / "extra.py"
            extra.write_bytes(b"raise RuntimeError('never import this')")
            with self.assertRaisesRegex(c.Rejected, "inventory"):
                c.authenticate(root, manifest)
            # Fixture cleanup belongs to TemporaryDirectory, never the repository.

    def test_manifest_data_contract(self):
        manifest = c.load_manifest()  # only this successor's DATA trust anchor
        self.assertEqual(len(manifest["package_sha256"]), 28)
        self.assertEqual(len(manifest["live_inputs"]), 121)
        self.assertEqual(len(c.pin_index(manifest)), 149)
        self.assertEqual(len(lifetime.source_pins()), 61)
        self.assertEqual(manifest["main_scientific_receipt_sha256"],
                         "c1bc50f54937cd3b2efae61bb5b655b55859b3ed7ddcf1a2e9bbd8682fc88f3d")

    def test_windows_adapter_exact_one_expression(self):
        raw = ("def spelling(path, here):\n    return " + c.WINDOWS_OLD + "\n").encode()
        expected = raw.replace(c.WINDOWS_OLD.encode(), c.WINDOWS_NEW.encode())
        self.assertEqual(c.windows_inventory_adapter(raw), expected)
        for invalid in (b"no anchor", raw + raw):
            with self.assertRaisesRegex(c.Rejected, "exact inventory adapter anchor"):
                c.windows_inventory_adapter(invalid)

    def test_timeout_wrapper_preserves_optimization(self):
        for level in (0, 1, 2):
            command = c.source_command(Path(__file__).parent, level)
            self.assertEqual(command[:3], [sys.executable, "-I", "-B"])
            self.assertEqual([part for part in command if part in ("-O", "-OO")],
                             ["-" + "O" * level] if level else [])
            self.assertIn("--source", command)
        for invalid in (True, -1, 3):
            with self.assertRaises(c.Rejected):
                c.source_command(Path(__file__).parent, invalid)


class SourceImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="bridge-import-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.name = "_bridge_invented_module"
        self.rel = c.CALLER + "/" + self.name + ".py"
        self.path = self.root / self.rel
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.raw = b"value = 7\ndef identity(x: int) -> int: return x\n"
        self.path.write_bytes(self.raw)

    def importers(self, pins=None):
        pins = {self.rel: record(self.raw)} if pins is None else pins
        return (("census", c.SourceImports(self.root, pins), c.Rejected),
                ("lifetime", lifetime.SourceFinder(self.root, {}, {
                    rel: row["sha256"] for rel, row in pins.items()}), lifetime.Rejected))

    def test_source_only_stale_bytecode_and_cleanup(self):
        # A valid timestamp header pointing to a poisonous code object. Both
        # adjacent and current-optimization cache paths must be ignored.
        stat = self.path.stat()
        stale = (importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(stat.st_mtime), len(self.raw))
                 + marshal.dumps(compile("raise RuntimeError('stale pyc ran')", str(self.path), "exec")))
        # Own the poisonous prefix inside this fixture, never a parent's -X
        # pycache_prefix. A parent may require its prefix to stay empty.
        previous_prefix = sys.pycache_prefix
        self.addCleanup(setattr, sys, "pycache_prefix", previous_prefix)
        sys.pycache_prefix = str(self.root / "fixture-bytecode")
        cached = Path(importlib.util.cache_from_source(str(self.path)))
        self.assertTrue(cached.resolve().is_relative_to(self.root))
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(stale)
        self.path.with_suffix(".pyc").write_bytes(stale)
        old_path, old_meta = list(sys.path), list(sys.meta_path)
        old_spec, old_bytecode = importlib.util.spec_from_file_location, sys.dont_write_bytecode
        for label, importer, _ in self.importers():
            with self.subTest(importer=label):
                with importer:
                    result = importlib.import_module(self.name)
                    self.assertEqual(result.value, 7)
                    self.assertIs(result.identity.__annotations__["x"], int)
                    self.assertEqual(importer.records, {self.rel: record(self.raw)["sha256"]})
                self.assertNotIn(self.name, sys.modules)
                self.assertEqual(sys.path, old_path)
                self.assertEqual(sys.meta_path, old_meta)
                self.assertIs(importlib.util.spec_from_file_location, old_spec)
                self.assertEqual(sys.dont_write_bytecode, old_bytecode)
                self.assertEqual(cached.read_bytes(), stale)

    def test_hash_checked_at_execution_not_only_discovery(self):
        for label, importer, error in self.importers():
            with self.subTest(importer=label):
                self.path.write_bytes(self.raw)
                with importer:
                    spec = importer.find_spec(self.name)
                    self.path.write_bytes(b"raise RuntimeError('unverified source ran')\n")
                    module = importlib.util.module_from_spec(spec)
                    with self.assertRaisesRegex(error, "[hH][aA][sS][hH]|SHA256"):
                        spec.loader.exec_module(module)
                self.assertEqual(importer.records, {})
        self.path.write_bytes(self.raw)

    def test_hash_and_compile_same_read(self):
        original_read = Path.read_bytes
        for label, importer, _ in self.importers():
            with self.subTest(importer=label):
                reads = []
                def read(path):
                    if path == self.path:
                        reads.append(path)
                        return self.raw if len(reads) == 1 else b"raise RuntimeError('second source read')\n"
                    return original_read(path)
                with mock.patch.object(Path, "read_bytes", read), importer:
                    self.assertEqual(importlib.import_module(self.name).value, 7)
                self.assertEqual(len(reads), 1)

    def test_unpinned_source_rejected(self):
        for label, importer, error in self.importers({}):
            with self.subTest(importer=label), importer:
                with self.assertRaisesRegex(error, "unpinned|unlisted"):
                    importlib.import_module(self.name)
                self.assertEqual(importer.records, {})

    def test_explicit_file_location_import_is_also_source_only(self):
        for label, importer, _ in self.importers():
            with self.subTest(importer=label):
                alias = "_bridge_invented_alias"
                with importer:
                    spec = importlib.util.spec_from_file_location(alias, self.path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[alias] = module
                    spec.loader.exec_module(module)
                    self.assertEqual(module.value, 7)
                    self.assertEqual(set(importer.records), {self.rel})
                self.assertNotIn(alias, sys.modules)

    def test_missing_pinned_source_does_not_fall_back(self):
        self.path.unlink()  # only the invented file in this test's temporary root
        for label, importer, error in self.importers():
            with self.subTest(importer=label), importer:
                with self.assertRaisesRegex(error, "regular contained"):
                    importlib.import_module(self.name)

    def test_failed_explicit_import_cleans_alias(self):
        alias = "_bridge_rejected_alias"
        for label, importer, error in self.importers():
            with self.subTest(importer=label):
                self.path.write_bytes(self.raw)
                with importer:
                    spec = importlib.util.spec_from_file_location(alias, self.path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[alias] = module
                    self.path.write_bytes(b"value = 'unauthenticated'\n")
                    with self.assertRaises(error):
                        spec.loader.exec_module(module)
                self.assertNotIn(alias, sys.modules)
                self.assertEqual(importer.records, {})

    def test_windows_adapter_receipt_path_is_relative(self):
        path = self.root / c.WINDOWS_VERIFIER
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = ("def spelling(path, here):\n    return " + c.WINDOWS_OLD + "\n").encode()
        path.write_bytes(raw)
        imports = c.SourceImports(self.root, {c.WINDOWS_VERIFIER: record(raw)})
        with imports:
            spec = importlib.util.spec_from_file_location("frozen_caller_verifier", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
        self.assertEqual(imports.records, {c.WINDOWS_VERIFIER: record(raw)["sha256"]})
        if c.os.name == "nt":
            self.assertEqual(imports.adapters, [{"path": c.WINDOWS_VERIFIER,
                                                "old": c.WINDOWS_OLD, "new": c.WINDOWS_NEW}])
        else:
            self.assertEqual(imports.adapters, [])

    def test_preloaded_source_namespace_rejected(self):
        sys.modules[self.name] = types.ModuleType(self.name)
        try:
            for label, importer, error in self.importers():
                with self.subTest(importer=label):
                    with self.assertRaisesRegex(error, "preloaded"):
                        with importer:
                            self.fail("preloaded namespace accepted")
        finally:
            sys.modules.pop(self.name, None)

    def test_forbidden_audit_import_names(self):
        for label, importer, error in self.importers():
            with self.subTest(importer=label), importer:
                for name in ("accounting", "source_audit", "verify", "extract_census"):
                    with self.assertRaisesRegex(error, "forbidden"):
                        importlib.import_module(name)

    def test_failure_restores_import_environment(self):
        old_spec, old_meta = importlib.util.spec_from_file_location, list(sys.meta_path)
        for label, importer, _ in self.importers():
            with self.subTest(importer=label):
                with self.assertRaisesRegex(RuntimeError, "fixture failure"):
                    with importer:
                        importlib.import_module(self.name)
                        raise RuntimeError("fixture failure")
                self.assertIs(importlib.util.spec_from_file_location, old_spec)
                self.assertEqual(sys.meta_path, old_meta)
                self.assertNotIn(self.name, sys.modules)


class SyntheticLifetimeTests(unittest.TestCase):
    def test_retained_independent_synthetic_controls(self):
        report = lifetime.synthetic()
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["positive"], {"T": 3, "B": 3, "direct_references": 9,
                                             "distinct_identities": 3, "zero_block_returns": 2})
        self.assertEqual(len(report["controls"]), 5)
        self.assertTrue(all(row["rejected"] for row in report["controls"]))
        self.assertEqual(report["observer_control"]["fresh_identities"], 3)
        self.assertEqual(report["observer_control"]["interned_identities"], 1)

    def test_synthetic_size_guards(self):
        with self.assertRaisesRegex(lifetime.Rejected, "operation bound"):
            lifetime.inspect_operations([("node",)] * (lifetime.MAX_OPERATIONS + 1), [])
        with self.assertRaisesRegex(lifetime.Rejected, "wrapper bound"):
            lifetime.inspect_operations([], [None] * (lifetime.MAX_RETURNS + 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
