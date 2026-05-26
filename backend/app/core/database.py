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
                    graph_json TEXT,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_graph(self, project_id: str, name: str, root_path: str, graph: NormalizedGraph):
        graph_json = graph.model_dump_json()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO projects (id, name, root_path, graph_json)
                VALUES (?, ?, ?, ?)
            """, (project_id, name, root_path, graph_json))

    def load_graph(self, project_id: str) -> Optional[NormalizedGraph]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT graph_json FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return NormalizedGraph.model_validate_json(row[0])
        return None
