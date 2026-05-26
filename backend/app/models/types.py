from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

class NodeKind(str, Enum):
    PROJECT = "PROJECT"
    FOLDER = "FOLDER"
    FILE = "FILE"
    MODULE = "MODULE"
    CLASS = "CLASS"
    METHOD = "METHOD"
    FUNCTION = "FUNCTION"
    INTERFACE = "INTERFACE"
    ENUM = "ENUM"
    TRAIT = "TRAIT"
    EXTERNAL_PACKAGE = "EXTERNAL_PACKAGE"

class RelationType(str, Enum):
    IMPORTS = "IMPORTS"
    EXPORTS = "EXPORTS"
    CALLS = "CALLS"
    CREATES = "CREATES"
    INHERITS = "INHERITS"
    IMPLEMENTS = "IMPLEMENTS"
    REFERENCES = "REFERENCES"
    READS = "READS"
    WRITES = "WRITES"
    DEPENDS_ON = "DEPENDS_ON"
    CIRCULAR = "CIRCULAR"

class NodeStatus(str, Enum):
    VERIFIED = "VERIFIED"
    BROKEN = "BROKEN"
    WARNING = "WARNING"
    UNRESOLVED = "UNRESOLVED"

class SourceRange(BaseModel):
    start_line: int
    start_column: int
    end_line: int
    end_column: int

class ViolationSeverity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Violation(BaseModel):
    id: str
    ruleId: str
    severity: ViolationSeverity
    message: str
    sourceNodeIds: List[str] = Field(default_factory=list)
    edgeIds: List[str] = Field(default_factory=list)
    status: str = "active"
    range: Optional[SourceRange] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CustomRule(BaseModel):
    id: str
    severity: ViolationSeverity = ViolationSeverity.high
    message: str
    from_path: Optional[str] = None # Regex or substring
    to_path: Optional[str] = None   # Regex or substring
    action: str = "DENY" # Currently only DENY supported

class PheonixConfig(BaseModel):
    project_name: Optional[str] = None
    rules: List[CustomRule] = Field(default_factory=list)

class ParseError(BaseModel):
    message: str
    range: Optional[SourceRange] = None
    recoverable: bool
    code: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParsedSymbol(BaseModel):
    name: str
    kind: str # 'class', 'function', etc.
    scope: Optional[str] = None
    exported: bool
    range: Optional[SourceRange] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParsedRelation(BaseModel):
    sourceRef: str
    targetRef: str
    relationType: RelationType
    symbolName: Optional[str] = None
    namespace: Optional[str] = None
    dynamic: bool = False
    confidence: float = 1.0
    range: Optional[SourceRange] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ImportSymbol(BaseModel):
    source: str
    imported: Optional[List[str]] = None
    alias: Optional[Dict[str, str]] = None
    dynamic: bool = False
    range: Optional[SourceRange] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExportSymbol(BaseModel):
    name: str
    kind: str
    range: Optional[SourceRange] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FileParseMetadata(BaseModel):
    parserVersion: str
    languageVersion: Optional[str] = None
    lineCount: Optional[int] = None
    byteSize: Optional[int] = None
    hash: Optional[str] = None
    durationMs: Optional[float] = None
    wasIncremental: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParseRequest(BaseModel):
    fileId: str
    path: str
    language: str
    content: str
    contentHash: str
    version: int
    projectRoot: str

class ParseResult(BaseModel):
    fileId: str
    path: str
    language: str
    parsed: bool
    syntaxErrors: List[ParseError] = Field(default_factory=list)
    symbols: List[ParsedSymbol] = Field(default_factory=list)
    relations: List[ParsedRelation] = Field(default_factory=list)
    exports: List[ExportSymbol] = Field(default_factory=list)
    imports: List[ImportSymbol] = Field(default_factory=list)
    metadata: FileParseMetadata
    confidence: float = 1.0

class GraphNode(BaseModel):
    id: str
    kind: NodeKind
    label: str
    path: Optional[str] = None
    parentId: Optional[str] = None
    status: NodeStatus = NodeStatus.UNRESOLVED
    size: Optional[int] = None
    health: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationType: Union[RelationType, str]
    status: NodeStatus = NodeStatus.UNRESOLVED
    weight: float = 1.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NormalizedGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    violations: List[Violation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
