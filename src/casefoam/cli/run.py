import typer
from pathlib import Path
from casefoam.utility import of_cases
import os
import subprocess
import time
from rich.progress import track

app = typer.Typer()


@app.command()
def folder(
    folder: str,
    script_name=typer.Option("Allrun", help="specify to run in all of cases"),
):
    p = Path.cwd() / folder
    cwd = Path.cwd()
    if not p.exists():
        raise FileNotFoundError(f"Folder with OpenFOAM cases does not excist")

    cases = of_cases(folder)
    total = 0
    for case in track(cases, description="running cases..."):
        os.chdir(cwd / case)
        subprocess.run(f"./{script_name}")
        total += 1
    print(f"run {total} OpenFOAM Cases.")
