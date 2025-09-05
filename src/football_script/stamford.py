import typer
app = typer.Typer(help="stamford: packaging helper (stub)")

@app.command()
def info():
    typer.echo("stamford: packaging commands are stubs in v1. Use `hatch build` for wheels.")
