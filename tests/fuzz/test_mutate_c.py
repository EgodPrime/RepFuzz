from repfuzz.mutate import mutate_int, mutate_float, mutate_str, mutate_bytes


def test_mutate_int():
    data = 10
    new_data = mutate_int(data)
    for _ in range(20):
        new_data = mutate_int(new_data)
        print(new_data)
    assert new_data != data
    assert data != 1


def test_mutate_float():
    data = 3.14
    new_data = mutate_float(data)
    for _ in range(20):
        new_data = mutate_float(new_data)
        print(new_data)
    assert new_data != data
    assert data == 3.14
    print(f"data={data}")


def test_mutate_str():
    data = "Hello, World!"
    new_data = mutate_str(data)
    for _ in range(20):
        new_data = mutate_str(new_data)
        print(new_data)
    assert new_data != data
    assert data == "Hello, World!"
    print(f"data={data}")


def test_mutate_bytes():
    data = b"Hello, World!"
    new_data = mutate_bytes(data)
    for _ in range(20):
        new_data = mutate_bytes(new_data)
        print(new_data)
    print(f"data={data}")
    assert new_data != data
    assert data == b"Hello, World!"
