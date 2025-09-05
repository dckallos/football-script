from pathlib import Path
from football_script.compiler.parser import parse_to_ast
from football_script.compiler.codegen import to_python_ast, compile_module

def run_fs(src: str) -> dict:
    mod = parse_to_ast(src, uri="<test>")
    pymod = to_python_ast(mod)
    code = compile_module(pymod, filename="<test>")
    g = {"__name__":"__fs_test__"}
    import asyncio, football_script.runtime.core as rt
    g.update({"asyncio": asyncio, "rt": rt, "sleep_ms": rt.sleep_ms, "print": rt.print, "gather_all": rt.gather_all})
    exec(code, g, g)
    return g

def test_hello(tmp_path):
    g = run_fs('def main(){ print("ok"); } main()')
    assert "main" in g

def test_async_runs():
    g = run_fs('async def main(){ results = parallel{ sleep_ms(1), sleep_ms(1) }; } main()')
    import asyncio
    if callable(g.get("main")):
        if asyncio.iscoroutinefunction(g["main"]):
            asyncio.run(g["main"]())
