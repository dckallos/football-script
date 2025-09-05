# football-script v1 — Python-first tiny language (MVP)

This is the **football‑script v1** MVP: Lark parser → Python `ast` codegen → CPython runtime, plus a minimal LSP server skeleton and Typer-based CLI.

## Clarifications & Locked‑In Defaults

No answers were provided to the seven setup questions, so we applied the defaults and **record them here** (with rationale).

1. **Python version floor** — **3.11** (modern `typing`, `asyncio` improvements, `ExceptionGroup`, performance).
2. **Build backend** — **Hatch + hatchling** (PEP 517/518 compliant, simple `pyproject.toml`).
3. **Package / import names** — Distribution: **`football-script`**; Top-level import: **`football_script`**.
4. **CLI framework** — **Typer** (type‑hint friendly, built on Click).
5. **LSP feature floor** — **Diagnostics**, **Hover**, **Document Symbols**, **Go‑to Definition** (skeleton shipped; Phase 3 expands).
6. **Formatter knobs** — **None** in v1 (idempotent, Black‑style minimalism target for Phase 4).
7. **Theme pack name** — **`football-script-chelsea`** (opt‑in, separate package in Phase 5).

These choices are documented in the project plan and can be revisited in later phases without breaking v1.

## Quick start

```bash
# Prereq: Python 3.11+
pip install -e .

# Hello
chelsea run examples/hello.fs

# Async & parallel
chelsea run examples/async.fs

# Start LSP (TCP) and connect from an editor or netcat for smoke tests
chelsea lsp
```

> Tip: Use a virtual environment. For packaging, install `hatch` and run `hatch build` to create wheels.

## Language slice (v1)

- Literals: `NUMBER`, `STRING`, `true/false/none`
- Statements: assignments, `def` / `async def`, `if` / `while` / `return`, `import`
- Calls: `f(1,2)`, **names only** in v1 (no call on arbitrary expressions)
- Async: `await` operator (inside async funcs) and **`parallel{ ... }`** expression

### `parallel{ ... }` — semantics & error policy

- Lowers to an **await** of a helper that completes **all tasks** and aggregates failures.
- v1 runtime uses `asyncio.gather(..., return_exceptions=True)` internally and then **raises an `ExceptionGroup`** if any branch failed; otherwise returns the ordered results list.
- Parent cancellation cancels outstanding children (standard `asyncio` behavior).

```fs
async def main() {
  results = parallel{ sleep_ms(100), sleep_ms(200) }
  print("done")
}
```

### Notes

- Parser uses **Lark LALR** for speed and deterministic behavior.
- The lowering pipeline: FootballScript AST (dataclasses) → Python `ast.Module` → `compile()` → `exec()`.
- Only simple identifier calls are supported in v1; member calls etc. are out of scope.
- Boolean operators `and`/`or`/`not` are reserved for future expansion; basic arithmetic and comparisons are implemented.

## Milestones

- **Phase 1 (this commit):** Parser → Codegen → Runtime → CLI; minimal LSP diagnostics.
- **Phase 2:** Gradual typing boundary checks and casts.
- **Phase 3:** LSP features (hover, symbols, go‑to def).
- **Phase 4:** Formatter & linter.
- **Phase 5:** Optional Chelsea theme pack.
- **Phase 6:** Packaging & CI (wheels, coverage gates, SemVer).

## Performance

- Target parser throughput ≥ **1k LOC/s** on synthetic inputs (LALR has linear behavior on CFGs).

## License

MIT
