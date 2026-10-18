import sys
from pathlib import Path

# Add the project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.tool import Tool

if __name__ == "__main__":

    genomic_query = "SELECT * FROM genomic.bronze.sample_data"

    # this does create the sql_tool
    @Tool('sql_tool')
    def genomic_tool(query):
        print("--- creating sql_tool")
        return query
        
    # this does create the iterate_tool
    @Tool('iterate_tool')
    def iterating_tool(n):
        print("--- calling iterate_tool")
        for i in range(0,n):
            print(i)    
    # this does create the sum_tool
    @Tool('sum_tool')
    def sum_tool(a,b):
       # print("--- calling sum_tool")
        return a+b
    
    # call the genomic tool
    genomic_tool_instance = genomic_tool
    print(genomic_tool_instance.name)
    print(genomic_tool_instance.__repr__())
    print(genomic_tool_instance.__dict__)
    #print(genomic_tool_instance(genomic_query))

    # call the iterate tool
    iterating_tool_instance = iterating_tool # this is a BoundTool class
    print(iterating_tool_instance.name)
    #iterating_tool_instance.execute(5)
    #print(iterating_tool_instance.name)

    # call the sum tool
    sum_tool_instance = sum_tool(1, 10)
    #print(sum_tool_instance.name)
    #sum_tool_instance.execute(1, 10)
   # print(f"Sum result: {sum_tool_instance.result}")
