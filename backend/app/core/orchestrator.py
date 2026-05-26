import os
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor
from .scanner import RepositoryScanner
from .normalizer import Normalizer
from .rules import RuleEngine
from .database import Database
from .config_loader import ConfigLoader
from ..parsers.factory import ParserFactory
from ..models.types import ParseRequest, NormalizedGraph, ParseResult

def _parse_file_worker(file_info: Dict[str, Any], project_root: str) -> Optional[ParseResult]:
    """Worker function for multiprocessing."""
    # Initialize parser factory in each worker to avoid pickling issues
    factory = ParserFactory()
    lang = file_info['lang']
    parser = factory.get_parser(lang)
    if not parser:
        return None

    file_path = os.path.join(project_root, file_info['path'])
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        request = ParseRequest(
            fileId=file_info['id'],
            path=file_info['path'],
            language=lang,
            content=content,
            contentHash="hash", # Should ideally be pre-calculated
            version=1,
            projectRoot=project_root
        )
        return parser.parse(request)
    except Exception as e:
        print(f"Error parsing {file_info['path']}: {e}")
        return None

class Orchestrator:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.config = ConfigLoader.load_config(self.project_root)
        self.scanner = RepositoryScanner(self.project_root)
        self.normalizer = Normalizer(self.project_root)
        self.rule_engine = RuleEngine(self.config)
        self.db = Database()

    def analyze(self) -> NormalizedGraph:
        print(f"Scanning repository: {self.project_root}")
        nodes = self.scanner.scan()
        self.normalizer.add_nodes(nodes)

        file_nodes = [n for n in nodes if n.kind == "FILE"]
        print(f"Found {len(file_nodes)} files. Starting parallel parsing...")

        # Prepare tasks for workers
        tasks = []
        lang_map = {
            '.py': 'python', 
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.go': 'go'
        }
        for file_node in file_nodes:
            ext = os.path.splitext(file_node.label)[1].lower()
            lang = lang_map.get(ext)
            if lang:
                tasks.append({
                    'id': file_node.id,
                    'path': file_node.path,
                    'lang': lang
                })

        # Execute parsing in parallel
        results = []
        with ProcessPoolExecutor() as executor:
            # Using map or submit
            futures = [executor.submit(_parse_file_worker, task, self.project_root) for task in tasks]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        print(f"Parsing complete. Processing {len(results)} results...")
        for result in results:
            self.normalizer.process_parse_result(result)

        graph = self.normalizer.get_graph()

        print("Evaluating rules...")
        violations = self.rule_engine.evaluate(graph)
        graph.violations = violations

        print("Saving graph to database...")
        self.db.save_graph("default-project", "Default Project", self.project_root, graph)

        print("Analysis complete.")
        return graph
