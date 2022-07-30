import typer
from pathlib import Path
from casefoam.utility import of_cases, list_functionObjects
import os
import subprocess
import rich
import json

app = typer.Typer()

def create_functionobjects(fo_name,file,case_path):
    file_stem = Path(file).stem
    f_objects = f"""
{fo_name}_{file_stem} = casefoam.load_functionObject("{fo_name}","{file}",OfCases="{case_path}")
{fo_name}_{file_stem}.to_csv("results/{fo_name}_{file_stem}.csv",index=False)

"""
    return f_objects


def create_get_data(case_path):
    getData = []
    header = f"""
import casefoam
from pathlib import Path

#auto generated post processing of the data acquisition

#create results dir to save all data
Path("results").mkdir(exist_ok=True)
p_ofcases = "{case_path}"

"""
    getData.append(header)
    function_objects = list_functionObjects(case_path)

    for fo_name, files in function_objects.items():
        for file in files:
            getData.append(create_functionobjects(fo_name,file,case_path))

    return "".join(getData)


@app.command()
def function_objects(folder: str):
    p = Path.cwd() / folder
    cwd = Path.cwd()
    if not p.exists():
        raise FileNotFoundError(f"Folder with OpenFOAM cases does not excist")

    function_objects = list_functionObjects(folder)

    rich.print_json(json.dumps(function_objects,indent=2))

@app.command()
def template_getData(case_folder: str):

    getData = create_get_data(case_folder)

    with open("getData.py","w") as f:
        f.write(getData)
