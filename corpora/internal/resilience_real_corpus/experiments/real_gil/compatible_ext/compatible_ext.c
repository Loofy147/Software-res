#define PY_SSIZE_T_CLEAN
#include <Python.h>

static int compatible_exec(PyObject *module) {
    (void)module;
    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, compatible_exec},
#if defined(Py_GIL_DISABLED)
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "compatible_ext",
    "Intentional free-threading-compatible extension fixture.",
    0,
    NULL,
    slots,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC PyInit_compatible_ext(void) {
    return PyModuleDef_Init(&moduledef);
}
