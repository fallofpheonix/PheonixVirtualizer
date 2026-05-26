from typing import List, Optional
from .base import BaseParser
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser

class ParserFactory:
    def __init__(self):
        self.parsers: List[BaseParser] = [
            PythonParser(),
            JavaScriptParser()
        ]

    def get_parser(self, language: str) -> Optional[BaseParser]:
        for parser in self.parsers:
            if parser.supports_language(language):
                return parser
        return None

    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript"]
