from typing_extensions import Annotated
from typing import Literal, Union, List, Any
from pathlib import Path
import shutil
from enum import Enum
from pydantic import BaseModel, Field, validator

# instructions
class OF_Dict(BaseModel):
    instruction_type: Literal["of_dict"] = Field(default="of_dict")
    file_name: Union[str, Path]
    entry: str

    def execute(self):
        print(self.instruction_type)


class String(BaseModel):
    instruction_type: Literal["string"] = Field(default="string")
    file_name: Union[str, Path]
    entry: str

    def execute(self):
        print(self.instruction_type)


class Bash_Cmd(BaseModel):
    instruction_type: Literal["bash_cmd"] = Field(default="bash_cmd")

    def execute(self):
        print(self.instruction_type)


Instructions = Annotated[
    Union[OF_Dict, String, Bash_Cmd],
    Field(discriminator="instruction_type"),
]


class Category(BaseModel):
    name: str
    instructions: List[Instructions]


class Category_Data(BaseModel):
    cat_name: str
    values: List[Any]


class CaseData(BaseModel):
    case_data: List[Category_Data]


class StructureEnum(str, Enum):
    flat = "flat"
    tree = "tree"


class ParameterStudy(BaseModel):
    base_case: Union[str, Path]
    writeDir: Union[str, Path] = Field(default="Cases")
    structure: StructureEnum = StructureEnum.tree
    categories: List[Category]
    study_data: List[CaseData]

    @validator("study_data")
    def verify_data(cls, v, values, **kwargs):
        nCategories = len(values["categories"])
        nValues_in_categories = [len(val.instructions) for val in values["categories"]]
        if not all([len(d.case_data) == nCategories for d in v]):
            nCase_data = [len(d.case_data) for d in v]
            raise ValueError(
                f"""
                    number of provided categories: {nCategories}
                    number of data in a categories: min: {min(nCase_data)} max: {min(nCase_data)}
                    They have to match!
                 """
            )
        for d in v:
            nValues = [len(val.values) for val in d.case_data]
            if nValues != nValues_in_categories:
                raise ValueError(
                    f"""
                        number of instructions: {nValues_in_categories}
                        number of data: {nValues}
                        They have to match!
                    """
                )
        ## more validation are the cat names unique
        return v


class CaseModifier(BaseModel):
    categories: List[Category]
    case_data: CaseData

    def execute(self):
        for cat_mod in self.categories:
            cat_mod.execute()


class OFCases(BaseModel):
    cases: List[CaseModifier]


def create_cases(ps: ParameterStudy) -> List[OFCases]:
    cases = []
    cats = ps.categories
    for cs in ps.study_data:
        cases.append(CaseModifier(categories=cats, case_data=cs))
    return OFCases(cases=cases)


def get_cat_names(ps: ParameterStudy) -> List[str]:
    return [c.name for c in ps.categories]


def case_variations(cases: OFCases) -> List[List[str]]:
    vars = []
    for c in cases.cases:
        vars.append([d.cat_name for d in c.case_data.case_data])
    return vars


def case_struct(
    cvs: List[List[str]],
    writeDir: Union[str, Path] = "Cases",
    structure: StructureEnum = StructureEnum.tree,
) -> List[Path]:
    if structure == "tree":
        cs = [Path(writeDir, "/".join(cv)) for cv in cvs]
    else:
        cs = [Path(writeDir, "-".join(cv)) for cv in cvs]
    return cs


def study_structure(ps: ParameterStudy) -> None:
    cases = create_cases(ps)
    case_vars = case_variations(cases)

    with open(Path("para_study.json"), "w") as f:
        f.write(ps.json(indent=2))

    dir_cases = case_struct(case_vars, writeDir=ps.writeDir, structure=ps.structure)

    for c, d in zip(cases.cases, dir_cases):
        shutil.copytree(ps.base_case, d)
        with open(Path(d, "case.json"), "w") as f:
            f.write(c.json(indent=2))
