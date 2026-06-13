import time
from typing import List
from tree_sitter import Language, Parser
import tree_sitter_typescript as tstypescript
from .base import BaseParser
from ..models.types import (
    ParseRequest, ParseResult, ImportSymbol, ExportSymbol, 
    ParsedSymbol, FileParseMetadata, SourceRange
)

class TypeScriptParser(BaseParser):
    def __init__(self):
        # TypeScript grammar actually provides two languages: typescript and tsx
        self.ts_language = Language(tstypescript.language_typescript())
        self.tsx_language = Language(tstypescript.language_tsx())
        self.parser = Parser(self.ts_language)
        
        # Define shared query for TS and TSX
        self.query_src = """
            (import_statement
                source: (string) @import.source) @import

            (import_clause
                (named_imports
                    (import_specifier
                        name: (identifier) @import.symbol)))

            (import_clause
                (namespace_import
                    (identifier) @import.symbol))

            (import_clause
                (identifier) @import.symbol)

            (export_statement
                declaration: (function_declaration name: (identifier) @export.name)) @export.function

            (export_statement
                declaration: (class_declaration name: (identifier) @export.name)) @export.class

            (export_statement
                declaration: (interface_declaration name: (identifier) @export.name)) @export.interface

            (export_statement
                declaration: (enum_declaration name: (identifier) @export.name)) @export.enum

            (export_statement
                declaration: (lexical_declaration (variable_declarator name: (identifier) @export.name))) @export.variable

            (class_declaration name: (identifier) @symbol.name) @symbol.class
            (function_declaration name: (identifier) @symbol.name) @symbol.function
            (interface_declaration name: (identifier) @symbol.name) @symbol.interface
            (enum_declaration name: (identifier) @symbol.name) @symbol.enum
        """
        self.ts_query = self.ts_language.query(self.query_src)
        self.tsx_query = self.tsx_language.query(self.query_src)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['typescript', 'ts', 'tsx']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        
        # Switch language and query if it's TSX
        if request.path.endswith('.tsx') or request.language.lower() == 'tsx':
            self.parser.language = self.tsx_language
            query = self.tsx_query
        else:
            self.parser.language = self.ts_language
            query = self.ts_query
            
        tree = self.parser.parse(bytes(request.content, "utf8"))
        
        imports = []
        exports = []
        symbols = []
        
        captures = query.captures(tree.root_node)
        import_nodes = {}
        
        for node, tag in captures:
            range_info = self._get_range(node)
            text = node.text.decode('utf8')
            
            if tag == 'import.source':
                source = text.strip("'\"")
                curr = node
                while curr and curr.type != 'import_statement':
                    curr = curr.parent
                
                if curr not in import_nodes:
                    import_nodes[curr] = {'source': source, 'symbols': [], 'range': self._get_range(curr)}

            elif tag == 'import.symbol':
                curr = node
                while curr and curr.type != 'import_statement':
                    curr = curr.parent
                if curr in import_nodes:
                    import_nodes[curr]['symbols'].append(text)

            elif tag.startswith('export.name'):
                kind = tag.split('.')[-1]
                exports.append(ExportSymbol(name=text, kind=kind, range=range_info))
                symbols.append(ParsedSymbol(name=text, kind=kind, exported=True, range=range_info))

            elif tag.startswith('symbol.name'):
                kind = tag.split('.')[-1]
                if not any(e.name == text for e in exports):
                    symbols.append(ParsedSymbol(name=text, kind=kind, exported=False, range=range_info))

        for imp_data in import_nodes.values():
            imports.append(ImportSymbol(
                source=imp_data['source'],
                imported=imp_data['symbols'] if imp_data['symbols'] else None,
                range=imp_data['range']
            ))

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
