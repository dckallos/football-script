from __future__ import annotations
import asyncio
import sys
from pathlib import Path
import warnings
import typer
from lark.exceptions import UnexpectedToken, UnexpectedCharacters, UnexpectedInput

from .compiler.parser import parse_to_ast
from .compiler.codegen import to_python_ast, compile_module
from .runtime import core as rt

app = typer.Typer(help="football-script CLI (chelsea)")

@app.command()
def run(path: str):
    """Run a .fs program."""
    p = Path(path)
    if not p.exists():
        typer.echo(f"{path}: error FS1000: file not found")
        raise typer.Exit(2)
    src = p.read_text(encoding="utf-8")
    uri = p.resolve().as_uri()  # make absolute before converting to file:// URI
    try:
        fs_module = parse_to_ast(src, uri=uri)
    except UnexpectedToken as e:
        line = getattr(e, "line", None)
        col = getattr(e, "column", None)
        tok = getattr(e, "token", None)
        tok_desc = f"{getattr(tok, 'type', 'TOKEN')} {repr(getattr(tok, 'value', ''))}"
        _print_context(path, src, line, col)
        typer.echo(f"{path}:{line}:{col}: error FS1001: unexpected token {tok_desc}")
        raise typer.Exit(2)
    except UnexpectedCharacters as e:
        line = getattr(e, "line", None)
        col = getattr(e, "column", None)
        _print_context(path, src, line, col)
        typer.echo(f"{path}:{line}:{col}: error FS1002: unexpected characters")
        raise typer.Exit(2)
    except UnexpectedInput as e:
        line = getattr(e, "line", 1)
        col = getattr(e, "column", 1)
        _print_context(path, src, line, col)
        typer.echo(f"{path}:{line}:{col}: error FS1003: parse error")
        raise typer.Exit(2)
    py_module = to_python_ast(fs_module)
    code = compile_module(py_module, filename=path)
    # Prepare globals with runtime
    g = {
        "__name__": "__fs_main__",
        "asyncio": asyncio,
        "rt": rt,
        # expose selected runtime helpers directly
        "sleep_ms": rt.sleep_ms,
        "print": rt.print,
        "gather_all": rt.gather_all,
    }
    # Avoid noise if user wrote top-level calls to async funcs (common during exploration)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    exec(code, g, g)  # define functions, exec top-level

@app.command()
def repl():
    """Minimal REPL stub."""
    typer.echo("football-script REPL (stub). Type Ctrl-D to exit.")
    for line in sys.stdin:
        try:
            fs_module = parse_to_ast(line, uri="<repl>")
            py_module = to_python_ast(fs_module)
            code = compile_module(py_module, filename="<repl>")
            g = {"__name__": "__fs_repl__", "asyncio": asyncio, "rt": rt, "sleep_ms": rt.sleep_ms, "print": rt.print, "gather_all": rt.gather_all}
            exec(code, g, g)
        except Exception as e:
            typer.echo(f"error: {e}")

@app.command()
def lsp(host: str = "127.0.0.1", port: int = 2088):
    """Run the LSP server (TCP) for editor integration."""
    from .lsp.server import run_server
    run_server(host, port)

def _print_context(path: str, src: str, line: int | None, col: int | None):
    try:
        if line is None or col is None:
            return
        lines = src.splitlines()
        if 1 <= line <= len(lines):
            text = lines[line - 1]
            pointer = " " * (max(col - 1, 0)) + "^"
            typer.echo(f"{path}:{line}: {text}")
            typer.echo(f"{' ' * (len(path)+1)}{pointer}")
    except Exception:
        pass
