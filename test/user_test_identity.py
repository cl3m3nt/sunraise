import sys
from pathlib import Path

# Add the project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.user import User

if __name__ == "__main__":

    u = User("clement","user")
    print(u.identity) 