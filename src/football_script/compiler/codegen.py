from __future__ import annotations
import ast
from typing import List
from .astnodes import *

def _expr(e: Expr) -> ast.expr:
    if isinstance(e, Name): return ast.Name(id=e.id, ctx=ast.Load())
    if isinstance(e, Number): return ast.Constant(e.value)
    if isinstance(e, String): return ast.Constant(e.value)
    if isinstance(e, Bool): return ast.Constant(e.value)
    if isinstance(e, NoneLit): return ast.Constant(None)
    if isinstance(e, UnaryOp):
        if e.op == "+": return ast.UnaryOp(op=ast.UAdd(), operand=_expr(e.operand))
        if e.op == "-": return ast.UnaryOp(op=ast.USub(), operand=_expr(e.operand))
        if e.op == "await": return ast.Await(value=_expr(e.operand))
        if e.op == "not": return ast.UnaryOp(op=ast.Not(), operand=_expr(e.operand))
    if isinstance(e, BinOp):
        op_map = {
            "+": ast.Add(), "-": ast.Sub(), "*": ast.Mult(), "/": ast.Div(), "%": ast.Mod(),
            "==": ast.Eq(), "!=": ast.NotEq(), "<": ast.Lt(), "<=": ast.LtE(), ">": ast.Gt(), ">=": ast.GtE(),
            "and": ast.And(), "or": ast.Or(),
        }
        if e.op in ("==","!=", "<","<=",">",">="):
            return ast.Compare(left=_expr(e.left), ops=[op_map[e.op]], comparators=[_expr(e.right)])
        if e.op in ("and", "or"):
            # model boolean ops as left-assoc chain of two terms
            return ast.BoolOp(op=op_map[e.op], values=[_expr(e.left), _expr(e.right)])
        return ast.BinOp(left=_expr(e.left), op=op_map[e.op], right=_expr(e.right))
    if isinstance(e, Call):
        # Calls map to either runtime functions (rt.<name>) or Python builtins/globals
        target = ast.Name(id=e.func, ctx=ast.Load())
        return ast.Call(func=target, args=[_expr(a) for a in e.args], keywords=[])
    if isinstance(e, Parallel):
        # parallel{e1, e2} -> await gather_all(e1, e2)
        gather = ast.Name(id="gather_all", ctx=ast.Load())
        call = ast.Call(func=gather, args=[_expr(a) for a in e.exprs], keywords=[])
        return ast.Await(value=call)
    raise NotImplementedError(f"expr not implemented: {type(e).__name__}")

def _stmt(s: Stmt) -> ast.stmt:
    if isinstance(s, Assign):
        return ast.Assign(targets=[ast.Name(id=s.name, ctx=ast.Store())], value=_expr(s.value))
    if isinstance(s, Return):
        return ast.Return(value=_expr(s.value) if s.value is not None else None)
    if isinstance(s, If):
        return ast.If(test=_expr(s.test), body=[_stmt(b) for b in s.body], orelse=[_stmt(o) for o in s.orelse])
    if isinstance(s, While):
        return ast.While(test=_expr(s.test), body=[_stmt(b) for b in s.body], orelse=[])
    if isinstance(s, FuncDef):
        args = ast.arguments(posonlyargs=[], args=[ast.arg(arg=p) for p in s.params],
                             vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])
        body = [*_stmts(s.body)]
        if s.is_async:
            return ast.AsyncFunctionDef(name=s.name, args=args, body=body, decorator_list=[])
        else:
            return ast.FunctionDef(name=s.name, args=args, body=body, decorator_list=[])
    if isinstance(s, Call):
        return ast.Expr(value=_expr(s))
    # simple_stmt expr fallback
    if isinstance(s, (Name, Number, String, Bool, NoneLit, UnaryOp, BinOp, Parallel)):
        return ast.Expr(value=_expr(s))
    raise NotImplementedError(f"stmt not implemented: {type(s).__name__}")

def _stmts(stmts: List[Stmt]) -> List[ast.stmt]:
    return [ _stmt(s) for s in stmts ]

def to_python_ast(module: Module) -> ast.Module:
    body = _stmts(module.body)
    mod = ast.Module(body=body, type_ignores=[])
    ast.fix_missing_locations(mod)
    return mod

def compile_module(mod: ast.Module, filename: str = "<fs>") -> object:
    return compile(mod, filename=filename, mode="exec")
