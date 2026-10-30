"""store -- SQLite result store of the word search (SEARCHCORE).  Default ext/SEARCH/store.sqlite; WAL + busy timeout so several cpuq workers can write.
Tables: words(chash, blob=gzip JSON word, nev, npub)   evals(chash, profile, legal, ok, kappa REAL, kappa_str, lo, hi, side_ok, relaxed)
        lineage(chash, parent, edit JSON, class, seed, run_id, step)   validations(chash, level in fast|accept|prstack, ok, detail JSON)
        checkpoints(run_id, state JSON)   -- kappa_str/lo/hi are the exact Decimal-50 root and the 1e-14 crossing interval (strings)."""
import sqlite3,gzip,json,time,os
W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DEFAULT=W + '/ext/SEARCH/store.sqlite'
SCHEMA="""
CREATE TABLE IF NOT EXISTS words(chash TEXT PRIMARY KEY, blob BLOB NOT NULL, nev INT, npub INT, ts REAL);
CREATE TABLE IF NOT EXISTS evals(chash TEXT NOT NULL, profile TEXT NOT NULL, legal INT, ok INT, kappa REAL, kappa_str TEXT, lo TEXT, hi TEXT, side_ok INT, relaxed INT DEFAULT 0, ts REAL, PRIMARY KEY(chash,profile));
CREATE INDEX IF NOT EXISTS evals_k ON evals(kappa);
CREATE TABLE IF NOT EXISTS lineage(chash TEXT NOT NULL, parent TEXT, edit TEXT, class TEXT, seed INT, run_id TEXT, step INT, ts REAL, PRIMARY KEY(chash,parent));
CREATE TABLE IF NOT EXISTS validations(chash TEXT NOT NULL, level TEXT NOT NULL, ok INT, detail TEXT, ts REAL, PRIMARY KEY(chash,level));
CREATE TABLE IF NOT EXISTS checkpoints(run_id TEXT PRIMARY KEY, state TEXT, ts REAL);
"""
class Store:
    def __init__(s,path=None):
        s.path=path or DEFAULT; os.makedirs(os.path.dirname(s.path),exist_ok=True)
        s.db=sqlite3.connect(s.path,timeout=120,isolation_level=None); s.db.row_factory=sqlite3.Row
        s.db.execute('PRAGMA journal_mode=WAL'); s.db.execute('PRAGMA synchronous=NORMAL'); s.db.execute('PRAGMA busy_timeout=120000')
        s.db.executescript(SCHEMA)
    def _w(s,sql,args=()):
        s.db.execute('BEGIN IMMEDIATE')
        try: c=s.db.execute(sql,args); s.db.execute('COMMIT'); return c
        except Exception: s.db.execute('ROLLBACK'); raise
    def put_word(s,chash,w):
        if s.db.execute('SELECT 1 FROM words WHERE chash=?',(chash,)).fetchone(): return False
        blob=gzip.compress(json.dumps(w,separators=(',',':')).encode(),compresslevel=6)
        s._w('INSERT OR IGNORE INTO words VALUES(?,?,?,?,?)',(chash,blob,len(w['program']),len(w['initial']),time.time())); return True
    def get_word(s,chash):
        r=s.db.execute('SELECT blob FROM words WHERE chash=?',(chash,)).fetchone()
        return json.loads(gzip.decompress(r['blob'])) if r else None
    def add_eval(s,chash,profile,legal,kappa,iv=None,ok=None,validator='fast',relaxed=False,side_ok=None):
        iv=iv or {}
        s._w('INSERT OR REPLACE INTO evals VALUES(?,?,?,?,?,?,?,?,?,?,?)',(chash,profile,int(bool(legal)),int(bool(ok if ok is not None else legal)),kappa,iv.get('kappa'),iv.get('lo'),iv.get('hi'),None if side_ok is None else int(bool(side_ok)),int(relaxed),time.time()))
        if validator: s.add_validation(chash,validator,bool(ok if ok is not None else legal),dict(kappa=kappa))
    def get_eval(s,chash,profile=None):
        q='SELECT * FROM evals WHERE chash=?'+(' AND profile=?' if profile else ''); r=s.db.execute(q,(chash,)+((profile,) if profile else ())).fetchone(); return dict(r) if r else None
    def add_lineage(s,chash,parent,edit,cls,seed,run_id,step):
        s._w('INSERT OR IGNORE INTO lineage VALUES(?,?,?,?,?,?,?,?)',(chash,parent or '',json.dumps(edit,default=str)[:4000],cls,seed,run_id,step,time.time()))
    def add_validation(s,chash,level,ok,detail=None):
        s._w('INSERT OR REPLACE INTO validations VALUES(?,?,?,?,?)',(chash,level,int(bool(ok)),json.dumps(detail,default=str)[:20000],time.time()))
    def validations(s,chash): return {r['level']:dict(ok=bool(r['ok']),detail=r['detail']) for r in s.db.execute('SELECT * FROM validations WHERE chash=?',(chash,))}
    def save_ck(s,run_id,state): s._w('INSERT OR REPLACE INTO checkpoints VALUES(?,?,?)',(run_id,json.dumps(state,default=str),time.time()))
    def load_ck(s,run_id):
        r=s.db.execute('SELECT state FROM checkpoints WHERE run_id=?',(run_id,)).fetchone(); return json.loads(r['state']) if r else None
    def best(s,k=10,profile=None,legal_only=True):
        q='SELECT * FROM evals WHERE kappa IS NOT NULL'+(' AND ok=1' if legal_only else '')+(' AND profile=?' if profile else '')+' ORDER BY kappa DESC LIMIT ?'
        return [dict(r) for r in s.db.execute(q,((profile,) if profile else ())+(k,))]
    def chain(s,chash,maxlen=60):
        """lineage back to the root: [(chash, class, edit)] newest first"""
        out=[];seen=set()
        while chash and chash not in seen and len(out)<maxlen:
            seen.add(chash); r=s.db.execute('SELECT * FROM lineage WHERE chash=? ORDER BY ts LIMIT 1',(chash,)).fetchone()
            if not r: out.append((chash,'root',None)); break
            out.append((chash,r['class'],r['edit'])); chash=r['parent']
        return out
    def stats(s): return {t:s.db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in('words','evals','lineage','validations','checkpoints')}
