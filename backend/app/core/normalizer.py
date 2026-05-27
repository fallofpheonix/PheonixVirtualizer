import os
from typing import List, Dict, Optional, Tuple, Set
from ..models.types import (
    NormalizedGraph, GraphNode, GraphEdge, NodeKind, 
    NodeStatus, ParseResult, RelationType, ImportSymbol
)

class Normalizer:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.symbol_table: Dict[str, Set[str]] = {} # file_path -> set of exported symbol names
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_nodes(self, nodes: List[GraphNode]):
        for node in nodes:
            self.nodes[node.id] = node

    def process_parse_result(self, result: ParseResult):
        # Update global symbol table with exports from this file
        self.symbol_table[result.path] = {e.name for e in result.exports}
        
        # Resolve imports
        for imp in result.imports:
            target_path, candidates = self._resolve_path(result.path, imp.source)
            
            if target_path:
                # INTERNAL DEPENDENCY
                edge_id = f"{result.path}->{target_path}"
                status = NodeStatus.VERIFIED
                if imp.imported:
                    if target_path in self.symbol_table:
                        valid_exports = self.symbol_table[target_path]
                        missing_symbols = [sym for sym in imp.imported if sym not in valid_exports]
                        if missing_symbols:
                            status = NodeStatus.BROKEN
                
                self.edges.append(GraphEdge(
                    id=edge_id,
                    source=result.path,
                    target=target_path,
                    relationType=RelationType.IMPORTS,
                    status=status if target_path in self.nodes else NodeStatus.BROKEN,
                    metadata={"imported_symbols": imp.imported, "external": False}
                ))
            else:
                # EXTERNAL OR UNRESOLVED
                # Heuristic: if it doesn't look like a relative path, treat as external
                if not imp.source.startswith('.'):
                    # EXTERNAL PACKAGE (e.g., 'os', 'fastapi', 'react')
                    package_id = f"pkg:{imp.source}"
                    if package_id not in self.nodes:
                        self.nodes[package_id] = GraphNode(
                            id=package_id,
                            kind=NodeKind.EXTERNAL_PACKAGE,
                            label=imp.source,
                            status=NodeStatus.VERIFIED, # Assume external packages exist for now
                            metadata={"is_external": True}
                        )
                    
                    self.edges.append(GraphEdge(
                        id=f"{result.path}->{package_id}",
                        source=result.path,
                        target=package_id,
                        relationType=RelationType.IMPORTS,
                        status=NodeStatus.VERIFIED,
                        metadata={"imported_symbols": imp.imported, "external": True}
                    ))
                else:
                    # BROKEN INTERNAL RELATIVE IMPORT
                    edge_id = f"{result.path}->broken:{imp.source}"
                    self.edges.append(GraphEdge(
                        id=edge_id,
                        source=result.path,
                        target=edge_id, # Self-pointing for broken for now
                        relationType=RelationType.IMPORTS,
                        status=NodeStatus.BROKEN,
                        metadata={
                            "imported_symbols": imp.imported, 
                            "external": False, 
                            "raw_source": imp.source,
                            "diagnostic": {
                                "error": "ERR_PATH_RESOLVE",
                                "candidates_tried": candidates
                            }
                        }
                    ))

    def _resolve_path(self, source_path: str, import_source: str) -> Tuple[Optional[str], List[str]]:
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
            # Also try relative to project root
            potential_rel_path + ".py" if not is_relative else None,
        ]
        
        # Clean candidates
        candidates = [c for c in candidates if c is not None]

        for cand in candidates:
            # Try to find a node with this path
            if cand in self.nodes:
                return cand, candidates
            
        return None, candidates

    def get_graph(self) -> NormalizedGraph:
        return NormalizedGraph(
            nodes=list(self.nodes.values()),
            edges=self.edges
        )
