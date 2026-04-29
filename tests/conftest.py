import sys
from pathlib import Path

# Add the nodes directory to sys.path so tests can import parser directly
sys.path.insert(0, str(Path(__file__).parent.parent / "nodes"))
