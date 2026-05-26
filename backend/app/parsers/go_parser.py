import time
from typing import List
from tree_sitter import Language, Parser
import tree_sitter_go as tsgo
from .base import BaseParser
from ..models.types import (
    ParseRequest, ParseResult, ImportSymbol, ExportSymbol, 
    ParsedSymbol, FileParseMetadata, SourceRange
)

class GoParser(BaseParser):
    def __init__(self):
        self.language = Language(tsgo.language())
        self.parser = Parser(self.language)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['go']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        tree = self.parser.parse(bytes(request.content, "utf8"))
        root_node = tree.root_node

        imports = []
        exports = []
        symbols = []
        
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
        # Go specific traversal
        if node.type == 'import_spec':
            # import "x" or import y "x"
            path_node = node.child_by_field_name('path')
            if path_node:
                source = path_node.text.decode('utf8').strip("'\"")
                imports.append(ImportSymbol(source=source, range=self._get_range(node)))
        
        elif node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf8')
                # In Go, exported names start with uppercase
                is_exported = name[0].isupper() if name else False
                if is_exported:
                    exports.append(ExportSymbol(name=name, kind='function', range=self._get_range(node)))
                symbols.append(ParsedSymbol(name=name, kind='function', exported=is_exported, range=self._get_range(node)))

        elif node.type == 'type_declaration':
            # type X struct or type X interface
            for child in node.children:
                if child.type == 'type_spec':
                    name_node = child.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        is_exported = name[0].isupper() if name else False
                        if is_exported:
                            exports.append(ExportSymbol(name=name, kind='type', range=self._get_range(node)))
                        symbols.append(ParsedSymbol(name=name, kind='type', exported=is_exported, range=self._get_range(node)))

        for child in node.children:
            self._traverse(child, imports, exports, symbols)

    def _get_range(self, node) -> SourceRange:
        return SourceRange(
            start_line=node.start_point[0],
            start_column=node.start_point[1],
            end_line=node.end_point[0],
            end_column=node.end_point[1]
        )
