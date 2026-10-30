"""Run all ten nominated tests; record inclusive setup, Git and CLI times."""
import importlib.util,json,sys,time,unittest,hashlib
from collections import defaultdict
from pathlib import Path
repo=Path(__file__).resolve().parents[1]/'repo';path=repo/'tests/test_research_descendant_source_roles.py'
spec=importlib.util.spec_from_file_location('profile_helper_group',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=defaultdict(lambda:[0,0.0]);tests=[]
def observe(obj,name,label):
 original=getattr(obj,name)
 def wrapped(*a,**kw):
  start=time.perf_counter()
  try:return original(*a,**kw)
  finally:
   row=rows[label];row[0]+=1;row[1]+=time.perf_counter()-start
 setattr(obj,name,wrapped)
observe(m,'git','git');observe(m.DescendantSourceRoleTests,'setUp','setUp');observe(m.DescendantSourceRoleTests,'cli','cli')
class Result(unittest.TextTestResult):
 def startTest(self,t):self.start=time.perf_counter();super().startTest(t)
 def stopTest(self,t):tests.append([t.id(),time.perf_counter()-self.start]);super().stopTest(t)
suite=unittest.defaultTestLoader.loadTestsFromModule(m)
r=unittest.TextTestRunner(stream=sys.stdout,verbosity=2,resultclass=Result).run(suite)
print(json.dumps({'tests':tests,'inclusive_profiles':dict(rows),'failures':len(r.failures),'errors':len(r.errors),'skips':r.skipped,'tests_run':r.testsRun},sort_keys=True))
if not r.wasSuccessful() or r.testsRun!=10:raise SystemExit(1)
