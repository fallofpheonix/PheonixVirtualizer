import subprocess
import os
from typing import Dict, Any, Optional

class GitScanner:
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        self.is_repo = self._check_is_repo()

    def _check_is_repo(self) -> bool:
        try:
            subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.root_path, stderr=subprocess.STDOUT)
            return True
        except Exception:
            return False

    def get_file_metadata(self, rel_path: str) -> Dict[str, Any]:
        if not self.is_repo:
            return {}

        try:
            # Get churn (commit count)
            churn_cmd = ["git", "rev-list", "--count", "HEAD", "--", rel_path]
            churn = subprocess.check_output(churn_cmd, cwd=self.root_path, stderr=subprocess.STDOUT).decode().strip()
            
            # Get last commit date and author
            info_cmd = ["git", "log", "-1", "--format=%at|%an", "--", rel_path]
            info = subprocess.check_output(info_cmd, cwd=self.root_path, stderr=subprocess.STDOUT).decode().strip()
            
            if not info:
                return {"churn": 0, "last_commit_date": None, "last_commit_author": None}
                
            parts = info.split('|')
            last_date = parts[0] if len(parts) > 0 else None
            last_author = parts[1] if len(parts) > 1 else None
            
            return {
                "churn": int(churn) if churn else 0,
                "last_commit_date": int(last_date) if last_date else None,
                "last_commit_author": last_author
            }
        except Exception:
            return {"churn": 0, "last_commit_date": None, "last_commit_author": None}
