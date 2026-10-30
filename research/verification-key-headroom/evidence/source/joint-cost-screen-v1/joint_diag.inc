/* Diagnostic only: no Python numeric operation, original cache counter or
 * error state is changed. CLOCK_PROCESS_CPUTIME_ID is current-process CPU. */
typedef struct {
    unsigned long long entries, closed, timed, excluded_callback;
    unsigned long long hits, misses, inserted, errors;
    double wall, cpu;
} JointPhase;
typedef struct {
    struct timespec wall, cpu;
    int valid;
} JointClock;
typedef struct {
    JointClock start;
    int phase, eligible;
} JointTimer;
static JointPhase joint_phases[2];
static unsigned long long joint_key_depth, joint_integer_depth, joint_callback_depth;
static unsigned long long joint_clock_failures, joint_protocol_errors;
static unsigned long long joint_nested_intervals, joint_integer_overlaps;
static unsigned long long joint_integer_enters, joint_integer_leaves;
enum { JOINT_LOOKUP=0, JOINT_AFTER=1 };
enum { JOINT_HIT=0, JOINT_MISS=1, JOINT_INSERTED=2, JOINT_ERROR=3 };
static void joint_inc(unsigned long long *value) {
    if (*value==ULLONG_MAX) {
        if (joint_protocol_errors<ULLONG_MAX) joint_protocol_errors++;
    } else (*value)++;
}
static JointClock joint_clock(void) {
    JointClock stamp={0};
    int prior_errno=errno;
    int wall_ok=clock_gettime(CLOCK_MONOTONIC,&stamp.wall);
    int cpu_ok=clock_gettime(CLOCK_PROCESS_CPUTIME_ID,&stamp.cpu);
    stamp.valid=wall_ok==0 && cpu_ok==0;
    errno=prior_errno;
    return stamp;
}
static double joint_delta(struct timespec end, struct timespec start) {
    return (double)(end.tv_sec-start.tv_sec)+(double)(end.tv_nsec-start.tv_nsec)/1000000000.0;
}
static JointTimer joint_start(int phase) {
    JointTimer timer={0};
    timer.phase=phase;
    timer.eligible=joint_callback_depth==0;
    timer.start.valid=0;
    joint_inc(&joint_phases[phase].entries);
    if (!timer.eligible) {
        joint_inc(&joint_phases[phase].excluded_callback);
        return timer;
    }
    if (joint_key_depth) joint_inc(&joint_nested_intervals);
    if (joint_integer_depth) joint_inc(&joint_integer_overlaps);
    joint_inc(&joint_key_depth);
    joint_inc(&joint_phases[phase].timed);
    timer.start=joint_clock();
    if (!timer.start.valid) joint_inc(&joint_clock_failures);
    return timer;
}
static void joint_stop(JointTimer *timer, int outcome) {
    JointPhase *phase=&joint_phases[timer->phase];
    if (timer->eligible) {
        JointClock end=joint_clock();
        if (!end.valid) joint_inc(&joint_clock_failures);
        if (end.valid && timer->start.valid) {
            double wall=joint_delta(end.wall,timer->start.wall);
            double cpu=joint_delta(end.cpu,timer->start.cpu);
            if (wall<0 || cpu<0) joint_inc(&joint_protocol_errors);
            else { phase->wall+=wall;phase->cpu+=cpu; }
        }
        if (!joint_key_depth) joint_inc(&joint_protocol_errors);
        else joint_key_depth--;
    }
    joint_inc(&phase->closed);
    if (outcome==JOINT_HIT) joint_inc(&phase->hits);
    else if (outcome==JOINT_MISS) joint_inc(&phase->misses);
    else if (outcome==JOINT_INSERTED) joint_inc(&phase->inserted);
    else joint_inc(&phase->errors);
}
static PyObject *joint_integer_enter(PyObject *self, PyObject *unused) {
    (void)self;(void)unused;
    if (joint_key_depth) joint_inc(&joint_integer_overlaps);
    joint_inc(&joint_integer_enters);joint_inc(&joint_integer_depth);
    Py_RETURN_NONE;
}
static PyObject *joint_integer_leave(PyObject *self, PyObject *unused) {
    (void)self;(void)unused;
    joint_inc(&joint_integer_leaves);
    if (!joint_integer_depth) joint_inc(&joint_protocol_errors);
    else joint_integer_depth--;
    Py_RETURN_NONE;
}
static PyObject *joint_phase_dict(JointPhase *p) {
    return Py_BuildValue("{s:K,s:K,s:K,s:K,s:K,s:K,s:K,s:K,s:d,s:d}",
        "entries",p->entries,"closed",p->closed,"timed",p->timed,
        "excluded_callback",p->excluded_callback,"hits",p->hits,
        "misses",p->misses,"inserted",p->inserted,"errors",p->errors,
        "wall_seconds",p->wall,"cpu_seconds",p->cpu);
}
static PyObject *joint_diagnostics(PyObject *self, PyObject *unused) {
    (void)self;(void)unused;
    PyObject *lookup=joint_phase_dict(&joint_phases[JOINT_LOOKUP]);
    PyObject *after=joint_phase_dict(&joint_phases[JOINT_AFTER]);
    if (!lookup || !after) {Py_XDECREF(lookup);Py_XDECREF(after);return NULL;}
    PyObject *result=Py_BuildValue("{s:O,s:O,s:K,s:K,s:K,s:K,s:K,s:K,s:K,s:K,s:K}",
        "lookup",lookup,"after_callback",after,
        "key_depth",joint_key_depth,"integer_depth",joint_integer_depth,
        "callback_depth",joint_callback_depth,"clock_failures",joint_clock_failures,
        "protocol_errors",joint_protocol_errors,"nested_key_intervals",joint_nested_intervals,
        "integer_overlap_intervals",joint_integer_overlaps,
        "integer_enters",joint_integer_enters,"integer_leaves",joint_integer_leaves);
    Py_DECREF(lookup);Py_DECREF(after);return result;
}
static PyObject *joint_clock_calibration(PyObject *self, PyObject *unused) {
    (void)self;(void)unused;
    unsigned long long failures=0;
    JointClock start=joint_clock();
    for (int i=0;i<512;i++) {
        JointClock a=joint_clock(),b=joint_clock();
        if (!a.valid || !b.valid) failures++;
    }
    JointClock end=joint_clock();
    if (!start.valid || !end.valid || failures) {
        PyErr_SetString(PyExc_RuntimeError,"joint diagnostic calibration clock failure");return NULL;
    }
    return Py_BuildValue("{s:i,s:i,s:d,s:d,s:O}",
        "empty_intervals",512,"clock_gettime_calls_per_interval",4,
        "wall_seconds",joint_delta(end.wall,start.wall),
        "cpu_seconds",joint_delta(end.cpu,start.cpu),
        "subtracted_from_envelope",Py_False);
}
static PyMethodDef joint_module_methods[]={
    {"_joint_integer_enter",joint_integer_enter,METH_NOARGS,"Diagnostic activity marker only."},
    {"_joint_integer_leave",joint_integer_leave,METH_NOARGS,"Diagnostic activity marker only."},
    {"_joint_diagnostics",joint_diagnostics,METH_NOARGS,"Separate diagnostics; existing cache statistics unchanged."},
    {"_joint_clock_calibration",joint_clock_calibration,METH_NOARGS,"Record clock overhead; never subtract it."},
    {NULL,NULL,0,NULL}
};
