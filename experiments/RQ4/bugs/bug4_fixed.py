import numpy as np

a = ["a1b2", "1b2a", "b2a1", "2a1b", "a1b2a1b2a1b2a1b2a1b2"]
b1 = int(1e3)
b2 = int(1e6)
b3 = int(1e9)  # this is close to b5
b4 = int(1e12)
b5 = 1073750025  # this trigger Segmentation Fault
fillchar = "*"

np.strings.center(a, b1, fillchar)
print(f"A normal width of {b1} is ok")

np.strings.center(a, b2, fillchar)
print(f"A bigger width of {b2} is ok")

try:
    np.strings.center(a, b3, fillchar)
except Exception as e:
    print(f"A width of {b3} is not ok: {e}")

try:
    np.strings.center(a, b4, fillchar)
except Exception as e:
    print(f"A width of {b4} is not ok: {e}")

print(f"A special width of {b5} leads to Segmentation Fault")
try:
    np.strings.center(a, b5, fillchar)
except Exception as e:
    print("cannot reach")
