import networkx as nx
from typing import List, Dict
from ..models.types import (
    NormalizedGraph, GraphEdge, NodeStatus, 
    RelationType, ViolationSeverity, Violation
)

class RuleEngine:
    def __init__(self):
        pass

    def evaluate(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        
        # 1. Circular Dependency Detection
        violations.extend(self._check_circular_dependencies(graph))
        
        # 2. Broken Import Detection (already partially handled by Normalizer, but can be consolidated here)
        
        return violations

    def _check_circular_dependencies(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        
        # Build a temporary networkx graph for cycle detection
        G = nx.DiGraph()
        for node in graph.nodes:
            G.add_node(node.id)
        for edge in graph.edges:
            G.add_edge(edge.source, edge.target)

        cycles = list(nx.simple_cycles(G))
        for i, cycle in enumerate(cycles):
            # A cycle is a circular dependency
            message = f"Circular dependency detected: {' -> '.join(cycle)} -> {cycle[0]}"
            violations.append(Violation(
                id=f"circular-{i}",
                ruleId="CIRCULAR_DEP",
                severity=ViolationSeverity.medium,
                message=message,
                sourceNodeIds=cycle,
                edgeIds=[], # Could be populated by finding the edges in G
                status="active",
                metadata={"cycle": cycle}
            ))
        
        return violations
