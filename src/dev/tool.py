from functools import update_wrapper


def my_decorator(func):
    def wrapper(*args,**kwargs):
        print("Before the function runs")
        result = func(*args, **kwargs)
        print("After the function runs")
        return result
    return wrapper

class Tool:

    def __init__(self,name):
        self.name = name

    def __call__(self,param):
        print(param)
        return param


if __name__ == '__main__':

    def get_started(start):
        print(start)
        return start
    
    def get_going(going):
        print(going)
        return(going)
    
    get_started("now")


    # this only create the function wrapper defined by get_started
    get_started = my_decorator(get_started)
    # here, get_started is overloaded with the new definition of the decorator

    # this call the function wrapper
    get_started("test from decorator")

    print("\n")

    """
    # this only create the function wrapper defined by get_started
    get_going_func = my_decorator(get_going)
    get_going_func("test going")

    # this is equivalent to get_started_2 = my_decorator(get_started_2)
    @my_decorator 
    def get_started_2(start):
        print(start)
        return start
    
    # this is equivalent to get_going_func = my_decorator(get_going)
    @my_decorator
    def get_going_2(going):
        print(going)
        return going

    get_started_2("test_start_2")
    get_going_2("test_going_2")

    """

    # playing with tool
    @my_decorator
    def get_tool(tool:Tool):
        print("from get_tool with decorator")
        return tool
    # the call of the function get_tool create a Tool instance

    # I can use the same @my_decorator to create function or class here... it does not really make sense
    # Therefore the decorator allows to create function or class from a function call.
    # the functions of class can be totally different

    # creating a tool
    my_tool = Tool("sql_tool") # my_tool is a Tool
    my_tool("toto") # using __call__ directly from Tool class instance

    my_tool_test = get_tool(my_tool) #my_tool_test is a Tool wrapped by the decorator
    # Therefore, it return the Tool and execute the rest of the code within the wrapper function
    my_tool_test("titi") # using __call__ from Tool class instance created by decorator


