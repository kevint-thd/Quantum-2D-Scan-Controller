import sys
import os

# Add the parent directory (project root) to sys.path so tests can find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

