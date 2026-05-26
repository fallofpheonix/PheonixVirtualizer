import os
import time
from typing import List
from .scanner import RepositoryScanner
from .normalizer import Normalizer
from .rules import RuleEngine
from .database import Database
from ..parsers.factory import ParserFactory
from ..models.types import ParseRequest, NormalizedGraph

class Orchestrator:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.scanner = RepositoryScanner(self.project_root)
        self.normalizer = Normalizer(self.project_root)
        self.parser_factory = ParserFactory()
        self.rule_engine = RuleEngine()
        self.db = Database()

    def analyze(self) -> NormalizedGraph:
        print(f"Scanning repository: {self.project_root}")
        nodes = self.scanner.scan()
        self.normalizer.add_nodes(nodes)

        file_nodes = [n for n in nodes if n.kind == "FILE"]
        print(f"Found {len(file_nodes)} files. Starting parsing...")

        for file_node in file_nodes:
            ext = os.path.splitext(file_node.label)[1].lower()
            # Map extension to language
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript'
            }
            lang = lang_map.get(ext)
            if lang:
                parser = self.parser_factory.get_parser(lang)
                if parser:
                    file_path = os.path.join(self.project_root, file_node.path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        request = ParseRequest(
                            fileId=file_node.id,
                            path=file_node.path,
                            language=lang,
                            content=content,
                            contentHash="hash", # Should be calculated
                            version=1,
                            projectRoot=self.project_root
                        )
                        result = parser.parse(request)
                        self.normalizer.process_parse_result(result)
                    except Exception as e:
                        print(f"Error parsing {file_node.path}: {e}")

        graph = self.normalizer.get_graph()
        
        print("Evaluating rules...")
        violations = self.rule_engine.evaluate(graph)
        graph.violations = violations

        print("Saving graph to database...")
        self.db.save_graph("default-project", "Default Project", self.project_root, graph)

        print("Analysis complete.")
        return graph
