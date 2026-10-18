class Tool:
    """
    A Tool class that can wrap functions with a name and custom behavior.
    """
    
    def __init__(self, name, func=None):
        self.name = name
        self.func = func
    
    def __call__(self, *args, **kwargs):
        """
        Execute the wrapped function if it exists.
        Can be overridden in subclasses for custom behavior.
        """
        if self.func:
            return self.func(*args, **kwargs)
        else:
            print(f"Tool '{self.name}' called with args={args}, kwargs={kwargs}")
            return args[0] if args else None


# Optional: Decorator to create Tool instances
def tool(name):
    """Decorator to turn a function into a Tool instance."""
    def decorator(func):
        return Tool(name, func)
    return decorator


if __name__ == '__main__':
    
    # Example 1: Direct Tool instantiation
    def sql_func(query):
        return f"Executing: {query}"
     
    sql_tool = Tool("sql_tool", sql_func)
    print("Example 1:", sql_tool("SELECT * FROM users"))

    # Example 1 bis: Tool with decorator
    @tool('pyspark_tool')
    def pyspark_tool(transfo):
        return f"executing {transfo}"
    
    # pyspark_tool is defined as a function
    # @tool make this function pass as parameter to the decorator wrapper function
    # the decorator function return a Tool instance
    # Therefore, @tool de la function pyspark_tool renvoie un tool qui execute la function définie par pyspark_tool pour __call__
    # Donc, pyspark_tool, c'est une instance de la class Tool, avec la function pyspark_tool comme function __call__
    # pyspark_tool == instance de class, __call__ définie par def pyspark tool
    # c'est très tordu
    
    # Example 2: Using decorator
    @tool("math_tool")
    def add(a, b):
        return a + b
    
    print("Example 2:", add(5, 3))
    
    # Example 3: Tool without function (default behavior)
    empty_tool = Tool("empty_tool")
    print("Example 3:", empty_tool("test_data"))
