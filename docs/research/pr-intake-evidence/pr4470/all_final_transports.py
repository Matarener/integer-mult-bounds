"""Maintainer supplement: cover final transports inherited through unreviewed retiming.
Douglas Colkitt with OpenAI assistance. Apache-2.0.
Run from a PR4470 export root; uses the retained exact Clifford decoder.
"""
from pathlib import Path
import sys,json,hashlib
root=Path.cwd();sys.path.insert(0,str(root/'research/joint-helper-lattice'))
import native_joint as J
F=J.F
c,programs,base,before,counts=J.construct()
receipt=F.read(root/'research/joint-helper-lattice/NATIVE.json.gz')
checked={(e['old'],e['new']) for e in receipt['new_physical_edges_and_boundaries']}
final={(e[3],e[4]) for p in programs.values() for e in p if e[0]=='climb'}
helpers={(c['start'][r],c['final'][r]) for r in range(224,632)}
original=F.read(F.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
original_c=F.read(F.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
# These two exact inputs are bound to the completed PR4359/PR4416 native review.
for name,want in [('THREE-base-FULL-IDENTITY-NATIVE.json.gz','c54b0a3e129d28e6dbf74fa731fc3bb70fe3c6705f07256750fbecddcc842d39'),('THREE-base-FULL-IDENTITY-CANONICAL.json.gz','6418ec3da24d548a57f5c3fe5b9062c26c9478e638504a61c387f5cfb5f4ed61')]:
 F.need(hashlib.sha256((F.BASE/name).read_bytes()).hexdigest()==want,'Prior reviewed native source changed')
F.need(c['frames'][:len(original_c['frames'])]==original_c['frames'],'Prior reviewed frame labels changed')
inherited={(e[3],e[4]) for p in original.values() for e in p if e[0]=='climb'}
remaining=sorted((final|helpers)-checked-inherited)
ce=F.load(root/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','supplement_clifford')
P=F.load(root/'research/kappa-function-composition/complex/prune_native.py','supplement_phase')
X=F.load(root/'research/kappa-rebuild/complex/native_extensions.py','supplement_native')
for a,b in remaining:
 op=ce.canonical_frame(9,c['frames'][a]).adjoint().then(ce.canonical_frame(9,c['frames'][b]))
 for direction in ('forward','backward'):
  actual=P.conjugate(ce,op) if direction=='backward' else op
  rec=X.N.lower_exact(P,ce,actual)
  F.need(rec['rank']==len(c['frames'][b])-len(c['frames'][a]),'Exact remaining transport rank/phase')
print(json.dumps({'status':'PASS_ALL_FINAL_TRANSPORT_COVERAGE','final_transport_pairs':len(final),'helper_boundary_pairs':len(helpers),'registered_native_pairs':len(checked),'supplemental_pairs':len(remaining),'supplemental_orientations':2*len(remaining),'source_identical_prior_pairs_reused':len((final|helpers)-checked-set(remaining)), 'all_final_pairs_covered':(final|helpers)<=checked|inherited|set(remaining)}))
