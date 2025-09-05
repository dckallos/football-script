from __future__ import annotations
import asyncio
import sys
from pathlib import Path
import warnings
import typer

from .compiler.parser import parse_to_ast
from .compiler.codegen import to_python_ast, compile_module
from .runtime import core as rt

app = typer.Typer(help="football-script CLI (chelsea)")

@app.command()
def run(path: str):
    """Run a .fs program."""
    src = Path(path).read_text(encoding="utf-8")
    fs_module = parse_to_ast(src, uri=Path(path).as_uri())
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
    # If user defined main(), run it
    main = g.get("main")
    if callable(main):
        if asyncio.iscoroutinefunction(main):
            asyncio.run(main())
        else:
            main()

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
