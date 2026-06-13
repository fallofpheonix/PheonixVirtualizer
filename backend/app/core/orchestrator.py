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
            contentHash=file_info['hash'],
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
        project_id = "default-project"
        print(f"Scanning repository: {self.project_root}")
        nodes = self.scanner.scan()
        self.normalizer.add_nodes(nodes)

        file_nodes = [n for n in nodes if n.kind == "FILE"]
        print(f"Found {len(file_nodes)} files. Checking cache...")

        cached_hashes = self.db.get_file_cache(project_id)
        current_files = [n.path for n in file_nodes]
        self.db.clear_stale_cache(project_id, current_files)

        tasks = []
        parse_results = []
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
            if not lang:
                continue

            abs_path = os.path.join(self.project_root, file_node.path)
            try:
                current_hash = self.scanner.get_file_hash(abs_path)
            except Exception:
                continue
            
            if file_node.path in cached_hashes and cached_hashes[file_node.path] == current_hash:
                cached_json = self.db.get_parse_result(project_id, file_node.path)
                if cached_json:
                    try:
                        res = ParseResult.model_validate_json(cached_json)
                        res.metadata.wasIncremental = True
                        parse_results.append(res)
                        continue
                    except Exception:
                        pass

            tasks.append({
                'id': file_node.id,
                'path': file_node.path,
                'lang': lang,
                'hash': current_hash
            })

        if tasks:
            print(f"Parsing {len(tasks)} changed files...")
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(_parse_file_worker, task, self.project_root) for task in tasks]
                for future in futures:
                    result = future.result()
                    if result:
                        parse_results.append(result)
                        # Save to cache
                        self.db.save_parse_result(project_id, result.path, result.metadata.hash, result.model_dump_json())

        print(f"Processing {len(parse_results)} results...")
        for result in parse_results:
            self.normalizer.process_parse_result(result)

        graph = self.normalizer.get_graph()

        print("Evaluating rules...")
        violations = self.rule_engine.evaluate(graph)
        graph.violations = violations

        print("Saving graph to database...")
        self.db.save_graph(project_id, "Default Project", self.project_root, graph)

        print("Analysis complete.")
        return graph
