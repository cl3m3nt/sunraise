from tool import Tool,tool

#------------------------ START TOOL PLAYGROUND ------------------------
# Example 1: Direct Tool instantiation
def sql_func(query):
    return f"Executing: {query}"

sql_Tool = Tool("sql_tool", sql_func)
sql_query = "SELECT * FROM users"
sql_result = sql_Tool(sql_query)
#print(sql_result)

# Example 2: Decorator Tool instantiation

@tool("pyspark_tool")
def pyspark_func(query):
    return f"Executing: {query}"

# this create a instance named with pyspark_func, the specific __call__ function
pyspark_Tool = pyspark_func
pyspark_query = 'spark.sql("""SELECT * FROM catalog.bronze.table""")'

pyspark_result = pyspark_Tool(pyspark_query)
#print(pyspark_result)

pyspark_result_2 = pyspark_func(pyspark_query)
#print(pyspark_result_2)
#------------------------ END TOOL PLAYGROUND ------------------------