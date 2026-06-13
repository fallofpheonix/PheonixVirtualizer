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
        
        self.query = self.language.query("""
            (import_spec path: (interpreted_string_literal) @import.source) @import

            (function_declaration name: (identifier) @symbol.name) @symbol.function
            (type_spec name: (type_identifier) @symbol.name) @symbol.type
            (method_declaration name: (field_identifier) @symbol.name) @symbol.method
        """)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['go']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        tree = self.parser.parse(bytes(request.content, "utf8"))
        
        imports = []
        exports = []
        symbols = []
        
        captures = self.query.captures(tree.root_node)
        
        for node, tag in captures:
            range_info = self._get_range(node)
            text = node.text.decode('utf8')
            
            if tag == 'import.source':
                source = text.strip("'\"")
                imports.append(ImportSymbol(source=source, range=range_info))
            
            elif tag.startswith('symbol.name'):
                kind = tag.split('.')[-1]
                # In Go, exported names start with uppercase
                is_exported = text[0].isupper() if text else False
                if is_exported:
                    exports.append(ExportSymbol(name=text, kind=kind, range=range_info))
                symbols.append(ParsedSymbol(name=text, kind=kind, exported=is_exported, range=range_info))

        duration_ms = (time.time() - start_time) * 1000

        metadata = FileParseMetadata(
            parserVersion="0.2.0",
            lineCount=len(request.content.splitlines()),
            byteSize=len(request.content.encode('utf-8')),
            durationMs=duration_ms,
            hash=request.contentHash
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

    def _get_range(self, node) -> SourceRange:
        return SourceRange(
            start_line=node.start_point[0],
            start_column=node.start_point[1],
            end_line=node.end_point[0],
            end_column=node.end_point[1]
        )
