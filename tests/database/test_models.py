from repfuzz.database.models import Argument, API


def test_to_dict_1():
    # Create an instance of Argument
    arg = Argument(name="test_arg", type="int", example_value_list=[])
    # Convert the Argument instance to a dictionary
    arg_dict = arg.to_dict()
    # Check if the dictionary contains the correct keys and values
    assert arg_dict["name"] == "test_arg"
    assert arg_dict["type"] == "int"
    assert arg_dict["example_value_list"] == []


def test_to_dict_2():
    arg1 = Argument(name="arg1", type="str", example_value_list=["value1", "value2"])
    arg2 = Argument(name="arg2", type="int", example_value_list=[1, 2, 3])
    api = API(
        full_name="test_api",
        type="function",
        doc="This is a test API",
        num_normal_arg=1,
        num_kwonly_arg=1,
        normal_arg_list=[arg1],
        kwonly_arg_list=[arg2],
    )
    arg_dict = api.to_dict()
    print(arg_dict)
    assert arg_dict["normal_arg_list"][0]["example_value_list"] == ["value1", "value2"]
