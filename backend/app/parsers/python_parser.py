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
        
        # Define queries for imports, exports, and symbols
        self.query = self.language.query("""
            (import_from_statement
                module_name: (dotted_name) @import.module
                (import_list
                    (aliased_import
                        name: (dotted_name) @import.symbol
                        alias: (identifier)? @import.alias))?
                (wildcard_import)? @import.wildcard) @import.from

            (import_statement
                (dotted_name) @import.module) @import.simple

            (class_definition
                name: (identifier) @export.class.name) @export.class

            (function_definition
                name: (identifier) @export.function.name) @export.function
        """)

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['python', 'py']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        tree = self.parser.parse(bytes(request.content, "utf8"))
        
        imports = []
        exports = []
        symbols = []
        
        captures = self.query.captures(tree.root_node)
        
        # Group captures by parent node to handle complex statements
        import_from_nodes = {}
        
        for node, tag in captures:
            range_info = self._get_range(node)
            
            if tag == 'import.module':
                # Handle both 'import X' and 'from X import ...'
                # Find the top-level import statement
                curr = node
                while curr and curr.type not in ['import_statement', 'import_from_statement']:
                    curr = curr.parent
                
                if curr and curr.type == 'import_statement':
                    imports.append(ImportSymbol(
                        source=node.text.decode('utf8'),
                        range=range_info
                    ))
                elif curr and curr.type == 'import_from_statement':
                    if curr not in import_from_nodes:
                        import_from_nodes[curr] = {
                            'source': node.text.decode('utf8'), 
                            'symbols': [], 
                            'range': self._get_range(curr)
                        }

            elif tag == 'import.symbol':
                # Find the import_from_statement parent
                curr = node
                while curr and curr.type != 'import_from_statement':
                    curr = curr.parent
                if curr in import_from_nodes:
                    import_from_nodes[curr]['symbols'].append(node.text.decode('utf8'))
            
            elif tag == 'import.wildcard':
                if node in import_from_nodes:
                    import_from_nodes[node]['symbols'].append('*')

            elif tag == 'export.class.name':
                name = node.text.decode('utf8')
                exports.append(ExportSymbol(name=name, kind='class', range=range_info))
                symbols.append(ParsedSymbol(name=name, kind='class', exported=True, range=range_info))
            
            elif tag == 'export.function.name':
                name = node.text.decode('utf8')
                exports.append(ExportSymbol(name=name, kind='function', range=range_info))
                symbols.append(ParsedSymbol(name=name, kind='function', exported=True, range=range_info))

        # Finalize import_from_statements
        for node_data in import_from_nodes.values():
            imports.append(ImportSymbol(
                source=node_data['source'],
                imported=node_data['symbols'] if node_data['symbols'] else None,
                range=node_data['range']
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
