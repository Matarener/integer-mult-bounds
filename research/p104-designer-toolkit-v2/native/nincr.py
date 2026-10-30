"""nincr -- IncrWord with the chunk-replay kernel (IncrWord._run) in C (native/nativecore.c).  Bit-identical to incr.IncrWord by construction + tests/incr_fuzz.py --native-core.

    NIncrWord(word, profile=None)  same API as incr.IncrWord (subclass; only _run / initial_state / _post differ)
    make_incr(word, profile=None)  -> NIncrWord if TK_NATIVE_CORE=1 (and the kernel loads) else incr.IncrWord

State of a chunk boundary is an opaque little-endian bytes blob (cur int32[NR] | owned u8[NR] | pad | val u64[2][NR]) -- equality of blobs == equality of the Python state
tuples (values are canonical residues).  Events are packed once per event list (cache keyed by the list identity) into 8 x int32 records; coefficients are interned in an
append-only table through incr._coef (the exact Fraction analysis stays in Python).  Anything the kernel cannot represent (non-int fields, |x| >= 2^31, malformed events,
unparsable coefficients) falls back, for that chunk only, to the Python IncrWord._run on the decoded state (exact fallback).
"""
import os,sys,ctypes,struct,subprocess,array
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
import incr
from incr import _coef,_span
NONE=-2**31
SO=HERE+'/libnativecore.so'; SRC=HERE+'/nativecore.c'
def build(force=False):
    if force or not os.path.exists(SO) or os.path.getmtime(SO)<os.path.getmtime(SRC):
        subprocess.check_call(['cc','-O2','-shared','-fPIC','-o',SO+'.tmp',SRC]); os.replace(SO+'.tmp',SO)
_LIB=[None]
def lib():
    if _LIB[0] is None:
        build(); L=ctypes.CDLL(SO)
        L.nc_run.restype=ctypes.c_int
        L.nc_run.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_void_p,
                           ctypes.c_char_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
        L.nc_state_size.restype=ctypes.c_long; L.nc_state_size.argtypes=[ctypes.c_int]
        _LIB[0]=L
    return _LIB[0]
# ---- coefficient table (global, append-only)
_CI={}; _CTAB=[]          # value -> index ; list of 32-byte records
_CBUF=[None,0]            # (ctypes buffer, number of records in it)
_CSTRUCT=struct.Struct('<Qqq4B4x')
def _cidx(x):
    i=_CI.get(x)
    if i is None:
        q,n,d,qm,dy,grow,unit,cs,ca=_coef(x)
        if not(abs(cs)<2**62 and abs(ca)<2**62): raise OverflowError
        _CTAB.append(_CSTRUCT.pack(qm,cs,ca,0 if q else 1,int(dy),int(grow),int(unit))); i=_CI[x]=len(_CTAB)-1
    return i
def _ctab():
    if _CBUF[1]!=len(_CTAB):
        b=b''.join(_CTAB); buf=ctypes.create_string_buffer(b,len(b)+32); _CBUF[0]=buf; _CBUF[1]=len(_CTAB)
    return _CBUF[0]
# ---- event packing
_OPS={'MOVE':0,'INIT':1,'CLEAR':2,'SCALE':3,'COPY':4,'ADD':5}
def pack_events(evs):
    """-> bytes (n x 32) or None if some event is not representable"""
    flat=[]; ap=flat.extend; ops=_OPS
    try:
        for e in evs:
            o=ops.get(e[0],6); r=e[1]
            if o==0:
                _,r,a,b,pv=e; ap((0,r,0,a,b,1 if pv else 0,0,0))
            elif o<3: ap((o,r,0,0,0,0,e[2],0))
            elif o==3: ap((3,r,0,0,0,0,e[-1],_cidx(e[-2])))
            else: ap((o,r,e[2],0,0,0,e[-1],_cidx(e[-2])))
        if flat and min(flat)<=NONE: return None
        return struct.pack('<%di'%len(flat),*flat)
    except (struct.error,IndexError,TypeError,ValueError,ArithmeticError,OverflowError): return None
_SPB={}
def span_bits(b):
    v=_SPB.get(b)
    if v is None:
        m=0
        for x in _span(b): m|=1<<x
        v=_SPB[b]=m.to_bytes(64,'little')
    return v
RULES=['Role index','Transport source and ownership','Nested chronological transport','Owned initialization','Owned erasure at declared frame','Scalar destination and coefficient',
       'Dyadic scalar coefficient','Fixed scalar growth bound','Dyadic unit SCALE','Common scalar chart','COPY into cleared owned field','Scalar opcode']
class NIncrWord(incr.IncrWord):
    _nc_ready=False
    def _nc_setup(self):
        L=lib(); NR=self.NR; self._L=L; self._ssz=L.nc_state_size(NR)
        self._own=bytes(1 if r in self.OWN else 0 for r in range(NR))
        self._sbuf=ctypes.create_string_buffer(self._ssz); self._vcap=0; self._vbuf=None
        self._obuf=(ctypes.c_int64*19)(); self._nv=ctypes.c_int(0)
        self._eb={}; self._ft={}; self._ucnt=0; self._fallbacks=0; self._nruns=0
        self._stU=struct.Struct('<%di'%NR); self._vU=struct.Struct('<%dQ'%NR)
        self._nc_ready=True
    # ---- state codec
    def _encode(self,st):
        cur,owned,val=st
        c=self._stU.pack(*[NONE if x is None else x for x in cur])
        if any(x==NONE for x in cur if x is not None): raise OverflowError('frame index collides with the None sentinel')
        o=bytearray(self.NR)
        for r in owned: o[r]=1
        head=c+bytes(o); head+=bytes((-len(head))%8)
        return head+b''.join(self._vU.pack(*v) for v in val)
    def _decode(self,blob):
        NR=self.NR; cur=tuple(None if x==NONE else x for x in self._stU.unpack_from(blob,0))
        owned=frozenset(r for r in range(NR) if blob[4*NR+r])
        vo=(5*NR+7)&~7
        val=tuple(self._vU.unpack_from(blob,vo+8*NR*k) for k in range(2))
        return (cur,owned,val)
    def initial_state(self,initial):
        if not self._nc_ready: self._nc_setup()
        return self._encode(super().initial_state(initial))
    def _post(self,end,final,peak,life):
        if isinstance(end,bytes): end=self._decode(end)
        return super()._post(end,final,peak,life)
    # ---- frame table of a ctx
    def _ftab(self,ctx):
        t=self._ft.get(id(ctx))
        if t is None or t[0] is not ctx:
            if len(self._ft)>6: self._ft={k:v for k,v in self._ft.items() if v[0] is self.ctx}
            t=self._ft[id(ctx)]=(ctx,b''.join(span_bits(b) for b in ctx.bases),array.array('i',ctx.dim).tobytes(),len(ctx.bases))
        return t
    def _packed(self,evs):
        k=id(evs); t=self._eb.get(k)
        if t is None or t[0] is not evs:
            if len(self._eb)>4*len(self.chs)+64: self._eb={id(c.evs):self._eb[id(c.evs)] for c in self.chs if id(c.evs) in self._eb}
            t=self._eb[k]=(evs,pack_events(evs))
        return t[1]
    # ---- the kernel
    def _run(self,evs,state,ctx):
        if not self._nc_ready: self._nc_setup()
        pk=self._packed(evs)
        if pk is None or not evs:
            if not evs: return state,[],{},0,0,0
            return self._run_py(evs,state,ctx)
        _,sp,dm,nf=self._ftab(ctx); n=len(evs); vcap=4*n+8
        if self._vcap<vcap: self._vbuf=(ctypes.c_int32*(4*vcap))(); self._vcap=vcap
        L=self._L; rc=L.nc_run(self.NR,self._own,nf,sp,dm,pk,n,ctypes.addressof(_ctab()),state,ctypes.addressof(self._sbuf),ctypes.addressof(self._vbuf),self._vcap,ctypes.addressof(self._nv),ctypes.addressof(self._obuf))
        self._nruns+=1
        if rc==-1: raise IndexError('list index out of range')       # the message of the Python path (ctx.span -> bases[f])
        if rc!=0: raise RuntimeError('nativecore rc=%d'%rc)
        end=self._sbuf.raw; o=self._obuf; nv=self._nv.value
        paid={k:o[k] for k in range(16) if o[k]}
        V=[]
        if nv:
            vb=self._vbuf
            for j in range(nv): V.append(self._detail(evs,vb[4*j],vb[4*j+1],vb[4*j+2]))
        return end,V,paid,o[16],o[17],o[18]
    def _detail(self,evs,i,code,x):
        e=evs[i]; cx=None if x==NONE else x
        if code==0: return (i,RULES[0],e[1])
        if code==1: return (i,RULES[1],(e[1],cx,e[2],e[4]))
        if code==2: return (i,RULES[2],(e[1],e[2],e[3],e[4]))
        if code in(3,4,10): return (i,RULES[code],e[1])
        if code==5: return (i,RULES[5],(e[1],cx,e[-1]))
        if code in(6,7,8): return (i,RULES[code],_coef(e[-2])[0])
        if code==9:
            s=e[2]; return (i,RULES[9],(e[1],s,cx if 0<=s<self.NR else None,e[-1]))
        if code==11: return (i,RULES[11],e[0])
        raise RuntimeError('bad violation code %d'%code)
    def _run_py(self,evs,state,ctx):
        self._fallbacks+=1
        end,V,paid,scalar,life,peak=super()._run(evs,self._decode(state),ctx)
        return self._encode(end),V,paid,scalar,life,peak
def native_enabled(): return os.environ.get('TK_NATIVE_CORE')=='1'
def make_incr(word,profile=None,**kw):
    """IncrWord factory used by wsearch/evalincr: the C-kernel subclass under TK_NATIVE_CORE=1 (falls back to the Python class if the kernel cannot be built/loaded)"""
    if native_enabled():
        try: lib(); return NIncrWord(word,profile=profile,**kw)
        except (OSError,subprocess.CalledProcessError) as ex: sys.stderr.write('TK_NATIVE_CORE: kernel unavailable (%r), using python IncrWord\n'%(ex,))
    return incr.IncrWord(word,profile=profile,**kw)
