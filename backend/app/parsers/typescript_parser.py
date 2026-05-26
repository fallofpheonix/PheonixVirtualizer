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

    def supports_language(self, language: str) -> bool:
        return language.lower() in ['typescript', 'ts', 'tsx']

    def parse(self, request: ParseRequest) -> ParseResult:
        start_time = time.time()
        
        # Switch language if it's TSX
        if request.path.endswith('.tsx') or request.language.lower() == 'tsx':
            self.parser.language = self.tsx_language
        else:
            self.parser.language = self.ts_language
            
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
        # TypeScript specific traversal
        if node.type == 'import_statement':
            # import { x } from 'y'
            source_node = node.child_by_field_name('source')
            if source_node:
                source = source_node.text.decode('utf8').strip("'\"")
                
                # Extract specific symbols
                imported_symbols = []
                clause = node.child_by_field_name('import_clause')
                if clause:
                    # named_imports: { a, b as c }
                    named = clause.named_children[0] if clause.named_children else None
                    if named and named.type == 'named_imports':
                        for specifier in named.named_children:
                            # specifier can be 'import_specifier'
                            name_node = specifier.child_by_field_name('name')
                            if name_node:
                                imported_symbols.append(name_node.text.decode('utf8'))
                    # namespace_import: * as x
                    elif clause.named_children and clause.named_children[0].type == 'namespace_import':
                        imported_symbols.append('*')
                
                imports.append(ImportSymbol(
                    source=source, 
                    imported=imported_symbols, 
                    range=self._get_range(node)
                ))
        
        elif node.type == 'export_statement':
            # export const x = ... or export function x() ...
            declaration = node.child_by_field_name('declaration')
            if declaration:
                if declaration.type == 'function_declaration':
                    name_node = declaration.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        exports.append(ExportSymbol(name=name, kind='function', range=self._get_range(node)))
                elif declaration.type == 'class_declaration':
                    name_node = declaration.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        exports.append(ExportSymbol(name=name, kind='class', range=self._get_range(node)))
                elif declaration.type in ['variable_declaration', 'lexical_declaration']:
                    # export const x = 1, y = 2
                    for child in declaration.children:
                        if child.type == 'variable_declarator':
                            name_node = child.child_by_field_name('name')
                            if name_node:
                                name = name_node.text.decode('utf8')
                                exports.append(ExportSymbol(name=name, kind='variable', range=self._get_range(node)))

        elif node.type in ['class_declaration', 'interface_declaration', 'enum_declaration']:
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf8')
                kind = node.type.replace('_declaration', '')
                symbols.append(ParsedSymbol(name=name, kind=kind, exported=False, range=self._get_range(node)))

        for child in node.children:
            self._traverse(child, imports, exports, symbols)

    def _get_range(self, node) -> SourceRange:
        return SourceRange(
            start_line=node.start_point[0],
            start_column=node.start_point[1],
            end_line=node.end_point[0],
            end_column=node.end_point[1]
        )
