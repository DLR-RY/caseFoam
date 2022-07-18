import typer
from pathlib import Path
from casefoam.utility import of_cases
import os
import subprocess
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor
import asyncio
from random import random
from time import sleep

app = typer.Typer()


def execute_script(script_name, case_path, progress, task_bar):
    sleep_t = random() + 0.1
    sleep(sleep_t)
    os.chdir(case_path)
    subprocess.run(f"./{script_name}", stdout=subprocess.DEVNULL)
    progress.update(task_bar, advance=1)


async def run_case(cases, script_name, cwd, nProcs):
    with Progress() as progress:
        prog_bar = progress.add_task("running cases...", total=len(cases))
        with ThreadPoolExecutor(max_workers=nProcs) as pool:
            loop = asyncio.get_running_loop()
            futures = [
                loop.run_in_executor(
                    pool, execute_script, script_name, (cwd / case), progress, prog_bar
                )
                for case in cases
            ]
            try:
                await asyncio.gather(*futures, return_exceptions=False)
            except Exception as ex:
                print("Caught error executing task", ex)
                raise


@app.command()
def folder(
    folder: str,
    script_name=typer.Option("Allrun", help="specify to run in all of cases"),
    nProcs: int = typer.Option(1, "--nProcs"),
):
    p = Path.cwd() / folder
    cwd = Path.cwd()
    if not p.exists():
        raise FileNotFoundError(f"Folder with OpenFOAM cases does not excist")

    cases = of_cases(folder)
    total = 0
    #     for case in track(cases, description="running cases..."):
    #         os.chdir(cwd / case)
    #         subprocess.run(f"./{script_name}")
    #         total += 1
    loop = asyncio.get_event_loop()
    coroutine = run_case(cases, script_name, cwd, nProcs)
    loop.run_until_complete(coroutine)

    print(f"run {len(cases)} OpenFOAM Cases.")
