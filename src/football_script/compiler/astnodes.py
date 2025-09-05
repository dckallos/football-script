from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Union, Tuple

# Spans for diagnostics
@dataclass
class Span:
    uri: str
    start: Tuple[int, int]  # (line, column), 0-based
    end: Tuple[int, int]

# AST nodes (minimal)
@dataclass
class Module:
    body: List["Stmt"]
    span: Optional[Span] = None

class Stmt: ...
class Expr: ...

@dataclass
class Assign(Stmt):
    name: str
    value: Expr
    span: Optional[Span] = None

@dataclass
class Return(Stmt):
    value: Optional[Expr]
    span: Optional[Span] = None

@dataclass
class If(Stmt):
    test: Expr
    body: List[Stmt]
    orelse: List[Stmt]
    span: Optional[Span] = None

@dataclass
class While(Stmt):
    test: Expr
    body: List[Stmt]
    span: Optional[Span] = None

@dataclass
class FuncDef(Stmt):
    name: str
    params: List[str]
    body: List[Stmt]
    is_async: bool = False
    returns: Optional[Expr] = None  # v1: not used for codegen, reserved for typing
    span: Optional[Span] = None

@dataclass
class Call(Expr):
    func: str
    args: List[Expr]
    span: Optional[Span] = None

@dataclass
class Name(Expr):
    id: str
    span: Optional[Span] = None

@dataclass
class Number(Expr):
    value: Union[int, float]
    span: Optional[Span] = None

@dataclass
class String(Expr):
    value: str
    span: Optional[Span] = None

@dataclass
class Bool(Expr):
    value: bool
    span: Optional[Span] = None

@dataclass
class NoneLit(Expr):
    span: Optional[Span] = None

@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr
    span: Optional[Span] = None

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr
    span: Optional[Span] = None

@dataclass
class Parallel(Expr):
    exprs: List[Expr]
    span: Optional[Span] = None
