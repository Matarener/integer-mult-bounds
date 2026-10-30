/* Finite key-only comparator, not Cache/Event API replacement.
 * Baseline provenance: native_cache.c contribution(), Chris R / Clear1nsight,
 * substantial OpenAI Codex/Astra assistance. Apache-2.0.
 * All keys are exact seven-PyLong tuples; no arbitrary callbacks or cyclic values.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stddef.h>

#define WIDTH 7
#define EMPTY ((Py_ssize_t)-1)
#define TOMB ((Py_ssize_t)-2)
#define MAX_ROWS 3000000
#define PREFIX_EVERY 80

typedef struct {
    PyObject *part[WIDTH], *value;
    uint64_t hash;
    Py_ssize_t slot;
} Entry;
typedef struct {
    Entry *entry;
    Py_ssize_t *table, size, capacity, used, head, tombs, rehashes;
} Custom;

static int fault(Py_ssize_t at, int phase, Py_ssize_t wanted, int wanted_phase) {
    if (at == wanted && phase == wanted_phase) {
        PyErr_SetString(PyExc_MemoryError, "declared finite cleanup fault");
        return -1;
    }
    return 0;
}
static void entry_clear(Entry *e) {
    for (int j=0;j<WIDTH;j++) Py_CLEAR(e->part[j]);
    Py_CLEAR(e->value);
}
static void custom_clear(Custom *s) {
    if (s->entry) {
        for (Py_ssize_t j=0;j<s->capacity;j++) entry_clear(&s->entry[j]);
        PyMem_Free(s->entry);
    }
    PyMem_Free(s->table);
}
static Py_ssize_t *new_table(Py_ssize_t size) {
    Py_ssize_t *p=PyMem_Malloc((size_t)size * sizeof(*p));
    if (!p) { PyErr_NoMemory(); return NULL; }
    for (Py_ssize_t j=0;j<size;j++) p[j]=EMPTY;
    return p;
}
/* Unsigned 64-bit arithmetic is defined modulo 2^64. No PyLong layout access. */
static int hash_parts(PyObject *const part[WIDTH], uint64_t *answer) {
    uint64_t h=UINT64_C(0x9e3779b97f4a7c15);
    for (int j=0;j<WIDTH;j++) {
        Py_hash_t v=PyObject_Hash(part[j]);
        if (v == -1) return -1;
        h ^= (uint64_t)v + UINT64_C(0x9e3779b97f4a7c15) + (h << 6) + (h >> 2);
        h *= UINT64_C(0xbf58476d1ce4e5b9);
    }
    *answer=h;
    return 0;
}
static int equal_parts(Entry *e, PyObject *const part[WIDTH]) {
    for (int j=0;j<WIDTH;j++) {
        int eq=PyObject_RichCompareBool(e->part[j], part[j], Py_EQ);
        if (eq <= 0) return eq;
    }
    return 1;
}
/* Return 1 for found, 0 for absent, -1 for error; never treat a tomb as empty. */
static int lookup(Custom *s, PyObject *const part[WIDTH], uint64_t hash,
                  Py_ssize_t *entry_index) {
    Py_ssize_t slot=(Py_ssize_t)(hash & (uint64_t)(s->size-1));
    for (Py_ssize_t steps=0;steps<s->size;steps++) {
        Py_ssize_t ix=s->table[slot];
        if (ix == EMPTY) return 0;
        if (ix >= 0 && s->entry[ix].hash == hash) {
            int eq=equal_parts(&s->entry[ix],part);
            if (eq < 0) return -1;
            if (eq) { *entry_index=ix; return 1; }
        }
        slot=(slot+1)&(s->size-1);
    }
    PyErr_SetString(PyExc_RuntimeError,"table unexpectedly has no empty slot");
    return -1;
}
static Py_ssize_t vacant_slot(Py_ssize_t *table, Py_ssize_t size, uint64_t hash) {
    Py_ssize_t slot=(Py_ssize_t)(hash & (uint64_t)(size-1));
    for (Py_ssize_t steps=0;steps<size;steps++) {
        if (table[slot] < 0) return slot;
        slot=(slot+1)&(size-1);
    }
    PyErr_SetString(PyExc_RuntimeError,"table unexpectedly full");
    return -1;
}
static int rehash(Custom *s, int fail_allocation) {
    if (fail_allocation) { PyErr_NoMemory(); return -1; }
    Py_ssize_t *next=new_table(s->size);
    if (!next) return -1;
    for (Py_ssize_t j=0;j<s->capacity;j++) if (s->entry[j].value) {
        Py_ssize_t slot=vacant_slot(next,s->size,s->entry[j].hash);
        if (slot < 0) { PyMem_Free(next); return -1; }
        next[slot]=j;
    }
    /* Publish only after the new table is complete. */
    PyMem_Free(s->table); s->table=next;
    for (Py_ssize_t j=0;j<s->size;j++) if (next[j]>=0) s->entry[next[j]].slot=j;
    s->tombs=0; s->rehashes++;
    return 0;
}
static int exact_int(PyObject *o, Py_ssize_t *v, const char *name) {
    if (!PyLong_CheckExact(o)) { PyErr_Format(PyExc_TypeError,"exact int required: %s",name); return -1; }
    *v=PyLong_AsSsize_t(o);
    return PyErr_Occurred() ? -1 : 0;
}
static PyObject *run(PyObject *module, PyObject *args) {
    (void)module;
    PyObject *kind_o,*rows,*cap_o,*fail_o=NULL,*phase_o=NULL;
    Py_ssize_t kind,cap,fail_at=-1,phase_n=0;
    if (!PyArg_UnpackTuple(args,"run",3,5,&kind_o,&rows,&cap_o,&fail_o,&phase_o)) return NULL;
    if (exact_int(kind_o,&kind,"kind")<0 || exact_int(cap_o,&cap,"capacity")<0) return NULL;
    if (fail_o && exact_int(fail_o,&fail_at,"fail_at")<0) return NULL;
    if (phase_o && exact_int(phase_o,&phase_n,"fail_phase")<0) return NULL;
    if ((kind!=0 && kind!=1) || cap<1 || cap>16384 || fail_at < -1 || phase_n<0 || phase_n>6) {
        PyErr_SetString(PyExc_ValueError,"kind 0/1, capacity 1..16384, fail_at >= -1, phase 0..6"); return NULL;
    }
    if (!PyTuple_CheckExact(rows)) { PyErr_SetString(PyExc_TypeError,"exact tuple of keys"); return NULL; }
    Py_ssize_t n=PyTuple_GET_SIZE(rows);
    if (n>MAX_ROWS || fail_at>=n) { PyErr_SetString(PyExc_ValueError,"bounded corpus/failure index"); return NULL; }
    if ((fail_at==-1)!=(phase_n==0) || (kind==0 && phase_n==6)) {
        PyErr_SetString(PyExc_ValueError,"consistent failure specification; rehash fault is custom only"); return NULL;
    }
    for (Py_ssize_t i=0;i<n;i++) {
        PyObject *row=PyTuple_GET_ITEM(rows,i);
        if (!PyTuple_CheckExact(row) || PyTuple_GET_SIZE(row)!=WIDTH) {
            PyErr_SetString(PyExc_TypeError,"each key is an exact 7-tuple"); return NULL;
        }
        for (int j=0;j<WIDTH;j++) if (!PyLong_CheckExact(PyTuple_GET_ITEM(row,j))) {
            PyErr_SetString(PyExc_TypeError,"each field is an exact int"); return NULL;
        }
    }
    Custom s={0}; s.capacity=cap; s.size=8;
    while (s.size<2*cap) s.size*=2;
    PyObject *dict=NULL,**ring=NULL,*key=NULL,*result=NULL,*ids=NULL,*flags=NULL,*prefix=NULL,*stats=NULL,*answer=NULL;
    Py_ssize_t used=0,head=0,hits=0,misses=0,evictions=0,prefix_index=0;
    ids=PyTuple_New(n); flags=PyBytes_FromStringAndSize(NULL,n);
    prefix=PyTuple_New((n+PREFIX_EVERY-1)/PREFIX_EVERY);
    if (!ids || !flags || !prefix) goto done;
    if (kind==0) {
        dict=PyDict_New(); ring=PyMem_Calloc((size_t)cap,sizeof(*ring));
        if (!dict || !ring) { if (!PyErr_Occurred()) PyErr_NoMemory(); goto done; }
    } else {
        s.entry=PyMem_Calloc((size_t)cap,sizeof(*s.entry)); s.table=new_table(s.size);
        if (!s.entry || !s.table) { if (!PyErr_Occurred()) PyErr_NoMemory(); goto done; }
    }
    for (Py_ssize_t i=0;i<n;i++) {
        PyObject *row=PyTuple_GET_ITEM(rows,i),*part[WIDTH];
        for (int j=0;j<WIDTH;j++) part[j]=PyTuple_GET_ITEM(row,j);
        int found=0; uint64_t hash=0; Py_ssize_t ix=-1;
        unsigned char flag=0;
        if (kind==0) {
            key=PyTuple_New(WIDTH); if (!key) goto done;
            for (int j=0;j<WIDTH;j++) PyTuple_SET_ITEM(key,j,Py_NewRef(part[j]));
            PyObject *borrowed=PyDict_GetItemWithError(dict,key);
            if (borrowed) { result=Py_NewRef(borrowed); found=1; }
            else if (PyErr_Occurred()) goto done;
        } else {
            if (hash_parts(part,&hash)<0) goto done;
            found=lookup(&s,part,hash,&ix); if (found<0) goto done;
            if (found) result=Py_NewRef(s.entry[ix].value);
        }
        if (fault(i,1,fail_at,(int)phase_n)<0) goto done;
        if (found) hits++;
        else {
            misses++; flag=1;
            result=PyLong_FromSsize_t(misses); if (!result) goto done;
            if (fault(i,2,fail_at,(int)phase_n)<0) goto done;
            if (kind==1 && (s.used+s.tombs>=s.size*3/4 || (i==fail_at && phase_n==6))) {
                /* Phase 6 simulates allocation failure before publishing a new table. */
                if (rehash(&s,i==fail_at && phase_n==6)<0) goto done;
            }
            if (used==cap) {
                if (kind==0) {
                    if (PyDict_DelItem(dict,ring[head])<0) goto done;
                    Py_CLEAR(ring[head]);
                } else {
                    Entry *old=&s.entry[head];
                    s.table[old->slot]=TOMB; s.tombs++;
                    entry_clear(old); s.used--;
                }
                used--; evictions++; flag|=2;
            }
            if (fault(i,3,fail_at,(int)phase_n)<0) goto done;
            if (kind==0) {
                if (PyDict_SetItem(dict,key,result)<0) goto done;
                ring[head]=key; key=NULL;
            } else {
                Py_ssize_t slot=vacant_slot(s.table,s.size,hash); if (slot<0) goto done;
                Entry *e=&s.entry[head];
                for (int j=0;j<WIDTH;j++) e->part[j]=Py_NewRef(part[j]);
                e->value=Py_NewRef(result); e->hash=hash; e->slot=slot;
                if (s.table[slot]==TOMB) s.tombs--;
                s.table[slot]=head; s.used++;
            }
            head=(head+1)%cap; used++;
            if (fault(i,4,fail_at,(int)phase_n)<0) goto done;
        }
        Py_CLEAR(key);
        PyTuple_SET_ITEM(ids,i,result); result=NULL;
        PyBytes_AS_STRING(flags)[i]=(char)flag;
        if (fault(i,5,fail_at,(int)phase_n)<0) goto done;
        if ((i+1)%PREFIX_EVERY==0 || i+1==n) {
            PyObject *p=Py_BuildValue("(nnnnn)",i+1,hits,misses,evictions,used);
            if (!p) goto done;
            PyTuple_SET_ITEM(prefix,prefix_index++,p);
        }
    }
    stats=Py_BuildValue("{s:n,s:n,s:n,s:n,s:n,s:n,s:n}","calls",n,"hits",hits,"misses",misses,"evictions",evictions,"resident",used,"capacity",cap,"rehashes",s.rehashes);
    if (!stats) goto done;
    answer=PyTuple_Pack(4,ids,flags,prefix,stats);
done:
    Py_XDECREF(key); Py_XDECREF(result); Py_XDECREF(dict);
    if (ring) { for (Py_ssize_t j=0;j<cap;j++) Py_XDECREF(ring[j]); PyMem_Free(ring); }
    custom_clear(&s);
    Py_XDECREF(ids); Py_XDECREF(flags); Py_XDECREF(prefix); Py_XDECREF(stats);
    return answer;
}
static PyMethodDef methods[]={{"run",run,METH_VARARGS,"Private finite key comparator; 0=dict, 1=custom."},{NULL,NULL,0,NULL}};
static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_keypilot","Finite key-only pilot.",-1,methods,NULL,NULL,NULL,NULL};
PyMODINIT_FUNC PyInit__keypilot(void) { return PyModule_Create(&module); }
