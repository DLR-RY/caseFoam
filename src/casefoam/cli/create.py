import typer
import shutil
import pathlib
from casefoam.genCases import ParameterStudy, _create_study_structure

app = typer.Typer()


template_dir = pathlib.Path(__file__).parent.absolute() / "templates"


@app.command()
def template():
    gen_case_file = template_dir / "genCases.py"
    target_file = pathlib.Path(".", "genCases.py")
    if not target_file.exists():
        shutil.copyfile(gen_case_file, target_file)
    else:
        raise FileExistsError(
            "genCases.py is already present in this directory please remove it"
        )


@app.command()
def from_json():
    para_study = pathlib.Path("para_study.json")
    if para_study.exists():
        print("creating study structure from para_study.json")
        ps = ParameterStudy.parse_file("para_study.json")
        _create_study_structure(ps=ps)
    else:
        raise FileNotFoundError("para_study.json not found")
