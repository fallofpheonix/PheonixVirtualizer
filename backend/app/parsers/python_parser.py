import time
from typing import List
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from .base import BaseParser
from ..models.types import (
    ParseRequest, ParseResult, ImportSymbol, ExportSymbol, 
    ParsedSymbol, FileParseMetadata, SourceRange, ParseError
)

class PythonParser(BaseParser):
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['python', 'py']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        tree = self.parser.parse(bytes(request.content, "utf8"))
        root_node = tree.root_node

        imports = []
        exports = []
        symbols = []
        
        # Simple traversal for demonstration
        # We should use Tree-sitter queries for real work
        self._traverse(root_node, imports, exports, symbols)

        duration_ms = (time.time() - start_time) * 1000

        metadata = FileParseMetadata(
            parserVersion="0.1.0",
            lineCount=len(request.content.splitlines()),
            byteSize=len(request.content.encode('utf-8')),
            durationMs=duration_ms
        )

        return ParseResult(
            fileId=request.fileId,
            path=request.path,
            language=request.language,
            parsed=True,
            imports=imports,
            exports=exports,
            symbols=symbols,
            metadata=metadata
        )

    def _traverse(self, node, imports, exports, symbols):
        # This is a placeholder for a more robust query-based approach
        if node.type == 'import_from_statement':
            # from X import Y
            module_node = node.child_by_field_name('module_name')
            if module_node:
                module_name = module_node.text.decode('utf8')
                imports.append(ImportSymbol(source=module_name, range=self._get_range(node)))
        elif node.type == 'import_statement':
            # import X
            for child in node.children:
                if child.type == 'dotted_name':
                    imports.append(ImportSymbol(source=child.text.decode('utf8'), range=self._get_range(node)))
        elif node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf8')
                exports.append(ExportSymbol(name=name, kind='class', range=self._get_range(node)))
                symbols.append(ParsedSymbol(name=name, kind='class', exported=True, range=self._get_range(node)))
        elif node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf8')
                exports.append(ExportSymbol(name=name, kind='function', range=self._get_range(node)))
                symbols.append(ParsedSymbol(name=name, kind='function', exported=True, range=self._get_range(node)))

        for child in node.children:
            self._traverse(child, imports, exports, symbols)

    def _get_range(self, node) -> SourceRange:
        return SourceRange(
            start_line=node.start_point[0],
            start_column=node.start_point[1],
            end_line=node.end_point[0],
            end_column=node.end_point[1]
        )
