import time
from typing import List
from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjs
from .base import BaseParser
from ..models.types import (
    ParseRequest, ParseResult, ImportSymbol, ExportSymbol, 
    ParsedSymbol, FileParseMetadata, SourceRange
)

class JavaScriptParser(BaseParser):
    def __init__(self):
        self.language = Language(tsjs.language())
        self.parser = Parser(self.language)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['javascript', 'js']

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
        if node.type == 'import_statement':
            # import X from 'Y'
            source_node = node.child_by_field_name('source')
            if source_node:
                # Remove quotes
                source = source_node.text.decode('utf8').strip("'\"")
                imports.append(ImportSymbol(source=source, range=self._get_range(node)))
        elif node.type == 'lexical_declaration':
            # const X = require('Y')
            for child in node.children:
                if child.type == 'variable_declarator':
                    value_node = child.child_by_field_name('value')
                    if value_node and value_node.type == 'call_expression':
                        function_node = value_node.child_by_field_name('function')
                        if function_node and function_node.text.decode('utf8') == 'require':
                            args = value_node.child_by_field_name('arguments')
                            if args and len(args.children) > 1:
                                source = args.children[1].text.decode('utf8').strip("'\"")
                                imports.append(ImportSymbol(source=source, range=self._get_range(node)))
        elif node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf8')
                exports.append(ExportSymbol(name=name, kind='class', range=self._get_range(node)))
                symbols.append(ParsedSymbol(name=name, kind='class', exported=True, range=self._get_range(node)))
        elif node.type == 'function_declaration':
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
