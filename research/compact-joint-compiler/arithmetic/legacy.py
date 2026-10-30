"""Independent 63-predicate retained outer ledger at an explicit finer grid.
Source notices and exact retained function are in legacy-source.txt.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256

def need(ok,message):
 if not ok:raise ValueError(message)

def check(params,outer,kappa):
 source=Path(__file__).resolve().with_name('legacy-source.txt');raw=source.read_bytes()
 d=params['d'];eps,beta,q,a=(params[k]for k in('epsilon','beta','q','a'));grid=10**20
 backoff=Q((eps*q*grid).__floor__(),grid)-kappa;need(backoff>0,'Positive exact refined-grid backoff')
 env={'Q':Q,'R0':params['r0'],'ZETA':Q(1,10**8),'SLACK':d,'STOP':d,'FLOOR':grid,'BACKOFF':backoff,'EPS':eps,'BETA':beta,'THETA_POWER':Q(2),'HALO_POWER':48,'CORE_POWER':128,'STRASSEN_TAU':Q(45,16),'b':params['b'],'q':q,'a':a,'bit':params['bit_saving'],'online':Q('0.001730970419199163702738'),'old':Q('0.001730970419199163702738')}
 exec(compile(raw,'frozen legacy outer source','exec'),env)
 result=env['ledger']('compact4470')
 need(result['kappa']==kappa and result['margins']==outer['margins'],'Independent nine-row agreement')
 need(len(result['strict_checks'])==63 and all(x>0 for x in result['strict_checks'].values()),'All 63 legacy predicates')
 return {'strict_checks':result['strict_checks'],'grid':grid,'backoff':backoff,'nine_row_agreement':True,'source_sha256':sha256(raw).hexdigest()}
