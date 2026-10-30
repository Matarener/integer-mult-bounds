/* Exact bounded cache/control only. All Fraction arithmetic stays in Python.
 * Chris R / Clear1nsight, substantial OpenAI Codex/Astra assistance. Apache-2.0.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>

/* Diagnostic capture only: off by default; exact existing contribution keys. */
#define ACTUAL_CAPTURE_CALLS ((Py_ssize_t)2579750)
static PyObject *capture_keys=NULL;
static int capture_active=0;

static int capture_key(PyObject *key) {
    if (!capture_active || !capture_keys) {
        PyErr_SetString(PyExc_RuntimeError,"capture protocol inactive"); return -1;
    }
    if (PyList_GET_SIZE(capture_keys)>=ACTUAL_CAPTURE_CALLS) {
        PyErr_SetString(PyExc_OverflowError,"actual capture exceeds fixed complete call count"); return -1;
    }
    return PyList_Append(capture_keys,key);
}
static PyObject *capture_begin(PyObject *module, PyObject *unused) {
    (void)module; (void)unused;
    if (capture_active || capture_keys) {
        PyErr_SetString(PyExc_RuntimeError,"one active actual capture only"); return NULL;
    }
    capture_keys=PyList_New(0);
    if (!capture_keys) return NULL;
    capture_active=1; Py_RETURN_NONE;
}
static PyObject *capture_take(PyObject *module, PyObject *unused) {
    (void)module; (void)unused;
    if (!capture_active || !capture_keys || PyList_GET_SIZE(capture_keys)!=ACTUAL_CAPTURE_CALLS) {
        PyErr_SetString(PyExc_RuntimeError,"complete active actual key capture required"); return NULL;
    }
    PyObject *answer=PyList_AsTuple(capture_keys);
    if (!answer) return NULL;
    capture_active=0; Py_CLEAR(capture_keys);
    return answer;
}
static PyObject *capture_abort(PyObject *module, PyObject *unused) {
    (void)module; (void)unused;
    capture_active=0; Py_CLEAR(capture_keys); Py_RETURN_NONE;
}
static PyMethodDef capture_methods[]={
    {"_capture_begin",capture_begin,METH_NOARGS,"Begin one complete actual key capture."},
    {"_capture_take",capture_take,METH_NOARGS,"Take every captured original key, then clear."},
    {"_capture_abort",capture_abort,METH_NOARGS,"Idempotently clear capture on every path."},
    {NULL,NULL,0,NULL}
};

typedef struct {
    PyObject_HEAD
    PyObject *dict, *weights, *tokens, *compute, *num, *den, *fraction;
    PyObject **ring;
    Py_ssize_t capacity, used, head, calls, hits, misses, evictions;
    int ready, busy;
} Cache;
typedef struct {
    PyObject_HEAD
    vectorcallfunc vectorcall;
    Cache *cache;
    PyObject *q, *qn, *qd;
} Event;
static PyTypeObject CacheType, EventType;

static int cache_traverse(Cache *s, visitproc visit, void *arg) {
    Py_VISIT(s->dict); Py_VISIT(s->weights); Py_VISIT(s->tokens);
    Py_VISIT(s->compute); Py_VISIT(s->num); Py_VISIT(s->den); Py_VISIT(s->fraction);
    if (s->ring) for (Py_ssize_t i=0;i<s->capacity;i++) Py_VISIT(s->ring[i]);
    return 0;
}
static int cache_clear(Cache *s) {
    s->ready=0; s->busy=1;
    if (s->ring) {
        for (Py_ssize_t i=0;i<s->capacity;i++) Py_CLEAR(s->ring[i]);
        PyMem_Free(s->ring); s->ring=NULL;
    }
    Py_CLEAR(s->dict); Py_CLEAR(s->weights); Py_CLEAR(s->tokens);
    Py_CLEAR(s->compute); Py_CLEAR(s->num); Py_CLEAR(s->den); Py_CLEAR(s->fraction);
    return 0;
}
static void cache_dealloc(Cache *s) {
    PyObject_GC_UnTrack(s); cache_clear(s); Py_TYPE(s)->tp_free((PyObject *)s);
}
static int event_traverse(Event *s, visitproc visit, void *arg) {
    Py_VISIT(s->cache); Py_VISIT(s->q); Py_VISIT(s->qn); Py_VISIT(s->qd); return 0;
}
static int event_clear(Event *s) {
    Py_CLEAR(s->cache); Py_CLEAR(s->q); Py_CLEAR(s->qn); Py_CLEAR(s->qd); return 0;
}
static void event_dealloc(Event *s) {
    PyObject_GC_UnTrack(s); event_clear(s); Py_TYPE(s)->tp_free((PyObject *)s);
}
static PyObject *event_disabled(PyTypeObject *type, PyObject *args, PyObject *kw) {
    (void)type; (void)args; (void)kw;
    PyErr_SetString(PyExc_TypeError,"events are created only by Cache.event"); return NULL;
}
static int is_pair(PyObject *p) {
    return (PyList_CheckExact(p)||PyTuple_CheckExact(p)) && PySequence_Size(p)>=2;
}
static PyObject *cache_new(PyTypeObject *type, PyObject *args, PyObject *kw) {
    if (kw && PyDict_Size(kw)) { PyErr_SetString(PyExc_TypeError,"positional cache arguments only");return NULL; }
    PyObject *cap,*weights,*tokens,*compute,*num,*den,*fraction;
    if (!PyArg_UnpackTuple(args,"Cache",7,7,&cap,&weights,&tokens,&compute,&num,&den,&fraction)) return NULL;
    if (!PyLong_CheckExact(cap)) { PyErr_SetString(PyExc_ValueError,"integer capacity");return NULL; }
    Py_ssize_t ncap=PyLong_AsSsize_t(cap);
    if (ncap<1 || ncap>16384 || PyErr_Occurred()) { if(!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError,"capacity 1..16384");return NULL; }
    if (!(PyList_CheckExact(weights)||PyTuple_CheckExact(weights)) || !PyList_CheckExact(tokens) || !PyFunction_Check(compute) || !PyType_Check(fraction) || Py_TYPE(num)!=&PyMemberDescr_Type || Py_TYPE(den)!=&PyMemberDescr_Type || !Py_TYPE(num)->tp_descr_get || !Py_TYPE(den)->tp_descr_get) {
        PyErr_SetString(PyExc_TypeError,"exact native packet types");return NULL;
    }
    Py_ssize_t n=PySequence_Size(weights);
    if (PyList_GET_SIZE(tokens)!=n) { PyErr_SetString(PyExc_ValueError,"weight/token size");return NULL; }
    Cache *s=(Cache *)type->tp_alloc(type,0);
    if (!s) return NULL;
    s->capacity=ncap;
    s->dict=PyDict_New();s->weights=PyTuple_New(n);s->tokens=PyTuple_New(n);
    s->ring=PyMem_Calloc((size_t)ncap,sizeof(PyObject *));
    if (!s->dict || !s->weights || !s->tokens || !s->ring) { if(!PyErr_Occurred())PyErr_NoMemory();Py_DECREF(s);return NULL; }
    s->compute=Py_NewRef(compute);s->num=Py_NewRef(num);s->den=Py_NewRef(den);s->fraction=Py_NewRef(fraction);
    for (Py_ssize_t i=0;i<n;i++) {
        PyObject *row=PySequence_GetItem(weights,i);
        if (!row) { Py_DECREF(s);return NULL; }
        if (!is_pair(row)) { Py_DECREF(row);Py_DECREF(s);PyErr_SetString(PyExc_TypeError,"weight pair");return NULL; }
        PyObject *a=PySequence_GetItem(row,0),*c=PySequence_GetItem(row,1);Py_DECREF(row);
        if (!a || !c) { Py_XDECREF(a);Py_XDECREF(c);Py_DECREF(s);return NULL; }
        if (!Py_IS_TYPE(a,(PyTypeObject *)fraction)||!Py_IS_TYPE(c,(PyTypeObject *)fraction)) { Py_DECREF(a);Py_DECREF(c);Py_DECREF(s);PyErr_SetString(PyExc_TypeError,"exact Fraction weights");return NULL; }
        PyObject *pair=PyTuple_New(2);
        if (!pair) { Py_DECREF(a);Py_DECREF(c);Py_DECREF(s);return NULL; }
        PyTuple_SET_ITEM(pair,0,a);PyTuple_SET_ITEM(pair,1,c);PyTuple_SET_ITEM(s->weights,i,pair);
        PyObject *token=PySequence_GetItem(tokens,i);
        if (!token) { Py_DECREF(s);return NULL; }
        if (!PyLong_CheckExact(token)) { Py_DECREF(token);Py_DECREF(s);PyErr_SetString(PyExc_TypeError,"integer token");return NULL; }
        Py_ssize_t t=PyLong_AsSsize_t(token);
        if (t<0 || t>=16384 || PyErr_Occurred()) { Py_DECREF(token);Py_DECREF(s);if(!PyErr_Occurred())PyErr_SetString(PyExc_ValueError,"bounded token");return NULL; }
        PyTuple_SET_ITEM(s->tokens,i,token);
    }
    s->ready=1;return (PyObject *)s;
}
static PyObject *member(PyObject *descriptor, PyObject *object, PyObject *type) {
    return Py_TYPE(descriptor)->tp_descr_get(descriptor,object,type);
}
static PyObject *contribution(Event *e, PyObject *old, PyObject *v, Py_ssize_t i) {
    Cache *s=e->cache;
    if (i<0 || i>=PyTuple_GET_SIZE(s->tokens)) { PyErr_SetString(PyExc_IndexError,"native site index");return NULL; }
    if (!Py_IS_TYPE(old,(PyTypeObject *)s->fraction)||!Py_IS_TYPE(v,(PyTypeObject *)s->fraction)) { PyErr_SetString(PyExc_TypeError,"exact Fraction coefficients");return NULL; }
    PyObject *parts[4]={NULL,NULL,NULL,NULL};
    for (int k=0;k<4;k++) {
        parts[k]=member(k%2?s->den:s->num,k<2?old:v,s->fraction);
        if (!parts[k] || !PyLong_CheckExact(parts[k])) {
            for(int j=0;j<4;j++)Py_XDECREF(parts[j]);
            if(!PyErr_Occurred())PyErr_SetString(PyExc_TypeError,"integer Fraction slots");
            return NULL;
        }
    }
    PyObject *key=PyTuple_New(7);
    if(!key){for(int j=0;j<4;j++)Py_DECREF(parts[j]);return NULL;}
    PyTuple_SET_ITEM(key,0,parts[0]);PyTuple_SET_ITEM(key,1,parts[1]);
    PyTuple_SET_ITEM(key,2,Py_NewRef(e->qn));PyTuple_SET_ITEM(key,3,Py_NewRef(e->qd));
    PyTuple_SET_ITEM(key,4,parts[2]);PyTuple_SET_ITEM(key,5,parts[3]);PyTuple_SET_ITEM(key,6,Py_NewRef(PyTuple_GET_ITEM(s->tokens,i)));
    if(capture_active && capture_key(key)<0){Py_DECREF(key);return NULL;}
    if(s->calls==PY_SSIZE_T_MAX){Py_DECREF(key);PyErr_SetString(PyExc_OverflowError,"native counter overflow");return NULL;}
    s->calls++;
    PyObject *result=PyDict_GetItemWithError(s->dict,key);
    if(result){s->hits++;Py_INCREF(result);Py_DECREF(key);return result;}
    if(PyErr_Occurred()){Py_DECREF(key);return NULL;}
    s->misses++;
    PyObject *pair=PyTuple_GET_ITEM(s->weights,i);
    PyObject *argv[5]={old,e->q,v,PyTuple_GET_ITEM(pair,0),PyTuple_GET_ITEM(pair,1)};
    result=PyObject_Vectorcall(s->compute,argv,5,NULL);
    if(!result){Py_DECREF(key);return NULL;}
    if(!PyTuple_CheckExact(result)||PyTuple_GET_SIZE(result)!=4){Py_DECREF(result);Py_DECREF(key);PyErr_SetString(PyExc_TypeError,"four exact contributions");return NULL;}
    for(int k=0;k<4;k++)if(!Py_IS_TYPE(PyTuple_GET_ITEM(result,k),(PyTypeObject *)s->fraction)){Py_DECREF(result);Py_DECREF(key);PyErr_SetString(PyExc_TypeError,"Fraction contributions");return NULL;}
    if(s->used==s->capacity){
        PyObject *oldkey=s->ring[s->head];
        if(PyDict_DelItem(s->dict,oldkey)<0){Py_DECREF(result);Py_DECREF(key);return NULL;}
        Py_CLEAR(s->ring[s->head]);s->used--;s->evictions++;
    }
    if(PyDict_SetItem(s->dict,key,result)<0){Py_DECREF(result);Py_DECREF(key);return NULL;}
    s->ring[s->head]=key;s->head=(s->head+1)%s->capacity;s->used++;
    return result;
}
static int begin_event(Event *e) {
    if(!e->cache||!e->cache->ready){PyErr_SetString(PyExc_RuntimeError,"cleared native event");return -1;}
    if(e->cache->busy){PyErr_SetString(PyExc_RuntimeError,"reentrant native event");return -1;}
    e->cache->busy=1;return 0;
}
static PyObject *event_call(PyObject *obj, PyObject *const *args, size_t nargsf, PyObject *kw) {
    Event *e=(Event *)obj;
    if(PyVectorcall_NARGS(nargsf)!=3 || (kw&&PyTuple_GET_SIZE(kw))){PyErr_SetString(PyExc_TypeError,"event(old,v,index)");return NULL;}
    if(!PyLong_CheckExact(args[2])){PyErr_SetString(PyExc_TypeError,"integer site index");return NULL;}
    Py_ssize_t i=PyLong_AsSsize_t(args[2]);if(PyErr_Occurred())return NULL;
    if(begin_event(e)<0)return NULL;
    PyObject *result=contribution(e,args[0],args[1],i);e->cache->busy=0;return result;
}
static PyObject *cache_event(Cache *s, PyObject *q) {
    if(!s->ready){PyErr_SetString(PyExc_RuntimeError,"cleared cache");return NULL;}
    if(!Py_IS_TYPE(q,(PyTypeObject *)s->fraction)){PyErr_SetString(PyExc_TypeError,"exact Fraction scalar");return NULL;}
    Event *e=(Event *)EventType.tp_alloc(&EventType,0);if(!e)return NULL;
    e->vectorcall=event_call;e->cache=(Cache *)Py_NewRef((PyObject *)s);e->q=Py_NewRef(q);
    e->qn=member(s->num,q,s->fraction);
    if(!e->qn){Py_DECREF(e);return NULL;}
    e->qd=member(s->den,q,s->fraction);
    if(!e->qd){Py_DECREF(e);return NULL;}
    if(!PyLong_CheckExact(e->qn)||!PyLong_CheckExact(e->qd)){Py_DECREF(e);PyErr_SetString(PyExc_TypeError,"integer scalar slots");return NULL;}
    return (PyObject *)e;
}
static PyObject *cache_statistics(Cache *s, PyObject *unused) {
    (void)unused;
    if(!s->ready){PyErr_SetString(PyExc_RuntimeError,"cleared cache");return NULL;}
    return Py_BuildValue("{s:n,s:n,s:n,s:n,s:n,s:n,s:n}","calls",s->calls,"hits",s->hits,"misses",s->misses,"evictions",s->evictions,"bypasses",(Py_ssize_t)0,"resident",PyDict_Size(s->dict),"capacity",s->capacity);
}
static PyObject *event_apply(Event *e, PyObject *args) {
    PyObject *dst,*src,*scores;
    if(!PyArg_UnpackTuple(args,"apply",3,3,&dst,&src,&scores))return NULL;
    if(!PyDict_CheckExact(dst)||!PyDict_CheckExact(src)||dst==src||!PyList_CheckExact(scores)||PyList_GET_SIZE(scores)!=3){PyErr_SetString(PyExc_TypeError,"distinct exact rows and three scores");return NULL;}
    if(begin_event(e)<0)return NULL;
    Cache *s=e->cache;
    PyObject *pair=NULL,*result=NULL;
    PyObject *view=PyObject_CallMethod(src,"items",NULL);
    PyObject *iterator=view?PyObject_GetIter(view):NULL;
    Py_XDECREF(view);
    if(!iterator)goto fail;
    while((pair=PyIter_Next(iterator))){
        if(!PyTuple_CheckExact(pair)||PyTuple_GET_SIZE(pair)!=2){PyErr_SetString(PyExc_TypeError,"dict item pair");goto fail;}
        PyObject *index=PyTuple_GET_ITEM(pair,0),*value=PyTuple_GET_ITEM(pair,1);
        if(!PyLong_CheckExact(index)){PyErr_SetString(PyExc_TypeError,"integer source site");goto fail;}
        Py_ssize_t i=PyLong_AsSsize_t(index);if(PyErr_Occurred())goto fail;
        PyObject *zeroarg=PyLong_FromLong(0);if(!zeroarg)goto fail;
        PyObject *zero=PyObject_CallOneArg(s->fraction,zeroarg);Py_DECREF(zeroarg);if(!zero)goto fail;
        PyObject *old=PyDict_GetItemWithError(dst,index);
        if(old){Py_INCREF(old);Py_DECREF(zero);}else if(PyErr_Occurred()){Py_DECREF(zero);goto fail;}else old=zero;
        result=contribution(e,old,value,i);Py_DECREF(old);if(!result)goto fail;
        for(int k=0;k<3;k++){
            PyObject *score=PyList_GetItem(scores,k);
            if(!score)goto fail;
            Py_INCREF(score);
            PyObject *next=PyNumber_InPlaceAdd(score,PyTuple_GET_ITEM(result,k+1));
            Py_DECREF(score);
            if(!next)goto fail;
            if(PyList_SetItem(scores,k,next)<0)goto fail;
        }
        int truth=PyObject_IsTrue(PyTuple_GET_ITEM(result,0));
        if(truth<0)goto fail;
        if(truth){if(PyDict_SetItem(dst,index,PyTuple_GET_ITEM(result,0))<0)goto fail;}
        else{
            PyObject *present=PyDict_GetItemWithError(dst,index);
            if(present){if(PyDict_DelItem(dst,index)<0)goto fail;}
            else if(PyErr_Occurred())goto fail;
        }
        Py_CLEAR(result);Py_CLEAR(pair);
    }
    if(PyErr_Occurred())goto fail;
    Py_DECREF(iterator);s->busy=0;Py_RETURN_NONE;
fail:Py_XDECREF(result);Py_XDECREF(pair);Py_XDECREF(iterator);s->busy=0;return NULL;
}
static PyMethodDef cache_methods[]={{"event",(PyCFunction)cache_event,METH_O,"Fresh scalar context."},{"statistics",(PyCFunction)cache_statistics,METH_NOARGS,"Full counters."},{NULL,NULL,0,NULL}};
static PyMethodDef event_methods[]={{"apply",(PyCFunction)event_apply,METH_VARARGS,"Same coefficient loop and Python numeric operations."},{NULL,NULL,0,NULL}};
static PyTypeObject CacheType={PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="_fraction_native.Cache",.tp_basicsize=sizeof(Cache),.tp_flags=Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,
    .tp_new=cache_new,.tp_dealloc=(destructor)cache_dealloc,.tp_traverse=(traverseproc)cache_traverse,.tp_clear=(inquiry)cache_clear,.tp_methods=cache_methods};
static PyTypeObject EventType={PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="_fraction_native.Event",.tp_basicsize=sizeof(Event),.tp_flags=Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC|Py_TPFLAGS_HAVE_VECTORCALL,
    .tp_new=event_disabled,.tp_dealloc=(destructor)event_dealloc,.tp_traverse=(traverseproc)event_traverse,.tp_clear=(inquiry)event_clear,
    .tp_call=PyVectorcall_Call,.tp_vectorcall_offset=offsetof(Event,vectorcall),.tp_methods=event_methods};
static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_fraction_native","Bounded cache; exact Python arithmetic.",-1,capture_methods};
PyMODINIT_FUNC PyInit__fraction_native(void){
    if(PyType_Ready(&CacheType)<0||PyType_Ready(&EventType)<0)return NULL;
    PyObject *m=PyModule_Create(&module);if(!m)return NULL;
    if(PyModule_AddObjectRef(m,"Cache",(PyObject *)&CacheType)<0){Py_DECREF(m);return NULL;}
    return m;
}
