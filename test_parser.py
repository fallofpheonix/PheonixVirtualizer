import sys
import os

# Add the backend directory to sys.path to allow imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models.types import ParseRequest
from app.parsers.python_parser import PythonParser

def test_python_parser():
    content = """
import os
from datetime import datetime
import numpy as np

class MyClass:
    def __init__(self):
        pass

def my_function():
    print("Hello")
"""
    request = ParseRequest(
        fileId="test_file",
        path="test.py",
        language="python",
        content=content,
        contentHash="hash",
        version=1,
        projectRoot="."
    )
    
    parser = PythonParser()
    result = parser.parse(request)
    
    print(f"Parsed {result.path} successfully: {result.parsed}")
    print(f"Imports found: {[i.source for i in result.imports]}")
    print(f"Exports found: {[e.name for e in result.exports]}")
    print(f"Symbols found: {[s.name for s in result.symbols]}")

if __name__ == "__main__":
    test_python_parser()
