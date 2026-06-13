import sqlite3
import json
from typing import Optional
from ..models.types import NormalizedGraph

class Database:
    def __init__(self, db_path: str = "graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    root_path TEXT,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_cache (
                    project_id TEXT,
                    file_path TEXT,
                    hash TEXT,
                    result_json TEXT,
                    PRIMARY KEY (project_id, file_path)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    violation_count INTEGER,
                    cycle_count INTEGER,
                    avg_churn REAL,
                    metadata_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    project_id TEXT,
                    id TEXT,
                    kind TEXT,
                    label TEXT,
                    status TEXT,
                    parentId TEXT,
                    metadata_json TEXT,
                    PRIMARY KEY (project_id, id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    project_id TEXT,
                    id TEXT,
                    source TEXT,
                    target TEXT,
                    relation_type TEXT,
                    status TEXT,
                    is_cycle INTEGER DEFAULT 0,
                    metadata_json TEXT,
                    PRIMARY KEY (project_id, id)
                )
            """)

    def save_graph(self, project_id: str, name: str, root_path: str, graph: NormalizedGraph):
        with sqlite3.connect(self.db_path) as conn:
            # Update project metadata
            conn.execute("""
                INSERT OR REPLACE INTO projects (id, name, root_path, last_analyzed)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (project_id, name, root_path))

            # Delta writes for nodes
            for node in graph.nodes:
                conn.execute("""
                    INSERT OR REPLACE INTO nodes (project_id, id, kind, label, status, parentId, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (project_id, node.id, node.kind, node.label, node.status, node.parentId, json.dumps(node.metadata)))

            # Delta writes for edges
            for edge in graph.edges:
                conn.execute("""
                    INSERT OR REPLACE INTO edges (project_id, id, source, target, relation_type, status, is_cycle, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (project_id, edge.id, edge.source, edge.target, edge.relationType, edge.status, 1 if edge.is_cycle else 0, json.dumps(edge.metadata)))

            # Clear stale nodes and edges
            node_ids = [n.id for n in graph.nodes]
            if node_ids:
                conn.execute(f"DELETE FROM nodes WHERE project_id = ? AND id NOT IN ({','.join(['?']*len(node_ids))})", (project_id, *node_ids))
            
            edge_ids = [e.id for e in graph.edges]
            if edge_ids:
                conn.execute(f"DELETE FROM edges WHERE project_id = ? AND id NOT IN ({','.join(['?']*len(edge_ids))})", (project_id, *edge_ids))

    def load_graph(self, project_id: str) -> Optional[NormalizedGraph]:
        with sqlite3.connect(self.db_path) as conn:
            # Load nodes
            cursor = conn.execute("SELECT id, kind, label, status, parentId, metadata_json FROM nodes WHERE project_id = ?", (project_id,))
            nodes = []
            for row in cursor.fetchall():
                from ..models.types import GraphNode, NodeKind, NodeStatus
                nodes.append(GraphNode(
                    id=row[0],
                    kind=NodeKind(row[1]),
                    label=row[2],
                    status=NodeStatus(row[3]),
                    parentId=row[4],
                    metadata=json.loads(row[5])
                ))
            
            # Load edges
            cursor = conn.execute("SELECT id, source, target, relation_type, status, is_cycle, metadata_json FROM edges WHERE project_id = ?", (project_id,))
            edges = []
            for row in cursor.fetchall():
                from ..models.types import GraphEdge
                edges.append(GraphEdge(
                    id=row[0],
                    source=row[1],
                    target=row[2],
                    relationType=row[3],
                    status=row[4],
                    is_cycle=bool(row[5]),
                    metadata=json.loads(row[6])
                ))
            
            if not nodes:
                return None
                
            return NormalizedGraph(nodes=nodes, edges=edges)

    def get_file_cache(self, project_id: str) -> Dict[str, str]:
        """Returns a mapping of file_path -> hash."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT file_path, hash FROM file_cache WHERE project_id = ?", (project_id,))
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_parse_result(self, project_id: str, file_path: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT result_json FROM file_cache WHERE project_id = ? AND file_path = ?", (project_id, file_path))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_parse_result(self, project_id: str, file_path: str, file_hash: str, result_json: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO file_cache (project_id, file_path, hash, result_json)
                VALUES (?, ?, ?, ?)
            """, (project_id, file_path, file_hash, result_json))

    def clear_stale_cache(self, project_id: str, current_files: List[str]):
        """Remove cache entries for files that no longer exist."""
        if not current_files:
            return
        placeholders = ', '.join(['?'] * len(current_files))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"""
                DELETE FROM file_cache 
                WHERE project_id = ? AND file_path NOT IN ({placeholders})
            """, (project_id, *current_files))

    def create_snapshot(self, project_id: str, graph: NormalizedGraph):
        import uuid
        snapshot_id = str(uuid.uuid4())
        violation_count = len(graph.violations)
        cycle_count = len([v for v in graph.violations if v.ruleId == "CIRCULAR_DEP"])
        
        # Calculate average churn from file nodes
        file_nodes = [n for n in graph.nodes if n.kind == "FILE"]
        churns = [n.metadata.get("churn", 0) for n in file_nodes]
        avg_churn = sum(churns) / len(churns) if churns else 0
        
        metadata = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges)
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO snapshots (id, project_id, violation_count, cycle_count, avg_churn, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (snapshot_id, project_id, violation_count, cycle_count, avg_churn, json.dumps(metadata)))
        return snapshot_id

    def get_snapshots(self, project_id: str):
        from typing import List, Dict, Any
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, violation_count, cycle_count, avg_churn, metadata_json 
                FROM snapshots WHERE project_id = ? 
                ORDER BY timestamp ASC
            """, (project_id,))
            return [{
                "timestamp": row[0],
                "violation_count": row[1],
                "cycle_count": row[2],
                "avg_churn": row[3],
                "metadata": json.loads(row[4])
            } for row in cursor.fetchall()]
