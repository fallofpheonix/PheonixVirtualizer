import networkx as nx
import re
import os
from typing import List, Dict
from ..models.types import (
    NormalizedGraph, GraphEdge, NodeStatus, 
    RelationType, ViolationSeverity, Violation, PheonixConfig
)
from .plugin_loader import load_plugins

class RuleEngine:
    def __init__(self, config: PheonixConfig = PheonixConfig()):
        self.config = config
        plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
        self.plugins = load_plugins(plugins_dir)

    def evaluate(self, graph: NormalizedGraph) -> List[Violation]:
        violations = []
        
        # 1. Circular Dependency Detection
        violations.extend(self._check_circular_dependencies(graph))
        
        # 2. Custom Architectural Rules
        violations.extend(self._check_custom_rules(graph))
        
        # 3. Plugin Rules
        for plugin in self.plugins:
            try:
                violations.extend(plugin.evaluate(graph))
            except Exception as e:
                print(f"Plugin error in {plugin.__class__.__name__}: {e}")
        
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
            G.add_edge(edge.source, edge.target, edge_id=edge.id)

        cycles = list(nx.simple_cycles(G))
        for i, cycle in enumerate(cycles):
            # A cycle is a circular dependency
            message = f"Circular dependency detected: {' -> '.join(cycle)} -> {cycle[0]}"
            
            cycle_edge_ids = []
            # Mark edges in cycle as WARNING and is_cycle=True
            for j in range(len(cycle)):
                source = cycle[j]
                target = cycle[(j + 1) % len(cycle)]
                
                # Find the specific edge in the graph
                # Note: If there are multiple edges between two nodes (rare for file imports), 
                # we flag all of them.
                for edge in graph.edges:
                    if edge.source == source and edge.target == target:
                        edge.status = NodeStatus.WARNING
                        edge.is_cycle = True
                        cycle_edge_ids.append(edge.id)

            violations.append(Violation(
                id=f"circular-{i}",
                ruleId="CIRCULAR_DEP",
                severity=ViolationSeverity.medium,
                message=message,
                sourceNodeIds=cycle,
                edgeIds=list(set(cycle_edge_ids)),
                status="active",
                metadata={"cycle": cycle}
            ))
        
        return violations
