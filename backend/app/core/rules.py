import networkx as nx
import re
from typing import List, Dict
from ..models.types import (
    NormalizedGraph, GraphEdge, NodeStatus, 
    RelationType, ViolationSeverity, Violation, PheonixConfig
)

class RuleEngine:
    def __init__(self, config: PheonixConfig = PheonixConfig()):
        self.config = config

    def evaluate(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        
        # 1. Circular Dependency Detection
        violations.extend(self._check_circular_dependencies(graph))
        
        # 2. Custom Architectural Rules
        violations.extend(self._check_custom_rules(graph))
        
        return violations

    def _check_custom_rules(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        for rule in self.config.rules:
            for edge in graph.edges:
                # Resolve nodes to check paths
                source_node = next((n for n in graph.nodes if n.id == edge.source), None)
                target_node = next((n for n in graph.nodes if n.id == edge.target), None)
                
                if not source_node or not target_node:
                    continue

                source_path = source_node.path or ""
                target_path = target_node.path or ""

                match_from = not rule.from_path or re.search(rule.from_path, source_path)
                match_to = not rule.to_path or re.search(rule.to_path, target_path)

                if match_from and match_to:
                    violations.append(Violation(
                        id=f"custom-{rule.id}-{edge.id}",
                        ruleId=rule.id,
                        severity=rule.severity,
                        message=rule.message,
                        sourceNodeIds=[edge.source, edge.target],
                        edgeIds=[edge.id],
                        status="active"
                    ))
                    # Mark edge as broken or warning based on severity
                    if rule.severity in [ViolationSeverity.high, ViolationSeverity.critical]:
                        edge.status = NodeStatus.BROKEN
                    else:
                        edge.status = NodeStatus.WARNING
        
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

            # Mark edges in cycle as WARNING in the original graph
            for j in range(len(cycle)):
                source = cycle[j]
                target = cycle[(j + 1) % len(cycle)]
                cycle_edge = next((e for e in graph.edges if e.source == source and e.target == target), None)
                if cycle_edge:
                    cycle_edge.status = NodeStatus.WARNING
        
        return violations
