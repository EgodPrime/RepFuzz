from repfuzz.fuzz.fuzz_api import fuzz_api


def test_fuzz_api():
    def x(a, b, c):
        return a + str(b) + str(c)

    fuzz_api(x, ["x", 1, (1, 2)])
