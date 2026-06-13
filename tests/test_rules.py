import pytest
from backend.app.core.rules import RuleEngine
from backend.app.models.types import NormalizedGraph, GraphNode, GraphEdge, NodeKind, NodeStatus, PheonixConfig

def test_cycle_detection():
    engine = RuleEngine(PheonixConfig())
    graph = NormalizedGraph(
        nodes=[
            GraphNode(id="a", kind=NodeKind.FILE, label="a", status=NodeStatus.VERIFIED),
            GraphNode(id="b", kind=NodeKind.FILE, label="b", status=NodeStatus.VERIFIED),
        ],
        edges=[
            GraphEdge(id="e1", source="a", target="b", relationType="IMPORTS", status=NodeStatus.VERIFIED),
            GraphEdge(id="e2", source="b", target="a", relationType="IMPORTS", status=NodeStatus.VERIFIED),
        ]
    )
    violations = engine.evaluate(graph)
    
    assert len(violations) == 1
    violation = violations[0]
    assert violation.ruleId == "CIRCULAR_DEP"
    assert "e1" in violation.edgeIds or "e2" in violation.edgeIds
    
    # Ensure graph edges are updated
    assert graph.edges[0].is_cycle is True
    assert graph.edges[1].is_cycle is True
