import os
from typing import List, Dict, Optional
from ..models.types import (
    NormalizedGraph, GraphNode, GraphEdge, NodeKind, 
    NodeStatus, ParseResult, RelationType, ImportSymbol
)

class Normalizer:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.symbol_table: Dict[str, List[str]] = {} # file_path -> list of exported symbols
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_nodes(self, nodes: List[GraphNode]):
        for node in nodes:
            self.nodes[node.id] = node

    def process_parse_result(self, result: ParseResult):
        # Update symbol table
        self.symbol_table[result.path] = [e.name for e in result.exports]
        
        # Resolve imports
        for imp in result.imports:
            target_path = self._resolve_path(result.path, imp.source)
            if target_path:
                edge_id = f"{result.path}->{target_path}"
                self.edges.append(GraphEdge(
                    id=edge_id,
                    source=result.path,
                    target=target_path,
                    relationType=RelationType.IMPORTS,
                    status=NodeStatus.VERIFIED if target_path in self.nodes else NodeStatus.BROKEN
                ))
            else:
                # Unresolved or broken path
                pass

    def _resolve_path(self, source_path: str, import_source: str) -> Optional[str]:
        # Basic resolution logic
        source_dir_rel = os.path.dirname(source_path)
        
        # Handle relative imports like '..models.types' or '.base'
        is_relative = import_source.startswith('.')
        if is_relative:
            # Count dots
            dots = 0
            for char in import_source:
                if char == '.':
                    dots += 1
                else:
                    break
            
            # Remove leading dots
            pure_import = import_source[dots:]
            
            # Go up 'dots - 1' levels from source_dir_rel
            target_dir = source_dir_rel
            for _ in range(dots - 1):
                target_dir = os.path.dirname(target_dir)
            
            potential_rel_path = os.path.join(target_dir, pure_import.replace('.', os.sep))
        else:
            potential_rel_path = import_source.replace('.', os.sep)

        candidates = [
            potential_rel_path + ".py",
            os.path.join(potential_rel_path, "__init__.py"),
            # Also try absolute from root for non-relative
            potential_rel_path + ".py" if not is_relative else None,
        ]
        
        # Clean candidates
        candidates = [c for c in candidates if c is not None]

        for cand in candidates:
            # Try to find a node with this path
            if cand in self.nodes:
                return cand
            
            # Also try relative to project root
            # (In some cases import_source is relative to root but doesn't start with dot)
            if not is_relative:
                # This is tricky for python as it depends on PYTHONPATH
                # For now assume root is in PYTHONPATH
                pass

        return None

    def get_graph(self) -> NormalizedGraph:
        return NormalizedGraph(
            nodes=list(self.nodes.values()),
            edges=self.edges
        )
