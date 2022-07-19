from typing_extensions import Annotated
from typing import Literal, Union, List, Any, Dict, Tuple, Optional, Callable
from pathlib import Path
import shutil, os
import itertools
import subprocess
from enum import Enum
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from pydantic import BaseModel, Field, validator

# instructions
class OF_Dict(BaseModel):
    instruction_type: Literal["of_dict"] = Field(default="of_dict")
    file_name: Union[str, Path] = Field(default="system/simulationParameters")
    entry: str

    def _nested_set(self, dic: Dict, keyword: str, value: Any):
        key_list = keyword.split("/")
        key_list[:] = [x for x in key_list if x]
        if len(key_list) == 1:
            dic[key_list[-1]] = value
            return
        for key in key_list[:-1]:
            if key not in dic:
                raise ValueError(
                    f"""
                    key not found in dictionary
                    valid options: {dic.keys()}
                    given: {key}
                """
                )  # Keyerror ignore line breaks
            dic = dic[key]
        dic[key_list[-1]] = value

    def execute(self, value: Any):
        ppp = ParsedParameterFile(self.file_name)
        self._nested_set(ppp.content, self.entry, value)
        ppp.writeFile()


class String(BaseModel):
    instruction_type: Literal["string"] = Field(default="string")
    file_name: Union[str, Path]
    entry: str

    def execute(self, value: str):
        file = Path(self.file_name)
        f_content = file.read_text()
        f_content = f_content.replace(self.entry, value)
        file.write_text(f_content)


class Bash_Cmd(BaseModel):
    instruction_type: Literal["bash_cmd"] = Field(default="bash_cmd")

    def execute(self, value: str):
        subprocess.call(value, shell=True)


Instructions = Annotated[
    Union[OF_Dict, String, Bash_Cmd],
    Field(discriminator="instruction_type"),
]


class Category(BaseModel):
    name: str
    instructions: List[Instructions]

    def execute(self, values: List[Any]):
        for i, instruct in enumerate(self.instructions):
            instruct.execute(values[i])


class Category_Data(BaseModel):
    cat_name: str
    values: List[Any]


class CaseData(BaseModel):
    case_data: List[Category_Data]


class CaseModifier(BaseModel):
    categories: List[Category]
    case_data: CaseData

    def execute(self):
        for idx, cat_mod in enumerate(self.categories):
            cat_mod.execute(self.case_data.case_data[idx].values)


class OFCases(BaseModel):
    cases: List[CaseModifier]

    def execute(self):
        for mod in self.cases:
            mod.execute()


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


def create_cases(ps: ParameterStudy) -> OFCases:
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


def create_category(
    cat_name: str,
    instructions: List[Union[Dict[str, Any], Union[OF_Dict, String, Bash_Cmd]]],
) -> Category:

    if type(instructions[0]) != dict:
        return Category(name=cat_name, instructions=instructions)

    # add default values for the case that a list of dict is supplied
    for i in instructions:
        if "instruction_type" not in i:
            i["instruction_type"] = "of_dict"
        if i["instruction_type"] == "of_dict":
            if "file_name" not in i:
                i["file_name"] = "system/simulationParameters"

    return Category(name=cat_name, instructions=instructions)


Cat_data_func = Callable[
    [int, Union[Any, List[Any]], Optional[List[str]]], Tuple[str, List[Any]]
]


def cat_data_modfunc(
    idx: int,
    data: Union[Any, List[Any]],
    cat_names: Optional[List[str]] = None,
    prefix: str = "c_",
) -> Tuple[str, List[Any]]:
    if cat_names != None:
        if type(data) == list:
            return cat_names[idx], data
        else:
            return cat_names[idx], [data]
    if type(data) == str:
        return data, [data]
    elif type(data) == list:
        return f"{prefix}{idx}", data
    else:  # assume integer float etc
        return f"{prefix}{data}", [data]


def create_category_data(
    data: List[Any],
    cat_names: Optional[List[str]] = None,
    modifier: Cat_data_func = cat_data_modfunc,
    **kwargs,
) -> List[Category_Data]:
    cat_data = []
    for idx, d in enumerate(data):
        cat_name, values = cat_data_modfunc(idx, d, cat_names, **kwargs)
        cat_data.append(Category_Data(cat_name=cat_name, values=values))
    return cat_data


def create_case_data(
    study_data: List[List[Category_Data]], cartesian: bool = True
) -> List[CaseData]:
    if not cartesian:
        cases_data = [CaseData(case_data=c) for c in case_variations]
        return cases_data

    case_variations = list(itertools.product(*study_data))
    cases_data = [CaseData(case_data=c) for c in case_variations]
    return cases_data


def _create_study_structure(ps: ParameterStudy) -> None:
    cases = create_cases(ps)
    case_vars = case_variations(cases)

    with open(Path("para_study.json"), "w") as f:
        f.write(ps.json(indent=2))

    dir_cases = case_struct(case_vars, writeDir=ps.writeDir, structure=ps.structure)

    for c, d in zip(cases.cases, dir_cases):
        shutil.copytree(ps.base_case, d)
        with open(Path(d, "case.json"), "w") as f:
            f.write(c.json(indent=2))

    pwd = os.getcwd()
    for c, d in zip(cases.cases, dir_cases):
        os.chdir(Path(pwd, d))
        c.execute()

    os.chdir(pwd)


def create_study_structure(
    base_case: Union[str, Path],
    categories: List[Category],
    study_data: Union[List[CaseData], List[List[Category_Data]]],
    writeDir: Union[str, Path] = "Cases",
    structure: StructureEnum = StructureEnum.tree,
    cartesian: bool = True,
) -> None:
    """creates the case structure for the parameter study


    Parameters
    ----------
        base_case (Union[str, Path]):
            Directory of the base case that is modified to create the parameter study
        categories (List[Category]):
            category with instructions
        study_data (Union[List[CaseData], List[List[Category_Data]]]):
             data of the category
        writeDir (Union[str, Path], optional):
            Directory where created cases are stored. 
        structure ({'flat', 'tree'}, optional):
            Hierarchy in which the case directory will be created.

            * 'flat': Creates the structure `parent_child_grandchild`.
            * 'tree': Creates the structure `parent/child/grandchild`. Defaults to "Cases".
        cartesian (bool, optional) Defaults to True. :
            cartesian product of all categories. Defaults to True.
    """
    if type(study_data[0]) != CaseData:
        study_data = create_case_data(study_data, cartesian)

    ps = ParameterStudy(
        base_case=base_case,
        writeDir=writeDir,
        structure=structure,
        categories=categories,
        study_data=study_data,
    )
    _create_study_structure(ps)
