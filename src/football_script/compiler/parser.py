from __future__ import annotations
from lark import Lark, Transformer, Token, Tree
from importlib.resources import files
from typing import List
from .astnodes import *

def _span(t) -> Span | None:
    if not hasattr(t, 'meta') or t.meta is None:
        return None
    m = t.meta
    return Span(uri=getattr(m, "uri", "<unknown>"), start=(m.line-1, m.column-1), end=(m.end_line-1, m.end_column-1))

_GRAMMAR = (files(__package__) / "grammar" / "football_script.lark").read_text(encoding="utf-8")

_parser = Lark(
    _GRAMMAR,
    parser="lalr",
    start="start",
    propagate_positions=True,
    maybe_placeholders=False,
)

class ToFsAst(Transformer):
    def start(self, items):
        # items[0] is module
        mod = items[0]
        return mod

    def module(self, items):
        return Module([*items])

    # Statements
    def assign(self, items):
        target = items[0]
        if isinstance(target, Name):
            name = target.id
        elif isinstance(target, Token):
            name = target.value
        else:
            name = str(target)
        return Assign(name=name, value=items[1])

    def return_stmt(self, items):
        return Return(value=items[0] if items else None)

    def funcdef(self, items):
        # def NAME ( [params] ) block
        name_node = items[0]
        name = name_node.id if isinstance(name_node, Name) else str(name_node)
        params: List[str] = []
        # items can be: NAME, params(Tree)?, block(list)
        if len(items) >= 3 and isinstance(items[1], Tree):
            params_tree = items[1]
            for p in params_tree.children:
                if isinstance(p, Name):
                    params.append(p.id)
                elif isinstance(p, Token):
                    params.append(p.value)
                else:
                    params.append(str(p))
            body = items[2]
        else:
            body = items[-1] if items else []
        return FuncDef(name=name, params=params, body=body, is_async=False)

    def async_funcdef(self, items):
        # async def NAME ( [params] ) block
        name_node = items[0]
        name = name_node.id if isinstance(name_node, Name) else str(name_node)
        params: List[str] = []
        if len(items) >= 3 and isinstance(items[1], Tree):
            params_tree = items[1]
            for p in params_tree.children:
                if isinstance(p, Name):
                    params.append(p.id)
                elif isinstance(p, Token):
                    params.append(p.value)
                else:
                    params.append(str(p))
            body = items[2]
        else:
            body = items[-1] if items else []
        return FuncDef(name=name, params=params, body=body, is_async=True)

    def block(self, items):
        # items are statements
        return items

    def if_stmt(self, items):
        test = items[0]
        body = items[1]
        orelse = items[2] if len(items) > 2 else []
        return If(test=test, body=body, orelse=orelse)

    def while_stmt(self, items):
        return While(test=items[0], body=items[1])

    def import_stmt(self, items):
        # Lower imports as Call("__import__", ["mod", "asname?"])
        dotted = []
        dotted_node = items[0]
        if isinstance(dotted_node, Tree) and dotted_node.data == "dotted":
            for part in dotted_node.children:
                if isinstance(part, Name):
                    dotted.append(part.id)
                elif isinstance(part, Token):
                    dotted.append(part.value)
                else:
                    dotted.append(str(part))
        else:
            dotted.append(str(dotted_node))
        asname = None
        if len(items) > 1:
            aspart = items[1]
            if isinstance(aspart, Name):
                asname = aspart.id
            elif isinstance(aspart, Token):
                asname = aspart.value
            else:
                asname = str(aspart)
        args = [String(".".join(dotted))] + ([String(asname)] if asname else [])
        return Call(func="__import__", args=args)

    def dotted_name(self, items):
        return Tree("dotted", items)

    # Expressions
    def NAME(self, token: Token): 
        return Name(token.value)

    def NUMBER(self, token: Token):
        s = token.value
        try:
            # Try int, else float
            if s.isdigit():
                return Number(int(s))
            return Number(float(s))
        except ValueError:
            return Number(float(s))

    def STRING(self, token: Token): 
        return String(eval(token.value))

    def true(self, _): return Bool(True)
    def false(self, _): return Bool(False)
    def none(self, _): return NoneLit()

    def comp_op(self, items):  # not used directly
        return items[0]

    def sum(self, items):
        # Reduce left-associative chains for +,-,*,/,%% and comparisons
        node = items[0]
        i = 1
        while i < len(items):
            op_tok = items[i]
            rhs = items[i+1]
            i += 2
            op = op_tok.value if isinstance(op_tok, Token) else str(op_tok)
            node = BinOp(left=node, op=op, right=rhs)
        return node

    term = sum  # reuse the same reducer for */%
    comparison = sum

    def factor(self, items):
        if len(items) == 2:
            op_tok = items[0]
            op = op_tok.value if isinstance(op_tok, Token) else str(op_tok)
            return UnaryOp(op=op, operand=items[1])
        return items[0]

    def call(self, items):
        primary = items[0]
        if isinstance(primary, Name):
            func = primary.id
        else:
            # v1: only name calls
            raise NotImplementedError("Only simple calls supported in v1")
        args = []
        for it in items[1:]:
            if isinstance(it, list):
                args.extend(it)
            else:
                args.append(it)
        return Call(func=func, args=args)

    def arglist(self, items): return items
    def parallel(self, items):
        exprs = items[0] if items else []
        return Parallel(exprs=exprs)

def parse_to_ast(text: str, uri: str = "<memory>") -> Module:
    # lark doesn't carry uri; we keep uri in spans as needed in future (not injected per-node here).
    tree = _parser.parse(text)
    return ToFsAst().transform(tree)
