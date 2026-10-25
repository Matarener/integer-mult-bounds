"""Append post-seal cold receipts without altering either sealed runtime."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def read(p):return json.loads(p.read_bytes())
def need(c,m):
 if not c:raise ValueError(m)
def pin(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 normal=read(HERE/'cold-normal-0001'/'RESULT.json');optimized=read(HERE/'cold-optimized-0001'/'RESULT.json');r=read(HERE/'RESULT.json');manifest=read(HERE/'MANIFEST.json')
 ignore={'at_utc','optimized','CPU_seconds','elapsed_seconds'}
 need({k:v for k,v in normal.items()if k not in ignore}=={k:v for k,v in optimized.items()if k not in ignore}and(normal['optimized'],optimized['optimized'])==(0,1),'Both cold modes same scientific certificate')
 for item in manifest['files']:
  need(hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'Sealed arithmetic runtime remains unchanged')
 gain=F(r['relative_gain_percent'])
 with localcontext()as c:
  c.prec=40;percent=str(Decimal(gain.numerator)/Decimal(gain.denominator))
 report=f'''PRIVATE G20/G23 ordinary successor complete, conditional on the same retained PR4760/PR4814 native/compiler/precision/completed-ROW implementation premises. No new PR.\n\nExact admitted ordinary BIT saving: {r['admitted']} = .003476110384. Comparator1737729/500000000=.003475458. Relative gain {r['relative_gain']} = {percent} percent, below0.1percent. This is distinct from the historicalrawroot .003476110419631239... and its different raw comparator. Wholekappa unchanged.\n\nThree frozen acyclic levels from completedPR4814: .003476103861, .003476110320, .003476110384. rho=.01, tested=.00347611041, uniform=.00347611040, covergap2^-36+1e-20, alpha_gap2^-39, v1024, primecoefficient2^45. Every completion at18^1024 and split at17^1024 is charged. ExactnewH0={r['tail']['new_H0']}, H1={r['tail']['new_H1']}. OldH0 rejected. These are rankcompiler thresholds; new tape/stock/precision and runtime cutoffs have separate explicit finite rules.\n\nAll original/helper jobs remain from the sealed literal provider:11400arbitraryRAW,57321actualqueries,2ownedbanks,1845episodes,18properrank4requests,485bitprefixheight. The independent arithmetic reader recounts P from the literal stream and T from actual original target owners, not a headline. All48native runtime bytes remain pinned. The independent rationalheight check reconstructs644frameprojectors, maxentry3bits and485bitresidual/VALUEenvelope, charged1024.\n\nFees are positive: base parking2614296168FIELDpasses exceeds old1e9 raw allowance; both internal7548 and canonical7248routes remain paid. The new finite DAG is bounded by explicit recursively defined integers J(n),A(n); ownedC_N<=2A(N) allocates per compiled unit, not perdepth. All route/normalizer/carry/parking/control work is bounded in retained primitive invocations by F=(q+2)^(32(N+1)^2)*(A(N)+2)^8, multiplying actual positive inherited backend/stream constants. Absolute machine constants, astronomicaluniformWORD,N andq are not materialized or declared1. New prime, height and eventual cutoff rules are explicitly fixed after finite compile. Stock remainsO_new(w loge) with restored complete spectators/ROW, and every fixed coefficient is absorbed only at a new threshold.\n\nIsolated normal/-O cold CLI bothPASS: primaryexactintervals plus independent positive-series/census audit. CPU {normal['CPU_seconds']}s / {optimized['CPU_seconds']}s. Runtime manifest {normal['certificate_manifest_sha256']}. Native provider manifest {normal['provider_manifest_sha256']}. Retained assumptions are explicitly conditional and root independent review is next. Published/frozen source trees and previous sealed native outputs were not edited.\n'''
 (HERE/'REPORT.txt').write_text(report,encoding='utf-8')
 latest={'status':'PRIVATE_CONDITIONAL_ORDINARY_G20_SUCCESSOR_COMPLETE','at_utc':datetime.now(timezone.utc).isoformat(),'read_first':'ordinary-certificate/REPORT.txt','certificate':pin(HERE/'RESULT.json'),'independent':pin(HERE/'INDEPENDENT.json'),'runtime_manifest':pin(HERE/'MANIFEST.json'),'normal':pin(HERE/'cold-normal-0001'/'RESULT.json'),'optimized':pin(HERE/'cold-optimized-0001'/'RESULT.json'),'admitted':r['admitted'],'comparator':r['comparator'],'relative_gain':r['relative_gain'],'relative_gain_percent_decimal':percent,'whole_kappa':None,'PR_created':False,'next':'Root independent exact proof/source/stock/fee review; private future bundle only. Do not decimal-tighten or rewrite old sealed manifests.'}
 put(ROOT/'LATEST-ORDINARY.json',latest)
 files=[HERE/'REPORT.txt',ROOT/'LATEST-ORDINARY.json',HERE/'RESULT.json',HERE/'INDEPENDENT.json',HERE/'FEE-BOUNDS.json',HERE/'RESTART.json',HERE/'MANIFEST.json',HERE/'cold-normal-0001'/'RESULT.json',HERE/'cold-optimized-0001'/'RESULT.json',HERE/'finish_receipts.py']
 put(HERE/'HANDOFF-MANIFEST.json',{'status':'APPEND_ONLY_COLD_ORDINARY_HANDOFF','files':[pin(p)for p in files]});print(json.dumps({'status':latest['status'],'admitted':r['admitted'],'relative_gain_percent':percent,'handoff_sha256':hashlib.sha256((HERE/'HANDOFF-MANIFEST.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()
