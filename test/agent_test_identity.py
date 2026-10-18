import sys
from pathlib import Path

# Add the project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agent_old import Agent

if __name__ == "__main__":

    a = Agent("test_agent","model","api_key",0.5,"system")
    
    print(a.identity)