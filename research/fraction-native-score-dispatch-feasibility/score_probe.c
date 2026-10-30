/* Bounded dispatch feasibility only. Original Fraction arithmetic retained.
 * Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0. */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
static int packet(PyObject *scores,PyObject *triples,PyObject *groups,PyObject *fraction,Py_ssize_t *count){
    if(!PyList_CheckExact(scores)||PyList_GET_SIZE(scores)!=3||!PyTuple_CheckExact(triples)||PyTuple_GET_SIZE(triples)!=16||!PyLong_CheckExact(groups)||!PyType_Check(fraction)){
        PyErr_SetString(PyExc_TypeError,"three scores, sixteen triples, integer groups and class");return -1;
    }
    *count=PyLong_AsSsize_t(groups);
    if(PyErr_Occurred())return -1;
    if(*count<0||*count>32768){PyErr_SetString(PyExc_ValueError,"groups 0..32768");return -1;}
    for(int i=0;i<16;i++){
        PyObject *row=PyTuple_GET_ITEM(triples,i);
        if(!PyTuple_CheckExact(row)||PyTuple_GET_SIZE(row)!=4){PyErr_SetString(PyExc_TypeError,"contribution-shaped triple");return -1;}
    }
    return 0;
}
static PyObject *generic(PyObject *module,PyObject *args){
    (void)module;PyObject *scores,*triples,*groups,*fraction;Py_ssize_t count;
    if(!PyArg_UnpackTuple(args,"generic",4,4,&scores,&triples,&groups,&fraction))return NULL;
    if(packet(scores,triples,groups,fraction,&count)<0)return NULL;
    for(Py_ssize_t group=0;group<count;group++){
        PyObject *result=PyTuple_GET_ITEM(triples,group%16);
        for(int k=0;k<3;k++){
            PyObject *score=PyList_GetItem(scores,k);
            if(!score)goto fail;
            Py_INCREF(score);
            PyObject *next=PyNumber_InPlaceAdd(score,PyTuple_GET_ITEM(result,k+1));
            Py_DECREF(score);
            if(!next)goto fail;
            if(PyList_SetItem(scores,k,next)<0)goto fail;
        }
    }
    return Py_BuildValue("(nn)",(Py_ssize_t)0,3*count);
fail:return NULL;
}
static PyObject *direct(PyObject *module,PyObject *args){
    (void)module;PyObject *scores,*triples,*groups,*fraction,*kernel;Py_ssize_t count;
    if(!PyArg_UnpackTuple(args,"direct",5,5,&scores,&triples,&groups,&fraction,&kernel))return NULL;
    if(!PyFunction_Check(kernel)){PyErr_SetString(PyExc_TypeError,"exact Python kernel packet");return NULL;}
    Py_ssize_t direct_count=0,fallback_count=0;
    if(packet(scores,triples,groups,fraction,&count)<0)return NULL;
    for(Py_ssize_t group=0;group<count;group++){
        PyObject *result=PyTuple_GET_ITEM(triples,group%16);
        for(int k=0;k<3;k++){
            PyObject *score=PyList_GetItem(scores,k);
            if(!score)goto fail;
            Py_INCREF(score);
            PyObject *increment=PyTuple_GET_ITEM(result,k+1),*next;
            if(Py_IS_TYPE(score,(PyTypeObject *)fraction)&&Py_IS_TYPE(increment,(PyTypeObject *)fraction)){
                PyObject *argv[2]={score,increment};next=PyObject_Vectorcall(kernel,argv,2,NULL);direct_count++;
            }else{next=PyNumber_InPlaceAdd(score,increment);fallback_count++;}
            Py_DECREF(score);
            if(!next)goto fail;
            if(PyList_SetItem(scores,k,next)<0)goto fail;
        }
    }
    return Py_BuildValue("(nn)",direct_count,fallback_count);
fail:return NULL;
}
static PyMethodDef methods[]={{"generic",generic,METH_VARARGS,"Exact parent generic score loop."},{"direct",direct,METH_VARARGS,"Guarded existing-kernel score loop."},{NULL,NULL,0,NULL}};
static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_score_probe","Bounded source-bound score dispatch probe.",-1,methods};
PyMODINIT_FUNC PyInit__score_probe(void){return PyModule_Create(&module);}
