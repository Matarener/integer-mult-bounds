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
