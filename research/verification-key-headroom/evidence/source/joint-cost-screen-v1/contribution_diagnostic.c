static PyObject *contribution(Event *e, PyObject *old, PyObject *v, Py_ssize_t i) {
    Cache *s=e->cache;
    JointTimer timer=joint_start(JOINT_LOOKUP);
    if (i<0 || i>=PyTuple_GET_SIZE(s->tokens)) { PyErr_SetString(PyExc_IndexError,"native site index");joint_stop(&timer,JOINT_ERROR);return NULL; }
    if (!Py_IS_TYPE(old,(PyTypeObject *)s->fraction)||!Py_IS_TYPE(v,(PyTypeObject *)s->fraction)) { PyErr_SetString(PyExc_TypeError,"exact Fraction coefficients");joint_stop(&timer,JOINT_ERROR);return NULL; }
    PyObject *parts[4]={NULL,NULL,NULL,NULL};
    for (int k=0;k<4;k++) {
        parts[k]=member(k%2?s->den:s->num,k<2?old:v,s->fraction);
        if (!parts[k] || !PyLong_CheckExact(parts[k])) {
            for(int j=0;j<4;j++)Py_XDECREF(parts[j]);
            if(!PyErr_Occurred())PyErr_SetString(PyExc_TypeError,"integer Fraction slots");
            joint_stop(&timer,JOINT_ERROR);return NULL;
        }
    }
    PyObject *key=PyTuple_New(7);
    if(!key){for(int j=0;j<4;j++)Py_DECREF(parts[j]);joint_stop(&timer,JOINT_ERROR);return NULL;}
    PyTuple_SET_ITEM(key,0,parts[0]);PyTuple_SET_ITEM(key,1,parts[1]);
    PyTuple_SET_ITEM(key,2,Py_NewRef(e->qn));PyTuple_SET_ITEM(key,3,Py_NewRef(e->qd));
    PyTuple_SET_ITEM(key,4,parts[2]);PyTuple_SET_ITEM(key,5,parts[3]);PyTuple_SET_ITEM(key,6,Py_NewRef(PyTuple_GET_ITEM(s->tokens,i)));
    if(s->calls==PY_SSIZE_T_MAX){Py_DECREF(key);PyErr_SetString(PyExc_OverflowError,"native counter overflow");joint_stop(&timer,JOINT_ERROR);return NULL;}
    s->calls++;
    PyObject *result=PyDict_GetItemWithError(s->dict,key);
    if(result){s->hits++;Py_INCREF(result);Py_DECREF(key);joint_stop(&timer,JOINT_HIT);return result;}
    if(PyErr_Occurred()){Py_DECREF(key);joint_stop(&timer,JOINT_ERROR);return NULL;}
    s->misses++;
    PyObject *pair=PyTuple_GET_ITEM(s->weights,i);
    PyObject *argv[5]={old,e->q,v,PyTuple_GET_ITEM(pair,0),PyTuple_GET_ITEM(pair,1)};
    joint_stop(&timer,JOINT_MISS);
    joint_inc(&joint_callback_depth);
    result=PyObject_Vectorcall(s->compute,argv,5,NULL);
    if (!joint_callback_depth) joint_inc(&joint_protocol_errors);else joint_callback_depth--;
    timer=joint_start(JOINT_AFTER);
    if(!result){Py_DECREF(key);joint_stop(&timer,JOINT_ERROR);return NULL;}
    if(!PyTuple_CheckExact(result)||PyTuple_GET_SIZE(result)!=4){Py_DECREF(result);Py_DECREF(key);PyErr_SetString(PyExc_TypeError,"four exact contributions");joint_stop(&timer,JOINT_ERROR);return NULL;}
    for(int k=0;k<4;k++)if(!Py_IS_TYPE(PyTuple_GET_ITEM(result,k),(PyTypeObject *)s->fraction)){Py_DECREF(result);Py_DECREF(key);PyErr_SetString(PyExc_TypeError,"Fraction contributions");joint_stop(&timer,JOINT_ERROR);return NULL;}
    if(s->used==s->capacity){
        PyObject *oldkey=s->ring[s->head];
        if(PyDict_DelItem(s->dict,oldkey)<0){Py_DECREF(result);Py_DECREF(key);joint_stop(&timer,JOINT_ERROR);return NULL;}
        Py_CLEAR(s->ring[s->head]);s->used--;s->evictions++;
    }
    if(PyDict_SetItem(s->dict,key,result)<0){Py_DECREF(result);Py_DECREF(key);joint_stop(&timer,JOINT_ERROR);return NULL;}
    s->ring[s->head]=key;s->head=(s->head+1)%s->capacity;s->used++;
    joint_stop(&timer,JOINT_INSERTED);
    return result;
}
