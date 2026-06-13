from typing import List
from app.core.plugin_loader import BaseRule
from app.models.types import NormalizedGraph, Violation, ViolationSeverity

class GodObjectRule(BaseRule):
    def evaluate(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        out_degree = {}
        for edge in graph.edges:
            out_degree[edge.source] = out_degree.get(edge.source, 0) + 1
            
        for node_id, degree in out_degree.items():
            if degree >= 20:
                violations.append(Violation(
                    id=f"god-object-{node_id}",
                    ruleId="GOD_OBJECT",
                    severity=ViolationSeverity.high,
                    message=f"God Object detected: Node {node_id} has {degree} outgoing dependencies (Threshold: 20).",
                    sourceNodeIds=[node_id],
                    edgeIds=[],
                    status="active"
                ))
        return violations
