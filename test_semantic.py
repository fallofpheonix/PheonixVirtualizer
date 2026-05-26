import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models.types import ParseRequest, ExportSymbol, ImportSymbol
from app.parsers.python_parser import PythonParser
from app.core.normalizer import Normalizer
from app.models.types import GraphNode, NodeKind, NodeStatus

def test_semantic_resolution():
    project_root = os.getcwd()
    normalizer = Normalizer(project_root)
    
    # 1. Mock file nodes
    file_b_path = "file_b.py"
    file_a_path = "file_a.py"
    
    normalizer.add_nodes([
        GraphNode(id=file_a_path, kind=NodeKind.FILE, label="file_a.py", path=file_a_path, status=NodeStatus.VERIFIED),
        GraphNode(id=file_b_path, kind=NodeKind.FILE, label="file_b.py", path=file_b_path, status=NodeStatus.VERIFIED)
    ])
    
    # 2. Parse result for file_b (exports 'login')
    result_b = PythonParser().parse(ParseRequest(
        fileId="file_b", path=file_b_path, language="python",
        content="def login(): pass", contentHash="h1", version=1, projectRoot="."
    ))
    # Ensure it found the export
    print(f"File B exports: {[e.name for e in result_b.exports]}")
    normalizer.process_parse_result(result_b)
    
    # 3. Parse result for file_a (imports 'login' from file_b) -> Should be VERIFIED
    result_a_good = PythonParser().parse(ParseRequest(
        fileId="file_a", path=file_a_path, language="python",
        content="from file_b import login", contentHash="h2", version=1, projectRoot="."
    ))
    normalizer.process_parse_result(result_a_good)
    
    # Check edges
    graph = normalizer.get_graph()
    edge_good = next((e for e in graph.edges if e.source == file_a_path and "login" in e.metadata.get("imported_symbols", [])), None)
    print(f"Edge (login): Status={edge_good.status if edge_good else 'NOT FOUND'}")
    
    # 4. Parse result for file_a (imports 'register' from file_b) -> Should be BROKEN
    result_a_bad = PythonParser().parse(ParseRequest(
        fileId="file_a", path=file_a_path, language="python",
        content="from file_b import register", contentHash="h3", version=1, projectRoot="."
    ))
    normalizer.process_parse_result(result_a_bad)
    
    # Check edges
    graph = normalizer.get_graph()
    edge_bad = next((e for e in graph.edges if e.source == file_a_path and "register" in e.metadata.get("imported_symbols", [])), None)
    print(f"Edge (register): Status={edge_bad.status if edge_bad else 'NOT FOUND'}")

if __name__ == "__main__":
    test_semantic_resolution()
