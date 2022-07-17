import typer

from casefoam.cli import create
from casefoam.cli import run

app = typer.Typer()
app.add_typer(create.app, name="create")
app.add_typer(run.app, name="run")
