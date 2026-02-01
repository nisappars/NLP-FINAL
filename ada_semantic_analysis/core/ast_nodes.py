from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = field(default=0, kw_only=True)

@dataclass
class CompilationUnitNode(ASTNode):
    """Represents a full file parsing unit."""
    files: List['PackageNode'] = field(default_factory=list)

@dataclass
class PackageNode(ASTNode):
    """Represents a package specification or body."""
    name: str
    is_body: bool
    declarations: List[ASTNode] = field(default_factory=list)
    body: Optional[List[ASTNode]] = None # For package bodies that contain statements/procedures

@dataclass
class SubprogramNode(ASTNode):
    """Represents a procedure or function."""
    name: str
    kind: str  # "procedure" or "function"
    parameters: List['ParameterNode'] = field(default_factory=list)
    return_type: Optional[str] = None
    declarations: List[ASTNode] = field(default_factory=list)
    statements: List[ASTNode] = field(default_factory=list)
    is_body: bool = True

@dataclass
class ParameterNode(ASTNode):
    name: str
    mode: str # "in", "out", "in out"
    type_name: str

@dataclass
class VariableDeclNode(ASTNode):
    names: List[str]
    type_name: str
    initial_value: Optional[str] = None

@dataclass
class TypeDeclNode(ASTNode):
    name: str
    type_def: str

@dataclass
class IfNode(ASTNode):
    condition: str
    then_block: List[ASTNode]
    elsif_parts: List['ElsifNode'] = field(default_factory=list)
    else_block: Optional[List[ASTNode]] = None

@dataclass
class ElsifNode(ASTNode):
    condition: str
    statements: List[ASTNode]

@dataclass
class LoopNode(ASTNode):
    name: Optional[str]
    iteration_scheme: Optional[str] # "while ...", "for ..."
    statements: List[ASTNode]

@dataclass
class CallNode(ASTNode):
    name: str
    arguments: List[str]

@dataclass
class AssignmentNode(ASTNode):
    target: str
    expression: str

@dataclass
class ReturnNode(ASTNode):
    expression: Optional[str] = None

@dataclass
class WhenNode(ASTNode):
    choices: str # "Idle | Active"
    statements: List[ASTNode]

@dataclass
class CaseNode(ASTNode):
    expression: str
    when_parts: List[WhenNode]
