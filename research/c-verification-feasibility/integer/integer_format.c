/*
 * Exact integer sparse-row and canonical dyadic formatting feasibility source.
 * Derived from integer.py: Ali Romman with substantial OpenAI Codex assistance.
 * Original literal scalar and reverse-cut oracles remain in the authenticated
 * reference. New C implementation: OpenAI Codex assistance, 2026-10-27.
 * Apache-2.0; preserve the predecessor NOTICE and complete attribution chain.
 *
 * SOURCE-ONLY PROTOTYPE: not compiled, executed, qualified, or benchmarked by
 * its author. Uses public Python C API and arbitrary-size exact PyLong values.
 * No mutable process-global answer cache and no sharing with Fraction oracle.
 * Row functions return fresh objects and never mutate any supplied object.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static int exact_int(PyObject *value)
{
    if (!PyLong_CheckExact(value)) {
        PyErr_SetString(PyExc_TypeError, "exact built-in int required");
        return 0;
    }
    return 1;
}

static Py_ssize_t sequence_length(PyObject *value)
{
    if (PyList_CheckExact(value)) return PyList_GET_SIZE(value);
    if (PyTuple_CheckExact(value)) return PyTuple_GET_SIZE(value);
    PyErr_SetString(PyExc_TypeError, "exact built-in list or tuple required");
    return -1;
}

static PyObject *sequence_item(PyObject *value, Py_ssize_t index)
{
    return PyList_CheckExact(value) ? PyList_GET_ITEM(value, index)
                                  : PyTuple_GET_ITEM(value, index);
}

static int int_sequence(PyObject *value, Py_ssize_t length)
{
    Py_ssize_t size = sequence_length(value);
    if (size < 0) return 0;
    if (size != length) {
        PyErr_SetString(PyExc_ValueError, "integer sequence has required length");
        return 0;
    }
    for (Py_ssize_t i = 0; i < size; ++i)
        if (!exact_int(sequence_item(value, i))) return 0;
    return 1;
}

static int int_row(PyObject *row)
{
    Py_ssize_t pos = 0;
    PyObject *key, *value;
    if (!PyDict_CheckExact(row)) {
        PyErr_SetString(PyExc_TypeError, "exact built-in dict required");
        return 0;
    }
    while (PyDict_Next(row, &pos, &key, &value))
        if (!exact_int(key) || !exact_int(value)) return 0;
    return 1;
}

/* Positive power-of-two scale only; zero and negative scales cannot enter
 * the dyadic normalizer. All operations remain PyLong operations. */
static int dyadic_scale(PyObject *scale)
{
    PyObject *zero = NULL, *one = NULL, *less = NULL, *mask = NULL;
    int positive, nonzero, ok = 0;
    if (!exact_int(scale)) return 0;
    zero = PyLong_FromLong(0);
    one = PyLong_FromLong(1);
    if (!zero || !one) goto done;
    positive = PyObject_RichCompareBool(scale, zero, Py_GT);
    if (positive < 0) goto done;
    if (!positive) {
        PyErr_SetString(PyExc_ValueError, "positive dyadic scale required");
        goto done;
    }
    less = PyNumber_Subtract(scale, one);
    if (!less) goto done;
    mask = PyNumber_And(scale, less);
    if (!mask) goto done;
    nonzero = PyObject_IsTrue(mask);
    if (nonzero < 0) goto done;
    if (nonzero) {
        PyErr_SetString(PyExc_ValueError, "positive dyadic scale required");
        goto done;
    }
    ok = 1;
 done:
    Py_XDECREF(zero); Py_XDECREF(one); Py_XDECREF(less); Py_XDECREF(mask);
    return ok;
}

static PyObject *shift_denominator(PyObject *exponent, int *divide)
{
    PyObject *zero = NULL, *one = NULL, *result = NULL;
    int negative;
    if (!exact_int(exponent)) return NULL;
    zero = PyLong_FromLong(0);
    one = PyLong_FromLong(1);
    if (!zero || !one) goto done;
    negative = PyObject_RichCompareBool(exponent, zero, Py_LT);
    if (negative < 0) goto done;
    if (negative) {
        PyErr_SetString(PyExc_ValueError, "nonnegative dyadic exponent required");
        goto done;
    }
    *divide = PyObject_IsTrue(exponent);
    if (*divide < 0) goto done;
    result = PyNumber_Lshift(one, exponent);
 done:
    Py_XDECREF(zero); Py_XDECREF(one);
    return result;
}

static PyObject *multiply_exact(PyObject *value, PyObject *numerator,
                                PyObject *denominator, int divide)
{
    PyObject *product = PyNumber_Multiply(value, numerator), *pair, *result;
    int remainder;
    if (!product || !divide) return product;
    pair = PyNumber_Divmod(product, denominator);
    Py_DECREF(product);
    if (!pair) return NULL;
    remainder = PyObject_IsTrue(PyTuple_GET_ITEM(pair, 1));
    if (remainder < 0) { Py_DECREF(pair); return NULL; }
    if (remainder) {
        Py_DECREF(pair);
        PyErr_SetString(PyExc_ValueError, "exact dyadic division");
        return NULL;
    }
    result = Py_NewRef(PyTuple_GET_ITEM(pair, 0));
    Py_DECREF(pair);
    return result;
}

static int add_product(PyObject **score, PyObject *value, PyObject *weight)
{
    PyObject *product = weight ? PyNumber_Multiply(value, weight)
                               : Py_NewRef(value);
    PyObject *next;
    if (!product) return 0;
    next = PyNumber_Add(*score, product);
    Py_DECREF(product);
    if (!next) return 0;
    Py_SETREF(*score, next);
    return 1;
}

static PyObject *indexed_pair(PyObject *weights, PyObject *key)
{
    Py_ssize_t size = sequence_length(weights), index;
    PyObject *pair;
    if (size < 0) return NULL;
    index = PyLong_AsSsize_t(key);
    if (index == -1 && PyErr_Occurred()) return NULL;
    if (index < 0 || index >= size) {
        PyErr_SetString(PyExc_IndexError, "weight event index out of range");
        return NULL;
    }
    pair = sequence_item(weights, index);
    return int_sequence(pair, 2) ? pair : NULL;
}

static PyObject *row_add(PyObject *dst, PyObject *src, PyObject *numerator,
                         PyObject *exponent, PyObject *scores, PyObject *weights)
{
    PyObject *out = NULL, *den = NULL, *zero = NULL, *score_tuple = NULL;
    PyObject *s[3] = {NULL, NULL, NULL};
    PyObject *key, *value, *scaled = NULL, *next = NULL;
    PyObject *old_abs = NULL, *new_abs = NULL, *change = NULL, *result = NULL;
    Py_ssize_t pos = 0;
    int divide = 0, nonzero;
    if (!int_row(dst) || !int_row(src) || !exact_int(numerator)) goto done;
    if (scores) {
        if (!int_sequence(scores, 3) || sequence_length(weights) < 0) goto done;
        for (int c = 0; c < 3; ++c) s[c] = Py_NewRef(sequence_item(scores, c));
    }
    den = shift_denominator(exponent, &divide);
    zero = PyLong_FromLong(0);
    if (!den || !zero) goto done;
    out = PyDict_Copy(dst);
    if (!out) goto done;
    while (PyDict_Next(src, &pos, &key, &value)) {
        PyObject *old = PyDict_GetItemWithError(out, key);
        PyObject *pair = NULL;
        int existed = old != NULL;
        if (!old && PyErr_Occurred()) goto done;
        if (!old) old = zero;
        if (scores) {
            pair = indexed_pair(weights, key);
            if (!pair) goto done;
        }
        scaled = multiply_exact(value, numerator, den, divide);
        if (!scaled) goto done;
        next = PyNumber_Add(old, scaled);
        Py_CLEAR(scaled);
        if (!next) goto done;
        if (scores) {
            old_abs = PyNumber_Absolute(old);
            new_abs = PyNumber_Absolute(next);
            if (!old_abs || !new_abs) goto done;
            change = PyNumber_Subtract(new_abs, old_abs);
            Py_CLEAR(old_abs); Py_CLEAR(new_abs);
            if (!change) goto done;
            if (!add_product(&s[0], change, sequence_item(pair, 0)) ||
                !add_product(&s[1], change, sequence_item(pair, 1)) ||
                !add_product(&s[2], change, NULL)) goto done;
            Py_CLEAR(change);
        }
        nonzero = PyObject_IsTrue(next);
        if (nonzero < 0) goto done;
        if (nonzero) {
            if (PyDict_SetItem(out, key, next) < 0) goto done;
        } else if (existed && PyDict_DelItem(out, key) < 0) goto done;
        Py_CLEAR(next);
    }
    if (scores) {
        score_tuple = PyTuple_New(3);
        if (!score_tuple) goto done;
        for (int c = 0; c < 3; ++c) {
            PyTuple_SET_ITEM(score_tuple, c, s[c]); s[c] = NULL;
        }
        result = PyTuple_Pack(2, out, score_tuple);
    } else result = Py_NewRef(out);
 done:
    Py_XDECREF(out); Py_XDECREF(den); Py_XDECREF(zero);
    Py_XDECREF(score_tuple); Py_XDECREF(scaled); Py_XDECREF(next);
    Py_XDECREF(old_abs); Py_XDECREF(new_abs); Py_XDECREF(change);
    for (int c = 0; c < 3; ++c) Py_XDECREF(s[c]);
    return result;
}

static PyObject *add_row_method(PyObject *self, PyObject *args)
{
    PyObject *dst, *src, *numerator, *exponent;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOOO:add_row", &dst, &src, &numerator, &exponent)) return NULL;
    return row_add(dst, src, numerator, exponent, NULL, NULL);
}

static PyObject *error_row_method(PyObject *self, PyObject *args)
{
    PyObject *dst, *src, *numerator, *exponent, *scores, *weights;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOOOOO:error_row", &dst, &src, &numerator,
                         &exponent, &scores, &weights)) return NULL;
    return row_add(dst, src, numerator, exponent, scores, weights);
}

static PyObject *scale_row_method(PyObject *self, PyObject *args)
{
    PyObject *row, *numerator, *exponent, *den = NULL, *out = NULL, *result = NULL;
    PyObject *key, *value, *next = NULL;
    Py_ssize_t pos = 0;
    int divide = 0;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOO:scale_row", &row, &numerator, &exponent)) return NULL;
    if (!int_row(row) || !exact_int(numerator)) goto done;
    den = shift_denominator(exponent, &divide);
    out = PyDict_New();
    if (!den || !out) goto done;
    while (PyDict_Next(row, &pos, &key, &value)) {
        next = multiply_exact(value, numerator, den, divide);
        if (!next || PyDict_SetItem(out, key, next) < 0) goto done;
        Py_CLEAR(next);
    }
    result = Py_NewRef(out);
 done:
    Py_XDECREF(den); Py_XDECREF(out); Py_XDECREF(next);
    return result;
}

/* scale was checked once by the batch entry point. For nonzero signed v,
 * v & -v is its positive power-of-two divisor. Intersect with scale by min;
 * dividing by that factor gives the same canonical pair as Fraction(v,scale).
 * Exact integer decimal conversion retains CPython's configured digit guard. */
static PyObject *ratio_text(PyObject *value, PyObject *scale, int always_denominator)
{
    PyObject *negative = NULL, *low = NULL, *factor = NULL, *num = NULL;
    PyObject *den = NULL, *one = NULL, *result = NULL;
    int nonzero = PyObject_IsTrue(value), larger, unit;
    if (nonzero < 0) return NULL;
    if (!nonzero) return PyUnicode_FromString(always_denominator ? "0/1" : "0");
    negative = PyNumber_Negative(value);
    if (!negative) goto done;
    low = PyNumber_And(value, negative);
    if (!low) goto done;
    larger = PyObject_RichCompareBool(low, scale, Py_GT);
    if (larger < 0) goto done;
    factor = larger ? scale : low;
    num = PyNumber_FloorDivide(value, factor);
    den = PyNumber_FloorDivide(scale, factor);
    one = PyLong_FromLong(1);
    if (!num || !den || !one) goto done;
    unit = PyObject_RichCompareBool(den, one, Py_EQ);
    if (unit < 0) goto done;
    result = !always_denominator && unit ? PyObject_Str(num)
                                        : PyUnicode_FromFormat("%S/%S", num, den);
 done:
    Py_XDECREF(negative); Py_XDECREF(low); Py_XDECREF(num);
    Py_XDECREF(den); Py_XDECREF(one);
    return result;
}

static PyObject *event_text(PyObject *event, PyObject *value, PyObject *scale)
{
    PyObject *ratio = ratio_text(value, scale, 1), *result;
    if (!ratio) return NULL;
    result = PyUnicode_FromFormat("%S:%U;", event, ratio);
    Py_DECREF(ratio);
    return result;
}

static PyObject *coefficient_bytes_method(PyObject *self, PyObject *args)
{
    PyObject *row, *scale, *keys = NULL, *parts = NULL, *empty = NULL;
    PyObject *text = NULL, *result = NULL;
    Py_ssize_t count;
    (void)self;
    if (!PyArg_ParseTuple(args, "OO:coefficient_bytes", &row, &scale)) return NULL;
    if (!int_row(row) || !dyadic_scale(scale)) goto done;
    keys = PyDict_Keys(row);
    if (!keys || PyList_Sort(keys) < 0 || PyList_Reverse(keys) < 0) goto done;
    count = PyList_GET_SIZE(keys);
    parts = PyTuple_New(count);
    if (!parts) goto done;
    for (Py_ssize_t i = 0; i < count; ++i) {
        PyObject *key = PyList_GET_ITEM(keys, i);
        PyObject *value = PyDict_GetItemWithError(row, key);
        PyObject *part;
        if (!value) goto done;
        part = event_text(key, value, scale);
        if (!part) goto done;
        PyTuple_SET_ITEM(parts, i, part);
    }
    empty = PyUnicode_FromString("");
    if (!empty) goto done;
    text = PyUnicode_Join(empty, parts);
    if (!text) goto done;
    result = PyUnicode_AsUTF8String(text);
 done:
    Py_XDECREF(keys); Py_XDECREF(parts); Py_XDECREF(empty); Py_XDECREF(text);
    return result;
}

static PyObject *coefficient_item_bytes_method(PyObject *self, PyObject *args)
{
    PyObject *event, *value, *scale, *text, *result;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOO:coefficient_item_bytes", &event, &value, &scale)) return NULL;
    if (!exact_int(event) || !exact_int(value) || !dyadic_scale(scale)) return NULL;
    text = event_text(event, value, scale);
    if (!text) return NULL;
    result = PyUnicode_AsUTF8String(text);
    Py_DECREF(text);
    return result;
}

static PyObject *score_bytes_method(PyObject *self, PyObject *args)
{
    PyObject *event, *scores, *units, *parts = NULL, *comma = NULL;
    PyObject *joined = NULL, *text = NULL, *result = NULL;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOO:score_bytes", &event, &scores, &units)) return NULL;
    if (!exact_int(event) || !int_sequence(scores, 3) || !int_sequence(units, 3)) goto done;
    parts = PyTuple_New(3);
    if (!parts) goto done;
    for (int c = 0; c < 3; ++c) {
        PyObject *unit = sequence_item(units, c), *part;
        if (!dyadic_scale(unit)) goto done;
        part = ratio_text(sequence_item(scores, c), unit, 0);
        if (!part) goto done;
        PyTuple_SET_ITEM(parts, c, part);
    }
    comma = PyUnicode_FromString(",");
    if (!comma) goto done;
    joined = PyUnicode_Join(comma, parts);
    if (!joined) goto done;
    text = PyUnicode_FromFormat("%S:%U;", event, joined);
    if (!text) goto done;
    result = PyUnicode_AsUTF8String(text);
 done:
    Py_XDECREF(parts); Py_XDECREF(comma); Py_XDECREF(joined); Py_XDECREF(text);
    return result;
}

/* Each returned tuple is (column index, new three-score tuple, exact bytes).
 * Iteration order is the original column's dict insertion order. The caller
 * assigns scores[index] and updates hashes[index] in that order. Input score
 * triples may alias: no mutation occurs here or in any other exported API. */
static PyObject *reverse_updates_method(PyObject *self, PyObject *args)
{
    PyObject *column, *scores, *wa, *wc, *event, *scale;
    PyObject *out = NULL, *s[3] = {NULL, NULL, NULL}, *magnitude = NULL;
    PyObject *st = NULL, *text = NULL, *bytes = NULL, *item = NULL, *result = NULL;
    PyObject *key, *value;
    Py_ssize_t pos = 0, count, offset = 0;
    (void)self;
    if (!PyArg_ParseTuple(args, "OOOOOO:reverse_updates", &column, &scores,
                         &wa, &wc, &event, &scale)) return NULL;
    if (!int_row(column) || !exact_int(wa) || !exact_int(wc) ||
        !exact_int(event) || !dyadic_scale(scale)) goto done;
    count = sequence_length(scores);
    if (count < 0) goto done;
    out = PyList_New(PyDict_Size(column));
    if (!out) goto done;
    while (PyDict_Next(column, &pos, &key, &value)) {
        Py_ssize_t index = PyLong_AsSsize_t(key);
        PyObject *old;
        if (index == -1 && PyErr_Occurred()) goto done;
        if (index < 0 || index >= count) {
            PyErr_SetString(PyExc_IndexError, "reverse score index out of range");
            goto done;
        }
        old = sequence_item(scores, index);
        if (!int_sequence(old, 3)) goto done;
        for (int c = 0; c < 3; ++c) s[c] = Py_NewRef(sequence_item(old, c));
        magnitude = PyNumber_Absolute(value);
        if (!magnitude || !add_product(&s[0], magnitude, wa) ||
            !add_product(&s[1], magnitude, wc) || !add_product(&s[2], magnitude, NULL)) goto done;
        Py_CLEAR(magnitude);
        st = PyTuple_New(3);
        if (!st) goto done;
        for (int c = 0; c < 3; ++c) { PyTuple_SET_ITEM(st, c, s[c]); s[c] = NULL; }
        text = event_text(event, value, scale);
        if (!text) goto done;
        bytes = PyUnicode_AsUTF8String(text);
        Py_CLEAR(text);
        if (!bytes) goto done;
        item = PyTuple_Pack(3, key, st, bytes);
        Py_CLEAR(st); Py_CLEAR(bytes);
        if (!item) goto done;
        PyList_SET_ITEM(out, offset++, item); item = NULL;
    }
    result = Py_NewRef(out);
 done:
    Py_XDECREF(out); Py_XDECREF(magnitude); Py_XDECREF(st);
    Py_XDECREF(text); Py_XDECREF(bytes); Py_XDECREF(item);
    for (int c = 0; c < 3; ++c) Py_XDECREF(s[c]);
    return result;
}

static PyMethodDef methods[] = {
    {"add_row", add_row_method, METH_VARARGS, "Return dst + (n/2**k)*src as a fresh exact-int dict."},
    {"error_row", error_row_method, METH_VARARGS, "Return fresh (row, three-score tuple) after sparse signed update."},
    {"scale_row", scale_row_method, METH_VARARGS, "Return fresh exact scaled row; reject non-exact divisions."},
    {"coefficient_bytes", coefficient_bytes_method, METH_VARARGS, "Descending full row bytes: event:numerator/denominator;."},
    {"coefficient_item_bytes", coefficient_item_bytes_method, METH_VARARGS, "One exact coefficient chunk for an ordered reverse stream."},
    {"score_bytes", score_bytes_method, METH_VARARGS, "Three score values with Fraction string conventions."},
    {"reverse_updates", reverse_updates_method, METH_VARARGS, "Fresh sparse reverse score updates with exact signed coefficient bytes."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_integer_format",
    "Source-only exact integer and dyadic formatting feasibility prototype.",
    -1,
    methods,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit__integer_format(void)
{
    return PyModule_Create(&module);
}
