import typer
from pathlib import Path
from casefoam.utility import of_cases, list_functionObjects
import os
import subprocess
import rich
import json
# from rich.pretty import pprint
# from rich.progress import Progress
# from concurrent.futures import ThreadPoolExecutor
# import asyncio
# from random import random
# from time import sleep

app = typer.Typer()


@app.command()
def function_objects(folder: str):
    p = Path.cwd() / folder
    cwd = Path.cwd()
    if not p.exists():
        raise FileNotFoundError(f"Folder with OpenFOAM cases does not excist")

    function_objects = list_functionObjects(folder)

    rich.print_json(json.dumps(function_objects,indent=2))

