import os
import hashlib
from typing import List, Dict
from .git_scanner import GitScanner
from ..models.types import GraphNode, NodeKind, NodeStatus

class RepositoryScanner:
    IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}
    IGNORE_FILES = {'.DS_Store', 'dependency_graph.json', 'graph.db'}

    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        self.git_scanner = GitScanner(self.root_path)

    def scan(self) -> List[GraphNode]:
        nodes = []
        for root, dirs, files in os.walk(self.root_path):
            # Prune ignored directories in-place to stop os.walk from entering them
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            rel_root = os.path.relpath(root, self.root_path)
            if rel_root == ".":
                parent_id = None
                folder_id = "root"
            else:
                parent_id = os.path.dirname(rel_root)
                if parent_id == "":
                    parent_id = "root"
                folder_id = rel_root

            if rel_root != ".":
                nodes.append(GraphNode(
                    id=folder_id,
                    kind=NodeKind.FOLDER,
                    label=os.path.basename(root),
                    path=rel_root,
                    parentId=parent_id,
                    status=NodeStatus.VERIFIED
                ))
            else:
                nodes.append(GraphNode(
                    id="root",
                    kind=NodeKind.PROJECT,
                    label=os.path.basename(self.root_path),
                    path=".",
                    status=NodeStatus.VERIFIED
                ))

            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.root_path)
                
                try:
                    git_meta = self.git_scanner.get_file_metadata(rel_file_path)
                    nodes.append(GraphNode(
                        id=rel_file_path,
                        kind=NodeKind.FILE,
                        label=file,
                        path=rel_file_path,
                        parentId=folder_id if rel_root != "." else "root",
                        status=NodeStatus.UNRESOLVED,
                        size=os.path.getsize(file_path),
                        metadata={
                            "extension": os.path.splitext(file)[1],
                            "mtime": os.path.getmtime(file_path),
                            "churn": git_meta.get("churn", 0),
                            "last_commit_date": git_meta.get("last_commit_date"),
                            "last_commit_author": git_meta.get("last_commit_author")
                        }
                    ))
                except (FileNotFoundError, OSError):
                    # Skip files that can't be accessed (e.g. broken symlinks)
                    continue
        
        return nodes

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
