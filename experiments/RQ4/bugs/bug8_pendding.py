import scipy.cluster.hierarchy

arr = [
    [0.0, 1.0, 1.0, 2.0],
    [2.0, 12.0, 1.0, 3.0],
    [3.0, 4.0, 1.0, 2.0],
    [5.0, 14.0, 1.0, 3.0],
    [6.0, 7.0, 1.0, 2.0],
    [8.0, 16.0, 1.0, 3.0],
    [9.0, 10.0, 1.0, 2.0],
    [11.0, 18.0, 1.0, 3.0],
    [13.0, 15.0, 2.0, 6.0],
    [17.0, 20.0, 2.0, 32.26562500000164],
    [19.0, 21.0, 2.0, 12.0],
]
scipy.cluster.hierarchy.cophenet(arr)

"""
Thread 1 "python" received signal SIGSEGV, Segmentation fault.
0x00007f494765f019 in __pyx_pw_5scipy_7cluster_10_hierarchy_13cophenetic_distances () from /root/miniconda3/envs/py313/lib/python3.13/site-packages/scipy/cluster/_hierarchy.cpython-313-x86_64-linux-gnu.so
(gdb) bt
#0  0x00007f494765f019 in __pyx_pw_5scipy_7cluster_10_hierarchy_13cophenetic_distances ()
   from /root/miniconda3/envs/py313/lib/python3.13/site-packages/scipy/cluster/_hierarchy.cpython-313-x86_64-linux-gnu.so
#1  0x00000000005385d1 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=9223372036854775811, args=0x7f4a8ef1a188, callable=0x7f4947721e50, 
    tstate=0x8ebc90 <_PyRuntime+283024>) at /usr/local/src/conda/python-3.13.1/Include/internal/pycore_call.h:168
#2  PyObject_Vectorcall (callable=0x7f4947721e50, args=0x7f4a8ef1a188, nargsf=9223372036854775811, kwnames=0x0) at /usr/local/src/conda/python-3.13.1/Objects/call.c:327
#3  0x000000000054a97d in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>, throwflag=<optimized out>)
    at /usr/local/src/conda/python-3.13.1/Python/generated_cases.c.h:813
#4  0x0000000000608dce in PyEval_EvalCode (co=<optimized out>, globals=0x7f4a8e963bc0, locals=<optimized out>) at /usr/local/src/conda/python-3.13.1/Python/ceval.c:601
#5  0x000000000062f62d in run_eval_code_obj (tstate=0x8ebc90 <_PyRuntime+283024>, co=0x7f4a8eb4a2b0, globals=0x7f4a8e963bc0, locals=0x7f4a8e963bc0)
    at /usr/local/src/conda/python-3.13.1/Python/pythonrun.c:1337
#6  0x000000000062a3cd in run_mod (mod=<optimized out>, filename=<optimized out>, globals=0x7f4a8e963bc0, locals=0x7f4a8e963bc0, flags=<optimized out>, 
    arena=<optimized out>, interactive_src=0x0, generate_new_source=0) at /usr/local/src/conda/python-3.13.1/Python/pythonrun.c:1422
#7  0x00000000006499d0 in pyrun_file (fp=0x139d2e0, filename=0x7f4a8e9d4580, start=<optimized out>, globals=0x7f4a8e963bc0, locals=0x7f4a8e963bc0, closeit=1, 
    flags=0x7ffc11db36f8) at /usr/local/src/conda/python-3.13.1/Python/pythonrun.c:1255
#8  0x000000000064844b in _PyRun_SimpleFileObject (fp=0x139d2e0, filename=0x7f4a8e9d4580, closeit=1, flags=0x7ffc11db36f8)
    at /usr/local/src/conda/python-3.13.1/Python/pythonrun.c:490
#9  0x0000000000647fab in _PyRun_AnyFileObject (fp=0x139d2e0, filename=0x7f4a8e9d4580, closeit=1, flags=0x7ffc11db36f8)
    at /usr/local/src/conda/python-3.13.1/Python/pythonrun.c:77
#10 0x0000000000641247 in pymain_run_file_obj (skip_source_first_line=0, filename=0x7f4a8e9d4580, program_name=0x7f4a8e9d45d0)
    at /usr/local/src/conda/python-3.13.1/Modules/main.c:409
#11 pymain_run_file (config=0x8be388 <_PyRuntime+96392>) at /usr/local/src/conda/python-3.13.1/Modules/main.c:428
--Type <RET> for more, q to quit, c to continue without paging--
#12 pymain_run_python (exitcode=0x7ffc11db36ec) at /usr/local/src/conda/python-3.13.1/Modules/main.c:696
#13 Py_RunMain () at /usr/local/src/conda/python-3.13.1/Modules/main.c:775
#14 0x00000000005f9169 in Py_BytesMain (argc=<optimized out>, argv=<optimized out>) at /usr/local/src/conda/python-3.13.1/Modules/main.c:829
#15 0x00007f4a8ec24d90 in __libc_start_call_main (main=main@entry=0x5f90a0 <main>, argc=argc@entry=2, argv=argv@entry=0x7ffc11db3948)
    at ../sysdeps/nptl/libc_start_call_main.h:58
#16 0x00007f4a8ec24e40 in __libc_start_main_impl (main=0x5f90a0 <main>, argc=2, argv=0x7ffc11db3948, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, 
    stack_end=0x7ffc11db3938) at ../csu/libc-start.c:392
#17 0x00000000005f84bd in _start ()
"""
