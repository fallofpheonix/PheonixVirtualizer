import pytest
from backend.app.core.normalizer import Normalizer
from backend.app.models.types import ParseResult, FileParseMetadata, GraphNode, NodeKind, NodeStatus, ImportSymbol

def test_resolve_path_external(project_root):
    norm = Normalizer(project_root)
    target, cands = norm._resolve_path(f"{project_root}/a.py", "os")
    assert target is None
    assert len(cands) > 0

def test_process_external_import(project_root):
    norm = Normalizer(project_root)
    pr = ParseResult(
        fileId="a.py", path="a.py", language="python", parsed=True,
        imports=[ImportSymbol(source="requests", imported=[])],
        exports=[], symbols=[],
        metadata=FileParseMetadata(parserVersion="1", durationMs=1, hash="h")
    )
    norm.process_parse_result(pr)
    graph = norm.get_graph()
    
    assert len(graph.nodes) == 1
    assert graph.nodes[0].id == "pkg:requests"
    assert len(graph.edges) == 1
    assert graph.edges[0].target == "pkg:requests"
    assert graph.edges[0].metadata["external"] is True
