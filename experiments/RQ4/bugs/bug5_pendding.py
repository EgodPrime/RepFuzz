import numpy

args = [1.0471975666666666, 8388613, True, 4194309, "k", 2048, 8388632, 0, 0]
print("before call")
res = numpy.format_float_positional(*args)
print("after call")

"""
Segmentation fault

Thread 1 "python" received signal SIGSEGV, Segmentation fault.
__memset_avx2_erms () at ../sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S:151
151     ../sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S: No such file or directory.
(gdb) bt
#0  0x000000000053626b in _PyGCHead_NEXT (gc=0x2020202020202020) at /usr/local/src/conda/python-3.12.7/Include/internal/pycore_gc.h:60
#1  update_refs (containers=0x962308 <_PyRuntime+75912>, containers@entry=0x2020202020202020) at /usr/local/src/conda/python-3.12.7/Modules/gcmodule.c:425
#2  deduce_unreachable (base=base@entry=0x962308 <_PyRuntime+75912>, unreachable=unreachable@entry=0x7ffd3a31d8c0) at /usr/local/src/conda/python-3.12.7/Modules/gcmodule.c:1115
#3  0x0000000000535d2a in gc_collect_main (tstate=0x9bfb70 <_PyRuntime+458992>, generation=2, n_collected=0x7ffd3a31d9a0, n_uncollectable=0x7ffd3a31d998, nofail=0) at /usr/local/src/conda/python-3.12.7/Modules/gcmodule.c:1242
#4  0x00000000005e464c in gc_collect_with_callback (tstate=tstate@entry=0x9bfb70 <_PyRuntime+458992>, generation=generation@entry=2) at /usr/local/src/conda/python-3.12.7/Modules/gcmodule.c:1426
#5  0x000000000061cc88 in PyGC_Collect () at /usr/local/src/conda/python-3.12.7/Modules/gcmodule.c:2111
#6  0x0000000000607dcb in Py_FinalizeEx () at /usr/local/src/conda/python-3.12.7/Python/pylifecycle.c:1988
#7  0x0000000000615e47 in Py_RunMain () at /usr/local/src/conda/python-3.12.7/Modules/main.c:715
#8  0x00000000005cc5b9 in Py_BytesMain (argc=<optimized out>, argv=<optimized out>) at /usr/local/src/conda/python-3.12.7/Modules/main.c:767
#9  0x00007f4b0853dd90 in __libc_start_call_main (main=main@entry=0x5cc4f0 <main>, argc=argc@entry=2, argv=argv@entry=0x7ffd3a31dd18) at ../sysdeps/nptl/libc_start_call_main.h:58
#10 0x00007f4b0853de40 in __libc_start_main_impl (main=0x5cc4f0 <main>, argc=2, argv=0x7ffd3a31dd18, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7ffd3a31dd08) at ../csu/libc-start.c:392
#11 0x00000000005cc3e9 in _start ()
"""
