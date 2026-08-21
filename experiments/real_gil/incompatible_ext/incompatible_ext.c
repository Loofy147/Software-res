#define PY_SSIZE_T_CLEAN
#include <Python.h>

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "incompatible_ext",
    "Intentional free-threading-incompatible extension fixture.",
    0,
    NULL,
};

PyMODINIT_FUNC PyInit_incompatible_ext(void) {
    /* Deliberately omit Py_mod_gil / Py_MOD_GIL_NOT_USED.
       On free-threaded CPython, import should therefore default to GIL-used. */
    return PyModule_Create(&moduledef);
}
