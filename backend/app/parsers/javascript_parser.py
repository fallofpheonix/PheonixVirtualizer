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
        
        self.query = self.language.query("""
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

            (call_expression
                function: (identifier) @require_func
                arguments: (arguments (string) @import.source)
                (#eq? @require_func "require")) @import.require

            (export_statement
                declaration: (function_declaration name: (identifier) @export.name)) @export.function

            (export_statement
                declaration: (class_declaration name: (identifier) @export.name)) @export.class

            (export_statement
                declaration: (lexical_declaration (variable_declarator name: (identifier) @export.name))) @export.variable

            (class_declaration name: (identifier) @symbol.name) @symbol.class
            (function_declaration name: (identifier) @symbol.name) @symbol.function
        """)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['javascript', 'js']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        tree = self.parser.parse(bytes(request.content, "utf8"))
        
        imports = []
        exports = []
        symbols = []
        
        captures = self.query.captures(tree.root_node)
        
        import_nodes = {}
        
        for node, tag in captures:
            range_info = self._get_range(node)
            text = node.text.decode('utf8')
            
            if tag == 'import.source':
                # ESM or CommonJS
                source = text.strip("'\"")
                curr = node
                while curr and curr.type not in ['import_statement', 'call_expression']:
                    curr = curr.parent
                
                if curr not in import_nodes:
                    import_nodes[curr] = {'source': source, 'symbols': [], 'range': self._get_range(curr)}
                else:
                    import_nodes[curr]['source'] = source

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
                # Only add if not already added as export
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
